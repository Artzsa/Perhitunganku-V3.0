# utils/excel_export.py
from io import BytesIO
import xlsxwriter
from collections import defaultdict
from .data_processing import load_data, parse_date, clean_int
from datetime import datetime

def build_export_excel(user_id,start:datetime.date,end:datetime.date):
    transaksi, anggaran, kategori_map = load_data(user_id)
    trx = [t for t in transaksi if start <= t["Tanggal"] <= end]
    bud = [b for b in anggaran if start <= b["Tanggal"] <= end]

    pemasukan = sum(t["Nominal"] for t in trx if t["Tipe"]=="pemasukan")
    pengeluaran = sum(t["Nominal"] for t in trx if t["Tipe"]=="pengeluaran")
    saldo = pemasukan - pengeluaran

    gsum = defaultdict(int)
    for t in trx:
        if t["Tipe"]!="pengeluaran": continue
        grp = kategori_map.get(t["Kategori"],"Unmapped")
        gsum[grp]+=t["Nominal"]

    g_needs, g_wants, g_savings = gsum.get("Needs",0), gsum.get("Wants",0), gsum.get("Savings",0)
    total_out = g_needs+g_wants+g_savings

    bio = BytesIO()
    wb = xlsxwriter.Workbook(bio,{"in_memory":True})
    fmt_header = wb.add_format({"bold":True,"bg_color":"#F2F2F2"})
    fmt_date   = wb.add_format({"num_format":"dd-mm-yyyy"})
    fmt_num    = wb.add_format({'num_format':'"Rp" #,##0'})
    fmt_pct    = wb.add_format({"num_format":"0.0%"})

    # Worksheet Transaksi
    ws_t=wb.add_worksheet("Transaksi")
    ws_t.write_row(0,0,["Tanggal","Keterangan","Kategori","Tipe","Nominal"],fmt_header)
    for i,t in enumerate(trx,1):
        ws_t.write_datetime(i,0,datetime.combine(t["Tanggal"],datetime.min.time()),fmt_date)
        ws_t.write(i,1,t["Keterangan"]); ws_t.write(i,2,t["Kategori"]); ws_t.write(i,3,t["Tipe"])
        ws_t.write_number(i,4,t["Nominal"],fmt_num)

    # Worksheet Anggaran
    ws_b=wb.add_worksheet("Anggaran")
    ws_b.write_row(0,0,["Tanggal","Kategori","Budget"],fmt_header)
    for i,b in enumerate(bud,1):
        ws_b.write_datetime(i,0,datetime.combine(b["Tanggal"],datetime.min.time()),fmt_date)
        ws_b.write(i,1,b["Kategori"]); ws_b.write_number(i,2,b["Budget"],fmt_num)

    # Worksheet Dashboard Enhanced
    ws_d=wb.add_worksheet("Dashboard")
    
    ws_d.write(0,0,"Enhanced Financial Dashboard",fmt_header)
    ws_d.write(1,0,"Periode")
    ws_d.write(1,2,f"{start.strftime('%d-%m-%Y')} s.d. {end.strftime('%d-%m-%Y')}")
    ws_d.write(2,0,"Total Pemasukan")
    ws_d.write(2,2,pemasukan,fmt_num)
    ws_d.write(3,0,"Total Pengeluaran")  
    ws_d.write(3,2,pengeluaran,fmt_num)
    ws_d.write(4,0,"Saldo")
    ws_d.write(4,2,saldo,fmt_num)

    ws_d.write(6,0,"50/30/20 Analysis",fmt_header)
    ws_d.write(7,0,"Group",fmt_header)
    ws_d.write(7,1,"Nominal",fmt_header)  
    ws_d.write(7,2,"Persentase",fmt_header)
    ws_d.write(7,3,"Status",fmt_header)
    
    if total_out > 0:
        needs_pct = (g_needs / total_out)
        wants_pct = (g_wants / total_out) 
        savings_pct = (g_savings / total_out)
    else:
        needs_pct = wants_pct = savings_pct = 0

    ws_d.write(8,0,"Needs")
    ws_d.write(8,1,g_needs,fmt_num)
    ws_d.write(8,2,needs_pct,fmt_pct)
    ws_d.write(8,3,"Ideal: 50%" if needs_pct <= 0.5 else "Over Budget!")
    
    ws_d.write(9,0,"Wants") 
    ws_d.write(9,1,g_wants,fmt_num)
    ws_d.write(9,2,wants_pct,fmt_pct)
    ws_d.write(9,3,"Ideal: 30%" if wants_pct <= 0.3 else "Over Budget!")
    
    ws_d.write(10,0,"Savings")
    ws_d.write(10,1,g_savings,fmt_num) 
    ws_d.write(10,2,savings_pct,fmt_pct)
    ws_d.write(10,3,"Ideal: 20%" if savings_pct >= 0.2 else "Kurang!")

    ws_d.write(12,0,"Ideal Ratio Targets",fmt_header)
    ws_d.write(13,0,"Needs: 50% (Kebutuhan)")
    ws_d.write(14,0,"Wants: 30% (Keinginan)") 
    ws_d.write(15,0,"Savings: 20% (Tabungan)")

    ws_d.set_column(0,0,25)
    ws_d.set_column(1,1,15)
    ws_d.set_column(2,2,15)
    ws_d.set_column(3,3,20)

    wb.close()
    bio.seek(0)
    bio.name=f"Export_Enhanced_{user_id}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.xlsx"
    return bio
