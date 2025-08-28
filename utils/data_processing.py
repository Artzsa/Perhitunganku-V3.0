# utils/data_processing.py
from datetime import datetime, timedelta, date
from collections import defaultdict
from config import sheet_transaksi, sheet_budget, sheet_kategori

def parse_date(val):
    if not val: return None
    if isinstance(val, datetime): return val.date()
    for fmt in ("%d-%m-%Y","%Y-%m-%d","%d/%m/%Y"):
        try: return datetime.strptime(str(val).strip(), fmt).date()
        except: continue
    return None

def clean_int(val):
    if val is None: return 0
    if isinstance(val,(int,float)): return int(val)
    val = str(val).replace("Rp","").replace(",","").replace(".","").strip()
    try: return int(val)
    except: return 0

def get_date_range_from_args(args_text: str):
    today = date.today()
    s = (args_text or "").strip()
    if not s:
        start = today.replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)-timedelta(days=1)
        return start, end
    if s.lower() == "tahun":
        return date(today.year,1,1), date(today.year,12,31)
    try:
        d1,d2 = s.split()
        start = datetime.strptime(d1,"%d-%m-%Y").date()
        end   = datetime.strptime(d2,"%d-%m-%Y").date()
        return (start,end) if start<=end else (end,start)
    except:
        return None,None

def load_data(user_id):
    rows_t = sheet_transaksi.get_all_records()
    rows_b = sheet_budget.get_all_records()
    kategori_map = {}
    if sheet_kategori:
        for r in sheet_kategori.get_all_records():
            k = str(r.get("Kategori","")).lower().strip()
            g = str(r.get("Grup503020","")).strip()
            if k: kategori_map[k]=g if g in ("Needs","Wants","Savings") else "Unmapped"
    transaksi=[]
    for r in rows_t:
        tgl = parse_date(r.get("Tanggal"))
        if not tgl: continue
        if str(r.get("ID User"))!=str(user_id): continue
        transaksi.append({
            "Tanggal": tgl,
            "Nominal": clean_int(r.get("Nominal")),
            "Keterangan": r.get("Keterangan",""),
            "Kategori": str(r.get("Kategori","")).lower().strip(),
            "Tipe": str(r.get("Tipe","")).lower().strip()
        })
    anggaran=[]
    for r in rows_b:
        tgl = parse_date(r.get("Tanggal"))
        if not tgl: continue
        if str(r.get("ID User"))!=str(user_id): continue
        anggaran.append({
            "Tanggal":tgl,
            "Kategori":str(r.get("Kategori","")).lower().strip(),
            "Budget":clean_int(r.get("Budget",0))
        })
    return transaksi,anggaran,kategori_map

def get_budget(uid,start,end):
    data={}
    for r in sheet_budget.get_all_records():
        t=parse_date(r.get('Tanggal'))
        if not t: continue
        if str(r.get('ID User'))==str(uid) and start<=t<=end:
            k=r['Kategori'].lower()
            data[k]=data.get(k,0)+clean_int(r['Budget'])
    return data

def get_spent(uid,k,start,end):
    tot=0
    for r in sheet_transaksi.get_all_records():
        t=parse_date(r.get('Tanggal'))
        if not t: continue
        if str(r.get('ID User'))==str(uid) and r['Kategori'].lower()==k.lower() and r['Tipe'].lower()=="pengeluaran" and start<=t<=end:
            tot+=clean_int(r['Nominal'])
    return tot

def laporan_detail(uid,start,end):
    pemasukan=pengeluaran=0; kategori_sums={}; trxs=[]
    for r in sheet_transaksi.get_all_records():
        t=parse_date(r.get('Tanggal'))
        if not t: continue
        if str(r.get('ID User'))!=str(uid): continue
        if not (start<=t<=end): continue
        nominal=clean_int(r['Nominal'])
        trxs.append((t,r['Keterangan'],nominal,r['Kategori'],r['Tipe']))
        if r['Tipe'].lower()=="pemasukan": pemasukan+=nominal
        elif r['Tipe'].lower()=="pengeluaran":
            pengeluaran+=nominal
            k=r['Kategori'].lower()
            kategori_sums[k]=kategori_sums.get(k,0)+nominal
    return pemasukan,pengeluaran,pemasukan-pengeluaran,kategori_sums,trxs

def parse_transaksi(msg):
    try:
        if '/' not in msg:return None
        desc_nom,kat=msg.split('/')
        if '+' in desc_nom:desc,nom=desc_nom.split('+');tipe="pemasukan"
        elif '-' in desc_nom:desc,nom=desc_nom.split('-');tipe="pengeluaran"
        else:return None
        return {"keterangan":desc.strip(),"nominal":clean_int(nom),"kategori":kat.strip().lower(),"tipe":tipe}
    except:return None
