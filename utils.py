"""
Утилиты для валидации и форматирования
"""
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """Валидация email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def normalize_email(email: str) -> str:
    """Нормализация email (lowercase, trim)"""
    return email.lower().strip()

def validate_inn(inn: str) -> bool:
    """Валидация ИНН (10 или 12 цифр)"""
    inn = inn.strip()
    return inn.isdigit() and len(inn) in [10, 12]

def normalize_inn(inn: str) -> str:
    """Нормализация ИНН (только цифры)"""
    return ''.join(filter(str.isdigit, inn))

def mask_inn(inn: str) -> str:
    """Маскировка ИНН для отображения"""
    if len(inn) == 10:
        return f"{inn[:3]}***{inn[-2:]}"
    elif len(inn) == 12:
        return f"{inn[:4]}****{inn[-2:]}"
    return inn

def mask_email(email: str) -> str:
    """Маскировка email для отображения"""
    if '@' not in email:
        return email
    
    local, domain = email.split('@')
    if len(local) <= 2:
        masked_local = local[0] + '*'
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]
    
    return f"{masked_local}@{domain}"
