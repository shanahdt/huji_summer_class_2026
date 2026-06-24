"""
utils/recommender.py — Music recommenders, built on the Day 4 similarity work
Summer Institute 2026 · Hebrew University of Jerusalem

You already built pairwise similarity matrices (edit distance, Jaccard,
contour) for a set of tunes on Day 4. A recommender system is, underneath,
exactly that: a similarity matrix plus a rule for "show me the closest
ones." This module makes that connection explicit, then scales it up to a
classic distinction in real recommender systems:

    ITEM-ITEM   -> recommend_similar()
        "Which OTHER TUNES are most like this one?" Compares items using
        their own musical features (the matrices you already built). This
        is what Day 4 Parts 1-4 have been doing the whole time.

    USER-USER   -> build_composer_profiles() + composer_similarity_matrix()
                   + user_user_recommend()
        "Which OTHER LISTENER has similar taste to this one?" In a real
        system this comes from listening logs (who streamed what), not
        musical features. We don't have listening logs, so we use composer
        STYLE as a stand-in for "shared audience": if Bach and Composer X
        write similarly, a Bach fan plausibly enjoys Composer X too. This is
        a real assumption real systems make ("content-based" user
        profiles), not a trick -- but it's worth noticing it's a DIFFERENT
        THEORY of similarity than the item-item version, even though the
        underlying math (compare two vectors, rank by closeness) looks the
        same.

    recommender_widget() ties both together interactively: pick a tune and a
    metric from dropdowns, and watch the recommendation list change live --
    a hands-on way to feel how much the (usually invisible) metric choice
    matters.

Beginner usage
---------------
    from utils import recommend_similar
    recommend_similar(edit_mat, tids, tids[0], top_n=5)

    from utils import build_composer_profiles, composer_similarity_matrix, user_user_recommend
    profiles = build_composer_profiles({'Bach': '../data/humdrum_scores/Bach/Inventio',
                                         'Beethoven': '../data/humdrum_scores/Beethoven/Quartets.Str'})
    sim = composer_similarity_matrix(profiles, plot=True)
    user_user_recommend('Bach', sim)

    from utils import recommender_widget
    recommender_widget({'Edit distance': edit_mat, 'Jaccard': jac_mat}, tids)
"""

from collections import Counter

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from music21 import converter
from sklearn.metrics.pairwise import cosine_similarity

from .corpus import PITCH_CLASS_NAMES
from .ngrams import _gather_files


# ── Item-item: recommend using the similarity matrices you already built ────

def recommend_similar(matrix, tune_ids, query, top_n=5, verbose=False):
    """
    ITEM-ITEM recommender: given a precomputed pairwise DISTANCE matrix
    (0 = identical, bigger = more different -- e.g. the edit_mat, jac_mat,
    or con_mat you built earlier in this notebook), recommend the top_n
    tunes most similar to `query`.

    This is exactly what a "people who listened to X also listened to Y"
    item-item recommender does under the hood: rank everything else by
    closeness in a precomputed similarity/distance table, and show the
    closest few. You built the table by hand -- this just reads it.

    Parameters
    ----------
    matrix : 2D numpy array or pd.DataFrame
        A square DISTANCE matrix aligned with `tune_ids` (matrix[i, j] =
        distance between tune_ids[i] and tune_ids[j]).
    tune_ids : list of str
        Labels matching the rows/columns of `matrix`, in order.
    query : str
        The tune to find neighbours for. Must be in `tune_ids`.
    top_n : int
        How many recommendations to return (default 5).
    verbose : bool
        If True, print the recommendation table.

    Returns
    -------
    pd.DataFrame with columns: tune_id, distance (sorted closest-first).

    Example
    -------
        recommend_similar(edit_mat, tids, tids[0], top_n=5)
        recommend_similar(jac_mat, tids, tids[0], top_n=5, verbose=True)
    """
    if query not in tune_ids:
        raise ValueError(
            f"'{query}' not found in tune_ids. Available: {list(tune_ids)[:10]}..."
        )

    mat = matrix.values if isinstance(matrix, pd.DataFrame) else np.asarray(matrix)
    idx = tune_ids.index(query)
    distances = mat[idx].astype(float).copy()
    distances[idx] = np.inf  # never recommend the tune to itself

    order = np.argsort(distances)[:top_n]
    result = pd.DataFrame({
        'tune_id': [tune_ids[i] for i in order],
        'distance': [float(distances[i]) for i in order],
    })

    if verbose:
        print(f"Top {min(top_n, len(order))} matches for '{query}' "
              f"(lower distance = more similar):")
        print(result.to_string(index=False))

    return result


# ── User-user: build composer "taste profiles" and compare THOSE ───────────

def _composer_feature_counts(file_path, max_interval=12):
    """
    Internal helper: parse one file ONCE and return (pc_counter,
    interval_counter) -- a Counter of the 12 pitch classes and a Counter of
    melodic intervals (signed semitones between consecutive notes in score
    order, clipped to +/- max_interval).
    """
    score = converter.parse(str(file_path))
    midi_vals = []
    pc_counter = Counter()
    for element in score.recurse().notes:
        pitches = element.pitches if element.isChord else [element.pitch]
        for p in pitches:
            pc_counter[PITCH_CLASS_NAMES[p.pitchClass]] += 1
        midi_vals.append(int(pitches[0].midi))

    raw_intervals = [b - a for a, b in zip(midi_vals, midi_vals[1:])]
    clipped = [max(-max_interval, min(max_interval, i)) for i in raw_intervals]
    interval_counter = Counter(clipped)
    return pc_counter, interval_counter


def build_composer_profiles(composer_sources, pattern='*.krn', max_interval=12,
                             verbose=True, plot=False):
    """
    ONE-STOP: build a musical "style fingerprint" for each composer -- a
    normalized pitch-class histogram concatenated with a normalized
    melodic-interval histogram, averaged across every piece in that
    composer's corpus.

    This is the ITEM-FEATURE side of the item-item vs. user-user distinction
    described at the top of this module: we're describing what each
    composer's music actually sounds like, so that "similar style" can
    later stand in for "shared audience" in user_user_recommend().

    Parameters
    ----------
    composer_sources : dict
        {composer_name: folder_path_or_list_of_files}, e.g.
        {'Bach': '../data/humdrum_scores/Bach/Inventio',
         'Beethoven': '../data/humdrum_scores/Beethoven/Quartets.Str'}
    pattern : str
        Glob pattern used when a source is a folder (default '*.krn').
    max_interval : int
        Melodic intervals are clipped to [-max_interval, max_interval]
        semitones before binning (default 12, i.e. within an octave).
    verbose : bool
        If True (default), print progress every 25 files per composer, plus
        a short summary line per composer when done. If False, runs
        silently except for skip warnings (see below).
    plot : bool
        If True, plot each composer's pitch-class profile as a grouped bar
        chart. Default False -- the notebook controls when to visualize.

    Returns
    -------
    pd.DataFrame, one row per composer (index = composer name), columns
    'pc_C', 'pc_C#', ..., 'pc_B' (pitch-class proportions) and
    'int_-12', ..., 'int_+12' (interval proportions).

    Example
    -------
        profiles = build_composer_profiles({
            'Bach': '../data/humdrum_scores/Bach/Inventio',
            'Beethoven': '../data/humdrum_scores/Beethoven/Quartets.Str',
            'Chopin': '../data/humdrum_scores/Chopin/Mazurkas',
            'Mozart': '../data/humdrum_scores/Mozart/Quartets.Str',
        }, verbose=True)
    """
    rows = {}

    for composer, source in composer_sources.items():
        try:
            files = _gather_files(source, pattern)
        except Exception as e:
            print(f"{composer}: could not read source ({e}); skipping this composer.")
            continue

        if not files:
            print(f"{composer}: no files matching '{pattern}' found in {source}; "
                  f"skipping this composer.")
            continue

        pc_totals = Counter()
        interval_totals = Counter()
        skipped = []

        for i, f in enumerate(files):
            if verbose and i % 25 == 0:
                print(f'  {composer}: {i + 1}/{len(files)}...')
            try:
                pcs, ivls = _composer_feature_counts(f, max_interval=max_interval)
                pc_totals.update(pcs)
                interval_totals.update(ivls)
            except Exception as e:
                skipped.append((f, str(e)))

        if skipped:
            print(f'{composer}: skipped {len(skipped)} unreadable file(s).')

        used = len(files) - len(skipped)
        if used == 0:
            print(f'{composer}: no readable files -- skipping this composer.')
            continue
        if verbose:
            print(f'{composer}: {used} file(s) used, {sum(pc_totals.values())} notes.')

        pc_total = sum(pc_totals.values()) or 1
        int_total = sum(interval_totals.values()) or 1
        row = {f'pc_{name}': pc_totals.get(name, 0) / pc_total
               for name in PITCH_CLASS_NAMES}
        row.update({f'int_{i:+d}': interval_totals.get(i, 0) / int_total
                     for i in range(-max_interval, max_interval + 1)})
        rows[composer] = row

    if not rows:
        raise ValueError(
            'No composer profiles could be built -- check that composer_sources '
            'points at real folders/files.'
        )

    profiles = pd.DataFrame(rows).T

    if plot:
        pc_cols = [f'pc_{name}' for name in PITCH_CLASS_NAMES]
        ax = profiles[pc_cols].T.plot(kind='bar', figsize=(10, 4))
        ax.set_xticklabels(PITCH_CLASS_NAMES, rotation=0)
        ax.set_ylabel('Proportion of notes')
        ax.set_title('Pitch-class profile by composer')
        ax.legend(title='Composer')
        plt.tight_layout()
        plt.show()

    return profiles


def composer_similarity_matrix(profiles, metric='cosine', plot=False):
    """
    Compare composer style profiles (from build_composer_profiles()) to each
    other and return a SIMILARITY matrix (higher = more alike, unlike the
    DISTANCE matrices recommend_similar() expects).

    Parameters
    ----------
    profiles : pd.DataFrame
        Output of build_composer_profiles() -- one row per composer.
    metric : 'cosine' or 'correlation'
        'cosine' (default) compares the shape of the two profile vectors,
        ignoring overall scale. 'correlation' (Pearson) additionally
        centers each profile around its own mean first.
    plot : bool
        If True, show a heatmap. Default False -- the notebook controls
        when to visualize.

    Returns
    -------
    pd.DataFrame -- composer x composer similarity matrix, values in [0, 1]
    for cosine (roughly; can dip slightly negative for very dissimilar
    profiles) or [-1, 1] for correlation.

    Example
    -------
        sim = composer_similarity_matrix(profiles, plot=True)
    """
    if metric == 'cosine':
        values = cosine_similarity(profiles.values)
    elif metric == 'correlation':
        values = profiles.T.corr().values
    else:
        raise ValueError("metric must be 'cosine' or 'correlation'")

    matrix = pd.DataFrame(values, index=profiles.index, columns=profiles.index)

    if plot:
        plt.figure(figsize=(6, 5))
        sns.heatmap(matrix, annot=True, fmt='.2f', cmap='Blues')
        plt.title(f'Composer style similarity ({metric})')
        plt.tight_layout()
        plt.show()

    return matrix


def user_user_recommend(target, similarity_matrix, top_n=3, verbose=False):
    """
    USER-USER recommender: given a target "listener" (here, a composer
    standing in for a listener with that composer's taste), who else's
    music is most similar in overall style, per
    composer_similarity_matrix()?

    The metaphor: recommend_similar() compares individual TUNES (item-item).
    This compares whole LISTENERS -- here approximated by composer style --
    and asks which other listener has the most similar taste. "What would
    Bach listen to?" becomes "which composer's style profile is closest to
    Bach's?"

    Parameters
    ----------
    target : str
        A composer name present in `similarity_matrix`'s index.
    similarity_matrix : pd.DataFrame
        Output of composer_similarity_matrix().
    top_n : int
        How many other composers to return (default 3).
    verbose : bool
        If True, print a friendly summary.

    Returns
    -------
    pd.Series -- the top_n most similar composers, sorted descending,
    indexed by composer name, values = similarity score.

    Example
    -------
        sim = composer_similarity_matrix(profiles)
        user_user_recommend('Bach', sim, top_n=3, verbose=True)
    """
    if target not in similarity_matrix.index:
        raise ValueError(
            f"'{target}' not found. Available composers: "
            f"{list(similarity_matrix.index)}"
        )

    scores = similarity_matrix.loc[target].drop(target).sort_values(ascending=False)
    top = scores.head(top_n)

    if verbose:
        print(f"If '{target}' were a listener, based on overall style, "
              f"they'd most likely enjoy:")
        for name, score in top.items():
            print(f'  {name}: similarity = {score:.3f}')

    return top


# ── Live, interactive comparison of item-item recommenders ─────────────────

def recommender_widget(matrices, tune_ids, top_n=5):
    """
    Interactive ipywidgets explorer: pick a tune and a similarity metric
    from dropdowns, and watch the top_n recommended tunes update live. This
    is the most direct way to FEEL how much the (usually invisible) metric
    choice matters -- same tune, different metric, different answer.

    Parameters
    ----------
    matrices : dict
        {metric_name: distance_matrix}, e.g.
        {'Edit distance': edit_mat, 'Jaccard': jac_mat, 'Contour': con_mat}.
        Every matrix must be aligned with `tune_ids` (see recommend_similar()).
    tune_ids : list of str
        Labels matching the rows/columns of every matrix in `matrices`.
    top_n : int
        How many recommendations to show per update (default 5).

    Returns
    -------
    None (displays the widget directly; only works in a Jupyter front-end).

    Example
    -------
        recommender_widget({'Edit distance': edit_mat, 'Jaccard': jac_mat,
                             'Contour': con_mat}, tids)
    """
    try:
        import ipywidgets as widgets
        from IPython.display import display, clear_output
    except ImportError as e:
        raise ImportError(
            'recommender_widget() needs ipywidgets and a Jupyter front-end '
            f'to display anything (original error: {e}).'
        )

    if not matrices:
        raise ValueError('matrices must be a non-empty dict of {name: matrix}.')

    tune_dropdown = widgets.Dropdown(options=list(tune_ids), description='Tune:')
    metric_dropdown = widgets.Dropdown(options=list(matrices.keys()), description='Metric:')
    output = widgets.Output()

    def update(*_args):
        with output:
            clear_output(wait=True)
            try:
                result = recommend_similar(
                    matrices[metric_dropdown.value], list(tune_ids),
                    tune_dropdown.value, top_n=top_n,
                )
                display(result)
            except Exception as e:
                print(f'Could not compute recommendations: {e}')

    tune_dropdown.observe(update, names='value')
    metric_dropdown.observe(update, names='value')
    display(widgets.HBox([tune_dropdown, metric_dropdown]), output)
    update()
