"""
CUSTOMER MODEL - Model untuk representasi pelanggan
==================================================
Implementasi OOP untuk entitas Customer dengan prinsip:
- Encapsulation: Data dan method dikapsulasi dalam class
- Inheritance: Base class dan derived class untuk tipe customer
- Validation: Validasi data customer
- Clean Code: Single Responsibility Principle
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
from datetime import datetime


class BaseCustomer(ABC):
    """
    Abstract Base Class untuk Customer - menerapkan prinsip Abstraction
    Mendefinisikan kontrak yang harus diimplementasi oleh semua tipe customer
    """
    
    @abstractmethod
    def get_discount_multiplier(self) -> float:
        """Method abstract untuk mendapatkan multiplier diskon"""
        pass
    
    @abstractmethod
    def get_customer_type(self) -> str:
        """Method abstract untuk mendapatkan tipe customer"""
        pass


class Customer(BaseCustomer):
    """
    Class Customer yang merepresentasikan pelanggan toko
    
    Prinsip OOP yang diterapkan:
    - Encapsulation: Data private dengan getter/setter
    - Inheritance: Mewarisi dari BaseCustomer
    - Validation: Validasi input umur dan nama
    - Single Responsibility: Hanya menangani data customer
    """
    
    def __init__(self, nama: str, umur: int, is_member: bool = False):
        """
        Constructor untuk inisialisasi Customer
        
        Args:
            nama (str): Nama pelanggan
            umur (int): Umur pelanggan
            is_member (bool): Status membership (default: False)
            
        Raises:
            ValueError: Jika ada input yang tidak valid
        """
        self._validate_inputs(nama, umur)
        
        # Private attributes - Encapsulation
        self._nama = nama.strip().title()
        self._umur = umur
        self._is_member = is_member
        self._created_at = datetime.now()
    
    def _validate_inputs(self, nama: str, umur: int) -> None:
        """
        Private method untuk validasi input - Encapsulation
        
        Args:
            nama (str): Nama pelanggan
            umur (int): Umur pelanggan
            
        Raises:
            ValueError: Jika ada input yang tidak valid
        """
        if not nama or not nama.strip():
            raise ValueError("Nama pelanggan tidak boleh kosong")
        
        if umur < 0 or umur > 150:
            raise ValueError("Umur pelanggan harus antara 0-150 tahun")
    
    # Getter methods - Encapsulation
    @property
    def nama(self) -> str:
        """Getter untuk nama pelanggan"""
        return self._nama
    
    @property
    def umur(self) -> int:
        """Getter untuk umur pelanggan"""
        return self._umur
    
    @property
    def is_member(self) -> bool:
        """Getter untuk status membership"""
        return self._is_member
    
    @property
    def created_at(self) -> datetime:
        """Getter untuk waktu pembuatan customer"""
        return self._created_at
    
    # Setter methods dengan validasi - Encapsulation
    @is_member.setter
    def is_member(self, value: bool) -> None:
        """
        Setter untuk status membership
        
        Args:
            value (bool): Status membership baru
        """
        self._is_member = value
    
    def get_discount_multiplier(self) -> float:
        """
        Implementasi method abstract dari BaseCustomer
        Menghitung multiplier diskon berdasarkan status member
        
        Returns:
            float: Multiplier diskon (0.05 untuk member, 0.0 untuk non-member)
        """
        return 0.05 if self._is_member else 0.0
    
    def get_customer_type(self) -> str:
        """
        Implementasi method abstract dari BaseCustomer
        
        Returns:
            str: Tipe customer
        """
        return "Member" if self._is_member else "Regular"
    
    def is_senior(self) -> bool:
        """
        Method untuk mengecek apakah customer termasuk lansia
        
        Returns:
            bool: True jika umur >= 60, False sebaliknya
        """
        return self._umur >= 60
    
    def upgrade_to_member(self) -> bool:
        """
        Method untuk upgrade customer menjadi member
        
        Returns:
            bool: True jika berhasil upgrade, False jika sudah member
        """
        if not self._is_member:
            self._is_member = True
            return True
        return False
    
    def get_age_category(self) -> str:
        """
        Method untuk mendapatkan kategori umur
        
        Returns:
            str: Kategori umur (anak, dewasa, lansia)
        """
        if self._umur < 18:
            return "Anak"
        elif self._umur < 60:
            return "Dewasa"
        else:
            return "Lansia"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Method untuk mengkonversi object ke dictionary
        
        Returns:
            Dict[str, Any]: Representasi object dalam bentuk dictionary
        """
        return {
            'nama': self._nama,
            'umur': self._umur,
            'is_member': self._is_member,
            'customer_type': self.get_customer_type(),
            'age_category': self.get_age_category(),
            'is_senior': self.is_senior(),
            'discount_multiplier': self.get_discount_multiplier(),
            'created_at': self._created_at.isoformat()
        }
    
    def __str__(self) -> str:
        """
        Method untuk string representation
        
        Returns:
            str: String representation dari customer
        """
        member_status = "Member" if self._is_member else "Non-Member"
        return f"{self._nama} ({self._umur} tahun) - {member_status}"
    
    def __repr__(self) -> str:
        """
        Method untuk detailed representation (debugging)
        
        Returns:
            str: Detailed string representation
        """
        return (f"Customer(nama='{self._nama}', umur={self._umur}, "
                f"is_member={self._is_member})")
    
    def __eq__(self, other) -> bool:
        """
        Method untuk equality comparison
        
        Args:
            other: Object lain untuk dibandingkan
            
        Returns:
            bool: True jika sama, False jika berbeda
        """
        if not isinstance(other, Customer):
            return False
        return (self._nama == other._nama and 
                self._umur == other._umur)


class PremiumCustomer(Customer):
    """
    Class untuk Premium Customer - menerapkan prinsip Inheritance
    Customer dengan benefit tambahan dan diskon lebih besar
    
    Prinsip OOP:
    - Inheritance: Mewarisi dari Customer
    - Polymorphism: Override method untuk behavior berbeda
    - Encapsulation: Data tambahan untuk premium customer
    """
    
    def __init__(self, nama: str, umur: int, membership_points: int = 0):
        """
        Constructor untuk PremiumCustomer
        
        Args:
            nama (str): Nama pelanggan
            umur (int): Umur pelanggan
            membership_points (int): Poin membership (default: 0)
        """
        # Memanggil constructor parent - Inheritance
        super().__init__(nama, umur, is_member=True)
        
        # Data tambahan untuk premium customer
        self._membership_points = max(0, membership_points)
        self._tier = self._calculate_tier()
    
    def _calculate_tier(self) -> str:
        """
        Private method untuk menghitung tier berdasarkan points
        
        Returns:
            str: Tier customer (Bronze, Silver, Gold, Platinum)
        """
        if self._membership_points >= 10000:
            return "Platinum"
        elif self._membership_points >= 5000:
            return "Gold"
        elif self._membership_points >= 1000:
            return "Silver"
        else:
            return "Bronze"
    
    @property
    def membership_points(self) -> int:
        """Getter untuk membership points"""
        return self._membership_points
    
    @property
    def tier(self) -> str:
        """Getter untuk tier customer"""
        return self._tier
    
    def add_points(self, points: int) -> None:
        """
        Method untuk menambah membership points
        
        Args:
            points (int): Jumlah points yang ditambahkan
        """
        if points > 0:
            self._membership_points += points
            self._tier = self._calculate_tier()
    
    def get_discount_multiplier(self) -> float:
        """
        Override method dari parent - Polymorphism
        Premium customer mendapat diskon lebih besar berdasarkan tier
        
        Returns:
            float: Multiplier diskon berdasarkan tier
        """
        tier_discounts = {
            "Bronze": 0.07,    # 7%
            "Silver": 0.10,    # 10%
            "Gold": 0.15,      # 15%
            "Platinum": 0.20   # 20%
        }
        return tier_discounts.get(self._tier, 0.05)
    
    def get_customer_type(self) -> str:
        """
        Override method dari parent
        
        Returns:
            str: Tipe customer dengan tier
        """
        return f"Premium {self._tier}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Override method dari parent
        Menambahkan informasi premium customer
        
        Returns:
            Dict[str, Any]: Dictionary representation dengan data premium
        """
        data = super().to_dict()
        data.update({
            'membership_points': self._membership_points,
            'tier': self._tier,
            'is_premium': True
        })
        return data
    
    def __str__(self) -> str:
        """
        Override string representation
        
        Returns:
            str: String dengan informasi premium customer
        """
        return (f"{self._nama} ({self._umur} tahun) - "
                f"Premium {self._tier} ({self._membership_points} points)")


class VIPCustomer(PremiumCustomer):
    """
    Class untuk VIP Customer - menerapkan prinsip Multi-level Inheritance
    Customer dengan benefit paling tinggi
    
    Prinsip OOP:
    - Multi-level Inheritance: Customer -> PremiumCustomer -> VIPCustomer
    - Polymorphism: Override method untuk behavior khusus VIP
    """
    
    def __init__(self, nama: str, umur: int, membership_points: int = 0, 
                 personal_assistant: str = ""):
        """
        Constructor untuk VIPCustomer
        
        Args:
            nama (str): Nama pelanggan
            umur (int): Umur pelanggan
            membership_points (int): Poin membership
            personal_assistant (str): Nama personal assistant
        """
        # Memanggil constructor parent
        super().__init__(nama, umur, membership_points)
        
        self._personal_assistant = personal_assistant.strip()
        self._vip_benefits = [
            "Free delivery",
            "Priority service", 
            "Exclusive discounts",
            "Personal assistant"
        ]
    
    @property
    def personal_assistant(self) -> str:
        """Getter untuk personal assistant"""
        return self._personal_assistant
    
    @property
    def vip_benefits(self) -> list:
        """Getter untuk VIP benefits"""
        return self._vip_benefits.copy()
    
    def get_discount_multiplier(self) -> float:
        """
        Override method dari parent
        VIP customer mendapat diskon tetap 25%
        
        Returns:
            float: Multiplier diskon VIP (0.25)
        """
        return 0.25  # 25% discount untuk VIP
    
    def get_customer_type(self) -> str:
        """
        Override method dari parent
        
        Returns:
            str: Tipe customer VIP
        """
        return "VIP"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Override method dari parent
        Menambahkan informasi VIP customer
        
        Returns:
            Dict[str, Any]: Dictionary representation dengan data VIP
        """
        data = super().to_dict()
        data.update({
            'personal_assistant': self._personal_assistant,
            'vip_benefits': self._vip_benefits,
            'is_vip': True
        })
        return data
    
    def __str__(self) -> str:
        """
        Override string representation
        
        Returns:
            str: String dengan informasi VIP customer
        """
        assistant_info = f" (PA: {self._personal_assistant})" if self._personal_assistant else ""
        return f"{self._nama} ({self._umur} tahun) - VIP{assistant_info}"
