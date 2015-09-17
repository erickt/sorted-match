import collections
import itertools
import optparse
import pprint
import sys
import textwrap

def generate_header(haystack, hay_map):
    missing_first = haystack[0]
    while missing_first in hay_map:
        missing_first = ' ' + missing_first

    missing_last = haystack[-1]
    while missing_last in hay_map:
        missing_last = missing_last + '~'

    print textwrap.dedent("""
    use std::cmp::Ordering;
    use std::slice;

    pub static HAYSTACK: &'static [(&'static str, usize)] = &[%s];
    pub static MISSING_FIRST: &'static str = "%s";
    pub static MISSING_LAST: &'static str = "%s";

    #[allow(dead_code)]
    #[inline]
    unsafe fn slice_from_unchecked(slice: &[u8], pos: usize) -> &[u8] {
        let ptr = slice.as_ptr();
        let len = slice.len();
        slice::from_raw_parts(ptr.offset(pos as isize), len - pos)
    }

    #[allow(dead_code)]
    #[inline]
    unsafe fn split_at_unchecked(slice: &[u8], pos: usize) -> (&[u8], &[u8]) {
        let ptr = slice.as_ptr();
        let len = slice.len();
        (
            slice::from_raw_parts(ptr, pos),
            slice::from_raw_parts(ptr.offset(pos as isize), len - pos),
        )
    }

    #[allow(dead_code)]
    #[inline]
    unsafe fn eq_slice_unchecked(a: &[u8], b: &[u8]) -> bool {
        memcmp(a, b, a.len()) == 0
    }

    #[allow(dead_code)]
    #[inline]
    unsafe fn cmp_slice_unchecked(a: &[u8], b: &[u8]) -> Ordering {
        let cmp = memcmp(a, b, a.len());
        if cmp == 0 { Ordering::Equal }
        else if cmp < 0 { Ordering::Less }
        else { Ordering::Greater }
    }

    #[allow(dead_code)]
    #[inline]
    unsafe fn memcmp(a: &[u8], b: &[u8], len: usize) -> i32 {
        // NOTE: In theory n should be libc::size_t and not usize, but libc is not available here
        #[allow(improper_ctypes)]
        extern { fn memcmp(s1: *const i8, s2: *const i8, n: usize) -> i32; }
        memcmp(a.as_ptr() as *const i8, b.as_ptr() as *const i8, len)
    }
    """ % (
        ','.join('("%s", %s)' % (hay, hay_map[hay]) for hay in haystack),
        missing_first,
        missing_last,
    ))

# ------------------------------------------------------------------------------

def generate_match(haystack, hay_map):
    print textwrap.dedent("""
    #[inline]
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
    #[inline]
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

def group_by_len(haystack):
    d = {}
    for hay in haystack:
        try:
            hays = d[len(hay)]
        except KeyError:
            hays = d[len(hay)] = []

        hays.append(hay)

    return sorted(d.iteritems(), lambda a, b: cmp(a[0], b[0]))

def generate_linear_len(haystack, hay_map):
    print textwrap.dedent("""
    #[inline]
    pub fn linear_len_search(needle: &str) -> usize {
        let needle = needle.as_bytes();

        match needle.len() {""")


    for length, hays in group_by_len(haystack):
        print '        %s => {' % length

        first = True
        for hay in hays:
            if first:
                first = False
                print '            if unsafe { eq_slice_unchecked(needle, b"%s") } { return %s; }' % (hay, hay_map[hay])
            else:
                print '            else if unsafe { eq_slice_unchecked(needle, b"%s") } { return %s; }' % (hay, hay_map[hay])

        print '        }'

    print '        _ => { }'
    print '    }'
    print '    %s' % len(haystack)
    print '}'

# ------------------------------------------------------------------------------

def walk_binary(haystack, hay_map, fn, start, end, indent=0, use_bytes=False, use_ord=True):
    if start == end:
        return ""

    index = (end + start) // 2
    spaces = ' ' * indent

    less = walk_binary(haystack, hay_map, fn, start, index, indent=indent + 8, use_bytes=use_bytes, use_ord=use_ord)
    if less:
        less = '{\n%s\n%s}' % (less, spaces + ' ' * 4)
    else:
        less = '{ }'

    greater = walk_binary(haystack, hay_map, fn, index + 1, end, indent=indent + 8, use_bytes=use_bytes, use_ord=use_ord)
    if greater:
        greater = '{\n%s\n%s}' % (greater, spaces + ' ' * 4)
    else:
        greater = '{ }'

    hay = haystack[index]

    if use_bytes:
      h = 'b"%s"' % hay
    else:
      h = '"%s"' % hay

    if use_ord:
      lines = [
          'match %s(needle, %s) {' % (fn, h),
          '    Ordering::Less => %s' % less,
          '    Ordering::Equal => { return %s; }' % hay_map[hay],
          '    Ordering::Greater => %s' % greater,
          '}',
      ]
    else:
      lines = [
          'let cmp = memcmp(needle, %s, %s);' % (h, len(hay)),
          'if cmp < 0 %s' % less,
          'else if cmp == 0 { return %s; }' % hay_map[hay],
          'else %s' % greater,
      ]


    return '\n'.join('%s%s' % (spaces, line) for line in lines)

def generate_binary(haystack, hay_map):
    haystack = sorted(haystack)

    print textwrap.dedent("""
    #[inline]
    pub fn binary_search(needle: &str) -> usize {""")
    print walk_binary(haystack, hay_map, 'str::cmp', 0, len(haystack), 4)
    print '    %s' % len(haystack)
    print '}'

def generate_binary_len(haystack, hay_map):
    print textwrap.dedent("""
    #[inline]
    pub fn binary_len_search(needle: &str) -> usize {
        let needle = needle.as_bytes();
        unsafe {
            match needle.len() {""")

    for length, hays in group_by_len(haystack):
        hays.sort()

        print '            %s => {' % length
        print walk_binary(hays, hay_map, 'cmp_slice_unchecked', 0, len(hays), 16, use_bytes=True, use_ord=False)
        print '            }'

    print '        _ => { }'
    print '        }'
    print '    }'
    print '    %s' % len(haystack)
    print '}'

# ------------------------------------------------------------------------------

class Trie(object):
    def __init__(self):
        self.roots = {}

    def insert(self, key, value):
        chars = list(key)
        chars.reverse()

        try:
            root = self.roots[len(chars)]
        except KeyError:
            root = self.roots[len(chars)] = TrieNode()

        root.insert(chars, value)

    def walk(self):
        lines = []
        roots = sorted(self.roots.iteritems(), lambda a, b: cmp(a[0], b[0]))
        assert len(roots) > 0

        if len(roots) > 1:
            lines.append('    match needle.len() {')
            for length, root in roots:
                lines.append('        %s => {' % (length,))
                lines.append(root.walk(12))
                lines.append('        }')

            lines.extend([
                '        _ => { }',
                '    }',
            ])
        else:
            length, root = roots[0]
            lines.append('    if needle.len() == %s {' % (length,))
            lines.append(root.walk(4))
            lines.append('    }')

        return '\n'.join(lines)

    def print_trie(self):
        for i, (length, root) in enumerate(sorted(self.roots.iteritems(), lambda a, b: cmp(a[0], b[0]))):
            if i == 0:
                prefix = '+'
            else:
                prefix = '|'
            print '%s%s' % (prefix, length)
            root.print_trie(2)

    def compress(self):
        for root in self.roots.itervalues():
            root.compress(0)

class TrieNode(object):
    def __init__(self):
        self.value = None
        self.children = collections.OrderedDict()

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
        spaces = ' ' * depth
        length = len(next(self.children.iterkeys()))
        assert length >= 1

        lines = []

        if any(child.children for child in self.children.itervalues()):
            if length == 1:
                lines.append(
                    '%s    let (prefix, needle) = unsafe { (*needle.get_unchecked(0), slice_from_unchecked(needle, 1)) };' % (spaces,),
                )
            else:
                lines.append(
                    '%s    let (prefix, needle) = unsafe { split_at_unchecked(needle, %s) };' % (spaces, length)
                )

            if length == 1:
                lines.append(
                    '%s    match prefix {' % (spaces,)
                )

                for key, child in sorted(self.children.iteritems()):
                    assert len(key) == 1

                    s = [spaces + '        ']

                    s.append("b'%s'" % key)
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
            else:
                assert len(self.children) == 1

                key, child = next(self.children.iteritems())

                lines.append(
                    '%s    if unsafe { eq_slice_unchecked(prefix, b"%s") } {' % (spaces, key)
                )

                if child.value is not None:
                    lines.append('%s        if needle.is_empty() { return %s; }' % (spaces, child.value))

                    if child.children:
                        lines.append(child.walk(depth + 8))
                else:
                    lines.append(child.walk(depth + 8))

                lines.append(
                    '%s    }' % (spaces,)
                )
        elif length == 1:
            if length == 1:
                lines.append(
                    '%s    let needle = unsafe { *needle.get_unchecked(0) };' % (spaces,)
                )

            lines.append(
                '%s    match needle {' % (spaces,)
            )

            for key, child in sorted(self.children.iteritems()):
                assert not child.children
                assert child.value is not None
                assert len(key) == 1

                s = [spaces + '        ']

                s.append("b'%s'" % key)
                s.append(' => { return %s; }' % (child.value,))
                lines.append(''.join(s))

            lines.extend([
                '%s        _ => { }' % (spaces,),
                '%s}' % (spaces,),
            ])
        else:
            assert len(self.children) == 1

            key, child = next(self.children.iteritems())
            assert child.value is not None

            # we could have multiple children
            lines.append(
                '%sif unsafe { eq_slice_unchecked(needle, b"%s") } { return %s; }' % (spaces, key, child.value)
            )

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

    #trie.print_trie()
    #return

    print textwrap.dedent("""
    #[inline]
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
    generate_linear_len(haystack, hay_map)
    generate_binary(haystack, hay_map)
    generate_binary_len(haystack, hay_map)
    generate_trie(haystack, hay_map)

if __name__ == '__main__':
    sys.exit(main())
