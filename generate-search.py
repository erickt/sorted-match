import itertools
import optparse
import pprint
import sys
import textwrap

#prefixes = sys.argv[1].split(',')
#count = int(sys.argv[2])

#haystack_template = list(
#        'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
#        'abcdefghijklmnopqrstuvwxyz')

#haystack_template = [
#    "self",
#    "static",
#    "super",
#    "tt",
#    "matchers",
#    "__rust_abi",
#    "<opaque>",
#    "<unnamed_field>",
#    "Self",
#    "prelude_import",
#    "as",
#    "break",
#    "crate",
#    "else",
#    "enum",
#    "extern",
#    "false",
#    "fn",
#    "for",
#    "if",
#    "impl",
#    "in",
#    "let",
#    "loop",
#    "match",
#    "mod",
#    "move",
#    "mut",
#    "pub",
#    "ref",
#    "return",
#    "struct",
#    "true",
#    "trait",
#    "type",
#    "unsafe",
#    "use",
#    "virtual",
#    "while",
#    "continue",
#    "box",
#    "const",
#    "where",
#    "proc",
#    "alignof",
#    "become",
#    "offsetof",
#    "priv",
#    "pure",
#    "sizeof",
#    "typeof",
#    "unsized",
#    "yield",
#    "do",
#    "abstract",
#    "final",
#    "override",
#    "macro",
#]

haystack_template = [
    "pub",
    "fn",
    "for",
    "type",
    "let",
    "match",
    "if",
    "in",
    "as",
    "struct",
    "return",
    "use",
    "trait",
    "else",
    "mut",
    "where",
    "enum",
    "const",
    "ref",
    "do",
    "impl",
    "true",
    "Self",
    "self",
    "while",
    "unsafe",
    "yield",
    "mod",
    "box",
    "abstract",
    "move",
    "false",
    "crate",
    "final",
    "static",
    "become",
    "matchers",
    "offsetof",
    "typeof",
    "break",
    "alignof",
    "<opaque>",
    "override",
    "priv",
    "prelude_import",
    "<unnamed_field>",
    "tt",
    "continue",
    "extern",
    "macro",
    "unsized",
    "pure",
    "virtual",
    "super",
    "loop",
    "sizeof",
    "proc",
    "__rust_abi",
]

prefixes = ['']
count = len(haystack_template)

haystack = []

for i, c in enumerate(itertools.cycle(haystack_template)):
    if i >= count:
        break

    prefix = prefixes[i % len(prefixes)]
    haystack.append(prefix + c)


sorted_haystack = sorted(haystack)
hay_map = {}

for i, hay in enumerate(sorted_haystack):
    hay_map[hay] = i


def generate_header():
    print textwrap.dedent("""
    use std::cmp::Ordering;

    pub static HAYSTACK: &'static [&'static str] = &[%s];
    """ % ','.join('"%s"' % hay for hay in sorted_haystack))

# ------------------------------------------------------------------------------

def generate_match():
    print textwrap.dedent("""
    #[no_mangle]
    #[inline(never)]
    pub fn match_search(needle: &str) -> usize {
        match needle {""")

    for hay in haystack:
        print '        "%s" => %s,' % (hay, hay_map[hay])

    print '        _ => %s' % len(haystack)
    print '    }'
    print '}'

# ------------------------------------------------------------------------------

def generate_linear():
    print textwrap.dedent("""
    //#[no_mangle]
    #[inline(never)]
    pub fn linear_search(needle: &str) -> usize {""")

    first = True
    for hay in haystack:
        if first:
            first = False
            print '    if needle == "%s" { %s }' % (hay, hay_map[hay])
        else:
            print '    else if needle == "%s" { %s }' % (hay, hay_map[hay])

    print '    else { %s }' % len(haystack)
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

    hay = sorted_haystack[index]

    lines = [
        'match %s(needle, "%s") {' % (fn, hay),
        '    Ordering::Less => %s' % less,
        '    Ordering::Equal => { return %s; }' % hay_map[hay],
        '    Ordering::Greater => %s' % greater,
        '}',
    ]

    return '\n'.join('%s%s' % (spaces, line) for line in lines)

def generate_binary():
    print textwrap.dedent("""
    //#[no_mangle]
    #[inline(never)]
    pub fn binary_search(needle: &str) -> usize {""")
    print walk_binary('str::cmp', 0, len(haystack), 4)
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

    for hay in haystack:
        trie.insert(hay, hay_map[hay])

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
