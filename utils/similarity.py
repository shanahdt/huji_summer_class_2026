"""
utils/similarity.py — Comparing corpora with Jaccard similarity
Summer Institute 2026 · Hebrew University of Jerusalem
"""

from collections import Counter

import pandas as pd


def jaccard(counter1, counter2, top_n=50):
    """
    Compute Jaccard similarity between the top-N bigrams of two Counters.

    Jaccard = |intersection| / |union|

    Returns a float in [0, 1]. Identical top-N sets → 1.0; no overlap → 0.0.

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
