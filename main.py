"""
MAIN APPLICATION - Aplikasi Kasir OOP
====================================
File utama aplikasi kasir dengan implementasi OOP lengkap.

Prinsip OOP yang diterapkan:
- Facade Pattern: Interface sederhana untuk operasi kompleks
- Dependency Injection: Service dependencies di-inject
- Command Pattern: Menu operations sebagai commands
- Observer Pattern: Event handling untuk transaction
- Single Responsibility: Setiap class punya tugas spesifik

Author: Kasir OOP Development Team
Version: 2.0.0
"""

from typing import Optional, List, Dict, Any
import sys
import os

# Add current directory to path untuk import
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import semua dependencies
try:
    from models.customer import Customer, PremiumCustomer, VIPCustomer
    from models.cart import ShoppingCart, CartManager
    from models.product import Product, ProductItem, KategoriBarang
    from models.transaction import Transaction, TransactionStatus
    
    from services.product_service import ProductService
    from services.discount_service import DiscountService
    from services.tax_service import TaxService
    from services.transaction_service import TransactionService
    
    from utils.input_utils import InputHandler, MenuHandler, ProgressDisplay
    from utils.display_utils import (
        HeaderDisplay, ProductDisplay, CartDisplay,
        ReceiptDisplay, DashboardDisplay, MessageDisplay,
        ColorTheme
    )
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Pastikan semua file berada di lokasi yang benar")
    sys.exit(1)


class CustomerManager:
    """
    Class untuk mengelola customer - Single Responsibility
    
    Prinsip OOP:
    - Single Responsibility: Hanya mengelola customer
    - Factory Pattern: Membuat berbagai tipe customer
    - Repository Pattern: Penyimpanan customer data
    """
    
    def __init__(self):
        """Constructor untuk CustomerManager"""
        self._customers: Dict[str, Customer] = {}
        self._input_handler = InputHandler()
    
    def create_customer(self) -> Optional[Customer]:
        """
        Membuat customer baru dengan input interaktif
        
        Returns:
            Optional[Customer]: Customer yang dibuat atau None jika batal
        """
        try:
            MessageDisplay.info("Membuat data customer baru")
            
            # Input nama
            nama = self._input_handler.get_string(
                "Nama customer", min_length=2, max_length=50
            )
            
            # Input umur
            umur = self._input_handler.get_integer(
                "Umur customer", min_value=0, max_value=150
            )
            
            # Input status member
            is_member = self._input_handler.get_yes_no(
                "Apakah customer sudah menjadi member?", default=False
            )
            
            if not is_member:
                # Tawarkan pendaftaran member
                daftar_member = self._input_handler.get_yes_no(
                    "Ingin mendaftar sebagai member?", default=False
                )
                is_member = daftar_member
            
            # Jika member, tawarkan upgrade ke premium/VIP
            if is_member:
                customer_type = self._input_handler.get_choice(
                    "Tipe membership",
                    choices=['regular', 'premium', 'vip'],
                    default='regular'
                )
                
                if customer_type == 'premium':
                    points = self._input_handler.get_integer(
                        "Membership points", min_value=0, default=0
                    )
                    customer = PremiumCustomer(nama, umur, points)
                    
                elif customer_type == 'vip':
                    points = self._input_handler.get_integer(
                        "Membership points", min_value=0, default=10000
                    )
                    assistant = self._input_handler.get_string(
                        "Nama personal assistant", allow_empty=True, default=""
                    )
                    customer = VIPCustomer(nama, umur, points, assistant)
                    
                else:
                    customer = Customer(nama, umur, True)
            else:
                customer = Customer(nama, umur, False)
            
            # Simpan customer
            self._customers[customer.nama.lower()] = customer
            
            MessageDisplay.success(f"Customer {customer.nama} berhasil dibuat!")
            return customer
            
        except (KeyboardInterrupt, EOFError):
            MessageDisplay.warning("Pembuatan customer dibatalkan")
            return None
        except Exception as e:
            MessageDisplay.error(f"Gagal membuat customer: {e}")
            return None
    
    def get_customer(self, nama: str) -> Optional[Customer]:
        """
        Mendapatkan customer berdasarkan nama
        
        Args:
            nama (str): Nama customer
            
        Returns:
            Optional[Customer]: Customer jika ditemukan
        """
        return self._customers.get(nama.lower())
    
    def list_customers(self) -> List[Customer]:
        """
        Mendapatkan semua customer
        
        Returns:
            List[Customer]: List semua customer
        """
        return list(self._customers.values())


class ShoppingManager:
    """
    Class untuk mengelola shopping process - Facade Pattern
    
    Prinsip OOP:
    - Facade Pattern: Interface sederhana untuk shopping complex process
    - Composition: Menggunakan berbagai service
    - State Management: Mengelola state shopping session
    """
    
    def __init__(self, product_service: ProductService):
        """
        Constructor untuk ShoppingManager
        
        Args:
            product_service (ProductService): Service untuk produk
        """
        self._product_service = product_service
        self._input_handler = InputHandler()
        self._product_display = ProductDisplay()
        self._cart_display = CartDisplay()
        
    def create_shopping_cart(self, customer: Customer) -> ShoppingCart:
        """
        Membuat shopping cart baru
        
        Args:
            customer (Customer): Customer pemilik cart
            
        Returns:
            ShoppingCart: Cart yang baru dibuat
        """
        return ShoppingCart(customer)
    
    def add_items_to_cart(self, cart: ShoppingCart) -> bool:
        """
        Proses menambah item ke cart secara interaktif
        
        Args:
            cart (ShoppingCart): Cart untuk ditambahi item
            
        Returns:
            bool: True jika ada item yang ditambahkan
        """
        try:
            HeaderDisplay().show_section_header("PILIH BARANG BELANJA", "🛒")
            
            # Tampilkan katalog produk
            all_products = self._product_service.get_all_products()
            self._product_display.show_product_catalog(all_products)
            
            items_added = False
            
            while True:
                print(f"\n{ColorTheme.info('MENAMBAH ITEM KE KERANJANG')}")
                
                # Input nama produk
                product_name = self._input_handler.get_string(
                    "Nama produk (atau 'selesai' untuk lanjut)",
                    min_length=1
                )
                
                if product_name.lower() == 'selesai':
                    break
                
                # Cari produk
                product = self._product_service.get_product(product_name.lower())
                if not product:
                    MessageDisplay.warning(f"Produk '{product_name}' tidak ditemukan")
                    
                    # Coba pencarian fuzzy
                    search_results = self._product_service.search_products(product_name)
                    if search_results:
                        print(f"\nProduk yang mungkin Anda maksud:")
                        for p in search_results[:3]:
                            print(f"- {p.get_display_name()}")
                    continue
                
                # Tampilkan detail produk
                self._product_display.show_product_details(product)
                
                # Input jumlah
                jumlah = self._input_handler.get_integer(
                    f"Jumlah {product.get_display_name()} ({product.satuan})",
                    min_value=1
                )
                
                # Buat product item dan tambah ke cart
                product_item = ProductItem(product, jumlah)
                
                if cart.add_item(product_item):
                    MessageDisplay.success(
                        f"Berhasil menambah {jumlah} {product.satuan} {product.get_display_name()}"
                    )
                    items_added = True
                else:
                    MessageDisplay.error("Gagal menambah item ke keranjang")
                
                # Tampilkan current cart
                print(f"\n{ColorTheme.highlight('KERANJANG SAAT INI:')}")
                self._cart_display.show_cart_details(cart)
                
                # Tanya lanjut atau tidak
                lanjut = self._input_handler.get_yes_no(
                    "Tambah item lain?", default=True
                )
                if not lanjut:
                    break
            
            return items_added
            
        except (KeyboardInterrupt, EOFError):
            MessageDisplay.warning("Proses belanja dibatalkan")
            return False
        except Exception as e:
            MessageDisplay.error(f"Error dalam proses belanja: {e}")
            return False


class CheckoutManager:
    """
    Class untuk mengelola checkout process - Command Pattern
    
    Prinsip OOP:
    - Command Pattern: Checkout sebagai command
    - Orchestration: Mengkoordinasi berbagai service
    - Transaction Management: Mengelola transaksi
    """
    
    def __init__(self, transaction_service: TransactionService):
        """
        Constructor untuk CheckoutManager
        
        Args:
            transaction_service (TransactionService): Service untuk transaksi
        """
        self._transaction_service = transaction_service
        self._input_handler = InputHandler()
        self._receipt_display = ReceiptDisplay()
    
    def process_checkout(self, cart: ShoppingCart) -> Optional[Transaction]:
        """
        Proses checkout cart menjadi transaksi
        
        Args:
            cart (ShoppingCart): Cart yang akan di-checkout
            
        Returns:
            Optional[Transaction]: Transaksi jika berhasil
        """
        try:
            HeaderDisplay().show_section_header("CHECKOUT", "💳")
            
            if cart.is_empty:
                MessageDisplay.error("Keranjang belanja kosong")
                return None
            
            # Tampilkan ringkasan cart
            CartDisplay().show_cart_details(cart)
            
            # Hitung total dengan preview
            totals = self._transaction_service._orchestrator.calculate_transaction_totals(cart)
            self._show_total_breakdown(totals)
            
            # Konfirmasi lanjut checkout
            lanjut = self._input_handler.get_yes_no(
                "Lanjut ke pembayaran?", default=True
            )
            if not lanjut:
                MessageDisplay.info("Checkout dibatalkan")
                return None
            
            # Input pembayaran
            payment_amount, payment_method, installments = self._get_payment_input(
                totals['total_amount']
            )
            
            # Buat transaksi
            MessageDisplay.loading("Memproses transaksi")
            ProgressDisplay().show_loading("Processing payment", 2)
            
            transaction = self._transaction_service.create_transaction(
                cart=cart,
                payment_amount=payment_amount,
                payment_method=payment_method,
                installments=installments
            )
            
            if transaction:
                # Complete transaksi
                self._transaction_service.complete_transaction(transaction.transaction_id)
                
                MessageDisplay.success("Transaksi berhasil!")
                
                # Tampilkan struk
                self._receipt_display.show_receipt(transaction)
                
                return transaction
            else:
                MessageDisplay.error("Gagal membuat transaksi")
                return None
                
        except (KeyboardInterrupt, EOFError):
            MessageDisplay.warning("Checkout dibatalkan")
            return None
        except Exception as e:
            MessageDisplay.error(f"Error dalam checkout: {e}")
            return None
    
    def _show_total_breakdown(self, totals: Dict[str, Any]) -> None:
        """
        Tampilkan breakdown total perhitungan
        
        Args:
            totals (Dict[str, Any]): Data breakdown total
        """
        print(f"\n{ColorTheme.highlight('RINGKASAN PEMBAYARAN:')}")
        print("-" * 40)
        
        # Subtotal
        print(f"Subtotal: Rp{totals['subtotal']:,}")
        
        # Diskon
        if totals['discounts']:
            for discount in totals['discounts']:
                print(f"{discount.name}: -Rp{discount.amount:,}")
            print(f"Total diskon: -Rp{totals['total_discount']:,}")
            print(f"Setelah diskon: Rp{totals['subtotal_after_discount']:,}")
        
        # Pajak
        if totals['taxes']:
            for tax in totals['taxes']:
                print(f"{tax.name}: +Rp{tax.amount:,}")
            print(f"Total pajak: +Rp{totals['total_tax']:,}")
        
        print("=" * 40)
        total_str = f"Rp{totals['total_amount']:,}"
        print(f"{ColorTheme.success('TOTAL BAYAR:')} {ColorTheme.info(total_str)}")
    
    def _get_payment_input(self, total_amount: int) -> tuple[int, str, List[int]]:
        """
        Input metode dan jumlah pembayaran
        
        Args:
            total_amount (int): Total yang harus dibayar
            
        Returns:
            tuple[int, str, List[int]]: (payment_amount, method, installments)
        """
        # Pilih metode pembayaran
        payment_methods = ['cash', 'card', 'digital', 'transfer']
        payment_method = self._input_handler.get_choice(
            "Metode pembayaran", payment_methods, default='cash'
        )
        
        # Tanya cicilan untuk non-cash
        installments = []
        if payment_method != 'cash':
            use_installment = self._input_handler.get_yes_no(
                "Gunakan cicilan?", default=False
            )
            
            if use_installment:
                installment_count = self._input_handler.get_integer(
                    "Jumlah cicilan", min_value=2, max_value=12
                )
                
                print(f"Masukkan {installment_count} cicilan:")
                installments = self._input_handler.get_multiple_integers(
                    "Cicilan", installment_count, min_value=1000
                )
                
                total_installments = sum(installments)
                print(f"Total cicilan: Rp{total_installments:,}")
                
                return total_installments, payment_method, installments
        
        # Input pembayaran regular
        while True:
            payment_amount = self._input_handler.get_integer(
                f"Jumlah pembayaran (Total: Rp{total_amount:,})",
                min_value=0
            )
            
            if payment_amount >= total_amount:
                kembalian = payment_amount - total_amount
                if kembalian > 0:
                    print(f"Kembalian: {ColorTheme.success(f'Rp{kembalian:,}')}")
                break
            else:
                kurang = total_amount - payment_amount
                MessageDisplay.warning(f"Kurang bayar Rp{kurang:,}")
                
                lanjut = self._input_handler.get_yes_no(
                    "Coba lagi?", default=True
                )
                if not lanjut:
                    break
        
        return payment_amount, payment_method, installments


class CashierApp:
    """
    Main Application Class - Facade Pattern
    
    Prinsip OOP yang diterapkan:
    - Facade Pattern: Interface sederhana untuk aplikasi kompleks
    - Dependency Injection: Semua service di-inject
    - Command Pattern: Menu operations sebagai commands
    - Single Responsibility: Koordinasi aplikasi
    """
    
    def __init__(self):
        """Constructor untuk CashierApp"""
        # Initialize services - Dependency Injection
        self._product_service = ProductService()
        self._discount_service = DiscountService()
        self._tax_service = TaxService()
        self._transaction_service = TransactionService()
        
        # Initialize managers
        self._customer_manager = CustomerManager()
        self._shopping_manager = ShoppingManager(self._product_service)
        self._checkout_manager = CheckoutManager(self._transaction_service)
        
        # Initialize UI components
        self._input_handler = InputHandler()
        self._menu_handler = MenuHandler()
        self._header_display = HeaderDisplay()
        self._dashboard_display = DashboardDisplay()
        
        # App state
        self._current_customer: Optional[Customer] = None
        self._current_cart: Optional[ShoppingCart] = None
    
    def run(self) -> None:
        """
        Method utama untuk menjalankan aplikasi
        Main event loop dengan error handling
        """
        try:
            self._header_display.show_app_header()
            MessageDisplay.info("Aplikasi Kasir OOP dimulai")
            
            while True:
                try:
                    choice = self._show_main_menu()
                    
                    if choice == '0':
                        self._handle_exit()
                        break
                    elif choice == '1':
                        self._handle_new_transaction()
                    elif choice == '2':
                        self._handle_view_products()
                    elif choice == '3':
                        self._handle_view_customers()
                    elif choice == '4':
                        self._handle_view_transactions()
                    elif choice == '5':
                        self._handle_analytics()
                    elif choice == '6':
                        self._handle_settings()
                    else:
                        MessageDisplay.warning("Pilihan tidak valid")
                        
                except KeyboardInterrupt:
                    print(f"\n{ColorTheme.warning('Operasi dibatalkan')}")
                    continue
                except Exception as e:
                    MessageDisplay.error(f"Error dalam operasi: {e}")
                    continue
                    
        except KeyboardInterrupt:
            print(f"\n{ColorTheme.info('Aplikasi dihentikan oleh user')}")
        except Exception as e:
            MessageDisplay.error(f"Error fatal dalam aplikasi: {e}")
        finally:
            MessageDisplay.info("Terima kasih telah menggunakan Kasir OOP!")
    
    def _show_main_menu(self) -> str:
        """
        Tampilkan main menu dan dapatkan pilihan user
        
        Returns:
            str: Pilihan user
        """
        menu_options = {
            '1': '🛒 Transaksi Baru',
            '2': '📦 Lihat Produk',
            '3': '👥 Kelola Customer',
            '4': '📋 Riwayat Transaksi',
            '5': '📊 Analytics & Reports',
            '6': '⚙️ Pengaturan'
        }
        
        # Show current session info
        if self._current_customer:
            print(f"\n{ColorTheme.info('Session:')} Customer: {self._current_customer.nama}")
            if self._current_cart and not self._current_cart.is_empty:
                print(f"Cart: {self._current_cart.items_count} item(s)")
        
        return self._menu_handler.display_menu("KASIR TOKO KELONTONG - MENU UTAMA", menu_options)
    
    def _handle_new_transaction(self) -> None:
        """Handle menu transaksi baru"""
        try:
            HeaderDisplay().show_section_header("TRANSAKSI BARU", "🛒")
            
            # Step 1: Buat atau pilih customer
            if not self._current_customer:
                customer = self._get_or_create_customer()
                if not customer:
                    MessageDisplay.warning("Transaksi dibatalkan - tidak ada customer")
                    return
                self._current_customer = customer
            
            # Step 2: Buat cart jika belum ada
            if not self._current_cart:
                self._current_cart = self._shopping_manager.create_shopping_cart(self._current_customer)
            
            # Step 3: Pilih menu transaksi
            transaction_menu = {
                '1': 'Tambah Item ke Keranjang',
                '2': 'Lihat Keranjang',
                '3': 'Checkout',
                '4': 'Ganti Customer',
                '5': 'Reset Keranjang'
            }
            
            while True:
                choice = self._menu_handler.display_menu("MENU TRANSAKSI", transaction_menu)
                
                if choice == '0':
                    break
                elif choice == '1':
                    self._shopping_manager.add_items_to_cart(self._current_cart)
                elif choice == '2':
                    self._show_current_cart()
                elif choice == '3':
                    transaction = self._checkout_manager.process_checkout(self._current_cart)
                    if transaction:
                        # Reset session setelah checkout berhasil
                        self._current_cart = None
                        self._current_customer = None
                        MessageDisplay.success("Transaksi selesai! Session direset.")
                        break
                elif choice == '4':
                    self._current_customer = None
                    self._current_cart = None
                    MessageDisplay.info("Customer session direset")
                    break
                elif choice == '5':
                    if self._current_cart:
                        self._current_cart.clear_cart()
                        MessageDisplay.success("Keranjang dikosongkan")
                    
        except Exception as e:
            MessageDisplay.error(f"Error dalam transaksi: {e}")
    
    def _get_or_create_customer(self) -> Optional[Customer]:
        """
        Mendapatkan customer existing atau buat baru
        
        Returns:
            Optional[Customer]: Customer yang dipilih atau dibuat
        """
        customer_menu = {
            '1': 'Buat Customer Baru',
            '2': 'Pilih Customer Existing'
        }
        
        choice = self._menu_handler.display_menu("PILIH CUSTOMER", customer_menu)
        
        if choice == '1':
            return self._customer_manager.create_customer()
        elif choice == '2':
            return self._select_existing_customer()
        
        return None
    
    def _select_existing_customer(self) -> Optional[Customer]:
        """
        Pilih customer yang sudah ada
        
        Returns:
            Optional[Customer]: Customer yang dipilih
        """
        customers = self._customer_manager.list_customers()
        
        if not customers:
            MessageDisplay.warning("Belum ada customer. Buat customer baru dulu.")
            return self._customer_manager.create_customer()
        
        # Tampilkan daftar customer
        print(f"\n{ColorTheme.highlight('DAFTAR CUSTOMER:')}")
        customer_names = []
        for i, customer in enumerate(customers, 1):
            print(f"{i}. {customer}")
            customer_names.append(customer.nama)
        
        # Pilih customer
        choice_index = self._menu_handler.display_numbered_menu(
            "PILIH CUSTOMER", customer_names, allow_exit=True
        )
        
        if choice_index >= 0:
            return customers[choice_index]
        
        return None
    
    def _show_current_cart(self) -> None:
        """Tampilkan keranjang saat ini"""
        if not self._current_cart:
            MessageDisplay.warning("Tidak ada keranjang aktif")
            return
        
        if self._current_cart.is_empty:
            MessageDisplay.info("Keranjang kosong")
            return
        
        CartDisplay().show_cart_summary(self._current_cart)
        CartDisplay().show_cart_details(self._current_cart)
    
    def _handle_view_products(self) -> None:
        """Handle menu lihat produk"""
        HeaderDisplay().show_section_header("MANAJEMEN PRODUK", "📦")
        
        product_menu = {
            '1': 'Lihat Semua Produk',
            '2': 'Cari Produk',
            '3': 'Filter per Kategori',
            '4': 'Produk Termurah',
            '5': 'Produk Termahal'
        }
        
        choice = self._menu_handler.display_menu("MENU PRODUK", product_menu)
        
        if choice == '1':
            products = self._product_service.get_all_products()
            ProductDisplay().show_product_catalog(products)
        elif choice == '2':
            self._search_products()
        elif choice == '3':
            self._filter_products_by_category()
        elif choice == '4':
            products = self._product_service.get_cheapest_products()
            self._show_product_list("PRODUK TERMURAH", products)
        elif choice == '5':
            products = self._product_service.get_most_expensive_products()
            self._show_product_list("PRODUK TERMAHAL", products)
    
    def _search_products(self) -> None:
        """Search produk"""
        query = self._input_handler.get_string("Kata kunci pencarian", min_length=1)
        results = self._product_service.search_products(query)
        
        if results:
            self._show_product_list(f"HASIL PENCARIAN: '{query}'", results)
        else:
            MessageDisplay.warning(f"Tidak ada produk yang cocok dengan '{query}'")
    
    def _filter_products_by_category(self) -> None:
        """Filter produk berdasarkan kategori"""
        categories = ['makanan', 'minuman', 'kebutuhan']
        category_str = self._input_handler.get_choice("Pilih kategori", categories)
        
        category = KategoriBarang(category_str)
        products = self._product_service.filter_by_category(category)
        
        self._show_product_list(f"KATEGORI: {category_str.upper()}", products)
    
    def _show_product_list(self, title: str, products: List[Product]) -> None:
        """
        Tampilkan list produk dengan title
        
        Args:
            title (str): Judul list
            products (List[Product]): List produk
        """
        print(f"\n{ColorTheme.highlight(title)}")
        if products:
            ProductDisplay().show_product_list_table(products)
        else:
            MessageDisplay.info("Tidak ada produk dalam kategori ini")
    
    def _handle_view_customers(self) -> None:
        """Handle menu kelola customer"""
        HeaderDisplay().show_section_header("MANAJEMEN CUSTOMER", "👥")
        
        customers = self._customer_manager.list_customers()
        
        if not customers:
            MessageDisplay.info("Belum ada customer")
            create = self._input_handler.get_yes_no("Buat customer baru?")
            if create:
                self._customer_manager.create_customer()
            return
        
        print(f"\n{ColorTheme.highlight('DAFTAR CUSTOMER:')}")
        for i, customer in enumerate(customers, 1):
            print(f"{i}. {customer}")
            if hasattr(customer, 'membership_points'):
                print(f"   Points: {customer.membership_points}")
    
    def _handle_view_transactions(self) -> None:
        """Handle menu riwayat transaksi"""
        HeaderDisplay().show_section_header("RIWAYAT TRANSAKSI", "📋")
        
        transaction_menu = {
            '1': 'Semua Transaksi',
            '2': 'Transaksi Hari Ini',
            '3': 'Transaksi per Customer',
            '4': 'Transaksi per Status'
        }
        
        choice = self._menu_handler.display_menu("MENU TRANSAKSI", transaction_menu)
        
        if choice == '1':
            self._show_all_transactions()
        elif choice == '2':
            self._show_daily_transactions()
        elif choice == '3':
            self._show_customer_transactions()
        elif choice == '4':
            self._show_transactions_by_status()
    
    def _show_all_transactions(self) -> None:
        """Tampilkan semua transaksi"""
        transactions = self._transaction_service._transaction_history
        self._display_transaction_list("SEMUA TRANSAKSI", transactions)
    
    def _show_daily_transactions(self) -> None:
        """Tampilkan transaksi hari ini"""
        transactions = self._transaction_service.get_daily_transactions()
        self._display_transaction_list("TRANSAKSI HARI INI", transactions)
    
    def _show_customer_transactions(self) -> None:
        """Tampilkan transaksi customer tertentu"""
        customer_name = self._input_handler.get_string("Nama customer", min_length=1)
        transactions = self._transaction_service.get_customer_transactions(customer_name)
        self._display_transaction_list(f"TRANSAKSI: {customer_name.upper()}", transactions)
    
    def _show_transactions_by_status(self) -> None:
        """Tampilkan transaksi berdasarkan status"""
        status_options = ['completed', 'pending', 'cancelled', 'refunded']
        status_str = self._input_handler.get_choice("Pilih status", status_options)
        
        status = TransactionStatus(status_str)
        transactions = self._transaction_service.get_transactions_by_status(status)
        self._display_transaction_list(f"STATUS: {status_str.upper()}", transactions)
    
    def _display_transaction_list(self, title: str, transactions: List[Transaction]) -> None:
        """
        Tampilkan list transaksi
        
        Args:
            title (str): Judul list
            transactions (List[Transaction]): List transaksi
        """
        print(f"\n{ColorTheme.highlight(title)}")
        
        if not transactions:
            MessageDisplay.info("Tidak ada transaksi")
            return
        
        for i, transaction in enumerate(transactions, 1):
            status_color = ColorTheme.GREEN if transaction.status == TransactionStatus.COMPLETED else ColorTheme.YELLOW
            status_text = ColorTheme.colorize(transaction.status.value.upper(), status_color)
            
            print(f"{i}. ID: {transaction.transaction_id}")
            print(f"   Customer: {transaction.customer.nama}")
            print(f"   Total: Rp{transaction.total_amount:,}")
            print(f"   Status: {status_text}")
            print(f"   Tanggal: {transaction.created_at.strftime('%d/%m/%Y %H:%M')}")
            print()
    
    def _handle_analytics(self) -> None:
        """Handle menu analytics"""
        HeaderDisplay().show_section_header("ANALYTICS & REPORTS", "📊")
        
        analytics = self._transaction_service.get_sales_analytics()
        
        # Tampilkan analytics
        self._dashboard_display.show_sales_summary(analytics)
        self._dashboard_display.show_status_breakdown(analytics.get('status_breakdown', {}))
        self._dashboard_display.show_top_customers(analytics.get('top_customers', []))
        self._dashboard_display.show_category_performance(analytics.get('category_performance', {}))
    
    def _handle_settings(self) -> None:
        """Handle menu pengaturan"""
        HeaderDisplay().show_section_header("PENGATURAN SISTEM", "⚙️")
        
        settings_menu = {
            '1': 'Pengaturan Pajak',
            '2': 'Pengaturan Diskon',
            '3': 'Reset Data',
            '4': 'Informasi Sistem'
        }
        
        choice = self._menu_handler.display_menu("MENU PENGATURAN", settings_menu)
        
        if choice == '1':
            self._tax_settings()
        elif choice == '2':
            self._discount_settings()
        elif choice == '3':
            self._reset_data()
        elif choice == '4':
            self._show_system_info()
    
    def _tax_settings(self) -> None:
        """Pengaturan pajak"""
        tax_modes = ['standard', 'category', 'luxury', 'combined']
        current_mode = self._tax_service._tax_mode
        
        print(f"Mode pajak saat ini: {ColorTheme.info(current_mode)}")
        
        new_mode = self._input_handler.get_choice(
            "Pilih mode pajak baru", tax_modes, default=current_mode
        )
        
        self._tax_service.set_tax_mode(new_mode)
        MessageDisplay.success(f"Mode pajak diubah ke: {new_mode}")
    
    def _discount_settings(self) -> None:
        """Pengaturan diskon"""
        MessageDisplay.info("Pengaturan diskon saat ini menggunakan konfigurasi default")
        print("- Diskon lansia: 10% (usia 60+)")
        print("- Diskon member: 5-25% (tergantung tier)")
        print("- Diskon kategori: 7% (min 3 item makanan/minuman, 2 item kebutuhan)")
        print("- Diskon hari: 15% (Senin), 20% (Sabtu)")
    
    def _reset_data(self) -> None:
        """Reset data aplikasi"""
        confirm = self._input_handler.get_yes_no(
            "⚠️ PERINGATAN: Ini akan menghapus semua data transaksi dan customer. Lanjutkan?",
            default=False
        )
        
        if confirm:
            double_confirm = self._input_handler.get_yes_no(
                "Apakah Anda yakin? Data yang dihapus tidak dapat dikembalikan!",
                default=False
            )
            
            if double_confirm:
                # Reset data
                self._transaction_service._transactions.clear()
                self._transaction_service._transaction_history.clear()
                self._customer_manager._customers.clear()
                self._current_customer = None
                self._current_cart = None
                
                MessageDisplay.success("Semua data berhasil direset!")
            else:
                MessageDisplay.info("Reset dibatalkan")
        else:
            MessageDisplay.info("Reset dibatalkan")
    
    def _show_system_info(self) -> None:
        """Tampilkan informasi sistem"""
        print(f"\n{ColorTheme.highlight('INFORMASI SISTEM')}")
        print("-" * 40)
        print(f"Aplikasi: Kasir Toko Kelontong OOP")
        print(f"Versi: 2.0.0")
        print(f"Total Produk: {self._product_service.get_product_count()}")
        print(f"Total Customer: {len(self._customer_manager.list_customers())}")
        print(f"Total Transaksi: {len(self._transaction_service._transaction_history)}")
        print(f"Mode Pajak: {self._tax_service._tax_mode}")
        print(f"Session Customer: {self._current_customer.nama if self._current_customer else 'Tidak ada'}")
    
    def _handle_exit(self) -> None:
        """Handle menu keluar"""
        if self._current_cart and not self._current_cart.is_empty:
            MessageDisplay.warning("Masih ada keranjang belanja yang tidak di-checkout")
            save_session = self._input_handler.get_yes_no(
                "Simpan session untuk nanti?", default=True
            )
            
            if not save_session:
                self._current_cart = None
                self._current_customer = None
        
        MessageDisplay.success("Sampai jumpa! Terima kasih telah menggunakan Kasir OOP")


def main():
    """
    Function main untuk menjalankan aplikasi
    Entry point aplikasi dengan error handling global
    """
    try:
        app = CashierApp()
        app.run()
    except KeyboardInterrupt:
        print(f"\n{ColorTheme.info('Aplikasi dihentikan')}")
    except Exception as e:
        print(f"\n{ColorTheme.error('Error fatal:')} {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
