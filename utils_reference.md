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

---

## Day 2 — `utils/ngrams.py`: n-grams and transition matrices

**`get_ngrams(sequence, n)`** — Return all n-grams of a sequence as a list of tuples.
```python
get_ngrams([1, 2, 3, 4], 2)   # -> [(1, 2), (2, 3), (3, 4)]
```

**`note_sequence(file_path_or_score)`** — Return the list of note names (e.g. 'C4', 'D4') in a piece, in order. Chords are expanded.

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

## `utils/similarity.py`: comparing corpora

**`jaccard(counter1, counter2, top_n=50)`** — Jaccard similarity (|intersection| / |union|) between the top-N bigrams of two Counters. 1.0 = identical top-N sets, 0.0 = no overlap.
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

---

## Setup

**`setup_colab(repo_url=...)`** — Clone the course repo and set the working directory when running in Colab; does nothing if already running locally with `../data` present. First cell of every notebook.
```python
from utils import setup_colab
setup_colab()
```
