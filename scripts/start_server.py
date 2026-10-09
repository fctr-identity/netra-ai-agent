"""Compatibility launcher; the local entry point is python main.py."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[1] / 'main.py'), run_name='__main__')
