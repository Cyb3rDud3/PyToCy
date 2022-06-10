PyToCy
(( POC ONLY ))

Easy Automatic conversation from python syntax to cython syntax 

<b>./main.py --infile foo.py --compile True --> will make cython module called foo_cythonized</b>

<b>./main.py --infile foo.py --> will print the cythonized content of foo.py</b>



	Usage:
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


Notes:

         *CLASSES ARE CURRENTLY NOT SUPPORTED, SO THEY WILL REMAIN PYTHONIEZD*
	 
	 *Passing anything without type annotation --> will result in the object remaining pythonized
	 (while it still can be cythonized, it will be without any type optimizations so don't expect anything special in the performance section)*

            
