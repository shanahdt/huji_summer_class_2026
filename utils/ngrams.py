"""
utils/ngrams.py — N-grams and transition matrices
Summer Institute 2026 · Hebrew University of Jerusalem

This module answers the Day 2 question: "How often does one note (or scale
degree, or interval) follow another — and what does that look like as a
table or a heatmap?"

The "one-stop" functions (ngram_table, scale_degree_ngram_table) each do all
three steps for you:
    1. IMPORT   — parse one file, a list of files, or every file in a folder
    2. PROCESS  — count n-grams (bigrams, trigrams, ... ) of notes
    3. OUTPUT   — return a frequency table AND plot it (heatmap for bigrams,
                  bar chart for anything else)

Beginner usage
---------------
    from utils import ngram_table
    table, counter = ngram_table('../data/happy_birthday.krn', n=2)   # bigrams
    table, counter = ngram_table('../data/charlie_parker', n=3)       # trigrams, whole folder

    from utils import scale_degree_ngram_table
    table, counter = scale_degree_ngram_table('../data/Essen/England', n=2)
"""

from collections import Counter
from glob import glob
from itertools import islice
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from music21 import converter

# ── Low-level n-gram helpers ──────────────────────────────────────────────────

def get_ngrams(sequence, n):
    """
    Return all n-grams from a sequence as a list of tuples.

    Example
    -------
        get_ngrams([1, 2, 3, 4], 2)
        # → [(1, 2), (2, 3), (3, 4)]
    """
    return list(zip(*[islice(sequence, i, None) for i in range(n)]))


def _gather_files(source, pattern='*.krn'):
    """
    Internal helper: turn `source` into a list of file paths.

    Accepts:
        - a single file path (str/Path)        -> [that file]
        - a folder path (str/Path)              -> every file matching `pattern`
        - a list/tuple of file paths            -> returned as-is (as strings)
    """
    if isinstance(source, (list, tuple)):
        return [str(s) for s in source]
    p = Path(source)
    if p.is_dir():
        return sorted(str(f) for f in p.glob(pattern))
    return [str(p)]


def note_sequence(file_path_or_score):
    """
    Return the list of note names (e.g. 'C4', 'D4', ...) in a piece, in order.
    Chords are expanded into their individual pitches.
    """
    score = (converter.parse(str(file_path_or_score))
             if isinstance(file_path_or_score, (str, Path))
             else file_path_or_score)
    names = []
    for element in score.recurse().notes:
        if element.isChord:
            for p in element.pitches:
                names.append(p.nameWithOctave)
        else:
            names.append(element.pitch.nameWithOctave)
    return names


def most_common_ngrams(kern_file_path, n=2):
    """
    Return the most common n-grams of note names from a single kern file.

    Parameters
    ----------
    kern_file_path : str
        Path to a .krn file.
    n : int
        Size of the n-gram window (default 2 = bigrams).

    Returns
    -------
    list of ((note, ...), count) tuples, sorted most-common first.

    Example
    -------
        most_common_ngrams('../data/happy_birthday.krn', n=2)
    """
    if n < 1:
        raise ValueError('n must be >= 1')
    names = note_sequence(kern_file_path)
    return Counter(get_ngrams(names, n)).most_common()


# ── Transition matrices (bigrams only — that's what a 2-D heatmap can show) ──

def create_transition_matrix(weighted_ngrams):
    """
    Build a nested dict transition matrix from a list of (bigram, count) pairs.

    Parameters
    ----------
    weighted_ngrams : list
        Output of most_common_ngrams() — list of ((from, to), count).

    Returns
    -------
    dict of {from_note: {to_note: count}}
    """
    matrix = {}
    for ngram, count in weighted_ngrams:
        if len(ngram) < 2:
            continue
        from_note, to_note = ngram[0], ngram[1]
        matrix.setdefault(from_note, {}).setdefault(to_note, 0)
        matrix[from_note][to_note] += count
    return matrix


def plot_transition_matrix(transition_matrix, as_percentages=False,
                            title=None, figsize=(9, 7)):
    """
    Plot a transition matrix as a heatmap.

    Parameters
    ----------
    transition_matrix : dict
        Output of create_transition_matrix().
    as_percentages : bool
        If True, normalise each row so values sum to 100.
    title : str, optional
        Custom title. Auto-generated if None.
    figsize : tuple
        Matplotlib figure size.

    Example
    -------
        data = most_common_ngrams('../data/happy_birthday.krn', n=2)
        matrix = create_transition_matrix(data)
        plot_transition_matrix(matrix, as_percentages=True)
    """
    df = pd.DataFrame(transition_matrix).T.fillna(0).astype(int)

    if as_percentages:
        df = df.div(df.sum(axis=1).replace(0, 1), axis=0) * 100

    fmt = '.1f' if as_percentages else 'd'
    auto_title = ('Transition matrix (%)' if as_percentages
                  else 'Transition matrix (counts)')

    plt.figure(figsize=figsize)
    sns.heatmap(df, annot=True, fmt=fmt, cmap='Blues',
                linewidths=0.3, linecolor='white')
    plt.title(title or auto_title)
    plt.xlabel('To note')
    plt.ylabel('From note')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    plt.show()


# ── ONE-STOP: bigrams, trigrams, and beyond ──────────────────────────────────

def ngram_table(source, n=2, top_n=15, pattern='*.krn', plot=True,
                 title=None, figsize=None):
    """
    ONE-STOP function: import a piece (or a whole folder of pieces), count
    n-grams of note names, and show the result as a table + plot.

    Parameters
    ----------
    source : str, Path, or list
        A single file path, a folder path (every matching file is used), or
        a list of file paths.
    n : int
        N-gram size. n=2 -> bigrams, n=3 -> trigrams, etc.
    top_n : int
        How many rows to keep in the returned table.
    pattern : str
        Glob pattern used when `source` is a folder (default '*.krn').
    plot : bool
        If True, show a plot: a heatmap for bigrams (n=2), or a bar chart
        of the top n-grams for any other n.
    title : str, optional
        Custom plot title.
    figsize : tuple, optional
        Matplotlib figure size.

    Returns
    -------
    table : pd.DataFrame — columns: ngram, count, percent
    counter : collections.Counter — every n-gram and its count

    Example
    -------
        # Bigrams in a single tune
        table, counter = ngram_table('../data/happy_birthday.krn', n=2)

        # Trigrams across an entire folder of tunes
        table, counter = ngram_table('../data/charlie_parker', n=3, top_n=20)
    """
    if n < 1:
        raise ValueError('n must be >= 1')

    files = _gather_files(source, pattern)
    counter = Counter()
    skipped = []
    for f in files:
        try:
            counter.update(get_ngrams(note_sequence(f), n))
        except Exception as e:
            skipped.append((f, str(e)))

    if skipped:
        print(f'Skipped {len(skipped)} unreadable file(s).')

    total = sum(counter.values()) or 1
    rows = [{'ngram': ' → '.join(gram), 'count': count,
             'percent': f'{100 * count / total:.2f}%'}
            for gram, count in counter.most_common(top_n)]
    table = pd.DataFrame(rows)

    if plot and counter:
        if n == 2:
            matrix = create_transition_matrix(counter.most_common())
            plot_transition_matrix(matrix,
                                    title=title or f'Bigram transitions ({len(files)} file(s))',
                                    figsize=figsize or (9, 7))
        else:
            plt.figure(figsize=figsize or (10, 5))
            top = counter.most_common(top_n)
            labels = [' → '.join(gram) for gram, _ in top]
            values = [count for _, count in top]
            plt.bar(labels, values, color='steelblue', edgecolor='white')
            plt.title(title or f'Top {n}-grams ({len(files)} file(s))')
            plt.xlabel(f'{n}-gram')
            plt.ylabel('Count')
            plt.xticks(rotation=60, ha='right')
            plt.tight_layout()
            plt.show()

    return table, counter


# ── Scale-degree (key-relative) bigrams ──────────────────────────────────────

# Chromatic scale-degree labels (12 semitones above tonic)
DEGREE_LABELS = ['1', 'b2', '2', 'b3', '3', '4', '#4',
                 '5', 'b6', '6', 'b7', '7']

_SEMITONE_TO_LABEL = {i: DEGREE_LABELS[i] for i in range(12)}


def scale_degree_sequence(file_path_or_score):
    """
    Return the chromatic scale-degree label (e.g. '1', 'b3', '5') for every
    note in a piece, relative to the piece's own detected tonic. Useful for
    comparing pieces in different keys on equal footing.
    """
    score = (converter.parse(str(file_path_or_score))
             if isinstance(file_path_or_score, (str, Path))
             else file_path_or_score)
    tonic_pc = int(score.analyze('key').tonic.pitchClass)
    return [_SEMITONE_TO_LABEL[(int(p.pitchClass) - tonic_pc) % 12]
            for p in score.pitches]


def extract_scale_degree_bigrams(file_list, corpus_name='Corpus'):
    """
    Extract chromatic scale-degree bigrams from a list of kern files.

    Notes are mapped relative to the detected tonic of each piece, so
    the labels (1, b2, 2 ... 7) are key-independent.

    Parameters
    ----------
    file_list : list of str
        Paths to .krn files.
    corpus_name : str
        Label used in warning messages.

    Returns
    -------
    counter : Counter  —  {(from_label, to_label): count}
    skipped : list     —  [(file_path, error_message), ...]

    Example
    -------
        files = sorted(glob('../data/charlie_parker/*.krn'))
        counter, skipped = extract_scale_degree_bigrams(files, 'Parker')
    """
    all_bigrams = []
    skipped = []

    for file_path in file_list:
        try:
            labels = scale_degree_sequence(file_path)
        except Exception as e:
            skipped.append((file_path, str(e)))
            continue
        all_bigrams.extend(zip(labels, labels[1:]))

    if skipped:
        print(f'{corpus_name}: skipped {len(skipped)} unreadable file(s).')

    return Counter(all_bigrams), skipped


def scale_degree_ngram_table(source, n=2, top_n=15, pattern='*.krn',
                              corpus_name='Corpus', plot=True, title=None):
    """
    ONE-STOP function: import a piece (or folder of pieces), convert notes to
    key-relative scale degrees, count n-grams, and show a table + plot.

    This is the key-relative counterpart to ngram_table() — use it when you
    want patterns expressed as scale degrees (1, b3, 5, ...) instead of raw
    pitch names, so pieces in different keys can be compared directly.

    Parameters
    ----------
    source : str, Path, or list
        A single file, a folder (every matching file is used), or a list of files.
    n : int
        N-gram size (2 = bigrams, 3 = trigrams, ...).
    top_n : int
        Rows to keep in the table.
    pattern : str
        Glob pattern when `source` is a folder.
    corpus_name : str
        Label used in the plot title and warning messages.
    plot : bool
        If True, show a heatmap (n=2) or bar chart (n>2).

    Returns
    -------
    table : pd.DataFrame — columns: ngram, count, percent
    counter : Counter

    Example
    -------
        table, counter = scale_degree_ngram_table('../data/Essen/England', n=2)
    """
    files = _gather_files(source, pattern)
    counter = Counter()
    skipped = []
    for f in files:
        try:
            labels = scale_degree_sequence(f)
            counter.update(get_ngrams(labels, n))
        except Exception as e:
            skipped.append((f, str(e)))

    if skipped:
        print(f'{corpus_name}: skipped {len(skipped)} unreadable file(s).')

    total = sum(counter.values()) or 1
    rows = [{'ngram': ' → '.join(gram), 'count': count,
             'percent': f'{100 * count / total:.2f}%'}
            for gram, count in counter.most_common(top_n)]
    table = pd.DataFrame(rows)

    if plot and counter:
        if n == 2:
            matrix = _counter_to_degree_matrix(counter, 'counts')
            plt.figure(figsize=(9, 7))
            sns.heatmap(matrix, annot=True, fmt='g', cmap='Blues',
                        linewidths=0.2, linecolor='white')
            plt.title(title or f'{corpus_name}: scale-degree bigrams')
            plt.xlabel('To scale degree')
            plt.ylabel('From scale degree')
            plt.tight_layout()
            plt.show()
        else:
            plt.figure(figsize=(10, 5))
            top = counter.most_common(top_n)
            labels_ = [' → '.join(gram) for gram, _ in top]
            values = [count for _, count in top]
            plt.bar(labels_, values, color='coral', edgecolor='white')
            plt.title(title or f'{corpus_name}: top {n}-grams (scale degrees)')
            plt.xlabel(f'{n}-gram')
            plt.ylabel('Count')
            plt.xticks(rotation=60, ha='right')
            plt.tight_layout()
            plt.show()

    return table, counter


def bigram_table(counter, corpus_name, top_n=15):
    """
    Convert a bigram Counter into a readable DataFrame.

    Returns columns: Corpus, Bigram, Count, Percent.

    Example
    -------
        tbl = bigram_table(parker_counter, 'Parker', top_n=10)
        display(tbl)
    """
    total = sum(counter.values()) or 1
    rows = []
    for (d1, d2), count in counter.most_common(top_n):
        rows.append({
            'Corpus': corpus_name,
            'Bigram': f'{d1}->{d2}',
            'Count': count,
            'Percent': f'{100 * count / total:.2f}%',
        })
    return pd.DataFrame(rows)


def _counter_to_degree_matrix(counter, value_type='counts'):
    """Build a 12x12 DataFrame from a bigram Counter (internal helper)."""
    matrix = {f: {t: 0 for t in DEGREE_LABELS} for f in DEGREE_LABELS}
    for (f, t), count in counter.items():
        if f in matrix and t in matrix[f]:
            matrix[f][t] += count

    df = pd.DataFrame(matrix).T.loc[DEGREE_LABELS, DEGREE_LABELS]

    if value_type == 'percentages':
        row_sums = df.sum(axis=1).replace(0, 1)
        df = df.div(row_sums, axis=0) * 100

    return df


def compare_two_corpora_bigrams(left_files, right_files,
                                 left_name='Corpus A', right_name='Corpus B',
                                 value_type='counts', top_n=None,
                                 figsize=(22, 9)):
    """
    Extract scale-degree bigrams from two file lists and plot them side by side.

    Parameters
    ----------
    left_files, right_files : list of str
        Paths to .krn files for each corpus.
    left_name, right_name : str
        Labels for the two corpora.
    value_type : 'counts' or 'percentages'
    top_n : int or None
        If given, keep only the top-N bigrams before building the matrix.
    figsize : tuple
        Figure size — increase if labels are cramped.

    Returns
    -------
    left_matrix, right_matrix : pd.DataFrame (12×12)

    Example
    -------
        compare_two_corpora_bigrams(
            sorted(glob('../data/charlie_parker/*.krn')),
            sorted(glob('../data/dizzy_gillespie/*.krn')),
            left_name='Parker', right_name='Dizzy',
            value_type='percentages'
        )
    """
    if value_type not in ('counts', 'percentages'):
        raise ValueError("value_type must be 'counts' or 'percentages'")

    left_counter, _ = extract_scale_degree_bigrams(left_files, left_name)
    right_counter, _ = extract_scale_degree_bigrams(right_files, right_name)

    if top_n is not None:
        left_counter = Counter(dict(left_counter.most_common(top_n)))
        right_counter = Counter(dict(right_counter.most_common(top_n)))

    left_matrix = _counter_to_degree_matrix(left_counter, value_type)
    right_matrix = _counter_to_degree_matrix(right_counter, value_type)

    fmt = '.1f' if value_type == 'percentages' else 'g'
    cbar_label = 'Percent' if value_type == 'percentages' else 'Count'

    fig, axes = plt.subplots(1, 2, figsize=figsize)
    for ax, matrix, name in zip(axes,
                                 [left_matrix, right_matrix],
                                 [left_name, right_name]):
        sns.heatmap(matrix, annot=True, fmt=fmt, cmap='Blues', ax=ax,
                    linewidths=0.2, linecolor='white',
                    cbar_kws={'label': cbar_label},
                    annot_kws={'size': 8})
        ax.set_title(f'{name} ({value_type}, scale degrees)')
        ax.set_xlabel('To scale degree')
        ax.set_ylabel('From scale degree')
        ax.tick_params(axis='x', rotation=45)
        ax.tick_params(axis='y', rotation=0)

    plt.tight_layout()
    plt.show()

    return left_matrix, right_matrix


# ── Interval analysis ─────────────────────────────────────────────────────────

def interval_label(semitones):
    """
    Convert a signed semitone interval to a human-readable label.

    Example
    -------
        interval_label(7)   # → 'up P5 (+7)'
        interval_label(-2)  # → 'down M2 (-2)'
        interval_label(0)   # → 'stay (P1, 0)'
    """
    names = {0: 'P1', 1: 'm2', 2: 'M2', 3: 'm3', 4: 'M3', 5: 'P4',
             6: 'TT', 7: 'P5', 8: 'm6', 9: 'M6', 10: 'm7', 11: 'M7', 12: 'P8'}

    if semitones == 0:
        return 'stay (P1, 0)'

    direction = 'up' if semitones > 0 else 'down'
    size = abs(int(semitones))
    name = names.get(size, f'{size} st')
    return f'{direction} {name} ({semitones:+d})'


def load_interval_corpus(patterns):
    """
    Load multiple kern corpora and extract melodic interval sequences.

    Parameters
    ----------
    patterns : list of (label, glob_pattern)
        E.g. [('English', '../data/Essen/England/*.krn'),
               ('Czech',   '../data/Essen/Czech/*.krn')]

    Returns
    -------
    pd.DataFrame with columns: tune_id, corpus, intervals

    Example
    -------
        df = load_interval_corpus([
            ('English', '../data/Essen/England/*.krn'),
            ('Czech',   '../data/Essen/Czech/*.krn'),
        ])
    """
    rows = []
    for corpus_name, pattern in patterns:
        for file_path in sorted(glob(pattern)):
            try:
                score = converter.parse(file_path)
                midi_vals = []
                for el in score.recurse().notes:
                    if el.isChord:
                        midi_vals.append(int(el.pitches[0].midi))
                    else:
                        midi_vals.append(int(el.pitch.midi))
                ivls = [b - a for a, b in zip(midi_vals, midi_vals[1:])]
                rows.append({
                    'tune_id': Path(file_path).stem,
                    'corpus': corpus_name,
                    'intervals': ivls,
                })
            except Exception:
                continue
    return pd.DataFrame(rows)
