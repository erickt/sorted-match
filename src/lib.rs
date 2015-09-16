#![feature(test)]

extern crate test;
extern crate search;

use std::collections::HashMap;
use std::env;
use std::fs;

fn haystack() -> (Vec<String>, HashMap<String, usize>, usize) {
    use std::io::Read;

    let tokens: Vec<_> = match env::var("HAYSTACK") {
        Ok(file) => {
            let mut f = fs::File::open(file).unwrap();
            let mut s = String::new();
            f.read_to_string(&mut s).unwrap();

            s.split(" ")
                .map(|s| s.to_owned())
                .collect()
        }
        Err(_) => {
            search::HAYSTACK.iter()
                .map(|&(hay, _)| hay.to_string())
                .collect()
        }
    };

    let len = tokens.iter().fold(0, |sum, s| sum + s.len());

    let mut words = HashMap::new();

    for token in tokens.iter() {
        words.insert(token.clone(), search::match_search(&token));
    }

    (tokens, words, len)
}

fn bench_search_average<F>(b: &mut test::Bencher, f: F)
    where F: Fn(&str) -> usize,
{
    let (haystack, words, len) = haystack();
    b.bytes = len as u64;
    b.iter(|| {
        for hay in haystack.iter() {
            let expected = *words.get(&**hay).unwrap();
            let result = (f)(hay);
            assert_eq!(expected, result);
            test::black_box(result);
        }

        let result = (f)(search::MISSING_FIRST);
        assert_eq!(search::HAYSTACK.len(), result);
        test::black_box(result);

        let result = (f)(search::MISSING_FIRST);
        assert_eq!(search::HAYSTACK.len(), result);
        test::black_box(result);
    })
}

fn bench_search_one<F>(b: &mut test::Bencher, needle: &str, index: usize, f: F)
    where F: Fn(&str) -> usize,
{
    let (haystack, _, len) = haystack();
    b.bytes = len as u64;
    b.iter(|| {
        for _ in haystack.iter() {
            let result = (f)(needle);
            assert_eq!(index, result);
            test::black_box(result);
        }
    })
}

fn bench_search_first<F>(b: &mut test::Bencher, f: F)
    where F: Fn(&str) -> usize,
{
    let &(word, index) = search::HAYSTACK.first().unwrap();
    bench_search_one(
        b,
        word,
        index,
        f)
}

fn bench_search_middle<F>(b: &mut test::Bencher, f: F)
    where F: Fn(&str) -> usize,
{
    let index = search::HAYSTACK.len() / 2;
    let &(word, index) = search::HAYSTACK.get(index).unwrap();
    bench_search_one(
        b,
        word,
        index,
        f)
}

fn bench_search_last<F>(b: &mut test::Bencher, f: F)
    where F: Fn(&str) -> usize,
{
    let &(word, index) = search::HAYSTACK.last().unwrap();
    bench_search_one(
        b,
        word,
        index,
        f)
}

fn bench_search_missing_first<F>(b: &mut test::Bencher, f: F)
    where F: Fn(&str) -> usize,
{
    bench_search_one(
        b,
        search::MISSING_FIRST,
        search::HAYSTACK.len(),
        f)
}

fn bench_search_missing_last<F>(b: &mut test::Bencher, f: F)
    where F: Fn(&str) -> usize,
{
    bench_search_one(
        b,
        search::MISSING_LAST,
        search::HAYSTACK.len(),
        f)
}

//////////////////////////////////////////////////////////////////////////////

macro_rules! benchmarks {
    ($($name:ident | $method:ident => $function:expr,)*) => {
        $(
            #[bench]
            fn $name(b: &mut test::Bencher) {
                $method(b, $function)
            }

        )*
    }
}

benchmarks! {
    bench_average_match | bench_search_average => search::match_search,
    bench_first_match | bench_search_first => search::match_search,
    bench_middle_match | bench_search_middle => search::match_search,
    bench_last_match | bench_search_last => search::match_search,
    bench_missing_first_match | bench_search_missing_first => search::match_search,
    bench_missing_last_match | bench_search_missing_last => search::match_search,

    bench_average_linear | bench_search_average => search::linear_search,
    bench_first_linear | bench_search_first => search::linear_search,
    bench_middle_linear | bench_search_middle => search::linear_search,
    bench_last_linear | bench_search_last => search::linear_search,
    bench_missing_first_linear | bench_search_missing_first => search::linear_search,
    bench_missing_last_linear | bench_search_missing_last => search::linear_search,

    bench_average_binary | bench_search_average => search::binary_search,
    bench_first_binary | bench_search_first => search::binary_search,
    bench_middle_binary | bench_search_middle => search::binary_search,
    bench_last_binary | bench_search_last => search::binary_search,
    bench_missing_first_binary | bench_search_missing_first => search::binary_search,
    bench_missing_last_binary | bench_search_missing_last => search::binary_search,

    bench_average_trie | bench_search_average => search::trie_search,
    bench_first_trie | bench_search_first => search::trie_search,
    bench_middle_trie | bench_search_middle => search::trie_search,
    bench_last_trie | bench_search_last => search::trie_search,
    bench_missing_first_trie | bench_search_missing_first => search::trie_search,
    bench_missing_last_trie | bench_search_missing_last => search::trie_search,
}

//////////////////////////////////////////////////////////////////////////////

fn hashmap_search(map: &HashMap<String, usize>, needle: &str) -> usize {
    map.get(needle).map(|v| *v).unwrap_or(search::HAYSTACK.len())
}

fn hashmap() -> HashMap<String, usize> {
    let mut map = HashMap::with_capacity(100);
    for &(hay, index) in search::HAYSTACK.iter() {
        map.insert(hay.to_string(), index);
    }
    map
}

#[bench]
fn bench_average_hashmap(b: &mut test::Bencher) {
    let map = hashmap();
    bench_search_average(b, |n| hashmap_search(&map, n))
}

#[bench]
fn bench_first_hashmap(b: &mut test::Bencher) {
    let map = hashmap();
    bench_search_first(b, |n| hashmap_search(&map, n))
}

#[bench]
fn bench_middle_hashmap(b: &mut test::Bencher) {
    let map = hashmap();
    bench_search_middle(b, |n| hashmap_search(&map, n))
}

#[bench]
fn bench_last_hashmap(b: &mut test::Bencher) {
    let map = hashmap();
    bench_search_last(b, |n| hashmap_search(&map, n))
}

#[bench]
fn bench_missing_first_hashmap(b: &mut test::Bencher) {
    let map = hashmap();
    bench_search_missing_first(b, |n| hashmap_search(&map, n))
}

#[bench]
fn bench_missing_last_hashmap(b: &mut test::Bencher) {
    let map = hashmap();
    bench_search_missing_last(b, |n| hashmap_search(&map, n))
}
