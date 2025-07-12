"""
INPUT UTILITIES - Utility classes untuk input handling
====================================================
Implementasi OOP untuk input handling dengan prinsip:
- Single Responsibility: Setiap class punya tugas spesifik
- Validation: Validasi input yang robust
- Error Handling: Penanganan error yang baik
- Reusability: Bisa digunakan di berbagai tempat
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, List, Callable, Dict
import sys


class InputValidator(ABC):
    """
    Abstract base class untuk input validator - Strategy Pattern
    Mendefinisikan interface untuk validasi input
    """
    
    @abstractmethod
    def validate(self, value: Any) -> tuple[bool, str]:
        """
        Method abstract untuk validasi
        
        Args:
            value (Any): Value yang akan divalidasi
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        pass


class IntegerValidator(InputValidator):
    """
    Validator untuk input integer
    
    Prinsip OOP:
    - Single Responsibility: Hanya validasi integer
    - Strategy Pattern: Implementasi konkret dari InputValidator
    """
    
    def __init__(self, min_value: int = None, max_value: int = None):
        """
        Constructor untuk IntegerValidator
        
        Args:
            min_value (int, optional): Nilai minimum
            max_value (int, optional): Nilai maksimum
        """
        self._min_value = min_value
        self._max_value = max_value
    
    def validate(self, value: Any) -> tuple[bool, str]:
        """
        Validasi input integer
        
        Args:
            value (Any): Value yang akan divalidasi
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        try:
            int_value = int(value)
            
            # Cek range jika ditentukan
            if self._min_value is not None and int_value < self._min_value:
                return False, f"Nilai harus minimal {self._min_value}"
            
            if self._max_value is not None and int_value > self._max_value:
                return False, f"Nilai harus maksimal {self._max_value}"
            
            return True, ""
            
        except (ValueError, TypeError):
            return False, "Input harus berupa angka"


class StringValidator(InputValidator):
    """
    Validator untuk input string
    
    Prinsip OOP:
    - Single Responsibility: Hanya validasi string
    - Configuration: Berbagai konfigurasi validasi
    """
    
    def __init__(self, min_length: int = 1, max_length: int = 100,
                 allow_empty: bool = False, required_chars: str = None):
        """
        Constructor untuk StringValidator
        
        Args:
            min_length (int): Panjang minimum
            max_length (int): Panjang maksimum
            allow_empty (bool): Boleh kosong atau tidak
            required_chars (str): Karakter yang harus ada
        """
        self._min_length = min_length
        self._max_length = max_length
        self._allow_empty = allow_empty
        self._required_chars = required_chars
    
    def validate(self, value: Any) -> tuple[bool, str]:
        """
        Validasi input string
        
        Args:
            value (Any): Value yang akan divalidasi
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not isinstance(value, str):
            return False, "Input harus berupa text"
        
        value = value.strip()
        
        # Cek empty
        if not value and not self._allow_empty:
            return False, "Input tidak boleh kosong"
        
        # Cek panjang
        if len(value) < self._min_length:
            return False, f"Input harus minimal {self._min_length} karakter"
        
        if len(value) > self._max_length:
            return False, f"Input maksimal {self._max_length} karakter"
        
        # Cek required chars
        if self._required_chars:
            if not any(char in value for char in self._required_chars):
                return False, f"Input harus mengandung salah satu: {self._required_chars}"
        
        return True, ""


class ChoiceValidator(InputValidator):
    """
    Validator untuk input pilihan (choice)
    
    Prinsip OOP:
    - Single Responsibility: Hanya validasi choice
    - Flexibility: Support berbagai tipe choice
    """
    
    def __init__(self, choices: List[Any], case_sensitive: bool = False):
        """
        Constructor untuk ChoiceValidator
        
        Args:
            choices (List[Any]): List pilihan yang valid
            case_sensitive (bool): Apakah case sensitive
        """
        self._choices = choices
        self._case_sensitive = case_sensitive
        
        if not case_sensitive:
            self._choices = [str(choice).lower() for choice in choices]
    
    def validate(self, value: Any) -> tuple[bool, str]:
        """
        Validasi input choice
        
        Args:
            value (Any): Value yang akan divalidasi
            
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        check_value = value
        if not self._case_sensitive:
            check_value = str(value).lower()
        
        if check_value in self._choices:
            return True, ""
        
        choices_str = ", ".join(str(choice) for choice in self._choices)
        return False, f"Pilihan harus salah satu dari: {choices_str}"


class InputHandler:
    """
    Class utama untuk handling input dengan validasi
    
    Prinsip OOP yang diterapkan:
    - Strategy Pattern: Menggunakan validator strategies
    - Template Method: Template untuk input process
    - Error Handling: Penanganan error yang konsisten
    - Retry Logic: Logic untuk retry input
    """
    
    def __init__(self, max_retries: int = 3):
        """
        Constructor untuk InputHandler
        
        Args:
            max_retries (int): Maksimal retry untuk input
        """
        self._max_retries = max_retries
    
    def get_input(self, prompt: str, validator: InputValidator = None,
                  converter: Callable = None, default: Any = None) -> Any:
        """
        Method umum untuk mendapatkan input dengan validasi
        
        Args:
            prompt (str): Prompt untuk input
            validator (InputValidator): Validator untuk input
            converter (Callable): Function untuk convert input
            default (Any): Default value jika input kosong
            
        Returns:
            Any: Input yang sudah divalidasi dan dikonversi
        """
        for attempt in range(self._max_retries + 1):
            try:
                # Tampilkan prompt
                if default is not None:
                    display_prompt = f"{prompt} (default: {default}): "
                else:
                    display_prompt = f"{prompt}: "
                
                raw_input = input(display_prompt).strip()
                
                # Gunakan default jika input kosong
                if not raw_input and default is not None:
                    return default
                
                # Validasi jika ada validator
                if validator:
                    is_valid, error_message = validator.validate(raw_input)
                    if not is_valid:
                        print(f"❌ {error_message}")
                        if attempt < self._max_retries:
                            continue
                        else:
                            raise ValueError("Maksimal retry tercapai")
                
                # Convert jika ada converter
                if converter:
                    try:
                        return converter(raw_input)
                    except Exception as e:
                        print(f"❌ Error konversi: {e}")
                        if attempt < self._max_retries:
                            continue
                        else:
                            raise ValueError("Error konversi input")
                
                return raw_input
                
            except KeyboardInterrupt:
                print("\n❌ Input dibatalkan oleh user")
                sys.exit(0)
            except EOFError:
                print("\n❌ Input tidak valid")
                if attempt < self._max_retries:
                    continue
                else:
                    raise ValueError("Input tidak dapat dibaca")
        
        raise ValueError("Gagal mendapatkan input yang valid")
    
    def get_integer(self, prompt: str, min_value: int = None, 
                   max_value: int = None, default: int = None) -> int:
        """
        Method khusus untuk input integer
        
        Args:
            prompt (str): Prompt untuk input
            min_value (int, optional): Nilai minimum
            max_value (int, optional): Nilai maksimum
            default (int, optional): Default value
            
        Returns:
            int: Integer yang sudah divalidasi
        """
        validator = IntegerValidator(min_value, max_value)
        return self.get_input(prompt, validator, int, default)
    
    def get_string(self, prompt: str, min_length: int = 1, 
                  max_length: int = 100, allow_empty: bool = False,
                  default: str = None) -> str:
        """
        Method khusus untuk input string
        
        Args:
            prompt (str): Prompt untuk input
            min_length (int): Panjang minimum
            max_length (int): Panjang maksimum
            allow_empty (bool): Boleh kosong atau tidak
            default (str, optional): Default value
            
        Returns:
            str: String yang sudah divalidasi
        """
        validator = StringValidator(min_length, max_length, allow_empty)
        return self.get_input(prompt, validator, str.strip, default)
    
    def get_choice(self, prompt: str, choices: List[Any], 
                  case_sensitive: bool = False, default: Any = None) -> Any:
        """
        Method khusus untuk input pilihan
        
        Args:
            prompt (str): Prompt untuk input
            choices (List[Any]): List pilihan yang valid
            case_sensitive (bool): Apakah case sensitive
            default (Any, optional): Default value
            
        Returns:
            Any: Choice yang sudah divalidasi
        """
        validator = ChoiceValidator(choices, case_sensitive)
        
        # Tampilkan pilihan
        choices_str = ", ".join(str(choice) for choice in choices)
        full_prompt = f"{prompt} ({choices_str})"
        
        result = self.get_input(full_prompt, validator, None, default)
        
        # Convert back ke original case jika tidak case sensitive
        if not case_sensitive:
            for choice in choices:
                if str(choice).lower() == str(result).lower():
                    return choice
        
        return result
    
    def get_yes_no(self, prompt: str, default: bool = None) -> bool:
        """
        Method khusus untuk input yes/no
        
        Args:
            prompt (str): Prompt untuk input
            default (bool, optional): Default value
            
        Returns:
            bool: True untuk yes, False untuk no
        """
        choices = ['y', 'yes', 'n', 'no']
        default_str = None
        
        if default is not None:
            default_str = 'y' if default else 'n'
        
        result = self.get_choice(prompt, choices, False, default_str)
        return result.lower() in ['y', 'yes']
    
    def get_multiple_integers(self, prompt: str, count: int,
                            min_value: int = None, max_value: int = None) -> List[int]:
        """
        Method untuk input multiple integers
        
        Args:
            prompt (str): Prompt untuk input
            count (int): Jumlah integer yang dibutuhkan
            min_value (int, optional): Nilai minimum
            max_value (int, optional): Nilai maksimum
            
        Returns:
            List[int]: List integer yang sudah divalidasi
        """
        results = []
        for i in range(count):
            value = self.get_integer(f"{prompt} #{i+1}", min_value, max_value)
            results.append(value)
        return results


class MenuHandler:
    """
    Class khusus untuk handling menu selection
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani menu
    - Template Method: Template untuk menu display
    - Strategy Pattern: Berbagai tipe menu
    """
    
    def __init__(self, input_handler: InputHandler = None):
        """
        Constructor untuk MenuHandler
        
        Args:
            input_handler (InputHandler): Handler untuk input
        """
        self._input_handler = input_handler or InputHandler()
    
    def display_menu(self, title: str, options: Dict[str, str],
                    allow_exit: bool = True) -> str:
        """
        Display menu dan dapatkan pilihan user
        
        Args:
            title (str): Judul menu
            options (Dict[str, str]): Dictionary {key: description}
            allow_exit (bool): Tampilkan opsi exit
            
        Returns:
            str: Key pilihan user
        """
        print(f"\n{'='*50}")
        print(f"{title.center(50)}")
        print('='*50)
        
        # Tampilkan opsi
        for key, description in options.items():
            print(f"{key}. {description}")
        
        if allow_exit:
            print("0. Keluar")
            choices = list(options.keys()) + ['0']
        else:
            choices = list(options.keys())
        
        print("-" * 50)
        
        choice = self._input_handler.get_choice("Pilih menu", choices)
        return choice
    
    def display_numbered_menu(self, title: str, items: List[str],
                            allow_exit: bool = True) -> int:
        """
        Display menu dengan nomor otomatis
        
        Args:
            title (str): Judul menu
            items (List[str]): List item menu
            allow_exit (bool): Tampilkan opsi exit
            
        Returns:
            int: Index pilihan user (0-based)
        """
        print(f"\n{'='*50}")
        print(f"{title.center(50)}")
        print('='*50)
        
        # Tampilkan items dengan nomor
        for i, item in enumerate(items, 1):
            print(f"{i}. {item}")
        
        if allow_exit:
            print("0. Kembali")
            max_choice = len(items)
            min_choice = 0
        else:
            max_choice = len(items)
            min_choice = 1
        
        print("-" * 50)
        
        choice = self._input_handler.get_integer(
            "Pilih nomor", min_choice, max_choice
        )
        
        if choice == 0:
            return -1  # Indicator untuk exit
        else:
            return choice - 1  # Convert ke 0-based index


class ProgressDisplay:
    """
    Class untuk menampilkan progress dan loading
    
    Prinsip OOP:
    - Single Responsibility: Hanya menangani display progress
    - State Management: Mengelola state progress
    """
    
    def __init__(self):
        """Constructor untuk ProgressDisplay"""
        self._is_active = False
    
    def show_loading(self, message: str = "Loading", duration: int = 1) -> None:
        """
        Tampilkan loading animation
        
        Args:
            message (str): Pesan loading
            duration (int): Durasi dalam detik
        """
        import time
        
        self._is_active = True
        
        frames = ['|', '/', '-', '\\']
        end_time = time.time() + duration
        
        print(f"\n{message} ", end='', flush=True)
        
        frame_index = 0
        while time.time() < end_time and self._is_active:
            print(f"\r{message} {frames[frame_index]}", end='', flush=True)
            frame_index = (frame_index + 1) % len(frames)
            time.sleep(0.1)
        
        print(f"\r{message} ✅")
        self._is_active = False
    
    def show_progress_bar(self, current: int, total: int, 
                         width: int = 50, message: str = "") -> None:
        """
        Tampilkan progress bar
        
        Args:
            current (int): Progress saat ini
            total (int): Total progress
            width (int): Lebar progress bar
            message (str): Pesan tambahan
        """
        if total == 0:
            percentage = 100
        else:
            percentage = min(100, (current * 100) // total)
        
        filled = (percentage * width) // 100
        bar = '█' * filled + '░' * (width - filled)
        
        print(f"\r{message} [{bar}] {percentage}%", end='', flush=True)
        
        if percentage == 100:
            print()  # New line when complete
