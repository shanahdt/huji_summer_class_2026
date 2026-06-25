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

Extra credit / historical & corpus-scale questions
----------------------------------------------------
    5. How does a piece's entropy change depending on HOW you represent it
       (raw pitch vs. pitch class vs. scale degree vs. interval vs. contour
       vs. rhythm)?
           -> compare_entropy_representations()
    6. What does the entropy DISTRIBUTION across a whole corpus look like?
           -> corpus_entropy_profile()
    7. Do two corpora differ in how PREDICTABLE their melodies are (not just
       in what pitches they use)?
           -> compare_corpus_conditional_entropy()
    8. Has melodic predictability/entropy changed over MUSIC HISTORY?
           -> entropy_over_time()  (uses date_from_kern_headers())
    9. Before any of this — how much information is in a sequence if you
       assume every symbol is equally likely? (the pre-Shannon baseline)
           -> hartley_information()

    from utils import hartley_information
    bits = hartley_information(85, 12)   # UConn fight song

    from utils import compare_entropy_representations
    table = compare_entropy_representations('../data/happy_birthday.krn')

    from utils import corpus_entropy_profile
    profile = corpus_entropy_profile('../data/Essen/England')

    from utils import compare_corpus_conditional_entropy
    result = compare_corpus_conditional_entropy(
        '../data/Essen/England', '../data/Essen/Italia', names=('English', 'Italian'))

    from utils import entropy_over_time
    df = entropy_over_time(['../data/humdrum_scores/Mozart',
                             '../data/humdrum_scores/Beethoven'])
"""

import re
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from music21 import converter

from .corpus import PITCH_CLASS_NAMES, note_table, pitch_histogram, describe_corpus
from .ngrams import get_ngrams, note_sequence, pitch_class_sequence


# ── Symbol sequences (shared by entropy AND similarity functions) ───────────

def _symbol_sequence(file_path_or_score, by='pitch_class'):
    """
    Internal helper: turn a piece into an ordered list of symbols, at
    whichever granularity you ask for. Shared building block for the
    entropy functions in this module AND the edit-distance functions in
    similarity.py, so 'by' means the same thing everywhere in the package.

    by='pitch_class'   -> octave-folded pitch names ('C', 'C#', ...)
    by='note'          -> full pitch + octave ('C4', 'C#4', ...)
    by='scale_degree'  -> DIATONIC scale degree (1-7, relative to the
                          piece's detected key; 0 = chromatic/out-of-scale).
                          NOTE: this is intentionally NOT the same as
                          ngrams.py's scale_degree_sequence(), which just
                          transposes pitch classes to a 12-label chromatic
                          alphabet — that's a bijective relabeling of pitch
                          class and so can NEVER produce a different Shannon
                          entropy than by='pitch_class'. The 1-7 diatonic
                          reduction is genuinely lossy (multiple chromatic
                          pitch classes can collapse into the same degree,
                          or into the 0 bucket), so it actually differs.
    by='interval'      -> signed melodic interval, in semitones, between
                          consecutive notes
    by='contour'       -> melodic direction between consecutive notes
                          (+1 up, -1 down, 0 repeat)
    """
    if by == 'pitch_class':
        return pitch_class_sequence(file_path_or_score)
    elif by == 'note':
        return note_sequence(file_path_or_score)
    elif by == 'scale_degree':
        return _diatonic_scale_degree_sequence(_as_score(file_path_or_score))
    elif by == 'interval':
        midi_vals = _midi_sequence(_as_score(file_path_or_score))
        return [b - a for a, b in zip(midi_vals, midi_vals[1:])]
    elif by == 'contour':
        midi_vals = _midi_sequence(_as_score(file_path_or_score))
        return [1 if b > a else (-1 if b < a else 0)
                for a, b in zip(midi_vals, midi_vals[1:])]
    else:
        raise ValueError(
            "by must be 'pitch_class', 'note', 'scale_degree', 'interval', or 'contour'")


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
    by : 'pitch_class', 'note', 'scale_degree', 'interval', or 'contour'
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


# ── Internal helpers for the representation/corpus/date functions below ─────

def _as_score(file_path_or_score):
    """Internal: parse a file path into a music21 Score (or pass a Score through)."""
    return (converter.parse(str(file_path_or_score))
            if isinstance(file_path_or_score, (str, Path))
            else file_path_or_score)


def _midi_sequence(score):
    """Internal: ordered MIDI numbers for every note in a score (chords expanded)."""
    midi_vals = []
    for element in score.recurse().notes:
        pitches = element.pitches if element.isChord else [element.pitch]
        for p in pitches:
            midi_vals.append(int(p.midi))
    return midi_vals


def _diatonic_scale_degree_sequence(score):
    """
    Internal: DIATONIC scale degree (1-7, relative to the piece's detected
    key) for every note, with 0 standing in for chromatic/out-of-scale notes.

    This is deliberately different from scale_degree_sequence() in ngrams.py,
    which returns a 12-category CHROMATIC label (e.g. 'b3') for every note —
    that one is for melodic n-gram/bigram work, this one is for the
    "how many distinct symbols does a 1-7 diatonic alphabet need" entropy
    question in compare_entropy_representations().
    """
    key_obj = score.analyze('key')
    degrees = []
    for p in score.pitches:
        deg = key_obj.getScaleDegreeFromPitch(p, comparisonAttribute='pitchClass')
        degrees.append(deg if deg is not None else 0)
    return degrees


def _duration_bin_sequence(score, bin_size=0.25):
    """Internal: durations (in quarter notes) rounded to the nearest `bin_size`."""
    return [round(float(element.duration.quarterLength) / bin_size) * bin_size
            for element in score.recurse().notes]


# ── Q5: how much does ENTROPY depend on how you represent the piece? ────────

def hartley_information(n_symbols, n_possible):
    """
    BUILDING BLOCK: Hartley's 1928 information measure — the pre-Shannon
    baseline that assumes every symbol is equally likely: H = n * log2(s),
    where n is the number of symbols (e.g. notes) and s is the number of
    POSSIBLE values each one could take.

    Shannon entropy (shannon_entropy()) is always <= this, because real
    melodies don't use every pitch equally often — the gap between the two
    is itself informative (it's how much structure/redundancy there is).

    Parameters
    ----------
    n_symbols : int
        Number of symbols in the sequence (e.g. number of notes).
    n_possible : int
        Number of possible distinct values each symbol could take (e.g. 12
        for chromatic pitch classes).

    Returns
    -------
    float — bits

    Example
    -------
        hartley_information(85, 12)    # UConn fight song: 85 notes, 12 possible pitch classes
        hartley_information(142, 12)   # Northwestern fight song: 142 notes, 12 possible pitch classes
    """
    if n_possible < 1:
        raise ValueError('n_possible must be >= 1')

    bits = n_symbols * (np.log2(n_possible) if n_possible > 1 else 0.0)
    print(f'{n_symbols} notes with {n_possible} possible values = {bits:.2f} bits (Hartley 1928)')
    return float(bits)


def compare_entropy_representations(file_path_or_score, plot=True):
    """
    ONE-STOP: how much does a piece's entropy depend on HOW you describe it?
    Computes Shannon entropy for the SAME piece across six representations:
    raw pitch names, pitch classes, diatonic scale degrees (1-7, 0 =
    chromatic), melodic intervals (signed semitones), contour (+1 up / -1
    down / 0 repeat), and rhythmic durations (binned to the nearest 0.25
    quarter note).

    Coarser representations (e.g. contour, with only 3 possible symbols)
    will generally have LOWER entropy than finer ones (e.g. raw pitch) —
    this function makes that trade-off visible side by side.

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    plot : bool
        If True (default), show a horizontal bar chart with each bar
        labeled by its entropy value.

    Returns
    -------
    pd.DataFrame — columns: representation, entropy, n_unique_symbols, n_events

    Example
    -------
        table = compare_entropy_representations('../data/happy_birthday.krn')
    """
    try:
        score = _as_score(file_path_or_score)
    except Exception as e:
        print(f'Could not parse {file_path_or_score}: {e}')
        return pd.DataFrame(columns=['representation', 'entropy', 'n_unique_symbols', 'n_events'])

    midi_vals = _midi_sequence(score)
    intervals = [b - a for a, b in zip(midi_vals, midi_vals[1:])]
    contour = [1 if b > a else (-1 if b < a else 0) for a, b in zip(midi_vals, midi_vals[1:])]

    representations = {
        'pitch (raw)': note_sequence(score),
        'pitch_class': pitch_class_sequence(score),
        'scale_degree (1-7)': _diatonic_scale_degree_sequence(score),
        'interval (semitones)': intervals,
        'contour (+1/-1/0)': contour,
        'duration (binned)': _duration_bin_sequence(score),
    }

    rows = []
    for name, seq in representations.items():
        ent = shannon_entropy(Counter(seq))
        rows.append({
            'representation': name,
            'entropy': ent,
            'n_unique_symbols': len(set(seq)),
            'n_events': len(seq),
        })
    result = pd.DataFrame(rows)

    if plot:
        plt.figure(figsize=(9, 5))
        bars = plt.barh(result['representation'], result['entropy'],
                         color='steelblue', edgecolor='white')
        for bar, val in zip(bars, result['entropy']):
            plt.text(val + 0.03, bar.get_y() + bar.get_height() / 2,
                      f'{val:.2f}', va='center')
        plt.xlabel('Shannon entropy (bits)')
        title_name = (Path(str(file_path_or_score)).stem
                      if isinstance(file_path_or_score, (str, Path)) else 'this piece')
        plt.title(f'Entropy by representation — {title_name}')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.show()

    return result


def corpus_entropy_profile(kern_dir, representation='scale_degree', pattern='*.krn',
                            verbose=True, plot=True):
    """
    ONE-STOP: what does the entropy DISTRIBUTION look like across a whole
    corpus? Computes Shannon entropy (in the chosen representation) for
    every piece in `kern_dir` and reports the mean/median/min/max.

    Parameters
    ----------
    kern_dir : str or Path
        Folder of kern files.
    representation : 'pitch_class', 'note', 'scale_degree', 'interval', or 'contour'
        Symbol granularity — see _symbol_sequence().
    pattern : str
        Glob pattern (default '*.krn').
    verbose : bool
        If True (default), print progress every 25 files and report skipped files.
    plot : bool
        If True (default), show a histogram of entropy values with the mean marked.

    Returns
    -------
    pd.DataFrame — columns: tune_id, entropy, n_notes

    Example
    -------
        profile = corpus_entropy_profile('../data/Essen/England')
    """
    path = Path(kern_dir)
    if not path.exists():
        print(f'Path not found: {kern_dir}')
        return pd.DataFrame(columns=['tune_id', 'entropy', 'n_notes'])

    files = sorted(path.glob(pattern)) if path.is_dir() else [path]
    if not files:
        print(f"No files matching '{pattern}' found in {kern_dir}")
        return pd.DataFrame(columns=['tune_id', 'entropy', 'n_notes'])

    rows = []
    skipped = []
    for i, f in enumerate(files):
        if verbose and i % 25 == 0:
            print(f'  {i + 1}/{len(files)}...')
        try:
            seq = _symbol_sequence(str(f), by=representation)
            rows.append({'tune_id': f.stem, 'entropy': shannon_entropy(Counter(seq)),
                         'n_notes': len(seq)})
        except Exception as e:
            skipped.append((str(f), str(e)))
            if verbose:
                print(f'  Skipped {f.name}: {e}')

    if skipped:
        print(f'Skipped {len(skipped)} unreadable file(s).')

    if not rows:
        print('No pieces could be read.')
        return pd.DataFrame(columns=['tune_id', 'entropy', 'n_notes'])

    result = pd.DataFrame(rows)

    print(f'{len(result)} piece(s) — entropy ({representation}): '
          f'mean={result["entropy"].mean():.3f}, median={result["entropy"].median():.3f}, '
          f'min={result["entropy"].min():.3f}, max={result["entropy"].max():.3f}')

    if plot:
        plt.figure(figsize=(9, 4.5))
        plt.hist(result['entropy'], bins=20, color='steelblue', edgecolor='white')
        mean_val = result['entropy'].mean()
        plt.axvline(mean_val, color='coral', linestyle='--', linewidth=2,
                    label=f'mean = {mean_val:.3f}')
        plt.xlabel(f'Entropy (bits) — {representation}')
        plt.ylabel('Number of pieces')
        plt.title(f'Entropy distribution: {Path(kern_dir).name} ({len(result)} pieces)')
        plt.legend()
        plt.tight_layout()
        plt.show()

    return result


def compare_corpus_conditional_entropy(kern_dir_a, kern_dir_b, names=('A', 'B'), n=2,
                                        representation='scale_degree', pattern='*.krn',
                                        plot=True, verbose=True):
    """
    ONE-STOP: do two corpora differ in how PREDICTABLE their melodies are
    (as opposed to just what pitches they use)? Pools every piece's n-grams
    together WITHIN each corpus first, then computes conditional entropy
    H(X_n | X_1..n-1) = H(joint n-gram) - H(context (n-1)-gram) for each
    corpus and compares them — the corpus-scale counterpart to
    conditional_entropy() (which works on one piece).

    Parameters
    ----------
    kern_dir_a, kern_dir_b : str or Path
        Two folders of kern files.
    names : tuple of 2 str
        Labels for the two corpora.
    n : int
        N-gram size (default 2: "given the previous note...").
    representation : 'pitch_class', 'note', 'scale_degree', 'interval', or 'contour'
    pattern : str
    plot : bool
        If True (default), show a side-by-side bar chart with values labeled.
    verbose : bool
        If True (default), print progress every 25 files per corpus.

    Returns
    -------
    dict with keys: entropy_a, entropy_b, difference, n, names

    Example
    -------
        result = compare_corpus_conditional_entropy(
            '../data/Essen/England', '../data/Essen/Italia', names=('English', 'Italian'))
    """
    def _pooled_conditional_entropy(kern_dir, label):
        path = Path(kern_dir)
        if not path.exists():
            print(f'Path not found: {kern_dir}')
            return 0.0

        files = sorted(path.glob(pattern)) if path.is_dir() else [path]
        joint_counts = Counter()
        context_counts = Counter()
        skipped = []
        for i, f in enumerate(files):
            if verbose and i % 25 == 0:
                print(f'  {label}: {i + 1}/{len(files)}...')
            try:
                seq = _symbol_sequence(str(f), by=representation)
                if len(seq) < n:
                    continue
                grams = get_ngrams(seq, n)
                joint_counts.update(grams)
                context_counts.update(g[:-1] for g in grams)
            except Exception as e:
                skipped.append((str(f), str(e)))
                if verbose:
                    print(f'  Skipped {f.name}: {e}')

        if skipped:
            print(f'{label}: skipped {len(skipped)} unreadable file(s).')

        h_joint = shannon_entropy(joint_counts)
        h_context = shannon_entropy(context_counts)
        return h_joint - h_context

    if verbose:
        print(f'Processing {names[0]}...')
    h_cond_a = _pooled_conditional_entropy(kern_dir_a, names[0])
    if verbose:
        print(f'Processing {names[1]}...')
    h_cond_b = _pooled_conditional_entropy(kern_dir_b, names[1])

    diff = h_cond_a - h_cond_b

    print(f'H(note | previous {n - 1}) — {names[0]}: {h_cond_a:.3f} bits')
    print(f'H(note | previous {n - 1}) — {names[1]}: {h_cond_b:.3f} bits')
    print(f'Difference ({names[0]} - {names[1]}): {diff:+.3f} bits')

    if plot:
        plt.figure(figsize=(6, 4.5))
        bars = plt.bar(names, [h_cond_a, h_cond_b], color=['steelblue', 'coral'],
                        edgecolor='white')
        for bar, val in zip(bars, [h_cond_a, h_cond_b]):
            plt.text(bar.get_x() + bar.get_width() / 2, val, f'{val:.3f}',
                      ha='center', va='bottom')
        plt.ylabel(f'H(note | previous {n - 1}) — bits')
        plt.title(f'Conditional entropy: {names[0]} vs {names[1]} '
                  f'({representation}, n={n})')
        plt.tight_layout()
        plt.show()

    return {'entropy_a': h_cond_a, 'entropy_b': h_cond_b, 'difference': diff,
            'n': n, 'names': names}


# ── Q8: has melodic predictability changed over MUSIC HISTORY? ──────────────

def date_from_kern_headers(file_path):
    """
    Extract a composition year (int) from a kern file's Humdrum reference
    records, checking in this order:
        1. !!!CDT — nominally "composition date", BUT in real-world kern
           files this field is almost always the COMPOSER'S OWN birth-death
           lifespan (e.g. '1756/1/27/-1791/12/5/' for Mozart), not the
           piece's date. We can't tell a genuine composition-date
           uncertainty window (e.g. '1781-1782') apart from a lifespan by
           punctuation alone, but we CAN tell by the GAP between the two
           years: composition windows span a few years; lifespans span
           decades. So if CDT has two years and they're more than 15 years
           apart, it's treated as a lifespan and skipped in favor of PDT.
        2. !!!PDT — publication date (empirically, the field that actually
           tracks real composition/publication years in most corpora).
        3. !!!CBY — composer birth year + 25, as a rough fallback estimate.
        4. None if nothing usable was found.

    Robustly handles formats like '1781/', 'c1781', 'ca. 1781',
    '1781-1782' (takes the first year), and multi-part Humdrum date
    strings like '1756/1/27/-1791/12/5/'.

    Parameters
    ----------
    file_path : str or Path

    Returns
    -------
    int (year) or None

    Example
    -------
        date_from_kern_headers('../data/humdrum_scores/Mozart/Sonatas/sonata01-1.krn')
    """
    try:
        with open(file_path, 'r', errors='ignore') as f:
            text = f.read()
    except Exception:
        return None

    def field(tag):
        m = re.search(rf'^!!!{tag}\s*:\s*(.*)$', text, re.MULTILINE)
        return m.group(1).strip() if m else None

    def years_in(raw):
        return [int(y) for y in re.findall(r'\d{4}', raw)]

    cdt = field('CDT')
    if cdt:
        years = years_in(cdt)
        if len(years) == 1:
            return years[0]
        elif len(years) >= 2 and (years[-1] - years[0]) <= 15:
            return years[0]
        # else: looks like a composer lifespan, not a composition date -- fall through

    pdt = field('PDT')
    if pdt:
        years = years_in(pdt)
        if years:
            return years[0]

    cby = field('CBY')
    if cby:
        years = years_in(cby)
        if years:
            return years[0] + 25

    return None


def entropy_over_time(kern_dirs, representation='scale_degree', min_year=1600,
                       max_year=1950, pattern='*.krn', smooth=True, plot=True,
                       verbose=True):
    """
    ONE-STOP: has melodic entropy/predictability changed over MUSIC HISTORY?
    Extracts a composition year for every piece in every folder in
    `kern_dirs` (via date_from_kern_headers()), computes Shannon entropy per
    piece, and plots entropy against year.

    Parameters
    ----------
    kern_dirs : list of (str or Path)
        One folder per composer/corpus group — each is labeled by its last
        folder name (e.g. '../data/humdrum_scores/Mozart' -> 'Mozart').
    representation : 'pitch_class', 'note', 'scale_degree', 'interval', or 'contour'
    min_year, max_year : int
        Pieces with dates outside this range are excluded.
    pattern : str
    smooth : bool
        If True (default), overlay a LOWESS smoothing curve (black) over
        the pooled scatter.
    plot : bool
        If True (default), show the scatter plot, colored by composer/corpus.
    verbose : bool
        If True (default), print progress every 25 files per folder.

    Returns
    -------
    pd.DataFrame — columns: tune_id, composer, year, entropy, n_notes, source_dir

    Always reports at the end how many files had a recoverable, in-range
    date vs. how many were skipped.

    Example
    -------
        df = entropy_over_time(['../data/humdrum_scores/Mozart',
                                 '../data/humdrum_scores/Beethoven'])
    """
    rows = []
    n_total = 0
    n_dated = 0

    for kern_dir in kern_dirs:
        path = Path(kern_dir)
        if not path.exists():
            print(f'Path not found: {kern_dir} -- skipping.')
            continue

        composer = path.name
        # recursive: composer/corpus folders in this course's data (e.g.
        # humdrum_scores/Mozart/Sonatas/, .../Quartets.Str/) are commonly
        # organized into genre subfolders, unlike the flatter corpora (Essen,
        # charlie_parker, ...) the other directory-scanning functions expect.
        files = sorted(path.rglob(pattern)) if path.is_dir() else [path]
        if verbose:
            print(f'{composer}: scanning {len(files)} file(s)...')

        for i, f in enumerate(files):
            n_total += 1
            if verbose and i % 25 == 0:
                print(f'  {i + 1}/{len(files)}...')
            try:
                year = date_from_kern_headers(str(f))
                if year is None or not (min_year <= year <= max_year):
                    continue
                seq = _symbol_sequence(str(f), by=representation)
                if not seq:
                    continue
                n_dated += 1
                rows.append({
                    'tune_id': f.stem,
                    'composer': composer,
                    'year': year,
                    'entropy': shannon_entropy(Counter(seq)),
                    'n_notes': len(seq),
                    'source_dir': str(kern_dir),
                })
            except Exception as e:
                if verbose:
                    print(f'  Skipped {f.name}: {e}')

    result = pd.DataFrame(rows)

    pct = (100 * n_dated / n_total) if n_total else 0.0
    print(f'Recovered usable dates for {n_dated}/{n_total} file(s) ({pct:.1f}%). '
          f'{n_total - n_dated} file(s) skipped (no date, date outside '
          f'{min_year}-{max_year}, or unreadable).')

    if result.empty:
        print('No dated pieces to plot.')
        return result

    if plot:
        import seaborn as sns
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=result, x='year', y='entropy', hue='composer',
                         alpha=0.7, s=45)
        if smooth and len(result) >= 5:
            try:
                from statsmodels.nonparametric.smoothers_lowess import lowess
                smoothed = lowess(result['entropy'], result['year'], frac=0.4)
                plt.plot(smoothed[:, 0], smoothed[:, 1], color='black',
                         linewidth=2.5, label='LOWESS trend')
            except ImportError:
                print('statsmodels not available -- skipping LOWESS smoothing.')
        plt.xlabel('Year')
        plt.ylabel(f'Entropy (bits) — {representation}')
        plt.title(f'Entropy over time ({representation})')
        plt.legend(title='Composer/corpus', bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.tight_layout()
        plt.show()

    return result
