from subprocess import check_output
from tqdm import tqdm
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
    def __init__(self, key, category = "directory"):
        self._key = key
        self._children = {}
        self._category = category

        self._digest = None

    def __str__(self):
        return string_for_tree(self)

    def category(self):
        return self._category

    def key(self):
        return self._key

    def add_child(self, key, category = "directory"):
        child = Tree(key, category)
        self._children[key] = child

        return child

    def child_for(self, key):
        return self._children[key]

    def has_children(self):
        return len(self._children) > 0

    def children(self):
        return [ self.child_for(key) for key in self._children ]

    def build_digest(self, progress_fn = lambda: None):
        if self.category() == "file":
            progress_fn(self.key())
            self._digest = digest_file(self.key())

        for child in self.children():
            child.build_digest(progress_fn)

    def file_count(self):
        if self.category() == "file":
            return 1

        if not self.has_children():
            return 0

        leaf_count = 0

        for child in self.children():
            leaf_count += child.leaf_count()

        return leaf_count

    def leaf_count(self):
        if not self.has_children():
            return 1

        leaf_count = 0

        for child in self.children():
            leaf_count += child.leaf_count()

        return leaf_count

def manifest(root):
    ret = build_manifest(Tree(root))

    return ret

def build_manifest(tree):
    for root, subdirs, files in os.walk(tree.key()):
        for file in files:
            fpath = os.path.join(root, file)
            tree.add_child(fpath, "file")

        for subdir in subdirs:
            build_manifest(tree.add_child(os.path.join(root, subdir)))

        break

    return tree

if __name__ == '__main__':
    treeA = manifest('/Users/speleo/Documents/Programs/python')

    with tqdm(total=treeA.file_count(), unit='files') as pbar:
        def progress_fn(fname):
            pbar.update(1)

        treeA.build_digest(progress_fn)
