"""
Extractor de entidades de mensajes usando regex y NLP básico.
Detecta fechas, horas y cantidad de personas en texto natural.
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from utils.logger import app_logger


class EntityExtractor:

    PARTY_SIZE_PATTERNS = [
        r'(\d+)\s*personas?',
        r'para\s*(\d+)',
        r'somos\s*(\d+)',
        r'mesa\s*para\s*(\d+)',
        r'(\d+)\s*comensales?'
    ]
    
    TIME_PATTERNS = [
        r'(\d{1,2}):(\d{2})',  # 20:00, 8:30
        r'(\d{1,2})\s*(?:pm|am)',  # 8pm, 9am
        r'(\d{1,2})\s*de\s*la\s*(?:tarde|noche|mañana)',  # 8 de la noche
    ]
    
    DATE_KEYWORDS = {
        'hoy': 0,
        'mañana': 1,
        'pasado mañana': 2,
        'pasado': 2
    }
    
    @staticmethod
    def extract_party_size(text: str) -> Optional[int]:
        """
        Extrae la cantidad de personas del texto.
        
        Ejemplos:
            "para 4 personas" -> 4
            "somos 2" -> 2
            "mesa para 6" -> 6
        
        Args:
            text: Texto del mensaje
            
        Returns:
            Cantidad de personas o None si no se encuentra
        """
        text_lower = text.lower()
        
        for pattern in EntityExtractor.PARTY_SIZE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    party_size = int(match.group(1))
                    if 1 <= party_size <= 50:  # Validación razonable
                        app_logger.debug(f"Party size extraído: {party_size}")
                        return party_size
                except (ValueError, IndexError):
                    continue
        
        return None
    
    @staticmethod
    def extract_time(text: str) -> Optional[str]:
        """
        Extrae la hora del texto y la normaliza a formato HH:MM.
        
        Ejemplos:
            "a las 20:00" -> "20:00"
            "8pm" -> "20:00"
            "8 de la noche" -> "20:00"
        
        Args:
            text: Texto del mensaje
            
        Returns:
            Hora en formato HH:MM o None si no se encuentra
        """
        text_lower = text.lower()
        
        # Patrón HH:MM
        match = re.search(r'(\d{1,2}):(\d{2})', text_lower)
        if match:
            hour = int(match.group(1))
            minute = int(match.group(2))
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
        
        # Patrón con PM/AM
        match = re.search(r'(\d{1,2})\s*(?:pm|am)', text_lower)
        if match:
            hour = int(match.group(1))
            is_pm = 'pm' in text_lower
            
            if is_pm and hour != 12:
                hour += 12
            elif not is_pm and hour == 12:
                hour = 0
            
            if 0 <= hour <= 23:
                return f"{hour:02d}:00"
        
        # Patrón "X de la tarde/noche/mañana"
        match = re.search(r'(\d{1,2})\s*de\s*la\s*(tarde|noche|mañana)', text_lower)
        if match:
            hour = int(match.group(1))
            period = match.group(2)
            
            if period == 'tarde' and hour < 12:
                hour += 12
            elif period == 'noche' and hour < 12:
                hour += 12
            
            if 0 <= hour <= 23:
                return f"{hour:02d}:00"
        
        return None
    
    @staticmethod
    def extract_date(text: str) -> Optional[datetime]:
        """
        Extrae la fecha del texto.
        
        Ejemplos:
            "hoy" -> fecha de hoy
            "mañana" -> fecha de mañana
            "15/01/2026" -> 2026-01-15
        
        Args:
            text: Texto del mensaje
            
        Returns:
            Objeto datetime o None si no se encuentra
        """
        text_lower = text.lower()
        
        # Buscar palabras clave relativas
        for keyword, days_offset in EntityExtractor.DATE_KEYWORDS.items():
            if keyword in text_lower:
                target_date = datetime.now() + timedelta(days=days_offset)
                app_logger.debug(f"Fecha extraída: {target_date.date()} (keyword: {keyword})")
                return target_date
        
        # Buscar formato DD/MM/YYYY o DD-MM-YYYY
        match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', text_lower)
        if match:
            try:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                target_date = datetime(year, month, day)
                app_logger.debug(f"Fecha extraída: {target_date.date()}")
                return target_date
            except ValueError:
                pass
        
        return None
    
    @staticmethod
    def extract_all(text: str) -> Dict[str, Any]:
        """
        Extrae todas las entidades del texto.
        
        Args:
            text: Texto del mensaje
            
        Returns:
            Diccionario con las entidades extraídas
        """
        return {
            "party_size": EntityExtractor.extract_party_size(text),
            "time": EntityExtractor.extract_time(text),
            "date": EntityExtractor.extract_date(text)
        }