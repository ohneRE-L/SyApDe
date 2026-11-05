"""
Application commands package.

Re-exports stdlib `cmd.Cmd` to avoid shadowing issues with pdb/pytest on Windows.
"""

import sys
import os
import importlib.machinery

try:
    for p in sys.path:
        if p and p != "." and "lab1" not in p:
            candidate = os.path.join(p, "cmd.py")
            if os.path.isfile(candidate):
                _loader = importlib.machinery.SourceFileLoader("_stdlib_cmd", candidate)
                _mod = _loader.load_module()
                Cmd = getattr(_mod, "Cmd", None)
                IDENTCHARS = getattr(_mod, "IDENTCHARS", None)
                PROMPT = getattr(_mod, "PROMPT", None)
                break
except Exception:
    pass
