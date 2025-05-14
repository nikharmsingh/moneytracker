"""
This module suppresses specific warnings that are not relevant to the application.
Import this module at the beginning of your application to suppress these warnings.
"""

import warnings
import sys

def suppress_all_warnings():
    """Suppress all warnings."""
    if not sys.warnoptions:
        warnings.simplefilter("ignore")

def suppress_cryptography_warnings():
    """Suppress cryptography-related warnings."""
    # Suppress all deprecation warnings from pymongo
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="pymongo")
    
    # Suppress all deprecation warnings from cryptography
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="cryptography")
    
    # Specifically target naive datetime warnings
    warnings.filterwarnings("ignore", message=".*naïve datetime.*", category=Warning)
    warnings.filterwarnings("ignore", message=".*naive datetime.*", category=Warning)
    
    # Specifically target the warnings about this_update and next_update
    warnings.filterwarnings("ignore", message=".*this_update.*", category=Warning)
    warnings.filterwarnings("ignore", message=".*next_update.*", category=Warning)

# Apply the warning suppressions
suppress_cryptography_warnings()