"""
PRODUCT MODEL - Model untuk representasi barang
===============================================
Implementasi OOP untuk entitas Barang dengan prinsip:
- Encapsulation: Data dan method dikapsulasi dalam class
- Validation: Validasi data input
- Clean Code: Naming yang jelas dan struktur yang rapi
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any


class KategoriBarang(Enum):
    """
    Enum untuk kategori barang - menerapkan prinsip Type Safety
    Enum memberikan konstanta yang aman dan mudah dimaintain
    """
    MAKANAN = "makanan"
    MINUMAN = "minuman" 
    KEBUTUHAN = "kebutuhan"
    
    @classmethod
    def get_emoji(cls, kategori: 'KategoriBarang') -> str:
        """
        Method untuk mendapatkan emoji berdasarkan kategori
        
        Args:
            kategori (KategoriBarang): Kategori barang
            
        Returns:
            str: Emoji yang sesuai dengan kategori
        """
        emoji_map = {
            cls.MAKANAN: '🍚',
            cls.MINUMAN: '🥤',
            cls.KEBUTUHAN: '🧼'
        }
        return emoji_map.get(kategori, '📦')


class BaseProduct(ABC):
    """
    Abstract Base Class untuk Product - menerapkan prinsip Abstraction
    Mendefinisikan kontrak/interface yang harus diimplementasi oleh subclass
    """
    
    @abstractmethod
    def get_total_price(self) -> int:
        """Method abstract untuk menghitung total harga"""
        pass
    
    @abstractmethod
    def get_display_name(self) -> str:
        """Method abstract untuk mendapatkan nama display"""
        pass


class Product(BaseProduct):
    """
    Class Product yang merepresentasikan barang di toko
    
    Prinsip OOP yang diterapkan:
    - Encapsulation: Data private dengan getter/setter
    - Inheritance: Mewarisi dari BaseProduct
    - Validation: Validasi input pada constructor dan setter
    """
    
    def __init__(self, nama: str, harga: int, satuan: str, kategori: KategoriBarang):
        """
        Constructor untuk inisialisasi Product
        
        Args:
            nama (str): Nama barang
            harga (int): Harga per satuan
            satuan (str): Satuan barang (kg, botol, buah, dll)
            kategori (KategoriBarang): Kategori barang
            
        Raises:
            ValueError: Jika ada input yang tidak valid
        """
        self._validate_inputs(nama, harga, satuan, kategori)
        
        # Private attributes - Encapsulation
        self._nama = nama.strip().lower()
        self._harga = harga
        self._satuan = satuan.strip().lower()
        self._kategori = kategori
    
    def _validate_inputs(self, nama: str, harga: int, satuan: str, kategori: KategoriBarang) -> None:
        """
        Private method untuk validasi input - Encapsulation
        
        Args:
            nama (str): Nama barang
            harga (int): Harga barang
            satuan (str): Satuan barang
            kategori (KategoriBarang): Kategori barang
            
        Raises:
            ValueError: Jika ada input yang tidak valid
        """
        if not nama or not nama.strip():
            raise ValueError("Nama barang tidak boleh kosong")
        
        if harga <= 0:
            raise ValueError("Harga barang harus lebih dari 0")
        
        if not satuan or not satuan.strip():
            raise ValueError("Satuan barang tidak boleh kosong")
        
        if not isinstance(kategori, KategoriBarang):
            raise ValueError("Kategori harus berupa KategoriBarang enum")
    
    # Getter methods - Encapsulation
    @property
    def nama(self) -> str:
        """Getter untuk nama barang"""
        return self._nama
    
    @property
    def harga(self) -> int:
        """Getter untuk harga barang"""
        return self._harga
    
    @property
    def satuan(self) -> str:
        """Getter untuk satuan barang"""
        return self._satuan
    
    @property
    def kategori(self) -> KategoriBarang:
        """Getter untuk kategori barang"""
        return self._kategori
    
    # Setter methods dengan validasi - Encapsulation
    @harga.setter
    def harga(self, value: int) -> None:
        """
        Setter untuk harga dengan validasi
        
        Args:
            value (int): Harga baru
            
        Raises:
            ValueError: Jika harga tidak valid
        """
        if value <= 0:
            raise ValueError("Harga barang harus lebih dari 0")
        self._harga = value
    
    def get_total_price(self) -> int:
        """
        Implementasi method abstract dari BaseProduct
        Untuk Product sederhana, total price sama dengan harga
        
        Returns:
            int: Total harga
        """
        return self._harga
    
    def get_display_name(self) -> str:
        """
        Implementasi method abstract dari BaseProduct
        Format nama untuk ditampilkan (Title Case)
        
        Returns:
            str: Nama yang sudah diformat untuk display
        """
        return self._nama.replace('_', ' ').title()
    
    def get_emoji(self) -> str:
        """
        Method untuk mendapatkan emoji kategori
        
        Returns:
            str: Emoji yang sesuai dengan kategori
        """
        return KategoriBarang.get_emoji(self._kategori)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Method untuk mengkonversi object ke dictionary
        Berguna untuk serialization dan debugging
        
        Returns:
            Dict[str, Any]: Representasi object dalam bentuk dictionary
        """
        return {
            'nama': self._nama,
            'harga': self._harga,
            'satuan': self._satuan,
            'kategori': self._kategori.value,
            'display_name': self.get_display_name(),
            'emoji': self.get_emoji()
        }
    
    def __str__(self) -> str:
        """
        Method untuk string representation
        
        Returns:
            str: String representation dari object
        """
        return f"{self.get_display_name()} - Rp{self._harga:,}/{self._satuan}"
    
    def __repr__(self) -> str:
        """
        Method untuk detailed representation (debugging)
        
        Returns:
            str: Detailed string representation
        """
        return (f"Product(nama='{self._nama}', harga={self._harga}, "
                f"satuan='{self._satuan}', kategori={self._kategori})")
    
    def __eq__(self, other) -> bool:
        """
        Method untuk equality comparison
        
        Args:
            other: Object lain untuk dibandingkan
            
        Returns:
            bool: True jika sama, False jika berbeda
        """
        if not isinstance(other, Product):
            return False
        return (self._nama == other._nama and 
                self._kategori == other._kategori)
    
    def __hash__(self) -> int:
        """
        Method untuk hashing - diperlukan jika object digunakan sebagai key
        
        Returns:
            int: Hash value dari object
        """
        return hash((self._nama, self._kategori))


class ProductItem(Product):
    """
    Class untuk item product dengan jumlah pembelian
    
    Prinsip OOP:
    - Inheritance: Mewarisi dari Product
    - Composition: Menggunakan Product sebagai base
    - Encapsulation: Data jumlah yang ter-encapsulasi
    """
    
    def __init__(self, product: Product, jumlah: int):
        """
        Constructor untuk ProductItem
        
        Args:
            product (Product): Product yang dibeli
            jumlah (int): Jumlah yang dibeli
            
        Raises:
            ValueError: Jika jumlah tidak valid
        """
        # Inheritance - memanggil constructor parent
        super().__init__(product.nama, product.harga, product.satuan, product.kategori)
        
        if jumlah <= 0:
            raise ValueError("Jumlah pembelian harus lebih dari 0")
        
        self._jumlah = jumlah
    
    @property
    def jumlah(self) -> int:
        """Getter untuk jumlah pembelian"""
        return self._jumlah
    
    @jumlah.setter  
    def jumlah(self, value: int) -> None:
        """
        Setter untuk jumlah dengan validasi
        
        Args:
            value (int): Jumlah baru
            
        Raises:
            ValueError: Jika jumlah tidak valid
        """
        if value <= 0:
            raise ValueError("Jumlah pembelian harus lebih dari 0")
        self._jumlah = value
    
    def get_total_price(self) -> int:
        """
        Override method dari parent - Polymorphism
        Menghitung total harga berdasarkan jumlah
        
        Returns:
            int: Total harga (harga × jumlah)
        """
        return self._harga * self._jumlah
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Override method dari parent
        Menambahkan informasi jumlah dan total
        
        Returns:
            Dict[str, Any]: Dictionary representation dengan jumlah dan total
        """
        data = super().to_dict()
        data.update({
            'jumlah': self._jumlah,
            'total': self.get_total_price()
        })
        return data
    
    def __str__(self) -> str:
        """
        Override string representation
        
        Returns:
            str: String dengan informasi lengkap termasuk jumlah dan total
        """
        return (f"{self.get_display_name()}: {self._jumlah} {self._satuan} "
                f"x Rp{self._harga:,} = Rp{self.get_total_price():,}")
