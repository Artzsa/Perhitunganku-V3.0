# main.py
import time
import logging
import config
from config import bot, TOKEN, CREDS_FILE, my_logger
from notification_system import NotificationSystem, NotificationAPI

# Import semua handler
import handlers.command_handlers
import handlers.message_handlers
import handlers.callback_handlers

# Konfigurasi logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === INISIALISASI NOTIFICATION SYSTEM ===
try:
    print("🚀 Starting notification system...")
    notif_system = NotificationSystem(TOKEN, CREDS_FILE)
    notif_system.start()  # <- WAJIB, biar sheet_users dll. kebentuk
    notif_api = NotificationAPI(notif_system)

    # Simpan ke config biar bisa dipanggil di handler
    config.notif_system = notif_system
    config.notif_api = notif_api
    config.NOTIF_ENABLED = True

    print("✅ Notification system started!")
except Exception as e:
    print(f"⚠️ Notification system tidak dapat dimuat: {e}")
    print("Bot akan berjalan tanpa sistem notifikasi.")
    config.NOTIF_ENABLED = False
    config.notif_api = None


# === RUN BOT ===
def run_bot():
    while True:
        try:
            print("🚀 Bot Perhitunganku Enhanced v3.0 berjalan...")
            print("✨ Fitur terbaru:")
            print("   📊 Progress bar visual untuk anggaran")
            print("   💡 Smart tips berdasarkan pola pengeluaran")  
            print("   📈 Chart ASCII untuk visualisasi data")
            print("   🎯 Enhanced UI/UX dengan feedback real-time")

            my_logger.info("Bot Enhanced dimulai...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)

        except KeyboardInterrupt:
            print("\n🛑 Bot dihentikan oleh user")
            my_logger.info("Bot dihentikan manual")
            if config.notif_system:
                config.notif_system.stop()
            break

        except Exception as e:
            print(f"❌ Polling error: {e}")
            my_logger.error(f"Polling error: {e}")
            print("🔄 Mencoba reconnect dalam 5 detik...")
            time.sleep(5)


if __name__ == "__main__":
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n👋 Bot Enhanced dihentikan. Terima kasih!")
    except Exception as e:
        print(f"❌ Error fatal: {e}")
        my_logger.error(f"Error fatal: {e}")
