from subprocess import check_output
import os

def digest_file(fname):
    output = check_output([
        'openssl',
        'dgst',
        '-sha256',
        fname,
    ])

    return output.split(' ')[1][:-1]


def string_for_tree(tree, lvl = 0):
    out = "| " * ((lvl - 2) / 2)

    if (lvl != 0):
        out += "|-"

    out += tree.key() + "\n"

    for child in tree.children():
        out += string_for_tree(child, lvl + 2)

    return out

class Tree:
    def __init__(self, key):
        self._key = key
        self._children = {}

    def __str__(self):
        return string_for_tree(self)

    def key(self):
        return self._key

    def add_child(self, key):
        child = Tree(key)
        self._children[key] = child

        return child

    def child_for(self, key):
        return self._children[key]

    def has_children(self):
        return len(self._children) > 0

    def children(self):
        return [ self.child_for(key) for key in self._children ]

    def leaf_count(self):
        if not self.has_children():
            return 1

        leaf_count = 0

        for child in self.children():
            leaf_count += child.leaf_count()

        return leaf_count

def manifest(root):
    org_dir = os.getcwd()
    os.chdir(root)

    ret = build_manifest(Tree('./'))

    os.chdir(org_dir)

    return ret

def build_manifest(tree):
    for root, subdirs, files in os.walk(tree.key()):
        for file in files:
            fpath = os.path.join(root, file)
            digest = digest_file(fpath)
            tree.add_child(file + ' ' + digest)

        for subdir in subdirs:
            build_manifest(tree.add_child(os.path.join(root, subdir)))

        break

    return tree

if __name__ == '__main__':
    treeA = manifest('./test/A/')
    treeB = manifest('./test/B/')

    print treeA
    print treeB
