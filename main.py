import ast
import argparse
Name,parse = ast.Name, ast.parse
parser = argparse.ArgumentParser()
parser.add_argument("--infile", type=str,required=True)
parser.add_argument('-c',"--compile")

args = parser.parse_args()
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



class _Unparser(ast._Unparser):
    def __init__(self,*, _avoid_backslashes=False, should_cythonize=False):
        ast._Unparser.__init__(self,)
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



def unparse(ast_obj):
    unparser = _Unparser(should_cythonize=True)
    return unparser.visit(ast_obj)

def make_code(code):
    code = parse(code)
    return unparse(code)

def load_code_from_file(file: str) -> str:
    try:
        with open(file, 'r') as f:
            return f.read()
    except Exception as e:
        print(e)
        return ''

def main():
    source_code = load_code_from_file(args.infile)
    if not source_code:
        print('unknown error')
        exit()
    source_code = make_code(source_code)
    if args.compile:
        if args.infile.endswith('.pyx'):
            file = args.infile.replace('.pyx','_cythonized.pyx')
        elif args.infile.endswith('.py'):
            file = args.infile.replace('.py','_cythonized.pyx')
        else:
            file = args.infile + '_cythonized.pyx'
        print(file)
        with open(file, 'w') as to_cython_file:
            to_cython_file.write(source_code)
        from setuptools import setup,sandbox
        from Cython.Build import cythonize
        from Cython.Distutils import build_ext
        setup(ext_modules=cythonize(file,language_level = "3"), script_args=["build_ext", "--inplace"],cmdclass={'build_ext': build_ext})
        print('[*] Finished Compiling of {}, You can import your functions from {}. \n Example: from {} import Foo'.format(args.infile.replace('\\','').replace('/','').replace('.py','').replace('.',''), file.replace('.pyx', '').replace('\\','').replace('/','').replace('.',''),file.replace('.pyx','').replace('\\','').replace('/','').replace('.','')))
    else:
        print(source_code)




if __name__ == "__main__":
    main()
