To Run:

```
python generate-search.py prefix 5 > search/src/lib.rs && cargo bench
```

where `prefix` is a common string in order to force collisions, and `5` is the
number of strings in the match.
