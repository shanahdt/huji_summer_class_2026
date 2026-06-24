"""
utils/information_theory.py — Entropy, predictability, and shared information
Summer Institute 2026 · Hebrew University of Jerusalem

This module answers the Day 4 question: "how much uncertainty is there in a
melody, how predictable is it, and how differently do two pieces (or two
corpora, or two features of the same piece) behave?" — starting from the
simplest possible measure and building up to bigger comparisons.

Questions answered here, smallest to largest:
    1. How much pitch variety/uncertainty is in ONE piece?
           -> pitch_entropy()
    2. Once you know the previous note(s), how much LESS uncertain is the
       next one? (i.e. how predictable/structured is this melody?)
           -> conditional_entropy()
    3. How differently do TWO corpora use pitch?
           -> compare_corpus_entropy()  (uses kl_divergence())
    4. Within a piece, how much does one feature (pitch) tell you about
       another (rhythm)?
           -> pitch_duration_mutual_information()  (uses mutual_information())

Beginner usage
---------------
    from utils import pitch_entropy
    entropy, counts = pitch_entropy('../data/happy_birthday.krn')

    from utils import conditional_entropy
    result = conditional_entropy('../data/happy_birthday.krn', n=2)

    from utils import compare_corpus_entropy
    compare_corpus_entropy('../data/Essen/England', '../data/Essen/Italia',
                            names=('English', 'Italian'))

    from utils import pitch_duration_mutual_information
    mi, joint = pitch_duration_mutual_information('../data/happy_birthday.krn')
"""

from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .corpus import PITCH_CLASS_NAMES, note_table, pitch_histogram, describe_corpus
from .ngrams import get_ngrams, note_sequence, pitch_class_sequence, scale_degree_sequence


# ── Symbol sequences (shared by entropy AND similarity functions) ───────────

def _symbol_sequence(file_path_or_score, by='pitch_class'):
    """
    Internal helper: turn a piece into an ordered list of symbols, at
    whichever granularity you ask for. Shared building block for the
    entropy functions in this module AND the edit-distance functions in
    similarity.py, so 'by' means the same thing everywhere in the package.

    by='pitch_class'   -> octave-folded pitch names ('C', 'C#', ...)
    by='note'          -> full pitch + octave ('C4', 'C#4', ...)
    by='scale_degree'  -> key-relative chromatic degree ('1', 'b3', '5', ...)
    """
    if by == 'pitch_class':
        return pitch_class_sequence(file_path_or_score)
    elif by == 'note':
        return note_sequence(file_path_or_score)
    elif by == 'scale_degree':
        return scale_degree_sequence(file_path_or_score)
    else:
        raise ValueError("by must be 'pitch_class', 'note', or 'scale_degree'")


# ── Q1: how much uncertainty is in ONE distribution? ─────────────────────────

def shannon_entropy(data, base=2):
    """
    CORE MEASURE: Shannon entropy, H = -Σ p_i log_b(p_i) — how much
    uncertainty/"surprise" is built into a distribution.

    0 = totally predictable (only one outcome ever happens). Higher = more
    spread out across possibilities — the maximum for N equally-likely
    outcomes is log_b(N).

    Parameters
    ----------
    data : sequence, Counter, dict, or pd.Series
        Either raw observations (e.g. a list of pitch classes — entropy is
        computed from how often each value appears), OR an already-built
        distribution of counts/probabilities (e.g. from pitch_histogram()).
    base : float
        Logarithm base. 2 (default) gives entropy in BITS, the unit used
        throughout this module. Use base=np.e for "nats".

    Returns
    -------
    float >= 0, in the chosen base's units.

    Example
    -------
        shannon_entropy(['C', 'C', 'G', 'G', 'E'])          # from raw notes
        shannon_entropy({'C': 2, 'G': 2, 'E': 1})            # from counts
        shannon_entropy(pitch_histogram('../data/happy_birthday.krn', plot=False))
    """
    if isinstance(data, pd.Series):
        counts = data
    elif isinstance(data, (dict, Counter)):
        counts = pd.Series(dict(data))
    else:
        counts = pd.Series(Counter(data))

    counts = counts[counts > 0]
    if counts.empty:
        return 0.0

    probs = counts / counts.sum()
    return float(-(probs * np.log(probs) / np.log(base)).sum())


def pitch_entropy(file_path_or_score, by='pitch_class', plot=True, title=None):
    """
    ONE-STOP, Q1 (the smallest question): how much pitch variety is in this
    piece? Builds the pitch(-class) histogram (see pitch_histogram() in
    corpus.py) and reports its Shannon entropy in bits.

    A 2-note piece used equally often has entropy = 1.0 bit; a 12-pitch-
    class piece used equally often has entropy = log2(12) ≈ 3.58 bits (the
    max possible for 12 categories); a one-note drone has entropy = 0.

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    by : 'pitch_class' or 'pitch'
        See pitch_histogram(). 'pitch_class' (default) folds octaves together.
    plot : bool
        If True, show the histogram, labeled with the entropy value.
    title : str, optional

    Returns
    -------
    entropy : float — bits
    counts  : pd.Series — the underlying histogram

    Example
    -------
        entropy, counts = pitch_entropy('../data/happy_birthday.krn')
        print(f'{entropy:.2f} bits')
    """
    counts = pitch_histogram(file_path_or_score, by=by, plot=False)
    entropy = shannon_entropy(counts)
    n_used = int((counts > 0).sum())
    max_entropy = np.log2(n_used) if n_used > 0 else 0.0

    if plot:
        plt.figure(figsize=(9, 4))
        counts.plot(kind='bar', color='steelblue', edgecolor='white')
        plt.title(title or f'Pitch histogram — entropy = {entropy:.2f} bits')
        plt.xlabel('Pitch class' if by == 'pitch_class' else 'Pitch')
        plt.ylabel('Count')
        plt.xticks(rotation=0 if by == 'pitch_class' else 45,
                   ha='center' if by == 'pitch_class' else 'right')
        plt.tight_layout()
        plt.show()

    print(f'Entropy: {entropy:.3f} bits  '
          f'(max possible for the {n_used} pitch (class)es actually used: '
          f'{max_entropy:.3f} bits)')

    return entropy, counts


# ── Q2: how predictable is the NEXT note, given context? ────────────────────

def conditional_entropy(file_path_or_score, n=2, by='pitch_class', base=2):
    """
    ONE-STOP, Q2 (a bigger question than Q1): once you know the previous
    (n-1) note(s), how much LESS uncertain is the next note? This is
    conditional entropy, H(next | context) = H(joint n-gram) -
    H(context (n-1)-gram) — smaller than the plain entropy from
    pitch_entropy() whenever a melody's note choices depend on what came
    before (true of almost all tonal music — that dependency IS melodic
    structure).

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    n : int
        N-gram size. n=2 (default): "given the PREVIOUS note, how
        predictable is THIS note?" Try n=3 for "...given the previous two."
    by : 'pitch_class', 'note', or 'scale_degree'
        Symbol granularity — see _symbol_sequence().
    base : float
        Log base for entropy (bits by default).

    Returns
    -------
    dict with keys:
        'unconditional_entropy' — H(X), entropy of the note distribution alone
        'conditional_entropy'   — H(X | context), entropy of the next note
                                   GIVEN the previous n-1 notes
        'information_gain'      — bits of uncertainty the context removes
                                   (unconditional - conditional); 0 = context
                                   tells you nothing, bigger = more
                                   predictable/structured melody

    Example
    -------
        result = conditional_entropy('../data/happy_birthday.krn', n=2)
        print(result['information_gain'], 'bits gained from the previous note')
    """
    seq = _symbol_sequence(file_path_or_score, by=by)
    if len(seq) < n:
        raise ValueError(f'Need at least {n} notes; this piece only has {len(seq)}.')

    grams = get_ngrams(seq, n)
    joint_counts = Counter(grams)
    context_counts = Counter(g[:-1] for g in grams)

    h_joint = shannon_entropy(joint_counts, base=base)
    h_context = shannon_entropy(context_counts, base=base)
    h_conditional = h_joint - h_context

    h_unconditional = shannon_entropy(Counter(seq), base=base)
    info_gain = h_unconditional - h_conditional

    print(f'H(note)                       = {h_unconditional:.3f} bits  (no context)')
    print(f'H(note | previous {n - 1})           = {h_conditional:.3f} bits')
    print(f'Information gain from context = {info_gain:.3f} bits')

    return {
        'unconditional_entropy': h_unconditional,
        'conditional_entropy': h_conditional,
        'information_gain': info_gain,
    }


# ── Q3: how differently do TWO corpora use pitch? ────────────────────────────

def kl_divergence(p, q, base=2):
    """
    CORE MEASURE: Kullback-Leibler divergence D_KL(P || Q) — how many EXTRA
    bits you'd need, on average, to describe outcomes from distribution P if
    you used a code optimized for distribution Q instead.

    0 = identical distributions; bigger = more different. NOT symmetric:
    D_KL(P||Q) is generally different from D_KL(Q||P) — order matters (the
    same spirit of asymmetry you'll meet again in tversky_index(), in
    similarity.py).

    Parameters
    ----------
    p, q : Counter, dict, or pd.Series
        Two count/probability distributions over the SAME categories (e.g.
        two pitch-class histograms). A small smoothing constant is added
        automatically so zero counts don't make this infinite.
    base : float
        Log base (bits by default).

    Returns
    -------
    float >= 0

    Example
    -------
        d = kl_divergence(counts_a, counts_b)
    """
    p_s = p.copy() if isinstance(p, pd.Series) else pd.Series(dict(p))
    q_s = q.copy() if isinstance(q, pd.Series) else pd.Series(dict(q))
    index = p_s.index.union(q_s.index)
    eps = 1e-9
    p_s = p_s.reindex(index).fillna(0) + eps
    q_s = q_s.reindex(index).fillna(0) + eps
    p_prob = p_s / p_s.sum()
    q_prob = q_s / q_s.sum()
    return float((p_prob * np.log(p_prob / q_prob) / np.log(base)).sum())


def compare_corpus_entropy(corpus_a, corpus_b, pattern='*.krn', by='pitch_class',
                            names=('Corpus A', 'Corpus B'), plot=True, figsize=(9, 4.5)):
    """
    ONE-STOP, Q3 (bigger than Q1/Q2 — now comparing TWO corpora): how
    differently do two corpora use pitch? Builds an aggregated
    pitch(-class) distribution for each corpus, reports each one's entropy,
    and reports the KL divergence between them in BOTH directions (it's
    asymmetric — see kl_divergence()), plus a side-by-side bar chart.

    Parameters
    ----------
    corpus_a, corpus_b : str, Path, or list
        Two folders of files (or lists of files) — same as describe_corpus().
    pattern : str
    by : 'pitch_class' or 'pitch'
    names : tuple of 2 str
        Labels for the two corpora in the printout/plot.
    plot, figsize

    Returns
    -------
    dict with keys: 'entropy_a', 'entropy_b', 'kl_a_to_b', 'kl_b_to_a',
    'counts_a', 'counts_b'

    Example
    -------
        result = compare_corpus_entropy(
            '../data/Essen/England', '../data/Essen/Italia',
            names=('English', 'Italian'))
    """
    _, _, counts_a = describe_corpus(corpus_a, pattern=pattern, by=by, plot=False, verbose=False)
    _, _, counts_b = describe_corpus(corpus_b, pattern=pattern, by=by, plot=False, verbose=False)

    entropy_a = shannon_entropy(counts_a)
    entropy_b = shannon_entropy(counts_b)
    kl_ab = kl_divergence(counts_a, counts_b)
    kl_ba = kl_divergence(counts_b, counts_a)

    print(f'{names[0]}: entropy = {entropy_a:.3f} bits')
    print(f'{names[1]}: entropy = {entropy_b:.3f} bits')
    print(f'D_KL({names[0]} || {names[1]}) = {kl_ab:.3f} bits  '
          f'(extra bits to encode {names[0]} using a {names[1]}-shaped code)')
    print(f'D_KL({names[1]} || {names[0]}) = {kl_ba:.3f} bits')

    if plot:
        df = pd.DataFrame({names[0]: counts_a, names[1]: counts_b}).fillna(0)
        df.plot(kind='bar', figsize=figsize, color=['steelblue', 'coral'], edgecolor='white')
        plt.title(f'{names[0]} vs {names[1]}  (D_KL = {kl_ab:.2f} / {kl_ba:.2f} bits)')
        plt.ylabel('Count')
        plt.xlabel('Pitch class' if by == 'pitch_class' else 'Pitch')
        plt.xticks(rotation=0 if by == 'pitch_class' else 45,
                   ha='center' if by == 'pitch_class' else 'right')
        plt.tight_layout()
        plt.show()

    return {
        'entropy_a': entropy_a, 'entropy_b': entropy_b,
        'kl_a_to_b': kl_ab, 'kl_b_to_a': kl_ba,
        'counts_a': counts_a, 'counts_b': counts_b,
    }


# ── Q4: how much does one feature tell you about another? ───────────────────

def mutual_information(seq_x, seq_y, base=2):
    """
    CORE MEASURE: mutual information, I(X;Y) = H(X) + H(Y) - H(X,Y) — how
    much knowing X reduces your uncertainty about Y (and, unlike
    conditional entropy or KL divergence, this one IS symmetric: I(X;Y) ==
    I(Y;X)).

    0 = X and Y are independent; bigger = more entangled.

    Parameters
    ----------
    seq_x, seq_y : sequences of equal length
        Paired observations — seq_x[i] and seq_y[i] are two features of the
        SAME i-th thing (e.g. a note's pitch class and its duration bin).
    base : float

    Returns
    -------
    float >= 0

    Example
    -------
        mi = mutual_information(pitch_classes, duration_bins)
    """
    if len(seq_x) != len(seq_y):
        raise ValueError('seq_x and seq_y must be the same length (paired observations).')

    h_x = shannon_entropy(Counter(seq_x), base=base)
    h_y = shannon_entropy(Counter(seq_y), base=base)
    h_xy = shannon_entropy(Counter(zip(seq_x, seq_y)), base=base)
    return h_x + h_y - h_xy


def pitch_duration_mutual_information(file_path_or_score, duration_bins=None, plot=True):
    """
    ONE-STOP, Q4 (the biggest question in this module): within ONE piece,
    how much does a note's PITCH tell you about its DURATION (and vice
    versa)? Mutual information between the pitch-class sequence and a
    (binned) duration sequence.

    0 bits = pitch and rhythm look unrelated in this piece. Bigger = they're
    entangled (e.g. a piece where high notes are always short).

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    duration_bins : list of float, optional
        Bin edges (in quarter notes) for grouping durations into categories
        before computing entropy — every raw continuous duration would
        otherwise be its own unique "category". Default: [0, 0.5, 1, 2, 4,
        inf]. Pass your own edges for finer/coarser bins.
    plot : bool
        If True, show a heatmap of the joint pitch-class x duration-bin
        distribution.

    Returns
    -------
    mi : float — mutual information, in bits
    joint : pd.DataFrame — the joint distribution (pitch class x duration bin)

    Example
    -------
        mi, joint = pitch_duration_mutual_information('../data/happy_birthday.krn')
    """
    df = note_table(file_path_or_score)
    if df.empty:
        print('No notes found.')
        return 0.0, pd.DataFrame()

    if duration_bins is None:
        duration_bins = [0, 0.5, 1, 2, 4, np.inf]
    bin_labels = [f'{duration_bins[i]}-{duration_bins[i + 1]}'
                  for i in range(len(duration_bins) - 1)]
    df = df.copy()
    df['duration_bin'] = pd.cut(df['duration_ql'], bins=duration_bins,
                                 labels=bin_labels, right=False).astype(str)

    mi = mutual_information(df['pitch_class_name'].tolist(), df['duration_bin'].tolist())

    joint = pd.crosstab(df['pitch_class_name'], df['duration_bin'])
    joint = joint.reindex(PITCH_CLASS_NAMES).fillna(0).astype(int)

    print(f'Mutual information between pitch class and duration: {mi:.3f} bits')
    if mi < 0.05:
        print('  -> close to 0: pitch and rhythm look roughly independent here.')
    else:
        print('  -> noticeably above 0: pitch and rhythm are entangled in this piece.')

    if plot:
        import seaborn as sns
        plt.figure(figsize=(8, 5))
        sns.heatmap(joint, annot=True, fmt='d', cmap='Blues')
        plt.title(f'Pitch class x duration bin (MI = {mi:.3f} bits)')
        plt.xlabel('Duration bin (quarter notes)')
        plt.ylabel('Pitch class')
        plt.tight_layout()
        plt.show()

    return mi, joint
