import itertools
import optparse
import pprint
import sys
import textwrap

def generate_header(haystack, hay_map):
    missing_first = haystack[0]
    while missing_first in hay_map:
        missing_first = '_' + missing_first

    missing_last = haystack[-1]
    while missing_last in hay_map:
        missing_last = missing_last + '~'

    print textwrap.dedent("""
    use std::cmp::Ordering;

    pub static HAYSTACK: &'static [(&'static str, usize)] = &[%s];
    pub static MISSING_FIRST: &'static str = "%s";
    pub static MISSING_LAST: &'static str = "%s";
    """ % (
        ','.join('("%s", %s)' % (hay, hay_map[hay]) for hay in haystack),
        missing_first,
        missing_last,
    ))

# ------------------------------------------------------------------------------

def generate_match(haystack, hay_map):
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

def generate_linear(haystack, hay_map):
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

def walk_binary(haystack, hay_map, fn, start, end, indent=0):
    if start == end:
        return ""

    index = (end + start) // 2
    spaces = ' ' * indent

    less = walk_binary(haystack, hay_map, fn, start, index, indent=indent + 8)
    if less:
        less = '{\n%s\n%s}' % (less, spaces + ' ' * 4)
    else:
        less = '{ }'

    greater = walk_binary(haystack, hay_map, fn, index + 1, end, indent=indent + 8)
    if greater:
        greater = '{\n%s\n%s}' % (greater, spaces + ' ' * 4)
    else:
        greater = '{ }'

    hay = haystack[index]

    lines = [
        'match %s(needle, "%s") {' % (fn, hay),
        '    Ordering::Less => %s' % less,
        '    Ordering::Equal => { return %s; }' % hay_map[hay],
        '    Ordering::Greater => %s' % greater,
        '}',
    ]

    return '\n'.join('%s%s' % (spaces, line) for line in lines)

def generate_binary(haystack, hay_map):
    haystack = sorted(haystack)

    print textwrap.dedent("""
    //#[no_mangle]
    #[inline(never)]
    pub fn binary_search(needle: &str) -> usize {""")
    print walk_binary(haystack, hay_map, 'str::cmp', 0, len(haystack), 4)
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


def generate_trie(haystack, hay_map):
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

def calculate_frequency(): pass

def main():
    parser = optparse.OptionParser()
    parser.add_option('--sort',
            action='store_true',
            default=False,
            help='sort the keywords')
    parser.add_option('--sort-by-frequency',
            action='store',
            help='sort the keywords by frequency occurring in this file')
    parser.add_option('--reverse',
            action='store_true',
            default=False,
            help='reverse sort keywords')

    (options, args) = parser.parse_args()

    if len(args) != 1:
        print 'did not specify haystack'
        return 1

    haystack_filename = args[0]

    if options.sort and options.sort_by_frequency:
        print '--sort and --sort-by-frequency are incompatible'
        return 1

    with open(haystack_filename) as f:
        haystack = [line for line in f.read().split('\n') if line != '']

    if options.sort:
        haystack.sort(reverse=options.reverse)
    elif options.sort_by_frequency:
        frequency = {}
        for hay in haystack:
            frequency[hay] = 0

        with open(options.sort_by_frequency) as f:
            words = f.read().split(' ')

        for word in words:
            try:
                frequency[word] += 1
            except KeyError:
                pass

        haystack = [hay for count, hay in
            sorted(((count, hay) for hay, count in frequency.iteritems()),
                reverse=not options.reverse)
        ]

    hay_map = {}
    for i, hay in enumerate(sorted(haystack)):
        hay_map[hay] = i

    generate_header(haystack, hay_map)
    generate_match(haystack, hay_map)
    generate_linear(haystack, hay_map)
    generate_binary(haystack, hay_map)
    generate_trie(haystack, hay_map)

if __name__ == '__main__':
    sys.exit(main())
