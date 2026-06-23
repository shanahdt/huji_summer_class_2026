"""
utils/keyfinding.py — Comparing key-finding algorithms
Summer Institute 2026 · Hebrew University of Jerusalem

This module answers the Day 3 question: "music21 ships several different
key-finding algorithms — how do their answers compare, for one piece or
across a whole corpus, and how often do they match a ground-truth key?"

The "one-stop" functions each do all three steps for you:
    1. IMPORT   — parse one file or every file in a folder
    2. PROCESS  — run several key-finding algorithms and (optionally) score
                  them against a ground-truth key
    3. OUTPUT   — return a table AND plot it

Beginner usage
---------------
    from utils import compare_keyfinding_algorithms
    table = compare_keyfinding_algorithms('../data/happy_birthday.krn')

    from utils import compare_keyfinding_corpus, load_essen_keys
    ground_truth = load_essen_keys('../data/essen_keys.csv')
    results, summary = compare_keyfinding_corpus(
        '../data/Essen/England', ground_truth=ground_truth)

    from utils import compare_keyscapes
    compare_keyscapes('../data/happy_birthday.krn')
"""

import re
from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.colors import to_rgb
from music21 import analysis, converter, pitch
from music21.analysis import windowed
from scipy import stats

from .ngrams import _gather_files

class AlbrechtShanahan(analysis.discrete.KeyWeightKeyAnalysis):
    """
    Albrecht & Shanahan (2013) key-profile weights, trained on a large
    corpus of pieces rather than derived from listener judgments (compare
    to Krumhansl-Schmuckler, which comes from probe-tone experiments).

    Reference: Albrecht, J. D., & Shanahan, D. (2013). The Use of Large
    Corpora to Train a New Type of Key-Finding Algorithm: An Improved
    Treatment of the Minor Mode. Music Perception, 31(1), 59-67.
    """
    _DOC_ALL_INHERITED = False
    name = 'Albrecht Shanahan Key Analysis'
    identifiers = ['key.albrechtshanahan', 'albrecht-shanahan', 'albrechtshanahan']

    def getWeights(self, weightType='major'):
        weightType = weightType.lower()
        if weightType == 'major':
            return [0.238, 0.006, 0.111, 0.006, 0.137, 0.094, 0.016,
                    0.214, 0.009, 0.080, 0.008, 0.081]
        elif weightType == 'minor':
            return [0.220, 0.006, 0.104, 0.123, 0.019, 0.103, 0.012,
                    0.214, 0.062, 0.022, 0.061, 0.052]
        else:
            raise ValueError(f'weightType must be major or minor, not {weightType}')


# The key-finding algorithms made available by default. The first five come
# from music21's analysis.discrete module; Albrecht-Shanahan is defined just
# above. (KrumhanslKessler is the same underlying weights as
# KrumhanslSchmuckler, so we only list it once to avoid a duplicate row.)
DEFAULT_ALGORITHMS = {
    'Krumhansl-Schmuckler': analysis.discrete.KrumhanslSchmuckler,
    'Aarden-Essen': analysis.discrete.AardenEssen,
    'Simple Weights': analysis.discrete.SimpleWeights,
    'Bellman-Budge': analysis.discrete.BellmanBudge,
    'Temperley-Kostka-Payne': analysis.discrete.TemperleyKostkaPayne,
    'Albrecht-Shanahan': AlbrechtShanahan,
}


def _as_score(file_path_or_score):
    if isinstance(file_path_or_score, (str, Path)):
        return converter.parse(str(file_path_or_score))
    return file_path_or_score


def _resolve_algorithm_class(algorithm):
    """
    Internal helper: turn a name (str), class, or instance into a usable
    KeyWeightKeyAnalysis class. Shared by get_key_profile() and the
    keyscape functions.
    """
    if isinstance(algorithm, str):
        match = next((name for name in DEFAULT_ALGORITHMS
                      if name.lower() == algorithm.lower()), None)
        if match is None:
            raise ValueError(f"Unknown algorithm '{algorithm}'. "
                              f'Choices: {list(DEFAULT_ALGORITHMS)}')
        return DEFAULT_ALGORITHMS[match]
    if isinstance(algorithm, type):
        return algorithm
    return type(algorithm)


def _gather_training_files(source, pattern='*.krn'):
    """
    Internal helper: like _gather_files(), but a list/tuple may also mix in
    folder paths (so you can combine multiple corpora to train on), e.g.
    ['../data/Essen/Italia', '../data/Essen/Deutschl']. Folders are searched
    recursively (some collections, like Deutschl, organize files into
    sub-folders by set), unlike the flat glob() used elsewhere.
    """
    def _files_in(folder):
        return sorted(str(f) for f in Path(folder).rglob(pattern))

    if isinstance(source, (list, tuple)):
        files = []
        for item in source:
            p = Path(item)
            files.extend(_files_in(p) if p.is_dir() else [str(p)])
        return files
    p = Path(source)
    return _files_in(p) if p.is_dir() else [str(p)]


# ── Single piece: compare algorithms against each other ──────────────────────

def compare_keyfinding_algorithms(file_path_or_score, algorithms=None,
                                   plot=True, title=None):
    """
    ONE-STOP function: run several key-finding algorithms on one piece and
    show a table + bar chart comparing what each one decided.

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
        The piece to analyze.
    algorithms : dict, optional
        {label: music21.analysis.discrete class}. Defaults to DEFAULT_ALGORITHMS
        (Krumhansl-Schmuckler, Aarden-Essen, Simple Weights, Bellman-Budge,
        Temperley-Kostka-Payne).
    plot : bool
        If True, show a bar chart of each algorithm's correlation
        coefficient (how confident it was), colored by whether it agrees
        with the majority key.
    title : str, optional
        Custom plot title.

    Returns
    -------
    pd.DataFrame with one row per algorithm:
        algorithm, tonic, mode, key, correlation

    Example
    -------
        table = compare_keyfinding_algorithms('../data/happy_birthday.krn')
        table
    """
    score = _as_score(file_path_or_score)
    algos = algorithms or DEFAULT_ALGORITHMS

    rows = []
    for label, cls in algos.items():
        key = cls().getSolution(score)
        rows.append({
            'algorithm': label,
            'tonic': key.tonic.name,
            'mode': key.mode,
            'key': str(key),
            'correlation': round(float(key.correlationCoefficient), 3),
        })
    table = pd.DataFrame(rows)

    majority_key = table['key'].mode().iloc[0]
    n_unique = table['key'].nunique()
    name = (Path(file_path_or_score).name
            if isinstance(file_path_or_score, (str, Path)) else 'piece')
    print(f'{name}: {n_unique} unique key answer(s) across {len(table)} '
          f'algorithm(s). Majority answer: {majority_key}.')

    if plot:
        colors = ['steelblue' if k == majority_key else 'coral' for k in table['key']]
        plt.figure(figsize=(8, 4))
        plt.bar(table['algorithm'], table['correlation'], color=colors, edgecolor='white')
        for i, row in table.iterrows():
            plt.text(i, row['correlation'] + 0.02, row['key'], ha='center', fontsize=8)
        plt.title(title or f'Key-finding algorithms: {name}\n'
                            f'(blue = agrees with majority, coral = disagrees)')
        plt.ylabel('Correlation coefficient')
        plt.ylim(0, 1.15)
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        plt.show()

    return table


# ── Ground-truth key labels (Essen folksongs / Bach chorales) ───────────────

_MODE_SUFFIXES = {
    'dor': 'dorian', 'mix': 'mixolydian', 'phr': 'phrygian',
    'lyd': 'lydian', 'loc': 'locrian', 'aeo': 'aeolian', 'ion': 'ionian',
}


def parse_kern_key_token(token):
    """
    Parse a humdrum/kern-style key token into (tonic_name, mode).

    Handles the conventions used in this course's data files:
        'g'      -> ('G', 'minor')      lowercase letter = minor
        'A-'     -> ('A-', 'major')     uppercase letter = major, '-' = flat
        'f#'     -> ('F#', 'minor')
        '*ador'  -> ('A', 'dorian')     leading '*' and mode suffixes are OK
        '*Gmix'  -> ('G', 'mixolydian')

    Example
    -------
        parse_kern_key_token('A-')   # -> ('A-', 'major')
        parse_kern_key_token('*gdor')  # -> ('G', 'dorian')
    """
    token = str(token).lstrip('*').strip()
    mode = None
    base = token
    for suffix, name in _MODE_SUFFIXES.items():
        if token.lower().endswith(suffix) and len(token) > len(suffix):
            mode = name
            base = token[:-len(suffix)]
            break

    letter = base[0]
    accidental = base[1:]  # '', '-', or '#'
    tonic_name = letter.upper() + accidental

    if mode is None:
        mode = 'major' if letter.isupper() else 'minor'

    return tonic_name, mode


def load_essen_keys(csv_path):
    """
    Load ground-truth keys for the Essen folksong collection.

    Expects a CSV with no header, where each row is: region, [set,] file_id, key
    — most regions have 3 fields (no subdivision), but some (e.g. Deutschl)
    have 4 fields with a 'set' subfolder in the middle. This is the format
    of data/essen_keys.csv, and rows are read field-by-field rather than by
    fixed column position so both row shapes parse correctly.

    Returns
    -------
    dict — {file_id: {'tonic': str, 'mode': str, 'region': str, 'set': str or None}}

    Example
    -------
        ground_truth = load_essen_keys('../data/essen_keys.csv')
        ground_truth['deut5150']   # -> {'tonic': 'G', 'mode': 'minor', ...}
        ground_truth['england1']   # -> {'tonic': 'G', 'mode': 'major', ...}
    """
    lookup = {}
    with open(csv_path) as f:
        for line in f:
            fields = [x.strip() for x in line.strip().split(',') if x.strip() != '']
            if len(fields) < 3:
                continue
            region, *middle, file_id, key = fields
            set_name = middle[0] if middle else None
            tonic, mode = parse_kern_key_token(key)
            lookup[file_id] = {'tonic': tonic, 'mode': mode,
                                'region': region, 'set': set_name}
    return lookup


def load_chorale_keys(csv_path):
    """
    Load ground-truth keys for the Bach chorales.

    Expects a CSV with no header and columns: tune_id, key (this is the
    format of data/chorale_keys.csv, e.g. 'chor001,*G').

    Returns
    -------
    dict — {tune_id: {'tonic': str, 'mode': str}}

    Example
    -------
        ground_truth = load_chorale_keys('../data/chorale_keys.csv')
        ground_truth['chor001']   # -> {'tonic': 'G', 'mode': 'major'}
    """
    df = pd.read_csv(csv_path, header=None, names=['tune_id', 'key'])
    lookup = {}
    for _, row in df.iterrows():
        tonic, mode = parse_kern_key_token(row['key'])
        lookup[row['tune_id']] = {'tonic': tonic, 'mode': mode}
    return lookup


_KERN_KEY_TOKEN = re.compile(
    r'^\*([A-Ga-g][#-]{0,2}(?:dor|mix|phr|lyd|loc|aeo|ion)?):$')


def load_keys_from_kern(source, pattern='*.krn', verbose=True):
    """
    Build a ground-truth key dict straight from the key token embedded in
    humdrum/kern files themselves (a line like '*G:' or '*a:'), instead of
    a separate CSV. Use this for any kern corpus that ISN'T the Essen
    collection or the Bach chorales (those already have load_essen_keys()/
    load_chorale_keys() for their existing CSVs) — e.g. your own corpus, or
    one without a ground-truth file provided.

    Only the file's first key token is used (its main/opening key), so this
    won't capture modulations — same limitation as the Essen/chorale CSVs.
    Files with no recognizable key token are skipped and reported, not
    silently guessed.

    Parameters
    ----------
    source : str, Path, or list
        A folder of kern files (searched recursively), or a list of files.
    pattern : str
        Glob pattern when `source` is a folder (default '*.krn').
    verbose : bool
        Print how many files had a key found vs. not.

    Returns
    -------
    dict — {tune_id: {'tonic': str, 'mode': str}}, the same shape as
    load_essen_keys() / load_chorale_keys() — feed straight into
    compare_keyfinding_corpus(), train_key_profile(), train_and_test_key_
    algorithm(), etc.

    Example
    -------
        ground_truth = load_keys_from_kern('../data/my_corpus')
        results, summary = compare_keyfinding_corpus(
            '../data/my_corpus', ground_truth=ground_truth)
    """
    files = _gather_training_files(source, pattern)
    lookup = {}
    not_found = []

    for f in files:
        tune_id = Path(f).stem
        found = None
        try:
            with open(f, errors='ignore') as fh:
                for line in fh:
                    first_col = line.split('\t')[0].strip()
                    m = _KERN_KEY_TOKEN.match(first_col)
                    if m:
                        found = m.group(1)
                        break
        except OSError as e:
            not_found.append(tune_id)
            continue

        if found:
            tonic, mode = parse_kern_key_token(found)
            lookup[tune_id] = {'tonic': tonic, 'mode': mode}
        else:
            not_found.append(tune_id)

    if verbose:
        print(f'Found a key for {len(lookup)}/{len(files)} file(s).')
        if not_found:
            preview = ', '.join(not_found[:10])
            print(f'No key token found in {len(not_found)} file(s): {preview}'
                  f'{", ..." if len(not_found) > 10 else ""}')

    return lookup


_TITLE_KEY = re.compile(
    r'\bin\s+([A-Ga-g])(-flat|-sharp|b|#)?\s+(major|minor)\b', re.IGNORECASE)


def _accidental_from_word(token):
    """Internal helper: '-flat'/'b' -> '-', '-sharp'/'#' -> '#', else ''."""
    if not token:
        return ''
    token = token.lower()
    if 'flat' in token or token == 'b':
        return '-'
    if 'sharp' in token or token == '#':
        return '#'
    return ''


def load_keys_from_title(source, pattern='*.krn', verbose=True):
    """
    Build a ground-truth key dict by reading the key straight out of a
    piece's title (the humdrum '!!!OTL:' reference record), e.g.
    'String Quartet No. 1 in F Major, Op. 18, No. 1' -> F major.

    Use this when load_keys_from_kern() finds almost nothing — some
    corpora (e.g. Beethoven's quartets in this course's data) carry a key
    SIGNATURE ('*k[b-]') but never an actual key token ('*F:'). Classical
    instrumental works (quartets, sonatas, symphonies, concertos) are
    conventionally named by key, so the title is a reliable fallback.

    Caveat: this gives the work's OVERALL announced key, not necessarily
    the key of every individual movement (an inner movement may be in a
    related key) — same "main key only" limitation as the other ground-
    truth loaders in this module. If a corpus has neither a key token nor
    a key in its title, you'll need to label it by hand.

    Parameters
    ----------
    source : str, Path, or list
        A folder of kern files (searched recursively), or a list of files.
    pattern : str
        Glob pattern when `source` is a folder (default '*.krn').
    verbose : bool
        Print how many files had a key found vs. not.

    Returns
    -------
    dict — {tune_id: {'tonic': str, 'mode': str}}, the same shape as
    load_essen_keys() / load_chorale_keys() / load_keys_from_kern().

    Example
    -------
        ground_truth = load_keys_from_title('../data/humdrum_scores/Beethoven')
        results, summary = compare_keyfinding_corpus(
            '../data/humdrum_scores/Beethoven', ground_truth=ground_truth)
    """
    files = _gather_training_files(source, pattern)
    lookup = {}
    not_found = []

    for f in files:
        tune_id = Path(f).stem
        title = None
        try:
            with open(f, errors='ignore') as fh:
                for line in fh:
                    if line.startswith('!!!OTL'):
                        title = line.split(':', 1)[1].strip() if ':' in line else None
                        break
        except OSError:
            not_found.append(tune_id)
            continue

        m = _TITLE_KEY.search(title) if title else None
        if m:
            letter, acc, mode = m.groups()
            tonic = letter.upper() + _accidental_from_word(acc)
            lookup[tune_id] = {'tonic': tonic, 'mode': mode.lower()}
        else:
            not_found.append(tune_id)

    if verbose:
        print(f'Found a key in the title for {len(lookup)}/{len(files)} file(s).')
        if not_found:
            preview = ', '.join(not_found[:10])
            print(f'No key found in title for {len(not_found)} file(s): {preview}'
                  f'{", ..." if len(not_found) > 10 else ""}')

    return lookup


# ── Corpus-level comparison (optionally against ground truth) ───────────────

def compare_keyfinding_corpus(source, pattern='*.krn', algorithms=None,
                               ground_truth=None, plot=True, verbose=True):
    """
    ONE-STOP function: run several key-finding algorithms over every piece
    in a folder, optionally score them against ground-truth keys, and show
    a table + bar chart of how each algorithm performed.

    Parameters
    ----------
    source : str, Path, or list
        A folder of files, or a list of file paths.
    pattern : str
        Glob pattern when `source` is a folder (default '*.krn').
    algorithms : dict, optional
        {label: music21.analysis.discrete class}. Defaults to DEFAULT_ALGORITHMS.
    ground_truth : dict, optional
        {tune_id: {'tonic': str, 'mode': str}}, e.g. from load_essen_keys()
        or load_chorale_keys(). If given, accuracy is computed against it.
        If omitted, algorithms are instead scored by how often they agree
        with the majority vote across algorithms for each piece.
    plot : bool
        If True, show a bar chart summarizing each algorithm's performance.
    verbose : bool
        Print progress while loading files.

    Returns
    -------
    results : pd.DataFrame
        One row per (piece, algorithm): tune_id, algorithm, tonic, mode,
        correlation, and (if ground_truth given) tonic_correct, mode_correct,
        both_correct.
    summary : pd.DataFrame
        One row per algorithm with mean correlation and (if ground_truth
        given) tonic/mode/overall accuracy, or (otherwise) agreement rate
        with the majority vote.

    Example
    -------
        ground_truth = load_essen_keys('../data/essen_keys.csv')
        results, summary = compare_keyfinding_corpus(
            '../data/Essen/England', ground_truth=ground_truth)
        summary
    """
    files = _gather_files(source, pattern)
    algos = algorithms or DEFAULT_ALGORITHMS

    rows = []
    skipped = []
    for i, f in enumerate(files):
        if verbose and i % 25 == 0:
            print(f'  Analyzing {i + 1}/{len(files)}...')
        tune_id = Path(f).stem
        try:
            score = converter.parse(f)
        except Exception as e:
            skipped.append((f, str(e)))
            continue

        for label, cls in algos.items():
            try:
                key = cls().getSolution(score)
            except Exception:
                continue
            row = {
                'tune_id': tune_id,
                'algorithm': label,
                'tonic': key.tonic.name,
                'mode': key.mode,
                'correlation': round(float(key.correlationCoefficient), 3),
            }
            if ground_truth and tune_id in ground_truth:
                truth = ground_truth[tune_id]
                row['tonic_correct'] = row['tonic'] == truth['tonic']
                row['mode_correct'] = row['mode'] == truth['mode']
                row['both_correct'] = row['tonic_correct'] and row['mode_correct']
            rows.append(row)

    if verbose and skipped:
        print(f'Skipped {len(skipped)} unreadable file(s).')

    results = pd.DataFrame(rows)
    if results.empty:
        print('No pieces could be analyzed.')
        return results, pd.DataFrame()

    if ground_truth and 'both_correct' in results.columns:
        summary = results.groupby('algorithm').agg(
            mean_correlation=('correlation', 'mean'),
            tonic_accuracy=('tonic_correct', 'mean'),
            mode_accuracy=('mode_correct', 'mean'),
            overall_accuracy=('both_correct', 'mean'),
            n_pieces=('tune_id', 'nunique'),
        ).reset_index()
        score_col, score_label = 'overall_accuracy', 'Accuracy vs. ground truth'
    else:
        # No ground truth: score each algorithm by agreement with the
        # majority key chosen across algorithms, per piece.
        majority = (results.groupby('tune_id')['algorithm']
                    .apply(lambda s: None))  # placeholder, replaced below
        key_per_piece = results.assign(key=results['tonic'] + ' ' + results['mode'])
        majority_key = (key_per_piece.groupby('tune_id')['key']
                         .agg(lambda s: s.value_counts().idxmax()))
        key_per_piece['agrees_with_majority'] = key_per_piece.apply(
            lambda r: r['key'] == majority_key[r['tune_id']], axis=1)
        summary = key_per_piece.groupby('algorithm').agg(
            mean_correlation=('correlation', 'mean'),
            agreement_rate=('agrees_with_majority', 'mean'),
            n_pieces=('tune_id', 'nunique'),
        ).reset_index()
        score_col, score_label = 'agreement_rate', 'Agreement with majority vote'

    if plot:
        plt.figure(figsize=(8, 4.5))
        plt.bar(summary['algorithm'], summary[score_col], color='steelblue', edgecolor='white')
        plt.title(f'{score_label} ({len(files)} piece(s))')
        plt.ylabel(score_label)
        plt.ylim(0, 1.05)
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        plt.show()

    return results, summary


# ── Bach chorales: wide-format table (annotated key + every algorithm) ──────

def bach_chorale_key_table(chorale_dir='../data/humdrum_scores/Bach/Chorales/371chorales',
                            ground_truth_csv='../data/chorale_keys.csv',
                            pattern='chor*.krn', algorithms=None, verbose=True):
    """
    ONE-STOP function: run every key-finding algorithm on every Bach chorale
    and build a single wide table — one row per chorale, one column for the
    annotated (ground-truth) key, and one column per algorithm showing its
    guess as 'Tonic mode (correlation)', e.g. 'G major (0.91)'.

    Parameters
    ----------
    chorale_dir : str or Path
        Folder of chorale kern files. Defaults to the 371 chorales shipped
        with the course data.
    ground_truth_csv : str or Path
        CSV of annotated keys. Defaults to data/chorale_keys.csv.
    pattern : str
        Glob pattern for chorale files (default 'chor*.krn' — this already
        excludes the per-voice files like chor001.krn.soprano, since those
        don't end in '.krn').
    algorithms : dict, optional
        {label: music21.analysis.discrete class}. Defaults to DEFAULT_ALGORITHMS.
    verbose : bool
        Print progress while analyzing.

    Returns
    -------
    pd.DataFrame — columns: tune_id, annotated_key, then one column per
    algorithm (e.g. 'Aarden-Essen') with values like 'G major (0.91)'.

    Example
    -------
        table = bach_chorale_key_table()
        table.head()
    """
    ground_truth = load_chorale_keys(ground_truth_csv)
    files = sorted(Path(chorale_dir).glob(pattern))
    algos = algorithms or DEFAULT_ALGORITHMS

    rows = []
    skipped = []
    for i, f in enumerate(files):
        if verbose and i % 50 == 0:
            print(f'  Analyzing {i + 1}/{len(files)}...')
        tune_id = f.stem
        try:
            score = converter.parse(str(f))
        except Exception as e:
            skipped.append((str(f), str(e)))
            continue

        truth = ground_truth.get(tune_id)
        row = {
            'tune_id': tune_id,
            'annotated_key': f"{truth['tonic']} {truth['mode']}" if truth else 'unknown',
        }
        for label, cls in algos.items():
            try:
                key = cls().getSolution(score)
                row[label] = (f'{key.tonic.name} {key.mode} '
                               f'({key.correlationCoefficient:.2f})')
            except Exception:
                row[label] = None
        rows.append(row)

    if verbose:
        print(f'Analyzed {len(rows)} chorale(s).')
        if skipped:
            print(f'Skipped {len(skipped)} unreadable file(s).')

    return pd.DataFrame(rows)


# ── Build-your-own key-finding algorithm ─────────────────────────────────────

def get_key_profile(algorithm):
    """
    Extract the major/minor key-profile weights (12 numbers each) from a
    key-finding algorithm, so you can inspect, copy, and modify them before
    building your own custom algorithm with make_key_algorithm().

    Parameters
    ----------
    algorithm : str, class, or instance
        One of:
          - the name of a built-in algorithm (matching DEFAULT_ALGORITHMS,
            e.g. 'Krumhansl-Schmuckler', 'Aarden-Essen')
          - a music21.analysis.discrete.KeyWeightKeyAnalysis subclass
          - an already-created instance of one

    Returns
    -------
    dict — {'major': [12 floats], 'minor': [12 floats]}
        Each list is ordered by semitone distance above the tonic
        (index 0 = tonic, index 7 = the fifth, etc.).

    Example
    -------
        profile = get_key_profile('Krumhansl-Schmuckler')
        my_major = profile['major'][:]   # copy so you can edit freely
        my_major[7] *= 1.5               # exaggerate the importance of the fifth
        # now feed my_major into make_key_algorithm() or test_custom_key_algorithm()
    """
    if isinstance(algorithm, str):
        match = next((name for name in DEFAULT_ALGORITHMS
                      if name.lower() == algorithm.lower()), None)
        if match is None:
            raise ValueError(f"Unknown algorithm '{algorithm}'. "
                              f'Choices: {list(DEFAULT_ALGORITHMS)}')
        algorithm = DEFAULT_ALGORITHMS[match]

    instance = algorithm() if isinstance(algorithm, type) else algorithm
    return {
        'major': list(instance.getWeights('major')),
        'minor': list(instance.getWeights('minor')),
    }


def make_key_algorithm(major_weights, minor_weights, name='Custom'):
    """
    Build your own key-finding algorithm from a pair of 12-number weight
    profiles, so it can be used anywhere a built-in algorithm (like
    AardenEssen or KrumhanslSchmuckler) can be used.

    Parameters
    ----------
    major_weights, minor_weights : list of 12 floats
        How strongly each of the 12 pitch classes (starting at the tonic)
        is associated with a major / minor key. Higher = stronger association.
        Get a starting point with get_key_profile().
    name : str
        Label for the algorithm (shown in tables and plots).

    Returns
    -------
    A music21.analysis.discrete.KeyWeightKeyAnalysis subclass. Call it with
    () to make an instance, the same way you'd use a built-in algorithm:
        MyAlgorithm = make_key_algorithm(major, minor, name='My Profile')
        key = MyAlgorithm().getSolution(score)

    Example
    -------
        major = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
        minor = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
        MyAlgorithm = make_key_algorithm(major, minor, name='My Profile')
    """
    if len(major_weights) != 12 or len(minor_weights) != 12:
        raise ValueError('major_weights and minor_weights must each have '
                          'exactly 12 numbers (one per pitch class, starting '
                          'at the tonic).')

    major_weights = list(major_weights)
    minor_weights = list(minor_weights)

    class CustomKeyAlgorithm(analysis.discrete.KeyWeightKeyAnalysis):
        pass

    CustomKeyAlgorithm.name = f'{name} Key Analysis'

    def getWeights(self, weightType='major'):
        weightType = weightType.lower()
        if weightType == 'major':
            return major_weights
        elif weightType == 'minor':
            return minor_weights
        raise ValueError("weightType must be 'major' or 'minor'")

    CustomKeyAlgorithm.getWeights = getWeights
    return CustomKeyAlgorithm


def test_custom_key_algorithm(major_weights, minor_weights, source,
                               pattern='*.krn', name='Custom',
                               ground_truth=None, compare_to_defaults=True,
                               plot=True, verbose=True):
    """
    ONE-STOP function: build a custom key-finding algorithm from your own
    major/minor weight profiles, then test it across a corpus — optionally
    side-by-side with the built-in algorithms and/or scored against
    ground-truth keys — table + plot in one call.

    Parameters
    ----------
    major_weights, minor_weights : list of 12 floats
        Your custom key-profile weights (see get_key_profile() to start from
        a built-in profile, or make_key_algorithm() to build the algorithm
        without testing it).
    source : str, Path, or list
        A folder of files, or a list of file paths.
    pattern : str
        Glob pattern when `source` is a folder (default '*.krn').
    name : str
        Label for your algorithm in the results.
    ground_truth : dict, optional
        From load_essen_keys() / load_chorale_keys() — if given, accuracy is
        computed against it.
    compare_to_defaults : bool
        If True (default), also run the 5 built-in algorithms so you can see
        how your custom profile stacks up.
    plot, verbose : bool

    Returns
    -------
    results, summary — same shape as compare_keyfinding_corpus()

    Example
    -------
        profile = get_key_profile('Aarden-Essen')
        my_major = profile['major'][:]
        my_major[7] *= 1.5   # exaggerate the dominant
        ground_truth = load_essen_keys('../data/essen_keys.csv')
        results, summary = test_custom_key_algorithm(
            my_major, profile['minor'], '../data/Essen/England',
            name='Boosted Dominant', ground_truth=ground_truth)
    """
    custom_algorithm = make_key_algorithm(major_weights, minor_weights, name=name)
    algorithms = {name: custom_algorithm}
    if compare_to_defaults:
        algorithms.update(DEFAULT_ALGORITHMS)

    return compare_keyfinding_corpus(source, pattern=pattern, algorithms=algorithms,
                                      ground_truth=ground_truth, plot=plot,
                                      verbose=verbose)


# ── Train your own key-profile on a corpus, then test it elsewhere ──────────

def train_key_profile(source, ground_truth, pattern='*.krn', verbose=True):
    """
    BUILD YOUR OWN key-profile weights by counting how often each scale
    degree actually shows up in a corpus of pieces with known keys. This is
    the corpus-trained approach (the same idea behind Albrecht-Shanahan), as
    opposed to Krumhansl-Schmuckler's weights, which came from listener
    judgments rather than counting notes.

    For every piece, each note is shifted so the tonic = position 0, then
    tallied into a 12-slot histogram — kept separate for major-mode and
    minor-mode pieces — and each histogram is normalized to sum to 1. Feed
    the result straight into make_key_algorithm() or
    test_custom_key_algorithm() (or use train_and_test_key_algorithm() below
    to do both steps in one call).

    Parameters
    ----------
    source : str, Path, or list
        What to train on. Can be one folder, a LIST OF FOLDERS (e.g. the
        Italian and German corpora combined), or a list of individual files.
    ground_truth : dict
        {tune_id: {'tonic': str, 'mode': str}} — from load_essen_keys() or
        load_chorale_keys(). Required: training needs to know each piece's
        true tonic. Pieces missing from this dict, or labeled with a mode
        other than 'major'/'minor' (e.g. 'dorian'), are skipped.
    pattern : str
        Glob pattern used for any folder in `source` (default '*.krn').
    verbose : bool
        Print how many pieces were used vs. skipped.

    Returns
    -------
    dict — {'major': [12 floats], 'minor': [12 floats]}, each summing to 1.0
    (all-zero if no pieces of that mode were found — watch for this with
    small or narrow corpora).

    Example
    -------
        ground_truth = load_essen_keys('../data/essen_keys.csv')
        profile = train_key_profile(
            ['../data/Essen/Italia', '../data/Essen/Deutschl'], ground_truth)
        profile['major']
    """
    files = _gather_training_files(source, pattern)

    major_counts = [0] * 12
    minor_counts = [0] * 12
    n_major = n_minor = 0
    skipped = []

    for f in files:
        tune_id = Path(f).stem
        truth = ground_truth.get(tune_id)
        if truth is None:
            skipped.append((f, 'no ground-truth key'))
            continue
        if truth['mode'] not in ('major', 'minor'):
            skipped.append((f, f"mode '{truth['mode']}' isn't major/minor"))
            continue
        try:
            score = converter.parse(f)
            tonic_pc = pitch.Pitch(truth['tonic']).pitchClass
        except Exception as e:
            skipped.append((f, str(e)))
            continue

        counts = major_counts if truth['mode'] == 'major' else minor_counts
        for n in score.flatten().notes:
            for p in (n.pitches if n.isChord else [n.pitch]):
                counts[(p.pitchClass - tonic_pc) % 12] += 1

        if truth['mode'] == 'major':
            n_major += 1
        else:
            n_minor += 1

    if verbose:
        print(f'Trained on {n_major + n_minor} piece(s): '
              f'{n_major} major, {n_minor} minor.')
        if skipped:
            print(f'Skipped {len(skipped)} piece(s) (no ground truth, '
                  f'unreadable, or non-major/minor mode).')

    major_total = sum(major_counts) or 1
    minor_total = sum(minor_counts) or 1
    return {
        'major': [c / major_total for c in major_counts],
        'minor': [c / minor_total for c in minor_counts],
    }


def train_and_test_key_algorithm(train_source, test_source, ground_truth,
                                  pattern='*.krn', name='Trained',
                                  compare_to_defaults=True, plot=True,
                                  verbose=True):
    """
    ONE-STOP function: train your own key-profile weights on one corpus
    (or combination of corpora), then test how well the resulting algorithm
    generalizes to a DIFFERENT corpus — table + plot in one call.

    This is the exercise behind Albrecht-Shanahan: pick what you train on,
    pick what you test on, and see how well an empirically-trained profile
    transfers to repertoire it has never seen.

    Parameters
    ----------
    train_source : str, Path, or list
        Corpus (or corpora!) to train weights on — one folder, a list of
        folders (e.g. Italian + German together), or a list of files.
    test_source : str, Path, or list
        A DIFFERENT corpus to test the trained algorithm on (and to compare
        against the built-in algorithms, if compare_to_defaults=True).
    ground_truth : dict
        {tune_id: {'tonic': str, 'mode': str}}, from load_essen_keys() or
        load_chorale_keys(). Used both to train the weights (on train_source)
        and to score accuracy on the test corpus (test_source) — so it needs
        to cover tune_ids from both.
    pattern : str
        Glob pattern used for any folder in train_source/test_source.
    name : str
        Label for your trained algorithm in the results.
    compare_to_defaults : bool
        If True (default), also run the built-in algorithms on the test
        corpus for comparison.
    plot, verbose : bool

    Returns
    -------
    profile : dict — {'major': [...], 'minor': [...]}, the weights learned
        from train_source.
    results, summary — same shape as compare_keyfinding_corpus(), scored on
        test_source.

    Example
    -------
        ground_truth = load_essen_keys('../data/essen_keys.csv')
        profile, results, summary = train_and_test_key_algorithm(
            train_source=['../data/Essen/Italia', '../data/Essen/Deutschl'],
            test_source='../data/Essen/Czech',
            ground_truth=ground_truth,
            name='Italian+German')
        summary
    """
    if verbose:
        print('Training...')
    profile = train_key_profile(train_source, ground_truth, pattern=pattern,
                                 verbose=verbose)

    if verbose:
        print('\nTesting on a different corpus...')
    results, summary = test_custom_key_algorithm(
        profile['major'], profile['minor'], test_source, pattern=pattern,
        name=name, ground_truth=ground_truth,
        compare_to_defaults=compare_to_defaults, plot=plot, verbose=verbose)

    return profile, results, summary


# ── Keyscapes: visualizing key-finding across window size and position ──────

def _keyscape_data(score, algorithm, min_window=1, max_window=None,
                    window_step='pow2', window_type='overlap',
                    window_size=None):
    """
    Internal helper: run music21's windowed key analysis for one algorithm
    and return (colors, meta, processor). `colors` is a list of rows (one
    per window size), each row a list of hex color strings, one per window
    position — short rows for big windows, long rows for small windows. This
    triangular shape *is* the keyscape.

    Window sizes are measured in quarter notes (beats) — the span of the
    piece each key is computed over — NOT a count of individual notes.

    If `window_size` is given, it overrides min_window/max_window/window_step
    and analyzes ONLY that one window size (a single row/strip, not a
    triangle) — and skips music21's automatic extra "whole piece" row.
    """
    algo_cls = _resolve_algorithm_class(algorithm)
    processor = algo_cls()
    wa = windowed.WindowedAnalysis(score, processor)
    if window_size is not None:
        _solutions, colors, meta = wa.process(
            window_size, window_size, 1, windowType=window_type,
            includeTotalWindow=False)
    else:
        _solutions, colors, meta = wa.process(
            min_window, max_window, window_step, windowType=window_type)
    return colors, meta, processor


def _keyscape_grid(colors_matrix):
    """
    Internal helper: turn a list of rows of hex colors (ragged — shorter at
    the top, where windows are bigger) into a rectangular (rows, cols, 3)
    RGB array, centering each row so the result renders as a triangle.
    """
    max_len = max(len(row) for row in colors_matrix)
    grid = np.ones((len(colors_matrix), max_len, 3))  # white background
    for r, row in enumerate(colors_matrix):
        pad = (max_len - len(row)) // 2
        for c, hexcolor in enumerate(row):
            grid[r, pad + c] = to_rgb(hexcolor or '#ffffff')
    return grid


_KEY_SORT_ORDER = ['C-', 'C', 'C#', 'D-', 'D', 'D#', 'E-', 'E', 'F', 'F#',
                    'G-', 'G', 'G#', 'A-', 'A', 'A#', 'B-', 'B']


def _merge_key_legends(legends):
    """
    Internal helper: combine several per-algorithm solutionLegend(compress=
    True) outputs into one legend covering every key used by ANY of them,
    sorted consistently — so a single shared legend works for a whole row
    of compare_keyscapes() panels.
    """
    major, minor = {}, {}
    for legend in legends:
        for row_label, pairs in legend:
            target = major if row_label == 'Major' else minor
            for keyname, color in pairs:
                if keyname:
                    target[keyname] = color

    def _ordered(d, lower):
        order = [k.lower() if lower else k for k in _KEY_SORT_ORDER]
        return [(k, d[k]) for k in order if k in d]

    return [['Major', _ordered(major, lower=False)],
            ['Minor', _ordered(minor, lower=True)]]


def _draw_key_legend(ax, legend_data):
    """Internal helper: draw a compact 'Major'/'Minor' color-swatch legend
    (from processor.solutionLegend()) onto a given matplotlib Axes."""
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    for row_i, (_label, pairs) in enumerate(legend_data):
        used = [(k, c) for k, c in pairs if k]
        n = max(len(used), 1)
        y = 0.55 if row_i == 0 else 0.05
        for i, (keyname, color) in enumerate(used):
            x = i / n
            ax.add_patch(mpatches.Rectangle((x, y), 0.8 / n, 0.35, color=color))
            ax.text(x + 0.4 / n, y - 0.05, keyname, ha='center', va='top', fontsize=7)


def keyscape(file_path_or_score, algorithm='Krumhansl-Schmuckler',
             window_size=None, min_window=1, max_window=None,
             window_step='pow2', plot=True, title=None, figsize=(8, 5)):
    """
    ONE-STOP function: plot a keyscape for a piece — a triangular diagram
    showing the key a chosen algorithm detects in EVERY contiguous window of
    the piece, at every window size. The bottom row uses the smallest
    windows (most local, most "noisy"); the single point at the top is the
    whole piece analyzed as one window. Color = detected key (see the
    legend below the plot). Great for spotting modulations or ambiguous
    passages at a glance.

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    algorithm : str, class, or instance
        Which key-finding algorithm to use. A name from DEFAULT_ALGORITHMS
        (e.g. 'Krumhansl-Schmuckler', 'Albrecht-Shanahan'), or an algorithm
        you built yourself with make_key_algorithm().
    window_size : int, optional
        Fix the analysis to ONE window size — the span (in quarter notes,
        i.e. beats — NOT number of notes) over which each key is computed —
        instead of a whole range. The plot becomes a single horizontal strip
        (one key detected per window of that many beats, slid across the
        piece) rather than a triangle. E.g. window_size=8 computes a key for
        every 8-beat span. Overrides min_window/max_window/window_step.
    min_window, max_window : int
        Used when window_size is None. Smallest / largest window size, in
        quarter notes (beats), not number of notes. max_window=None analyzes
        up to the whole piece.
    window_step : int or 'pow2'
        Used when window_size is None. Spacing between window sizes tested.
        'pow2' (default) only tests sizes that double each time
        (1, 2, 4, 8, ...) — much faster than testing every single size.
    plot : bool
        If True, draw the keyscape + legend.
    title : str, optional
    figsize : tuple

    Returns
    -------
    colors : list of lists of hex color strings (one list per window size,
        smallest window first — just one list if window_size was given)
    meta : list of dicts, e.g. [{'windowSize': 1}, {'windowSize': 2}, ...]

    Example
    -------
        colors, meta = keyscape('../data/happy_birthday.krn')
        colors, meta = keyscape('../data/happy_birthday.krn',
                                 algorithm='Albrecht-Shanahan')

        # just one fixed window size, as a single strip:
        colors, meta = keyscape('../data/happy_birthday.krn', window_size=8)
    """
    score = _as_score(file_path_or_score)
    colors, meta, processor = _keyscape_data(
        score, algorithm, min_window=min_window, max_window=max_window,
        window_step=window_step, window_size=window_size)

    if plot:
        name = (Path(file_path_or_score).name
                if isinstance(file_path_or_score, (str, Path)) else 'piece')
        algo_label = algorithm if isinstance(algorithm, str) else (
            algorithm.__name__ if isinstance(algorithm, type) else type(algorithm).__name__)

        grid = _keyscape_grid(colors)
        if window_size is not None:
            height_ratios = [1, 1]
            if figsize == (8, 5):
                figsize = (8, 2.5)
        else:
            height_ratios = [5, 1]
        fig, (ax1, ax2) = plt.subplots(
            2, 1, figsize=figsize, gridspec_kw={'height_ratios': height_ratios})
        ax1.imshow(grid, aspect='auto', origin='lower')
        ax1.set_yticks(range(len(meta)))
        ax1.set_yticklabels([m['windowSize'] for m in meta], fontsize=8)
        ax1.set_ylabel('Window size (quarter notes)')
        ax1.set_xticks([])
        ax1.set_xlabel('Position in piece →')
        ax1.set_title(title or f'Keyscape: {name} ({algo_label})')
        _draw_key_legend(ax2, processor.solutionLegend(compress=True))
        plt.tight_layout()
        plt.show()

    return colors, meta


def compare_keyscapes(file_path_or_score, algorithms=None, window_size=None,
                       min_window=1, max_window=None, window_step='pow2',
                       figsize=None, title=None):
    """
    ONE-STOP function: plot keyscapes for SEVERAL key-finding algorithms on
    the same piece, side by side, so you can compare at a glance where they
    agree (same colors stacked the same way) and where they disagree
    (different colors in the same spot) — especially in the small-window
    rows near the bottom, where algorithms tend to differ most.

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    algorithms : dict, optional
        {label: algorithm}. Defaults to DEFAULT_ALGORITHMS (all 6 built-ins).
        Values can also be algorithms you built with make_key_algorithm().
    window_size : int, optional
        Fix the analysis to ONE window size — the span (in quarter notes,
        i.e. beats — NOT number of notes) over which each key is computed.
        Each panel becomes a single horizontal strip rather than a triangle,
        which makes side-by-side disagreements easier to scan. Overrides
        min_window/max_window/window_step when given.
    min_window, max_window, window_step : see keyscape() (used when
        window_size is None)
    figsize : tuple, optional
        Defaults to scale with the number of algorithms shown.
    title : str, optional
        Overall figure title.

    Returns
    -------
    dict — {label: (colors, meta)} for each algorithm, same shape as the
    return value of keyscape().

    Example
    -------
        compare_keyscapes('../data/happy_birthday.krn')

        # just two algorithms, side by side:
        from utils import DEFAULT_ALGORITHMS
        compare_keyscapes('../data/happy_birthday.krn', algorithms={
            'Krumhansl-Schmuckler': DEFAULT_ALGORITHMS['Krumhansl-Schmuckler'],
            'Albrecht-Shanahan': DEFAULT_ALGORITHMS['Albrecht-Shanahan'],
        })

        # fix one window size (8 quarter notes / beats) instead of the
        # full triangle:
        compare_keyscapes('../data/happy_birthday.krn', window_size=8)
    """
    score = _as_score(file_path_or_score)
    algos = algorithms or DEFAULT_ALGORITHMS
    n = len(algos)
    height_ratios = [1, 1] if window_size is not None else [5, 1]
    figsize = figsize or (3.2 * n, 2.5 if window_size is not None else 5)

    name = (Path(file_path_or_score).name
            if isinstance(file_path_or_score, (str, Path)) else 'piece')

    fig, axes = plt.subplots(
        2, n, figsize=figsize, gridspec_kw={'height_ratios': height_ratios})
    if n == 1:
        axes = axes.reshape(2, 1)

    output = {}
    per_algo_legends = []
    for i, (label, algorithm) in enumerate(algos.items()):
        colors, meta, processor = _keyscape_data(
            score, algorithm, min_window=min_window, max_window=max_window,
            window_step=window_step, window_size=window_size)
        output[label] = (colors, meta)
        per_algo_legends.append(processor.solutionLegend(compress=True))

        grid = _keyscape_grid(colors)
        ax = axes[0, i]
        ax.imshow(grid, aspect='auto', origin='lower')
        ax.set_yticks(range(len(meta)))
        ax.set_yticklabels([m['windowSize'] for m in meta], fontsize=7)
        ax.set_xticks([])
        ax.set_title(label, fontsize=9)
        if i == 0:
            ax.set_ylabel('Window size (quarter notes)')

    # one shared legend, centered under the whole row
    for ax in axes[1]:
        ax.axis('off')
    legend_ax = fig.add_axes([0.15, 0.0, 0.7, 0.12])
    legend_ax.axis('off')
    if per_algo_legends:
        _draw_key_legend(legend_ax, _merge_key_legends(per_algo_legends))

    fig.suptitle(title or f'Keyscape comparison: {name}')
    plt.tight_layout(rect=(0, 0.08, 1, 1))
    plt.show()

    return output


# ── Statistical hypothesis testing: comparing algorithms rigorously ─────────
#
# These all take the `results` table (NOT `summary`) returned by
# compare_keyfinding_corpus() / test_custom_key_algorithm() — one row per
# (piece, algorithm) — and run a standard hypothesis test on it, with a plot.

def chi_square_accuracy(results, correct_col='both_correct', plot=True,
                         figsize=(8, 4.5), title=None):
    """
    HYPOTHESIS TEST: does ACCURACY (hits vs. misses) depend on which
    algorithm you use? Runs a chi-square test of independence on a
    hits/misses contingency table (algorithm x correct/incorrect).

    Null hypothesis (H0): accuracy is independent of algorithm — i.e. every
    algorithm has the same underlying hit rate, and any differences you see
    are just noise.

    Parameters
    ----------
    results : pd.DataFrame
        The `results` table from compare_keyfinding_corpus() /
        test_custom_key_algorithm() — needs an 'algorithm' column and a
        ground-truth-derived correctness column. Only present if you called
        that function WITH a ground_truth argument.
    correct_col : str
        Which correctness column to test: 'both_correct' (tonic AND mode,
        default), 'tonic_correct', or 'mode_correct'.
    plot : bool
        If True, show a stacked bar chart of hits vs. misses per algorithm.
    figsize : tuple
    title : str, optional

    Returns
    -------
    table : pd.DataFrame — the hits/misses contingency table
    chi2 : float — chi-square statistic
    p : float — p-value
    dof : int — degrees of freedom

    Example
    -------
        ground_truth = load_essen_keys('../data/essen_keys.csv')
        results, summary = compare_keyfinding_corpus(
            '../data/Essen/England', ground_truth=ground_truth)
        table, chi2, p, dof = chi_square_accuracy(results)
    """
    if correct_col not in results.columns:
        raise ValueError(
            f"'{correct_col}' not found in results. Did you call "
            f"compare_keyfinding_corpus() / test_custom_key_algorithm() "
            f"WITH a ground_truth argument? That's what adds the "
            f"tonic_correct / mode_correct / both_correct columns.")

    table = pd.crosstab(results['algorithm'], results[correct_col])
    table = table.rename(columns={True: 'Correct', False: 'Incorrect'})
    for col in ('Correct', 'Incorrect'):
        if col not in table.columns:
            table[col] = 0
    table = table[['Correct', 'Incorrect']]

    # chi-square needs variation in BOTH outcomes (some hits and some misses
    # overall) — if every algorithm was 100% right (or 100% wrong), there's
    # nothing to test, and scipy would otherwise raise a cryptic error.
    no_variation = table['Correct'].sum() == 0 or table['Incorrect'].sum() == 0
    if no_variation:
        chi2, p, dof = None, None, None
        print(f"Every algorithm scored the same on '{correct_col}' (all correct, "
              f"or all incorrect) — there's no variation to test. Try a bigger "
              f"corpus, or a `correct_col` that actually varies.")
    else:
        chi2, p, dof, _expected = stats.chi2_contingency(table)
        print(f"Chi-square test of independence — accuracy ({correct_col}) vs. algorithm:")
        print(f'  chi2 = {chi2:.3f}, dof = {dof}, p = {p:.4f}')
        if p < 0.05:
            print('  -> p < 0.05: accuracy differs significantly across algorithms.')
        else:
            print('  -> p >= 0.05: no significant evidence that accuracy differs by algorithm.')

    if plot:
        table.plot(kind='bar', stacked=True, figsize=figsize,
                   color=['steelblue', 'coral'], edgecolor='white')
        stat_str = (f'chi2={chi2:.2f}, dof={dof}, p={p:.4f}' if chi2 is not None
                    else 'no variation to test')
        plt.title(title or f'Hits vs. misses by algorithm ({correct_col})\n{stat_str}')
        plt.ylabel('Number of pieces')
        plt.xlabel('Algorithm')
        plt.xticks(rotation=30, ha='right')
        plt.legend(title=None)
        plt.tight_layout()
        plt.show()

    return table, chi2, p, dof


def ttest_algorithm_correlations(results, algorithm_a, algorithm_b, paired=True,
                                  plot=True, figsize=(5, 4.5), title=None):
    """
    HYPOTHESIS TEST: does algorithm A get higher CORRELATION COEFFICIENTS
    (how confident the algorithm was) than algorithm B? Runs a t-test on the
    'correlation' column, comparing two named algorithms.

    Null hypothesis (H0): the two algorithms have the same mean correlation.

    Parameters
    ----------
    results : pd.DataFrame
        The `results` table from compare_keyfinding_corpus() /
        test_custom_key_algorithm() — needs 'tune_id', 'algorithm',
        'correlation' columns. ground_truth is NOT required for this test.
    algorithm_a, algorithm_b : str
        Two of the labels appearing in results['algorithm'].
    paired : bool
        If True (default), runs a PAIRED t-test (scipy.stats.ttest_rel) —
        the correct choice here, since both algorithms were run on the SAME
        pieces. Set False for an independent-samples t-test
        (scipy.stats.ttest_ind) only if you've filtered to different,
        non-overlapping pieces per algorithm.
    plot : bool
        If True, show a bar chart of the two means with error bars (±1 SD).
    figsize : tuple
    title : str, optional

    Returns
    -------
    t : float — t-statistic
    p : float — p-value
    mean_a, mean_b : float — mean correlation for each algorithm

    Example
    -------
        t, p, mean_a, mean_b = ttest_algorithm_correlations(
            results, 'Krumhansl-Schmuckler', 'Albrecht-Shanahan')
    """
    a = results[results['algorithm'] == algorithm_a]
    b = results[results['algorithm'] == algorithm_b]
    if a.empty or b.empty:
        raise ValueError(
            f"Couldn't find both algorithms in results['algorithm']. "
            f"Available: {sorted(results['algorithm'].unique())}")

    if paired:
        merged = a[['tune_id', 'correlation']].merge(
            b[['tune_id', 'correlation']], on='tune_id', suffixes=('_a', '_b'))
        if merged.empty:
            raise ValueError(
                'No shared tune_id values between the two algorithms — use '
                'paired=False for an independent-samples test instead.')
        vals_a, vals_b = merged['correlation_a'], merged['correlation_b']
        t, p = stats.ttest_rel(vals_a, vals_b)
    else:
        vals_a, vals_b = a['correlation'], b['correlation']
        t, p = stats.ttest_ind(vals_a, vals_b)

    mean_a, mean_b = vals_a.mean(), vals_b.mean()
    test_name = 'Paired' if paired else 'Independent-samples'
    print(f'{test_name} t-test: {algorithm_a} (mean={mean_a:.3f}) vs. '
          f'{algorithm_b} (mean={mean_b:.3f})')
    print(f'  t = {t:.3f}, p = {p:.4f}')
    if p < 0.05:
        print('  -> p < 0.05: the two algorithms differ significantly.')
    else:
        print('  -> p >= 0.05: no significant difference detected.')

    if plot:
        plt.figure(figsize=figsize)
        plt.bar([algorithm_a, algorithm_b], [mean_a, mean_b],
                yerr=[vals_a.std(), vals_b.std()],
                color=['steelblue', 'coral'], edgecolor='white', capsize=6)
        plt.ylabel('Mean correlation coefficient')
        plt.title(title or f'{test_name} t-test: t={t:.2f}, p={p:.4f}')
        plt.xticks(rotation=15, ha='right')
        plt.tight_layout()
        plt.show()

    return t, p, mean_a, mean_b


def compare_algorithms_anova(results, value='correlation', algorithms=None,
                              method='anova', plot=True, figsize=(9, 5), title=None):
    """
    HYPOTHESIS TEST + PLOT: do key-finding algorithms differ OVERALL (not
    just pairwise) in their correlation coefficients? Runs a one-way ANOVA
    (or, for skewed/non-normal data, a Kruskal-Wallis test) across every
    algorithm present in `results`, and draws a box-and-whiskers plot
    showing each algorithm's full distribution side by side — median,
    interquartile range, and outliers all at a glance.

    Null hypothesis (H0): all algorithms have the same mean (ANOVA) / same
    distribution (Kruskal-Wallis) of `value`.

    Parameters
    ----------
    results : pd.DataFrame
        The `results` table from compare_keyfinding_corpus() /
        test_custom_key_algorithm() — needs an 'algorithm' column and a
        numeric `value` column.
    value : str
        Which numeric column to test/plot. 'correlation' by default. (To
        test accuracy instead, first cast a correctness column to int, e.g.
        results['hit'] = results['both_correct'].astype(int), then pass
        value='hit'.)
    algorithms : list of str, optional
        Restrict the test/plot to just these algorithm labels (default: all
        algorithms present in `results`).
    method : 'anova' or 'kruskal'
        'anova' (default): one-way ANOVA (scipy.stats.f_oneway) — assumes
        roughly normally-distributed values in each group.
        'kruskal': Kruskal-Wallis (scipy.stats.kruskal) — a non-parametric
        alternative that doesn't assume normality; safer with small samples
        or skewed correlation values.
    plot : bool
        If True, show the box-and-whiskers plot.
    figsize : tuple
    title : str, optional

    Returns
    -------
    stat : float — the F-statistic (ANOVA) or H-statistic (Kruskal-Wallis)
    p : float — p-value

    Example
    -------
        stat, p = compare_algorithms_anova(results)
        stat, p = compare_algorithms_anova(results, method='kruskal')
    """
    algos = algorithms or sorted(results['algorithm'].unique())
    groups = [results.loc[results['algorithm'] == a, value].dropna() for a in algos]
    keep = [(a, g) for a, g in zip(algos, groups) if len(g) > 0]
    if len(keep) < 2:
        raise ValueError('Need at least 2 algorithms with data to compare.')
    algos, groups = zip(*keep)

    if method == 'anova':
        stat, p = stats.f_oneway(*groups)
        test_label = 'One-way ANOVA'
    elif method == 'kruskal':
        stat, p = stats.kruskal(*groups)
        test_label = 'Kruskal-Wallis'
    else:
        raise ValueError("method must be 'anova' or 'kruskal'")

    print(f"{test_label} on '{value}' across {len(algos)} algorithm(s):")
    print(f'  statistic = {stat:.3f}, p = {p:.4f}')
    if p < 0.05:
        print('  -> p < 0.05: at least one algorithm differs significantly from the rest.')
    else:
        print('  -> p >= 0.05: no significant overall difference detected.')

    if plot:
        plt.figure(figsize=figsize)
        plot_df = results[results['algorithm'].isin(algos)]
        sns.boxplot(data=plot_df, x='algorithm', y=value, order=list(algos),
                    color='steelblue')
        plt.title(title or f'{test_label}: {value} by algorithm '
                            f'(stat={stat:.2f}, p={p:.4f})')
        plt.xlabel('Algorithm')
        plt.ylabel(value.replace('_', ' ').title())
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        plt.show()

    return stat, p
