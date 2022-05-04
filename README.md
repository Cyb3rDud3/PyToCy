PyToCy
(( POC ONLY ))

Easy Automatic conversation if python syntax to cython syntax [[ POC ]]

Usage:
    install:
        replace the methods at $PYTHON/Lib/ast.py with those in our local ast_to_rep.py

    usage:
        use basic-lib type annotations to "cythonize" a section.
        section without type annotation will not be cythonized.
        example:
            x = 5 --> remain x = 5
            x: int = 5 --> cdef int x = 5
            _____________________________
            def add(a: int, b: int) -> int:
                res: int = a + b
                return res
            --> will become
            cpdef int add(int a,int b):
                cdef int res = a + b
                return res
            ______________________________
            want cdef instead of cpdef? just pass @cdef as decorator for function.
            @cdef
            def add(a: int, b: int) -> int:
                res: int = a + b
                return res
            --> will become
            cdef int add(int a,int b):
                cdef int res = a + b
                return res

            ______________________________


            *CLASSES ARE CURRENTLY NOT SUPPORTED*

            from ast import unparse,parse
            code = """ your_py_code_here """
            res = unparse(parse(code),should_cythonize=True)
            #put res in file that end's with *.pyx*, and cythonize/cython it.
