#!/usr/bin/env python3
"""Test script to verify setup"""

print("Testing imports...")

try:
    import flask
    print("[OK] Flask imported")
except ImportError:
    print("[ERROR] Flask not found - run: pip install flask")

try:
    import sentence_transformers
    print("[OK] Sentence Transformers imported")
except ImportError:
    print("[ERROR] Sentence Transformers not found - run: pip install sentence-transformers")

try:
    import transformers
    print("[OK] Transformers imported")
except ImportError:
    print("[ERROR] Transformers not found - run: pip install transformers")

try:
    import torch
    print("[OK] PyTorch imported")
except ImportError:
    print("[ERROR] PyTorch not found - run: pip install torch")

try:
    import language_tool_python
    print("[OK] LanguageTool imported")
except ImportError:
    print("[ERROR] LanguageTool not found - run: pip install language-tool-python")

try:
    import numpy
    print("[OK] NumPy imported")
except ImportError:
    print("[ERROR] NumPy not found - run: pip install numpy")

try:
    import sklearn
    print("[OK] Scikit-learn imported")
except ImportError:
    print("[ERROR] Scikit-learn not found - run: pip install scikit-learn")

print("\nTesting data import...")
try:
    from data import SAMPLE_PARAGRAPHS
    print(f"[OK] Data imported - {len(SAMPLE_PARAGRAPHS)} paragraphs available")
except ImportError as e:
    print(f"[ERROR] Data import failed: {e}")

print("\nSetup test complete!")