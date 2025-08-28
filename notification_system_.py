# notification_system.py
import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import threading
import schedule
import time
from datetime import datetime, timedelta
import logging

# Konfigurasi logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NotificationSystem:
    def __init__(self, token, creds_file):
        logger.info("🔧 Initializing Notification System...")
        self.token = token  
        self.bot = telebot.TeleBot(token)
        self.creds_file = creds_file
        self.running = False
        self.scheduler_thread = None
        self.notification_history = {}  
        self.sheet_users = None   # <-- default biar gak error

        try:
            scope = [
                "https://spreadsheets.google.com/feeds",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = ServiceAccountCredentials.from_json_keyfile_name(creds_file, scope)
            self.client = gspread.authorize(creds)
            logger.info("✅ Google Sheets initialized for notifications")

            # Inisialisasi worksheet USERS
            try:
                self.sheet_users = self.client.open("Perhitunganku").worksheet("Users")
                logger.info("✅ Worksheet 'Users' ditemukan")
            except gspread.WorksheetNotFound:
                sh = self.client.open("Perhitunganku")
                self.sheet_users = sh.add_worksheet(title="Users", rows=100, cols=10)
                self.sheet_users.append_row([
                    "user_id", "username", "notifications_enabled",
                    "morning_reminder", "evening_summary",
                    "lunch_reminder", "budget_alerts", "weekly_report",
                    "last_active", "timezone"
                ])
                logger.info("🆕 Worksheet 'Users' dibuat otomatis")

        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Sheets: {e}")
            self.client = None
            self.sheet_users = None   # <-- biar jelas walau error
    def start(self):
        """Mulai notification system"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(
                target=self.run_scheduler, daemon=True
            )
            self.scheduler_thread.start()
            logger.info("✅ Notification system started")

    def stop(self):
        """Hentikan notification system"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2)
            logger.info("🛑 Notification system stopped")

    def run_scheduler(self):
        """Loop scheduler untuk cek notifikasi"""
        logger.info("⏰ Scheduler started...")
        while self.running:
            try:
                users = self.get_active_users()
                logger.debug(f"Scheduler tick, {len(users)} active users")
                # nanti bisa kamu tambahkan:
                # self.send_morning_reminders()
                # self.send_evening_summary()
                # self.check_budget_alerts()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
            time.sleep(60)  # cek tiap 1 menit
        
        # Schedule tasks
        schedule.every().day.at("08:00").do(self.send_morning_reminders)
        schedule.every().day.at("20:00").do(self.send_evening_summary)
        schedule.every(30).minutes.do(self.check_budget_alerts)
        
        # Start scheduler in a separate thread
        self.scheduler_thread = threading.Thread(target=self.run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        print("✅ Notification system started successfully!")

    # Metode lainnya...
       
    def start(self):
        """Start notification system"""
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        logger.info("Notification system started")
        print("Notification system started with token:", self.token)

        
    def stop(self):
        """Stop notification system"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
        logger.info("Notification system stopped")
        print("Notification system stopped.")

    
    def _run_scheduler(self):
        """Run scheduled tasks"""
        # Schedule daily reminders
        schedule.every().day.at("08:00").do(self.send_morning_reminders)
        schedule.every().day.at("20:00").do(self.send_evening_summary)
        schedule.every().day.at("12:00").do(self.send_lunch_reminder)
        
        # Schedule weekly reports
        schedule.every().monday.at("09:00").do(self.send_weekly_report)
        
        # Schedule monthly reports
        schedule.every().day.at("09:00").do(self.check_monthly_report)
        
        # Budget alerts every 3 hours
        schedule.every(3).hours.do(self.check_budget_alerts)
        
        while self.running:
            schedule.run_pending()
            time.sleep(30)  # Check every 30 seconds
    
    # === USER MANAGEMENT ===
    def get_active_users(self):
        """Get list of active users with notification preferences"""
        try:
            users = []
            records = self.sheet_users.get_all_records()
            
            for record in records:
                if record.get('notifications_enabled', 'true').lower() == 'true':
                    users.append({
                        'user_id': record['user_id'],
                        'username': record.get('username', ''),
                        'morning_reminder': record.get('morning_reminder', 'true').lower() == 'true',
                        'evening_summary': record.get('evening_summary', 'true').lower() == 'true',
                        'lunch_reminder': record.get('lunch_reminder', 'false').lower() == 'true',
                        'budget_alerts': record.get('budget_alerts', 'true').lower() == 'true',
                        'weekly_report': record.get('weekly_report', 'true').lower() == 'true',
                        'last_active': record.get('last_active', ''),
                        'timezone': record.get('timezone', 'Asia/Jakarta')
                    })
            
            return users
        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []
    
    def register_user(self, user_id, username=""):
        """Register new user for notifications"""
        try:
            # Check if user already exists
            users = self.sheet_users.get_all_records()
            for user in users:
                if str(user.get('user_id')) == str(user_id):
                    return  # User already registered
            
            # Add new user with default preferences
            self.sheet_users.append_row([
                user_id,
                username,
                'true',  # notifications_enabled
                'true',  # morning_reminder
                'true',  # evening_summary
                'false', # lunch_reminder
                'true',  # budget_alerts
                'true',  # weekly_report
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # last_active
                'Asia/Jakarta'  # timezone
            ])
            
            logger.info(f"New user registered: {user_id}")
        except Exception as e:
            logger.error(f"Error registering user: {e}")
    
    # === NOTIFICATION TYPES ===
    
    def send_morning_reminders(self):
        """Send morning reminder to track expenses"""
        users = self.get_active_users()
        
        for user in users:
            if not user['morning_reminder']:
                continue
                
            try:
                # Get yesterday's tracking status
                yesterday = (datetime.now() - timedelta(days=1)).date()
                has_yesterday_record = self._check_user_activity(user['user_id'], yesterday)
                
                if has_yesterday_record:
                    message = (
                        "☀️ <b>Selamat Pagi!</b>\n\n"
                        "✅ Bagus! Kemarin Anda sudah mencatat transaksi.\n"
                        "Mari lanjutkan kebiasaan baik ini hari ini! 💪\n\n"
                        "💡 <i>Tips: Catat pengeluaran segera setelah transaksi agar tidak lupa.</i>"
                    )
                else:
                    message = (
                        "☀️ <b>Selamat Pagi!</b>\n\n"
                        "⚠️ Sepertinya kemarin Anda lupa mencatat transaksi.\n"
                        "Tidak apa-apa, mari mulai hari ini dengan lebih baik! 🌟\n\n"
                        "📝 Gunakan format: <code>[keterangan] -[jumlah] /[kategori]</code>"
                    )
                
                self.bot.send_message(
                    user['user_id'],
                    message,
                    parse_mode='HTML'
                )
                
                # Log notification
                self._log_notification(user['user_id'], 'morning_reminder', 'sent')
                
            except Exception as e:
                logger.error(f"Error sending morning reminder to {user['user_id']}: {e}")
    
    def send_evening_summary(self):
        """Send evening summary with daily spending"""
        users = self.get_active_users()
        today = datetime.now().date()
        
        for user in users:
            if not user['evening_summary']:
                continue
                
            try:
                # Get today's summary
                summary = self._get_daily_summary(user['user_id'], today)
                
                if summary['transaction_count'] > 0:
                    message = (
                        f"🌙 <b>Ringkasan Hari Ini</b>\n"
                        f"📅 {today.strftime('%d %B %Y')}\n\n"
                        f"📊 <b>Statistik:</b>\n"
                        f"• Transaksi: {summary['transaction_count']} kali\n"
                        f"• Pemasukan: Rp{summary['income']:,}\n"
                        f"• Pengeluaran: Rp{summary['expense']:,}\n"
                        f"• Net: Rp{summary['net']:,}\n\n"
                    )
                    
                    # Add category breakdown if exists
                    if summary['categories']:
                        message += "📂 <b>Per Kategori:</b>\n"
                        for cat, amount in summary['categories'].items():
                            message += f"• {cat.title()}: Rp{amount:,}\n"
                    
                    # Add motivational message
                    if summary['net'] >= 0:
                        message += "\n✨ <i>Great job managing your finances today!</i>"
                    else:
                        message += "\n💡 <i>Tomorrow is a new opportunity to save more!</i>"
                else:
                    message = (
                        "🌙 <b>Ringkasan Hari Ini</b>\n\n"
                        "📝 Belum ada transaksi tercatat hari ini.\n"
                        "Jangan lupa catat pengeluaran Anda!\n\n"
                        "💤 <i>Selamat beristirahat!</i>"
                    )
                
                self.bot.send_message(
                    user['user_id'],
                    message,
                    parse_mode='HTML'
                )
                
                self._log_notification(user['user_id'], 'evening_summary', 'sent')
                
            except Exception as e:
                logger.error(f"Error sending evening summary to {user['user_id']}: {e}")
    
    def send_lunch_reminder(self):
        """Optional lunch time reminder"""
        users = self.get_active_users()
        
        for user in users:
            if not user['lunch_reminder']:
                continue
                
            try:
                message = (
                    "🍽️ <b>Lunch Time Reminder!</b>\n\n"
                    "Jangan lupa catat pengeluaran makan siang Anda! 📝\n"
                    "Tracking yang konsisten = kontrol keuangan yang lebih baik 💪\n\n"
                    "<i>Format: Makan siang -[jumlah] /makanan</i>"
                )
                
                self.bot.send_message(
                    user['user_id'],
                    message,
                    parse_mode='HTML'
                )
                
            except Exception as e:
                logger.error(f"Error sending lunch reminder to {user['user_id']}: {e}")
    
    def check_budget_alerts(self):
        """Check and send budget alerts"""
        users = self.get_active_users()
        today = datetime.now().date()
        start_date = today.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        for user in users:
            if not user['budget_alerts']:
                continue
                
            try:
                alerts = self._check_budget_status(user['user_id'], start_date, end_date)
                
                if alerts:
                    message = "🚨 <b>BUDGET ALERT!</b> 🚨\n\n"
                    
                    for alert in alerts:
                        emoji = self._get_alert_emoji(alert['percentage'])
                        message += (
                            f"{emoji} <b>{alert['category'].title()}</b>\n"
                            f"• Used: {alert['percentage']:.0f}%"
                            f" (Rp{alert['spent']:,} / Rp{alert['budget']:,})\n"
                            f"• Remaining: Rp{alert['remaining']:,}\n\n"
                        )
                    
                    message += "💡 <i>Tip: Review your spending and adjust if needed!</i>"
                    
                    # Check if we already sent this alert today
                    alert_key = f"budget_alert_{today}"
                    if not self._was_notified_today(user['user_id'], alert_key):
                        self.bot.send_message(
                            user['user_id'],
                            message,
                            parse_mode='HTML'
                        )
                        self._log_notification(user['user_id'], alert_key, 'sent')
                
            except Exception as e:
                logger.error(f"Error checking budget alerts for {user['user_id']}: {e}")
    
    def send_weekly_report(self):
        """Send weekly financial report"""
        users = self.get_active_users()
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        for user in users:
            if not user['weekly_report']:
                continue
                
            try:
                # Get weekly data
                report = self._generate_weekly_report(user['user_id'], week_start, week_end)
                
                message = (
                    "📊 <b>WEEKLY FINANCIAL REPORT</b> 📊\n"
                    f"📅 {week_start.strftime('%d/%m')} - {week_end.strftime('%d/%m/%Y')}\n\n"
                    f"💰 <b>Summary:</b>\n"
                    f"• Income: Rp{report['income']:,}\n"
                    f"• Expenses: Rp{report['expenses']:,}\n"
                    f"• Net: Rp{report['net']:,}\n"
                    f"• Transactions: {report['transaction_count']}\n\n"
                )
                
                # Add comparison with last week
                if report['last_week_comparison']:
                    comp = report['last_week_comparison']
                    message += "📈 <b>vs Last Week:</b>\n"
                                        
                    if comp['expense_change'] > 0:
                        message += f"• Expenses ↗️ +{comp['expense_change']:.0f}%\n"
                    else:
                        message += f"• Expenses ↘️ {comp['expense_change']:.0f}%\n"
                    
                    if comp['saving_rate'] > 0:
                        message += f"• Saving rate: {comp['saving_rate']:.0f}% 👍\n"
                
                # Add top categories
                if report['top_categories']:
                    message += "\n📂 <b>Top Spending Categories:</b>\n"
                    for i, (cat, amount) in enumerate(report['top_categories'][:3], 1):
                        message += f"{i}. {cat.title()}: Rp{amount:,}\n"
                
                # Add insights
                message += f"\n💡 <b>Insight:</b> {report['insight']}"
                
                # Add action buttons
                markup = telebot.types.InlineKeyboardMarkup()
                markup.add(
                    telebot.types.InlineKeyboardButton("📊 Detail Report", callback_data="weekly_detail"),
                    telebot.types.InlineKeyboardButton("📈 View Trends", callback_data="view_trends")
                )
                
                self.bot.send_message(
                    user['user_id'],
                    message,
                    parse_mode='HTML',
                    reply_markup=markup
                )
                
                self._log_notification(user['user_id'], 'weekly_report', 'sent')
                
            except Exception as e:
                logger.error(f"Error sending weekly report to {user['user_id']}: {e}")
    
    def check_monthly_report(self):
        """Check if it's time to send monthly report (1st of month)"""
        if datetime.now().day == 1:
            self.send_monthly_report()
    
    def send_monthly_report(self):
        """Send comprehensive monthly report"""
        users = self.get_active_users()
        
        # Get last month's date range
        today = datetime.now().date()
        last_month_end = today.replace(day=1) - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        
        for user in users:
            try:
                report = self._generate_monthly_report(
                    user['user_id'], 
                    last_month_start, 
                    last_month_end
                )
                
                message = (
                    "📊 <b>MONTHLY FINANCIAL REPORT</b> 📊\n"
                    f"📅 {last_month_start.strftime('%B %Y')}\n"
                    "━━━━━━━━━━━━━━━━━\n\n"
                    f"💰 <b>Financial Overview:</b>\n"
                    f"• Total Income: Rp{report['income']:,}\n"
                    f"• Total Expenses: Rp{report['expenses']:,}\n"
                    f"• Net Savings: Rp{report['net']:,}\n"
                    f"• Saving Rate: {report['saving_rate']:.1f}%\n\n"
                )
                
                # Budget performance
                if report['budget_performance']:
                    message += "🎯 <b>Budget Performance:</b>\n"
                    for cat, perf in report['budget_performance'].items():
                        if perf['percentage'] > 100:
                            emoji = "🔴"
                            status = "OVER"
                        elif perf['percentage'] > 80:
                            emoji = "🟡"
                            status = "Warning"
                        else:
                            emoji = "🟢"
                            status = "Good"
                        
                        message += (
                            f"{emoji} {cat.title()}: {perf['percentage']:.0f}% "
                            f"({status})\n"
                        )
                
                # Monthly trends
                message += f"\n📈 <b>Trends:</b>\n"
                message += f"• Highest spending day: {report['highest_day']}\n"
                message += f"• Most expensive category: {report['top_category']}\n"
                message += f"• Total transactions: {report['transaction_count']}\n"
                
                # Recommendations
                message += f"\n💡 <b>Recommendations:</b>\n"
                for rec in report['recommendations']:
                    message += f"• {rec}\n"
                
                # Achievement if any
                if report['achievements']:
                    message += f"\n🏆 <b>Achievements:</b>\n"
                    for ach in report['achievements']:
                        message += f"• {ach}\n"
                
                self.bot.send_message(
                    user['user_id'],
                    message,
                    parse_mode='HTML'
                )
                
                self._log_notification(user['user_id'], 'monthly_report', 'sent')
                
            except Exception as e:
                logger.error(f"Error sending monthly report to {user['user_id']}: {e}")
    
    # === CUSTOM NOTIFICATIONS ===
    
    def send_custom_notification(self, user_id, message, notification_type="custom"):
        """Send custom notification to specific user"""
        try:
            self.bot.send_message(user_id, message, parse_mode='HTML')
            self._log_notification(user_id, notification_type, 'sent')
            return True
        except Exception as e:
            logger.error(f"Error sending custom notification: {e}")
            return False
    
    def send_achievement_notification(self, user_id, achievement_name, achievement_desc, points=0):
        """Send achievement unlocked notification"""
        message = (
            "🏆 <b>ACHIEVEMENT UNLOCKED!</b> 🏆\n\n"
            f"🎯 <b>{achievement_name}</b>\n"
            f"📝 {achievement_desc}\n"
        )
        
        if points > 0:
            message += f"✨ +{points} XP\n"
        
        message += "\n🎉 Congratulations! Keep up the great work!"
        
        return self.send_custom_notification(user_id, message, "achievement")
    
    def send_streak_notification(self, user_id, streak_days):
        """Send streak milestone notification"""
        milestones = [7, 30, 60, 90, 100, 365]
        
        if streak_days in milestones:
            emoji_map = {
                7: "🔥",
                30: "💪", 
                60: "🌟",
                90: "⭐",
                100: "💯",
                365: "👑"
            }
            
            message = (
                f"{emoji_map.get(streak_days, '🔥')} <b>STREAK MILESTONE!</b>\n\n"
                f"Amazing! You've tracked your finances for {streak_days} days straight!\n\n"
                f"Keep the momentum going! 🚀"
            )
            
            return self.send_custom_notification(user_id, message, "streak_milestone")
    
    def send_savings_goal_notification(self, user_id, goal_name, current, target):
        """Send savings goal progress notification"""
        percentage = (current / target * 100) if target > 0 else 0
        
        if percentage >= 100:
            message = (
                "🎯 <b>GOAL ACHIEVED!</b> 🎯\n\n"
                f"Congratulations! You've reached your '{goal_name}' savings goal!\n"
                f"Target: Rp{target:,}\n"
                f"Achieved: Rp{current:,}\n\n"
                "Time to set a new goal? 🚀"
            )
        elif percentage >= 75:
            message = (
                "📈 <b>SAVINGS GOAL UPDATE</b>\n\n"
                f"You're {percentage:.0f}% towards your '{goal_name}' goal!\n"
                f"Current: Rp{current:,}\n"
                f"Target: Rp{target:,}\n"
                f"Remaining: Rp{target-current:,}\n\n"
                "Almost there! Keep saving! 💪"
            )
        else:
            return  # Don't send for lower percentages
        
        return self.send_custom_notification(user_id, message, "savings_goal")
    
    # === HELPER FUNCTIONS ===
    
    def _check_user_activity(self, user_id, date):
        """Check if user has any transaction on specific date"""
        try:
            records = self.sheet_transaksi.get_all_records()
            for record in records:
                if (str(record.get('ID User')) == str(user_id) and 
                    self._parse_date(record.get('Tanggal')) == date):
                    return True
            return False
        except Exception as e:
            logger.error(f"Error checking user activity: {e}")
            return False
    
    def _get_daily_summary(self, user_id, date):
        """Get daily transaction summary"""
        summary = {
            'transaction_count': 0,
            'income': 0,
            'expense': 0,
            'net': 0,
            'categories': {}
        }
        
        try:
            records = self.sheet_transaksi.get_all_records()
            
            for record in records:
                if (str(record.get('ID User')) == str(user_id) and 
                    self._parse_date(record.get('Tanggal')) == date):
                    
                    summary['transaction_count'] += 1
                    amount = self._clean_amount(record.get('Nominal', 0))
                    category = record.get('Kategori', 'lainnya').lower()
                    trans_type = record.get('Tipe', '').lower()
                    
                    if trans_type == 'pemasukan':
                        summary['income'] += amount
                    elif trans_type == 'pengeluaran':
                        summary['expense'] += amount
                        summary['categories'][category] = summary['categories'].get(category, 0) + amount
            
            summary['net'] = summary['income'] - summary['expense']
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
        
        return summary
    
    def _check_budget_status(self, user_id, start_date, end_date):
        """Check budget status and return alerts"""
        alerts = []
        
        try:
            # Get budgets
            budget_records = self.sheet_budget.get_all_records()
            budgets = {}
            
            for record in budget_records:
                if (str(record.get('ID User')) == str(user_id) and
                    start_date <= self._parse_date(record.get('Tanggal')) <= end_date):
                    
                    category = record.get('Kategori', '').lower()
                    amount = self._clean_amount(record.get('Budget', 0))
                    budgets[category] = budgets.get(category, 0) + amount
            
            # Get spending
            transaction_records = self.sheet_transaksi.get_all_records()
            spending = {}
            
            for record in transaction_records:
                if (str(record.get('ID User')) == str(user_id) and
                    record.get('Tipe', '').lower() == 'pengeluaran' and
                    start_date <= self._parse_date(record.get('Tanggal')) <= end_date):
                    
                    category = record.get('Kategori', '').lower()
                    amount = self._clean_amount(record.get('Nominal', 0))
                    spending[category] = spending.get(category, 0) + amount
            
            # Check alerts
            for category, budget in budgets.items():
                spent = spending.get(category, 0)
                percentage = (spent / budget * 100) if budget > 0 else 0
                
                # Alert if over 80%
                if percentage >= 80:
                    alerts.append({
                        'category': category,
                        'budget': budget,
                        'spent': spent,
                        'remaining': budget - spent,
                        'percentage': percentage
                    })
            
        except Exception as e:
            logger.error(f"Error checking budget status: {e}")
        
        return alerts
    
    def _generate_weekly_report(self, user_id, start_date, end_date):
        """Generate weekly report data"""
        report = {
            'income': 0,
            'expenses': 0,
            'net': 0,
            'transaction_count': 0,
            'top_categories': [],
            'last_week_comparison': None,
            'insight': ''
        }
        
        try:
            # Get this week's data
            categories = {}
            records = self.sheet_transaksi.get_all_records()
            
            for record in records:
                if (str(record.get('ID User')) == str(user_id) and
                    start_date <= self._parse_date(record.get('Tanggal')) <= end_date):
                    
                    report['transaction_count'] += 1
                    amount = self._clean_amount(record.get('Nominal', 0))
                    trans_type = record.get('Tipe', '').lower()
                    category = record.get('Kategori', 'lainnya').lower()
                    
                    if trans_type == 'pemasukan':
                        report['income'] += amount
                    elif trans_type == 'pengeluaran':
                        report['expenses'] += amount
                        categories[category] = categories.get(category, 0) + amount
            
            report['net'] = report['income'] - report['expenses']
            report['top_categories'] = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            # Compare with last week
            last_week_start = start_date - timedelta(days=7)
            last_week_end = end_date - timedelta(days=7)
            last_week_expenses = 0
            
            for record in records:
                if (str(record.get('ID User')) == str(user_id) and
                    record.get('Tipe', '').lower() == 'pengeluaran' and
                    last_week_start <= self._parse_date(record.get('Tanggal')) <= last_week_end):
                    
                    last_week_expenses += self._clean_amount(record.get('Nominal', 0))
            if last_week_expenses > 0:
                expense_change = ((report['expenses'] - last_week_expenses) / last_week_expenses * 100)
                saving_rate = (report['net'] / report['income'] * 100) if report['income'] > 0 else 0
                
                report['last_week_comparison'] = {
                    'expense_change': expense_change,
                    'saving_rate': saving_rate
                }
            
            # Generate insight
            if report['net'] > 0:
                report['insight'] = f"Great week! You saved Rp{report['net']:,} ({report['net']/report['income']*100:.0f}% of income)"
            else:
                report['insight'] = "Consider reducing expenses to improve your savings rate."
            
        except Exception as e:
            logger.error(f"Error generating weekly report: {e}")
        
        return report
    
    def _generate_monthly_report(self, user_id, start_date, end_date):
        """Generate comprehensive monthly report"""
        report = {
            'income': 0,
            'expenses': 0,
            'net': 0,
            'saving_rate': 0,
            'transaction_count': 0,
            'budget_performance': {},
            'highest_day': '',
            'top_category': '',
            'recommendations': [],
            'achievements': []
        }
        
        try:
            # Get monthly transactions
            daily_expenses = {}
            categories = {}
            records = self.sheet_transaksi.get_all_records()
            
            for record in records:
                date = self._parse_date(record.get('Tanggal'))
                if (str(record.get('ID User')) == str(user_id) and
                    start_date <= date <= end_date):
                    
                    report['transaction_count'] += 1
                    amount = self._clean_amount(record.get('Nominal', 0))
                    trans_type = record.get('Tipe', '').lower()
                    category = record.get('Kategori', 'lainnya').lower()
                    
                    if trans_type == 'pemasukan':
                        report['income'] += amount
                    elif trans_type == 'pengeluaran':
                        report['expenses'] += amount
                        categories[category] = categories.get(category, 0) + amount
                        daily_expenses[date] = daily_expenses.get(date, 0) + amount
            
            report['net'] = report['income'] - report['expenses']
            report['saving_rate'] = (report['net'] / report['income'] * 100) if report['income'] > 0 else 0
            
            # Find highest spending day
            if daily_expenses:
                highest_date = max(daily_expenses.items(), key=lambda x: x[1])
                report['highest_day'] = f"{highest_date[0].strftime('%d %B')} (Rp{highest_date[1]:,})"
            
            # Find top category
            if categories:
                top_cat = max(categories.items(), key=lambda x: x[1])
                report['top_category'] = f"{top_cat[0].title()} (Rp{top_cat[1]:,})"
            
            # Check budget performance
            budget_records = self.sheet_budget.get_all_records()
            budgets = {}
            
            for record in budget_records:
                if (str(record.get('ID User')) == str(user_id) and
                    start_date <= self._parse_date(record.get('Tanggal')) <= end_date):
                    
                    category = record.get('Kategori', '').lower()
                    amount = self._clean_amount(record.get('Budget', 0))
                    budgets[category] = budgets.get(category, 0) + amount
            
            for category, budget in budgets.items():
                spent = categories.get(category, 0)
                percentage = (spent / budget * 100) if budget > 0 else 0
                report['budget_performance'][category] = {
                    'budget': budget,
                    'spent': spent,
                    'percentage': percentage
                }
            
            # Generate recommendations
            if report['saving_rate'] < 10:
                report['recommendations'].append("Try to save at least 10% of your income")
            
            if report['budget_performance']:
                over_budget = [cat for cat, perf in report['budget_performance'].items() 
                              if perf['percentage'] > 100]
                if over_budget:
                    report['recommendations'].append(f"Focus on reducing {', '.join(over_budget)} expenses")
            
            # Check achievements
            if report['saving_rate'] >= 30:
                report['achievements'].append("🏆 Super Saver - Saved 30%+ of income!")
            
            if all(perf['percentage'] <= 100 for perf in report['budget_performance'].values()):
                report['achievements'].append("🎯 Budget Master - Stayed within all budgets!")
            
        except Exception as e:
            logger.error(f"Error generating monthly report: {e}")
        
        return report
    
    def _parse_date(self, date_str):
        """Parse date from various formats"""
        if not date_str:
            return None
        
        from datetime import datetime
        
        for fmt in ("%d-%m-%Y", "%Y-%m-%d", "%d/%m/%Y"):
            try:
                return datetime.strptime(str(date_str).strip(), fmt).date()
            except:
                continue
        return None
    
    def _clean_amount(self, value):
        """Clean and convert amount to integer"""
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return int(value)
        
        # Clean string values
        value = str(value).replace("Rp", "").replace(",", "").replace(".", "").strip()
        try:
            return int(value)
        except:
            return 0
    
    def _get_alert_emoji(self, percentage):
        """Get emoji based on percentage"""
        if percentage >= 100:
            return "🔴"
        elif percentage >= 90:
            return "🟠"
        elif percentage >= 80:
            return "🟡"
        else:
            return "🟢"
    
    def _was_notified_today(self, user_id, notification_type):
        """Check if user was already notified today"""
        today = datetime.now().date()
        
        if user_id in self.notification_history:
            for notif in self.notification_history[user_id]:
                if (notif['type'] == notification_type and 
                    notif['date'] == today):
                    return True
        return False
    
    def _log_notification(self, user_id, notification_type, status):
        """Log notification history"""
        self.notification_history[user_id].append({
            'type': notification_type,
            'date': datetime.now().date(),
            'time': datetime.now().time(),
            'status': status
        })
        
        # Keep only last 100 notifications per user
        if len(self.notification_history[user_id]) > 100:
            self.notification_history[user_id] = self.notification_history[user_id][-100:]

# === API untuk integrasi dengan bot utama ===

class NotificationAPI:
    """API class for easy integration with main bot"""
    
    def __init__(self, notification_system):
        self.notif_system = notification_system
    
    def register_user(self, user_id, username=""):
        """Register new user for notifications"""
        return self.notif_system.register_user(user_id, username)
    
    def send_transaction_confirmation(self, user_id, transaction_type, amount, category):
        """Send transaction confirmation with tips"""
        emoji = "📥" if transaction_type == "pemasukan" else "📤"
        
        message = (
            f"{emoji} <b>Transaksi Tercatat!</b>\n\n"
            f"Jenis: {transaction_type.title()}\n"
            f"Jumlah: Rp{amount:,}\n"
            f"Kategori: {category.title()}\n"
        )
        
        # Add smart tip based on transaction
        if transaction_type == "pengeluaran":
            # Check budget impact
            today = datetime.now().date()
            start = today.replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            alerts = self.notif_system._check_budget_status(user_id, start, end)
            for alert in alerts:
                if alert['category'] == category and alert['percentage'] > 80:
                    message += (
                        f"\n⚠️ <b>Perhatian:</b> "
                        f"Budget {category} sudah {alert['percentage']:.0f}% terpakai!"
                    )
        
        return self.notif_system.send_custom_notification(user_id, message, "transaction_confirm")
    
    def send_achievement(self, user_id, achievement_name, achievement_desc, points=0):
        """Send achievement notification"""
        return self.notif_system.send_achievement_notification(
            user_id, achievement_name, achievement_desc, points
        )
    
    def send_streak_milestone(self, user_id, streak_days):
        """Send streak milestone notification"""
        return self.notif_system.send_streak_notification(user_id, streak_days)
    
    def check_and_send_budget_alert(self, user_id):
        """Manually trigger budget check for specific user"""
        today = datetime.now().date()
        start = today.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        alerts = self.notif_system._check_budget_status(user_id, start, end)
        if alerts:
            message = "🚨 <b>BUDGET ALERT!</b> 🚨\n\n"
            for alert in alerts:
                emoji = self.notif_system._get_alert_emoji(alert['percentage'])
                message += (
                    f"{emoji} <b>{alert['category'].title()}</b>\n"
                    f"• Used: {alert['percentage']:.0f}%"
                    f" (Rp{alert['spent']:,} / Rp{alert['budget']:,})\n"
                    f"• Remaining: Rp{alert['remaining']:,}\n\n"
                )
            message += "💡 <i>Tip: Review your spending and adjust if needed!</i>"
            return self.notif_system.send_custom_notification(user_id, message, "budget_alert_manual")
        return False
    
    def update_user_preferences(self, user_id, preferences):
        """Update user notification preferences"""
        try:
            # Get all users
            users = self.notif_system.sheet_users.get_all_records()
            
            # Find user row
            row_index = None
            for i, user in enumerate(users, start=2):  # Start from row 2 (after header)
                if str(user.get('user_id')) == str(user_id):
                    row_index = i
                    break
            
            if row_index:
                # Update preferences
                for key, value in preferences.items():
                    if key == 'morning_reminder':
                        self.notif_system.sheet_users.update(f'D{row_index}', str(value).lower())
                    elif key == 'evening_summary':
                        self.notif_system.sheet_users.update(f'E{row_index}', str(value).lower())
                    elif key == 'lunch_reminder':
                        self.notif_system.sheet_users.update(f'F{row_index}', str(value).lower())
                    elif key == 'budget_alerts':
                        self.notif_system.sheet_users.update(f'G{row_index}', str(value).lower())
                    elif key == 'weekly_report':
                        self.notif_system.sheet_users.update(f'H{row_index}', str(value).lower())
                    elif key == 'notifications_enabled':
                        self.notif_system.sheet_users.update(f'C{row_index}', str(value).lower())
                
                # Update last_active
                self.notif_system.sheet_users.update(f'I{row_index}', 
                                                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                return True
            else:
                # User not found, register first
                self.notif_system.register_user(user_id)
                return self.update_user_preferences(user_id, preferences)
                
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return False
    
    def get_user_preferences(self, user_id):
        """Get user notification preferences"""
        try:
            users = self.notif_system.sheet_users.get_all_records()
            
            for user in users:
                if str(user.get('user_id')) == str(user_id):
                    return {
                        'notifications_enabled': user.get('notifications_enabled', 'true').lower() == 'true',
                        'morning_reminder': user.get('morning_reminder', 'true').lower() == 'true',
                        'evening_summary': user.get('evening_summary', 'true').lower() == 'true',
                        'lunch_reminder': user.get('lunch_reminder', 'false').lower() == 'true',
                        'budget_alerts': user.get('budget_alerts', 'true').lower() == 'true',
                        'weekly_report': user.get('weekly_report', 'true').lower() == 'true'
                    }
            
            # User not found, return defaults
            return {
                'notifications_enabled': True,
                'morning_reminder': True,
                'evening_summary': True,
                'lunch_reminder': False,
                'budget_alerts': True,
                'weekly_report': True
            }
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return None
    
    def send_custom_message(self, user_id, message):
        """Send custom message to user"""
        return self.notif_system.send_custom_notification(user_id, message, "custom_message")
    
    def broadcast_message(self, message, filter_func=None):
        """Broadcast message to all or filtered users"""
        users = self.notif_system.get_active_users()
        sent_count = 0
        
        for user in users:
            if filter_func and not filter_func(user):
                continue
                
            try:
                self.notif_system.bot.send_message(
                    user['user_id'],
                    message,
                    parse_mode='HTML'
                )
                sent_count += 1
                time.sleep(0.1)  # Avoid hitting rate limits
            except Exception as e:
                logger.error(f"Error broadcasting to {user['user_id']}: {e}")
        
        return sent_count

# === Main function for standalone testing ===
if __name__ == "__main__":
    import os
    
    # For testing - replace with your actual values
    TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN')
    CREDS_FILE = 'credentials.json'
    
    print("🚀 Starting Notification System...")
    
    # Initialize notification system
    notif_system = NotificationSystem(TOKEN, CREDS_FILE)
    notif_system.start()
    
    # Create API instance
    notif_api = NotificationAPI(notif_system)
    
    print("✅ Notification system is running!")
    print("📋 Scheduled notifications:")
    print("   - Morning reminders: 08:00")
    print("   - Lunch reminders: 12:00")
    print("   - Evening summary: 20:00")
    print("   - Weekly reports: Monday 09:00")
    print("   - Monthly reports: 1st of month 09:00")
    print("   - Budget alerts: Every 3 hours")
    print("\nPress Ctrl+C to stop...")
    
    try:
        # Keep running
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Stopping notification system...")
        notif_system.stop()
        print("✅ Notification system stopped.")