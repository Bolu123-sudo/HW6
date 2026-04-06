# COP 4533 Assignment 3

**Student Name:** Boluwatife Abegunde  
**UFID:** [replace with your UFID]

## Summary
This project finds a common subsequence of two strings whose total character score is as large as possible.
Each character has a nonnegative weight, so the goal is to maximize total score rather than just the number of matched characters.

The program prints:
1. the best score
2. one subsequence that achieves that score

## Files
```text
.
├── Makefile
├── README.md
├── src/
│   └── solver_driver.cpp
├── scripts/
│   ├── benchmark.py
│   └── generate_tests.py
└── data/
    ├── example.in
    ├── example.out
    ├── test1.in ... test10.in
    ├── test1.out ... test10.out
    ├── runtime_results.csv
    ├── runtime_graph.svg
    └── runtime_graph.png
```

## Build
```bash
make
```

This creates:
```bash
./weighted_matcher
```

## Run
Using redirected input:
```bash
./weighted_matcher < data/example.in
```

Using a file argument:
```bash
./weighted_matcher data/example.in
```

## Format
```text
K
x1 v1
x2 v2
...
xK vK
A
B
```

Where:
- `K` is the number of scored characters
- each of the next `K` lines gives a character and its value
- `A` is the first string
- `B` is the second string

## Example
### Input (`data/example.in`)
```text
3
a 2
b 4
c 5
aacb
caab
```

### Output (`data/example.out`)
```text
9
cb
```

The subsequence `cb` has score `5 + 4 = 9`.

## Question 1: Empirical Comparison
I created 10 nontrivial inputs, each with string lengths at least 25.
The generator intentionally varies:
- alphabet size
- character weights
- string lengths
- repetition patterns
- shuffled shared blocks
- mutation noise

Generate the 10 tests with:
```bash
python3 scripts/generate_tests.py
```

Run the timing script with:
```bash
python3 scripts/benchmark.py
```

The benchmark script:
- runs the solver on all 10 files
- writes the matching `.out` files
- stores timing data in `data/runtime_results.csv`
- writes a dependency-free graph to `data/runtime_graph.svg`
- optionally writes `data/runtime_graph.png` if `matplotlib` is installed

### Runtime Discussion
The measured growth follows the dynamic programming table size closely. Since the algorithm fills one table entry per pair of prefix positions, the amount of work scales with `|A| * |B|`, which gives the expected `O(nm)` runtime trend. Small timing variation is normal because operating-system scheduling and process startup overhead add noise to real measurements.

## Question 2: Recurrence Equation
Let `best[i][j]` represent the maximum total score obtainable from the prefixes `A[0..i-1]` and `B[0..j-1]`.

### Base cases
```text
best[0][j] = 0
best[i][0] = 0
```
If either prefix is empty, no positive-score common subsequence can be formed.

### Recurrence
If the current characters are different, the best answer must come from skipping one side:
```text
best[i][j] = max(best[i-1][j], best[i][j-1])
```

If the current characters match, we may also choose to use that character:
```text
best[i][j] = max(
    best[i-1][j],
    best[i][j-1],
    best[i-1][j-1] + value(A[i-1])
)
```

### Why it is correct
Any optimal answer on prefixes must do one of three things: ignore the last character of `A`, ignore the last character of `B`, or match both last characters when they are equal. The recurrence checks exactly those possibilities and keeps the largest score, so each table entry is correct.

## Question 3: Pseudocode and Big-Oh
### Pseudocode
```text
solve(A, B, score):
    let n = length(A)
    let m = length(B)
    create table best with (n + 1) rows and (m + 1) columns
    fill first row and first column with 0

    for r from 1 to n:
        for c from 1 to m:
            skip_left = best[r - 1][c]
            skip_right = best[r][c - 1]
            best[r][c] = max(skip_left, skip_right)

            if A[r - 1] == B[c - 1]:
                take_both = best[r - 1][c - 1] + score[A[r - 1]]
                best[r][c] = max(best[r][c], take_both)

    r = n
    c = m
    answer = empty string

    while r > 0 and c > 0:
        if A[r - 1] == B[c - 1] and
           best[r][c] == best[r - 1][c - 1] + score[A[r - 1]]:
            append A[r - 1] to answer
            r = r - 1
            c = c - 1
        else if best[r - 1][c] >= best[r][c - 1]:
            r = r - 1
        else:
            c = c - 1

    reverse(answer)
    print best[n][m]
    print answer
```

### Runtime
There are `(n + 1)(m + 1)` table entries, and each one is computed in constant time, so the runtime is:
```text
O(nm)
```

### Space
The full table is stored, so the space complexity is:
```text
O(nm)
```

## Assumptions
- all character values are nonnegative
- input strings contain only characters listed in the scoring section
- any optimal subsequence is acceptable when multiple answers have the same score

## Reproducing Results
You can reproduce with:
```bash
make
python3 scripts/generate_tests.py
python3 scripts/benchmark.py
./weighted_matcher < data/example.in
```
