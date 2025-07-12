"""
TRANSACTION MODEL - Model untuk representasi transaksi
====================================================
Implementasi OOP untuk transaksi dengan prinsip:
- Encapsulation: Data transaksi ter-encapsulasi
- Immutability: Transaksi tidak bisa diubah setelah dibuat
- Value Object Pattern: Representasi data yang immutable
- Builder Pattern: Membangun transaksi secara bertahap
"""

from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cart import ShoppingCart
from models.customer import BaseCustomer


class TransactionStatus(Enum):
    """
    Enum untuk status transaksi
    """
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass(frozen=True)
class DiscountDetail:
    """
    Dataclass untuk detail diskon - Value Object Pattern
    Immutable object yang merepresentasikan satu jenis diskon
    
    Attributes:
        name (str): Nama diskon
        amount (int): Jumlah diskon dalam rupiah
        percentage (float): Persentase diskon
        description (str): Deskripsi diskon
    """
    name: str
    amount: int
    percentage: float
    description: str = ""
    
    def __post_init__(self):
        """Validasi setelah inisialisasi"""
        if self.amount < 0:
            raise ValueError("Amount diskon tidak boleh negatif")
        if not 0 <= self.percentage <= 1:
            raise ValueError("Persentase diskon harus antara 0-1")


@dataclass(frozen=True)
class PaymentDetail:
    """
    Dataclass untuk detail pembayaran - Value Object Pattern
    
    Attributes:
        amount_paid (int): Jumlah yang dibayarkan
        payment_method (str): Metode pembayaran
        change_amount (int): Kembalian
        installments (List[int]): List cicilan jika ada
    """
    amount_paid: int
    payment_method: str = "cash"
    change_amount: int = 0
    installments: List[int] = field(default_factory=list)
    
    def __post_init__(self):
        """Validasi setelah inisialisasi"""
        if self.amount_paid < 0:
            raise ValueError("Jumlah pembayaran tidak boleh negatif")
        if self.change_amount < 0:
            raise ValueError("Kembalian tidak boleh negatif")


class Transaction:
    """
    Class Transaction untuk merepresentasikan satu transaksi
    
    Prinsip OOP yang diterapkan:
    - Encapsulation: Data transaksi ter-encapsulasi
    - Immutability: Setelah dibuat, data tidak bisa diubah
    - Value Objects: Menggunakan DiscountDetail dan PaymentDetail
    - Single Responsibility: Hanya menangani data transaksi
    """
    
    def __init__(self, 
                 transaction_id: str,
                 cart: ShoppingCart,
                 subtotal: int,
                 discounts: List[DiscountDetail],
                 tax_amount: int,
                 total_amount: int,
                 payment: PaymentDetail):
        """
        Constructor untuk Transaction
        
        Args:
            transaction_id (str): ID unik transaksi
            cart (ShoppingCart): Keranjang belanja
            subtotal (int): Subtotal sebelum diskon
            discounts (List[DiscountDetail]): List detail diskon
            tax_amount (int): Jumlah pajak
            total_amount (int): Total akhir
            payment (PaymentDetail): Detail pembayaran
        """
        # Validasi input
        self._validate_inputs(transaction_id, cart, subtotal, tax_amount, total_amount)
        
        # Private attributes - Encapsulation dan Immutability
        self._transaction_id = transaction_id
        self._cart = cart
        self._customer = cart.customer
        self._subtotal = subtotal
        self._discounts = discounts.copy()  # Copy untuk immutability
        self._tax_amount = tax_amount
        self._total_amount = total_amount
        self._payment = payment
        self._status = TransactionStatus.PENDING
        self._created_at = datetime.now()
        self._completed_at: Optional[datetime] = None
        
        # Finalisasi cart agar tidak bisa diubah
        cart.finalize_cart()
    
    def _validate_inputs(self, transaction_id: str, cart: ShoppingCart, 
                        subtotal: int, tax_amount: int, total_amount: int) -> None:
        """
        Private method untuk validasi input
        
        Args:
            transaction_id (str): ID transaksi
            cart (ShoppingCart): Cart
            subtotal (int): Subtotal
            tax_amount (int): Pajak
            total_amount (int): Total
            
        Raises:
            ValueError: Jika ada input yang tidak valid
        """
        if not transaction_id or not transaction_id.strip():
            raise ValueError("Transaction ID tidak boleh kosong")
        
        if cart.is_empty:
            raise ValueError("Cart tidak boleh kosong")
        
        if subtotal < 0:
            raise ValueError("Subtotal tidak boleh negatif")
        
        if tax_amount < 0:
            raise ValueError("Tax amount tidak boleh negatif")
        
        if total_amount < 0:
            raise ValueError("Total amount tidak boleh negatif")
    
    # Getter methods - Encapsulation
    @property
    def transaction_id(self) -> str:
        """Getter untuk transaction ID"""
        return self._transaction_id
    
    @property
    def cart(self) -> ShoppingCart:
        """Getter untuk cart"""
        return self._cart
    
    @property
    def customer(self) -> BaseCustomer:
        """Getter untuk customer"""
        return self._customer
    
    @property
    def subtotal(self) -> int:
        """Getter untuk subtotal"""
        return self._subtotal
    
    @property
    def discounts(self) -> List[DiscountDetail]:
        """Getter untuk discounts (copy untuk immutability)"""
        return self._discounts.copy()
    
    @property
    def tax_amount(self) -> int:
        """Getter untuk tax amount"""
        return self._tax_amount
    
    @property
    def total_amount(self) -> int:
        """Getter untuk total amount"""
        return self._total_amount
    
    @property
    def payment(self) -> PaymentDetail:
        """Getter untuk payment detail"""
        return self._payment
    
    @property
    def status(self) -> TransactionStatus:
        """Getter untuk status"""
        return self._status
    
    @property
    def created_at(self) -> datetime:
        """Getter untuk created at"""
        return self._created_at
    
    @property
    def completed_at(self) -> Optional[datetime]:
        """Getter untuk completed at"""
        return self._completed_at
    
    def get_total_discount(self) -> int:
        """
        Method untuk mendapatkan total diskon
        
        Returns:
            int: Total semua diskon
        """
        return sum(discount.amount for discount in self._discounts)
    
    def get_discount_by_name(self, name: str) -> Optional[DiscountDetail]:
        """
        Method untuk mendapatkan diskon berdasarkan nama
        
        Args:
            name (str): Nama diskon
            
        Returns:
            Optional[DiscountDetail]: Detail diskon jika ditemukan
        """
        for discount in self._discounts:
            if discount.name.lower() == name.lower():
                return discount
        return None
    
    def complete_transaction(self) -> bool:
        """
        Method untuk menyelesaikan transaksi
        
        Returns:
            bool: True jika berhasil, False jika sudah completed
        """
        if self._status == TransactionStatus.PENDING:
            self._status = TransactionStatus.COMPLETED
            self._completed_at = datetime.now()
            return True
        return False
    
    def cancel_transaction(self) -> bool:
        """
        Method untuk membatalkan transaksi
        
        Returns:
            bool: True jika berhasil, False jika sudah completed
        """
        if self._status == TransactionStatus.PENDING:
            self._status = TransactionStatus.CANCELLED
            return True
        return False
    
    def refund_transaction(self) -> bool:
        """
        Method untuk refund transaksi
        
        Returns:
            bool: True jika berhasil, False jika tidak bisa di-refund
        """
        if self._status == TransactionStatus.COMPLETED:
            self._status = TransactionStatus.REFUNDED
            return True
        return False
    
    def is_paid_in_full(self) -> bool:
        """
        Method untuk mengecek apakah sudah lunas
        
        Returns:
            bool: True jika sudah lunas
        """
        return self._payment.amount_paid >= self._total_amount
    
    def get_outstanding_amount(self) -> int:
        """
        Method untuk mendapatkan sisa yang harus dibayar
        
        Returns:
            int: Sisa pembayaran (0 jika sudah lunas)
        """
        return max(0, self._total_amount - self._payment.amount_paid)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Method untuk mengkonversi transaksi ke dictionary
        
        Returns:
            Dict[str, Any]: Representasi transaksi dalam bentuk dictionary
        """
        return {
            'transaction_id': self._transaction_id,
            'customer': self._customer.to_dict(),
            'cart': self._cart.to_dict(),
            'subtotal': self._subtotal,
            'discounts': [
                {
                    'name': d.name,
                    'amount': d.amount,
                    'percentage': d.percentage,
                    'description': d.description
                } for d in self._discounts
            ],
            'total_discount': self.get_total_discount(),
            'tax_amount': self._tax_amount,
            'total_amount': self._total_amount,
            'payment': {
                'amount_paid': self._payment.amount_paid,
                'payment_method': self._payment.payment_method,
                'change_amount': self._payment.change_amount,
                'installments': self._payment.installments
            },
            'status': self._status.value,
            'created_at': self._created_at.isoformat(),
            'completed_at': self._completed_at.isoformat() if self._completed_at else None,
            'is_paid_in_full': self.is_paid_in_full(),
            'outstanding_amount': self.get_outstanding_amount()
        }
    
    def __str__(self) -> str:
        """
        Method untuk string representation
        
        Returns:
            str: String representation dari transaksi
        """
        return (f"Transaction {self._transaction_id}: {self._customer.nama} - "
                f"Rp{self._total_amount:,} ({self._status.value})")
    
    def __repr__(self) -> str:
        """
        Method untuk detailed representation
        
        Returns:
            str: Detailed string representation
        """
        return (f"Transaction(id='{self._transaction_id}', "
                f"customer='{self._customer.nama}', "
                f"total={self._total_amount}, status='{self._status.value}')")


class TransactionBuilder:
    """
    Builder class untuk membangun Transaction - Builder Pattern
    Memudahkan pembuatan transaksi secara bertahap
    
    Prinsip OOP:
    - Builder Pattern: Membangun object kompleks secara bertahap
    - Method Chaining: Method return self untuk chaining
    - Validation: Validasi sebelum build
    """
    
    def __init__(self):
        """Constructor untuk TransactionBuilder"""
        self._transaction_id: Optional[str] = None
        self._cart: Optional[ShoppingCart] = None
        self._subtotal: int = 0
        self._discounts: List[DiscountDetail] = []
        self._tax_amount: int = 0
        self._total_amount: int = 0
        self._payment: Optional[PaymentDetail] = None
    
    def set_transaction_id(self, transaction_id: str) -> 'TransactionBuilder':
        """
        Set transaction ID
        
        Args:
            transaction_id (str): ID transaksi
            
        Returns:
            TransactionBuilder: Self untuk method chaining
        """
        self._transaction_id = transaction_id
        return self
    
    def set_cart(self, cart: ShoppingCart) -> 'TransactionBuilder':
        """
        Set shopping cart
        
        Args:
            cart (ShoppingCart): Cart untuk transaksi
            
        Returns:
            TransactionBuilder: Self untuk method chaining
        """
        self._cart = cart
        return self
    
    def set_subtotal(self, subtotal: int) -> 'TransactionBuilder':
        """
        Set subtotal
        
        Args:
            subtotal (int): Subtotal transaksi
            
        Returns:
            TransactionBuilder: Self untuk method chaining
        """
        self._subtotal = subtotal
        return self
    
    def add_discount(self, discount: DiscountDetail) -> 'TransactionBuilder':
        """
        Tambah diskon
        
        Args:
            discount (DiscountDetail): Detail diskon
            
        Returns:
            TransactionBuilder: Self untuk method chaining
        """
        self._discounts.append(discount)
        return self
    
    def set_tax_amount(self, tax_amount: int) -> 'TransactionBuilder':
        """
        Set tax amount
        
        Args:
            tax_amount (int): Jumlah pajak
            
        Returns:
            TransactionBuilder: Self untuk method chaining
        """
        self._tax_amount = tax_amount
        return self
    
    def set_total_amount(self, total_amount: int) -> 'TransactionBuilder':
        """
        Set total amount
        
        Args:
            total_amount (int): Total akhir
            
        Returns:
            TransactionBuilder: Self untuk method chaining
        """
        self._total_amount = total_amount
        return self
    
    def set_payment(self, payment: PaymentDetail) -> 'TransactionBuilder':
        """
        Set payment detail
        
        Args:
            payment (PaymentDetail): Detail pembayaran
            
        Returns:
            TransactionBuilder: Self untuk method chaining
        """
        self._payment = payment
        return self
    
    def build(self) -> Transaction:
        """
        Build Transaction object
        
        Returns:
            Transaction: Transaction yang sudah dibuild
            
        Raises:
            ValueError: Jika ada data yang belum di-set
        """
        # Validasi data required
        if not self._transaction_id:
            raise ValueError("Transaction ID belum di-set")
        if not self._cart:
            raise ValueError("Cart belum di-set")
        if not self._payment:
            raise ValueError("Payment detail belum di-set")
        
        return Transaction(
            transaction_id=self._transaction_id,
            cart=self._cart,
            subtotal=self._subtotal,
            discounts=self._discounts,
            tax_amount=self._tax_amount,
            total_amount=self._total_amount,
            payment=self._payment
        )
    
    def reset(self) -> 'TransactionBuilder':
        """
        Reset builder untuk transaction baru
        
        Returns:
            TransactionBuilder: Self untuk method chaining
        """
        self._transaction_id = None
        self._cart = None
        self._subtotal = 0
        self._discounts = []
        self._tax_amount = 0
        self._total_amount = 0
        self._payment = None
        return self
