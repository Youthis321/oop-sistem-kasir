"""
PRODUCT SERVICE - Service untuk pengelolaan produk
================================================
Implementasi OOP untuk business logic produk dengan prinsip:
- Repository Pattern: Abstraksi data access layer
- Factory Pattern: Pembuatan product objects
- CRUD Operations: Create, Read, Update, Delete
- Search and Filter: Pencarian dan filter produk
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Callable, Any
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.product import Product, ProductItem, KategoriBarang


class ProductRepository(ABC):
    """
    Abstract Repository untuk Product - Repository Pattern
    Mendefinisikan interface untuk data access layer
    """
    
    @abstractmethod
    def save(self, product: Product) -> bool:
        """Simpan product"""
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[Product]:
        """Cari product berdasarkan nama"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Product]:
        """Ambil semua product"""
        pass
    
    @abstractmethod
    def update(self, product: Product) -> bool:
        """Update product"""
        pass
    
    @abstractmethod
    def delete(self, name: str) -> bool:
        """Hapus product berdasarkan nama"""
        pass


class InMemoryProductRepository(ProductRepository):
    """
    Implementasi Repository menggunakan memory - Repository Pattern
    Untuk development dan testing
    
    Prinsip OOP:
    - Repository Pattern: Implementasi konkret dari ProductRepository
    - Encapsulation: Data ter-encapsulasi dalam dictionary
    - Single Responsibility: Hanya menangani penyimpanan data
    """
    
    def __init__(self):
        """Constructor untuk InMemoryProductRepository"""
        self._products: Dict[str, Product] = {}
        self._initialize_default_products()
    
    def _initialize_default_products(self) -> None:
        """
        Inisialisasi produk default
        Private method untuk setup data awal
        """
        default_products = [
            # Makanan
            Product('beras', 15000, 'kg', KategoriBarang.MAKANAN),
            Product('telur', 20000, 'kg', KategoriBarang.MAKANAN),
            Product('roti', 8000, 'buah', KategoriBarang.MAKANAN),
            Product('sayur', 5000, 'kg', KategoriBarang.MAKANAN),
            Product('buah', 10000, 'kg', KategoriBarang.MAKANAN),
            Product('gula', 12000, 'kg', KategoriBarang.MAKANAN),
            Product('kerupuk', 2000, 'kg', KategoriBarang.MAKANAN),
            Product('mie_instan', 1500, 'buah', KategoriBarang.MAKANAN),
            
            # Minuman
            Product('susu', 12000, 'botol', KategoriBarang.MINUMAN),
            Product('kopi', 5000, 'buah', KategoriBarang.MINUMAN),
            Product('teh', 3000, 'kantong', KategoriBarang.MINUMAN),
            
            # Kebutuhan
            Product('minyak', 25000, 'botol', KategoriBarang.KEBUTUHAN),
            Product('sabun', 5000, 'batang', KategoriBarang.KEBUTUHAN),
            Product('sampo', 10000, 'batang', KategoriBarang.KEBUTUHAN)
        ]
        
        for product in default_products:
            self._products[product.nama] = product
    
    def save(self, product: Product) -> bool:
        """
        Simpan product ke repository
        
        Args:
            product (Product): Product yang akan disimpan
            
        Returns:
            bool: True jika berhasil disimpan
        """
        if not isinstance(product, Product):
            return False
        
        self._products[product.nama] = product
        return True
    
    def find_by_name(self, name: str) -> Optional[Product]:
        """
        Cari product berdasarkan nama
        
        Args:
            name (str): Nama product
            
        Returns:
            Optional[Product]: Product jika ditemukan, None jika tidak
        """
        name = name.strip().lower()
        return self._products.get(name)
    
    def find_all(self) -> List[Product]:
        """
        Ambil semua product
        
        Returns:
            List[Product]: List semua product
        """
        return list(self._products.values())
    
    def update(self, product: Product) -> bool:
        """
        Update product yang sudah ada
        
        Args:
            product (Product): Product dengan data baru
            
        Returns:
            bool: True jika berhasil diupdate
        """
        if product.nama in self._products:
            self._products[product.nama] = product
            return True
        return False
    
    def delete(self, name: str) -> bool:
        """
        Hapus product berdasarkan nama
        
        Args:
            name (str): Nama product yang akan dihapus
            
        Returns:
            bool: True jika berhasil dihapus
        """
        name = name.strip().lower()
        if name in self._products:
            del self._products[name]
            return True
        return False
    
    def count(self) -> int:
        """
        Hitung jumlah product
        
        Returns:
            int: Jumlah product
        """
        return len(self._products)
    
    def exists(self, name: str) -> bool:
        """
        Cek apakah product ada
        
        Args:
            name (str): Nama product
            
        Returns:
            bool: True jika product ada
        """
        name = name.strip().lower()
        return name in self._products


class ProductFactory:
    """
    Factory untuk membuat Product objects - Factory Pattern
    
    Prinsip OOP:
    - Factory Pattern: Abstraksi pembuatan object
    - Static Methods: Method yang tidak bergantung pada instance
    - Validation: Validasi sebelum pembuatan object
    """
    
    @staticmethod
    def create_product(nama: str, harga: int, satuan: str, 
                      kategori: KategoriBarang) -> Product:
        """
        Factory method untuk membuat Product
        
        Args:
            nama (str): Nama product
            harga (int): Harga product
            satuan (str): Satuan product
            kategori (KategoriBarang): Kategori product
            
        Returns:
            Product: Product object yang baru dibuat
            
        Raises:
            ValueError: Jika ada parameter yang tidak valid
        """
        # Validasi akan dilakukan oleh constructor Product
        return Product(nama, harga, satuan, kategori)
    
    @staticmethod
    def create_product_item(product: Product, jumlah: int) -> ProductItem:
        """
        Factory method untuk membuat ProductItem
        
        Args:
            product (Product): Product base
            jumlah (int): Jumlah pembelian
            
        Returns:
            ProductItem: ProductItem object yang baru dibuat
            
        Raises:
            ValueError: Jika parameter tidak valid
        """
        return ProductItem(product, jumlah)
    
    @staticmethod
    def create_from_dict(data: Dict[str, Any]) -> Product:
        """
        Factory method untuk membuat Product dari dictionary
        
        Args:
            data (Dict[str, Any]): Data product dalam bentuk dictionary
            
        Returns:
            Product: Product object yang baru dibuat
            
        Raises:
            KeyError: Jika ada key yang missing
            ValueError: Jika ada value yang tidak valid
        """
        required_keys = ['nama', 'harga', 'satuan', 'kategori']
        
        for key in required_keys:
            if key not in data:
                raise KeyError(f"Key '{key}' tidak ditemukan dalam data")
        
        # Convert kategori string ke enum
        if isinstance(data['kategori'], str):
            kategori = KategoriBarang(data['kategori'])
        else:
            kategori = data['kategori']
        
        return ProductFactory.create_product(
            data['nama'], data['harga'], data['satuan'], kategori
        )


class ProductService:
    """
    Service utama untuk pengelolaan produk
    
    Prinsip OOP yang diterapkan:
    - Dependency Injection: Menerima repository dari luar
    - Single Responsibility: Hanya menangani business logic produk
    - Facade Pattern: Menyediakan interface sederhana untuk operasi kompleks
    - Search and Filter: Berbagai cara pencarian dan filter
    """
    
    def __init__(self, repository: ProductRepository = None):
        """
        Constructor untuk ProductService
        
        Args:
            repository (ProductRepository): Repository untuk data access
        """
        self._repository = repository or InMemoryProductRepository()
        self._factory = ProductFactory()
    
    def create_product(self, nama: str, harga: int, satuan: str, 
                      kategori: KategoriBarang) -> Optional[Product]:
        """
        Membuat product baru
        
        Args:
            nama (str): Nama product
            harga (int): Harga product
            satuan (str): Satuan product
            kategori (KategoriBarang): Kategori product
            
        Returns:
            Optional[Product]: Product jika berhasil dibuat, None jika gagal
        """
        try:
            # Cek apakah product sudah ada
            if self._repository.find_by_name(nama):
                return None  # Product sudah ada
            
            # Buat product baru menggunakan factory
            product = self._factory.create_product(nama, harga, satuan, kategori)
            
            # Simpan ke repository
            if self._repository.save(product):
                return product
            
            return None
        except (ValueError, Exception):
            return None
    
    def get_product(self, nama: str) -> Optional[Product]:
        """
        Mendapatkan product berdasarkan nama
        
        Args:
            nama (str): Nama product
            
        Returns:
            Optional[Product]: Product jika ditemukan
        """
        return self._repository.find_by_name(nama)
    
    def get_all_products(self) -> List[Product]:
        """
        Mendapatkan semua product
        
        Returns:
            List[Product]: List semua product
        """
        return self._repository.find_all()
    
    def update_product(self, nama: str, harga: int = None, 
                      satuan: str = None) -> bool:
        """
        Update product yang sudah ada
        
        Args:
            nama (str): Nama product
            harga (int, optional): Harga baru
            satuan (str, optional): Satuan baru
            
        Returns:
            bool: True jika berhasil diupdate
        """
        product = self._repository.find_by_name(nama)
        if not product:
            return False
        
        try:
            # Update harga jika diberikan
            if harga is not None:
                product.harga = harga
            
            # Update satuan jika diberikan (perlu buat product baru karena immutable)
            if satuan is not None:
                updated_product = Product(
                    product.nama, 
                    product.harga, 
                    satuan, 
                    product.kategori
                )
                return self._repository.update(updated_product)
            
            return self._repository.update(product)
        except (ValueError, Exception):
            return False
    
    def delete_product(self, nama: str) -> bool:
        """
        Hapus product
        
        Args:
            nama (str): Nama product yang akan dihapus
            
        Returns:
            bool: True jika berhasil dihapus
        """
        return self._repository.delete(nama)
    
    def search_products(self, query: str) -> List[Product]:
        """
        Cari product berdasarkan query
        
        Args:
            query (str): Query pencarian
            
        Returns:
            List[Product]: List product yang cocok
        """
        query = query.lower().strip()
        all_products = self._repository.find_all()
        
        # Filter berdasarkan nama yang mengandung query
        results = []
        for product in all_products:
            if query in product.nama or query in product.get_display_name().lower():
                results.append(product)
        
        return results
    
    def filter_by_category(self, kategori: KategoriBarang) -> List[Product]:
        """
        Filter product berdasarkan kategori
        
        Args:
            kategori (KategoriBarang): Kategori yang dicari
            
        Returns:
            List[Product]: List product dalam kategori tersebut
        """
        all_products = self._repository.find_all()
        return [p for p in all_products if p.kategori == kategori]
    
    def filter_by_price_range(self, min_price: int = 0, 
                             max_price: int = float('inf')) -> List[Product]:
        """
        Filter product berdasarkan range harga
        
        Args:
            min_price (int): Harga minimum
            max_price (int): Harga maksimum
            
        Returns:
            List[Product]: List product dalam range harga
        """
        all_products = self._repository.find_all()
        return [p for p in all_products 
                if min_price <= p.harga <= max_price]
    
    def get_products_grouped_by_category(self) -> Dict[KategoriBarang, List[Product]]:
        """
        Mendapatkan product yang dikelompokkan berdasarkan kategori
        
        Returns:
            Dict[KategoriBarang, List[Product]]: Dictionary product per kategori
        """
        all_products = self._repository.find_all()
        grouped = {}
        
        for product in all_products:
            if product.kategori not in grouped:
                grouped[product.kategori] = []
            grouped[product.kategori].append(product)
        
        return grouped
    
    def get_cheapest_products(self, limit: int = 5) -> List[Product]:
        """
        Mendapatkan product termurah
        
        Args:
            limit (int): Jumlah product yang dikembalikan
            
        Returns:
            List[Product]: List product termurah
        """
        all_products = self._repository.find_all()
        sorted_products = sorted(all_products, key=lambda p: p.harga)
        return sorted_products[:limit]
    
    def get_most_expensive_products(self, limit: int = 5) -> List[Product]:
        """
        Mendapatkan product termahal
        
        Args:
            limit (int): Jumlah product yang dikembalikan
            
        Returns:
            List[Product]: List product termahal
        """
        all_products = self._repository.find_all()
        sorted_products = sorted(all_products, key=lambda p: p.harga, reverse=True)
        return sorted_products[:limit]
    
    def create_product_item(self, product_name: str, jumlah: int) -> Optional[ProductItem]:
        """
        Membuat ProductItem dari nama product dan jumlah
        
        Args:
            product_name (str): Nama product
            jumlah (int): Jumlah pembelian
            
        Returns:
            Optional[ProductItem]: ProductItem jika berhasil, None jika gagal
        """
        product = self._repository.find_by_name(product_name)
        if not product:
            return None
        
        try:
            return self._factory.create_product_item(product, jumlah)
        except ValueError:
            return None
    
    def get_product_count(self) -> int:
        """
        Mendapatkan jumlah total product
        
        Returns:
            int: Jumlah product
        """
        return len(self._repository.find_all())
    
    def product_exists(self, nama: str) -> bool:
        """
        Cek apakah product ada
        
        Args:
            nama (str): Nama product
            
        Returns:
            bool: True jika product ada
        """
        return self._repository.find_by_name(nama) is not None
