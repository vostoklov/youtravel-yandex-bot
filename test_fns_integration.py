#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции с ФНС API
"""
import asyncio
import logging
import sys
from fns_api import FNSAPI, validate_inn_with_fns, get_company_by_inn

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_fns_api():
    """Тестирование ФНС API"""
    print("🔍 Тестирование интеграции с ФНС API")
    print("=" * 50)
    
    # Тестовые ИНН
    test_inns = [
        "1234567890",  # Тестовый ИНН (должен работать с мок-данными)
        "7707083893",  # Реальный ИНН Яндекса
        "123456789012",  # Тестовый ИНН ИП
        "invalid_inn",  # Неверный ИНН
        "123",  # Слишком короткий ИНН
    ]
    
    async with FNSAPI() as fns_api:
        for inn in test_inns:
            print(f"\n📋 Тестирование ИНН: {inn}")
            print("-" * 30)
            
            try:
                # Тест валидации
                validation_result = await fns_api.validate_inn(inn)
                print(f"✅ Валидация: {validation_result}")
                
                # Тест получения информации о компании
                if validation_result.get('valid', False):
                    company_info = await fns_api.get_company_info(inn)
                    print(f"🏢 Информация о компании: {company_info}")
                else:
                    print(f"❌ ИНН не прошел валидацию: {validation_result.get('error', 'Неизвестная ошибка')}")
                    
            except Exception as e:
                print(f"❌ Ошибка при тестировании ИНН {inn}: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено")

async def test_utils_integration():
    """Тестирование интеграции с utils"""
    print("\n🔧 Тестирование интеграции с utils")
    print("=" * 50)
    
    from utils import validate_inn_with_fns
    
    test_inns = [
        "1234567890",  # Тестовый ИНН
        "7707083893",  # Реальный ИНН
        "invalid",     # Неверный ИНН
    ]
    
    for inn in test_inns:
        print(f"\n📋 Тестирование utils для ИНН: {inn}")
        print("-" * 30)
        
        try:
            result = await validate_inn_with_fns(inn)
            print(f"✅ Результат: {result}")
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование utils завершено")

async def test_mock_data():
    """Тестирование с мок-данными"""
    print("\n🎭 Тестирование с мок-данными")
    print("=" * 50)
    
    # Тестируем мок-данные
    test_inns = [
        "1234567890",  # Должен найтись
        "123456789012",  # Должен найтись
        "9876543210",  # Не должен найтись
    ]
    
    async with FNSAPI() as fns_api:
        for inn in test_inns:
            print(f"\n📋 Тестирование мок-данных для ИНН: {inn}")
            print("-" * 30)
            
            try:
                company_info = await fns_api._get_mock_company_info(inn)
                print(f"🏢 Мок-данные: {company_info}")
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Тестирование мок-данных завершено")

async def main():
    """Главная функция тестирования"""
    print("🚀 Запуск тестирования интеграции с ФНС API")
    print("=" * 60)
    
    try:
        # Тест 1: Базовое API
        await test_fns_api()
        
        # Тест 2: Интеграция с utils
        await test_utils_integration()
        
        # Тест 3: Мок-данные
        await test_mock_data()
        
        print("\n🎉 Все тесты завершены успешно!")
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
