import textwrap
import pprint
import sys

prefix = sys.argv[1]
count = int(sys.argv[2])

haystack = [prefix + c for c in [
    'a',
    'b',
    'c',
    'd',
    'e',
    'f',
    'g',
    'h',
    'i',
    'j',
    'k',
    'l',
    'm',
    'n',
    'o',
    'p',
    'q',
    'r',
    's',
    't',
    'u',
    'v',
    'w',
    'x',
    'y',
    'z',
]][:count]

print """\
use std::cmp::Ordering;

pub static HAYSTACK: &'static [&'static str] = &[%s];
""" % ','.join('"%s"' % hay for hay in haystack)

print """\n
#[inline]
fn cmp_slice(a: &str, b: &str) -> Ordering {
    // NOTE: In theory n should be libc::size_t and not usize, but libc is not available here
    #[allow(improper_ctypes)]
    extern { fn memcmp(s1: *const i8, s2: *const i8, n: usize) -> i32; }
    unsafe {
        let cmp = memcmp(a.as_ptr() as *const i8, b.as_ptr() as *const i8, a.len());
        if cmp == 0 {
            a.len().cmp(&b.len())
        } else if cmp < 0 {
            Ordering::Less
        } else {
            Ordering::Greater
        }

    }
}

/*
//#[no_mangle]
//#[inline(never)]
fn cmp_slice(a: &str, b: &str) -> Ordering {
    for (a_byte, b_byte) in a.bytes().zip(b.bytes()) {
        if a_byte < b_byte {
            return Ordering::Less;
        } else if a_byte > b_byte {
            return Ordering::Greater;
        }
    }

    if a.len() < b.len() {
        return Ordering::Less;
    } else if a.len() > b.len() {
        return Ordering::Greater;
    } else {
        return Ordering::Equal;
    }
}
*/

//#[no_mangle]
#[inline]
fn eq_slice(a: &str, b: &str) -> bool {
    // NOTE: In theory n should be libc::size_t and not usize, but libc is not available here
    #[allow(improper_ctypes)]
    extern { fn memcmp(s1: *const i8, s2: *const i8, n: usize) -> i32; }
    a.len() == b.len() && unsafe {
        memcmp(a.as_ptr() as *const i8,
               b.as_ptr() as *const i8,
               a.len()) == 0
    }
}
"""

# ------------------------------------------------------------------------------

print """\
#[no_mangle]
#[inline(never)]
pub fn match_search(needle: &str) -> usize {
    match needle {"""

for i, hay in enumerate(haystack):
  print '        "%s" => %s,' % (hay, i)

print """\
        _ => %s
    }
}""" % (i + 1)
print

# ------------------------------------------------------------------------------

print """\
//#[no_mangle]
#[inline(never)]
pub fn linear_std_search(needle: &str) -> usize {"""

first = True
for i, hay in enumerate(haystack):
  if first:
    first = False
    print '    if needle == "%s" { %s }' % (hay, i)
  else:
    print '    else if needle == "%s" { %s }' % (hay, i)

print """\
    else { %s }
}""" % (i + 1)
print

# ------------------------------------------------------------------------------

print """\
//#[no_mangle]
#[inline(never)]
pub fn linear_memcmp_search(needle: &str) -> usize {"""

first = True
for i, hay in enumerate(haystack):
  if first:
    first = False
    print '    if eq_slice(needle, "%s") { %s }' % (hay, i)
  else:
    print '    else if eq_slice(needle, "%s") { %s }' % (hay, i)

print """\
    else { %s }
}""" % (i + 1)
print

# ------------------------------------------------------------------------------

ordering = []

def walk(fn, start, end, indent=0):
  if start == end:
    return ""

  index = (end + start) // 2
  spaces = ' ' * indent

  less = walk(fn, start, index, indent=indent + 8)
  if less:
    less = '{\n%s\n%s}' % (less, spaces + ' ' * 4)
  else:
    less = '{ }'

  greater = walk(fn, index + 1, end, indent=indent + 8)
  if greater:
    greater = '{\n%s\n%s}' % (greater, spaces + ' ' * 4)
  else:
    greater = '{ }'

  return """\
%smatch %s(needle, "%s") {
%s    Ordering::Less => %s
%s    Ordering::Equal => { return %s; }
%s    Ordering::Greater => %s
%s}""" % (
      spaces,
      fn,
      haystack[index],
      spaces,
      less,
      spaces,
      index,
      spaces,
      greater,
      spaces,
  )

print """\
//#[no_mangle]
#[inline(never)]
pub fn binary_std_search(needle: &str) -> usize {"""
print walk('str::cmp', 0, len(haystack), 4)
print """\
    %s
}""" % len(haystack)

print """\
//#[no_mangle]
#[inline(never)]
pub fn binary_memcmp_search(needle: &str) -> usize {"""
print walk('cmp_slice', 0, len(haystack), 4)
print """\
    %s
}""" % len(haystack)
