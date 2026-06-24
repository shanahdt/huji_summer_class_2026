"""
utils/idyom.py — Predicting the next note: long-term and short-term models
Summer Institute 2026 · Hebrew University of Jerusalem

This module is the IDyOM-style capstone on top of information_theory.py's
entropy work: instead of just describing HOW MUCH uncertainty is in a
melody, these functions build actual predictive models and ask, note by
note, "how surprised should a listener be right here?"

Two kinds of model, the same distinction IDyOM (Pearce 2005) is built on:
    LTM (long-term model)  — trained ahead of time on a CORPUS of other
                              pieces; represents stable, learned style
                              knowledge ("what usually happens after this
                              context, across many pieces").
    STM (short-term model) — trained ONLINE, from scratch, on the piece
                              currently being heard; represents what's
                              been learned about THIS piece so far ("what's
                              happened after this context, in this piece,
                              up to now").
Combining the two (weighted by how confident/low-entropy each one's
prediction is) is IDyOM's actual mechanism for generating a surprise
("information content") value for every note in a melody.

Questions answered here, smallest to largest:
    1. How surprising is one prediction, given one model?
           -> NGramModel.predict_proba() + information_content()
    2. How surprising is each note in a piece, based only on what's been
       heard so far IN that piece (no outside training)?
           -> stm_information_content()
    3. ...based only on a model trained ahead of time on OTHER pieces?
           -> train_ltm_model() + ltm_information_content()
    4. What if we use BOTH — this piece's own patterns AND prior style
       knowledge — combined the way a listener would?
           -> combine_ltm_stm(), surprise_contour()
    5. Averaged over a whole corpus, which pieces/corpora are more
       surprising (predictable) than others?
           -> corpus_information_content()

Beginner usage
---------------
    from utils import stm_information_content, surprise_contour, train_ltm_model

    # STM only — no outside training needed:
    df, probs = stm_information_content('../data/happy_birthday.krn', n=3)

    # LTM + STM combined, with a plot:
    ltm = train_ltm_model('../data/Essen/Deutschl', n=3)
    result = surprise_contour('../data/Essen/England/england1.krn', ltm_model=ltm, n=3)

    # Whole-corpus summary:
    table = corpus_information_content('../data/Essen/England', ltm_model=ltm, n=3)
"""

from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .corpus import PITCH_CLASS_NAMES
from .information_theory import _symbol_sequence, shannon_entropy
from .ngrams import DEGREE_LABELS, _gather_files, get_ngrams


def _alphabet_for(by):
    """
    Internal helper: the fixed, known set of possible symbols for a given
    viewpoint — needed up front so models can be smoothed (see NGramModel)
    without ever hitting an unseen-symbol problem.

    Only 'pitch_class' and 'scale_degree' are supported here (NOT 'note')
    because note_sequence() includes octave, which has no fixed-size
    alphabet — Laplace smoothing over an unbounded vocabulary doesn't work.
    """
    if by == 'pitch_class':
        return list(PITCH_CLASS_NAMES)
    elif by == 'scale_degree':
        return list(DEGREE_LABELS)
    else:
        raise ValueError(
            "idyom.py only supports by='pitch_class' or by='scale_degree' "
            "(both have a fixed, known alphabet — needed for smoothing). "
            "'note' has unbounded vocabulary across octaves and isn't supported here.")


# ── The model: counts contexts -> next-symbol, with smoothing ───────────────

class NGramModel:
    """
    A smoothed n-gram model over a FIXED, known alphabet (pitch classes or
    scale degrees) — the shared machinery behind both the long-term model
    (LTM, trained once on a corpus) and the short-term model (STM, trained
    online as a piece unfolds). The only difference between LTM and STM is
    WHEN/HOW you call train()/update() — same class either way.

    Parameters
    ----------
    n : int
        N-gram order — the model conditions on the previous (n-1) symbols.
        n=1 means "no context, just the overall symbol frequencies."
    by : 'pitch_class' or 'scale_degree'
        Which fixed alphabet to smooth over — see _alphabet_for().
    alpha : float
        Additive (Lidstone) smoothing constant. 1.0 = classic Laplace
        smoothing. Smaller (e.g. 0.1-0.5) trusts the observed counts more;
        this matters most early on, before much has been seen.

    Example
    -------
        model = NGramModel(n=3, by='pitch_class')
        model.train(['C', 'D', 'E', 'D', 'C'])
        model.predict_proba(('D', 'E'))   # -> {'C': 0.09, 'C#': 0.02, ...}
    """

    def __init__(self, n=3, by='pitch_class', alpha=0.5):
        if n < 1:
            raise ValueError('n must be >= 1')
        self.n = n
        self.by = by
        self.alpha = alpha
        self.alphabet = _alphabet_for(by)
        self.context_counts = {}   # {context_tuple: Counter(next_symbol -> count)}

    def update(self, context, symbol):
        """Record one (context, next-symbol) observation. The online half of STM."""
        context = tuple(context)
        self.context_counts.setdefault(context, Counter())[symbol] += 1

    def train(self, sequence):
        """
        Train (or keep training) on a full sequence at once — slide an
        n-gram window across it and update() on every (context, symbol)
        pair. Used for batch-training the LTM on a corpus; you can also
        call this repeatedly across multiple pieces to pool their counts
        into one shared LTM.
        """
        if len(sequence) < self.n:
            return
        for gram in get_ngrams(list(sequence), self.n):
            context, symbol = gram[:-1], gram[-1]
            self.update(context, symbol)

    def predict_proba(self, context):
        """
        Predict a full probability distribution over the alphabet, given a
        context — the model's belief about what comes next.

        Returns
        -------
        dict {symbol: probability}, summing to 1, smoothed so every
        symbol in the alphabet always has SOME nonzero probability (even
        one this model has never seen in this exact context).
        """
        context = tuple(context)[-(self.n - 1):] if self.n > 1 else ()
        counts = self.context_counts.get(context, Counter())
        total = sum(counts.values())
        V = len(self.alphabet)
        return {s: (counts.get(s, 0) + self.alpha) / (total + self.alpha * V)
                for s in self.alphabet}

    def entropy(self, context):
        """Shannon entropy (bits) of this model's predictive distribution at a context."""
        return shannon_entropy(self.predict_proba(context))


def information_content(symbol, probs, base=2):
    """
    CORE MEASURE: information content (a.k.a. surprise) of one observed
    symbol under a predicted distribution: IC = -log_b(P(symbol)).

    0 = the model was certain and right. Bigger = the model was caught off
    guard — low predicted probability for what actually happened.

    Parameters
    ----------
    symbol : the observed value
    probs : dict {symbol: probability} — e.g. from NGramModel.predict_proba()
    base : float — log base (bits by default)

    Example
    -------
        probs = model.predict_proba(('D', 'E'))
        ic = information_content('C', probs)
    """
    p = probs.get(symbol, 1e-12)
    return float(-np.log(max(p, 1e-12)) / np.log(base))


# ── Q2: STM — what does THIS piece teach you about itself, as you go? ───────

def stm_information_content(file_path_or_score, n=3, by='pitch_class', alpha=0.5):
    """
    ONE-STOP, Q2: how surprising is each note, based ONLY on what's been
    heard so far IN this same piece? Builds a short-term model (STM) from
    scratch — it starts knowing nothing — and walks through the piece
    once, predicting each note from its (n-1)-note context BEFORE seeing
    it, then learning from it (online/incremental, exactly like a first-
    time listener).

    The first (n-1) notes have no full context yet and are skipped — IC is
    only reported from position n-1 onward.

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    n : int — n-gram order (context length = n-1). Default 3.
    by : 'pitch_class' or 'scale_degree'
    alpha : float — smoothing constant, see NGramModel.

    Returns
    -------
    df : pd.DataFrame — columns: position, symbol, entropy, ic_stm
    probs : list of dict — the predicted distribution at each position
            (kept separate since it's not naturally tabular; needed by
            combine_ltm_stm()).

    Example
    -------
        df, probs = stm_information_content('../data/happy_birthday.krn', n=3)
        df.plot(x='position', y='ic_stm')
    """
    seq = _symbol_sequence(file_path_or_score, by=by)
    stm = NGramModel(n=n, by=by, alpha=alpha)

    rows, probs = [], []
    for i in range(n - 1, len(seq)):
        context = seq[i - (n - 1):i]
        symbol = seq[i]
        p = stm.predict_proba(context)
        ic = information_content(symbol, p)
        rows.append({'position': i, 'symbol': symbol,
                     'entropy': shannon_entropy(p), 'ic_stm': ic})
        probs.append(p)
        stm.update(context, symbol)   # learn from it AFTER predicting — online

    return pd.DataFrame(rows), probs


# ── Q3: LTM — what does a model trained on OTHER pieces predict? ────────────

def train_ltm_model(source, n=3, by='pitch_class', pattern='*.krn', alpha=0.5, verbose=True):
    """
    ONE-STOP, Q3 (training half): build a long-term model (LTM) — train an
    n-gram model ahead of time on a whole corpus of OTHER pieces, pooling
    their counts into one shared model. This represents general style
    knowledge, independent of whatever piece you'll later test it on.

    Parameters
    ----------
    source : str, Path, or list
        A folder, single file, or list of files — same as describe_corpus().
    n : int — n-gram order. Should match whatever you'll use at test time.
    by : 'pitch_class' or 'scale_degree'
    pattern : str
    alpha : float — smoothing constant, see NGramModel.
    verbose : bool — print how many pieces were used.

    Returns
    -------
    NGramModel, trained on every piece in the corpus.

    Example
    -------
        ltm = train_ltm_model('../data/Essen/Deutschl', n=3, by='pitch_class')
    """
    files = _gather_files(source, pattern=pattern)
    model = NGramModel(n=n, by=by, alpha=alpha)
    used, skipped = 0, 0
    for f in files:
        try:
            seq = _symbol_sequence(f, by=by)
            model.train(seq)
            used += 1
        except Exception:
            skipped += 1
    if verbose:
        print(f'Trained LTM (n={n}, by={by}) on {used} piece(s)'
              + (f', skipped {skipped}' if skipped else '') + '.')
    return model


def ltm_information_content(file_path_or_score, ltm_model, n=None):
    """
    ONE-STOP, Q3 (testing half): how surprising is each note in this piece,
    according to a model trained ahead of time on OTHER pieces (no online
    learning — the LTM stays frozen while testing)?

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    ltm_model : NGramModel — from train_ltm_model()
    n : int, optional — defaults to ltm_model.n; only override if you know
        what you're doing (mismatched n breaks the context alignment
        combine_ltm_stm() relies on).

    Returns
    -------
    df : pd.DataFrame — columns: position, symbol, entropy, ic_ltm
    probs : list of dict — predicted distribution at each position

    Example
    -------
        ltm = train_ltm_model('../data/Essen/Deutschl', n=3)
        df, probs = ltm_information_content('../data/Essen/England/england1.krn', ltm)
    """
    n = n or ltm_model.n
    seq = _symbol_sequence(file_path_or_score, by=ltm_model.by)

    rows, probs = [], []
    for i in range(n - 1, len(seq)):
        context = seq[i - (n - 1):i]
        symbol = seq[i]
        p = ltm_model.predict_proba(context)
        ic = information_content(symbol, p)
        rows.append({'position': i, 'symbol': symbol,
                     'entropy': shannon_entropy(p), 'ic_ltm': ic})
        probs.append(p)

    return pd.DataFrame(rows), probs


# ── Q4: combine STM + LTM the way a listener actually would ──────────────────

def combine_ltm_stm(stm_df, stm_probs, ltm_df, ltm_probs, bias=1.0):
    """
    ONE-STOP, Q4: fuse the short-term (this piece) and long-term (prior
    style knowledge) predictions into one combined prediction, the way
    IDyOM does it — weighting each model's distribution by how CONFIDENT
    (low-entropy) it is at that exact moment, so whichever model currently
    "knows what's coming" contributes more.

        weight_i  ∝  (1 / (entropy_i + epsilon)) ** bias
        combined_prob(symbol) = Σ_i weight_i * p_i(symbol)

    Parameters
    ----------
    stm_df, stm_probs : from stm_information_content()
    ltm_df, ltm_probs : from ltm_information_content()
        Must come from the SAME piece, with the SAME n (so positions line
        up) — both functions index by absolute note position.
    bias : float
        How strongly entropy differences translate into weight differences.
        1.0 (default) = weight directly proportional to inverse entropy.
        Higher = more winner-take-all (the more confident model dominates).
        0 = ignore confidence, always average the two models equally.

    Returns
    -------
    pd.DataFrame — columns: position, symbol, ic_stm, ic_ltm, ic_combined,
    weight_stm, weight_ltm

    Example
    -------
        stm_df, stm_probs = stm_information_content(piece, n=3)
        ltm_df, ltm_probs = ltm_information_content(piece, ltm, n=3)
        combined = combine_ltm_stm(stm_df, stm_probs, ltm_df, ltm_probs)
    """
    merged = stm_df.merge(ltm_df, on=['position', 'symbol'], suffixes=('_stm', '_ltm'))
    if merged.empty:
        raise ValueError(
            "No overlapping (position, symbol) pairs between the STM and LTM "
            "results — did they come from the same piece, with the same n?")

    eps = 1e-9
    rows = []
    # stm_df/ltm_df may have been filtered by the merge — re-pull only the
    # probs whose position survived, in the same order as `merged`.
    stm_pos_to_idx = {p: i for i, p in enumerate(stm_df['position'])}
    ltm_pos_to_idx = {p: i for i, p in enumerate(ltm_df['position'])}

    for _, row in merged.iterrows():
        p_stm = stm_probs[stm_pos_to_idx[row['position']]]
        p_ltm = ltm_probs[ltm_pos_to_idx[row['position']]]
        h_stm = shannon_entropy(p_stm)
        h_ltm = shannon_entropy(p_ltm)

        w_stm_raw = (1.0 / (h_stm + eps)) ** bias
        w_ltm_raw = (1.0 / (h_ltm + eps)) ** bias
        w_stm = w_stm_raw / (w_stm_raw + w_ltm_raw)
        w_ltm = 1.0 - w_stm

        combined_probs = {s: w_stm * p_stm[s] + w_ltm * p_ltm[s] for s in p_stm}
        ic_combined = information_content(row['symbol'], combined_probs)

        rows.append({
            'position': row['position'], 'symbol': row['symbol'],
            'ic_stm': row['ic_stm'], 'ic_ltm': row['ic_ltm'],
            'ic_combined': ic_combined, 'weight_stm': w_stm, 'weight_ltm': w_ltm,
        })

    return pd.DataFrame(rows)


def surprise_contour(file_path_or_score, ltm_model=None, n=3, by='pitch_class',
                      alpha=0.5, bias=1.0, plot=True, figsize=(10, 4.5), title=None):
    """
    ONE-STOP, Q4 (the headline IDyOM plot): how surprising is each note in
    this piece, over time? Always runs the STM (no setup required); if you
    pass a trained `ltm_model` (see train_ltm_model()), also runs the LTM
    and combines the two into a single entropy-weighted surprise contour —
    the closest thing in this package to "real IDyOM."

    Peaks in the contour are the notes a listener should find most
    surprising — often phrase boundaries, unexpected leaps, or chromatic
    notes outside the established context.

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    ltm_model : NGramModel, optional
        From train_ltm_model(). If omitted, only the STM is used (no
        outside training needed at all — works on a single piece).
    n : int — n-gram order. If ltm_model is given, its own `n` is used
        instead, so STM and LTM stay aligned.
    by : 'pitch_class' or 'scale_degree' (ignored if ltm_model given —
         uses ltm_model.by instead, for the same alignment reason).
    alpha : float — STM smoothing constant.
    bias : float — see combine_ltm_stm().
    plot, figsize, title

    Returns
    -------
    pd.DataFrame — the combined table (ic_combined, ic_stm, ic_ltm,
    weights) if ltm_model was given, otherwise just the STM table.

    Example
    -------
        # STM only:
        df = surprise_contour('../data/happy_birthday.krn', n=3)

        # STM + LTM combined:
        ltm = train_ltm_model('../data/Essen/Deutschl', n=3)
        df = surprise_contour('../data/Essen/England/england1.krn', ltm_model=ltm)
    """
    if ltm_model is not None:
        n, by = ltm_model.n, ltm_model.by

    stm_df, stm_probs = stm_information_content(file_path_or_score, n=n, by=by, alpha=alpha)

    if ltm_model is not None:
        ltm_df, ltm_probs = ltm_information_content(file_path_or_score, ltm_model, n=n)
        result = combine_ltm_stm(stm_df, stm_probs, ltm_df, ltm_probs, bias=bias)
        y_col = 'ic_combined'
    else:
        result = stm_df
        y_col = 'ic_stm'

    mean_ic = result[y_col].mean()
    peak_row = result.loc[result[y_col].idxmax()]
    print(f'Mean information content: {mean_ic:.3f} bits')
    print(f"Most surprising note: '{peak_row['symbol']}' at position "
          f"{int(peak_row['position'])} ({peak_row[y_col]:.3f} bits)")

    if plot:
        plt.figure(figsize=figsize)
        if ltm_model is not None:
            plt.plot(result['position'], result['ic_stm'], color='lightsteelblue',
                      linewidth=1, label='STM only', alpha=0.7)
            plt.plot(result['position'], result['ic_ltm'], color='peachpuff',
                      linewidth=1, label='LTM only', alpha=0.7)
            plt.plot(result['position'], result[y_col], color='steelblue',
                      linewidth=2, label='Combined')
            plt.legend()
        else:
            plt.plot(result['position'], result[y_col], color='steelblue', linewidth=2)
        plt.axhline(mean_ic, color='gray', linestyle='--', linewidth=1)
        plt.title(title or f'Surprise contour ({y_col}) — mean = {mean_ic:.2f} bits')
        plt.xlabel('Note position')
        plt.ylabel('Information content (bits)')
        plt.tight_layout()
        plt.show()

    return result


# ── Q5: averaged over a whole corpus ────────────────────────────────────────

def corpus_information_content(source, ltm_model=None, n=3, by='pitch_class',
                                 pattern='*.krn', alpha=0.5, bias=1.0,
                                 plot=True, figsize=(9, 4.5), title=None):
    """
    ONE-STOP, Q5 (the biggest question in this module): averaged over a
    whole corpus, how surprising/predictable is each piece? Runs
    surprise_contour() (without plotting each one) on every file, and
    summarizes mean information content per piece.

    The returned table is in exactly the same shape as
    compare_keyfinding_corpus()'s `results` table (one row per piece,
    a numeric column to compare) — relabel/merge it the same way to feed
    ttest_algorithm_correlations() or compare_algorithms_anova() from
    keyfinding.py if you want to test a hypothesis about WHICH corpus (or
    which n, or which model) produces more/less surprising melodies.

    Parameters
    ----------
    source : str, Path, or list — folder, file, or list of files
    ltm_model : NGramModel, optional — see surprise_contour()
    n, by, pattern, alpha, bias — see surprise_contour() / train_ltm_model()
    plot : bool — if True, show a histogram of mean IC across pieces
    figsize, title

    Returns
    -------
    pd.DataFrame — columns: tune_id, n_notes, mean_ic

    Example
    -------
        ltm = train_ltm_model('../data/Essen/Deutschl', n=3)
        table = corpus_information_content('../data/Essen/England', ltm_model=ltm, n=3)
        table.sort_values('mean_ic', ascending=False).head()   # most surprising tunes
    """
    files = _gather_files(source, pattern=pattern)
    rows, skipped = [], 0
    for f in files:
        try:
            result = surprise_contour(f, ltm_model=ltm_model, n=n, by=by,
                                       alpha=alpha, bias=bias, plot=False)
            y_col = 'ic_combined' if ltm_model is not None else 'ic_stm'
            rows.append({'tune_id': f, 'n_notes': len(result), 'mean_ic': result[y_col].mean()})
        except Exception:
            skipped += 1

    table = pd.DataFrame(rows)
    print(f'Computed information content for {len(table)} piece(s)'
          + (f', skipped {skipped}' if skipped else '') + '.')

    if plot and not table.empty:
        plt.figure(figsize=figsize)
        plt.hist(table['mean_ic'], bins=15, color='steelblue', edgecolor='white')
        plt.axvline(table['mean_ic'].mean(), color='coral', linestyle='--',
                    label=f"mean = {table['mean_ic'].mean():.2f} bits")
        plt.title(title or 'Mean information content per piece')
        plt.xlabel('Mean information content (bits)')
        plt.ylabel('Number of pieces')
        plt.legend()
        plt.tight_layout()
        plt.show()

    return table
