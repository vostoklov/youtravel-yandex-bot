#!/usr/bin/env python3
"""
Скрипт для подготовки GOOGLE_CREDENTIALS_JSON для Railway
Конвертирует JSON файл в одну строку для переменной окружения
"""
import json
import sys

def prepare_credentials(file_path='credentials.json'):
    """Читает credentials.json и выводит в формате для Railway"""
    try:
        with open(file_path, 'r') as f:
            credentials = json.load(f)
        
        # Конвертируем в компактную строку без пробелов
        compact_json = json.dumps(credentials, separators=(',', ':'))
        
        print("=" * 80)
        print("GOOGLE_CREDENTIALS_JSON для Railway:")
        print("=" * 80)
        print(compact_json)
        print("=" * 80)
        print()
        print("Скопируйте строку выше и вставьте в переменную окружения GOOGLE_CREDENTIALS_JSON на Railway")
        print()
        print("Детали service account:")
        print(f"  Email: {credentials.get('client_email')}")
        print(f"  Project ID: {credentials.get('project_id')}")
        print()
        print("⚠️  ВАЖНО: Убедитесь, что этот email добавлен в Google Sheets с правами Editor!")
        print(f"  Таблица emails: https://docs.google.com/spreadsheets/d/{{SHEET_ID}}/edit")
        print()
        
        return compact_json
        
    except FileNotFoundError:
        print(f"❌ Файл {file_path} не найден!", file=sys.stderr)
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}", file=sys.stderr)
        return None

if __name__ == "__main__":
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'credentials.json'
    result = prepare_credentials(file_path)
    
    if result:
        # Копируем в буфер обмена, если доступен pbcopy (macOS)
        try:
            import subprocess
            subprocess.run(['pbcopy'], input=result.encode(), check=True)
            print("✅ JSON скопирован в буфер обмена!")
        except:
            pass

