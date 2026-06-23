"""
utils/corpus.py — Importing pieces and corpora
Summer Institute 2026 · Hebrew University of Jerusalem

This module answers the Day 1 question: "I have a file (or a folder of files) —
how do I get it into Python, see a table of its notes, and look at a pitch
histogram?"

Every "one-stop" function here does three things for you in a single call:
    1. IMPORT   — parse the file(s) with music21
    2. PROCESS  — build a clean table (a pandas DataFrame) of the notes
    3. OUTPUT   — show you the table and/or plot a pitch histogram

Beginner usage
---------------
    from utils import describe_piece
    notes_df, counts = describe_piece('../data/happy_birthday.krn')

    from utils import describe_corpus
    tunes_df, streams, counts = describe_corpus('../data/Essen/England')
"""

from glob import glob
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from music21 import converter, interval, note

# 12 pitch classes in the order music21 numbers them (C = 0, C#/Db = 1, ...).
PITCH_CLASS_NAMES = ['C', 'C#', 'D', 'Eb', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']


# ── Loading a single piece ───────────────────────────────────────────────────

def load_piece(file_path):
    """
    Parse one file (kern, MusicXML, MIDI, ...) into a music21 Score.

    This is the simplest possible "import" step — most of the other
    functions in this module call load_piece() for you, so you usually
    don't need to call it yourself.

    Example
    -------
        score = load_piece('../data/happy_birthday.krn')
    """
    return converter.parse(str(file_path))


def _as_score(file_path_or_score):
    """Internal helper: accept either a file path (str/Path) or an
    already-parsed music21 Score, and always return a Score."""
    if isinstance(file_path_or_score, (str, Path)):
        return load_piece(file_path_or_score)
    return file_path_or_score


def note_table(file_path_or_score):
    """
    Build a beginner-friendly table of every note in a piece.

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
        A path to a file, or a Score you already parsed with load_piece().

    Returns
    -------
    pd.DataFrame with one row per note, columns:
        position       — note's position in the piece (0, 1, 2, ...)
        offset_beats   — where the note starts, in quarter notes
        pitch           — pitch name with octave, e.g. 'D4'
        pitch_class    — 0-11 (C=0, C#=1, ... B=11)
        pitch_class_name — e.g. 'D'
        octave         — e.g. 4
        midi           — MIDI note number, e.g. 62
        duration_ql    — duration in quarter notes

    Chords are expanded so every pitch inside a chord gets its own row.

    Example
    -------
        df = note_table('../data/happy_birthday.krn')
        df.head()
    """
    score = _as_score(file_path_or_score)

    rows = []
    position = 0
    for element in score.recurse().notes:
        pitches = element.pitches if element.isChord else [element.pitch]
        for p in pitches:
            rows.append({
                'position': position,
                'offset_beats': float(element.offset),
                'pitch': p.nameWithOctave,
                'pitch_class': int(p.pitchClass),
                'pitch_class_name': PITCH_CLASS_NAMES[p.pitchClass],
                'octave': p.octave,
                'midi': int(p.midi),
                'duration_ql': float(element.duration.quarterLength),
            })
            position += 1

    return pd.DataFrame(rows)


def pitch_histogram(file_path_or_score, by='pitch_class', plot=True,
                     title=None, color='steelblue'):
    """
    Count how often each pitch (or pitch class) appears in a piece, and
    optionally plot it as a bar chart.

    Parameters
    ----------
    file_path_or_score : str, Path, or music21 Score
    by : 'pitch_class' or 'pitch'
        'pitch_class' folds octaves together (C3 and C4 both count as 'C').
        'pitch' keeps octaves separate (C3 and C4 are different bars).
    plot : bool
        If True, show a bar chart.
    title : str, optional
        Custom plot title.
    color : str
        Bar color.

    Returns
    -------
    pd.Series of counts, indexed by pitch class name (or pitch name),
    sorted in a musically sensible order.

    Example
    -------
        counts = pitch_histogram('../data/happy_birthday.krn')
    """
    df = note_table(file_path_or_score)
    if df.empty:
        print('No notes found.')
        return pd.Series(dtype=int)

    if by == 'pitch_class':
        counts = df['pitch_class_name'].value_counts()
        counts = counts.reindex(PITCH_CLASS_NAMES).fillna(0).astype(int)
        xlabel = 'Pitch class'
    elif by == 'pitch':
        counts = df['pitch'].value_counts()
        # sort by MIDI number so the x-axis reads low-to-high
        order = (df[['pitch', 'midi']].drop_duplicates()
                 .sort_values('midi')['pitch'].tolist())
        counts = counts.reindex(order).fillna(0).astype(int)
        xlabel = 'Pitch'
    else:
        raise ValueError("by must be 'pitch_class' or 'pitch'")

    if plot:
        plt.figure(figsize=(9, 4))
        counts.plot(kind='bar', color=color, edgecolor='white')
        plt.title(title or f'Pitch histogram ({xlabel.lower()})')
        plt.xlabel(xlabel)
        plt.ylabel('Count')
        plt.xticks(rotation=45 if by == 'pitch' else 0, ha='right' if by == 'pitch' else 'center')
        plt.tight_layout()
        plt.show()

    return counts


def describe_piece(file_path, by='pitch_class', plot=True):
    """
    ONE-STOP function for a single piece: import it, build a note table,
    and plot a pitch histogram — all in one call.

    Parameters
    ----------
    file_path : str or Path
        Path to a kern/MusicXML/MIDI file.
    by : 'pitch_class' or 'pitch'
        See pitch_histogram().
    plot : bool
        If True, show the histogram.

    Returns
    -------
    notes_df : pd.DataFrame — one row per note (see note_table())
    counts   : pd.Series    — pitch (class) counts (see pitch_histogram())

    Example
    -------
        notes_df, counts = describe_piece('../data/happy_birthday.krn')
        print(notes_df.head())
        print(counts)
    """
    score = load_piece(file_path)
    notes_df = note_table(score)
    name = Path(file_path).name
    counts = pitch_histogram(score, by=by, plot=plot,
                              title=f'Pitch histogram: {name}')
    print(f'{name}: {len(notes_df)} notes, range '
          f'{notes_df["pitch"].iloc[0] if len(notes_df) else "—"} ... '
          f'(see notes_df for the full table)')
    return notes_df, counts


# ── Loading a corpus (a folder of files) ─────────────────────────────────────

def import_corpus(folder_path, pattern='*.krn', verbose=True):
    """
    Parse every matching file in a folder into music21 Scores.

    Parameters
    ----------
    folder_path : str or Path
        Folder containing the files (e.g. '../data/Essen/England').
    pattern : str
        Glob pattern for filenames (default '*.krn'; use '*.xml', '*.mid', etc.
        for other formats).
    verbose : bool
        Print progress and a final count.

    Returns
    -------
    streams : dict — {tune_id: music21 Score}, tune_id is the filename
              without extension.
    skipped : list — [(file_path, error_message), ...] for files that
              failed to parse.

    Example
    -------
        streams, skipped = import_corpus('../data/Essen/England')
    """
    files = sorted(Path(folder_path).glob(pattern))
    streams, skipped = {}, []

    for i, f in enumerate(files):
        if verbose and i % 50 == 0:
            print(f'  Loading {i + 1}/{len(files)}...')
        try:
            streams[f.stem] = converter.parse(str(f))
        except Exception as e:
            skipped.append((str(f), str(e)))

    if verbose:
        print(f'Loaded {len(streams)} piece(s) from {folder_path}.')
        if skipped:
            print(f'Skipped {len(skipped)} unreadable file(s).')

    return streams, skipped


def describe_corpus(folder_path, pattern='*.krn', by='pitch_class',
                     plot=True, verbose=True):
    """
    ONE-STOP function for a folder of pieces: import every file, build a
    per-tune summary table, and plot a pitch histogram aggregated across
    the whole corpus — all in one call.

    Parameters
    ----------
    folder_path : str or Path
        Folder containing the files, e.g. '../data/Essen/England'.
    pattern : str
        Glob pattern for filenames (default '*.krn').
    by : 'pitch_class' or 'pitch'
        See pitch_histogram().
    plot : bool
        If True, show the aggregated histogram.
    verbose : bool
        Print loading progress.

    Returns
    -------
    tunes_df : pd.DataFrame
        One row per tune. Columns: tune_id, n_notes, pitches,
        pitch_classes (list of 0-11 ints), intervals (list of semitones).
    streams : dict — {tune_id: music21 Score}
    counts : pd.Series — pitch (class) counts aggregated over the corpus

    Example
    -------
        tunes_df, streams, counts = describe_corpus('../data/Essen/England')
        tunes_df.sort_values('n_notes', ascending=False).head()
    """
    streams, skipped = import_corpus(folder_path, pattern=pattern, verbose=verbose)

    records = []
    all_pitch_classes = []
    for tune_id, score in streams.items():
        notes = [n for n in score.flatten().notes if isinstance(n, note.Note)]
        pcs = [n.pitch.pitchClass for n in notes]
        all_pitch_classes.extend(pcs)
        records.append({
            'tune_id': tune_id,
            'n_notes': len(notes),
            'pitches': [n.nameWithOctave for n in notes],
            'pitch_classes': pcs,
            'intervals': [interval.Interval(notes[j], notes[j + 1]).semitones
                          for j in range(len(notes) - 1)],
        })

    tunes_df = pd.DataFrame(records)

    pc_counter = pd.Series(all_pitch_classes).value_counts()
    counts = pc_counter.reindex(range(12)).fillna(0).astype(int)
    counts.index = PITCH_CLASS_NAMES

    if by == 'pitch':
        # rebuild using full pitch names instead of pitch classes
        all_pitches = [p for row in tunes_df['pitches'] for p in row]
        counts = pd.Series(all_pitches).value_counts().sort_index()

    if plot and not tunes_df.empty:
        plt.figure(figsize=(9, 4))
        counts.plot(kind='bar', color='coral', edgecolor='white')
        plt.title(f'Aggregated pitch histogram: {folder_path} '
                  f'({len(tunes_df)} pieces)')
        plt.xlabel('Pitch class' if by == 'pitch_class' else 'Pitch')
        plt.ylabel('Count')
        plt.xticks(rotation=0 if by == 'pitch_class' else 45,
                   ha='center' if by == 'pitch_class' else 'right')
        plt.tight_layout()
        plt.show()

    return tunes_df, streams, counts


# ── Backward-compatible loader (Beregovski klezmer corpus) ──────────────────

def load_corpus(kern_dir='../data/beregovski_corpus/kern', verbose=True):
    """
    Load the Beregovski klezmer corpus from kern files.

    Kept for backward compatibility with earlier notebooks. For a generic
    corpus folder, prefer describe_corpus() or import_corpus() above.

    Returns
    -------
    df : pd.DataFrame
        One row per tune. Columns: tune_id, n_notes, pitches,
        pitch_classes, scale_degrees, intervals.
    streams : dict
        {tune_id: music21.stream.Score}

    Example
    -------
        df, streams = load_corpus()
        meta = pd.read_csv('https://raw.githubusercontent.com/shanahdt/'
                           'mode_in_klezmer/main/metadata.csv')
        df = df.merge(meta, on='tune_id', how='left')
    """
    # Map pitch class to scale degree relative to G (all tunes notated in G)
    pc_to_degree = {7: 1, 9: 2, 11: 3, 0: 4, 2: 5, 4: 6, 6: 7,
                    8: 2, 10: 3, 1: 4, 3: 5, 5: 6}

    kern_files = sorted(Path(kern_dir).glob('*.krn'))
    records, streams = {}, {}

    for i, f in enumerate(kern_files):
        if verbose and i % 50 == 0:
            print(f'  Loading {i + 1}/{len(kern_files)}...')
        try:
            score = converter.parse(str(f))
            notes = [n for n in score.flatten().notes if isinstance(n, note.Note)]
            pcs = [n.pitch.pitchClass for n in notes]
            records[f.stem] = {
                'tune_id': f.stem,
                'n_notes': len(notes),
                'pitches': [n.nameWithOctave for n in notes],
                'pitch_classes': pcs,
                'scale_degrees': [pc_to_degree.get(pc, 0) for pc in pcs],
                'intervals': [
                    interval.Interval(notes[j], notes[j + 1]).semitones
                    for j in range(len(notes) - 1)
                ],
            }
            streams[f.stem] = score
        except Exception as e:
            if verbose:
                print(f'  Skipped {f.stem}: {e}')

    if verbose:
        print(f'Loaded {len(records)} tunes.')

    return pd.DataFrame(records.values()), streams
