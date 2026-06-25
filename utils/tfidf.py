"""
utils/tfidf.py — Distinctiveness measures for melodic n-grams and chord progressions
Summer Institute 2026 · Hebrew University of Jerusalem

Frequency alone ("how often does this n-gram occur?") doesn't tell you what
makes a corpus DISTINCTIVE — a very common bigram might just be common
everywhere. This module borrows TF-IDF (term frequency - inverse document
frequency), the classic text-mining trick for finding words that are
characteristic of a document but not just generically frequent, and applies
it to melodic n-grams and harmonic (Roman numeral) progressions.

Two ways to use it:
    1. A simple, lightweight two-corpus comparison (no IDF, just relative
       frequency on each side) -> distinctive_ngrams()
    2. Full multi-corpus TF-IDF, melodic or harmonic -> tf_idf_ngrams(),
       tf_idf_chord_progressions(), and plot_tfidf_heatmap() for an
       alternative visualization of either one's output.

Beginner usage
---------------
    from utils import distinctive_ngrams
    from utils import extract_scale_degree_bigrams
    counter_a, _ = extract_scale_degree_bigrams(files_a, 'A')
    counter_b, _ = extract_scale_degree_bigrams(files_b, 'B')
    dist_a, dist_b = distinctive_ngrams(counter_a, counter_b, 'A', 'B')

    from utils import tf_idf_ngrams
    table = tf_idf_ngrams({'Parker': parker_files, 'Gillespie': dizzy_files})

    from utils import tf_idf_chord_progressions
    table = tf_idf_chord_progressions({'Bach': bach_files, 'Beatles': beatles_csvs})

    from utils import plot_tfidf_heatmap
    plot_tfidf_heatmap(table)
"""

from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from music21 import converter, roman

from .ngrams import get_ngrams, _gather_files, pitch_class_sequence, scale_degree_sequence


# ── Internal helpers ──────────────────────────────────────────────────────────

def _interval_sequence(file_path_or_score):
    """Internal: signed-semitone melodic intervals between consecutive notes."""
    score = (converter.parse(str(file_path_or_score))
             if isinstance(file_path_or_score, (str, Path))
             else file_path_or_score)
    midi_vals = []
    for element in score.recurse().notes:
        pitches = element.pitches if element.isChord else [element.pitch]
        for p in pitches:
            midi_vals.append(int(p.midi))
    return [b - a for a, b in zip(midi_vals, midi_vals[1:])]


def _contour_sequence(file_path_or_score):
    """Internal: melodic contour (+1 up / -1 down / 0 repeat) between consecutive notes."""
    intervals = _interval_sequence(file_path_or_score)
    return [1 if iv > 0 else (-1 if iv < 0 else 0) for iv in intervals]


def _representation_sequence(file_path_or_score, representation='scale_degree'):
    """Internal: dispatch to the right symbol-sequence extractor by name."""
    if representation == 'scale_degree':
        return scale_degree_sequence(file_path_or_score)
    elif representation == 'pitch_class':
        return pitch_class_sequence(file_path_or_score)
    elif representation == 'interval':
        return _interval_sequence(file_path_or_score)
    elif representation == 'contour':
        return _contour_sequence(file_path_or_score)
    else:
        raise ValueError("representation must be 'scale_degree', 'pitch_class', "
                          "'interval', or 'contour'")


def _roman_numeral_sequence(file_path):
    """
    Internal: one Roman-numeral label per chord in a kern file, via
    music21 chordify() + roman.romanNumeralFromChord(), using the piece's
    own detected key.
    """
    score = converter.parse(str(file_path))
    key_obj = score.analyze('key')
    chordified = score.chordify()
    numerals = []
    for c in chordified.recurse().getElementsByClass('Chord'):
        try:
            rn = roman.romanNumeralFromChord(c, key_obj)
            label = rn.romanNumeralAlone or rn.figure
            if label:
                numerals.append(label)
        except Exception:
            continue
    return numerals


def _chord_sequence_from_file(file_path):
    """
    Internal: one chord-symbol sequence per file, auto-detecting format.
    '.csv' -> Billboard-style chord-CSV (expects a 'chord' column, used as
    vocabulary directly). Anything else -> kern file, Roman-numeralized.
    """
    file_path = str(file_path)
    if file_path.lower().endswith('.csv'):
        df = pd.read_csv(file_path)
        if 'chord' not in df.columns:
            raise ValueError(f"CSV {file_path} has no 'chord' column")
        return df['chord'].dropna().astype(str).tolist()
    return _roman_numeral_sequence(file_path)


def _build_tfidf_table(counters, item_col='ngram'):
    """
    Internal: shared TF-IDF math for tf_idf_ngrams() and
    tf_idf_chord_progressions() — both just supply a {corpus_name: Counter}
    dict of term counts and get back a long-format TF-IDF table.

    Smoothed IDF = log((n_corpora + 1) / (DF + 1)), to avoid division
    by zero while still going to 0 for a term that appears in every
    corpus (DF == n_corpora) -- a truly universal term is, by definition,
    not distinctive to anyone.
    """
    n_corpora = len(counters)
    doc_freq = Counter()
    for counter in counters.values():
        for item in counter:
            doc_freq[item] += 1

    rows = []
    for corpus_name, counter in counters.items():
        total = sum(counter.values()) or 1
        for item, count in counter.items():
            tf = count / total
            df_ = doc_freq[item]
            idf = np.log((n_corpora + 1) / (df_ + 1))
            rows.append({'corpus': corpus_name, item_col: item,
                         'tf': tf, 'idf': idf, 'tfidf': tf * idf})

    result = pd.DataFrame(rows)
    if not result.empty:
        result = (result.sort_values(['corpus', 'tfidf'], ascending=[True, False])
                         .reset_index(drop=True))
    return result


def _plot_tfidf_subplots(result, item_col, top_n, color, title):
    """Internal: shared 'one horizontal bar chart per corpus' plotting code."""
    names = list(result['corpus'].unique())
    if not names:
        return
    fig, axes = plt.subplots(1, len(names), figsize=(5 * len(names), max(4, top_n * 0.3)))
    axes = np.atleast_1d(axes)
    for ax, name in zip(axes, names):
        top = result[result['corpus'] == name].head(top_n).iloc[::-1]
        labels = [' '.join(map(str, item)) if isinstance(item, tuple) else str(item)
                  for item in top[item_col]]
        ax.barh(labels, top['tfidf'], color=color, edgecolor='white')
        ax.set_title(name)
        ax.set_xlabel('TF-IDF')
    fig.suptitle(title)
    plt.tight_layout()
    plt.show()


# ── Lightweight two-corpus distinctiveness (no IDF) ──────────────────────────

def distinctive_ngrams(counter_a, counter_b, name_a='A', name_b='B', top_n=10):
    """
    BUILDING BLOCK: a lighter-weight alternative to full TF-IDF for the
    simplest case — comparing exactly TWO corpora. For each n-gram, computes
    its relative frequency in each corpus and a directional distinctiveness
    score: distinctiveness_for_a = freq_a / (freq_a + freq_b + epsilon).

    A score near 1.0 means the n-gram is essentially only used by that
    corpus; a score near 0.5 means it's shared roughly equally.

    Parameters
    ----------
    counter_a, counter_b : Counter
        N-gram counts for each corpus, e.g. from extract_scale_degree_bigrams().
    name_a, name_b : str
        Labels used in the printed summary.
    top_n : int
        Rows to keep in each returned table.

    Returns
    -------
    (distinctive_to_a, distinctive_to_b) : two pd.DataFrames, each with
    columns ngram | freq_a | freq_b | distinctiveness, sorted descending.

    Example
    -------
        from utils import extract_scale_degree_bigrams
        counter_a, _ = extract_scale_degree_bigrams(parker_files, 'Parker')
        counter_b, _ = extract_scale_degree_bigrams(dizzy_files, 'Dizzy')
        dist_a, dist_b = distinctive_ngrams(counter_a, counter_b, 'Parker', 'Dizzy')
    """
    total_a = sum(counter_a.values()) or 1
    total_b = sum(counter_b.values()) or 1
    all_ngrams = set(counter_a) | set(counter_b)
    eps = 1e-10

    rows = []
    for ng in all_ngrams:
        freq_a = counter_a.get(ng, 0) / total_a
        freq_b = counter_b.get(ng, 0) / total_b
        rows.append({
            'ngram': ng, 'freq_a': freq_a, 'freq_b': freq_b,
            'dist_a': freq_a / (freq_a + freq_b + eps),
            'dist_b': freq_b / (freq_a + freq_b + eps),
        })
    df = pd.DataFrame(rows)

    distinctive_to_a = (df[['ngram', 'freq_a', 'freq_b', 'dist_a']]
                         .rename(columns={'dist_a': 'distinctiveness'})
                         .sort_values('distinctiveness', ascending=False)
                         .head(top_n).reset_index(drop=True))
    distinctive_to_b = (df[['ngram', 'freq_a', 'freq_b', 'dist_b']]
                         .rename(columns={'dist_b': 'distinctiveness'})
                         .sort_values('distinctiveness', ascending=False)
                         .head(top_n).reset_index(drop=True))

    print(f'Most distinctive to {name_a}:')
    print(distinctive_to_a.to_string(index=False))
    print(f'\nMost distinctive to {name_b}:')
    print(distinctive_to_b.to_string(index=False))

    return distinctive_to_a, distinctive_to_b


# ── Full multi-corpus TF-IDF: melodic n-grams ────────────────────────────────

def tf_idf_ngrams(corpus_dict, n=2, top_n=20, representation='scale_degree',
                   pattern='*.krn', plot=True, verbose=True):
    """
    ONE-STOP: which melodic n-grams are most DISTINCTIVE to each corpus,
    across any number of corpora (not just two)? Unlike raw frequency, a
    high TF-IDF score means an n-gram is both common WITHIN a corpus and
    rare ACROSS the others.

    Steps: (1) extract n-gram counts per corpus in the chosen
    representation; (2) TF = count / total n-grams in that corpus;
    (3) DF = number of corpora the n-gram appears in at all;
    (4) IDF = log((n_corpora + 1) / (DF + 1)) (smoothed);
    (5) TF-IDF = TF * IDF.

    Parameters
    ----------
    corpus_dict : dict
        {corpus_name: [file paths]} — e.g. {'Parker': parker_files, 'Dizzy': dizzy_files}.
    n : int
        N-gram size (default 2 = bigrams).
    top_n : int
        Rows kept per corpus (also controls plot height).
    representation : 'scale_degree', 'pitch_class', 'interval', or 'contour'
    pattern : str
        Glob pattern, used if a corpus_dict value is a folder rather than a file list.
    plot : bool
        If True (default), one horizontal-bar subplot per corpus.
    verbose : bool
        If True (default), print progress every 25 files and report skipped files.

    Returns
    -------
    pd.DataFrame — columns: corpus, ngram, tf, idf, tfidf
    (sorted by tfidf descending within each corpus)

    Example
    -------
        table = tf_idf_ngrams({'Parker': parker_files, 'Gillespie': dizzy_files})
    """
    counters = {}
    for name, files in corpus_dict.items():
        file_list = _gather_files(files, pattern)
        if verbose:
            print(f'{name}: {len(file_list)} file(s)')
        counter = Counter()
        skipped = []
        for i, f in enumerate(file_list):
            if verbose and i % 25 == 0:
                print(f'  {i + 1}/{len(file_list)}...')
            try:
                seq = _representation_sequence(f, representation)
                if len(seq) >= n:
                    counter.update(get_ngrams(seq, n))
            except Exception as e:
                skipped.append((f, str(e)))
                if verbose:
                    print(f'  Skipped {Path(f).name}: {e}')
        if skipped:
            print(f'{name}: skipped {len(skipped)} unreadable file(s).')
        counters[name] = counter

    result = _build_tfidf_table(counters, item_col='ngram')

    if plot and not result.empty:
        _plot_tfidf_subplots(result, 'ngram', top_n, 'steelblue',
                              f'Most distinctive {n}-grams by corpus ({representation})')

    return result


# ── Full multi-corpus TF-IDF: harmonic (chord) progressions ──────────────────

def tf_idf_chord_progressions(corpus_dict, n=2, top_n=20, pattern='*', plot=True,
                               verbose=True):
    """
    ONE-STOP: the harmonic counterpart to tf_idf_ngrams() — which chord
    progressions are most distinctive to each corpus? Each piece (file) is
    treated as one "document"; each term is a Roman-numeral n-gram.

    File type is auto-detected from the extension:
        '.krn'  -> music21 chordify() + roman.romanNumeralFromChord(),
                   using the piece's own detected key.
        '.csv'  -> Billboard-style chord-CSV; expects a 'chord' column,
                   whose chord symbols are used as the vocabulary directly.

    Parameters
    ----------
    corpus_dict : dict
        {corpus_name: [file paths]} — kern and/or chord-CSV files, mixed freely.
    n : int
        N-gram size (default 2).
    top_n : int
        Rows kept per corpus (also controls plot height).
    pattern : str
        Glob pattern, used if a corpus_dict value is a folder rather than a file list.
    plot : bool
        If True (default), one horizontal-bar subplot per corpus.
    verbose : bool
        If True (default), print progress every 25 files and report skipped files.

    Returns
    -------
    pd.DataFrame — columns: corpus, progression, tf, idf, tfidf

    Example
    -------
        table = tf_idf_chord_progressions({'Bach': bach_kern_files,
                                            'Beatles': beatles_chord_csvs})
    """
    counters = {}
    for name, files in corpus_dict.items():
        file_list = _gather_files(files, pattern)
        if verbose:
            print(f'{name}: {len(file_list)} file(s)')
        counter = Counter()
        skipped = []
        for i, f in enumerate(file_list):
            if verbose and i % 25 == 0:
                print(f'  {i + 1}/{len(file_list)}...')
            try:
                seq = _chord_sequence_from_file(f)
                if len(seq) >= n:
                    counter.update(get_ngrams(seq, n))
            except Exception as e:
                skipped.append((f, str(e)))
                if verbose:
                    print(f'  Skipped {Path(f).name}: {e}')
        if skipped:
            print(f'{name}: skipped {len(skipped)} unreadable file(s).')
        counters[name] = counter

    result = _build_tfidf_table(counters, item_col='progression')

    if plot and not result.empty:
        _plot_tfidf_subplots(result, 'progression', top_n, 'coral',
                              f'Most distinctive {n}-gram chord progressions by corpus')

    return result


# ── Alternative visualization for either TF-IDF table above ─────────────────

def plot_tfidf_heatmap(tfidf_df, top_n=20, figsize=(12, 8)):
    """
    Alternative visualization for the output of tf_idf_ngrams() or
    tf_idf_chord_progressions(): a heatmap with rows = the top_n most
    distinctive terms (ranked by their MAX TF-IDF across any corpus),
    columns = corpora, color = TF-IDF score (blue scale, white = 0).

    Parameters
    ----------
    tfidf_df : pd.DataFrame
        Output of tf_idf_ngrams() (has an 'ngram' column) or
        tf_idf_chord_progressions() (has a 'progression' column).
    top_n : int
    figsize : tuple

    Returns
    -------
    matplotlib.figure.Figure (or None if tfidf_df is empty)

    Example
    -------
        table = tf_idf_ngrams({'Parker': parker_files, 'Gillespie': dizzy_files})
        plot_tfidf_heatmap(table)
    """
    if tfidf_df is None or tfidf_df.empty:
        print('Empty TF-IDF table -- nothing to plot.')
        return None

    item_col = next((c for c in tfidf_df.columns if c not in ('corpus', 'tf', 'idf', 'tfidf')),
                     tfidf_df.columns[0])

    pivot = tfidf_df.pivot_table(index=item_col, columns='corpus', values='tfidf', fill_value=0)
    top_items = pivot.max(axis=1).sort_values(ascending=False).head(top_n).index
    pivot = pivot.loc[top_items]

    pivot.index = [' '.join(map(str, idx)) if isinstance(idx, tuple) else str(idx)
                   for idx in pivot.index]

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='Blues', linewidths=0.3,
                linecolor='white', ax=ax)
    ax.set_title(f'TF-IDF heatmap — top {len(pivot)} {item_col}s')
    ax.set_xlabel('Corpus')
    ax.set_ylabel(item_col.replace('_', ' ').capitalize())
    plt.tight_layout()
    plt.show()

    return fig
