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
                           pitch histograms (describe_piece, describe_corpus);
                           also download_corpus() for grabbing a corpus that
                           lives in its own (non-course) GitHub repo
    utils/ngrams.py      — Day 2: bigrams, trigrams, transition matrices,
                           scale-degree patterns (ngram_table, scale_degree_ngram_table)
    utils/keyfinding.py — Day 3: comparing key-finding algorithms, scoring
                           them against ground-truth keys (compare_keyfinding_algorithms,
                           compare_keyfinding_corpus)
    utils/information_theory.py — Day 4: entropy, predictability, and shared
                           information (pitch_entropy, conditional_entropy,
                           compare_corpus_entropy, pitch_duration_mutual_information);
                           also hartley_information(), compare_entropy_representations(),
                           corpus_entropy_profile(), compare_corpus_conditional_entropy(),
                           date_from_kern_headers(), and entropy_over_time() for
                           corpus- and history-scale entropy questions
    utils/tfidf.py        — Day 4: TF-IDF distinctiveness for melodic n-grams and
                           harmonic progressions (distinctive_ngrams, tf_idf_ngrams,
                           tf_idf_chord_progressions, plot_tfidf_heatmap)
    utils/similarity.py — Day 4: melodic/corpus similarity, four ways —
                           set overlap (jaccard, tversky_index), edit
                           distance (melodic_edit_distance), spatial distance
                           over feature vectors (feature_matrix,
                           spatial_similarity_matrix), and a simplified
                           structural alignment (structural_alignment);
                           similarity_matrices() builds edit/jaccard/contour
                           distance tables for a whole tune list in one call,
                           compare_tunes() inspects a single pair from it, and
                           find_transitivity_violation() searches a corpus
                           for the worst A~B, B~C, but not-A~C triple
    utils/recommender.py — Day 4: recommenders built on the similarity work —
                           item-item (recommend_similar) and user-user via
                           composer style profiles (build_composer_profiles,
                           composer_similarity_matrix, user_user_recommend)
    utils/idyom.py       — Day 5: IDyOM-style long-term/short-term predictive
                           models and information content (surprise_contour,
                           train_ltm_model, corpus_information_content)

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
    download_corpus,
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
    pitch_class_sequence,
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

# ── Day 4: information theory (entropy, KL divergence, mutual information) ───
from .information_theory import (
    shannon_entropy,
    pitch_entropy,
    conditional_entropy,
    kl_divergence,
    compare_corpus_entropy,
    mutual_information,
    pitch_duration_mutual_information,
    hartley_information,
    compare_entropy_representations,
    corpus_entropy_profile,
    compare_corpus_conditional_entropy,
    date_from_kern_headers,
    entropy_over_time,
)

# ── Day 4: TF-IDF distinctiveness for n-grams and chord progressions ────────
from .tfidf import (
    distinctive_ngrams,
    tf_idf_ngrams,
    tf_idf_chord_progressions,
    plot_tfidf_heatmap,
)

# ── Day 4: similarity (Jaccard, edit distance, Tversky index) ────────────────
from .similarity import (
    jaccard,
    jaccard_matrix,
    edit_distance,
    normalized_edit_distance,
    melodic_edit_distance,
    tversky_index,
    tversky_matrix,
    contour_similarity,
    ngram_similarity,
    similarity_matrices,
    melodic_feature_vector,
    feature_matrix,
    spatial_similarity,
    spatial_similarity_matrix,
    find_transitivity_violation,
    structural_alignment,
    compare_tunes,
)

# ── Day 4: recommenders (item-item via the similarity matrices; user-user
#           via composer style profiles) ─────────────────────────────────────
from .recommender import (
    recommend_similar,
    build_composer_profiles,
    composer_similarity_matrix,
    user_user_recommend,
    recommender_widget,
)

# ── Day 5: IDyOM-style long-term/short-term predictive models ────────────────
from .idyom import (
    NGramModel,
    information_content,
    stm_information_content,
    train_ltm_model,
    ltm_information_content,
    combine_ltm_stm,
    surprise_contour,
    corpus_information_content,
)

__all__ = [
    'setup_colab',
    # corpus.py
    'download_corpus', 'load_piece', 'note_table', 'pitch_histogram', 'describe_piece',
    'import_corpus', 'describe_corpus', 'load_corpus', 'PITCH_CLASS_NAMES',
    # ngrams.py
    'get_ngrams', 'note_sequence', 'pitch_class_sequence', 'most_common_ngrams',
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
    # information_theory.py
    'shannon_entropy', 'pitch_entropy', 'conditional_entropy', 'kl_divergence',
    'compare_corpus_entropy', 'mutual_information', 'pitch_duration_mutual_information',
    'hartley_information', 'compare_entropy_representations', 'corpus_entropy_profile',
    'compare_corpus_conditional_entropy', 'date_from_kern_headers', 'entropy_over_time',
    # tfidf.py
    'distinctive_ngrams', 'tf_idf_ngrams', 'tf_idf_chord_progressions', 'plot_tfidf_heatmap',
    # similarity.py
    'jaccard', 'jaccard_matrix', 'edit_distance', 'normalized_edit_distance',
    'melodic_edit_distance', 'tversky_index', 'tversky_matrix',
    'contour_similarity', 'ngram_similarity', 'similarity_matrices',
    'melodic_feature_vector', 'feature_matrix', 'spatial_similarity',
    'spatial_similarity_matrix', 'find_transitivity_violation',
    'structural_alignment', 'compare_tunes',
    # recommender.py
    'recommend_similar', 'build_composer_profiles', 'composer_similarity_matrix',
    'user_user_recommend', 'recommender_widget',
    # idyom.py
    'NGramModel', 'information_content', 'stm_information_content',
    'train_ltm_model', 'ltm_information_content', 'combine_ltm_stm',
    'surprise_contour', 'corpus_information_content',
]
