# handlers/message_handlers.py
from config import bot, sheet_transaksi
from utils.data_processing import parse_transaksi, get_budget, get_spent
from utils.visual_enhancements import create_progress_bar, get_budget_health_status
from keyboards.inline_keyboards import create_main_menu
from datetime import datetime, timedelta, date
from telebot import types

@bot.message_handler(func=lambda m: not m.text.startswith('/'))
def handle_transaksi_enhanced(m):
    lines = m.text.strip().splitlines()
    results=[]; errors=[]
    
    for line in lines:
        d=parse_transaksi(line.strip())
        if not d:
            errors.append(line); continue
        tgl=datetime.now().strftime("%d-%m-%Y")
        sheet_transaksi.append_row([tgl,d['nominal'],d['keterangan'],d['kategori'],d['tipe'],m.from_user.id])
        
        tipe_emoji = "📥" if d['tipe'] == "pemasukan" else "📤"
        results.append(f"{tipe_emoji} <b>{d['tipe'].title()}</b> dicatat: {d['keterangan']} Rp{d['nominal']:,} ({d['kategori']})")
    
    reply = ""
    if results: 
        reply += "✅ <b>TRANSAKSI BERHASIL DICATAT:</b>\n\n"
        reply += "\n".join(results)
        
        expenses = [r for r in results if "📤" in r]
        if expenses:
            reply += "\n\n📊 <b>DAMPAK TERHADAP ANGGARAN:</b>\n"
            today = datetime.now().date()
            start = today.replace(day=1)
            end = (start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            budgets = get_budget(m.from_user.id, start, end)
            
            for line in lines:
                d = parse_transaksi(line.strip())
                if d and d['tipe'] == 'pengeluaran' and d['kategori'] in budgets:
                    spent = get_spent(m.from_user.id, d['kategori'], start, end)
                    budget = budgets[d['kategori']]
                    percentage = (spent / budget * 100) if budget > 0 else 0
                    
                    progress_bar, emoji = create_progress_bar(spent, budget, 12)
                    status, _ = get_budget_health_status(percentage)
                    
                    reply += f"{emoji} <b>{d['kategori'].title()}:</b> {status.split()[1]}\n"
                    reply += f"<code>{progress_bar}</code>\n"
                    reply += f"Terpakai: Rp{spent:,} dari Rp{budget:,}\n\n"
    
    if errors: 
        reply += "\n\n❌ <b>FORMAT SALAH:</b>\n"
        reply += "\n".join(errors)
        reply += "\n\n💡 <b>Format yang benar:</b> <code>[keterangan] +/-[jumlah] /[kategori]</code>\n"
        reply += "<b>Contoh:</b> <code>Makan siang -25000 /makanan</code>"
    
    markup = types.InlineKeyboardMarkup()
    if results:
        markup.add(types.InlineKeyboardButton("📊 Lihat Laporan Hari Ini", callback_data="report_daily"))
        markup.add(types.InlineKeyboardButton("💰 Cek Status Anggaran", callback_data="list_budget"))
    markup.add(types.InlineKeyboardButton("📝 Panduan Input", callback_data="menu_transaksi"))
    markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
    
    bot.send_message(m.chat.id, reply, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    unknown_text = f"""
❓ <b>Perintah tidak dikenal:</b> <code>{message.text}</code>

🤖 <b>Mungkin maksud Anda:</b>
• <code>/menu</code> - Menu utama
• <code>/help</code> - Panduan lengkap
• <code>/status</code> - Status keuangan cepat
• <code>/tips</code> - Tips finansial personal

📝 <b>Untuk catat transaksi:</b>
<code>[keterangan] +/-[jumlah] /[kategori]</code>

<b>Contoh:</b> <code>Makan siang -25000 /makanan</code>
    """
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🏠 Menu Utama", callback_data="main_menu"))
    markup.add(types.InlineKeyboardButton("❓ Bantuan", callback_data="help"))
    
    bot.send_message(message.chat.id, unknown_text, parse_mode="HTML", reply_markup=markup)
