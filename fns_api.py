"""
Модуль для работы с ФНС API
Интеграция с базой данных ИНН российских ЮЛ и ИП
"""
import aiohttp
import asyncio
import logging
from typing import Optional, Dict, Any, Union
from datetime import datetime
import config

logger = logging.getLogger(__name__)

class FNSAPI:
    """Класс для работы с ФНС API"""
    
    def __init__(self):
        self.base_url = "https://api-fns.ru/api"
        self.api_key = getattr(config, 'FNS_API_KEY', None)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'YouTravel-Bot/1.0',
                'Accept': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_company_info(self, inn: str) -> Optional[Dict[str, Any]]:
        """
        Получить информацию о компании по ИНН
        
        Args:
            inn: ИНН компании (10 или 12 цифр)
            
        Returns:
            Dict с информацией о компании или None если не найдена
        """
        if not self.session:
            raise RuntimeError("FNS API session not initialized. Use async context manager.")
        
        if not self.api_key:
            logger.warning("FNS API key not configured, using mock data")
            return await self._get_mock_company_info(inn)
        
        try:
            # Подготавливаем параметры запроса
            params = {
                'key': self.api_key,
                'inn': inn,
                'format': 'json'
            }
            
            logger.info(f"Requesting company info for INN: {inn[:3]}***")
            
            async with self.session.get(f"{self.base_url}/egr", params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('status') == 'success' and data.get('items'):
                        company_data = data['items'][0]
                        
                        # Обрабатываем и нормализуем данные
                        result = {
                            'inn': company_data.get('inn', inn),
                            'name': company_data.get('name', 'Не указано'),
                            'ogrn': company_data.get('ogrn', ''),
                            'kpp': company_data.get('kpp', ''),
                            'address': company_data.get('address', 'Не указан'),
                            'status': company_data.get('status', 'Неизвестно'),
                            'type': self._determine_company_type(company_data),
                            'registration_date': company_data.get('reg_date', ''),
                            'last_update': company_data.get('update_date', ''),
                            'is_active': company_data.get('status') == 'ACTIVE',
                            'found': True
                        }
                        
                        logger.info(f"Company found: {result['name']} ({result['type']})")
                        return result
                    else:
                        logger.warning(f"Company not found for INN: {inn}")
                        return {'found': False, 'inn': inn}
                        
                else:
                    logger.error(f"FNS API error: HTTP {response.status}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error("FNS API request timeout")
            return None
        except Exception as e:
            logger.error(f"FNS API request failed: {e}")
            return None
    
    async def validate_inn(self, inn: str) -> Dict[str, Any]:
        """
        Валидация ИНН с проверкой в базе ФНС
        
        Args:
            inn: ИНН для проверки
            
        Returns:
            Dict с результатами валидации
        """
        # Базовая валидация формата
        if not inn or not inn.isdigit():
            return {
                'valid': False,
                'error': 'ИНН должен содержать только цифры',
                'found': False
            }
        
        if len(inn) not in [10, 12]:
            return {
                'valid': False,
                'error': 'ИНН должен содержать 10 или 12 цифр',
                'found': False
            }
        
        # Проверка контрольной суммы (упрощенная)
        if not self._validate_inn_checksum(inn):
            return {
                'valid': False,
                'error': 'Неверная контрольная сумма ИНН',
                'found': False
            }
        
        # Проверка в базе ФНС
        company_info = await self.get_company_info(inn)
        
        if company_info is None:
            return {
                'valid': False,
                'error': 'Ошибка при проверке ИНН в базе ФНС',
                'found': False
            }
        
        if not company_info.get('found', False):
            return {
                'valid': False,
                'error': 'ИНН не найден в базе ФНС',
                'found': False
            }
        
        if not company_info.get('is_active', False):
            return {
                'valid': False,
                'error': 'Компания неактивна или ликвидирована',
                'found': True,
                'company_info': company_info
            }
        
        return {
            'valid': True,
            'found': True,
            'company_info': company_info
        }
    
    def _determine_company_type(self, company_data: Dict[str, Any]) -> str:
        """Определить тип компании (ЮЛ или ИП)"""
        # Проверяем по длине ИНН и другим признакам
        inn = company_data.get('inn', '')
        
        if len(inn) == 10:
            return 'ЮЛ'  # Юридическое лицо
        elif len(inn) == 12:
            return 'ИП'  # Индивидуальный предприниматель
        else:
            return 'Неизвестно'
    
    def _validate_inn_checksum(self, inn: str) -> bool:
        """
        Упрощенная проверка контрольной суммы ИНН
        В реальной реализации нужно использовать полный алгоритм
        """
        try:
            if len(inn) == 10:
                # Для ЮЛ - проверяем 10-ю цифру
                weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]
                checksum = sum(int(inn[i]) * weights[i] for i in range(9)) % 11
                if checksum > 9:
                    checksum = checksum % 10
                return checksum == int(inn[9])
            
            elif len(inn) == 12:
                # Для ИП - проверяем 11-ю и 12-ю цифры
                weights1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
                weights2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
                
                checksum1 = sum(int(inn[i]) * weights1[i] for i in range(10)) % 11
                if checksum1 > 9:
                    checksum1 = checksum1 % 10
                
                checksum2 = sum(int(inn[i]) * weights2[i] for i in range(11)) % 11
                if checksum2 > 9:
                    checksum2 = checksum2 % 10
                
                return (checksum1 == int(inn[10]) and checksum2 == int(inn[11]))
            
            return False
            
        except (ValueError, IndexError):
            return False
    
    async def _get_mock_company_info(self, inn: str) -> Dict[str, Any]:
        """
        Мок-данные для тестирования без реального API
        """
        logger.info(f"Using mock data for INN: {inn}")
        
        # Простая имитация - если ИНН содержит "123", то компания найдена
        if "123" in inn:
            return {
                'inn': inn,
                'name': f'Тестовая компания {inn}',
                'ogrn': '1234567890123',
                'kpp': '123456789',
                'address': 'г. Москва, ул. Тестовая, д. 1',
                'status': 'ACTIVE',
                'type': 'ЮЛ' if len(inn) == 10 else 'ИП',
                'registration_date': '2020-01-01',
                'last_update': '2024-01-01',
                'is_active': True,
                'found': True
            }
        else:
            return {'found': False, 'inn': inn}

# Глобальный инстанс
fns_api = FNSAPI()

# Утилиты для использования в других модулях
async def validate_inn_with_fns(inn: str) -> Dict[str, Any]:
    """
    Утилита для валидации ИНН через ФНС API
    
    Args:
        inn: ИНН для проверки
        
    Returns:
        Dict с результатами валидации
    """
    async with fns_api as api:
        return await api.validate_inn(inn)

async def get_company_by_inn(inn: str) -> Optional[Dict[str, Any]]:
    """
    Утилита для получения информации о компании по ИНН
    
    Args:
        inn: ИНН компании
        
    Returns:
        Dict с информацией о компании или None
    """
    async with fns_api as api:
        return await api.get_company_info(inn)
