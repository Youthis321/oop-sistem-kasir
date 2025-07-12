"""
UTILS PACKAGE - Kumpulan utility classes
=======================================
Package ini berisi utility classes untuk aplikasi:
- InputUtils: Utilities untuk input handling dan validasi
- DisplayUtils: Utilities untuk output display dan formatting

Prinsip OOP yang diterapkan:
- Single Responsibility: Setiap utility punya tugas spesifik
- Strategy Pattern: Berbagai strategi untuk input dan display
- Template Method: Template untuk formatting dan validation
- Reusability: Utility yang bisa digunakan di mana saja
"""

# Import dari input_utils
from utils.input_utils import (
    InputValidator,
    IntegerValidator,
    StringValidator,
    ChoiceValidator,
    InputHandler,
    MenuHandler,
    ProgressDisplay
)

# Import dari display_utils
from utils.display_utils import (
    DisplayFormatter,
    IndonesianFormatter,
    ColorTheme,
    HeaderDisplay,
    ProductDisplay,
    CartDisplay,
    ReceiptDisplay,
    DashboardDisplay,
    MessageDisplay
)

# Define what's available when importing with "from utils import *"
__all__ = [
    # Input utilities
    'InputValidator',
    'IntegerValidator', 
    'StringValidator',
    'ChoiceValidator',
    'InputHandler',
    'MenuHandler',
    'ProgressDisplay',
    
    # Display utilities
    'DisplayFormatter',
    'IndonesianFormatter',
    'ColorTheme',
    'HeaderDisplay',
    'ProductDisplay',
    'CartDisplay',
    'ReceiptDisplay',
    'DashboardDisplay',
    'MessageDisplay'
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Kasir OOP Development Team"
__description__ = "Utility Classes untuk Aplikasi Kasir Sederhana"
