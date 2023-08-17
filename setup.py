import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": ["os","pygame","inspect","random"], "include_files":["ressources", "Ressources Kaiser","Kaiser.py","Outils.py"]}

# GUI applications require a different base on Windows (the default is for a
# console application).

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "Tetris",
        version = "1.0",
        description = "Tetris adapté de X 2019 MP/PC",
        options = {"build_exe": build_exe_options},
        executables = [Executable("Tetris.py", base=base)])