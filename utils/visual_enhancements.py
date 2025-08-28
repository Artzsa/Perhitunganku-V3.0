# utils/visual_enhancements.py
from .data_processing import laporan_detail, get_budget, get_spent
from datetime import datetime

def create_progress_bar(current, target, width=20):
    """Membuat progress bar visual dengan emoji dan status"""
    if target == 0:
        return "░" * width + " 0%", "⚪"
    
    percentage = min(current / target, 1.0)
    filled = int(percentage * width)
    
    # Pilih emoji berdasarkan persentase
    if percentage < 0.5:
        emoji = "🟢"
        bar_char = "█"
    elif percentage < 0.8:
        emoji = "🟡" 
        bar_char = "█"
    elif percentage <= 1.0:
        emoji = "🟠"
        bar_char = "█"
    else:
        emoji = "🔴"
        bar_char = "█"
        filled = width  # Full bar jika over budget
    
    bar = bar_char * filled + "░" * (width - filled)
    return f"{bar} {percentage*100:.1f}%", emoji

def get_budget_health_status(percentage):
    """Get status kesehatan anggaran"""
    if percentage < 50:
        return "🟢 Aman", "Pengeluaran masih terkendali dengan baik!"
    elif percentage < 70:
        return "🟡 Hati-hati", "Mulai perhatikan pengeluaran Anda."
    elif percentage < 90:
        return "🟠 Waspada", "Anggaran hampir habis, kurangi pengeluaran!"
    elif percentage <= 100:
        return "🔴 Bahaya", "Anggaran hampir habis!"
    else:
        return "💥 Over Budget!", "Anda sudah melewati batas anggaran!"

def generate_smart_tips(uid, start_date, end_date):
    """Generate tips cerdas berdasarkan pola pengeluaran user"""
    tips = []
    
    # Ambil data transaksi dan anggaran
    pemasukan, pengeluaran, saldo, kategori_sums, _ = laporan_detail(uid, start_date, end_date)
    budgets = get_budget(uid, start_date, end_date)
    
    # Tip 1: Analisis Saldo
    if saldo < 0:
        tips.append("💸 <b>Urgent:</b> Saldo minus! Segera kurangi pengeluaran atau cari pemasukan tambahan.")
    elif saldo < pemasukan * 0.1:  # Saldo kurang dari 10% pemasukan
        tips.append("⚠️ <b>Peringatan:</b> Saldo tipis! Lebih hati-hati dengan pengeluaran.")
    else:
        tips.append("👍 <b>Good Job:</b> Saldo masih sehat!")
    
    # Tip 2: Analisis per Kategori
    for kategori, spent in kategori_sums.items():
        if kategori in budgets:
            budget = budgets[kategori]
            percentage = (spent / budget * 100) if budget > 0 else 0
            
            if percentage > 100:
                tips.append(f"🚨 <b>{kategori.title()}:</b> Over budget {percentage-100:.0f}%! Segera batasi pengeluaran kategori ini.")
            elif percentage > 80:
                tips.append(f"🟠 <b>{kategori.title()}:</b> Sudah {percentage:.0f}% dari budget. Hati-hati ya!")
    
    # Tip 3: Kategori Terbesar
    if kategori_sums:
        biggest_category = max(kategori_sums.items(), key=lambda x: x[1])
        biggest_name, biggest_amount = biggest_category
        total_expense = sum(kategori_sums.values())
        biggest_percentage = (biggest_amount / total_expense * 100) if total_expense > 0 else 0
        
        if biggest_percentage > 40:
            tips.append(f"📊 <b>Insight:</b> {biggest_name.title()} adalah pengeluaran terbesar Anda ({biggest_percentage:.0f}%). Coba cari cara untuk mengoptimalkannya!")
    
    # Tip 4: Motivasi/Appreciation
    if not any("Over budget" in tip for tip in tips) and saldo > 0:
        tips.append("🌟 <b>Excellent:</b> Semua anggaran terkendali! Pertahankan kebiasaan baik ini.")
    
    # Tip 5: Saran Umum
    if len(budgets) < 3:
        tips.append("💡 <b>Saran:</b> Buat anggaran untuk lebih banyak kategori agar keuangan lebih terstruktur!")
    
    return tips[:3]  # Batasi maksimal 3 tips

def create_spending_chart(kategori_sums, max_width=15):
    """Membuat chart pengeluaran dengan bar ASCII"""
    if not kategori_sums:
        return "📊 Belum ada data pengeluaran."
    
    max_val = max(kategori_sums.values())
    chart = "📊 <b>Visualisasi Pengeluaran:</b>\n<pre>"
    
    # Sort berdasarkan nilai tertinggi
    sorted_items = sorted(kategori_sums.items(), key=lambda x: x[1], reverse=True)
    
    for kategori, nilai in sorted_items[:5]:  # Top 5 kategori
        bar_length = int((nilai / max_val) * max_width) if max_val > 0 else 0
        bar = "█" * bar_length + "░" * (max_width - bar_length)
        
        # Truncate kategori name jika terlalu panjang
        kategori_display = kategori[:8].ljust(8)
        chart += f"{kategori_display} {bar} {nilai/1000:.0f}k\n"
    
    chart += "</pre>"
    return chart
