"""
utils/similarity.py — Comparing melodies and corpora
Summer Institute 2026 · Hebrew University of Jerusalem

This is the other half of the Day 4 question (see information_theory.py for
the entropy half): "how similar are two melodies, or two corpora, to each
other?" — three families of measure, roughly simplest to most flexible:

    1. Set overlap          -> jaccard() / jaccard_matrix()
       "What fraction of the bigrams/pitches these two share, out of
       everything either one uses?" Symmetric, treats both sides equally.

    2. Edit distance         -> edit_distance() / melodic_edit_distance()
       "How many note-by-note edits turn melody A into melody B?" Cares
       about ORDER, not just which notes appear — two melodies can share
       every pitch and still have a large edit distance if they're
       sequenced differently.

    3. Tversky index         -> tversky_index() / tversky_matrix()
       A generalization of Jaccard/Dice that can be ASYMMETRIC — useful
       when "A is similar to B" shouldn't be assumed to equal "B is
       similar to A" (e.g. comparing an ornamented version of a tune
       against a plain "prototype" version).

The functions above compare two whole CORPORA (via bigram Counters). For
comparing two individual PIECES directly from their file paths, use:

    contour_similarity()      -> melodic direction (up/down/same) agreement
    ngram_similarity()        -> per-piece sibling of jaccard()
    melodic_edit_distance()   -> per-piece sibling of edit_distance()
    similarity_matrices()     -> ONE-STOP: build all three as N x N tables
                                  for a whole list of tunes in one call

Beginner usage
---------------
    from utils import jaccard, edit_distance, melodic_edit_distance, tversky_index
    j = jaccard(parker_counter, dizzy_counter)
    d = edit_distance(['C', 'D', 'E'], ['C', 'D', 'G'])
    d = melodic_edit_distance('../data/tune1.krn', '../data/tune2.krn')
    s = tversky_index(set_a, set_b, alpha=0.1, beta=0.9)

    from utils import contour_similarity, ngram_similarity, similarity_matrices
    contour_similarity('../data/tune1.krn', '../data/tune2.krn')
    ngram_similarity('../data/tune1.krn', '../data/tune2.krn', n=3)
    matrices, tids = similarity_matrices(files_subset, plot=True)
"""

import re
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from music21 import converter
from music21.pitch import Pitch

from .information_theory import _symbol_sequence
from .ngrams import DEGREE_LABELS, get_ngrams, note_sequence, _gather_files
from .corpus import PITCH_CLASS_NAMES, load_corpus


def jaccard(counter1, counter2, top_n=50):
    """
    Compute Jaccard similarity between the top-N bigrams of two Counters.

    Jaccard = |intersection| / |union|

    Returns a float in [0, 1]. Identical top-N sets → 1.0; no overlap → 0.0.

    This is a SPECIAL CASE of tversky_index() below, with alpha=beta=1 — see
    that function for an asymmetric version of this same idea.

    Parameters
    ----------
    counter1, counter2 : Counter
        Bigram counters (e.g. from extract_scale_degree_bigrams).
    top_n : int
        Number of most-common bigrams to compare (default 50).

    Example
    -------
        j = jaccard(parker_counter, dizzy_counter, top_n=50)
        print(f'Parker vs Dizzy: {j:.3f}')
    """
    s1 = set(dict(counter1.most_common(top_n)).keys())
    s2 = set(dict(counter2.most_common(top_n)).keys())
    if not s1 and not s2:
        return 1.0
    return len(s1 & s2) / len(s1 | s2)


def jaccard_matrix(counters, top_n=50):
    """
    Build a pairwise Jaccard similarity matrix from a dict of Counters.

    Parameters
    ----------
    counters : dict
        {label: Counter} — e.g. {'Parker': counter1, 'Dizzy': counter2}
    top_n : int
        Top-N bigrams used per counter (default 50).

    Returns
    -------
    pd.DataFrame — symmetric matrix of Jaccard scores.

    Example
    -------
        counters = {
            'Parker': parker_counter,
            'Dizzy':  dizzy_counter,
            'Freygish': freygish_counter,
        }
        df = jaccard_matrix(counters)
        sns.heatmap(df, annot=True, fmt='.2f', cmap='Blues')
    """
    labels = list(counters.keys())
    matrix = pd.DataFrame(index=labels, columns=labels, dtype=float)
    for l1 in labels:
        for l2 in labels:
            matrix.loc[l1, l2] = jaccard(counters[l1], counters[l2], top_n)
    return matrix


# ── Edit distance: similarity that cares about ORDER ─────────────────────────

def edit_distance(seq_a, seq_b, substitution_cost=None):
    """
    Levenshtein (edit) distance between two sequences — the minimum cost of
    insertions, deletions, and substitutions needed to turn seq_a into
    seq_b. Works on ANY sequence of comparable items: characters, note
    names, pitch classes, scale degrees, whatever you pass in.

    Unlike jaccard() (which only cares which items appear, not their
    order), edit distance is sensitive to SEQUENCE — 'CDE' and 'EDC' share
    every pitch but have a large edit distance.

    Parameters
    ----------
    seq_a, seq_b : sequence
        Two sequences to compare (e.g. two note-name lists from
        note_sequence()).
    substitution_cost : callable, optional
        cost_fn(a, b) -> float, the cost of substituting item a for item b.
        Default: 1 if a != b else 0 (the classic "any mismatch costs the
        same" version). Pass your own function for a more musically aware
        distance — e.g. cost based on semitone distance, so swapping C for
        C# costs less than swapping C for F# (see melodic_edit_distance()'s
        weighted=True for a ready-made version of this).

    Returns
    -------
    float — the edit distance. 0 = identical sequences.

    Example
    -------
        edit_distance(['C', 'D', 'E', 'F'], ['C', 'D', 'G', 'F'])   # -> 1
        edit_distance(midi_a, midi_b,
                      substitution_cost=lambda a, b: abs(a - b) / 12)
    """
    a, b = list(seq_a), list(seq_b)
    n, m = len(a), len(b)
    if n == 0:
        return float(m)
    if m == 0:
        return float(n)

    cost_fn = substitution_cost or (lambda x, y: 0.0 if x == y else 1.0)

    prev = list(range(m + 1))
    for i in range(1, n + 1):
        curr = [float(i)] + [0.0] * m
        for j in range(1, m + 1):
            sub = prev[j - 1] + cost_fn(a[i - 1], b[j - 1])
            delete = prev[j] + 1
            insert = curr[j - 1] + 1
            curr[j] = min(sub, delete, insert)
        prev = curr
    return float(prev[m])


def normalized_edit_distance(seq_a, seq_b, substitution_cost=None):
    """
    edit_distance(), scaled to [0, 1] by dividing by the longer sequence's
    length — handy for comparing melodies of different lengths, or for
    turning the distance into a similarity score (1 - this value).

    Example
    -------
        d = normalized_edit_distance(seq_a, seq_b)
        similarity = 1 - d
    """
    a, b = list(seq_a), list(seq_b)
    if not a and not b:
        return 0.0
    return edit_distance(a, b, substitution_cost) / max(len(a), len(b))


def _semitone_substitution_cost(by):
    """
    Internal helper: build a substitution-cost function that charges less
    for swapping NEARBY pitches than distant ones (max cost 1.0, for a
    tritone swap; 0.0 for an exact match), instead of edit_distance()'s
    default "any mismatch costs the same".
    """
    if by == 'scale_degree':
        index_map = {label: i for i, label in enumerate(DEGREE_LABELS)}
    else:
        index_map = {name: i for i, name in enumerate(PITCH_CLASS_NAMES)}
    strip_octave = re.compile(r'-?\d+$')

    def cost(x, y):
        if x == y:
            return 0.0
        xs = strip_octave.sub('', x) if by == 'note' else x
        ys = strip_octave.sub('', y) if by == 'note' else y
        if xs in index_map and ys in index_map:
            diff = abs(index_map[xs] - index_map[ys]) % 12
            diff = min(diff, 12 - diff)
            return diff / 6.0
        return 1.0

    return cost


def melodic_edit_distance(file_path_or_score_a, file_path_or_score_b,
                           by='pitch_class', weighted=False, normalize=True):
    """
    ONE-STOP: edit distance between two PIECES, instead of two raw
    sequences you've already extracted yourself.

    Parameters
    ----------
    file_path_or_score_a, file_path_or_score_b : str, Path, or music21 Score
    by : 'pitch_class', 'note', or 'scale_degree'
        How to represent each note before comparing. 'scale_degree' is
        key-independent, so it's the fairer choice for comparing melodies
        in different keys.
    weighted : bool
        If False (default): plain edit distance — any pitch mismatch costs
        1, regardless of how far apart the two pitches are. If True: cost
        is proportional to the distance between pitches in semitones
        (wrapped to 0-6, i.e. 0 = same pitch, 1.0 = a tritone apart) — a
        neighboring-note substitution costs less than a tritone leap.
    normalize : bool
        If True (default), scale to [0, 1] by the longer melody's length.

    Returns
    -------
    float — distance (0 = identical)

    Example
    -------
        d = melodic_edit_distance('../data/tune1.krn', '../data/tune2.krn')
        d = melodic_edit_distance('../data/tune1.krn', '../data/tune2.krn',
                                   by='scale_degree', weighted=True)
    """
    seq_a = _symbol_sequence(file_path_or_score_a, by=by)
    seq_b = _symbol_sequence(file_path_or_score_b, by=by)

    cost_fn = _semitone_substitution_cost(by) if weighted else None
    fn = normalized_edit_distance if normalize else edit_distance
    return fn(seq_a, seq_b, substitution_cost=cost_fn)


# ── Tversky index: a generalized, possibly ASYMMETRIC similarity ────────────

def tversky_index(set_a, set_b, alpha=0.5, beta=0.5):
    """
    Tversky's (1977) similarity index — a generalization of Jaccard and
    Dice that lets you weight "what's distinctively in A but not B" (the
    alpha term) separately from "what's distinctively in B but not A" (the
    beta term), instead of treating both directions of mismatch as equally
    important.

        S(A, B) = |A ∩ B| / (|A ∩ B| + alpha*|A - B| + beta*|B - A|)

    Special cases you already know:
        alpha = beta = 1     -> exactly jaccard()
        alpha = beta = 0.5   -> Dice's coefficient

    Tversky's own motivation was PSYCHOLOGICAL, not just mathematical: he
    showed people don't judge similarity symmetrically — e.g. subjects
    rated "North Korea is similar to China" as truer than "China is similar
    to North Korea", because the more feature-rich/prototypical item
    (China) contributes a smaller PROPORTION of its features as "missing"
    from the comparison. With alpha != beta, this function can reproduce
    that asymmetry: tversky_index(A, B) != tversky_index(B, A) in general.

    For melodies, this lets you ask asymmetric questions like: "is this
    ornamented performance more similar to its plain 'prototype' tune than
    the prototype is to the ornamented version?" — useful whenever one set
    is more sparse/skeletal and the other more elaborated.

    Parameters
    ----------
    set_a, set_b : set, or anything set()-able (list, Counter.keys(), etc.)
        Two sets of features — e.g. sets of bigrams, pitch classes, etc.
    alpha : float
        Weight on features distinctively in A (A - B). Default 0.5.
    beta : float
        Weight on features distinctively in B (B - A). Default 0.5.

    Returns
    -------
    float in [0, 1]. 1.0 = identical sets (or both empty).

    Example
    -------
        a = set(parker_counter.keys())
        b = set(dizzy_counter.keys())
        tversky_index(a, b)                       # symmetric, Dice-like
        tversky_index(a, b, alpha=1, beta=1)       # == jaccard-style ratio
        tversky_index(a, b, alpha=0.1, beta=0.9)   # asymmetric: penalize
                                                    # B's distinctive features
                                                    # much more than A's
    """
    a, b = set(set_a), set(set_b)
    if not a and not b:
        return 1.0
    intersection = len(a & b)
    only_a = len(a - b)
    only_b = len(b - a)
    denom = intersection + alpha * only_a + beta * only_b
    if denom == 0:
        return 1.0
    return intersection / denom


def tversky_matrix(counters, alpha=0.5, beta=0.5, top_n=50):
    """
    Pairwise Tversky index matrix from a dict of Counters — same idea as
    jaccard_matrix(), but with the alpha/beta knobs.

    IMPORTANT: unless alpha == beta, this matrix is NOT symmetric —
    matrix.loc[X, Y] can differ from matrix.loc[Y, X]. That asymmetry IS
    the point (see tversky_index()) — read each row as "how similar is the
    ROW corpus to the COLUMN corpus", not the other way around.

    Parameters
    ----------
    counters : dict — {label: Counter}
    alpha, beta : float — see tversky_index()
    top_n : int — top-N most common items per Counter to compare

    Returns
    -------
    pd.DataFrame

    Example
    -------
        counters = {'Parker': parker_counter, 'Dizzy': dizzy_counter}
        df = tversky_matrix(counters, alpha=0.2, beta=0.8)
        sns.heatmap(df, annot=True, fmt='.2f', cmap='Blues')
    """
    labels = list(counters.keys())
    sets = {l: set(dict(c.most_common(top_n)).keys()) for l, c in counters.items()}
    matrix = pd.DataFrame(index=labels, columns=labels, dtype=float)
    for l1 in labels:
        for l2 in labels:
            matrix.loc[l1, l2] = tversky_index(sets[l1], sets[l2], alpha=alpha, beta=beta)
    return matrix


# ── Comparing two individual PIECES (as opposed to two corpora above) ───────

def _contour_from_notes(note_names):
    """
    Internal helper: turn a list of note names (with octave, e.g. from
    note_sequence()) into a direction sequence: +1 = moved up, -1 = moved
    down, 0 = repeated pitch, one entry per note-to-note move.
    """
    ps = [Pitch(p).ps for p in note_names]
    return [1 if ps[i] > ps[i - 1] else (-1 if ps[i] < ps[i - 1] else 0)
            for i in range(1, len(ps))]


def _contour_agreement(contour_a, contour_b):
    """Internal helper: fraction of aligned up/down/same moves that match."""
    n = min(len(contour_a), len(contour_b))
    if n == 0:
        return 0.0
    return sum(1 for a, b in zip(contour_a[:n], contour_b[:n]) if a == b) / n


def contour_similarity(file_path_or_score_a, file_path_or_score_b):
    """
    ONE-STOP: how often do two melodies move the same direction (up, down,
    or repeat) from one note to the next? Always uses absolute pitch height
    (not scale degree or pitch class) — contour is about real melodic
    shape, so transposition doesn't matter but octave leaps do.

    Returns
    -------
    float in [0, 1]. 1.0 = identical note-to-note direction pattern (the
    actual notes can still differ); 0.0 = no agreement at all.

    Example
    -------
        contour_similarity('../data/tune1.krn', '../data/tune2.krn')
    """
    contour_a = _contour_from_notes(note_sequence(file_path_or_score_a))
    contour_b = _contour_from_notes(note_sequence(file_path_or_score_b))
    return _contour_agreement(contour_a, contour_b)


def ngram_similarity(file_path_or_score_a, file_path_or_score_b, n=3, by='scale_degree'):
    """
    ONE-STOP: Jaccard similarity of n-grams between two individual PIECES —
    the per-piece sibling of jaccard() above (which compares two whole
    CORPORA via pre-built bigram Counters). Built from tversky_index() with
    alpha=beta=1, which is exactly Jaccard — see tversky_index() if you want
    an asymmetric version of this same comparison.

    Parameters
    ----------
    file_path_or_score_a, file_path_or_score_b : str, Path, or music21 Score
    n : int
        N-gram size (default 3, i.e. trigrams).
    by : 'pitch_class', 'note', or 'scale_degree'
        How to represent each note before comparing (default 'scale_degree',
        so pieces in different keys are still comparable).

    Returns
    -------
    float in [0, 1]. 1.0 = identical sets of n-grams; 0.0 = no overlap.

    Example
    -------
        ngram_similarity('../data/tune1.krn', '../data/tune2.krn', n=3)
    """
    seq_a = _symbol_sequence(file_path_or_score_a, by=by)
    seq_b = _symbol_sequence(file_path_or_score_b, by=by)
    a = set(get_ngrams(seq_a, n))
    b = set(get_ngrams(seq_b, n))
    return tversky_index(a, b, alpha=1, beta=1)


def similarity_matrices(files, metrics=('edit', 'jaccard', 'contour'), by='scale_degree',
                         n=3, weighted=False, tune_ids=None, pattern='*.krn',
                         verbose=False, plot=False, figsize=None):
    """
    ONE-STOP: build pairwise DISTANCE matrices for a list of tunes, for one
    or more similarity metrics, in a single pass over the files — this is
    the "build a recommender-style similarity table for N tunes" step.

    Each file is parsed exactly ONCE (not once per metric, not once per
    pair) and converted to the sequences each metric needs, so this stays
    fast even for the 'jaccard'+'edit'+'contour' combination.

    Parameters
    ----------
    files : list of str/Path, or a folder path
        Tunes to compare. If a folder, every file matching `pattern` is
        used (alphabetical order).
    metrics : tuple/list of {'edit', 'jaccard', 'contour'}
        Which distance(s) to compute (default: all three).
            'edit'    -> normalized edit distance (see melodic_edit_distance)
            'jaccard' -> 1 - ngram_similarity() (n-gram overlap)
            'contour' -> 1 - contour_similarity() (direction agreement)
    by : 'pitch_class', 'note', or 'scale_degree'
        Representation used for 'edit' and 'jaccard' (default 'scale_degree'
        — key-independent). 'contour' always uses absolute pitch height.
    n : int
        N-gram size for the 'jaccard' metric (default 3).
    weighted : bool
        Passed through to the 'edit' metric — see melodic_edit_distance().
    tune_ids : list of str, optional
        Labels for each file. Default: each file's stem (filename without
        extension).
    pattern : str
        Glob pattern used only if `files` is a folder (default '*.krn').
    verbose : bool
        If True, print progress every 25 files while parsing.
    plot : bool
        If True, show a heatmap per metric, side by side.

    Returns
    -------
    matrices : dict {metric_name: pd.DataFrame}
        Each an N x N distance matrix (0 = identical), indexed/columned by
        the returned tune_ids.
    tune_ids : list of str
        Labels actually used (unreadable files are skipped and dropped).

    Example
    -------
        matrices, tids = similarity_matrices(files_subset, plot=True, verbose=True)
        edit_mat, jac_mat, con_mat = matrices['edit'], matrices['jaccard'], matrices['contour']
    """
    file_list = _gather_files(files, pattern)
    if tune_ids is None:
        tune_ids = [Path(f).stem for f in file_list]
    if len(tune_ids) != len(file_list):
        raise ValueError(
            f'tune_ids has {len(tune_ids)} entries but {len(file_list)} files were found.'
        )

    from music21 import converter  # local import: notebooks shouldn't need this directly

    cache = {}
    skipped = []
    for i, (f, tid) in enumerate(zip(file_list, tune_ids)):
        if verbose and i % 25 == 0:
            print(f'  {i + 1}/{len(file_list)}...')
        try:
            score = converter.parse(str(f))
            cache[tid] = {
                'by_seq': _symbol_sequence(score, by=by),
                'notes': note_sequence(score),
            }
        except Exception as e:
            skipped.append((f, str(e)))

    if skipped:
        print(f"Skipped {len(skipped)} unreadable file(s): "
              f"{', '.join(str(f) for f, _ in skipped[:5])}"
              f"{'...' if len(skipped) > 5 else ''}")

    good_ids = [t for t in tune_ids if t in cache]
    if not good_ids:
        raise ValueError('No files could be read — check the paths/pattern you passed in.')
    nn = len(good_ids)
    cost_fn = _semitone_substitution_cost(by) if weighted else None

    matrices = {}

    if 'edit' in metrics:
        mat = np.zeros((nn, nn))
        for i, a in enumerate(good_ids):
            for j, b in enumerate(good_ids):
                mat[i, j] = normalized_edit_distance(
                    cache[a]['by_seq'], cache[b]['by_seq'], substitution_cost=cost_fn
                )
        matrices['edit'] = pd.DataFrame(mat, index=good_ids, columns=good_ids)

    if 'jaccard' in metrics:
        mat = np.zeros((nn, nn))
        ngram_sets = {t: set(get_ngrams(cache[t]['by_seq'], n)) for t in good_ids}
        for i, a in enumerate(good_ids):
            for j, b in enumerate(good_ids):
                mat[i, j] = 1 - tversky_index(ngram_sets[a], ngram_sets[b], alpha=1, beta=1)
        matrices['jaccard'] = pd.DataFrame(mat, index=good_ids, columns=good_ids)

    if 'contour' in metrics:
        mat = np.zeros((nn, nn))
        contours = {t: _contour_from_notes(cache[t]['notes']) for t in good_ids}
        for i, a in enumerate(good_ids):
            for j, b in enumerate(good_ids):
                mat[i, j] = 1 - _contour_agreement(contours[a], contours[b])
        matrices['contour'] = pd.DataFrame(mat, index=good_ids, columns=good_ids)

    if plot and matrices:
        fig, axes = plt.subplots(1, len(matrices), figsize=figsize or (5 * len(matrices), 4))
        axes = np.atleast_1d(axes)
        for ax, (name, mat) in zip(axes, matrices.items()):
            sns.heatmap(mat, ax=ax, cmap='YlOrRd', xticklabels=False, yticklabels=False)
            ax.set_title(name.capitalize())
        fig.suptitle(f'Pairwise distance — {nn} tunes (darker = MORE different)')
        plt.tight_layout()
        plt.show()

    return matrices, good_ids


# ── Spatial distance: similarity as "closeness in a feature space" ──────────
#
# This is a FOURTH family, distinct from the three above: instead of
# comparing sequences or sets directly, reduce each piece to a handful of
# numeric features (a point in space), then measure how close two points
# are. sim(A, B) = 1 / (1 + distance(A, B)) -- closer points are more
# similar, identical points score 1.0.

def melodic_feature_vector(file_path_or_score, features=('note_density', 'tonic_prevalence',
                                                           'pitch_range', 'mean_interval')):
    """
    Reduce one piece to a small vector of numeric features -- a "point in
    space" for the spatial-distance view of similarity (as opposed to the
    sequence/set views used by edit distance, Jaccard, and Tversky above).

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    features : tuple of str
        Which features to compute, any of:
            'note_density'     -> notes per quarter-note of music (tempo-
                                   independent measure of how busy the line is)
            'tonic_prevalence'  -> fraction of notes that are scale-degree 1
                                   (relative to the piece's own detected key)
            'pitch_range'       -> highest minus lowest MIDI pitch (semitones)
            'mean_interval'     -> mean absolute size of melodic leaps (semitones)

    Returns
    -------
    pd.Series indexed by the requested feature names.

    Example
    -------
        melodic_feature_vector('../data/tune1.krn')
        melodic_feature_vector('../data/tune1.krn', features=('note_density', 'pitch_range'))
    """
    score = (converter.parse(str(file_path_or_score))
             if isinstance(file_path_or_score, (str, Path))
             else file_path_or_score)

    notes = list(score.recurse().notes)
    midi_vals = []
    for element in notes:
        pitches = element.pitches if element.isChord else [element.pitch]
        midi_vals.append(int(pitches[0].midi))

    values = {}
    if 'note_density' in features:
        duration = float(score.duration.quarterLength) or 1.0
        values['note_density'] = len(notes) / duration
    if 'tonic_prevalence' in features:
        from .ngrams import scale_degree_sequence
        degrees = scale_degree_sequence(score)
        values['tonic_prevalence'] = (degrees.count('1') / len(degrees)) if degrees else 0.0
    if 'pitch_range' in features:
        values['pitch_range'] = float(max(midi_vals) - min(midi_vals)) if midi_vals else 0.0
    if 'mean_interval' in features:
        if len(midi_vals) > 1:
            intervals = [abs(b - a) for a, b in zip(midi_vals, midi_vals[1:])]
            values['mean_interval'] = float(np.mean(intervals))
        else:
            values['mean_interval'] = 0.0

    return pd.Series(values, index=list(features))


def feature_matrix(files, features=('note_density', 'tonic_prevalence',
                                     'pitch_range', 'mean_interval'),
                    tune_ids=None, pattern='*.krn', verbose=False):
    """
    ONE-STOP: build a tune x feature table -- one melodic_feature_vector()
    row per file -- ready to hand to spatial_similarity_matrix().

    Parameters
    ----------
    files : list of str/Path, or a folder path
    features : tuple of str -- see melodic_feature_vector()
    tune_ids : list of str, optional -- default: each file's stem
    pattern : str -- glob pattern used only if `files` is a folder
    verbose : bool -- print progress every 25 files

    Returns
    -------
    pd.DataFrame, one row per tune, one column per feature.

    Example
    -------
        feats = feature_matrix(files_subset)
        sim = spatial_similarity_matrix(feats, plot=True)
    """
    file_list = _gather_files(files, pattern)
    if tune_ids is None:
        tune_ids = [Path(f).stem for f in file_list]

    rows = {}
    skipped = []
    for i, (f, tid) in enumerate(zip(file_list, tune_ids)):
        if verbose and i % 25 == 0:
            print(f'  {i + 1}/{len(file_list)}...')
        try:
            rows[tid] = melodic_feature_vector(f, features=features)
        except Exception as e:
            skipped.append((f, str(e)))

    if skipped:
        print(f"Skipped {len(skipped)} unreadable file(s): "
              f"{', '.join(str(f) for f, _ in skipped[:5])}"
              f"{'...' if len(skipped) > 5 else ''}")

    if not rows:
        raise ValueError('No files could be read -- check the paths/pattern you passed in.')

    return pd.DataFrame(rows).T


def spatial_similarity(vec_a, vec_b):
    """
    sim(A, B) = 1 / (1 + Euclidean distance between A and B) -- the
    textbook "similarity as inverse distance" formula: closer points in
    feature space score closer to 1.0, distant points score closer to 0.0.

    IMPORTANT: this is sensitive to the SCALE of each feature -- a feature
    measured in big numbers (e.g. note counts) will dominate one measured
    in small numbers (e.g. proportions) unless you standardize first. See
    spatial_similarity_matrix(standardize=True), which does this for you.

    Parameters
    ----------
    vec_a, vec_b : pd.Series, dict, or array-like
        Two feature vectors of the same length (e.g. from melodic_feature_vector()).

    Returns
    -------
    float in (0, 1]. 1.0 = identical points.

    Example
    -------
        a = melodic_feature_vector('../data/tune1.krn')
        b = melodic_feature_vector('../data/tune2.krn')
        spatial_similarity(a, b)
    """
    a = np.asarray(vec_a.values if isinstance(vec_a, pd.Series) else list(vec_a), dtype=float)
    b = np.asarray(vec_b.values if isinstance(vec_b, pd.Series) else list(vec_b), dtype=float)
    distance = float(np.sqrt(np.sum((a - b) ** 2)))
    return 1.0 / (1.0 + distance)


def spatial_similarity_matrix(feature_df, standardize=True, plot=False):
    """
    Pairwise spatial_similarity() matrix for every row in a tune x feature
    table (e.g. from feature_matrix() or build_composer_profiles()).

    Parameters
    ----------
    feature_df : pd.DataFrame -- one row per tune/corpus, one column per feature.
    standardize : bool
        If True (default), z-score each column first (mean 0, std 1) so no
        single feature's units dominate the distance -- standard practice
        before computing any spatial distance over mixed-unit features.
    plot : bool -- show a heatmap. Default False.

    Returns
    -------
    pd.DataFrame -- symmetric similarity matrix, values in (0, 1].

    Example
    -------
        feats = feature_matrix(files_subset)
        sim = spatial_similarity_matrix(feats, plot=True)
    """
    data = feature_df.copy()
    if standardize:
        stds = data.std(ddof=0).replace(0, 1)
        data = (data - data.mean()) / stds

    labels = list(data.index)
    matrix = pd.DataFrame(index=labels, columns=labels, dtype=float)
    for l1 in labels:
        for l2 in labels:
            matrix.loc[l1, l2] = spatial_similarity(data.loc[l1], data.loc[l2])

    if plot:
        plt.figure(figsize=(0.6 * len(labels) + 3, 0.5 * len(labels) + 2))
        sns.heatmap(matrix.astype(float), annot=len(labels) <= 12, fmt='.2f', cmap='Blues')
        plt.title('Spatial similarity (standardized feature distance)')
        plt.tight_layout()
        plt.show()

    return matrix


def find_transitivity_violation(corpus_path, n_tunes=20,
                                 sim_threshold=0.7, diff_threshold=0.4):
    """
    ONE-STOP demo of spatial similarity's broken transitivity (see the
    Jamaica-Cuba-Russia example in this module's docstring/lecture notes):
    load a random sample of tunes from a kern directory, build a spatial
    similarity matrix, and search all (A, B, C) triples for the worst case
    of "A~B and B~C, but A is NOT~C" -- the textbook violation of
    similarity-as-distance assuming transitivity.

    Parameters
    ----------
    corpus_path : str
        Path to a folder of .krn files (e.g. '../data/Essen/Czech').
    n_tunes : int
        How many tunes to randomly sample (default 20). Search is O(n^3)
        over the sample, so keep this modest.
    sim_threshold : float
        Minimum spatial_similarity() for A~B and B~C to count as
        "similar" (default 0.7).
    diff_threshold : float
        Maximum spatial_similarity() for A~C to count as "not similar"
        (default 0.4).

    Returns
    -------
    tuple (a, b, c, sim_ab, sim_bc, sim_ac), or None if no violation
    matching the thresholds was found in the sample. Also prints a
    human-readable summary either way.

    Example
    -------
        find_transitivity_violation('../data/Essen/Czech')
        find_transitivity_violation('../data/Essen/Polska', n_tunes=30)
    """
    import glob
    import random

    all_files = sorted(glob.glob(f'{corpus_path}/*.krn'))
    if len(all_files) == 0:
        print(f'No kern files found in {corpus_path}')
        return

    sample = random.sample(all_files, min(n_tunes, len(all_files)))
    df, _ = load_corpus(corpus_path, verbose=False)
    sample_ids = [Path(f).stem for f in sample]
    df = df[df.tune_id.isin(sample_ids)]

    # Build feature matrix and spatial similarity
    feats = feature_matrix(sample, tune_ids=sample_ids)
    sim = spatial_similarity_matrix(feats, plot=False)

    # Search for the worst violation
    worst_violation = 0
    worst_triple = None
    tids_list = list(sim.index)

    for a in tids_list:
        for b in tids_list:
            for c in tids_list:
                if len({a, b, c}) < 3:
                    continue
                ab = sim.loc[a, b]
                bc = sim.loc[b, c]
                ac = sim.loc[a, c]
                if ab > sim_threshold and bc > sim_threshold and ac < diff_threshold:
                    violation = ab + bc - ac
                    if violation > worst_violation:
                        worst_violation = violation
                        worst_triple = (a, b, c, ab, bc, ac)

    if worst_triple:
        a, b, c, ab, bc, ac = worst_triple
        print(f'Biggest transitivity violation found:\n')
        print(f'  {a} ~ {b}:  {ab:.3f}  (similar)')
        print(f'  {b} ~ {c}:  {bc:.3f}  (similar)')
        print(f'  {a} ~ {c}:  {ac:.3f}  (not similar) ←')
        print(f'\nViolation score: {worst_violation:.3f}')
        print(f'\nWhy are {a} and {b} similar,')
        print(f'and {b} and {c} similar, but {a} and {c} are not?')
    else:
        print(f'No strong violation found.')
        print(f'Try a larger n_tunes, or adjust sim_threshold/diff_threshold.')

    return worst_triple


# ── Alignment: similarity as shared higher-order STRUCTURE ──────────────────
#
# Tversky's feature-set view (jaccard/tversky_index above) asks "how many
# features do these share?" but treats every feature as a free-floating,
# unconnected item -- it has no notion of "feature X happens at the START
# of A, the same way feature Y happens at the START of B." Gentner's (1983)
# structure-mapping theory argues similarity often comes from matching
# RELATIONS between parts, not just matching parts themselves. The function
# below is a deliberately simple, illustrative version of that idea -- it
# is NOT a full structure-mapping engine -- but it does ask a genuinely
# different question than anything above: not "which notes/n-grams match?"
# but "does each piece's first half relate to its second half the same way?"

def structural_alignment(file_path_or_score_a, file_path_or_score_b, n_segments=2):
    """
    A simplified, illustrative take on Gentner-style structural alignment:
    split each melody into `n_segments` equal-length chunks (by note count),
    align them by position (segment 1 of A with segment 1 of B, etc.), and
    compare each aligned PAIR on three higher-order, RELATIONAL properties
    rather than on the literal notes:

        direction_match     -> do both segments rise, fall, or stay level
                                OVERALL (start note to end note)?
        repetition_match     -> does each segment repeat its own first pitch
                                anywhere later in the same segment? (a crude
                                stand-in for "has internal repetition")
        contour_agreement   -> note-to-note up/down/same agreement within
                                the aligned segment pair (reuses
                                _contour_agreement(), the same engine
                                contour_similarity() uses -- but applied
                                PER ALIGNED SEGMENT instead of to the whole
                                piece at once)

    Parameters
    ----------
    file_path_or_score_a, file_path_or_score_b : str, Path, or music21 Score
    n_segments : int
        How many equal-length chunks to split each melody into (default 2,
        matching the "both motives are in two halves" framing).

    Returns
    -------
    pd.DataFrame, one row per segment, columns:
        segment, direction_match, repetition_match, contour_agreement
    Plus an extra attribute-style summary: call .attrs['overall_score'] on
    the returned DataFrame for a single 0-1 number (mean of all three
    columns, all segments).

    Example
    -------
        result = structural_alignment('../data/tune1.krn', '../data/tune2.krn', n_segments=2)
        print(result)
        print(f"Overall structural alignment: {result.attrs['overall_score']:.3f}")
    """
    notes_a = note_sequence(file_path_or_score_a)
    notes_b = note_sequence(file_path_or_score_b)

    def split(names, n):
        ps = [Pitch(p).ps for p in names]
        size_a = max(1, len(ps) // n)
        chunks = [ps[i * size_a:(i + 1) * size_a] for i in range(n - 1)]
        chunks.append(ps[(n - 1) * size_a:])
        return [c for c in chunks if c]

    chunks_a = split(notes_a, n_segments)
    chunks_b = split(notes_b, n_segments)
    n = min(len(chunks_a), len(chunks_b))

    def direction(chunk):
        if len(chunk) < 2:
            return 0
        diff = chunk[-1] - chunk[0]
        return 1 if diff > 0 else (-1 if diff < 0 else 0)

    def has_internal_repetition(chunk):
        return len(chunk) > 1 and chunk[0] in chunk[1:]

    def contour(chunk):
        return [1 if chunk[i] > chunk[i - 1] else (-1 if chunk[i] < chunk[i - 1] else 0)
                for i in range(1, len(chunk))]

    rows = []
    for i in range(n):
        ca, cb = chunks_a[i], chunks_b[i]
        rows.append({
            'segment': i + 1,
            'direction_match': float(direction(ca) == direction(cb)),
            'repetition_match': float(has_internal_repetition(ca) == has_internal_repetition(cb)),
            'contour_agreement': _contour_agreement(contour(ca), contour(cb)),
        })

    result = pd.DataFrame(rows)
    score_cols = ['direction_match', 'repetition_match', 'contour_agreement']
    result.attrs['overall_score'] = float(result[score_cols].mean().mean()) if len(result) else 0.0
    return result


# ── Convenience: inspecting one pair out of a similarity_matrices() result ──

def compare_tunes(tids, corpus_df, edit_mat, jac_mat, con_mat,
                   a=0, b=1, show='scale_degrees'):
    """
    ONE-STOP look at a single pair of tunes: prints each tune's opening
    sequence (your choice of representation) side by side, plus their score
    in all three distance matrices from similarity_matrices() -- handy for
    sanity-checking a heatmap cell or following up on a disagreements table.

    Each tune can be given as a position in `tids` (int) or as the tune_id
    itself (str) -- mix and match freely.

    Parameters
    ----------
    tids : list of str
        Tune IDs in matrix order -- the `tids`/`good_ids` list returned
        alongside the matrices by similarity_matrices().
    corpus_df : pd.DataFrame
        Must have a 'tune_id' column, plus whichever column(s) `show` asks
        for (e.g. from load_corpus(), which provides 'scale_degrees',
        'pitches', and 'intervals').
    edit_mat, jac_mat, con_mat : pd.DataFrame
        The 'edit', 'jaccard', and 'contour' matrices from
        similarity_matrices() (indexed/columned by tune_id).
    a, b : int or str
        The two tunes to compare -- either their index into `tids` or their
        tune_id string. Default a=0, b=1 (the first two tunes).
    show : str
        Which sequence(s) to print for each tune:
            'scale_degrees' -> scale-degree sequence (default)
            'pitches'       -> note names with octave (e.g. 'G4', 'A4')
            'intervals'     -> melodic intervals, in semitones
            'all'           -> all three, one block per tune
        Any column not present in `corpus_df` prints as "not available"
        instead of raising.

    Returns
    -------
    None -- prints a short comparison. (Returns early, printing nothing
    else, if either tune_id isn't found.)

    Example
    -------
        matrices, tids = similarity_matrices(files_subset)
        compare_tunes(tids, corpus_df, matrices['edit'], matrices['jaccard'], matrices['contour'])
        compare_tunes(tids, corpus_df, matrices['edit'], matrices['jaccard'], matrices['contour'],
                      a='czech01', b='czech03', show='pitches')
    """
    # Resolve index or string to tune_id
    def resolve(x):
        if isinstance(x, int):
            return tids[x]
        elif isinstance(x, str):
            if x not in tids:
                print(f"Tune '{x}' not found. Available tunes:")
                for i, tid in enumerate(tids):
                    print(f"  {i}: {tid}")
                return None
            return x

    tune_a = resolve(a)
    tune_b = resolve(b)
    if tune_a is None or tune_b is None:
        return

    row_a = corpus_df[corpus_df.tune_id == tune_a].iloc[0]
    row_b = corpus_df[corpus_df.tune_id == tune_b].iloc[0]
    cols = ['scale_degrees', 'pitches', 'intervals'] if show == 'all' else [show]

    for tune_id, row in [(tune_a, row_a), (tune_b, row_b)]:
        print(f'{tune_id}:')
        for col in cols:
            if col in row.index:
                print(f'  {col}: {row[col][:20]}')
            else:
                print(f'  {col}: not available')
        print()

    print(f'Edit distance: {edit_mat.loc[tune_a, tune_b]:.3f}')
    print(f'Jaccard:       {jac_mat.loc[tune_a, tune_b]:.3f}')
    print(f'Contour:       {con_mat.loc[tune_a, tune_b]:.3f}')
