#=======================================================================
# Copyright Nicholas Tuckett 2015.
# Distributed under the MIT License.
# (See accompanying file license.txt or copy at
#  http://opensource.org/licenses/MIT)
#=======================================================================

BACKGROUND_COLOUR   = "background-colour"
BORDER_COLOUR       = "border-colour"
BORDER_WIDTH        = "border-width"
FONT                = "font"
TEXT_COLOUR         = "text-colour"
HIGHLIGHT_COLOUR    = "highlight-colour"

import collections


class Style(collections.MutableMapping):
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        if self.parent == None or self.store.has_key(key):
            return self.store[key]
        else:
            return self.parent[key]

    def __setitem__(self, key, value):
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        for x in self.store.keys() + self.parent.keys():
            yield x

    def __len__(self):
        return len(self.store) + len(parent)
