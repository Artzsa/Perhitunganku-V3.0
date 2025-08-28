# handlers/command_handlers.py
import config
from config import bot, sheet_budget, sheet_transaksi, NOTIF_ENABLED, notif_api
from keyboards.inline_keyboards import create_main_menu, create_export_menu
from utils.data_processing import clean_int, get_date_range_from_args, get_budget, get_spent, laporan_detail
from utils.visual_enhancements import create_progress_bar, get_budget_health_status, generate_smart_tips, create_spending_chart
from datetime import datetime, timedelta, date
from telebot import types

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    username = message.from_user.username or ""

    if NOTIF_ENABLED and notif_api:
        notif_api.register_user(user_id, username)

    welcome_text = """
🏦 <b>Selamat datang di Bot Perhitunganku Enhanced!</b>
✨ Anda sudah didaftarkan untuk menerima notifikasi 📢

✨ <b>Fitur Terbaru:</b>
📊 Progress bar visual untuk anggaran
💡 Smart tips berdasarkan pola pengeluaran Anda
📈 Chart ASCII untuk visualisasi data

🚀 <b>Bot ini membantu Anda:</b>
✅ Mencatat transaksi harian
✅ Mengatur anggaran bulanan  
✅ Melihat laporan keuangan dengan visualisasi
✅ Export data ke Excel
✅ Mendapat tips cerdas untuk keuangan

<i>Pilih menu di bawah untuk memulai:</i>
    """
    bot.send_message(message.chat.id, welcome_text, 
                    reply_markup=create_main_menu(), 
                    parse_mode="HTML")

@bot.message_handler(commands=['menu'])
def show_main_menu(message):
    menu_text = """
🎛️ <b>Menu Utama Bot Perhitunganku Enhanced</b>

Pilih fitur yang ingin Anda gunakan:
    """
    bot.send_message(message.chat.id, menu_text,
                    reply_markup=create_main_menu(),
                    parse_mode="HTML")

@bot.message_handler(commands=['help'])
def handle_help(m):
    help_text = """
📚 <b>Bot Perhitunganku Enhanced</b>

✨ <b>Fitur Terbaru:</b>
• 📊 Progress bar visual untuk anggaran
• 💡 Smart tips berdasarkan pola pengeluaran
• 📈 Chart ASCII untuk visualisasi data
• 🎯 Status kesehatan anggaran real-time

📝 <b>Catat transaksi:</b>
<code>[keterangan] +/-[jumlah] /[kategori]</code>

<b>Contoh:</b>
<code>Makan -25000 /makanan</code>
<code>Gaji +3000000 /gaji</code>

💰 <b>Anggaran Enhanced:</b>
/set_anggaran [kategori] [jumlah]
/cek_anggaran [kategori] → dengan progress bar!
/list_anggaran → dashboard visual

📊 <b>Laporan Enhanced:</b>
/laporanhari | /laporanminggu | /laporanbulan
/rekapbulanan mm yyyy
/export → download Excel enhanced

💡 <b>Tip:</b> Gunakan /menu untuk navigasi yang lebih mudah!
    """
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
    bot.send_message(m.chat.id, help_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['export'])
def cmd_export(m):
    from .callback_handlers import export_data # Import here to avoid circular dependency
    args = m.text.split(maxsplit=1)
    args = args[1] if len(args)>1 else ""
    start,end=get_date_range_from_args(args)
    if not start or not end:
        error_text = "❌ Format salah.\n\n📝 <b>Gunakan:</b>\n• /export → bulan ini\n• /export tahun\n• /export dd-mm-YYYY dd-mm-YYYY"
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📤 Menu Export", callback_data="menu_export"))
        markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
        bot.send_message(m.chat.id, error_text, parse_mode="HTML", reply_markup=markup)
        return
    
    export_data(m, start, end, "Custom Period")

@bot.message_handler(commands=['set_anggaran'])
def set_anggaran_enhanced(m):
    try:
        _, kategori, jumlah = m.text.split(maxsplit=2)
        jumlah = clean_int(jumlah)
        tgl = datetime.now().strftime("%d-%m-%Y")
        sheet_budget.append_row([tgl, kategori.lower(), jumlah, m.from_user.id])
        
        success_text = f"✅ <b>Anggaran berhasil diset!</b>\n\n"
        success_text += f"📂 <b>Kategori:</b> {kategori.title()}\n"
        success_text += f"💰 <b>Jumlah:</b> Rp{jumlah:,}\n"
        success_text += f"📅 <b>Berlaku:</b> {tgl}\n\n"
        
        today = datetime.now().date()
        start = today.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        spent = get_spent(m.from_user.id, kategori, start, end)
        
        if spent > 0:
            percentage = (spent / jumlah * 100) if jumlah > 0 else 0
            progress_bar, emoji = create_progress_bar(spent, jumlah, 15)
            status, advice = get_budget_health_status(percentage)
            
            success_text += f"📊 <b>Status saat ini:</b>\n"
            success_text += f"{emoji} <code>{progress_bar}</code>\n"
            success_text += f"Sudah terpakai: Rp{spent:,} ({percentage:.1f}%)\n"
            success_text += f"Sisa: Rp{jumlah-spent:,}\n"
            success_text += f"Status: {status}\n\n"
            success_text += f"💡 {advice}"
        else:
            success_text += f"🆕 <b>Anggaran baru!</b> Belum ada pengeluaran di kategori ini bulan ini."
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💰 Kelola Anggaran", callback_data="menu_anggaran"))
        markup.add(types.InlineKeyboardButton("📊 Dashboard Anggaran", callback_data="list_budget"))
        markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
        
        bot.send_message(m.chat.id, success_text, parse_mode="HTML", reply_markup=markup)
    except:
        error_text = """
❌ <b>Format salah!</b>

📝 <b>Format yang benar:</b>
<code>/set_anggaran [kategori] [jumlah]</code>

<b>Contoh:</b>
• <code>/set_anggaran makanan 500000</code>
• <code>/set_anggaran transport 300000</code>
• <code>/set_anggaran hiburan 200000</code>

💡 <b>Tips Anggaran Sehat:</b>
• 50% untuk kebutuhan (makanan, transport, tagihan)
• 30% untuk keinginan (hiburan, shopping)
• 20% untuk tabungan dan investasi
        """
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎯 Panduan Set Anggaran", callback_data="guide_set_budget"))
        markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
        
        bot.send_message(m.chat.id, error_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['cek_anggaran'])
def cek_anggaran_enhanced(m):
    try:
        _, kategori = m.text.split(maxsplit=1)
        today = datetime.now().date()
        start = today.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        budgets = get_budget(m.from_user.id, start, end)
        spent = get_spent(m.from_user.id, kategori, start, end)
        v = budgets.get(kategori.lower(), 0)
        sisa = v - spent
        
        if v > 0:
            percentage = (spent / v * 100) if v > 0 else 0
            progress_bar, status_emoji = create_progress_bar(spent, v, 20)
            status, advice = get_budget_health_status(percentage)
            
            days_left = (end - today).days + 1
            daily_avg = spent / (today.day) if today.day > 0 else 0
            projected_monthly = daily_avg * end.day if daily_avg > 0 else 0
            
            result_text = f"""
{status_emoji} <b>Status Anggaran: {kategori.title()}</b>

📊 <b>Progress Visual:</b>
<code>{progress_bar}</code>

💰 <b>Budget:</b> Rp{v:,}
📤 <b>Terpakai:</b> Rp{spent:,}
💎 <b>Sisa:</b> Rp{sisa:,}

🎯 <b>Status:</b> {status}
💡 <b>Saran:</b> {advice}

📈 <b>Analisis Tambahan:</b>
• Hari tersisa bulan ini: {days_left} hari
• Rata-rata harian: Rp{daily_avg:,.0f}
            """
            
            if projected_monthly > 0:
                projection_percentage = (projected_monthly / v * 100) if v > 0 else 0
                if projection_percentage > 100:
                    result_text += f"⚠️ Proyeksi akhir bulan: Rp{projected_monthly:,.0f} (OVER BUDGET {projection_percentage-100:.0f}%!)"
                elif projection_percentage > 90:
                    result_text += f"🟠 Proyeksi akhir bulan: Rp{projected_monthly:,.0f} (Hampir habis!)"
                else:
                    result_text += f"✅ Proyeksi akhir bulan: Rp{projected_monthly:,.0f} (Aman)"
            
        else:
            result_text = f"""
⚠️ <b>Belum ada anggaran untuk '{kategori.title()}'</b>

💡 <b>Set anggaran sekarang:</b>
<code>/set_anggaran {kategori} [jumlah]</code>

<b>Contoh:</b>
<code>/set_anggaran {kategori} 500000</code>

💸 <b>Pengeluaran bulan ini:</b> Rp{spent:,}
            """
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💰 Kelola Anggaran", callback_data="menu_anggaran"))
        markup.add(types.InlineKeyboardButton("📊 Dashboard Lengkap", callback_data="list_budget"))
        markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
        
        bot.send_message(m.chat.id, result_text, parse_mode="HTML", reply_markup=markup)
    except:
        error_text = """
❌ <b>Format salah!</b>

📝 <b>Format yang benar:</b>
<code>/cek_anggaran [kategori]</code>

<b>Contoh:</b>
• <code>/cek_anggaran makanan</code>
• <code>/cek_anggaran transport</code>
• <code>/cek_anggaran hiburan</code>

💡 <b>Fitur Enhanced:</b>
✅ Progress bar visual
✅ Proyeksi pengeluaran
✅ Smart recommendations
        """
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("💰 Panduan Cek Anggaran", callback_data="guide_check_budget"))
        markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
        
        bot.send_message(m.chat.id, error_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['list_anggaran'])
def list_anggaran_enhanced(m):
    today = datetime.now().date()
    start = today.replace(day=1)
    end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    budgets = get_budget(m.from_user.id, start, end)
    
    if not budgets:
        result_text = """
⚠️ <b>Belum ada anggaran bulan ini</b>

🎯 <b>Mulai kelola keuangan Anda:</b>

💡 Set anggaran pertama:
<code>/set_anggaran [kategori] [jumlah]</code>

<b>Contoh kategori penting:</b>
• <code>/set_anggaran makanan 1000000</code>
• <code>/set_anggaran transport 500000</code>
• <code>/set_anggaran tagihan 800000</code>
• <code>/set_anggaran hiburan 300000</code>
        """
    else:
        result_text = f"💰 <b>Dashboard Anggaran Enhanced</b>\n"
        result_text += f"📅 <b>Bulan {datetime.now().strftime('%B %Y')}</b>\n\n"
        
        total_budget = sum(budgets.values())
        total_spent = sum(get_spent(m.from_user.id, k, start, end) for k in budgets.keys())
        
        overall_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
        overall_bar, overall_emoji = create_progress_bar(total_spent, total_budget, 20)
        overall_status, _ = get_budget_health_status(overall_percentage)
        
        result_text += f"📊 <b>RINGKASAN KESELURUHAN</b>\n"
        result_text += f"{overall_emoji} <code>{overall_bar}</code>\n"
        result_text += f"Status: {overall_status}\n"
        result_text += f"💰 Total Budget: Rp{total_budget:,}\n"
        result_text += f"📤 Total Terpakai: Rp{total_spent:,}\n"
        result_text += f"💎 Total Sisa: Rp{total_budget - total_spent:,}\n\n"
        
        result_text += "📋 <b>DETAIL PER KATEGORI</b>\n\n"
        
        category_data = []
        for k, v in budgets.items():
            spent = get_spent(m.from_user.id, k, start, end)
            percentage = (spent / v * 100) if v > 0 else 0
            category_data.append((k, v, spent, percentage))
        
        category_data.sort(key=lambda x: x[3], reverse=True)
        
        for k, v, spent, percentage in category_data:
            sisa = v - spent
            progress_bar, status_emoji = create_progress_bar(spent, v, 15)
            status, advice = get_budget_health_status(percentage)
            
            result_text += f"{status_emoji} <b>{k.title()}</b> - {status.split()[1]}\n"
            result_text += f"<code>{progress_bar}</code>\n"
            result_text += f"Budget: Rp{v:,} | Terpakai: Rp{spent:,} | Sisa: Rp{sisa:,}\n"
            
            if percentage > 80:
                result_text += f"💡 {advice}\n"
            result_text += "\n"
        
        tips = generate_smart_tips(m.from_user.id, start, end)
        if tips:
            result_text += "💡 <b>SMART RECOMMENDATIONS:</b>\n"
            for tip in tips[:2]:
                result_text += f"• {tip}\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🎯 Set Anggaran Baru", callback_data="guide_set_budget"))
    markup.add(types.InlineKeyboardButton("💰 Menu Anggaran", callback_data="menu_anggaran"))
    markup.add(types.InlineKeyboardButton("📊 Lihat Laporan", callback_data="menu_laporan"))
    markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
    
    bot.send_message(m.chat.id, result_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['laporanhari'])
def lap_hari(m):
    from .callback_handlers import kirim_laporan_enhanced # Import here to avoid circular dependency
    t = datetime.now().date()
    kirim_laporan_enhanced(m, t, t, f"Laporan Hari {t.strftime('%d-%m-%Y')}")

@bot.message_handler(commands=['laporanminggu'])
def lap_minggu(m):
    from .callback_handlers import kirim_laporan_enhanced # Import here to avoid circular dependency
    t = datetime.now().date()
    start = t - timedelta(days=t.weekday())
    end = start + timedelta(days=6)
    kirim_laporan_enhanced(m, start, end, f"Laporan Minggu {start.strftime('%d-%m')} - {end.strftime('%d-%m')}")

@bot.message_handler(commands=['laporanbulan'])
def lap_bulan(m):
    from .callback_handlers import kirim_laporan_enhanced # Import here to avoid circular dependency
    today = datetime.now()
    start = today.replace(day=1).date()
    end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    kirim_laporan_enhanced(m, start, end, f"Laporan Bulan {today.strftime('%B %Y')}")

@bot.message_handler(commands=['rekapbulanan'])
def rekap_bulan(m):
    from .callback_handlers import kirim_laporan_enhanced # Import here to avoid circular dependency
    try:
        _, bln, thn = m.text.split()
        start = datetime(int(thn), int(bln), 1).date()
        end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        kirim_laporan_enhanced(m, start, end, f"Rekap Bulan {start.strftime('%B %Y')}")
    except: 
        error_text = """
❌ <b>Format salah!</b>

📝 <b>Format yang benar:</b>
<code>/rekapbulanan mm yyyy</code>

<b>Contoh:</b>
• <code>/rekapbulanan 12 2024</code> → Desember 2024
• <code>/rekapbulanan 1 2025</code> → Januari 2025

✨ <b>Fitur Enhanced meliputi:</b>
• Progress bar untuk setiap kategori anggaran
• Chart ASCII untuk visualisasi pengeluaran
• Smart tips berdasarkan pola keuangan Anda
• Status kesehatan keuangan dengan emoji
        """
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📊 Panduan Laporan", callback_data="guide_custom_report"))
        markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
        
        bot.send_message(m.chat.id, error_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['status'])
def quick_status(m):
    today = datetime.now().date()
    start = today.replace(day=1)
    end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    p_today, q_today, s_today, _, _ = laporan_detail(m.from_user.id, today, today)
    p_month, q_month, s_month, kats, _ = laporan_detail(m.from_user.id, start, end)
    
    status_emoji = "💚" if s_month > 0 else "💔" if s_month < 0 else "⚖️"
    
    status_text = f"""
{status_emoji} <b>Quick Financial Status</b>

📅 <b>HARI INI ({today.strftime('%d-%m-%Y')})</b>
📥 Pemasukan: Rp{p_today:,}
📤 Pengeluaran: Rp{q_today:,}
💰 Net: Rp{s_today:,}

📅 <b>BULAN INI ({start.strftime('%B %Y')})</b>
📥 Pemasukan: Rp{p_month:,}
📤 Pengeluaran: Rp{q_month:,}
💰 Saldo: Rp{s_month:,}
    """
    
    budgets = get_budget(m.from_user.id, start, end)
    if budgets:
        status_text += "\n💰 <b>QUICK BUDGET CHECK</b>\n"
        critical_count = 0
        for k, v in budgets.items():
            spent = get_spent(m.from_user.id, k, start, end)
            percentage = (spent / v * 100) if v > 0 else 0
            if percentage > 80:
                critical_count += 1
                emoji = "🔴" if percentage > 100 else "🟠"
                status_text += f"{emoji} {k.title()}: {percentage:.0f}%\n"
        
        if critical_count == 0:
            status_text += "🟢 Semua anggaran masih aman!"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 Laporan Lengkap", callback_data="report_monthly"))
    markup.add(types.InlineKeyboardButton("💰 Dashboard Anggaran", callback_data="list_budget"))
    markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
    
    bot.send_message(m.chat.id, status_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['tips'])
def financial_tips(m):
    today = datetime.now().date()
    start = today.replace(day=1)
    end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
    
    tips = generate_smart_tips(m.from_user.id, start, end)
    
    tips_text = f"💡 <b>Smart Financial Tips</b>\n"
    tips_text += f"📅 <b>Berdasarkan data bulan {start.strftime('%B %Y')}</b>\n\n"
    
    if tips:
        for i, tip in enumerate(tips, 1):
            tips_text += f"{i}. {tip}\n\n"
    else:
        tips_text += "🎯 Belum cukup data untuk memberikan tips personal.\n\n"
        tips_text += "💡 <b>Tips Umum:</b>\n"
        tips_text += "• Catat setiap transaksi untuk tracking yang akurat\n"
        tips_text += "• Set anggaran untuk setiap kategori pengeluaran\n"
        tips_text += "• Review laporan mingguan untuk evaluasi\n"
        tips_text += "• Terapkan aturan 50/30/20 untuk alokasi dana"
    
    tips_text += "📚 <b>Financial Wisdom:</b>\n"
    tips_text += "• 'A budget is telling your money where to go instead of wondering where it went.'\n"
    tips_text += "• 'It's not how much money you make, but how much money you keep.'\n"
    tips_text += "• 'Don't save what is left after spending, spend what is left after saving.'"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 Lihat Laporan", callback_data="menu_laporan"))
    markup.add(types.InlineKeyboardButton("💰 Kelola Anggaran", callback_data="menu_anggaran"))
    markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
    
    bot.send_message(m.chat.id, tips_text, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['test_morning'])
def test_morning(m):
    if config.NOTIF_ENABLED and config.notif_api:
        try:
            config.notif_api.notif_system.send_morning_reminders()
            bot.reply_to(m, "✅ Morning reminder sudah dikirim!")
        except Exception as e:
            bot.reply_to(m, f"❌ Gagal kirim morning reminder: {e}")
    else:
        bot.reply_to(m, "⚠️ Notification system tidak aktif.")


@bot.message_handler(commands=['test_evening'])
def test_evening(m):
    if config.NOTIF_ENABLED and config.notif_api:
        try:
            config.notif_api.notif_system.send_evening_summary()
            bot.reply_to(m, "✅ Evening summary sudah dikirim!")
        except Exception as e:
            bot.reply_to(m, f"❌ Gagal kirim evening summary: {e}")
    else:
        bot.reply_to(m, "⚠️ Notification system tidak aktif.")


@bot.message_handler(commands=['test_budget'])
def test_budget(m):
    if config.NOTIF_ENABLED and config.notif_api:
        try:
            config.notif_api.notif_system.check_budget_alerts()
            bot.reply_to(m, "✅ Budget alert dicek & dikirim jika ada alert.")
        except Exception as e:
            bot.reply_to(m, f"❌ Gagal cek/kirim budget alert: {e}")
    else:
        bot.reply_to(m, "⚠️ Notification system tidak aktif.")

