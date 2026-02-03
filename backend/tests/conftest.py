"""Pytest configuration and fixtures for tests.

Suppress common warnings to keep test output clean.
"""

import warnings

# Suppress specific deprecation warnings
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*datetime.datetime.utcnow.*"
)
warnings.filterwarnings(
    "ignore",
    category=DeprecationWarning,
    message=".*The 'app' shortcut is now deprecated.*",
)
warnings.filterwarnings(
    "ignore", category=DeprecationWarning, message=".*default datetime adapter.*"
)
