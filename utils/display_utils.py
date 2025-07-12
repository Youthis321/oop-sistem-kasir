"""
DISPLAY UTILITIES - Utility classes untuk output display
======================================================
Implementasi OOP untuk display/output dengan prinsip:
- Single Responsibility: Setiap class punya tugas spesifik
- Template Method: Template untuk format display
- Strategy Pattern: Berbagai strategi display
- Decorator Pattern: Menambah styling pada output
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
import textwrap
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import (
    Product, ProductItem, Customer, ShoppingCart, 
    Transaction, KategoriBarang
)


class DisplayFormatter(ABC):
    """
    Abstract base class untuk display formatter - Strategy Pattern
    Mendefinisikan interface untuk format display
    """
    
    @abstractmethod
    def format_currency(self, amount: int) -> str:
        """Format currency display"""
        pass
    
    @abstractmethod
    def format_table_row(self, columns: List[str], widths: List[int]) -> str:
        """Format table row"""
        pass


class IndonesianFormatter(DisplayFormatter):
    """
    Formatter untuk format Indonesia
    
    Prinsip OOP:
    - Strategy Pattern: Implementasi konkret dari DisplayFormatter
    - Localization: Format sesuai locale Indonesia
    """
    
    def format_currency(self, amount: int) -> str:
        """
        Format currency dalam format Rupiah
        
        Args:
            amount (int): Jumlah dalam rupiah
            
        Returns:
            str: String currency yang sudah diformat
        """
        return f"Rp{amount:,}".replace(',', '.')
    
    def format_table_row(self, columns: List[str], widths: List[int]) -> str:
        """
        Format table row dengan padding
        
        Args:
            columns (List[str]): List kolom
            widths (List[int]): List lebar kolom
            
        Returns:
            str: String row yang sudah diformat
        """
        formatted_columns = []
        for i, (column, width) in enumerate(zip(columns, widths)):
            if i == len(columns) - 1:  # Last column (usually price) - right align
                formatted_columns.append(column.rjust(width))
            else:
                formatted_columns.append(column.ljust(width))
        
        return " | ".join(formatted_columns)


class ColorTheme:
    """
    Class untuk color theme - Configuration Pattern
    
    Prinsip OOP:
    - Configuration: Konfigurasi warna terpusat
    - Constants: Konstanta warna
    """
    
    # ANSI Color codes
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    
    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'
    BG_BLUE = '\033[104m'
    
    @classmethod
    def colorize(cls, text: str, color: str, bold: bool = False) -> str:
        """
        Colorize text dengan warna
        
        Args:
            text (str): Text yang akan diwarnai
            color (str): Kode warna
            bold (bool): Apakah bold
            
        Returns:
            str: Text yang sudah diwarnai
        """
        style = cls.BOLD if bold else ''
        return f"{style}{color}{text}{cls.RESET}"
    
    @classmethod
    def success(cls, text: str) -> str:
        """Green text untuk success message"""
        return cls.colorize(text, cls.GREEN, True)
    
    @classmethod
    def error(cls, text: str) -> str:
        """Red text untuk error message"""
        return cls.colorize(text, cls.RED, True)
    
    @classmethod
    def warning(cls, text: str) -> str:
        """Yellow text untuk warning message"""
        return cls.colorize(text, cls.YELLOW, True)
    
    @classmethod
    def info(cls, text: str) -> str:
        """Blue text untuk info message"""
        return cls.colorize(text, cls.BLUE, True)
    
    @classmethod
    def highlight(cls, text: str) -> str:
        """Cyan text untuk highlight"""
        return cls.colorize(text, cls.CYAN, True)


class HeaderDisplay:
    """
    Class untuk menampilkan header aplikasi
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani header display
    - Template Method: Template untuk berbagai jenis header
    """
    
    def __init__(self, formatter: DisplayFormatter = None):
        """
        Constructor untuk HeaderDisplay
        
        Args:
            formatter (DisplayFormatter): Formatter untuk display
        """
        self._formatter = formatter or IndonesianFormatter()
    
    def show_app_header(self) -> None:
        """Tampilkan header aplikasi utama"""
        header = """
╔══════════════════════════════════════════════════════════════════╗
║                        🏪 KASIR TOKO KELONTONG                   ║
║                          Version 2.0 - OOP                      ║
║                     Selamat datang di toko kami!                ║
╚══════════════════════════════════════════════════════════════════╝
        """
        print(ColorTheme.highlight(header))
    
    def show_section_header(self, title: str, emoji: str = "📋") -> None:
        """
        Tampilkan header untuk section
        
        Args:
            title (str): Judul section
            emoji (str): Emoji untuk section
        """
        width = 70
        title_with_emoji = f"{emoji} {title.upper()} {emoji}"
        
        print(f"\n{'═' * width}")
        print(f"{title_with_emoji.center(width)}")
        print('═' * width)
    
    def show_subsection_header(self, title: str) -> None:
        """
        Tampilkan header untuk subsection
        
        Args:
            title (str): Judul subsection
        """
        print(f"\n--- {title.upper()} ---")
        print('-' * (len(title) + 8))


class ProductDisplay:
    """
    Class untuk display product-related information
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani display produk
    - Composition: Menggunakan formatter dan color theme
    """
    
    def __init__(self, formatter: DisplayFormatter = None):
        """
        Constructor untuk ProductDisplay
        
        Args:
            formatter (DisplayFormatter): Formatter untuk display
        """
        self._formatter = formatter or IndonesianFormatter()
    
    def show_product_catalog(self, products: List[Product]) -> None:
        """
        Tampilkan katalog produk berdasarkan kategori
        
        Args:
            products (List[Product]): List produk
        """
        # Group products by category
        categories = {}
        for product in products:
            if product.kategori not in categories:
                categories[product.kategori] = []
            categories[product.kategori].append(product)
        
        HeaderDisplay().show_section_header("DAFTAR BARANG", "🛒")
        
        # Emoji untuk kategori
        emoji_map = {
            KategoriBarang.MAKANAN: '🍚',
            KategoriBarang.MINUMAN: '🥤',
            KategoriBarang.KEBUTUHAN: '🧼'
        }
        
        for category, category_products in categories.items():
            emoji = emoji_map.get(category, '📦')
            print(f"\n{emoji} {ColorTheme.highlight(category.value.upper())}")
            print("-" * 50)
            
            for product in category_products:
                price_str = self._formatter.format_currency(product.harga)
                print(f"  {product.get_display_name():<15} {price_str:>12} /{product.satuan}")
    
    def show_product_details(self, product: Product) -> None:
        """
        Tampilkan detail produk
        
        Args:
            product (Product): Produk yang akan ditampilkan
        """
        print(f"\n📦 {ColorTheme.highlight('DETAIL PRODUK')}")
        print("-" * 30)
        print(f"Nama     : {product.get_display_name()}")
        print(f"Kategori : {product.get_emoji()} {product.kategori.value.title()}")
        print(f"Harga    : {self._formatter.format_currency(product.harga)}")
        print(f"Satuan   : {product.satuan}")
    
    def show_product_list_table(self, products: List[Product]) -> None:
        """
        Tampilkan daftar produk dalam format tabel
        
        Args:
            products (List[Product]): List produk
        """
        if not products:
            print(ColorTheme.warning("Tidak ada produk untuk ditampilkan"))
            return
        
        # Table headers
        headers = ["No", "Nama Produk", "Kategori", "Harga", "Satuan"]
        widths = [4, 20, 12, 15, 10]
        
        # Print header
        print(self._formatter.format_table_row(headers, widths))
        print("-" * sum(widths) + "-" * (len(widths) - 1) * 3)
        
        # Print rows
        for i, product in enumerate(products, 1):
            row = [
                str(i),
                product.get_display_name()[:18],
                product.kategori.value.title(),
                self._formatter.format_currency(product.harga),
                product.satuan
            ]
            print(self._formatter.format_table_row(row, widths))


class CartDisplay:
    """
    Class untuk display shopping cart
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani display cart
    - Composition: Menggunakan ProductDisplay untuk konsistensi
    """
    
    def __init__(self, formatter: DisplayFormatter = None):
        """
        Constructor untuk CartDisplay
        
        Args:
            formatter (DisplayFormatter): Formatter untuk display
        """
        self._formatter = formatter or IndonesianFormatter()
    
    def show_cart_summary(self, cart: ShoppingCart) -> None:
        """
        Tampilkan ringkasan keranjang belanja
        
        Args:
            cart (ShoppingCart): Keranjang belanja
        """
        HeaderDisplay().show_section_header("KERANJANG BELANJA", "🛒")
        
        if cart.is_empty:
            print(ColorTheme.warning("Keranjang belanja kosong"))
            return
        
        print(f"Customer: {ColorTheme.highlight(cart.customer.nama)}")
        print(f"Total Item: {cart.items_count} jenis, {cart.total_quantity} buah")
        print(f"Subtotal: {ColorTheme.info(self._formatter.format_currency(cart.calculate_subtotal()))}")
    
    def show_cart_details(self, cart: ShoppingCart) -> None:
        """
        Tampilkan detail isi keranjang
        
        Args:
            cart (ShoppingCart): Keranjang belanja
        """
        if cart.is_empty:
            print(ColorTheme.warning("Keranjang belanja kosong"))
            return
        
        # Group by category
        items_by_category = cart.get_items_by_category()
        
        emoji_map = {
            KategoriBarang.MAKANAN: '🍚',
            KategoriBarang.MINUMAN: '🥤',
            KategoriBarang.KEBUTUHAN: '🧼'
        }
        
        for category, items in items_by_category.items():
            emoji = emoji_map.get(category, '📦')
            print(f"\n{emoji} {ColorTheme.highlight(category.value.upper())}:")
            
            for item in items:
                total_str = self._formatter.format_currency(item.get_total_price())
                price_str = self._formatter.format_currency(item.harga)
                
                print(f"  {item.get_display_name()}: {item.jumlah} {item.satuan} "
                      f"x {price_str} = {ColorTheme.info(total_str)}")


class ReceiptDisplay:
    """
    Class untuk display receipt/struk
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani display struk
    - Template Method: Template untuk format struk
    """
    
    def __init__(self, formatter: DisplayFormatter = None):
        """
        Constructor untuk ReceiptDisplay
        
        Args:
            formatter (DisplayFormatter): Formatter untuk display
        """
        self._formatter = formatter or IndonesianFormatter()
    
    def show_receipt(self, transaction: Transaction) -> None:
        """
        Tampilkan struk transaksi lengkap
        
        Args:
            transaction (Transaction): Transaksi
        """
        print(f"\n{'═' * 60}")
        print(f"{'🧾 STRUK BELANJA'.center(60)}")
        print('═' * 60)
        
        # Header info
        print(f"Transaction ID: {transaction.transaction_id}")
        print(f"Tanggal: {transaction.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"Kasir: System OOP")
        print("-" * 60)
        
        # Customer info
        customer = transaction.customer
        print(f"Customer: {ColorTheme.highlight(customer.nama)}")
        print(f"Tipe: {customer.get_customer_type()}")
        if hasattr(customer, 'umur'):
            print(f"Umur: {customer.umur} tahun")
        print("-" * 60)
        
        # Items details
        cart = transaction.cart
        items_by_category = cart.get_items_by_category()
        
        emoji_map = {
            KategoriBarang.MAKANAN: '🍚',
            KategoriBarang.MINUMAN: '🥤',
            KategoriBarang.KEBUTUHAN: '🧼'
        }
        
        for category, items in items_by_category.items():
            emoji = emoji_map.get(category, '📦')
            print(f"\n{emoji} {category.value.upper()}:")
            
            for item in items:
                total_str = self._formatter.format_currency(item.get_total_price())
                price_str = self._formatter.format_currency(item.harga)
                
                print(f"  {item.get_display_name()}: {item.jumlah} {item.satuan} "
                      f"x {price_str} = {total_str}")
        
        print("-" * 60)
        
        # Financial breakdown
        subtotal_str = self._formatter.format_currency(transaction.subtotal)
        print(f"Subtotal: {subtotal_str:>45}")
        
        # Discounts
        if transaction.discounts:
            for discount in transaction.discounts:
                discount_str = self._formatter.format_currency(discount.amount)
                print(f"{discount.name}: -{discount_str:>35}")
            
            total_discount = transaction.get_total_discount()
            discount_total_str = self._formatter.format_currency(total_discount)
            subtotal_after_str = self._formatter.format_currency(transaction.subtotal - total_discount)
            print(f"Setelah diskon: {subtotal_after_str:>40}")
        
        # Tax
        if transaction.tax_amount > 0:
            tax_str = self._formatter.format_currency(transaction.tax_amount)
            print(f"Pajak (10%): +{tax_str:>41}")
        
        print("=" * 60)
        
        # Total
        total_str = self._formatter.format_currency(transaction.total_amount)
        print(f"{ColorTheme.highlight('TOTAL BAYAR:')} {ColorTheme.info(total_str):>40}")
        
        # Payment details
        payment = transaction.payment
        paid_str = self._formatter.format_currency(payment.amount_paid)
        print(f"Dibayar ({payment.payment_method}): {paid_str:>35}")
        
        if payment.change_amount > 0:
            change_str = self._formatter.format_currency(payment.change_amount)
            print(f"{ColorTheme.success('KEMBALIAN:')} {ColorTheme.success(change_str):>40}")
        
        # Installments
        if payment.installments:
            print(f"\nCicilan ({len(payment.installments)}x):")
            for i, installment in enumerate(payment.installments, 1):
                installment_str = self._formatter.format_currency(installment)
                print(f"  Cicilan {i}: {installment_str}")
        
        print("=" * 60)
        print(f"{'Terima kasih telah berbelanja!'.center(60)}")
        print(f"{'Status: ' + transaction.status.value.upper().center(50)}")
        print("=" * 60)


class DashboardDisplay:
    """
    Class untuk display dashboard dan analytics
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani display analytics
    - Data Visualization: Visualisasi data dalam text
    """
    
    def __init__(self, formatter: DisplayFormatter = None):
        """
        Constructor untuk DashboardDisplay
        
        Args:
            formatter (DisplayFormatter): Formatter untuk display
        """
        self._formatter = formatter or IndonesianFormatter()
    
    def show_sales_summary(self, analytics: Dict[str, Any]) -> None:
        """
        Tampilkan ringkasan penjualan
        
        Args:
            analytics (Dict[str, Any]): Data analytics
        """
        HeaderDisplay().show_section_header("RINGKASAN PENJUALAN", "📊")
        
        summary = analytics.get('summary', {})
        
        print(f"Total Revenue: {ColorTheme.success(self._formatter.format_currency(summary.get('total_revenue', 0)))}")
        print(f"Total Transaksi: {ColorTheme.info(str(summary.get('total_transactions', 0)))}")
        print(f"Total Item Terjual: {ColorTheme.info(str(summary.get('total_items_sold', 0)))}")
        print(f"Rata-rata per Transaksi: {ColorTheme.highlight(self._formatter.format_currency(summary.get('average_transaction_value', 0)))}")
    
    def show_top_customers(self, customers: List[Dict[str, Any]]) -> None:
        """
        Tampilkan top customers
        
        Args:
            customers (List[Dict[str, Any]]): Data top customers
        """
        if not customers:
            return
        
        print(f"\n🏆 {ColorTheme.highlight('TOP CUSTOMERS')}")
        print("-" * 50)
        
        for i, customer in enumerate(customers, 1):
            spent_str = self._formatter.format_currency(customer['total_spent'])
            print(f"{i}. {customer['name']}: {ColorTheme.success(spent_str)} "
                  f"({customer['transaction_count']} transaksi)")
    
    def show_category_performance(self, categories: Dict[str, Any]) -> None:
        """
        Tampilkan performa kategori
        
        Args:
            categories (Dict[str, Any]): Data performa kategori
        """
        if not categories:
            return
        
        print(f"\n📈 {ColorTheme.highlight('PERFORMA KATEGORI')}")
        print("-" * 60)
        
        emoji_map = {
            'makanan': '🍚',
            'minuman': '🥤',
            'kebutuhan': '🧼'
        }
        
        for category_name, data in categories.items():
            emoji = emoji_map.get(category_name, '📦')
            revenue_str = self._formatter.format_currency(data['total_revenue'])
            
            print(f"{emoji} {category_name.title()}:")
            print(f"  Revenue: {ColorTheme.success(revenue_str)}")
            print(f"  Items Sold: {ColorTheme.info(str(data['total_items_sold']))}")
            print(f"  Transactions: {data['transaction_count']}")
    
    def show_status_breakdown(self, status_data: Dict[str, int]) -> None:
        """
        Tampilkan breakdown status transaksi
        
        Args:
            status_data (Dict[str, int]): Data breakdown status
        """
        if not status_data:
            return
        
        print(f"\n📋 {ColorTheme.highlight('STATUS TRANSAKSI')}")
        print("-" * 30)
        
        status_colors = {
            'completed': ColorTheme.GREEN,
            'pending': ColorTheme.YELLOW,
            'cancelled': ColorTheme.RED,
            'refunded': ColorTheme.MAGENTA
        }
        
        for status, count in status_data.items():
            color = status_colors.get(status, ColorTheme.WHITE)
            colored_status = ColorTheme.colorize(status.title(), color)
            print(f"{colored_status}: {count}")


class MessageDisplay:
    """
    Class untuk display messages (error, success, warning)
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani message display
    - Strategy Pattern: Berbagai tipe message
    """
    
    @staticmethod
    def success(message: str, title: str = "SUCCESS") -> None:
        """Tampilkan success message"""
        print(f"\n✅ {ColorTheme.success(title)}: {message}")
    
    @staticmethod
    def error(message: str, title: str = "ERROR") -> None:
        """Tampilkan error message"""
        print(f"\n❌ {ColorTheme.error(title)}: {message}")
    
    @staticmethod
    def warning(message: str, title: str = "WARNING") -> None:
        """Tampilkan warning message"""
        print(f"\n⚠️ {ColorTheme.warning(title)}: {message}")
    
    @staticmethod
    def info(message: str, title: str = "INFO") -> None:
        """Tampilkan info message"""
        print(f"\n🔵 {ColorTheme.info(title)}: {message}")
    
    @staticmethod
    def loading(message: str = "Processing") -> None:
        """Tampilkan loading message"""
        print(f"\n⏳ {message}...")
    
    @staticmethod
    def separator(char: str = "-", length: int = 50) -> None:
        """Tampilkan separator line"""
        print(char * length)
