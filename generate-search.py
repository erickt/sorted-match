import textwrap
import pprint
import sys
import itertools

#prefixes = sys.argv[1].split(',')
#count = int(sys.argv[2])

#haystack_template = list(
#    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#    'abcdefghijklmnopqrstuvwxyz')

haystack_template = [
  "Self",
  "abstract",
  "alignof",
  "as",
  "become",
  "box",
  "break",
  "const",
  "continue",
  "crate",
  "do",
  "else",
  "enum",
  "extern",
  "false",
  "final",
  "fn",
  "for",
  "if",
  "impl",
  "in",
  "let",
  "loop",
  "macro",
  "match",
  "mod",
  "move",
  "mut",
  "offsetof",
  "override",
  "priv",
  "proc",
  "pub",
  "pure",
  "ref",
  "return",
  "self",
  "sizeof",
  "static",
  "struct",
  "super",
  "trait",
  "true",
  "type",
  "typeof",
  "unsafe",
  "unsized",
  "use",
  "virtual",
  "where",
  "while",
  "yield",
]

prefixes = ['']
count = len(haystack_template)

haystack = []

for i, c in enumerate(itertools.cycle(haystack_template)):
  if i >= count:
    break

  prefix = prefixes[i % len(prefixes)]
  haystack.append(prefix + c)

haystack.sort()

def generate_header():
  print textwrap.dedent("""
  use std::cmp::Ordering;

  pub static HAYSTACK: &'static [&'static str] = &[%s];
  """ % ','.join('"%s"' % hay for hay in haystack))

  print textwrap.dedent("""

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
  """)

# ------------------------------------------------------------------------------

def generate_match():
  print textwrap.dedent("""
  #[no_mangle]
  #[inline(never)]
  pub fn match_search(needle: &str) -> usize {
      match needle {""")

  for i, hay in enumerate(haystack):
    print '        "%s" => %s,' % (hay, i)

  print '        _ => %s' % (i + 1)
  print '    }'
  print '}'

# ------------------------------------------------------------------------------

def generate_linear():
  print textwrap.dedent("""
  //#[no_mangle]
  #[inline(never)]
  pub fn linear_search(needle: &str) -> usize {""")

  first = True
  for i, hay in enumerate(haystack):
    if first:
      first = False
      print '    if needle == "%s" { %s }' % (hay, i)
    else:
      print '    else if needle == "%s" { %s }' % (hay, i)

  print '    else { %s }' % (i + 1)
  print '}'

# ------------------------------------------------------------------------------

def walk_binary(fn, start, end, indent=0):
  if start == end:
    return ""

  index = (end + start) // 2
  spaces = ' ' * indent

  less = walk_binary(fn, start, index, indent=indent + 8)
  if less:
    less = '{\n%s\n%s}' % (less, spaces + ' ' * 4)
  else:
    less = '{ }'

  greater = walk_binary(fn, index + 1, end, indent=indent + 8)
  if greater:
    greater = '{\n%s\n%s}' % (greater, spaces + ' ' * 4)
  else:
    greater = '{ }'

  lines = [
    'match %s(needle, "%s") {' % (fn, haystack[index]),
    '    Ordering::Less => %s' % less,
    '    Ordering::Equal => { return %s; }' % index,
    '    Ordering::Greater => %s' % greater,
    '}',
  ]

  return '\n'.join('%s%s' % (spaces, line) for line in lines)

def generate_binary():
  ordering = []

  print textwrap.dedent("""
  //#[no_mangle]
  #[inline(never)]
  pub fn binary_search(needle: &str) -> usize {""")
  print walk_binary('cmp_slice', 0, len(haystack), 4)
  print '    %s' % len(haystack)
  print '}'

# ------------------------------------------------------------------------------

class Trie(object):
  def __init__(self):
    self.root = TrieNode()

  def insert(self, key, value):
    chars = list(key)
    chars.reverse()
    self.root.insert(chars, value)

  def walk(self):
    return self.root.walk(4)

  def print_trie(self):
    self.root.print_trie(0)

  def compress(self):
    self.root.compress(0)

class TrieNode(object):
  def __init__(self):
    self.value = None
    self.children = {}

  def insert(self, chars, value):
    assert len(chars) > 0

    char = chars.pop()

    try:
      node = self.children[char]
    except KeyError:
      node = self.children[char] = TrieNode()

    if len(chars) == 0:
      node.value = value
    else:
      node.insert(chars, value)

  def walk(self, depth):
    assert self.children

    spaces = ' ' * depth
    length = len(next(self.children.iterkeys()))

    lines = [
        '%sif needle.len() >= %s {' % (spaces, length),
    ]

    if length == 1:
      lines.append(
          '%s    let (prefix, needle) = (needle[0], &needle[1..]);' % (spaces,),
      )
    else:
      lines.append(
          '%s    let (prefix, needle) = needle.split_at(%s);' % (spaces, length)
      )

    lines.append(
        '%s    match prefix {' % (spaces,)
    )

    for key, child in sorted(self.children.iteritems()):
      s = [spaces + '        ']

      if len(key) == 1:
        s.append("b'%s'" % key)
      else:
        s.append('b"%s"' % key)

      s.append(' => {')

      lines.append(''.join(s))

      if child.value is not None:
        lines.append('%s            if needle.is_empty() { return %s; }' % (spaces, child.value))

        if child.children:
          lines.append(child.walk(depth + 12))
      else:
        lines.append(child.walk(depth + 12))

      lines.append('%s        }' % (spaces,))

    lines.append('%s        _ => { }' % (spaces,))
    lines.append('%s    }' % (spaces,))
    lines.append('%s}' % (spaces,))

    return '\n'.join(lines)

  def print_trie(self, depth):
    for i, (key, node) in enumerate(sorted(self.children.iteritems())):
      if i == 0:
        prefix = '+'
      else:
        prefix = '|'
      print ' ' * depth, prefix, key,

      if node.value is not None:
        print '=>', node.value
      else:
        print

      node.print_trie(depth + 2)

  def compress(self, depth):
    while len(self.children) == 1 and self.value is None:
      key, node = self.children.popitem()

      if len(node.children) == 1 and node.value is None:
        for k, n in node.children.iteritems():
          self.children[key + k] = n
      else:
        self.children[key] = node
        break

    for node in self.children.itervalues():
      node.compress(depth + 2)


def generate_trie():
  trie = Trie()

  for i, hay in enumerate(haystack):
    trie.insert(hay, i)

  trie.compress()

  print textwrap.dedent("""
  #[inline(never)]
  pub fn trie_search(needle: &str) -> usize {
      let needle = needle.as_bytes();
  """)

  print trie.walk()
  print '    %s' % len(haystack)
  print '}'

# ------------------------------------------------------------------------------

def main():
  generate_header()
  generate_match()
  generate_linear()
  generate_binary()
  generate_trie()

if __name__ == '__main__':
  sys.exit(main())
