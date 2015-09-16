Experiments with alternative string pattern matching algorithms.

Generating Patterns
===================

First create a file that's filled with the the strings you want in your
patterns. For example,
[rust\_keywords](https://github.com/erickt/sorted_match/blob/master/rust_keywords).
Then run:

```
% python generate-search.py rust-keywords > search/src/lib.rs
```

`generate-search.py` supports a few ways to modify the ordering of the strings
for linear searches. This uses `librustc/middle/ty.rs` to calculate the
frequency, but reverses the list to pessimize linear searches.

```
% python generate-search.py \
	--reverse \
	--sort-by-frequency $RUST_DIR/src/librustc/middle/ty.rs \
	rust-keywords > search/src/lib.rs
```

Benchmkarks
===========

The benchmarks test the agorithm for a couple situations:

This walks over the pattern strings in a variety of manners:

* `bench_*_average` tests every string in the haystack
* `bench_*_first` searches for the first string in the list
* `bench_*_first` searches for the last string in the list
* `bench_*_missing` searches for a missing string

To run the actual tests, just run:

```
% cargo bench
     Running target/release/sorted_match-5d78a942fa654b25

running 25 tests
test bench_binary_average  ... bench:       3,598 ns/iter (+/- 419)
test bench_binary_first    ... bench:       1,767 ns/iter (+/- 115)
test bench_binary_last     ... bench:         881 ns/iter (+/- 93)
test bench_binary_middle   ... bench:       1,707 ns/iter (+/- 111)
test bench_binary_missing  ... bench:       1,629 ns/iter (+/- 104)
test bench_hashmap_average ... bench:       4,320 ns/iter (+/- 379)
test bench_hashmap_first   ... bench:       1,997 ns/iter (+/- 162)
test bench_hashmap_last    ... bench:       1,849 ns/iter (+/- 254)
test bench_hashmap_middle  ... bench:       1,837 ns/iter (+/- 207)
test bench_hashmap_missing ... bench:       1,809 ns/iter (+/- 512)
test bench_linear_average  ... bench:       3,156 ns/iter (+/- 786)
test bench_linear_first    ... bench:         188 ns/iter (+/- 40)
test bench_linear_last     ... bench:       1,899 ns/iter (+/- 321)
test bench_linear_middle   ... bench:         423 ns/iter (+/- 250)
test bench_linear_missing  ... bench:       2,051 ns/iter (+/- 584)
test bench_match_average   ... bench:       3,289 ns/iter (+/- 782)
test bench_match_first     ... bench:         186 ns/iter (+/- 85)
test bench_match_last      ... bench:       2,014 ns/iter (+/- 644)
test bench_match_middle    ... bench:         403 ns/iter (+/- 134)
test bench_match_missing   ... bench:       2,172 ns/iter (+/- 529)
test bench_trie_average    ... bench:       3,265 ns/iter (+/- 896)
test bench_trie_first      ... bench:         531 ns/iter (+/- 176)
test bench_trie_last       ... bench:         304 ns/iter (+/- 86)
test bench_trie_middle     ... bench:         259 ns/iter (+/- 53)
test bench_trie_missing    ... bench:         274 ns/iter (+/- 95)
```

By default this uses the original string list as the haystack to search in.
This can be overridden with:

```
% env HAYSTACK=$RUST_DIR/src/librustc/middle/ty.rs cargo bench
     Running target/release/sorted_match-5d78a942fa654b25

running 25 tests
test bench_binary_average  ... bench:   5,041,879 ns/iter (+/- 1,202,342)
test bench_binary_first    ... bench:   2,777,212 ns/iter (+/- 1,097,922)
test bench_binary_last     ... bench:   1,373,670 ns/iter (+/- 603,955)
test bench_binary_middle   ... bench:   2,443,177 ns/iter (+/- 666,406)
test bench_binary_missing  ... bench:   2,324,033 ns/iter (+/- 772,219)
test bench_hashmap_average ... bench:   5,848,525 ns/iter (+/- 1,927,542)
test bench_hashmap_first   ... bench:   3,036,621 ns/iter (+/- 931,547)
test bench_hashmap_last    ... bench:   2,760,366 ns/iter (+/- 581,910)
test bench_hashmap_middle  ... bench:   2,853,826 ns/iter (+/- 834,944)
test bench_hashmap_missing ... bench:   2,468,195 ns/iter (+/- 976,209)
test bench_linear_average  ... bench:   4,631,128 ns/iter (+/- 746,226)
test bench_linear_first    ... bench:     265,450 ns/iter (+/- 78,900)
test bench_linear_last     ... bench:   2,995,565 ns/iter (+/- 802,273)
test bench_linear_middle   ... bench:     628,370 ns/iter (+/- 215,615)
test bench_linear_missing  ... bench:   2,863,219 ns/iter (+/- 614,214)
test bench_match_average   ... bench:   4,307,364 ns/iter (+/- 1,172,428)
test bench_match_first     ... bench:     252,207 ns/iter (+/- 123,532)
test bench_match_last      ... bench:   3,004,341 ns/iter (+/- 796,188)
test bench_match_middle    ... bench:     509,714 ns/iter (+/- 215,135)
test bench_match_missing   ... bench:   2,874,010 ns/iter (+/- 648,018)
test bench_trie_average    ... bench:   3,720,571 ns/iter (+/- 1,043,538)
test bench_trie_first      ... bench:     769,756 ns/iter (+/- 115,080)
test bench_trie_last       ... bench:     446,163 ns/iter (+/- 154,940)
test bench_trie_middle     ... bench:     358,770 ns/iter (+/- 153,687)
test bench_trie_missing    ... bench:     388,271 ns/iter (+/- 107,986)
```
