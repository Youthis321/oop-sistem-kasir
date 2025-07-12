"""
TAX SERVICE - Service untuk perhitungan pajak
===========================================
Implementasi OOP untuk business logic pajak dengan prinsip:
- Single Responsibility: Hanya menangani perhitungan pajak
- Strategy Pattern: Berbagai strategi pajak
- Configuration: Mudah dikonfigurasi rate pajak
- Open/Closed Principle: Mudah ditambah jenis pajak baru
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, List
from dataclasses import dataclass
import sys
import os

# Add parent directory to path  
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cart import ShoppingCart
from models.customer import BaseCustomer
from models.product import KategoriBarang


@dataclass
class TaxDetail:
    """
    Dataclass untuk detail pajak - Value Object Pattern
    
    Attributes:
        name (str): Nama pajak
        rate (float): Rate pajak (0.1 = 10%)
        amount (int): Jumlah pajak dalam rupiah
        taxable_amount (int): Jumlah yang kena pajak
        description (str): Deskripsi pajak
    """
    name: str
    rate: float
    amount: int
    taxable_amount: int
    description: str = ""
    
    def __post_init__(self):
        """Validasi setelah inisialisasi"""
        if self.rate < 0:
            raise ValueError("Rate pajak tidak boleh negatif")
        if self.amount < 0:
            raise ValueError("Amount pajak tidak boleh negatif")
        if self.taxable_amount < 0:
            raise ValueError("Taxable amount tidak boleh negatif")


class TaxStrategy(ABC):
    """
    Abstract Strategy untuk perhitungan pajak - Strategy Pattern
    Mendefinisikan interface untuk semua strategi pajak
    """
    
    @abstractmethod
    def calculate_tax(self, subtotal_after_discount: int, 
                     cart: ShoppingCart, customer: BaseCustomer) -> TaxDetail:
        """
        Method abstract untuk menghitung pajak
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            TaxDetail: Detail pajak yang dihitung
        """
        pass
    
    @abstractmethod
    def is_applicable(self, subtotal_after_discount: int, 
                     cart: ShoppingCart, customer: BaseCustomer) -> bool:
        """
        Method abstract untuk mengecek apakah pajak berlaku
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            bool: True jika pajak berlaku
        """
        pass


class StandardTaxStrategy(TaxStrategy):
    """
    Strategi pajak standar (PPN)
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani pajak standar
    - Strategy Pattern: Implementasi konkret dari TaxStrategy
    - Configuration: Rate dan threshold bisa dikonfigurasi
    """
    
    def __init__(self, tax_rate: float = 0.10, threshold: int = 100000):
        """
        Constructor untuk StandardTaxStrategy
        
        Args:
            tax_rate (float): Rate pajak (default: 10%)
            threshold (int): Batas minimum kena pajak (default: 100,000)
        """
        if tax_rate < 0 or tax_rate > 1:
            raise ValueError("Tax rate harus antara 0-1")
        if threshold < 0:
            raise ValueError("Threshold tidak boleh negatif")
        
        self._tax_rate = tax_rate
        self._threshold = threshold
    
    def is_applicable(self, subtotal_after_discount: int, 
                     cart: ShoppingCart, customer: BaseCustomer) -> bool:
        """
        Cek apakah pajak standar berlaku
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            bool: True jika subtotal melebihi threshold
        """
        return subtotal_after_discount > self._threshold
    
    def calculate_tax(self, subtotal_after_discount: int, 
                     cart: ShoppingCart, customer: BaseCustomer) -> TaxDetail:
        """
        Hitung pajak standar
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            TaxDetail: Detail pajak standar
        """
        if not self.is_applicable(subtotal_after_discount, cart, customer):
            return TaxDetail(
                name="PPN",
                rate=0.0,
                amount=0,
                taxable_amount=0,
                description="Tidak kena pajak (di bawah threshold)"
            )
        
        tax_amount = int(subtotal_after_discount * self._tax_rate)
        
        return TaxDetail(
            name="PPN",
            rate=self._tax_rate,
            amount=tax_amount,
            taxable_amount=subtotal_after_discount,
            description=f"Pajak {self._tax_rate*100:.0f}% untuk pembelian "
                       f"di atas Rp{self._threshold:,}"
        )


class CategoryBasedTaxStrategy(TaxStrategy):
    """
    Strategi pajak berdasarkan kategori barang
    
    Prinsip OOP:
    - Strategy Pattern: Implementasi pajak berbasis kategori
    - Configuration: Rate berbeda per kategori
    - Open/Closed: Mudah ditambah kategori baru
    """
    
    def __init__(self):
        """Constructor untuk CategoryBasedTaxStrategy"""
        # Konfigurasi pajak per kategori
        self._category_tax_rates = {
            KategoriBarang.MAKANAN: 0.05,     # 5% untuk makanan
            KategoriBarang.MINUMAN: 0.08,     # 8% untuk minuman
            KategoriBarang.KEBUTUHAN: 0.12    # 12% untuk kebutuhan
        }
        self._threshold = 50000  # Threshold lebih rendah untuk kategori
    
    def is_applicable(self, subtotal_after_discount: int, 
                     cart: ShoppingCart, customer: BaseCustomer) -> bool:
        """
        Cek apakah pajak kategori berlaku
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            bool: True jika subtotal melebihi threshold
        """
        return subtotal_after_discount > self._threshold
    
    def calculate_tax(self, subtotal_after_discount: int, 
                     cart: ShoppingCart, customer: BaseCustomer) -> List[TaxDetail]:
        """
        Hitung pajak per kategori
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            List[TaxDetail]: List pajak per kategori
        """
        if not self.is_applicable(subtotal_after_discount, cart, customer):
            return []
        
        taxes = []
        items_by_category = cart.get_items_by_category()
        
        for category, items in items_by_category.items():
            if category in self._category_tax_rates:
                category_total = sum(item.get_total_price() for item in items)
                tax_rate = self._category_tax_rates[category]
                tax_amount = int(category_total * tax_rate)
                
                taxes.append(TaxDetail(
                    name=f"Pajak {category.value.title()}",
                    rate=tax_rate,
                    amount=tax_amount,
                    taxable_amount=category_total,
                    description=f"Pajak {tax_rate*100:.0f}% untuk kategori {category.value}"
                ))
        
        return taxes


class LuxuryTaxStrategy(TaxStrategy):
    """
    Strategi pajak mewah untuk pembelian besar
    
    Prinsip OOP:
    - Strategy Pattern: Implementasi pajak untuk luxury purchase
    - Progressive Tax: Rate meningkat berdasarkan jumlah
    """
    
    def __init__(self):
        """Constructor untuk LuxuryTaxStrategy"""
        # Progressive tax brackets
        self._tax_brackets = [
            {'min_amount': 500000, 'rate': 0.05, 'name': 'Luxury Tier 1'},
            {'min_amount': 1000000, 'rate': 0.08, 'name': 'Luxury Tier 2'},
            {'min_amount': 2000000, 'rate': 0.12, 'name': 'Luxury Tier 3'}
        ]
    
    def is_applicable(self, subtotal_after_discount: int, 
                     cart: ShoppingCart, customer: BaseCustomer) -> bool:
        """
        Cek apakah pajak mewah berlaku
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            bool: True jika masuk kategori luxury
        """
        return subtotal_after_discount >= self._tax_brackets[0]['min_amount']
    
    def calculate_tax(self, subtotal_after_discount: int, 
                     cart: ShoppingCart, customer: BaseCustomer) -> TaxDetail:
        """
        Hitung pajak mewah
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            TaxDetail: Detail pajak mewah
        """
        if not self.is_applicable(subtotal_after_discount, cart, customer):
            return TaxDetail("Luxury Tax", 0.0, 0, 0, "Tidak masuk kategori luxury")
        
        # Cari tier yang sesuai (ambil yang tertinggi)
        applicable_tier = None
        for tier in reversed(self._tax_brackets):
            if subtotal_after_discount >= tier['min_amount']:
                applicable_tier = tier
                break
        
        if applicable_tier:
            tax_amount = int(subtotal_after_discount * applicable_tier['rate'])
            
            return TaxDetail(
                name=applicable_tier['name'],
                rate=applicable_tier['rate'],
                amount=tax_amount,
                taxable_amount=subtotal_after_discount,
                description=f"Luxury tax {applicable_tier['rate']*100:.0f}% "
                           f"untuk pembelian di atas Rp{applicable_tier['min_amount']:,}"
            )
        
        return TaxDetail("Luxury Tax", 0.0, 0, 0, "Tidak ada tier yang sesuai")


class TaxService:
    """
    Service utama untuk perhitungan pajak
    
    Prinsip OOP yang diterapkan:
    - Dependency Injection: Menerima strategies dari luar
    - Strategy Pattern: Menggunakan berbagai strategi pajak
    - Single Responsibility: Hanya mengkoordinasi perhitungan pajak
    - Configuration: Mudah switch mode perhitungan pajak
    """
    
    def __init__(self, tax_mode: str = "standard"):
        """
        Constructor untuk TaxService
        
        Args:
            tax_mode (str): Mode perhitungan pajak
                          - "standard": Pajak standar
                          - "category": Pajak per kategori
                          - "luxury": Pajak mewah
                          - "combined": Kombinasi standard + luxury
        """
        self._tax_mode = tax_mode
        self._strategies = self._initialize_strategies()
    
    def _initialize_strategies(self) -> Dict[str, TaxStrategy]:
        """
        Inisialisasi strategies berdasarkan mode
        
        Returns:
            Dict[str, TaxStrategy]: Dictionary strategies
        """
        return {
            'standard': StandardTaxStrategy(),
            'category': CategoryBasedTaxStrategy(),
            'luxury': LuxuryTaxStrategy()
        }
    
    def set_tax_mode(self, mode: str) -> None:
        """
        Set mode perhitungan pajak
        
        Args:
            mode (str): Mode pajak baru
            
        Raises:
            ValueError: Jika mode tidak valid
        """
        valid_modes = ['standard', 'category', 'luxury', 'combined']
        if mode not in valid_modes:
            raise ValueError(f"Mode harus salah satu dari: {valid_modes}")
        
        self._tax_mode = mode
    
    def calculate_tax(self, subtotal_after_discount: int, 
                     cart: ShoppingCart, customer: BaseCustomer) -> List[TaxDetail]:
        """
        Menghitung pajak berdasarkan mode yang dipilih
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            List[TaxDetail]: List detail pajak
        """
        taxes = []
        
        if self._tax_mode == "standard":
            # Hanya pajak standar
            standard_tax = self._strategies['standard'].calculate_tax(
                subtotal_after_discount, cart, customer
            )
            if standard_tax.amount > 0:
                taxes.append(standard_tax)
        
        elif self._tax_mode == "category":
            # Pajak per kategori
            category_taxes = self._strategies['category'].calculate_tax(
                subtotal_after_discount, cart, customer
            )
            taxes.extend(category_taxes)
        
        elif self._tax_mode == "luxury":
            # Hanya pajak mewah
            luxury_tax = self._strategies['luxury'].calculate_tax(
                subtotal_after_discount, cart, customer
            )
            if luxury_tax.amount > 0:
                taxes.append(luxury_tax)
        
        elif self._tax_mode == "combined":
            # Kombinasi standard + luxury (yang lebih besar)
            standard_tax = self._strategies['standard'].calculate_tax(
                subtotal_after_discount, cart, customer
            )
            luxury_tax = self._strategies['luxury'].calculate_tax(
                subtotal_after_discount, cart, customer
            )
            
            # Pilih yang lebih besar
            if luxury_tax.amount > standard_tax.amount:
                taxes.append(luxury_tax)
            elif standard_tax.amount > 0:
                taxes.append(standard_tax)
        
        return taxes
    
    def get_total_tax_amount(self, subtotal_after_discount: int, 
                           cart: ShoppingCart, customer: BaseCustomer) -> int:
        """
        Mendapatkan total semua pajak
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            int: Total amount pajak
        """
        taxes = self.calculate_tax(subtotal_after_discount, cart, customer)
        return sum(tax.amount for tax in taxes)
    
    def get_tax_summary(self, subtotal_after_discount: int, 
                       cart: ShoppingCart, customer: BaseCustomer) -> Dict[str, any]:
        """
        Mendapatkan ringkasan pajak
        
        Args:
            subtotal_after_discount (int): Subtotal setelah diskon
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            Dict[str, any]: Ringkasan pajak
        """
        taxes = self.calculate_tax(subtotal_after_discount, cart, customer)
        total_amount = sum(tax.amount for tax in taxes)
        
        return {
            'taxes': taxes,
            'total_tax_amount': total_amount,
            'tax_count': len(taxes),
            'tax_mode': self._tax_mode,
            'subtotal_before_tax': subtotal_after_discount,
            'total_after_tax': subtotal_after_discount + total_amount
        }
