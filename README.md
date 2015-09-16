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
* `bench_*_missing_first` searches for a missing string that sorts before the
  first string
* `bench_*_missing_last` searches for a missing string that sorts after the
  last string

To run the actual tests, just run:

```
% python generate-search.py --sort rust-keywords > search/src/lib.rs && cargo bench
   Compiling search v0.1.0 (file:///Users/erickt/projects/rust/sorted_match)
   Compiling sorted_match v0.1.0 (file:///Users/erickt/projects/rust/sorted_match)
     Running target/release/sorted_match-5d78a942fa654b25

running 30 tests
test bench_average_binary        ... bench:       3,813 ns/iter (+/- 1,292) = 78 MB/s
test bench_average_hashmap       ... bench:       4,887 ns/iter (+/- 1,476) = 61 MB/s
test bench_average_linear        ... bench:       3,577 ns/iter (+/- 1,089) = 83 MB/s
test bench_average_match         ... bench:       3,602 ns/iter (+/- 504) = 83 MB/s
test bench_average_trie          ... bench:       3,101 ns/iter (+/- 383) = 96 MB/s
test bench_first_binary          ... bench:       1,913 ns/iter (+/- 375) = 156 MB/s
test bench_first_hashmap         ... bench:       2,304 ns/iter (+/- 734) = 130 MB/s
test bench_first_linear          ... bench:         182 ns/iter (+/- 38) = 1648 MB/s
test bench_first_match           ... bench:         180 ns/iter (+/- 107) = 1666 MB/s
test bench_first_trie            ... bench:         577 ns/iter (+/- 124) = 519 MB/s
test bench_last_binary           ... bench:       1,454 ns/iter (+/- 99) = 206 MB/s
test bench_last_hashmap          ... bench:       2,113 ns/iter (+/- 468) = 141 MB/s
test bench_last_linear           ... bench:       3,247 ns/iter (+/- 885) = 92 MB/s
test bench_last_match            ... bench:       3,021 ns/iter (+/- 795) = 99 MB/s
test bench_last_trie             ... bench:         291 ns/iter (+/- 71) = 1030 MB/s
test bench_middle_binary         ... bench:         471 ns/iter (+/- 126) = 636 MB/s
test bench_middle_hashmap        ... bench:       1,993 ns/iter (+/- 442) = 150 MB/s
test bench_middle_linear         ... bench:       1,016 ns/iter (+/- 249) = 295 MB/s
test bench_middle_match          ... bench:       1,035 ns/iter (+/- 234) = 289 MB/s
test bench_middle_trie           ... bench:         282 ns/iter (+/- 196) = 1063 MB/s
test bench_missing_first_binary  ... bench:       1,806 ns/iter (+/- 417) = 166 MB/s
test bench_missing_first_hashmap ... bench:       2,023 ns/iter (+/- 596) = 148 MB/s
test bench_missing_first_linear  ... bench:         575 ns/iter (+/- 125) = 521 MB/s
test bench_missing_first_match   ... bench:         543 ns/iter (+/- 117) = 552 MB/s
test bench_missing_first_trie    ... bench:         240 ns/iter (+/- 138) = 1249 MB/s
test bench_missing_last_binary   ... bench:       1,539 ns/iter (+/- 506) = 194 MB/s
test bench_missing_last_hashmap  ... bench:       2,041 ns/iter (+/- 480) = 146 MB/s
test bench_missing_last_linear   ... bench:       2,104 ns/iter (+/- 1,389) = 142 MB/s
test bench_missing_last_match    ... bench:       2,176 ns/iter (+/- 432) = 137 MB/s
test bench_missing_last_trie     ... bench:         222 ns/iter (+/- 20) = 1351 MB/s

test result: ok. 0 passed; 0 failed; 0 ignored; 30 measured
```

By default this uses the original string list as the haystack to search in.
This can be overridden with:

```
% python generate-search.py \
	--sort-by-frequency ~/rust/rust/src/librustc/middle/ty.rs \
	rust-keywords > search/src/lib.rs && \
 	HAYSTACK=~/rust/rust/src/librustc/middle/ty.rs cargo bench
   Compiling search v0.1.0 (file:///Users/erickt/projects/rust/sorted_match)
   Compiling sorted_match v0.1.0 (file:///Users/erickt/projects/rust/sorted_match)
     Running target/release/sorted_match-5d78a942fa654b25

running 30 tests
test bench_average_binary        ... bench:   5,741,766 ns/iter (+/- 1,389,598) = 33 MB/s
test bench_average_hashmap       ... bench:   6,072,628 ns/iter (+/- 1,381,045) = 31 MB/s
test bench_average_linear        ... bench:   3,738,524 ns/iter (+/- 1,156,984) = 51 MB/s
test bench_average_match         ... bench:   3,804,468 ns/iter (+/- 760,833) = 50 MB/s
test bench_average_trie          ... bench:   3,541,574 ns/iter (+/- 879,198) = 54 MB/s
test bench_first_binary          ... bench:   1,274,322 ns/iter (+/- 153,439) = 150 MB/s
test bench_first_hashmap         ... bench:   2,864,557 ns/iter (+/- 989,497) = 67 MB/s
test bench_first_linear          ... bench:     607,929 ns/iter (+/- 136,532) = 316 MB/s
test bench_first_match           ... bench:     561,987 ns/iter (+/- 284,742) = 342 MB/s
test bench_first_trie            ... bench:     380,664 ns/iter (+/- 56,177) = 504 MB/s
test bench_last_binary           ... bench:   2,791,124 ns/iter (+/- 570,434) = 68 MB/s
test bench_last_hashmap          ... bench:   3,211,817 ns/iter (+/- 889,456) = 59 MB/s
test bench_last_linear           ... bench:     888,131 ns/iter (+/- 358,850) = 216 MB/s
test bench_last_match            ... bench:     907,487 ns/iter (+/- 313,105) = 211 MB/s
test bench_last_trie             ... bench:     738,395 ns/iter (+/- 302,533) = 260 MB/s
test bench_middle_binary         ... bench:   2,621,390 ns/iter (+/- 569,592) = 73 MB/s
test bench_middle_hashmap        ... bench:   2,952,153 ns/iter (+/- 722,948) = 64 MB/s
test bench_middle_linear         ... bench:   1,799,750 ns/iter (+/- 453,124) = 106 MB/s
test bench_middle_match          ... bench:   1,733,606 ns/iter (+/- 466,720) = 110 MB/s
test bench_middle_trie           ... bench:     401,265 ns/iter (+/- 108,148) = 479 MB/s
test bench_missing_first_binary  ... bench:   2,194,377 ns/iter (+/- 519,818) = 87 MB/s
test bench_missing_first_hashmap ... bench:   2,569,862 ns/iter (+/- 772,117) = 74 MB/s
test bench_missing_first_linear  ... bench:   3,009,606 ns/iter (+/- 785,544) = 63 MB/s
test bench_missing_first_match   ... bench:   2,983,913 ns/iter (+/- 771,314) = 64 MB/s
test bench_missing_first_trie    ... bench:     323,221 ns/iter (+/- 79,672) = 594 MB/s
test bench_missing_last_binary   ... bench:   2,571,708 ns/iter (+/- 670,678) = 74 MB/s
test bench_missing_last_hashmap  ... bench:   2,807,963 ns/iter (+/- 910,782) = 68 MB/s
test bench_missing_last_linear   ... bench:     273,713 ns/iter (+/- 42,410) = 702 MB/s
test bench_missing_last_match    ... bench:     299,812 ns/iter (+/- 106,137) = 641 MB/s
test bench_missing_last_trie     ... bench:     700,553 ns/iter (+/- 188,270) = 274 MB/s

test result: ok. 0 passed; 0 failed; 0 ignored; 30 measured
```
