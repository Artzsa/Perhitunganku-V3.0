# keyboards/inline_keyboards.py
from telebot import types

def create_main_menu():
    """Membuat menu utama dengan inline keyboard"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📝 Catat Transaksi", callback_data="menu_transaksi"),
        types.InlineKeyboardButton("💰 Kelola Anggaran", callback_data="menu_anggaran")
    )
    markup.add(
        types.InlineKeyboardButton("📊 Lihat Laporan", callback_data="menu_laporan"),
        types.InlineKeyboardButton("📤 Export Data", callback_data="menu_export")
    )
    markup.add(
        types.InlineKeyboardButton("❓ Bantuan", callback_data="help"),
        types.InlineKeyboardButton("🔄 Refresh Menu", callback_data="main_menu")
    )
    return markup

def create_transaction_menu():
    """Menu untuk catat transaksi"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("💸 Catat Pengeluaran", callback_data="guide_expense"),
        types.InlineKeyboardButton("💰 Catat Pemasukan", callback_data="guide_income"),
        types.InlineKeyboardButton("📋 Format Input", callback_data="format_help")
    )
    markup.add(types.InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="main_menu"))
    return markup

def create_budget_menu():
    """Menu untuk kelola anggaran"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎯 Set Anggaran Baru", callback_data="guide_set_budget"),
        types.InlineKeyboardButton("💰 Cek Anggaran", callback_data="guide_check_budget"),
        types.InlineKeyboardButton("📋 List Semua Anggaran", callback_data="list_budget")
    )
    markup.add(types.InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="main_menu"))
    return markup

def create_report_menu():
    """Menu untuk laporan"""
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📅 Hari Ini", callback_data="report_daily"),
        types.InlineKeyboardButton("📅 Minggu Ini", callback_data="report_weekly")
    )
    markup.add(
        types.InlineKeyboardButton("📅 Bulan Ini", callback_data="report_monthly"),
        types.InlineKeyboardButton("📊 Custom Periode", callback_data="guide_custom_report")
    )
    markup.add(types.InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="main_menu"))
    return markup

def create_export_menu():
    """Menu untuk export"""
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("📤 Export Bulan Ini", callback_data="export_month"),
        types.InlineKeyboardButton("📤 Export Tahun Ini", callback_data="export_year"),
        types.InlineKeyboardButton("📤 Export Custom", callback_data="guide_export_custom")
    )
    markup.add(types.InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="main_menu"))
    return markup
