from ast import NodeVisitor, Name

# file to edit == $PYTHON/Lib/ast.py
# add the next section at the top of the file, after the imports
KNOWN_CYTHON_TYPES = {"bool": "bint",
                      "int": "int",
                      "float": "float",
                      "object": "object",
                      "str": "str",
                      "Any": "object",
                      "List": "list",
                      "Dict": "dict",
                      "list": "list",
                      "dict": "dict",
                      "bytes": "bytes"}


# from here, all the next sections are methods of _Unparser Class. replace them.
class _Unparser(NodeVisitor):
    """Methods in this class recursively traverse an AST and
    output source code for the abstract syntax; original formatting
    is disregarded."""

    def __init__(self, *, _avoid_backslashes=False, should_cythonize=False):
        self._source = []
        self._buffer = []
        self._precedences = {}
        self._type_ignores = {}
        self._indent = 0
        self._avoid_backslashes = _avoid_backslashes
        self.cython = should_cythonize

    def fill(self, text="", is_cython=False):
        """Indent a piece of text and append it, according to the current
        indentation level"""
        if not is_cython:
            self.maybe_newline()
            self.write("    " * self._indent + text)
        else:
            self.write(text)

    def visit_AnnAssign(self, node):
        if not self.cython:
            self.fill()
            with self.delimit_if("(", ")", not node.simple and isinstance(node.target, Name)):
                self.traverse(node.target)
            self.write(": ")
            self.traverse(node.annotation)
            if node.value:
                self.write(" = ")
                self.traverse(node.value)
        else:
            self.fill()
            if not KNOWN_CYTHON_TYPES.get(node.annotation.id):
                for key, value in KNOWN_CYTHON_TYPES.items():
                    if node.annotation.id in key:
                        node.annotation.id = value
                        break
            with self.delimit_if("(", ")", not node.simple and isinstance(node.target, Name)):
                self.write('cdef ')
                self.traverse(node.annotation)
                self.write(' ')
                self.traverse(node.target)
            if node.value:
                self.write(" = ")
                self.traverse(node.value)

    def _function_helper(self, node, fill_suffix):
        if not self.cython or not node.returns:
            self.maybe_newline()
            for deco in node.decorator_list:
                self.fill("@")
                self.traverse(deco)
            def_str = fill_suffix + " " + node.name
            self.fill(def_str)
            with self.delimit("(", ")"):
                self.traverse(node.args)
            if node.returns:
                self.write(" -> ")
                self.traverse(node.returns)
            with self.block(extra=self.get_type_comment(node)):

                self._write_docstring_and_traverse_body(node)
        else:
            if not KNOWN_CYTHON_TYPES.get(node.returns.id):
                for key, value in KNOWN_CYTHON_TYPES.items():
                    if node.returns.id in key:
                        node.returns.id = value
                        break
            else:
                node.returns.id = KNOWN_CYTHON_TYPES[node.returns.id]
            if len(node.decorator_list) == 1:
                if node.decorator_list[0].id == 'cdef':
                    node.decorator_list.pop()
                    fill_suffix = 'cdef'
            else:
                fill_suffix = 'cpdef'
            self.maybe_newline()
            for deco in node.decorator_list:
                self.fill("@")
                self.traverse(deco)
            def_str = fill_suffix + " " + node.returns.id + " " + node.name
            self.fill(def_str)
            with self.delimit("(", ")"):
                to_add = ""
                for _arg in node.args.args:
                    if not KNOWN_CYTHON_TYPES.get(_arg.annotation.id):
                        for key, value in KNOWN_CYTHON_TYPES.items():
                            if _arg.annotation.id in key:
                                _arg.annotation.id = value
                                break
                    else:
                        _arg.annotation.id = KNOWN_CYTHON_TYPES[_arg.annotation.id]
                    if _arg.annotation.end_col_offset + 1 in [i.col_offset for i in node.args.defaults]:
                        to_add += f"{_arg.annotation.id} {_arg.arg}={''.join([str(i.value) for i in node.args.defaults if i.col_offset == _arg.annotation.end_col_offset + 1])},"
                    else:
                        to_add += f"{_arg.annotation.id} {_arg.arg},"
                to_add = to_add.rstrip(',').lstrip('\n')
                self.fill(to_add, is_cython=True)
            with self.block(extra=self.get_type_comment(node)):
                self._write_docstring_and_traverse_body(node)
