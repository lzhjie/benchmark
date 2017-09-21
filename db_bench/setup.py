from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import cython
extensions = [
    Extension("DbBench", ["DbBench.py"]),
    Extension("DbBenchCython", ["DbBenchCython.pyx"])
]
setup(
    name="db benchmark",
    ext_modules=cythonize(extensions),
    author_email="l.zhjie@qq.com"
)
