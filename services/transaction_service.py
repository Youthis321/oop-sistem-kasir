"""
TRANSACTION SERVICE - Service untuk pengelolaan transaksi
=======================================================
Implementasi OOP untuk business logic transaksi dengan prinsip:
- Orchestration: Mengkoordinasi semua service lain
- Transaction Management: Mengelola lifecycle transaksi
- Business Logic: Implementasi aturan bisnis
- Event-driven: Pattern untuk notifikasi dan logging
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.cart import ShoppingCart
from models.customer import BaseCustomer
from models.transaction import (
    Transaction, TransactionBuilder, DiscountDetail, 
    PaymentDetail, TransactionStatus
)
from services.discount_service import DiscountService
from services.tax_service import TaxService


class PaymentProcessor:
    """
    Class untuk memproses pembayaran - Single Responsibility
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani logic pembayaran
    - Validation: Validasi input pembayaran
    - Strategy Pattern: Berbagai metode pembayaran
    """
    
    def __init__(self):
        """Constructor untuk PaymentProcessor"""
        self._supported_methods = ['cash', 'card', 'digital', 'transfer']
    
    def validate_payment(self, total_amount: int, payment_amount: int, 
                        method: str = 'cash') -> Dict[str, Any]:
        """
        Validasi pembayaran
        
        Args:
            total_amount (int): Total yang harus dibayar
            payment_amount (int): Jumlah yang dibayarkan
            method (str): Metode pembayaran
            
        Returns:
            Dict[str, Any]: Hasil validasi
        """
        result = {
            'is_valid': False,
            'is_sufficient': False,
            'change_amount': 0,
            'outstanding_amount': 0,
            'message': ''
        }
        
        # Validasi method
        if method not in self._supported_methods:
            result['message'] = f"Metode pembayaran '{method}' tidak didukung"
            return result
        
        # Validasi amount
        if payment_amount < 0:
            result['message'] = "Jumlah pembayaran tidak boleh negatif"
            return result
        
        result['is_valid'] = True
        
        # Cek kecukupan pembayaran
        if payment_amount >= total_amount:
            result['is_sufficient'] = True
            result['change_amount'] = payment_amount - total_amount
            result['message'] = "Pembayaran berhasil"
        else:
            result['outstanding_amount'] = total_amount - payment_amount
            result['message'] = f"Kurang bayar Rp{result['outstanding_amount']:,}"
        
        return result
    
    def process_installment_payment(self, total_amount: int, 
                                  installments: List[int]) -> Dict[str, Any]:
        """
        Proses pembayaran cicilan
        
        Args:
            total_amount (int): Total yang harus dibayar
            installments (List[int]): List jumlah cicilan
            
        Returns:
            Dict[str, Any]: Hasil proses cicilan
        """
        total_paid = sum(installments)
        
        result = {
            'total_paid': total_paid,
            'is_complete': total_paid >= total_amount,
            'change_amount': max(0, total_paid - total_amount),
            'outstanding_amount': max(0, total_amount - total_paid),
            'installment_count': len(installments)
        }
        
        return result
    
    def create_payment_detail(self, amount_paid: int, method: str = 'cash',
                            installments: List[int] = None) -> PaymentDetail:
        """
        Membuat PaymentDetail object
        
        Args:
            amount_paid (int): Jumlah yang dibayarkan
            method (str): Metode pembayaran
            installments (List[int]): List cicilan
            
        Returns:
            PaymentDetail: Object detail pembayaran
        """
        if installments is None:
            installments = []
        
        return PaymentDetail(
            amount_paid=amount_paid,
            payment_method=method,
            change_amount=0,  # Akan dihitung di TransactionService
            installments=installments
        )


class TransactionOrchestrator:
    """
    Class untuk mengorkestrasikan semua service - Orchestration Pattern
    
    Prinsip OOP:
    - Orchestration: Mengkoordinasi multiple service
    - Dependency Injection: Menerima service dependencies
    - Transaction Management: Mengelola lifecycle transaksi
    """
    
    def __init__(self, discount_service: DiscountService = None,
                 tax_service: TaxService = None,
                 payment_processor: PaymentProcessor = None):
        """
        Constructor untuk TransactionOrchestrator
        
        Args:
            discount_service (DiscountService): Service untuk diskon
            tax_service (TaxService): Service untuk pajak
            payment_processor (PaymentProcessor): Processor untuk pembayaran
        """
        self._discount_service = discount_service or DiscountService()
        self._tax_service = tax_service or TaxService()
        self._payment_processor = payment_processor or PaymentProcessor()
    
    def calculate_transaction_totals(self, cart: ShoppingCart) -> Dict[str, Any]:
        """
        Menghitung total transaksi lengkap
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            
        Returns:
            Dict[str, Any]: Breakdown perhitungan transaksi
        """
        # 1. Hitung subtotal
        subtotal = cart.calculate_subtotal()
        
        # 2. Hitung diskon
        discounts = self._discount_service.calculate_all_discounts(cart, cart.customer)
        total_discount = sum(d.amount for d in discounts)
        
        # 3. Hitung subtotal setelah diskon
        subtotal_after_discount = subtotal - total_discount
        
        # 4. Hitung pajak
        taxes = self._tax_service.calculate_tax(subtotal_after_discount, cart, cart.customer)
        total_tax = sum(t.amount for t in taxes)
        
        # 5. Hitung total akhir
        total_amount = subtotal_after_discount + total_tax
        
        return {
            'subtotal': subtotal,
            'discounts': discounts,
            'total_discount': total_discount,
            'subtotal_after_discount': subtotal_after_discount,
            'taxes': taxes,
            'total_tax': total_tax,
            'total_amount': total_amount
        }
    
    def validate_transaction_data(self, cart: ShoppingCart, 
                                payment_amount: int) -> Dict[str, Any]:
        """
        Validasi data transaksi sebelum dibuat
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            payment_amount (int): Jumlah pembayaran
            
        Returns:
            Dict[str, Any]: Hasil validasi
        """
        result = {
            'is_valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Validasi cart
        if cart.is_empty:
            result['is_valid'] = False
            result['errors'].append("Keranjang belanja kosong")
        
        # Validasi customer
        if not cart.customer:
            result['is_valid'] = False
            result['errors'].append("Customer tidak valid")
        
        # Hitung total dan validasi pembayaran
        totals = self.calculate_transaction_totals(cart)
        payment_validation = self._payment_processor.validate_payment(
            totals['total_amount'], payment_amount
        )
        
        if not payment_validation['is_valid']:
            result['is_valid'] = False
            result['errors'].append(payment_validation['message'])
        
        if not payment_validation['is_sufficient']:
            result['warnings'].append(payment_validation['message'])
        
        return result


class TransactionService:
    """
    Service utama untuk pengelolaan transaksi
    
    Prinsip OOP yang diterapkan:
    - Facade Pattern: Interface sederhana untuk operasi kompleks
    - Command Pattern: Encapsulate operasi dalam method
    - Repository Pattern: Penyimpanan transaksi
    - Event-driven: Notifikasi untuk event transaksi
    """
    
    def __init__(self, orchestrator: TransactionOrchestrator = None):
        """
        Constructor untuk TransactionService
        
        Args:
            orchestrator (TransactionOrchestrator): Orchestrator untuk koordinasi
        """
        self._orchestrator = orchestrator or TransactionOrchestrator()
        self._transactions: Dict[str, Transaction] = {}
        self._transaction_history: List[Transaction] = []
    
    def create_transaction(self, cart: ShoppingCart, 
                         payment_amount: int,
                         payment_method: str = 'cash',
                         installments: List[int] = None) -> Optional[Transaction]:
        """
        Membuat transaksi baru
        
        Args:
            cart (ShoppingCart): Keranjang belanja
            payment_amount (int): Jumlah pembayaran
            payment_method (str): Metode pembayaran
            installments (List[int]): List cicilan jika ada
            
        Returns:
            Optional[Transaction]: Transaksi jika berhasil dibuat
        """
        try:
            # 1. Validasi data transaksi
            validation = self._orchestrator.validate_transaction_data(cart, payment_amount)
            if not validation['is_valid']:
                return None
            
            # 2. Hitung total transaksi
            totals = self._orchestrator.calculate_transaction_totals(cart)
            
            # 3. Proses pembayaran
            if installments:
                installment_result = self._orchestrator._payment_processor.process_installment_payment(
                    totals['total_amount'], installments
                )
                actual_payment = installment_result['total_paid']
                change_amount = installment_result['change_amount']
            else:
                installments = []
                actual_payment = payment_amount
                change_amount = max(0, payment_amount - totals['total_amount'])
            
            # 4. Buat payment detail
            payment = PaymentDetail(
                amount_paid=actual_payment,
                payment_method=payment_method,
                change_amount=change_amount,
                installments=installments
            )
            
            # 5. Generate transaction ID
            transaction_id = self._generate_transaction_id()
            
            # 6. Buat transaksi menggunakan builder
            transaction = (TransactionBuilder()
                          .set_transaction_id(transaction_id)
                          .set_cart(cart)
                          .set_subtotal(totals['subtotal'])
                          .set_tax_amount(totals['total_tax'])
                          .set_total_amount(totals['total_amount'])
                          .set_payment(payment)
                          .build())
            
            # 7. Tambahkan diskon
            for discount in totals['discounts']:
                transaction._discounts.append(discount)
            
            # 8. Simpan transaksi
            self._transactions[transaction_id] = transaction
            self._transaction_history.append(transaction)
            
            return transaction
            
        except Exception as e:
            print(f"Error creating transaction: {e}")
            return None
    
    def complete_transaction(self, transaction_id: str) -> bool:
        """
        Menyelesaikan transaksi
        
        Args:
            transaction_id (str): ID transaksi
            
        Returns:
            bool: True jika berhasil diselesaikan
        """
        transaction = self._transactions.get(transaction_id)
        if transaction:
            return transaction.complete_transaction()
        return False
    
    def cancel_transaction(self, transaction_id: str) -> bool:
        """
        Membatalkan transaksi
        
        Args:
            transaction_id (str): ID transaksi
            
        Returns:
            bool: True jika berhasil dibatalkan
        """
        transaction = self._transactions.get(transaction_id)
        if transaction:
            return transaction.cancel_transaction()
        return False
    
    def refund_transaction(self, transaction_id: str) -> bool:
        """
        Refund transaksi
        
        Args:
            transaction_id (str): ID transaksi
            
        Returns:
            bool: True jika berhasil di-refund
        """
        transaction = self._transactions.get(transaction_id)
        if transaction:
            return transaction.refund_transaction()
        return False
    
    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """
        Mendapatkan transaksi berdasarkan ID
        
        Args:
            transaction_id (str): ID transaksi
            
        Returns:
            Optional[Transaction]: Transaksi jika ditemukan
        """
        return self._transactions.get(transaction_id)
    
    def get_customer_transactions(self, customer_name: str) -> List[Transaction]:
        """
        Mendapatkan semua transaksi customer
        
        Args:
            customer_name (str): Nama customer
            
        Returns:
            List[Transaction]: List transaksi customer
        """
        return [
            t for t in self._transaction_history
            if t.customer.nama.lower() == customer_name.lower()
        ]
    
    def get_transactions_by_status(self, status: TransactionStatus) -> List[Transaction]:
        """
        Mendapatkan transaksi berdasarkan status
        
        Args:
            status (TransactionStatus): Status transaksi
            
        Returns:
            List[Transaction]: List transaksi dengan status tersebut
        """
        return [t for t in self._transaction_history if t.status == status]
    
    def get_daily_transactions(self, date: datetime = None) -> List[Transaction]:
        """
        Mendapatkan transaksi harian
        
        Args:
            date (datetime): Tanggal (default: hari ini)
            
        Returns:
            List[Transaction]: List transaksi hari tersebut
        """
        if date is None:
            date = datetime.now()
        
        target_date = date.date()
        
        return [
            t for t in self._transaction_history
            if t.created_at.date() == target_date
        ]
    
    def get_transaction_summary(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan ringkasan transaksi
        
        Args:
            transaction_id (str): ID transaksi
            
        Returns:
            Optional[Dict[str, Any]]: Ringkasan transaksi
        """
        transaction = self._transactions.get(transaction_id)
        if not transaction:
            return None
        
        return {
            'transaction': transaction.to_dict(),
            'is_profitable': transaction.total_amount > 0,
            'profit_margin': self._calculate_profit_margin(transaction),
            'items_sold': transaction.cart.total_quantity,
            'categories_involved': list(transaction.cart.get_items_by_category().keys())
        }
    
    def get_sales_analytics(self, start_date: datetime = None,
                          end_date: datetime = None) -> Dict[str, Any]:
        """
        Mendapatkan analitik penjualan
        
        Args:
            start_date (datetime): Tanggal mulai
            end_date (datetime): Tanggal akhir
            
        Returns:
            Dict[str, Any]: Analitik penjualan
        """
        # Filter transaksi berdasarkan tanggal
        filtered_transactions = self._transaction_history
        
        if start_date:
            filtered_transactions = [
                t for t in filtered_transactions 
                if t.created_at >= start_date
            ]
        
        if end_date:
            filtered_transactions = [
                t for t in filtered_transactions 
                if t.created_at <= end_date
            ]
        
        # Hitung analytics
        completed_transactions = [
            t for t in filtered_transactions 
            if t.status == TransactionStatus.COMPLETED
        ]
        
        total_revenue = sum(t.total_amount for t in completed_transactions)
        total_transactions = len(completed_transactions)
        total_items_sold = sum(t.cart.total_quantity for t in completed_transactions)
        
        return {
            'period': {
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None
            },
            'summary': {
                'total_revenue': total_revenue,
                'total_transactions': total_transactions,
                'total_items_sold': total_items_sold,
                'average_transaction_value': total_revenue // total_transactions if total_transactions > 0 else 0
            },
            'status_breakdown': self._get_status_breakdown(filtered_transactions),
            'top_customers': self._get_top_customers(completed_transactions),
            'category_performance': self._get_category_performance(completed_transactions)
        }
    
    def _generate_transaction_id(self) -> str:
        """
        Generate unique transaction ID
        
        Returns:
            str: Unique transaction ID
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"TXN_{timestamp}_{unique_id}"
    
    def _calculate_profit_margin(self, transaction: Transaction) -> float:
        """
        Hitung profit margin (simplified)
        
        Args:
            transaction (Transaction): Transaksi
            
        Returns:
            float: Profit margin
        """
        # Simplified calculation
        return 0.3  # Assume 30% profit margin
    
    def _get_status_breakdown(self, transactions: List[Transaction]) -> Dict[str, int]:
        """
        Breakdown transaksi berdasarkan status
        
        Args:
            transactions (List[Transaction]): List transaksi
            
        Returns:
            Dict[str, int]: Breakdown status
        """
        breakdown = {}
        for transaction in transactions:
            status = transaction.status.value
            breakdown[status] = breakdown.get(status, 0) + 1
        return breakdown
    
    def _get_top_customers(self, transactions: List[Transaction], 
                         limit: int = 5) -> List[Dict[str, Any]]:
        """
        Mendapatkan top customers
        
        Args:
            transactions (List[Transaction]): List transaksi
            limit (int): Limit jumlah customer
            
        Returns:
            List[Dict[str, Any]]: Top customers
        """
        customer_data = {}
        
        for transaction in transactions:
            customer_name = transaction.customer.nama
            if customer_name not in customer_data:
                customer_data[customer_name] = {
                    'name': customer_name,
                    'total_spent': 0,
                    'transaction_count': 0
                }
            
            customer_data[customer_name]['total_spent'] += transaction.total_amount
            customer_data[customer_name]['transaction_count'] += 1
        
        # Sort berdasarkan total spent
        sorted_customers = sorted(
            customer_data.values(),
            key=lambda x: x['total_spent'],
            reverse=True
        )
        
        return sorted_customers[:limit]
    
    def _get_category_performance(self, transactions: List[Transaction]) -> Dict[str, Any]:
        """
        Analisa performa per kategori
        
        Args:
            transactions (List[Transaction]): List transaksi
            
        Returns:
            Dict[str, Any]: Performance per kategori
        """
        category_data = {}
        
        for transaction in transactions:
            items_by_category = transaction.cart.get_items_by_category()
            
            for category, items in items_by_category.items():
                category_name = category.value
                
                if category_name not in category_data:
                    category_data[category_name] = {
                        'total_revenue': 0,
                        'total_items_sold': 0,
                        'transaction_count': 0
                    }
                
                category_total = sum(item.get_total_price() for item in items)
                category_items = sum(item.jumlah for item in items)
                
                category_data[category_name]['total_revenue'] += category_total
                category_data[category_name]['total_items_sold'] += category_items
                category_data[category_name]['transaction_count'] += 1
        
        return category_data
