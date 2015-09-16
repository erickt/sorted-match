#![feature(test)]

extern crate test;
extern crate search;

use std::collections::HashMap;
use std::env;
use std::fs;

fn haystack() -> (Vec<String>, HashMap<String, usize>) {
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

    let mut words = HashMap::new();

    for token in tokens.iter() {
        words.insert(token.clone(), search::match_search(&token));
    }

    (tokens, words)
}

fn bench_search_average<F>(haystack: &[String], words: &HashMap<String, usize>, f: F)
    where F: Fn(&str) -> usize,
{
    for hay in haystack.iter() {
        let value = *words.get(&**hay).unwrap();
        assert_eq!(value, (f)(hay));
    }

    assert_eq!(
        search::HAYSTACK.len(),
        (f)(search::MISSING));
}

fn bench_search_one<F>(haystack: &[String], needle: &str, index: usize, f: F)
    where F: Fn(&str) -> usize,
{
    for _ in haystack.iter() {
        assert_eq!(index, (f)(needle));
    }
}

fn bench_search_first<F>(haystack: &[String], f: F)
    where F: Fn(&str) -> usize,
{
    let &(word, index) = search::HAYSTACK.first().unwrap();
    bench_search_one(
        haystack,
        word,
        index,
        f)
}

fn bench_search_middle<F>(haystack: &[String], f: F)
    where F: Fn(&str) -> usize,
{
    let index = search::HAYSTACK.len() / 2;
    let &(word, index) = search::HAYSTACK.get(index).unwrap();
    bench_search_one(
        haystack,
        word,
        index,
        f)
}

fn bench_search_last<F>(haystack: &[String], f: F)
    where F: Fn(&str) -> usize,
{
    let &(word, index) = search::HAYSTACK.last().unwrap();
    bench_search_one(
        haystack,
        word,
        index,
        f)
}

fn bench_search_missing<F>(haystack: &[String], f: F)
    where F: Fn(&str) -> usize,
{
    bench_search_one(
        haystack,
        search::MISSING,
        search::HAYSTACK.len(),
        f)
}

//////////////////////////////////////////////////////////////////////////////

#[bench]
fn bench_match_average(b: &mut test::Bencher) {
    let (haystack, words) = haystack();
    b.iter(|| {
        bench_search_average(&haystack, &words, search::match_search)
    })
}

#[bench]
fn bench_match_first(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_first(&haystack, search::match_search)
    })
}

#[bench]
fn bench_match_middle(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_middle(&haystack, search::match_search)
    })
}

#[bench]
fn bench_match_last(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_last(&haystack, search::match_search)
    })
}

#[bench]
fn bench_match_missing(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_missing(&haystack, search::match_search)
    })
}

//////////////////////////////////////////////////////////////////////////////

#[bench]
fn bench_linear_average(b: &mut test::Bencher) {
    let (haystack, words) = haystack();
    b.iter(|| {
        bench_search_average(&haystack, &words, search::linear_search)
    })
}

#[bench]
fn bench_linear_first(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_first(&haystack, search::linear_search)
    })
}

#[bench]
fn bench_linear_middle(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_middle(&haystack, search::linear_search)
    })
}

#[bench]
fn bench_linear_last(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_last(&haystack, search::linear_search)
    })
}

#[bench]
fn bench_linear_missing(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_missing(&haystack, search::linear_search)
    })
}

//////////////////////////////////////////////////////////////////////////////

#[bench]
fn bench_binary_average(b: &mut test::Bencher) {
    let (haystack, words) = haystack();
    b.iter(|| {
        bench_search_average(&haystack, &words, search::binary_search)
    })
}

#[bench]
fn bench_binary_first(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_first(&haystack, search::binary_search)
    })
}

#[bench]
fn bench_binary_middle(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_middle(&haystack, search::binary_search)
    })
}

#[bench]
fn bench_binary_last(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_last(&haystack, search::binary_search)
    })
}

#[bench]
fn bench_binary_missing(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_missing(&haystack, search::binary_search)
    })
}

//////////////////////////////////////////////////////////////////////////////

#[bench]
fn bench_trie_average(b: &mut test::Bencher) {
    let (haystack, words) = haystack();
    b.iter(|| {
        bench_search_average(&haystack, &words, search::trie_search)
    })
}

#[bench]
fn bench_trie_first(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_first(&haystack, search::trie_search)
    })
}

#[bench]
fn bench_trie_middle(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_middle(&haystack, search::trie_search)
    })
}

#[bench]
fn bench_trie_last(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_last(&haystack, search::trie_search)
    })
}

#[bench]
fn bench_trie_missing(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    b.iter(|| {
        bench_search_missing(&haystack, search::trie_search)
    })
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
fn bench_hashmap_average(b: &mut test::Bencher) {
    let (haystack, words) = haystack();
    let map = hashmap();
    b.iter(|| {
        bench_search_average(&haystack, &words, |n| hashmap_search(&map, n))
    })
}

#[bench]
fn bench_hashmap_first(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    let map = hashmap();
    b.iter(|| {
        bench_search_first(&haystack, |n| hashmap_search(&map, n))
    })
}

#[bench]
fn bench_hashmap_middle(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    let map = hashmap();
    b.iter(|| {
        bench_search_middle(&haystack, |n| hashmap_search(&map, n))
    })
}

#[bench]
fn bench_hashmap_last(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    let map = hashmap();
    b.iter(|| {
        bench_search_last(&haystack, |n| hashmap_search(&map, n))
    })
}

#[bench]
fn bench_hashmap_missing(b: &mut test::Bencher) {
    let (haystack, _) = haystack();
    let map = hashmap();
    b.iter(|| {
        bench_search_missing(&haystack, |n| hashmap_search(&map, n))
    })
}
