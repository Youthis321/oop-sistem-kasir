"""
MODELS PACKAGE - Kumpulan model/entity untuk aplikasi kasir
=========================================================
Package ini berisi semua model yang digunakan dalam aplikasi:
- Product: Model untuk barang/produk
- Customer: Model untuk pelanggan (regular, premium, VIP)
- Cart: Model untuk keranjang belanja
- Transaction: Model untuk transaksi

Prinsip OOP yang diterapkan:
- Encapsulation: Data ter-encapsulasi dengan getter/setter
- Inheritance: Hierarki class customer dan product
- Polymorphism: Method yang di-override untuk behavior berbeda
- Abstraction: Abstract base class dan interface
"""

# Import semua class yang akan digunakan secara public
from models.product import (
    KategoriBarang,
    BaseProduct, 
    Product,
    ProductItem
)

from models.customer import (
    BaseCustomer,
    Customer,
    PremiumCustomer,
    VIPCustomer
)

from models.cart import (
    ShoppingCart,
    CartManager
)

from models.transaction import (
    TransactionStatus,
    DiscountDetail,
    PaymentDetail,
    Transaction,
    TransactionBuilder
)

# Define what's available when importing with "from models import *"
__all__ = [
    # Product classes
    'KategoriBarang',
    'BaseProduct',
    'Product', 
    'ProductItem',
    
    # Customer classes
    'BaseCustomer',
    'Customer',
    'PremiumCustomer', 
    'VIPCustomer',
    
    # Cart classes
    'ShoppingCart',
    'CartManager',
    
    # Transaction classes
    'TransactionStatus',
    'DiscountDetail',
    'PaymentDetail',
    'Transaction',
    'TransactionBuilder'
]

# Package metadata
__version__ = "1.0.0"
__author__ = "Kasir OOP Development Team"
__description__ = "OOP Models untuk Aplikasi Kasir Sederhana"
