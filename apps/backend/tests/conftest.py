"""Pytest configuration and fixtures for tests.

Suppress common warnings to keep test output clean.
"""

import logging
import sys
import warnings

# Fix Windows asyncio cleanup issues
# The asyncio module logs debug messages during event loop cleanup that
# can fail when pytest closes stdout. Suppress asyncio logging.
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    # Suppress asyncio debug logging that causes issues during pytest cleanup
    logging.getLogger("asyncio").setLevel(logging.CRITICAL)

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
