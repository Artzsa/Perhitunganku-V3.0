# handlers/callback_handlers.py
from config import bot, my_logger
from keyboards.inline_keyboards import (
    create_main_menu, create_transaction_menu, create_budget_menu,
    create_report_menu, create_export_menu
)
from utils.data_processing import laporan_detail, get_budget, get_spent
from utils.visual_enhancements import create_progress_bar, get_budget_health_status, generate_smart_tips, create_spending_chart
from utils.excel_export import build_export_excel
from datetime import datetime, timedelta, date
from telebot import types

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    try:
        if call.data == "main_menu":
            menu_text = """
🎛️ <b>Menu Utama Bot Perhitunganku Enhanced</b>

✨ Dengan fitur visual terbaru untuk pengalaman yang lebih baik!

Pilih fitur yang ingin Anda gunakan:
            """
            try:
                bot.edit_message_text(menu_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=create_main_menu(), parse_mode="HTML")
            except Exception as e:
                bot.send_message(call.message.chat.id, menu_text, 
                                reply_markup=create_main_menu(), parse_mode="HTML")
        
        elif call.data == "menu_transaksi":
            trans_text = """
📝 <b>Menu Catat Transaksi</b>

💡 <b>Tips:</b> Bot akan memberikan feedback visual setelah Anda input transaksi!

Pilih jenis transaksi yang ingin dicatat:
            """
            try:
                bot.edit_message_text(trans_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=create_transaction_menu(), parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, trans_text,
                                reply_markup=create_transaction_menu(), parse_mode="HTML")
        
        elif call.data == "menu_anggaran":
            budget_text = """
💰 <b>Menu Kelola Anggaran</b>

📊 <b>Fitur Terbaru:</b> Progress bar visual untuk monitoring anggaran real-time!

Kelola anggaran bulanan Anda:
            """
            try:
                bot.edit_message_text(budget_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=create_budget_menu(), parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, budget_text,
                                reply_markup=create_budget_menu(), parse_mode="HTML")
        
        elif call.data == "menu_laporan":
            report_text = """
📊 <b>Menu Lihat Laporan</b>

🎯 <b>Enhanced Features:</b>
• Progress bar untuk setiap kategori
• Chart ASCII untuk visualisasi
• Smart tips berdasarkan data Anda

Pilih periode laporan yang ingin dilihat:
            """
            try:
                bot.edit_message_text(report_text, call.message.chat.id, call.message.message_id,
                             reply_markup=create_report_menu(), parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, report_text,
                                reply_markup=create_report_menu(), parse_mode="HTML")
        
        elif call.data == "menu_export":
            export_text = """
📤 <b>Menu Export Data</b>

Export data Anda ke file Excel:
            """
            try:
                bot.edit_message_text(export_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=create_export_menu(), parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, export_text,
                                reply_markup=create_export_menu(), parse_mode="HTML")
        
        elif call.data == "help":
            help_text = """
📚 <b>Panduan Bot Perhitunganku Enhanced</b>

<b>📝 Format Catat Transaksi:</b>
<code>[keterangan] +/-[jumlah] /[kategori]</code>

<b>Contoh:</b>
• <code>Makan siang -25000 /makanan</code>
• <code>Gaji bulan ini +3000000 /gaji</code>
• <code>Beli buku -50000 /edukasi</code>

<b>💰 Anggaran:</b>
• <code>/set_anggaran makanan 500000</code>
• <code>/cek_anggaran makanan</code>
• <code>/list_anggaran</code>

<b>📊 Laporan Enhanced:</b>
• <code>/laporanhari</code> | <code>/laporanminggu</code> | <code>/laporanbulan</code>
• <code>/rekapbulanan 12 2024</code>

<b>📤 Export:</b>
• <code>/export</code> → bulan ini
• <code>/export tahun</code>
• <code>/export 01-01-2024 31-01-2024</code>

<b>✨ Fitur Baru:</b>
• Progress bar visual untuk anggaran
• Smart tips berdasarkan pola pengeluaran
• Chart ASCII untuk visualisasi data
            """
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali ke Menu", callback_data="main_menu"))
            try:
                bot.edit_message_text(help_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, help_text,
                                reply_markup=markup, parse_mode="HTML")
        
        elif call.data == "guide_expense":
            guide_text = """
💸 <b>Panduan Catat Pengeluaran</b>

<b>Format:</b>
<code>[keterangan] -[jumlah] /[kategori]</code>

<b>Contoh yang benar:</b>
• <code>Makan siang -25000 /makanan</code>
• <code>Bensin motor -20000 /transport</code>
• <code>Beli baju -150000 /pakaian</code>
• <code>Bayar listrik -200000 /utilitas</code>

💡 <b>Tips:</b> Gunakan kategori yang konsisten agar laporan lebih akurat!

🎯 <b>Fitur Baru:</b> Setelah input, bot akan menampilkan progress anggaran kategori secara otomatis!
            """
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="menu_transaksi"))
            try:
                bot.edit_message_text(guide_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, guide_text,
                                reply_markup=markup, parse_mode="HTML")
        
        elif call.data == "guide_income":
            guide_text = """
💰 <b>Panduan Catat Pemasukan</b>

<b>Format:</b>
<code>[keterangan] +[jumlah] /[kategori]</code>

<b>Contoh yang benar:</b>
• <code>Gaji bulanan +3000000 /gaji</code>
• <code>Freelance design +500000 /freelance</code>
• <code>Bonus kinerja +1000000 /bonus</code>
• <code>Jual barang bekas +200000 /lainnya</code>

💡 <b>Tips:</b> Catat semua sumber pemasukan untuk tracking yang lengkap!
            """
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="menu_transaksi"))
            try:
                bot.edit_message_text(guide_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, guide_text,
                                reply_markup=markup, parse_mode="HTML")
        
        elif call.data == "format_help":
            format_text = """
📋 <b>Format Input Transaksi</b>

<b>Struktur Umum:</b>
<code>[Deskripsi] [+/-][Nominal] /[Kategori]</code>

<b>✅ Yang BENAR:</b>
• <code>Makan siang -25000 /makanan</code>
• <code>Gaji +3000000 /gaji</code>
• <code>Transport ojol -15000 /transport</code>

<b>❌ Yang SALAH:</b>
• <code>Makan siang 25000 makanan</code> (tanpa +/- dan /)
• <code>-25000 /makanan</code> (tanpa deskripsi)
• <code>Makan siang -25000</code> (tanpa kategori)

<b>📝 Multiple Transaksi:</b>
Bisa input beberapa sekaligus, pisah dengan enter:
<code>Sarapan -10000 /makanan
Transport -5000 /transport
Freelance +200000 /freelance</code>
            """
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="menu_transaksi"))
            try:
                bot.edit_message_text(format_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, format_text,
                                reply_markup=markup, parse_mode="HTML")
        
        elif call.data == "guide_set_budget":
            budget_guide_text = """
🎯 <b>Panduan Set Anggaran</b>

<b>Format:</b>
<code>/set_anggaran [kategori] [jumlah]</code>

<b>Contoh:</b>
• <code>/set_anggaran makanan 1000000</code>
• <code>/set_anggaran transport 300000</code>
• <code>/set_anggaran hiburan 200000</code>

💡 <b>Tips Anggaran yang Baik:</b>
• 50% untuk kebutuhan (needs)
• 30% untuk keinginan (wants)  
• 20% untuk tabungan (savings)

🎯 <b>Fitur Baru:</b> Setelah set anggaran, gunakan <code>/cek_anggaran</code> untuk melihat progress bar visual!

Ketik perintah langsung di chat untuk mengatur anggaran!
            """
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="menu_anggaran"))
            try:
                bot.edit_message_text(budget_guide_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, budget_guide_text,
                                reply_markup=markup, parse_mode="HTML")
        
        elif call.data == "guide_check_budget":
            check_guide_text = """
💰 <b>Panduan Cek Anggaran</b>

<b>Format:</b>
<code>/cek_anggaran [kategori]</code>

<b>Contoh:</b>
• <code>/cek_anggaran makanan</code>
• <code>/cek_anggaran transport</code>
• <code>/cek_anggaran hiburan</code>

<b>📊 Info yang ditampilkan (ENHANCED):</b>
✅ Progress bar visual dengan emoji status
✅ Total anggaran yang diset
✅ Jumlah yang sudah terpakai
✅ Sisa anggaran
✅ Persentase penggunaan
✅ Status kesehatan anggaran
✅ Smart tips berdasarkan kondisi

Ketik perintah langsung di chat untuk cek anggaran!
            """
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="menu_anggaran"))
            try:
                bot.edit_message_text(check_guide_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, check_guide_text,
                                reply_markup=markup, parse_mode="HTML")
        
        elif call.data == "list_budget":
            today = datetime.now().date()
            start = today.replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            budgets = get_budget(call.from_user.id, start, end)
            
            if not budgets:
                result_text = "⚠️ <b>Belum ada anggaran bulan ini</b>\n\n💡 Set anggaran pertama Anda dengan:\n<code>/set_anggaran [kategori] [jumlah]</code>"
            else:
                result_text = f"💰 <b>Dashboard Anggaran Bulan {datetime.now().strftime('%B %Y')}</b>\n\n"
                total_budget = sum(budgets.values())
                total_spent = sum(get_spent(call.from_user.id, k, start, end) for k in budgets.keys())
                
                for k, v in budgets.items():
                    spent = get_spent(call.from_user.id, k, start, end)
                    sisa = v - spent
                    percentage = (spent / v * 100) if v > 0 else 0
                    progress_bar, status_emoji = create_progress_bar(spent, v, 15)
                    status, advice = get_budget_health_status(percentage)
                    
                    result_text += f"{status_emoji} <b>{k.title()}</b> - {status.split()[1]}\n"
                    result_text += f"<code>{progress_bar}</code>\n"
                    result_text += f"   Budget: Rp{v:,} | Terpakai: Rp{spent:,} | Sisa: Rp{sisa:,}\n\n"
                
                overall_percentage = (total_spent / total_budget * 100) if total_budget > 0 else 0
                overall_bar, overall_emoji = create_progress_bar(total_spent, total_budget, 20)
                
                result_text += f"📊 <b>RINGKASAN KESELURUHAN</b>\n"
                result_text += f"{overall_emoji} <code>{overall_bar}</code>\n"
                result_text += f"💰 <b>Total Budget:</b> Rp{total_budget:,}\n"
                result_text += f"📤 <b>Total Terpakai:</b> Rp{total_spent:,}\n"
                result_text += f"💎 <b>Total Sisa:</b> Rp{total_budget - total_spent:,}"
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🎯 Set Anggaran Baru", callback_data="guide_set_budget"))
            markup.add(types.InlineKeyboardButton("💰 Menu Anggaran", callback_data="menu_anggaran"))
            markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
            
            try:
                bot.edit_message_text(result_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, result_text,
                                reply_markup=markup, parse_mode="HTML")
        
        elif call.data == "report_daily":
            class DummyMessage:
                def __init__(self, call):
                    self.chat = call.message.chat
                    self.from_user = call.from_user
                    self.message_id = call.message.message_id
            
            dummy_message = DummyMessage(call)
            t = datetime.now().date()
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            
            kirim_laporan_enhanced(dummy_message, t, t, f"Laporan Hari {t.strftime('%d-%m-%Y')}")
        
        elif call.data == "report_weekly":
            class DummyMessage:
                def __init__(self, call):
                    self.chat = call.message.chat
                    self.from_user = call.from_user
                    self.message_id = call.message.message_id
            
            dummy_message = DummyMessage(call)
            t = datetime.now().date()
            start = t - timedelta(days=t.weekday())
            end = start + timedelta(days=6)
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            
            kirim_laporan_enhanced(dummy_message, start, end, f"Laporan Minggu {start.strftime('%d-%m')} - {end.strftime('%d-%m')}")
        
        elif call.data == "report_monthly":
            class DummyMessage:
                def __init__(self, call):
                    self.chat = call.message.chat
                    self.from_user = call.from_user
                    self.message_id = call.message.message_id
            
            dummy_message = DummyMessage(call)
            today = datetime.now()
            start = today.replace(day=1).date()
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            
            kirim_laporan_enhanced(dummy_message, start, end, f"Laporan Bulan {today.strftime('%B %Y')}")
        
        elif call.data == "guide_custom_report":
            custom_guide_text = """
📊 <b>Panduan Laporan Custom Enhanced</b>

<b>Format untuk periode tertentu:</b>
<code>/rekapbulanan [bulan] [tahun]</code>

<b>Contoh:</b>
• <code>/rekapbulanan 12 2024</code> → Desember 2024
• <code>/rekapbulanan 1 2025</code> → Januari 2025

<b>🎯 Laporan Enhanced berisi:</b>
✅ Progress bar untuk setiap kategori
✅ Chart ASCII untuk visualisasi pengeluaran
✅ Total pemasukan & pengeluaran dengan emoji status
✅ Smart tips berdasarkan pola pengeluaran Anda
✅ Breakdown per kategori dengan mini progress bar
✅ Perbandingan dengan anggaran
✅ Daftar transaksi terbaru

Ketik perintah langsung di chat!
            """
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="menu_laporan"))
            try:
                bot.edit_message_text(custom_guide_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, custom_guide_text,
                                reply_markup=markup, parse_mode="HTML")
        
        elif call.data == "export_month":
            today = datetime.now().date()
            start = today.replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            class DummyMessage:
                def __init__(self, call):
                    self.chat = call.message.chat
                    self.from_user = call.from_user
                    self.message_id = call.message.message_id
            
            dummy_message = DummyMessage(call)
            export_data(dummy_message, start, end, "Bulan Ini")
        
        elif call.data == "export_year":
            today = datetime.now().date()
            start = date(today.year, 1, 1)
            end = date(today.year, 12, 31)
            
            class DummyMessage:
                def __init__(self, call):
                    self.chat = call.message.chat
                    self.from_user = call.from_user
                    self.message_id = call.message.message_id
            
            dummy_message = DummyMessage(call)
            export_data(dummy_message, start, end, "Tahun Ini")
        
        elif call.data == "guide_export_custom":
            export_guide_text = """
📤 <b>Panduan Export Custom</b>

<b>Format:</b>
<code>/export [tanggal_mulai] [tanggal_selesai]</code>

<b>Contoh:</b>
• <code>/export 01-01-2024 31-01-2024</code>
• <code>/export 15-12-2024 15-01-2025</code>

<b>Format tanggal:</b> dd-mm-yyyy

<b>📋 File Excel berisi:</b>
• Sheet Transaksi (semua transaksi)
• Sheet Anggaran (data anggaran)
• Sheet Dashboard (ringkasan & analisis enhanced)

Ketik perintah langsung di chat!
            """
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Kembali", callback_data="menu_export"))
            try:
                bot.edit_message_text(export_guide_text, call.message.chat.id, call.message.message_id,
                                     reply_markup=markup, parse_mode="HTML")
            except:
                bot.send_message(call.message.chat.id, export_guide_text,
                                reply_markup=markup, parse_mode="HTML")
        
        bot.answer_callback_query(call.id)
        
    except Exception as e:
        my_logger.error(f"Callback handler error: {e}")
        bot.answer_callback_query(call.id, "❌ Terjadi kesalahan, coba lagi")

def export_data(message, start_date, end_date, period_name):
    try:
        loading_msg = bot.send_message(message.chat.id, 
                                      f"⏳ Sedang memproses export {period_name}...\n📊 Mengumpulkan data...")
        
        bot.edit_message_text(f"⏳ Sedang memproses export {period_name}...\n📋 Membuat file Excel...", 
                             message.chat.id, loading_msg.message_id)
        
        bio = build_export_excel(message.from_user.id, start_date, end_date)
        
        bot.edit_message_text(f"⏳ Sedang memproses export {period_name}...\n📤 Mengirim file...", 
                             message.chat.id, loading_msg.message_id)
        
        bot.delete_message(message.chat.id, loading_msg.message_id)
        
        caption_text = f"✅ Export {period_name} berhasil!\n📅 Periode: {start_date.strftime('%d-%m-%Y')} s/d {end_date.strftime('%d-%m-%Y')}"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🏠 Kembali ke Menu", callback_data="main_menu"))
        
        bot.send_document(message.chat.id, bio, caption=caption_text, reply_markup=markup)
        
    except Exception as e:
        bot.edit_message_text(f"❌ <b>Export {period_name} gagal!</b>\n\n🔍 Error: {str(e)}\n\n💡 Coba lagi dalam beberapa saat.", 
                             message.chat.id, loading_msg.message_id, parse_mode="HTML")

def kirim_laporan_enhanced(m, start, end, judul):
    p, q, s, kats, trxs = laporan_detail(m.from_user.id, start, end)
    
    if s > 0:
        status_emoji = "💚"
        status_text = "Surplus"
    elif s == 0:
        status_emoji = "⚖️"
        status_text = "Break Even"
    else:
        status_emoji = "💔"
        status_text = "Defisit"
    
    teks = f"{status_emoji} <b>{judul}</b>\n\n"
    teks += f"📥 Pemasukan: Rp{p:,}\n"
    teks += f"📤 Pengeluaran: Rp{q:,}\n"
    teks += f"💰 Saldo: Rp{s:,} ({status_text})\n\n"
    
    if kats:
        teks += create_spending_chart(kats) + "\n\n"
        
        teks += "📂 <b>Detail Pengeluaran:</b>\n"
        tot = sum(kats.values())
        sorted_cats = sorted(kats.items(), key=lambda x: x[1], reverse=True)
        
        for k, v in sorted_cats:
            persen = (v/tot)*100 if tot > 0 else 0
            mini_bar = "█" * int(persen/10) + "░" * (10 - int(persen/10))
            teks += f"• {k.title()}: Rp{v:,} ({persen:.1f}%)\n  <code>{mini_bar}</code>\n"
    
    budgets = get_budget(m.from_user.id, start, end)
    if budgets:
        teks += "\n💰 <b>Status Anggaran:</b>\n"
        for k, budget_amount in budgets.items():
            spent = get_spent(m.from_user.id, k, start, end)
            percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
            
            progress_bar, emoji = create_progress_bar(spent, budget_amount, 15)
            status, _ = get_budget_health_status(percentage)
            
            teks += f"{emoji} <b>{k.title()}</b> {status.split()[1]}\n"
            teks += f"<code>{progress_bar}</code>\n"
            teks += f"Rp{spent:,} / Rp{budget_amount:,}\n\n"
    
    tips = generate_smart_tips(m.from_user.id, start, end)
    if tips:
        teks += "💡 <b>Smart Tips & Insights:</b>\n"
        for tip in tips:
            teks += f"• {tip}\n"
        teks += "\n"
    
    if trxs:
        teks += "📝 <b>Transaksi Terbaru:</b>\n"
        recent_trxs = sorted(trxs, key=lambda x: x[0], reverse=True)[:5]
        for tgl, ket, nom, kat, tipe in recent_trxs:
            tanda = "📥" if tipe == "pemasukan" else "📤"
            amount_str = f"+Rp{nom:,}" if tipe == "pemasukan" else f"-Rp{nom:,}"
            teks += f"{tanda} {tgl.strftime('%d/%m')}: {ket[:20]} {amount_str}\n"
        
        if len(trxs) > 5:
            teks += f"... dan {len(trxs)-5} transaksi lainnya\n"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📊 Menu Laporan", callback_data="menu_laporan"))
    markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
    
    bot.send_message(m.chat.id, teks, parse_mode="HTML", reply_markup=markup)
