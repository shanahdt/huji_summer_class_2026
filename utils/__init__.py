"""
utils — Shared functions for Corpus Studies in Music
Summer Institute 2026 · Hebrew University of Jerusalem

Import at the top of any notebook (same as before — this is now a folder
of files instead of one big utils.py, but the import line doesn't change):

    import sys; sys.path.append('..')
    from utils import describe_piece, ngram_table, compare_keyfinding_algorithms
    # etc.

Where to find things
---------------------
    utils/corpus.py     — Day 1: importing a piece or a corpus, note tables,
                           pitch histograms (describe_piece, describe_corpus)
    utils/ngrams.py      — Day 2: bigrams, trigrams, transition matrices,
                           scale-degree patterns (ngram_table, scale_degree_ngram_table)
    utils/keyfinding.py — Day 3: comparing key-finding algorithms, scoring
                           them against ground-truth keys (compare_keyfinding_algorithms,
                           compare_keyfinding_corpus)
    utils/similarity.py — Jaccard similarity between corpora

Every "one-stop" function imports, processes, and plots in a single call —
look for functions named describe_*, *_table, or compare_* to start.
"""

import os
import subprocess

# ── Environment setup ─────────────────────────────────────────────────────

def setup_colab(repo_url='https://github.com/shanahdt/huji_summer_class_2026.git'):
    """
    Clone the course repo and set the working directory when running in Colab.
    Safe to call locally too — does nothing if ../data already exists.

    Usage (first cell of every notebook):
        from utils import setup_colab
        setup_colab()
    """
    repo_name = repo_url.rstrip('/').split('/')[-1].replace('.git', '')
    if not os.path.exists('../data'):
        colab_path = f'/content/{repo_name}'
        if not os.path.exists(colab_path):
            subprocess.run(['git', 'clone', repo_url], check=True)
        os.chdir(f'{colab_path}/notebooks')
        print('Repository cloned and working directory set.')
    else:
        print('Data directory found — running locally, no clone needed.')


# ── Day 1: importing pieces and corpora ──────────────────────────────────────
from .corpus import (
    load_piece,
    note_table,
    pitch_histogram,
    describe_piece,
    import_corpus,
    describe_corpus,
    load_corpus,
    PITCH_CLASS_NAMES,
)

# ── Day 2: n-grams and transition matrices ───────────────────────────────────
from .ngrams import (
    get_ngrams,
    note_sequence,
    most_common_ngrams,
    create_transition_matrix,
    plot_transition_matrix,
    ngram_table,
    scale_degree_sequence,
    extract_scale_degree_bigrams,
    scale_degree_ngram_table,
    bigram_table,
    compare_two_corpora_bigrams,
    interval_label,
    load_interval_corpus,
    DEGREE_LABELS,
)

# ── Day 3: key-finding algorithm comparison ──────────────────────────────────
from .keyfinding import (
    DEFAULT_ALGORITHMS,
    AlbrechtShanahan,
    compare_keyfinding_algorithms,
    compare_keyfinding_corpus,
    parse_kern_key_token,
    load_essen_keys,
    load_chorale_keys,
    load_keys_from_kern,
    load_keys_from_title,
    bach_chorale_key_table,
    get_key_profile,
    make_key_algorithm,
    test_custom_key_algorithm,
    train_key_profile,
    train_and_test_key_algorithm,
    keyscape,
    compare_keyscapes,
    chi_square_accuracy,
    ttest_algorithm_correlations,
    compare_algorithms_anova,
)

# ── Similarity ────────────────────────────────────────────────────────────────
from .similarity import jaccard, jaccard_matrix

__all__ = [
    'setup_colab',
    # corpus.py
    'load_piece', 'note_table', 'pitch_histogram', 'describe_piece',
    'import_corpus', 'describe_corpus', 'load_corpus', 'PITCH_CLASS_NAMES',
    # ngrams.py
    'get_ngrams', 'note_sequence', 'most_common_ngrams',
    'create_transition_matrix', 'plot_transition_matrix', 'ngram_table',
    'scale_degree_sequence', 'extract_scale_degree_bigrams',
    'scale_degree_ngram_table', 'bigram_table', 'compare_two_corpora_bigrams',
    'interval_label', 'load_interval_corpus', 'DEGREE_LABELS',
    # keyfinding.py
    'DEFAULT_ALGORITHMS', 'AlbrechtShanahan', 'compare_keyfinding_algorithms',
    'compare_keyfinding_corpus', 'parse_kern_key_token', 'load_essen_keys',
    'load_chorale_keys', 'load_keys_from_kern', 'load_keys_from_title',
    'bach_chorale_key_table', 'get_key_profile',
    'make_key_algorithm', 'test_custom_key_algorithm',
    'train_key_profile', 'train_and_test_key_algorithm',
    'keyscape', 'compare_keyscapes',
    'chi_square_accuracy', 'ttest_algorithm_correlations',
    'compare_algorithms_anova',
    # similarity.py
    'jaccard', 'jaccard_matrix',
]
