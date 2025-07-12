"""
DISCOUNT SERVICE - Service untuk perhitungan diskon
=================================================
Implementasi OOP untuk business logic diskon dengan prinsip:
- Single Responsibility: Hanya menangani perhitungan diskon
- Strategy Pattern: Berbagai strategi diskon
- Open/Closed Principle: Mudah ditambah tipe diskon baru
- Dependency Injection: Service tidak terikat pada implementasi konkret
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Tuple
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cart import ShoppingCart
from models.customer import BaseCustomer, Customer, PremiumCustomer, VIPCustomer
from models.product import KategoriBarang
from models.transaction import DiscountDetail


class DiscountStrategy(ABC):
    """
    Abstract Strategy untuk perhitungan diskon - Strategy Pattern
    Mendefinisikan interface untuk semua strategi diskon
    """
    
    @abstractmethod
    def calculate_discount(self, cart: ShoppingCart, customer: BaseCustomer) -> DiscountDetail:
        """
        Method abstract untuk menghitung diskon
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            DiscountDetail: Detail diskon yang dihitung
        """
        pass
    
    @abstractmethod
    def is_applicable(self, cart: ShoppingCart, customer: BaseCustomer) -> bool:
        """
        Method abstract untuk mengecek apakah diskon berlaku
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            bool: True jika diskon berlaku
        """
        pass


class SeniorDiscountStrategy(DiscountStrategy):
    """
    Strategi diskon untuk lansia
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani diskon lansia
    - Strategy Pattern: Implementasi konkret dari DiscountStrategy
    """
    
    def __init__(self, percentage: float = 0.10, min_age: int = 60):
        """
        Constructor untuk SeniorDiscountStrategy
        
        Args:
            percentage (float): Persentase diskon (default: 10%)
            min_age (int): Umur minimum untuk diskon (default: 60)
        """
        self._percentage = percentage
        self._min_age = min_age
    
    def is_applicable(self, cart: ShoppingCart, customer: BaseCustomer) -> bool:
        """
        Cek apakah diskon lansia berlaku
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            bool: True jika customer lansia
        """
        return hasattr(customer, 'umur') and customer.umur >= self._min_age
    
    def calculate_discount(self, cart: ShoppingCart, customer: BaseCustomer) -> DiscountDetail:
        """
        Hitung diskon lansia
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            DiscountDetail: Detail diskon lansia
        """
        if not self.is_applicable(cart, customer):
            return DiscountDetail("Diskon Lansia", 0, 0.0, "Tidak berlaku")
        
        subtotal = cart.calculate_subtotal()
        discount_amount = int(subtotal * self._percentage)
        
        return DiscountDetail(
            name="Diskon Lansia",
            amount=discount_amount,
            percentage=self._percentage,
            description=f"Diskon {self._percentage*100:.0f}% untuk usia {self._min_age}+ tahun"
        )


class MemberDiscountStrategy(DiscountStrategy):
    """
    Strategi diskon untuk member
    
    Prinsip OOP:
    - Polymorphism: Berbeda behavior untuk tipe customer berbeda
    - Strategy Pattern: Implementasi konkret dari DiscountStrategy
    """
    
    def is_applicable(self, cart: ShoppingCart, customer: BaseCustomer) -> bool:
        """
        Cek apakah diskon member berlaku
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            bool: True jika customer adalah member
        """
        return hasattr(customer, 'is_member') and customer.is_member
    
    def calculate_discount(self, cart: ShoppingCart, customer: BaseCustomer) -> DiscountDetail:
        """
        Hitung diskon member - Polymorphism berdasarkan tipe customer
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            DiscountDetail: Detail diskon member
        """
        if not self.is_applicable(cart, customer):
            return DiscountDetail("Diskon Member", 0, 0.0, "Tidak berlaku")
        
        subtotal = cart.calculate_subtotal()
        
        # Polymorphism - berbeda behavior berdasarkan tipe customer
        if isinstance(customer, VIPCustomer):
            percentage = 0.25  # 25% untuk VIP
            tier = "VIP"
        elif isinstance(customer, PremiumCustomer):
            percentage = customer.get_discount_multiplier()  # Berdasarkan tier
            tier = customer.tier
        else:
            percentage = 0.05  # 5% untuk member regular
            tier = "Regular"
        
        discount_amount = int(subtotal * percentage)
        
        return DiscountDetail(
            name=f"Diskon Member {tier}",
            amount=discount_amount,
            percentage=percentage,
            description=f"Diskon {percentage*100:.0f}% untuk member {tier}"
        )


class CategoryDiscountStrategy(DiscountStrategy):
    """
    Strategi diskon berdasarkan kategori barang
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani diskon kategori
    - Open/Closed: Mudah ditambah kategori baru
    """
    
    def __init__(self):
        """Constructor untuk CategoryDiscountStrategy"""
        # Konfigurasi diskon per kategori
        self._category_rules = {
            KategoriBarang.MAKANAN: {'min_items': 3, 'percentage': 0.07},
            KategoriBarang.MINUMAN: {'min_items': 3, 'percentage': 0.07},
            KategoriBarang.KEBUTUHAN: {'min_items': 2, 'percentage': 0.07}
        }
    
    def is_applicable(self, cart: ShoppingCart, customer: BaseCustomer) -> bool:
        """
        Cek apakah ada kategori yang memenuhi syarat diskon
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            bool: True jika ada kategori yang memenuhi syarat
        """
        category_totals = cart.get_category_totals()
        
        for category, rule in self._category_rules.items():
            if category in category_totals:
                if category_totals[category]['quantity'] >= rule['min_items']:
                    return True
        
        return False
    
    def calculate_discount(self, cart: ShoppingCart, customer: BaseCustomer) -> List[DiscountDetail]:
        """
        Hitung diskon kategori untuk semua kategori yang memenuhi syarat
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            List[DiscountDetail]: List diskon per kategori
        """
        discounts = []
        category_totals = cart.get_category_totals()
        
        for category, rule in self._category_rules.items():
            if category in category_totals:
                category_data = category_totals[category]
                
                if category_data['quantity'] >= rule['min_items']:
                    discount_amount = int(category_data['amount'] * rule['percentage'])
                    
                    discounts.append(DiscountDetail(
                        name=f"Diskon Kategori {category.value.title()}",
                        amount=discount_amount,
                        percentage=rule['percentage'],
                        description=f"Diskon {rule['percentage']*100:.0f}% untuk "
                                  f"{category.value} ≥ {rule['min_items']} item"
                    ))
        
        return discounts


class DayOfWeekDiscountStrategy(DiscountStrategy):
    """
    Strategi diskon berdasarkan hari dalam seminggu
    
    Prinsip OOP:
    - Strategy Pattern: Implementasi diskon berbasis waktu
    - Configuration: Mudah dikonfigurasi untuk hari berbeda
    """
    
    def __init__(self):
        """Constructor untuk DayOfWeekDiscountStrategy"""
        # Konfigurasi diskon per hari (0=Senin, 1=Selasa, ..., 6=Minggu)
        self._day_discounts = {
            0: {'percentage': 0.15, 'name': 'Diskon Hari Senin'},  # Senin
            5: {'percentage': 0.20, 'name': 'Diskon Hari Sabtu'}   # Sabtu
        }
    
    def is_applicable(self, cart: ShoppingCart, customer: BaseCustomer) -> bool:
        """
        Cek apakah hari ini ada diskon
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            bool: True jika hari ini ada diskon
        """
        today = datetime.now().weekday()
        return today in self._day_discounts
    
    def calculate_discount(self, cart: ShoppingCart, customer: BaseCustomer) -> DiscountDetail:
        """
        Hitung diskon berdasarkan hari
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            DiscountDetail: Detail diskon hari
        """
        today = datetime.now().weekday()
        
        if not self.is_applicable(cart, customer):
            return DiscountDetail("Diskon Hari", 0, 0.0, "Tidak ada diskon hari ini")
        
        day_config = self._day_discounts[today]
        subtotal = cart.calculate_subtotal()
        discount_amount = int(subtotal * day_config['percentage'])
        
        day_names = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
        
        return DiscountDetail(
            name=day_config['name'],
            amount=discount_amount,
            percentage=day_config['percentage'],
            description=f"Diskon spesial hari {day_names[today]} "
                       f"{day_config['percentage']*100:.0f}%"
        )


class DiscountService:
    """
    Service utama untuk perhitungan diskon
    
    Prinsip OOP yang diterapkan:
    - Dependency Injection: Menerima strategies dari luar
    - Strategy Pattern: Menggunakan berbagai strategi diskon
    - Single Responsibility: Hanya mengkoordinasi perhitungan diskon
    - Open/Closed: Mudah ditambah strategi baru tanpa ubah kode
    """
    
    def __init__(self, strategies: List[DiscountStrategy] = None):
        """
        Constructor untuk DiscountService
        
        Args:
            strategies (List[DiscountStrategy]): List strategi diskon
        """
        # Default strategies jika tidak diberikan
        if strategies is None:
            strategies = [
                SeniorDiscountStrategy(),
                MemberDiscountStrategy(),
                DayOfWeekDiscountStrategy()
            ]
        
        self._strategies = strategies
        self._category_strategy = CategoryDiscountStrategy()
    
    def add_strategy(self, strategy: DiscountStrategy) -> None:
        """
        Menambah strategi diskon baru
        
        Args:
            strategy (DiscountStrategy): Strategi diskon baru
        """
        if strategy not in self._strategies:
            self._strategies.append(strategy)
    
    def remove_strategy(self, strategy_type: type) -> bool:
        """
        Menghapus strategi diskon berdasarkan tipe
        
        Args:
            strategy_type (type): Tipe strategi yang akan dihapus
            
        Returns:
            bool: True jika berhasil dihapus
        """
        for i, strategy in enumerate(self._strategies):
            if isinstance(strategy, strategy_type):
                del self._strategies[i]
                return True
        return False
    
    def calculate_all_discounts(self, cart: ShoppingCart, 
                              customer: BaseCustomer) -> List[DiscountDetail]:
        """
        Menghitung semua diskon yang berlaku
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            List[DiscountDetail]: List semua diskon yang berlaku
        """
        all_discounts = []
        
        # Hitung diskon dari semua strategies
        for strategy in self._strategies:
            if strategy.is_applicable(cart, customer):
                discount = strategy.calculate_discount(cart, customer)
                if discount.amount > 0:
                    all_discounts.append(discount)
        
        # Hitung diskon kategori (bisa multiple)
        if self._category_strategy.is_applicable(cart, customer):
            category_discounts = self._category_strategy.calculate_discount(cart, customer)
            all_discounts.extend(category_discounts)
        
        return all_discounts
    
    def get_total_discount_amount(self, cart: ShoppingCart, 
                                customer: BaseCustomer) -> int:
        """
        Mendapatkan total semua diskon
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            int: Total amount diskon
        """
        discounts = self.calculate_all_discounts(cart, customer)
        return sum(discount.amount for discount in discounts)
    
    def get_discount_summary(self, cart: ShoppingCart, 
                           customer: BaseCustomer) -> Dict[str, any]:
        """
        Mendapatkan ringkasan diskon
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            customer (BaseCustomer): Customer
            
        Returns:
            Dict[str, any]: Ringkasan diskon
        """
        discounts = self.calculate_all_discounts(cart, customer)
        total_amount = sum(discount.amount for discount in discounts)
        
        return {
            'discounts': discounts,
            'total_discount_amount': total_amount,
            'discount_count': len(discounts),
            'original_subtotal': cart.calculate_subtotal(),
            'subtotal_after_discount': cart.calculate_subtotal() - total_amount
        }
