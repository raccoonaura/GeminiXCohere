import os
import platform

class Error(Exception):
    pass

def sys_exit_for_debugging_purposes():
    raise SystemExit(0)

def clear_all():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def set_marker():
    print("\033[s", end="")

def clear_screen():
    print("\033[u", end="")
    print("\033[J", end="")