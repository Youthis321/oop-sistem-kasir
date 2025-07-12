"""
SHOPPING CART MODEL - Model untuk keranjang belanja
=================================================
Implementasi OOP untuk keranjang belanja dengan prinsip:
- Encapsulation: Data cart ter-encapsulasi dengan method untuk manipulasi
- Composition: Menggunakan ProductItem dan Customer
- Single Responsibility: Hanya menangani logic keranjang belanja
- Iterator Pattern: Implementasi iterator untuk loop
"""

from typing import Dict, List, Iterator, Optional
from collections import defaultdict
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.product import ProductItem, KategoriBarang
from models.customer import BaseCustomer


class ShoppingCart:
    """
    Class ShoppingCart untuk mengelola keranjang belanja
    
    Prinsip OOP yang diterapkan:
    - Encapsulation: Data items ter-encapsulasi dengan method public
    - Composition: Menggunakan ProductItem sebagai komponen
    - Iterator Pattern: Implementasi __iter__ dan __next__
    - Single Responsibility: Hanya menangani logic cart
    """
    
    def __init__(self, customer: BaseCustomer):
        """
        Constructor untuk ShoppingCart
        
        Args:
            customer (BaseCustomer): Customer yang memiliki cart
        """
        # Private attributes - Encapsulation
        self._items: Dict[str, ProductItem] = {}
        self._customer = customer
        self._is_finalized = False
    
    @property
    def customer(self) -> BaseCustomer:
        """Getter untuk customer"""
        return self._customer
    
    @property
    def is_empty(self) -> bool:
        """
        Property untuk mengecek apakah cart kosong
        
        Returns:
            bool: True jika cart kosong, False sebaliknya
        """
        return len(self._items) == 0
    
    @property
    def items_count(self) -> int:
        """
        Property untuk mendapatkan jumlah jenis item dalam cart
        
        Returns:
            int: Jumlah jenis item
        """
        return len(self._items)
    
    @property
    def total_quantity(self) -> int:
        """
        Property untuk mendapatkan total kuantitas semua item
        
        Returns:
            int: Total kuantitas
        """
        return sum(item.jumlah for item in self._items.values())
    
    @property
    def is_finalized(self) -> bool:
        """Property untuk mengecek apakah cart sudah di-finalisasi"""
        return self._is_finalized
    
    def add_item(self, product_item: ProductItem) -> bool:
        """
        Method untuk menambah item ke cart
        
        Args:
            product_item (ProductItem): Item yang akan ditambahkan
            
        Returns:
            bool: True jika berhasil, False jika cart sudah finalized
            
        Raises:
            ValueError: Jika product_item tidak valid
        """
        if self._is_finalized:
            return False
        
        if not isinstance(product_item, ProductItem):
            raise ValueError("Item harus berupa ProductItem")
        
        item_key = product_item.nama
        
        if item_key in self._items:
            # Jika item sudah ada, tambahkan jumlahnya
            self._items[item_key].jumlah += product_item.jumlah
        else:
            # Jika item baru, tambahkan ke cart
            self._items[item_key] = product_item
        
        return True
    
    def remove_item(self, product_name: str) -> bool:
        """
        Method untuk menghapus item dari cart
        
        Args:
            product_name (str): Nama product yang akan dihapus
            
        Returns:
            bool: True jika berhasil dihapus, False jika tidak ditemukan atau cart finalized
        """
        if self._is_finalized:
            return False
        
        product_name = product_name.strip().lower()
        
        if product_name in self._items:
            del self._items[product_name]
            return True
        
        return False
    
    def update_quantity(self, product_name: str, new_quantity: int) -> bool:
        """
        Method untuk update kuantitas item
        
        Args:
            product_name (str): Nama product
            new_quantity (int): Kuantitas baru
            
        Returns:
            bool: True jika berhasil, False jika tidak ditemukan atau invalid
            
        Raises:
            ValueError: Jika kuantitas tidak valid
        """
        if self._is_finalized:
            return False
        
        if new_quantity <= 0:
            raise ValueError("Kuantitas harus lebih dari 0")
        
        product_name = product_name.strip().lower()
        
        if product_name in self._items:
            self._items[product_name].jumlah = new_quantity
            return True
        
        return False
    
    def get_item(self, product_name: str) -> Optional[ProductItem]:
        """
        Method untuk mendapatkan item berdasarkan nama
        
        Args:
            product_name (str): Nama product
            
        Returns:
            Optional[ProductItem]: ProductItem jika ditemukan, None jika tidak
        """
        product_name = product_name.strip().lower()
        return self._items.get(product_name)
    
    def get_all_items(self) -> List[ProductItem]:
        """
        Method untuk mendapatkan semua item dalam cart
        
        Returns:
            List[ProductItem]: List semua ProductItem dalam cart
        """
        return list(self._items.values())
    
    def get_items_by_category(self) -> Dict[KategoriBarang, List[ProductItem]]:
        """
        Method untuk mengelompokkan item berdasarkan kategori
        
        Returns:
            Dict[KategoriBarang, List[ProductItem]]: Dictionary item per kategori
        """
        categorized_items = defaultdict(list)
        
        for item in self._items.values():
            categorized_items[item.kategori].append(item)
        
        return dict(categorized_items)
    
    def calculate_subtotal(self) -> int:
        """
        Method untuk menghitung subtotal (sebelum diskon dan pajak)
        
        Returns:
            int: Subtotal cart
        """
        return sum(item.get_total_price() for item in self._items.values())
    
    def get_category_totals(self) -> Dict[KategoriBarang, Dict[str, int]]:
        """
        Method untuk mendapatkan total per kategori
        
        Returns:
            Dict[KategoriBarang, Dict[str, int]]: Dictionary dengan info per kategori
                - quantity: total kuantitas
                - amount: total harga
        """
        category_data = defaultdict(lambda: {'quantity': 0, 'amount': 0})
        
        for item in self._items.values():
            category_data[item.kategori]['quantity'] += item.jumlah
            category_data[item.kategori]['amount'] += item.get_total_price()
        
        return dict(category_data)
    
    def clear_cart(self) -> bool:
        """
        Method untuk mengosongkan cart
        
        Returns:
            bool: True jika berhasil, False jika cart sudah finalized
        """
        if self._is_finalized:
            return False
        
        self._items.clear()
        return True
    
    def finalize_cart(self) -> None:
        """
        Method untuk finalisasi cart (tidak bisa diubah lagi)
        Biasanya dipanggil setelah checkout
        """
        self._is_finalized = True
    
    def unfinalize_cart(self) -> None:
        """
        Method untuk membatalkan finalisasi cart
        Berguna untuk edit setelah checkout
        """
        self._is_finalized = False
    
    def to_dict(self) -> Dict:
        """
        Method untuk mengkonversi cart ke dictionary
        
        Returns:
            Dict: Representasi cart dalam bentuk dictionary
        """
        return {
            'customer': self._customer.to_dict(),
            'items': [item.to_dict() for item in self._items.values()],
            'items_count': self.items_count,
            'total_quantity': self.total_quantity,
            'subtotal': self.calculate_subtotal(),
            'is_finalized': self._is_finalized,
            'category_totals': {
                category.value: data 
                for category, data in self.get_category_totals().items()
            }
        }
    
    # Iterator Pattern Implementation
    def __iter__(self) -> Iterator[ProductItem]:
        """
        Method untuk membuat cart iterable
        
        Returns:
            Iterator[ProductItem]: Iterator untuk ProductItem
        """
        return iter(self._items.values())
    
    def __len__(self) -> int:
        """
        Method untuk mendapatkan panjang cart (jumlah jenis item)
        
        Returns:
            int: Jumlah jenis item dalam cart
        """
        return len(self._items)
    
    def __contains__(self, product_name: str) -> bool:
        """
        Method untuk mengecek apakah product ada dalam cart
        
        Args:
            product_name (str): Nama product
            
        Returns:
            bool: True jika ada, False jika tidak
        """
        return product_name.strip().lower() in self._items
    
    def __str__(self) -> str:
        """
        Method untuk string representation
        
        Returns:
            str: String representation dari cart
        """
        if self.is_empty:
            return f"Cart kosong untuk {self._customer.nama}"
        
        items_summary = f"{self.items_count} jenis item, {self.total_quantity} total item"
        return f"Cart {self._customer.nama}: {items_summary} (Rp{self.calculate_subtotal():,})"
    
    def __repr__(self) -> str:
        """
        Method untuk detailed representation
        
        Returns:
            str: Detailed string representation
        """
        return f"ShoppingCart(customer={repr(self._customer)}, items={len(self._items)})"


class CartManager:
    """
    Class untuk mengelola multiple shopping cart
    
    Prinsip OOP:
    - Single Responsibility: Hanya mengelola multiple cart
    - Encapsulation: Data carts ter-encapsulasi
    - Factory Pattern: Membuat cart baru
    """
    
    def __init__(self):
        """Constructor untuk CartManager"""
        self._carts: Dict[str, ShoppingCart] = {}
    
    def create_cart(self, customer: BaseCustomer) -> ShoppingCart:
        """
        Method untuk membuat cart baru
        
        Args:
            customer (BaseCustomer): Customer pemilik cart
            
        Returns:
            ShoppingCart: Cart yang baru dibuat
        """
        cart_id = f"{customer.nama}_{len(self._carts)}"
        cart = ShoppingCart(customer)
        self._carts[cart_id] = cart
        return cart
    
    def get_cart(self, cart_id: str) -> Optional[ShoppingCart]:
        """
        Method untuk mendapatkan cart berdasarkan ID
        
        Args:
            cart_id (str): ID cart
            
        Returns:
            Optional[ShoppingCart]: Cart jika ditemukan, None jika tidak
        """
        return self._carts.get(cart_id)
    
    def get_customer_carts(self, customer_name: str) -> List[ShoppingCart]:
        """
        Method untuk mendapatkan semua cart customer
        
        Args:
            customer_name (str): Nama customer
            
        Returns:
            List[ShoppingCart]: List cart milik customer
        """
        return [
            cart for cart in self._carts.values()
            if cart.customer.nama.lower() == customer_name.lower()
        ]
    
    def remove_cart(self, cart_id: str) -> bool:
        """
        Method untuk menghapus cart
        
        Args:
            cart_id (str): ID cart
            
        Returns:
            bool: True jika berhasil dihapus, False jika tidak ditemukan
        """
        if cart_id in self._carts:
            del self._carts[cart_id]
            return True
        return False
    
    def get_all_carts(self) -> List[ShoppingCart]:
        """
        Method untuk mendapatkan semua cart
        
        Returns:
            List[ShoppingCart]: List semua cart
        """
        return list(self._carts.values())
    
    def __len__(self) -> int:
        """
        Method untuk mendapatkan jumlah cart
        
        Returns:
            int: Jumlah cart yang dikelola
        """
        return len(self._carts)
