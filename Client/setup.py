import sys
from distutils.core import setup
py2exe_path = r"C:\Python27\Lib\site-packages"
if py2exe_path not in sys.path:
    sys.path.append(py2exe_path)
    import py2exe

setup(console=['GUI.py'])