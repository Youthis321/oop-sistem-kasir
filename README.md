# 🏪 Kasir Toko Kelontong - OOP Version

Implementasi lengkap aplikasi kasir menggunakan prinsip-prinsip Object-Oriented Programming (OOP) dengan Python.

## 📋 Daftar Isi

- [Gambaran Umum](#gambaran-umum)
- [Prinsip OOP yang Diterapkan](#prinsip-oop-yang-diterapkan)
- [Struktur Aplikasi](#struktur-aplikasi)
- [Fitur Utama](#fitur-utama)
- [Instalasi](#instalasi)
- [Cara Penggunaan](#cara-penggunaan)
- [Dokumentasi API](#dokumentasi-api)
- [Contoh Penggunaan](#contoh-penggunaan)

## 🎯 Gambaran Umum

Aplikasi kasir ini adalah upgrade dari versi prosedural sebelumnya, dibangun dengan arsitektur OOP yang solid. Aplikasi ini mengelola transaksi penjualan dengan fitur:

- **Manajemen Customer** (Regular, Premium, VIP)
- **Katalog Produk** dengan kategori
- **Sistem Diskon** berlapis (member, lansia, kategori, hari)
- **Sistem Pajak** yang fleksibel
- **Keranjang Belanja** dengan state management
- **Transaksi & Receipt** yang lengkap
- **Analytics & Reporting**

## 🏗️ Prinsip OOP yang Diterapkan

### 1. **Encapsulation** 🔒
```python
class Product:
    def __init__(self, nama: str, harga: int, satuan: str, kategori: KategoriBarang):
        # Private attributes
        self._nama = nama.strip().lower()
        self._harga = harga
        self._satuan = satuan.strip().lower()
        self._kategori = kategori
    
    @property
    def nama(self) -> str:
        """Getter untuk nama barang"""
        return self._nama
```

### 2. **Inheritance** 🧬
```python
class Customer(BaseCustomer):
    # Base customer implementation
    pass

class PremiumCustomer(Customer):
    # Extended customer with premium features
    pass

class VIPCustomer(PremiumCustomer):
    # Multi-level inheritance
    pass
```

### 3. **Polymorphism** 🔄
```python
class DiscountStrategy(ABC):
    @abstractmethod
    def calculate_discount(self, cart: ShoppingCart, customer: BaseCustomer) -> DiscountDetail:
        pass

class SeniorDiscountStrategy(DiscountStrategy):
    def calculate_discount(self, cart: ShoppingCart, customer: BaseCustomer) -> DiscountDetail:
        # Implementation untuk diskon lansia
        pass

class MemberDiscountStrategy(DiscountStrategy):
    def calculate_discount(self, cart: ShoppingCart, customer: BaseCustomer) -> DiscountDetail:
        # Implementation untuk diskon member
        pass
```

### 4. **Abstraction** 🎭
```python
class BaseCustomer(ABC):
    @abstractmethod
    def get_discount_multiplier(self) -> float:
        pass
    
    @abstractmethod
    def get_customer_type(self) -> str:
        pass
```

## 📁 Struktur Aplikasi

```
oop-kasir/
│
├── models/                     # 📦 Data Models & Entities
│   ├── __init__.py
│   ├── product.py             # Product, ProductItem, KategoriBarang
│   ├── customer.py            # Customer, PremiumCustomer, VIPCustomer
│   ├── cart.py                # ShoppingCart, CartManager
│   └── transaction.py         # Transaction, TransactionBuilder
│
├── services/                   # 🔧 Business Logic Services
│   ├── __init__.py
│   ├── discount_service.py    # Discount calculation strategies
│   ├── tax_service.py         # Tax calculation strategies
│   ├── product_service.py     # Product management & repository
│   └── transaction_service.py # Transaction orchestration
│
├── utils/                      # 🛠️ Utility Classes
│   ├── __init__.py
│   ├── input_utils.py         # Input handling & validation
│   └── display_utils.py       # Output formatting & display
│
├── main.py                     # 🚀 Main Application
└── README.md                   # 📖 Documentation
```

## ✨ Fitur Utama

### 👥 Customer Management
- **Regular Customer**: Customer biasa dengan diskon member 5%
- **Premium Customer**: Tier-based discount (Bronze/Silver/Gold/Platinum)
- **VIP Customer**: Diskon tetap 25% + personal assistant

### 🛒 Shopping Cart
- Add/remove items with validation
- Category-based organization
- Real-time subtotal calculation
- State management (finalized/editable)

### 💰 Discount System
- **Senior Discount**: 10% untuk usia 60+
- **Member Discount**: Berbeda per tier customer
- **Category Discount**: 7% untuk kategori dengan minimum item
- **Day-of-Week Discount**: Senin 15%, Sabtu 20%

### 🧾 Tax System
- **Standard Tax**: 10% untuk pembelian > Rp100,000
- **Category Tax**: Berbeda rate per kategori
- **Luxury Tax**: Progressive tax untuk pembelian besar

### 📊 Analytics & Reporting
- Sales summary dengan breakdown
- Top customers analysis
- Category performance metrics
- Transaction status tracking

## 🚀 Instalasi

1. **Clone atau copy folder oop-kasir**
```bash
cd oop-kasir
```

2. **Pastikan Python 3.8+ terinstall**
```bash
python --version
```

3. **Jalankan aplikasi**
```bash
python main.py
```

## 📖 Cara Penggunaan

### Menjalankan Aplikasi
```bash
python main.py
```

### Menu Utama
1. **🛒 Transaksi Baru** - Buat transaksi penjualan
2. **📦 Lihat Produk** - Browse katalog produk
3. **👥 Kelola Customer** - Manajemen customer
4. **📋 Riwayat Transaksi** - View transaction history
5. **📊 Analytics & Reports** - Laporan penjualan
6. **⚙️ Pengaturan** - System settings

### Flow Transaksi
1. **Pilih/Buat Customer** → Customer selection/creation
2. **Tambah Item** → Add products to cart
3. **Review Cart** → Check cart contents
4. **Checkout** → Calculate totals & process payment
5. **Receipt** → Print transaction receipt

## 🔧 Dokumentasi API

### Models

#### Product Class
```python
product = Product('beras', 15000, 'kg', KategoriBarang.MAKANAN)
print(product.get_display_name())  # "Beras"
print(product.get_emoji())         # "🍚"
```

#### Customer Classes
```python
# Regular customer
customer = Customer('John Doe', 25, True)

# Premium customer
premium = PremiumCustomer('Jane Smith', 30, membership_points=5000)
print(premium.tier)  # "Silver"

# VIP customer
vip = VIPCustomer('Bob Wilson', 45, 15000, 'Assistant Name')
print(vip.get_discount_multiplier())  # 0.25
```

#### Shopping Cart
```python
cart = ShoppingCart(customer)
product_item = ProductItem(product, 5)
cart.add_item(product_item)
print(cart.calculate_subtotal())
```

### Services

#### Product Service
```python
product_service = ProductService()
all_products = product_service.get_all_products()
search_results = product_service.search_products('beras')
makanan = product_service.filter_by_category(KategoriBarang.MAKANAN)
```

#### Discount Service
```python
discount_service = DiscountService()
discounts = discount_service.calculate_all_discounts(cart, customer)
total_discount = discount_service.get_total_discount_amount(cart, customer)
```

#### Transaction Service
```python
transaction_service = TransactionService()
transaction = transaction_service.create_transaction(
    cart=cart,
    payment_amount=50000,
    payment_method='cash'
)
```

## 📝 Contoh Penggunaan

### Membuat Transaksi Programatically
```python
from models import Customer, ShoppingCart, Product, ProductItem, KategoriBarang
from services import ProductService, TransactionService

# Setup
product_service = ProductService()
transaction_service = TransactionService()

# Buat customer
customer = Customer('Test User', 30, True)

# Buat cart dan tambah items
cart = ShoppingCart(customer)
beras = product_service.get_product('beras')
if beras:
    item = ProductItem(beras, 2)
    cart.add_item(item)

# Buat transaksi
transaction = transaction_service.create_transaction(
    cart=cart,
    payment_amount=50000,
    payment_method='cash'
)

if transaction:
    transaction_service.complete_transaction(transaction.transaction_id)
    print(f"Transaksi berhasil: {transaction.transaction_id}")
```

### Custom Discount Strategy
```python
from services.discount_service import DiscountStrategy
from models import DiscountDetail

class StudentDiscountStrategy(DiscountStrategy):
    def is_applicable(self, cart, customer):
        return hasattr(customer, 'umur') and customer.umur <= 25
    
    def calculate_discount(self, cart, customer):
        if self.is_applicable(cart, customer):
            subtotal = cart.calculate_subtotal()
            discount_amount = int(subtotal * 0.15)  # 15% discount
            
            return DiscountDetail(
                name="Diskon Student",
                amount=discount_amount,
                percentage=0.15,
                description="Diskon 15% untuk mahasiswa (usia ≤ 25)"
            )
        return DiscountDetail("Diskon Student", 0, 0.0, "Tidak berlaku")

# Tambahkan ke discount service
discount_service.add_strategy(StudentDiscountStrategy())
```

## 🎨 Design Patterns yang Digunakan

### 1. **Strategy Pattern**
- `DiscountStrategy` untuk berbagai jenis diskon
- `TaxStrategy` untuk berbagai perhitungan pajak
- `DisplayFormatter` untuk format output

### 2. **Repository Pattern**
- `ProductRepository` untuk data access abstraction
- `InMemoryProductRepository` untuk implementasi konkret

### 3. **Factory Pattern**
- `ProductFactory` untuk membuat Product objects
- `TransactionBuilder` untuk membangun Transaction

### 4. **Facade Pattern**
- `CashierApp` sebagai facade untuk seluruh aplikasi
- `TransactionService` sebagai facade untuk transaction operations

### 5. **Observer Pattern**
- Event handling dalam transaction lifecycle
- State changes notification

### 6. **Command Pattern**
- Menu operations sebagai commands
- Transaction operations encapsulation

## 🧪 Testing & Validation

### Input Validation
```python
from utils import InputHandler, IntegerValidator

input_handler = InputHandler()
validator = IntegerValidator(min_value=1, max_value=100)

# Input dengan validasi otomatis
quantity = input_handler.get_integer("Jumlah", min_value=1, max_value=100)
```

### Error Handling
```python
try:
    transaction = transaction_service.create_transaction(cart, payment, 'cash')
    if transaction:
        MessageDisplay.success("Transaksi berhasil!")
    else:
        MessageDisplay.error("Gagal membuat transaksi")
except Exception as e:
    MessageDisplay.error(f"Error: {e}")
```

## 🔍 Troubleshooting

### Common Issues

1. **Import Error**
```
ModuleNotFoundError: No module named 'models'
```
**Solution**: Pastikan menjalankan dari directory `oop-kasir/`

2. **Display Issues**
```
Color codes showing as text
```
**Solution**: Gunakan terminal yang support ANSI colors

3. **Input Validation Error**
```
Maksimal retry tercapai
```
**Solution**: Masukkan input sesuai format yang diminta

## 📈 Future Enhancements

### Planned Features
- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Web interface with Flask/FastAPI
- [ ] Inventory management
- [ ] Barcode scanning simulation
- [ ] Multi-language support
- [ ] Export to PDF/Excel
- [ ] REST API endpoints
- [ ] Unit testing suite

### Performance Optimizations
- [ ] Caching frequently accessed products
- [ ] Lazy loading for large datasets
- [ ] Async operations for I/O
- [ ] Memory optimization for large transactions

## 👨‍💻 Development

### Code Style
- Follow PEP 8 guidelines
- Use type hints consistently
- Document all public methods
- Keep methods small and focused

### Contributing
1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Update documentation
5. Submit pull request

## 📄 License

This project is created for educational purposes.

## 🙏 Acknowledgments

- Original procedural version sebagai foundation
- Python community untuk best practices
- Clean Code principles by Robert C. Martin
- Design Patterns inspiration

---

**Dibuat dengan ❤️ untuk pembelajaran OOP dengan Python**

*Versi: 2.0.0 | Update: Desember 2024*