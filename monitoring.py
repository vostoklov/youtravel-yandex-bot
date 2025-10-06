"""
Система мониторинга и алертов
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
import config
from database import db
from sheets import sheets

logger = logging.getLogger(__name__)

class MonitoringSystem:
    def __init__(self):
        self.last_check = None
        self.alert_thresholds = {
            'low_promos': 5,  # Минимум промокодов
            'high_error_rate': 10,  # Максимум ошибок в час
            'low_conversion': 20,  # Минимум конверсии в %
        }
    
    async def check_system_health(self) -> Dict[str, Any]:
        """Проверка здоровья системы"""
        health_status = {
            'timestamp': datetime.now(),
            'database': False,
            'google_sheets': False,
            'promo_codes': 0,
            'errors': []
        }
        
        try:
            # Проверка базы данных
            await db.get_stats()
            health_status['database'] = True
        except Exception as e:
            health_status['errors'].append(f"Database error: {e}")
            logger.error(f"Database health check failed: {e}")
        
        try:
            # Проверка Google Sheets
            promo_codes = sheets.get_available_promo_codes()
            health_status['google_sheets'] = True
            health_status['promo_codes'] = len(promo_codes)
        except Exception as e:
            health_status['errors'].append(f"Google Sheets error: {e}")
            logger.error(f"Google Sheets health check failed: {e}")
        
        return health_status
    
    async def check_metrics(self) -> Dict[str, Any]:
        """Проверка ключевых метрик"""
        try:
            stats = await db.get_detailed_stats()
            
            # Проверяем промокоды
            available_promos = sheets.get_available_promo_codes()
            stats['available_promos'] = len(available_promos)
            
            # Проверяем пороги
            alerts = []
            
            if stats['available_promos'] < self.alert_thresholds['low_promos']:
                alerts.append(f"⚠️ Мало промокодов: {stats['available_promos']}")
            
            if stats['conversion_rate'] < self.alert_thresholds['low_conversion']:
                alerts.append(f"⚠️ Низкая конверсия: {stats['conversion_rate']:.1f}%")
            
            return {
                'stats': stats,
                'alerts': alerts,
                'timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Metrics check failed: {e}")
            return {
                'stats': {},
                'alerts': [f"❌ Ошибка проверки метрик: {e}"],
                'timestamp': datetime.now()
            }
    
    async def send_daily_report(self, bot) -> bool:
        """Отправка ежедневного отчета админам"""
        try:
            metrics = await self.check_metrics()
            health = await self.check_system_health()
            
            # Формируем отчет
            report = self._format_daily_report(metrics, health)
            
            # Отправляем всем админам
            for admin_id in config.ADMIN_USER_IDS:
                try:
                    await bot.send_message(admin_id, report, parse_mode="HTML")
                    logger.info(f"Daily report sent to admin {admin_id}")
                except Exception as e:
                    logger.error(f"Failed to send report to admin {admin_id}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send daily report: {e}")
            return False
    
    def _format_daily_report(self, metrics: Dict[str, Any], health: Dict[str, Any]) -> str:
        """Форматирование ежедневного отчета"""
        stats = metrics.get('stats', {})
        alerts = metrics.get('alerts', [])
        
        report = f"📊 <b>Ежедневный отчет - {datetime.now().strftime('%d.%m.%Y')}</b>\n\n"
        
        # Статистика
        report += f"👥 <b>Пользователи:</b>\n"
        report += f"• Всего: {stats.get('total_users', 0)}\n"
        report += f"• Завершили: {stats.get('completed_users', 0)}\n"
        report += f"• Конверсия: {stats.get('conversion_rate', 0):.1f}%\n"
        report += f"• За 24ч: {stats.get('users_last_24h', 0)} новых\n\n"
        
        # Промокоды
        report += f"🎟️ <b>Промокоды:</b>\n"
        report += f"• Выдано: {stats.get('promo_codes_issued', 0)}\n"
        report += f"• Доступно: {stats.get('available_promos', 0)}\n\n"
        
        # Состояние системы
        report += f"🔧 <b>Состояние системы:</b>\n"
        report += f"• База данных: {'✅' if health['database'] else '❌'}\n"
        report += f"• Google Sheets: {'✅' if health['google_sheets'] else '❌'}\n\n"
        
        # Алерты
        if alerts:
            report += f"⚠️ <b>Внимание:</b>\n"
            for alert in alerts:
                report += f"• {alert}\n"
        else:
            report += f"✅ <b>Все системы работают нормально</b>\n"
        
        return report
    
    async def start_monitoring(self, bot):
        """Запуск мониторинга"""
        logger.info("🔍 Starting monitoring system...")
        
        while True:
            try:
                # Проверяем каждые 30 минут
                await asyncio.sleep(1800)  # 30 минут
                
                # Проверяем метрики
                metrics = await self.check_metrics()
                
                # Если есть критические алерты, отправляем немедленно
                critical_alerts = [alert for alert in metrics['alerts'] if '❌' in alert]
                if critical_alerts:
                    for admin_id in config.ADMIN_USER_IDS:
                        try:
                            await bot.send_message(
                                admin_id, 
                                f"🚨 <b>Критический алерт!</b>\n\n" + "\n".join(critical_alerts),
                                parse_mode="HTML"
                            )
                        except Exception as e:
                            logger.error(f"Failed to send critical alert to admin {admin_id}: {e}")
                
                # Отправляем ежедневный отчет в 9:00
                now = datetime.now()
                if now.hour == 9 and now.minute < 30:
                    await self.send_daily_report(bot)
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(300)  # 5 минут при ошибке

# Глобальный экземпляр
monitoring = MonitoringSystem()
