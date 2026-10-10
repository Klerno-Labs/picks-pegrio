#!/usr/bin/env python3
"""Validate static pages. The retired copy generator remains in git history."""
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).resolve().parent / 'scripts/validate.py'), run_name='__main__')
