# config.py
import logging
from telebot import TeleBot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === TOKEN & CREDS ===
TOKEN = '8048576532:AAEAYO9-1RHEKF-k-NlXoOgAkCJGmocX6lo'
CREDS_FILE = "credentials.json"   # path file kredensial Google Sheets

# === BOT ===
bot = TeleBot(TOKEN, parse_mode="HTML")

# === LOGGER ===
logging.basicConfig(level=logging.INFO)
my_logger = logging.getLogger("perhitunganku")

# === GOOGLE SHEETS ===
try:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, scope)
    client = gspread.authorize(creds)

    # ganti sesuai nama sheet yang kamu pakai
    sheet_transaksi = client.open("Perhitunganku").worksheet("Sheet1")
    sheet_budget    = client.open("Perhitunganku").worksheet("Sheet2")
    sheet_kategori  = client.open("Perhitunganku").worksheet("Sheet3")

except Exception as e:
    print(f"⚠️ Gagal load Google Sheets: {e}")
    sheet_budget = None
    sheet_transaksi = None

# === NOTIFICATION PLACEHOLDER ===
notif_system = None
notif_api = None
NOTIF_ENABLED = False