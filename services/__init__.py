"""
SERVICES PACKAGE - Kumpulan business logic services
=================================================
Package ini berisi semua service layer untuk aplikasi:
- DiscountService: Service untuk perhitungan diskon
- TaxService: Service untuk perhitungan pajak  
- ProductService: Service untuk pengelolaan produk
- TransactionService: Service untuk pengelolaan transaksi

Prinsip OOP yang diterapkan:
- Single Responsibility: Setiap service punya tanggung jawab spesifik
- Dependency Injection: Service bisa di-inject ke class lain
- Strategy Pattern: Berbagai strategi dalam setiap service
- Facade Pattern: Interface sederhana untuk operasi kompleks
"""

# Import semua service classes
from services.discount_service import (
    DiscountStrategy,
    SeniorDiscountStrategy,
    MemberDiscountStrategy,
    CategoryDiscountStrategy,
    DayOfWeekDiscountStrategy,
    DiscountService
)

from services.tax_service import (
    TaxDetail,
    TaxStrategy,
    StandardTaxStrategy,
    CategoryBasedTaxStrategy,
    LuxuryTaxStrategy,
    TaxService
)

from services.product_service import (
    ProductRepository,
    InMemoryProductRepository,
    ProductFactory,
    ProductService
)

from services.transaction_service import (
    PaymentProcessor,
    TransactionOrchestrator,
    TransactionService
)

# Define what's available when importing with "from services import *"
__all__ = [
    # Discount Service
    'DiscountStrategy',
    'SeniorDiscountStrategy',
    'MemberDiscountStrategy',
    'CategoryDiscountStrategy',
    'DayOfWeekDiscountStrategy',
    'DiscountService',
    
    # Tax Service
    'TaxDetail',
    'TaxStrategy',
    'StandardTaxStrategy',
    'CategoryBasedTaxStrategy',
    'LuxuryTaxStrategy',
    'TaxService',
    
    # Product Service
    'ProductRepository',
    'InMemoryProductRepository',
    'ProductFactory',
    'ProductService',
    
    # Transaction Service
    'PaymentProcessor',
    'TransactionOrchestrator',
    'TransactionService'
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Kasir OOP Development Team"
__description__ = "Business Logic Services untuk Aplikasi Kasir Sederhana"
