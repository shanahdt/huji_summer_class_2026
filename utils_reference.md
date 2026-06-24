# utils — Function Reference

Corpus Studies in Music, Summer Institute 2026 · Hebrew University of Jerusalem

Import any of these at the top of a notebook with `from utils import <name>`.

## Day 1 — `utils/corpus.py`: importing pieces and corpora

**`load_piece(file_path)`** — Parse one file (kern, MusicXML, MIDI, ...) into a music21 Score. Most other functions call this for you.
```python
score = load_piece('../data/happy_birthday.krn')
```

**`note_table(file_path_or_score)`** — Build a table with one row per note: position, offset in beats, pitch name, pitch class, octave, MIDI number, duration. Chords are expanded so each pitch gets its own row.
```python
df = note_table('../data/happy_birthday.krn')
df.head()
```

**`pitch_histogram(file_path_or_score, by='pitch_class', plot=True)`** — Count how often each pitch (or pitch class) appears, and plot a bar chart.
```python
counts = pitch_histogram('../data/happy_birthday.krn')
```

**`describe_piece(file_path, by='pitch_class', plot=True)`** — ONE-STOP: import a piece, build its note table, and plot a pitch histogram in a single call.
```python
notes_df, counts = describe_piece('../data/happy_birthday.krn')
```

**`import_corpus(folder_path, pattern='*.krn', verbose=True)`** — Parse every matching file in a folder into music21 Scores.
```python
streams, skipped = import_corpus('../data/Essen/England')
```

**`describe_corpus(folder_path, pattern='*.krn', by='pitch_class', plot=True)`** — ONE-STOP: import every file in a folder, build a per-tune summary table, and plot a pitch histogram aggregated over the whole corpus.
```python
tunes_df, streams, counts = describe_corpus('../data/Essen/England')
tunes_df.sort_values('n_notes', ascending=False).head()
```

**`load_corpus(kern_dir='../data/beregovski_corpus/kern')`** — Legacy loader for the Beregovski klezmer corpus (kept for backward compatibility with older notebooks). For any other folder, use `describe_corpus()` or `import_corpus()` instead.
```python
df, streams = load_corpus()
```

**`download_corpus(repo_url, subdir='kern', target_dir=None, pattern='*.krn')`** — Download one folder out of a GitHub repo that lives outside the course repo (e.g. a corpus a guest dataset is hosted in its own repo). Tries both `main` and `master` branches, skips the download if the files are already there, and raises a clear error if the expected subfolder isn't found. (For the course repo itself, use `setup_colab()` instead.)
```python
kern_dir = download_corpus('https://github.com/shanahdt/mode_in_klezmer')
```

---

## Day 2 — `utils/ngrams.py`: n-grams and transition matrices

**`get_ngrams(sequence, n)`** — Return all n-grams of a sequence as a list of tuples.
```python
get_ngrams([1, 2, 3, 4], 2)   # -> [(1, 2), (2, 3), (3, 4)]
```

**`note_sequence(file_path_or_score)`** — Return the list of note names (e.g. 'C4', 'D4') in a piece, in order. Chords are expanded.

**`pitch_class_sequence(file_path_or_score)`** — Like `note_sequence()`, but octave-folded pitch class names (e.g. 'C', 'C#'). Used internally by Day 4's entropy and edit-distance functions.

**`most_common_ngrams(kern_file_path, n=2)`** — Most common n-grams of note names in a single file.
```python
most_common_ngrams('../data/happy_birthday.krn', n=2)
```

**`create_transition_matrix(weighted_ngrams)`** — Build a nested-dict transition matrix from `most_common_ngrams()` output (bigrams only).

**`plot_transition_matrix(transition_matrix, as_percentages=False)`** — Plot a transition matrix as a heatmap.
```python
data = most_common_ngrams('../data/happy_birthday.krn', n=2)
matrix = create_transition_matrix(data)
plot_transition_matrix(matrix, as_percentages=True)
```

**`ngram_table(source, n=2, top_n=15, pattern='*.krn', plot=True)`** — ONE-STOP: import a file or a whole folder, count n-grams of note names, return a table + plot (heatmap for bigrams, bar chart otherwise).
```python
table, counter = ngram_table('../data/happy_birthday.krn', n=2)        # bigrams
table, counter = ngram_table('../data/charlie_parker', n=3, top_n=20)  # trigrams, whole folder
```

**`scale_degree_sequence(file_path_or_score)`** — Scale-degree label (e.g. '1', 'b3', '5') for every note, relative to the piece's own detected tonic — key-independent.

**`extract_scale_degree_bigrams(file_list, corpus_name='Corpus')`** — Scale-degree bigrams across a list of files.
```python
files = sorted(glob('../data/charlie_parker/*.krn'))
counter, skipped = extract_scale_degree_bigrams(files, 'Parker')
```

**`scale_degree_ngram_table(source, n=2, top_n=15, pattern='*.krn', plot=True)`** — ONE-STOP, key-relative counterpart to `ngram_table()`: notes become scale degrees first, so pieces in different keys compare directly.
```python
table, counter = scale_degree_ngram_table('../data/Essen/England', n=2)
```

**`bigram_table(counter, corpus_name, top_n=15)`** — Convert a bigram Counter into a readable DataFrame (Corpus, Bigram, Count, Percent).
```python
tbl = bigram_table(parker_counter, 'Parker', top_n=10)
```

**`compare_two_corpora_bigrams(left_files, right_files, left_name='Corpus A', right_name='Corpus B')`** — Scale-degree bigram heatmaps for two corpora, side by side.
```python
compare_two_corpora_bigrams(
    sorted(glob('../data/charlie_parker/*.krn')),
    sorted(glob('../data/dizzy_gillespie/*.krn')),
    left_name='Parker', right_name='Dizzy', value_type='percentages')
```

**`interval_label(semitones)`** — Human-readable label for a signed semitone interval.
```python
interval_label(7)    # -> 'up P5 (+7)'
interval_label(-2)   # -> 'down M2 (-2)'
```

**`load_interval_corpus(patterns)`** — Load multiple kern corpora and extract melodic interval sequences into one table.
```python
df = load_interval_corpus([
    ('English', '../data/Essen/England/*.krn'),
    ('Czech',   '../data/Essen/Czech/*.krn'),
])
```

---

## Day 3 — `utils/keyfinding.py`: key-finding algorithms

### Comparing algorithms

**`compare_keyfinding_algorithms(file_path_or_score, algorithms=None, plot=True)`** — ONE-STOP: run several key-finding algorithms on one piece, table + bar chart of what each decided.
```python
table = compare_keyfinding_algorithms('../data/happy_birthday.krn')
```

**`compare_keyfinding_corpus(source, pattern='*.krn', ground_truth=None, plot=True)`** — ONE-STOP: run several algorithms over every piece in a folder, optionally score against ground-truth keys (or, with none given, against majority vote), table + bar chart.
```python
ground_truth = load_essen_keys('../data/essen_keys.csv')
results, summary = compare_keyfinding_corpus('../data/Essen/England', ground_truth=ground_truth)
```

**`bach_chorale_key_table(chorale_dir=..., ground_truth_csv=..., algorithms=None)`** — ONE-STOP: every algorithm on every Bach chorale, one wide table (annotated key + each algorithm's guess).
```python
table = bach_chorale_key_table()
```

### Ground-truth key labels

**`parse_kern_key_token(token)`** — Parse a humdrum/kern key token into (tonic, mode), e.g. `'g'` → `('G', 'minor')`.

**`load_essen_keys(csv_path)`** — Ground-truth keys for the Essen folksong collection.
```python
ground_truth = load_essen_keys('../data/essen_keys.csv')
```

**`load_chorale_keys(csv_path)`** — Ground-truth keys for the Bach chorales.
```python
ground_truth = load_chorale_keys('../data/chorale_keys.csv')
```

### Build your own algorithm

**`get_key_profile(algorithm)`** — Extract a built-in algorithm's 12+12 major/minor weights as plain lists, so you can inspect or edit them.
```python
profile = get_key_profile('Krumhansl-Schmuckler')
my_major = profile['major'][:]
my_major[7] *= 1.5   # exaggerate the fifth
```

**`make_key_algorithm(major_weights, minor_weights, name='Custom')`** — Build a usable key-finding algorithm from your own 12+12 hard-coded weights.
```python
major = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
minor = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
MyAlgorithm = make_key_algorithm(major, minor, name='My Profile')
```

**`test_custom_key_algorithm(major_weights, minor_weights, source, ground_truth=None, compare_to_defaults=True)`** — ONE-STOP: build a custom algorithm from weights and test it on a corpus, optionally against the built-ins and/or ground truth.
```python
profile = get_key_profile('Aarden-Essen')
my_major = profile['major'][:]
my_major[7] *= 1.5
ground_truth = load_essen_keys('../data/essen_keys.csv')
results, summary = test_custom_key_algorithm(
    my_major, profile['minor'], '../data/Essen/England',
    name='Boosted Dominant', ground_truth=ground_truth)
```

### Train on one corpus, test on another

**`train_key_profile(source, ground_truth, pattern='*.krn')`** — Count how scale degrees actually appear across a corpus (or combination of corpora) of pieces with known keys, normalized into 12+12 major/minor weights.
```python
ground_truth = load_essen_keys('../data/essen_keys.csv')
profile = train_key_profile(['../data/Essen/Italia', '../data/Essen/Deutschl'], ground_truth)
```

**`train_and_test_key_algorithm(train_source, test_source, ground_truth, name='Trained', compare_to_defaults=True)`** — ONE-STOP: train weights on one corpus (or several combined), then test how well they generalize to a *different* corpus.
```python
ground_truth = load_essen_keys('../data/essen_keys.csv')
profile, results, summary = train_and_test_key_algorithm(
    train_source=['../data/Essen/Italia', '../data/Essen/Deutschl'],
    test_source='../data/Essen/Czech',
    ground_truth=ground_truth,
    name='Italian+German')
```

### Keyscapes (visualizing key over time and window size)

**`keyscape(file_path_or_score, algorithm='Krumhansl-Schmuckler', window_size=None)`** — ONE-STOP: triangular diagram of the detected key in every window, at every window size — bottom row = smallest/most local windows, top = whole piece. Pass `window_size` to lock to one span (in quarter notes/beats) and get a single strip instead of a triangle.
```python
colors, meta = keyscape('../data/happy_birthday.krn')
colors, meta = keyscape('../data/happy_birthday.krn', algorithm='Albrecht-Shanahan')
colors, meta = keyscape('../data/happy_birthday.krn', window_size=8)   # single strip
```

**`compare_keyscapes(file_path_or_score, algorithms=None, window_size=None)`** — ONE-STOP: keyscapes for several algorithms side by side, with one shared legend, so agreement/disagreement is easy to spot.
```python
compare_keyscapes('../data/happy_birthday.krn')                  # all 6 built-ins

from utils import DEFAULT_ALGORITHMS
compare_keyscapes('../data/happy_birthday.krn', algorithms={
    'Krumhansl-Schmuckler': DEFAULT_ALGORITHMS['Krumhansl-Schmuckler'],
    'Albrecht-Shanahan': DEFAULT_ALGORITHMS['Albrecht-Shanahan'],
})

compare_keyscapes('../data/happy_birthday.krn', window_size=8)   # fixed 8-beat window
```

### Ground truth from kern files (no separate CSV needed)

**`load_keys_from_kern(source, pattern='*.krn')`** — Ground-truth keys mined straight from the embedded `*G:`/`*a:` key token in kern files. Works well for Essen-style or chorale-style corpora that actually encode a key token.
```python
ground_truth = load_keys_from_kern('../data/my_corpus')
```

**`load_keys_from_title(source, pattern='*.krn')`** — Fallback ground-truth source: pulls the key out of the `!!!OTL:` title (e.g. "String Quartet ... in F Major" → F major). Use this when `load_keys_from_kern()` finds almost nothing — some corpora (e.g. the Beethoven quartets) carry only a key SIGNATURE, never a key token. Gives the work's *overall* announced key, not necessarily every movement's key.
```python
ground_truth = load_keys_from_title('../data/humdrum_scores/Beethoven')
```

### Testing hypotheses about algorithm performance

**`chi_square_accuracy(results, correct_col='both_correct')`** — HYPOTHESIS TEST: does accuracy (hits vs. misses) depend on which algorithm you use? Chi-square test of independence on a hits/misses contingency table, plus a stacked bar chart.
```python
ground_truth = load_essen_keys('../data/essen_keys.csv')
results, summary = compare_keyfinding_corpus('../data/Essen/Italia', ground_truth=ground_truth)
table, chi2, p, dof = chi_square_accuracy(results)
```

**`ttest_algorithm_correlations(results, algorithm_a, algorithm_b, paired=True)`** — HYPOTHESIS TEST: does algorithm A get higher correlation coefficients than algorithm B? Paired t-test (same pieces, both algorithms) by default, plus a bar chart of the two means.
```python
t, p, mean_a, mean_b = ttest_algorithm_correlations(
    results, 'Krumhansl-Schmuckler', 'Albrecht-Shanahan')
```

**`compare_algorithms_anova(results, value='correlation', method='anova')`** — HYPOTHESIS TEST + PLOT: do algorithms differ overall (not just pairwise)? One-way ANOVA (or `method='kruskal'` for non-parametric data) across every algorithm in `results`, plus a box-and-whiskers plot of the full distributions.
```python
stat, p = compare_algorithms_anova(results)
stat, p = compare_algorithms_anova(results, method='kruskal')
```

### Other

**`DEFAULT_ALGORITHMS`** — dict of the 6 built-in algorithms (`{label: class}`): Krumhansl-Schmuckler, Aarden-Essen, Simple Weights, Bellman-Budge, Temperley-Kostka-Payne, Albrecht-Shanahan.

**`AlbrechtShanahan`** — a `KeyWeightKeyAnalysis` subclass with corpus-trained (rather than listener-judgment) weights.

---

## Day 4 — `utils/information_theory.py`: entropy, predictability, shared information

Smallest question to largest:

**`shannon_entropy(data, base=2)`** — CORE MEASURE: H = -Σ p_i log_b(p_i), in bits by default. 0 = totally predictable; higher = more uncertainty. Takes either raw observations or a ready-made distribution (counts/probabilities).
```python
shannon_entropy(['C', 'C', 'G', 'G', 'E'])
shannon_entropy({'C': 2, 'G': 2, 'E': 1})
```

**`pitch_entropy(file_path_or_score, by='pitch_class', plot=True)`** — ONE-STOP, Q1: how much pitch variety is in this piece? Builds the pitch histogram and reports its entropy.
```python
entropy, counts = pitch_entropy('../data/happy_birthday.krn')
```

**`conditional_entropy(file_path_or_score, n=2, by='pitch_class')`** — ONE-STOP, Q2: once you know the previous note(s), how much LESS uncertain is the next one? Reports H(note), H(note | context), and the information gain (bits the context removes) — a measure of melodic structure/predictability.
```python
result = conditional_entropy('../data/happy_birthday.krn', n=2)
print(result['information_gain'])
```

**`kl_divergence(p, q, base=2)`** — CORE MEASURE: D_KL(P‖Q), the extra bits needed to encode P using a code built for Q. 0 = identical distributions. NOT symmetric — D_KL(P‖Q) ≠ D_KL(Q‖P).
```python
d = kl_divergence(counts_a, counts_b)
```

**`compare_corpus_entropy(corpus_a, corpus_b, by='pitch_class', names=(...))`** — ONE-STOP, Q3: how differently do two corpora use pitch? Entropy of each corpus plus KL divergence in both directions, with a side-by-side bar chart.
```python
result = compare_corpus_entropy('../data/Essen/England', '../data/Essen/Italia',
                                 names=('English', 'Italian'))
```

**`mutual_information(seq_x, seq_y, base=2)`** — CORE MEASURE: I(X;Y) = H(X) + H(Y) - H(X,Y) — how much knowing X reduces uncertainty about Y. Symmetric (unlike conditional entropy/KL divergence). 0 = independent.
```python
mi = mutual_information(pitch_classes, duration_bins)
```

**`pitch_duration_mutual_information(file_path_or_score, duration_bins=None, plot=True)`** — ONE-STOP, Q4 (the biggest question here): within one piece, how much does pitch tell you about rhythm (and vice versa)? Heatmap of the joint pitch-class × duration-bin distribution.
```python
mi, joint = pitch_duration_mutual_information('../data/happy_birthday.krn')
```

---

## Day 4 — `utils/similarity.py`: comparing melodies and corpora

### Set overlap

**`jaccard(counter1, counter2, top_n=50)`** — Jaccard similarity (|intersection| / |union|) between the top-N bigrams of two Counters. 1.0 = identical top-N sets, 0.0 = no overlap. A special case of `tversky_index()` below (alpha=beta=1).
```python
j = jaccard(parker_counter, dizzy_counter, top_n=50)
print(f'Parker vs Dizzy: {j:.3f}')
```

**`jaccard_matrix(counters, top_n=50)`** — Pairwise Jaccard similarity matrix from a dict of Counters.
```python
counters = {'Parker': parker_counter, 'Dizzy': dizzy_counter, 'Freygish': freygish_counter}
df = jaccard_matrix(counters)
sns.heatmap(df, annot=True, fmt='.2f', cmap='Blues')
```

### Edit distance (cares about order, not just overlap)

**`edit_distance(seq_a, seq_b, substitution_cost=None)`** — Levenshtein distance between any two sequences (characters, note names, pitch classes, MIDI numbers...). Unlike Jaccard, this is sensitive to ORDER — `'CDE'` and `'EDC'` share every pitch but have a large edit distance. Pass your own `substitution_cost(a, b)` for a musically weighted version (e.g. cost ∝ semitone distance).
```python
edit_distance(['C', 'D', 'E', 'F'], ['C', 'D', 'G', 'F'])   # -> 1.0
```

**`normalized_edit_distance(seq_a, seq_b, substitution_cost=None)`** — `edit_distance()` scaled to [0, 1] by the longer sequence's length, so melodies of different lengths are comparable.
```python
d = normalized_edit_distance(seq_a, seq_b)
similarity = 1 - d
```

**`melodic_edit_distance(file_a, file_b, by='pitch_class', weighted=False, normalize=True)`** — ONE-STOP: edit distance between two PIECES. `by='scale_degree'` is key-independent. `weighted=True` charges less for substituting a nearby pitch than a distant one (max cost 1.0 for a tritone), instead of treating every mismatch the same.
```python
d = melodic_edit_distance('../data/tune1.krn', '../data/tune2.krn')
d = melodic_edit_distance('../data/tune1.krn', '../data/tune2.krn',
                           by='scale_degree', weighted=True)
```

### Comparing two individual pieces (instead of two whole corpora)

The functions above compare two CORPORA via bigram Counters. These compare two PIECES directly from file paths — the building blocks behind the pairwise matrices you build with `similarity_matrices()`.

**`contour_similarity(file_a, file_b)`** — fraction of note-to-note moves (up/down/same) that agree between two melodies. Always uses absolute pitch height, so it's about real melodic shape, not key.
```python
contour_similarity('../data/tune1.krn', '../data/tune2.krn')
```

**`ngram_similarity(file_a, file_b, n=3, by='scale_degree')`** — per-piece sibling of `jaccard()`: Jaccard similarity of n-gram sets between two individual pieces (built from `tversky_index(..., alpha=1, beta=1)`).
```python
ngram_similarity('../data/tune1.krn', '../data/tune2.krn', n=3)
```

**`similarity_matrices(files, metrics=('edit', 'jaccard', 'contour'), by='scale_degree', n=3, weighted=False, tune_ids=None, pattern='*.krn', verbose=False, plot=False)`** — ONE-STOP: build N x N DISTANCE matrices for a list of tunes, one or more metrics at once, parsing each file only once no matter how many metrics you ask for. `verbose=True` prints progress every 25 files; `plot=True` shows a heatmap per metric.
```python
matrices, tids = similarity_matrices(files_subset, plot=True, verbose=True)
edit_mat, jac_mat, con_mat = matrices['edit'], matrices['jaccard'], matrices['contour']
```

**`compare_tunes(tids, corpus_df, edit_mat, jac_mat, con_mat, a=0, b=1, show='scale_degrees')`** — Quick look at a single pair out of a `similarity_matrices()` result: prints each tune's opening sequence side by side, plus their edit/Jaccard/contour scores — handy for sanity-checking a heatmap cell or following up on a `disagreements`-style table. `a`/`b` can each be an index into `tids` (int) or a tune_id (str). `show` picks what to print per tune — `'scale_degrees'` (default), `'pitches'` (note names with octave), `'intervals'` (semitones), or `'all'` for all three; `corpus_df` needs a `tune_id` column plus whichever of those `show` asks for (e.g. from `load_corpus()`, which provides all three).
```python
matrices, tids = similarity_matrices(files_subset)
compare_tunes(tids, corpus_df, matrices['edit'], matrices['jaccard'], matrices['contour'])
compare_tunes(tids, corpus_df, matrices['edit'], matrices['jaccard'], matrices['contour'],
              a='czech01', b='czech03', show='pitches')
```

### Tversky index (a generalized, possibly asymmetric similarity)

**`tversky_index(set_a, set_b, alpha=0.5, beta=0.5)`** — Tversky's (1977) similarity index: `S(A,B) = |A∩B| / (|A∩B| + α|A−B| + β|B−A|)`. Generalizes Jaccard (α=β=1) and Dice's coefficient (α=β=0.5). With α≠β, similarity is ASYMMETRIC — `tversky_index(A,B) ≠ tversky_index(B,A)` — modeling Tversky's finding that human similarity judgment isn't symmetric (a sparse/skeletal set vs. a rich/prototypical one don't "resemble" each other equally in both directions).
```python
a, b = set(parker_counter.keys()), set(dizzy_counter.keys())
tversky_index(a, b)                       # Dice-like, symmetric
tversky_index(a, b, alpha=0.1, beta=0.9)  # asymmetric: penalize b's
                                           # distinctive features much more
```

**`tversky_matrix(counters, alpha=0.5, beta=0.5, top_n=50)`** — Pairwise Tversky matrix from a dict of Counters. Unless alpha == beta, this matrix is NOT symmetric — read each row as "how similar is the ROW corpus to the COLUMN corpus."
```python
df = tversky_matrix({'Parker': parker_counter, 'Dizzy': dizzy_counter}, alpha=0.2, beta=0.8)
sns.heatmap(df, annot=True, fmt='.2f', cmap='Blues')
```
**Gotcha:** `top_n` truncates BOTH corpora's Counters to the same size N. Whenever both sets end up the same size, `|A−B|` always equals `|B−A|` (basic set arithmetic), so the matrix comes out symmetric no matter what alpha/beta you pick — silently defeating the point of using Tversky over Jaccard. If you actually need to see asymmetry, build the sets yourself with a frequency THRESHOLD instead (`{bigram for bigram, n in counter.items() if n >= k}`) so the two sets can come out different sizes, then call `tversky_index()` directly. `day4_similarity.ipynb`'s Tversky section does exactly this.

### Spatial distance (similarity as closeness in feature-space)

A fourth, geometric way to compare melodies: instead of comparing sequences or sets, reduce each piece to a handful of numbers (a point in space), then measure how close two points are.

**`melodic_feature_vector(file_path_or_score, features=('note_density', 'tonic_prevalence', 'pitch_range', 'mean_interval'))`** — one piece's "point in space": notes per quarter-note, fraction of notes on the tonic (scale-degree 1, relative to the piece's own detected key), pitch range in semitones, and mean melodic-leap size. Returns a `pd.Series`.
```python
melodic_feature_vector('../data/tune1.krn')
```

**`feature_matrix(files, features=(...), tune_ids=None, pattern='*.krn', verbose=False)`** — ONE-STOP: `melodic_feature_vector()` for every file in a folder/list, returned as a tune x feature `pd.DataFrame`, ready for `spatial_similarity_matrix()`.
```python
feats = feature_matrix(files_subset, tune_ids=tids)
```

**`spatial_similarity(vec_a, vec_b)`** — `sim(A,B) = 1 / (1 + Euclidean distance(A,B))`. Identical points score 1.0; similarity falls off as points get farther apart.

**`spatial_similarity_matrix(feature_df, standardize=True, plot=False)`** — pairwise `spatial_similarity()` for every row of a feature table. `standardize=True` (default) z-scores each column first, so no single feature's scale (e.g. pitch range in semitones vs. a 0-1 proportion) dominates the distance.
```python
sim = spatial_similarity_matrix(feats, plot=True)
```
**Limitations to know about** (covered in the Day 4 notebook): spatial accounts assume reflexivity, symmetry, and transitivity, all of which real similarity judgments routinely violate (Krumhansl 1979; Bartlett & Dowling 1988; the classic Jamaica-Cuba-Russia transitivity counterexample).

**`find_transitivity_violation(corpus_path, n_tunes=20, sim_threshold=0.7, diff_threshold=0.4)`** — turns the transitivity limitation above into a live demo: samples `n_tunes` random pieces from a kern folder, builds their spatial similarity matrix, and searches every (A, B, C) triple for the worst case of "A~B and B~C both above `sim_threshold`, but A~C below `diff_threshold`" — i.e. a real violation of "if A resembles B and B resembles C, then A should resemble C." Prints the worst triple it finds (or says none was found at the current thresholds) and returns `(a, b, c, sim_ab, sim_bc, sim_ac)`.
```python
find_transitivity_violation('../data/Essen/Czech')
find_transitivity_violation('../data/Essen/Polska', n_tunes=30)
```

### Alignment (similarity as shared higher-order structure)

**`structural_alignment(file_path_or_score_a, file_path_or_score_b, n_segments=2)`** — a deliberately SIMPLIFIED, illustrative take on Gentner's (1983) structure-mapping theory: splits both melodies into `n_segments` equal-length chunks, aligns them by position, and scores each aligned pair on three RELATIONAL properties (does the segment move in the same overall direction? does it repeat its own first pitch internally? how much does its note-to-note contour agree with the other segment's?). Not a full structure-mapping engine — real alignment work involves much richer relational structure.
```python
result = structural_alignment('../data/tune1.krn', '../data/tune2.krn', n_segments=2)
result.attrs['overall_score']   # single 0-1 number, mean across segments/columns
```

---

## Day 4 — `utils/recommender.py`: recommenders built on the similarity work

A similarity (or distance) matrix plus "show me the closest ones" *is* a recommender system. This module makes that explicit, then scales it to the classic item-item vs. user-user distinction: item-item compares tunes by their own musical features (the matrices you already built); user-user compares "listeners" — here, composers stand in for listeners, since composer style is a proxy for shared audience.

**`recommend_similar(matrix, tune_ids, query, top_n=5, verbose=False)`** — ITEM-ITEM: given a precomputed pairwise DISTANCE matrix (0 = identical) aligned with `tune_ids`, return the `top_n` tunes closest to `query`.
```python
recommend_similar(edit_mat, tids, tids[0], top_n=5)
```

**`build_composer_profiles(composer_sources, pattern='*.krn', max_interval=12, verbose=True, plot=False)`** — ONE-STOP: build a per-composer "style fingerprint" (normalized pitch-class histogram + normalized melodic-interval histogram, averaged across every piece in that composer's corpus). `composer_sources` is a dict `{composer_name: folder_or_file_list}`. Prints progress every 25 files per composer when `verbose=True`; unreadable files are skipped with a warning rather than raising.
```python
profiles = build_composer_profiles({
    'Bach': '../data/humdrum_scores/Bach/Inventio',
    'Beethoven': '../data/humdrum_scores/Beethoven/Quartets.Str',
    'Chopin': '../data/humdrum_scores/Chopin/Mazurkas',
    'Mozart': '../data/humdrum_scores/Mozart/Quartets.Str',
})
```

**`composer_similarity_matrix(profiles, metric='cosine', plot=False)`** — Compare composer profiles to each other. Returns a SIMILARITY matrix (higher = more alike — the opposite convention from `recommend_similar()`'s distance matrices). `metric='cosine'` or `'correlation'`.
```python
sim = composer_similarity_matrix(profiles, plot=True)
```

**`user_user_recommend(target, similarity_matrix, top_n=3, verbose=False)`** — USER-USER: given a target composer, return the `top_n` other composers with the most similar overall style, per `composer_similarity_matrix()` — "what would Bach listen to?"
```python
user_user_recommend('Bach', sim, top_n=3, verbose=True)
```

**`recommender_widget(matrices, tune_ids, top_n=5)`** — Interactive ipywidgets explorer: dropdowns for tune and metric, recommendations update live. `matrices` is a dict `{metric_name: distance_matrix}`. Jupyter-only (raises a clear `ImportError` if `ipywidgets` isn't available).
```python
recommender_widget({'Edit distance': edit_mat, 'Jaccard': jac_mat, 'Contour': con_mat}, tids)
```

---

## Day 5 — `utils/idyom.py`: predicting the next note (LTM + STM)

IDyOM-style predictive models: a **long-term model (LTM)**, trained ahead of time on a corpus of *other* pieces (style knowledge), and a **short-term model (STM)**, trained online from scratch on the piece currently playing (what's been learned so far, this piece only). Combining the two — weighted by which one is more confident at each moment — produces a per-note "surprise" score (information content). Only `by='pitch_class'` and `by='scale_degree'` are supported (both have a fixed, known alphabet needed for smoothing).

**`NGramModel(n=3, by='pitch_class', alpha=0.5)`** — the shared model class behind both LTM and STM. `.train(sequence)` batch-trains on a full sequence; `.update(context, symbol)` records one online observation; `.predict_proba(context)` returns a smoothed probability distribution over the alphabet; `.entropy(context)` is that distribution's Shannon entropy.
```python
model = NGramModel(n=3, by='pitch_class')
model.train(['C', 'D', 'E', 'D', 'C'])
model.predict_proba(('D', 'E'))
```

**`information_content(symbol, probs, base=2)`** — CORE MEASURE: IC = -log_b(P(symbol)) under a predicted distribution. 0 = the model was certain and right; bigger = the model was caught off guard.
```python
ic = information_content('C', model.predict_proba(('D', 'E')))
```

**`stm_information_content(file_path_or_score, n=3, by='pitch_class', alpha=0.5)`** — ONE-STOP: how surprising is each note, based only on what's been heard so far IN this piece? Builds an STM from scratch and predicts online, note by note (no outside training needed).
```python
df, probs = stm_information_content('../data/happy_birthday.krn', n=3)
```

**`train_ltm_model(source, n=3, by='pitch_class', pattern='*.krn', alpha=0.5)`** — ONE-STOP: train a long-term model on a corpus of other pieces.
```python
ltm = train_ltm_model('../data/Essen/Deutschl/test', n=3)
```

**`ltm_information_content(file_path_or_score, ltm_model, n=None)`** — ONE-STOP: how surprising is each note according to the frozen LTM (no online learning at test time)?
```python
df, probs = ltm_information_content('../data/Essen/England/england1.krn', ltm)
```

**`combine_ltm_stm(stm_df, stm_probs, ltm_df, ltm_probs, bias=1.0)`** — fuse STM and LTM predictions, weighted by inverse entropy (whichever model is more confident at that moment contributes more) — IDyOM's actual combination rule.
```python
combined = combine_ltm_stm(stm_df, stm_probs, ltm_df, ltm_probs)
```

**`surprise_contour(file_path_or_score, ltm_model=None, n=3, by='pitch_class', plot=True)`** — ONE-STOP, the headline plot: surprise (information content) over the whole piece. Pass `ltm_model` for STM+LTM combined; omit it for STM-only (works on a single piece, no setup). Peaks mark the most surprising notes — often phrase boundaries or unexpected leaps.
```python
surprise_contour('../data/happy_birthday.krn', n=3)                     # STM only
ltm = train_ltm_model('../data/Essen/Deutschl/test', n=3)
surprise_contour('../data/Essen/England/england1.krn', ltm_model=ltm)   # STM + LTM
```

**`corpus_information_content(source, ltm_model=None, n=3, by='pitch_class', pattern='*.krn')`** — ONE-STOP, the biggest question: mean information content per piece, across a whole corpus, plus a histogram. Same shape as `compare_keyfinding_corpus()`'s `results` table — feed it into `ttest_algorithm_correlations()` / `compare_algorithms_anova()` (from `keyfinding.py`) the same column-relabeling way, to test hypotheses about which corpus/model/n produces more or less surprising melodies.
```python
table = corpus_information_content('../data/Essen/England', ltm_model=ltm, n=3)
table.sort_values('mean_ic', ascending=False).head()   # most surprising tunes
```

---

## Setup

**`setup_colab(repo_url=...)`** — Clone the course repo and set the working directory when running in Colab; does nothing if already running locally with `../data` present. First cell of every notebook.
```python
from utils import setup_colab
setup_colab()
```
