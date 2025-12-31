import os
import platform

class Error(Exception):
    pass

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