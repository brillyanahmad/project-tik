"""
Server lokal untuk input data lewat browser.

    python server.py

Buka http://localhost:8000/input.html. Data disimpan ke folder data/ (CSV),
lalu analisis dihitung ulang otomatis dan dashboard tinggal di-refresh.
Hanya memakai pustaka bawaan Python dan hanya bisa diakses dari komputer ini.
"""
import csv
import json
import webbrowser
from datetime import date
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import analisis

BASE = Path(__file__).parent
DATA = BASE / "data"
PORT = 8000
PLATFORM = ("shopee", "tokopedia")
KOL_PRODUK = ["sku", "nama_produk", "harga_modal", "harga_jual", "stok_awal", "stok_minimum"]
KOL_JUAL = ["tanggal", "order_id", "sku", "jumlah", "harga_jual", "biaya_platform"]


def baca(nama):
    p = DATA / f"{nama}.csv"
    return analisis.baca_csv(p) if p.exists() else []


def tulis(nama, kolom, rows):
    DATA.mkdir(exist_ok=True)
    with open(DATA / f"{nama}.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=kolom, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def hitung_ulang():
    try:
        analisis.build()
    except SystemExit as e:
        return str(e)  # mis. belum ada data penjualan
    return None


def simpan_produk(d):
    rows = [{k: str(p.get(k, "")).strip() for k in KOL_PRODUK} for p in d["produk"]]
    skus = [r["sku"] for r in rows]
    if "" in skus or len(set(skus)) != len(skus):
        raise ValueError("SKU kosong atau ganda")
    for r in rows:
        float(r["harga_modal"]); int(r["stok_awal"]); int(r["stok_minimum"])
        if r["harga_jual"]:
            float(r["harga_jual"])
    tulis("produk", KOL_PRODUK, rows)
    return {}


def tambah_penjualan(d):
    pf = d["platform"]
    if pf not in PLATFORM:
        raise ValueError("platform tidak dikenal")
    ada = baca(pf)
    kunci = {(r["order_id"], r["sku"]) for r in ada}
    baru, lewat = [], 0
    for r in d["rows"]:
        r = {k: str(r.get(k, "")).strip() for k in KOL_JUAL}
        if not r["sku"] or not r["order_id"]:
            raise ValueError("SKU dan no. pesanan wajib ada")
        date.fromisoformat(r["tanggal"])
        if int(r["jumlah"]) <= 0:
            raise ValueError("jumlah harus lebih dari 0")
        float(r["harga_jual"]); float(r["biaya_platform"] or 0)
        if (r["order_id"], r["sku"]) in kunci:
            lewat += 1
            continue
        kunci.add((r["order_id"], r["sku"]))
        baru.append(r)
    tulis(pf, KOL_JUAL, ada + baru)
    return {"ditambah": len(baru), "dilewati": lewat}


def hapus_penjualan(d):
    pf, i = d["platform"], int(d["index"])
    if pf not in PLATFORM:
        raise ValueError("platform tidak dikenal")
    ada = baca(pf)
    del ada[i]
    tulis(pf, KOL_JUAL, ada)
    return {}


RUTE = {"/api/produk": simpan_produk, "/api/penjualan": tambah_penjualan, "/api/hapus": hapus_penjualan}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(BASE), **k)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *a):
        pass

    def kirim(self, kode, obj):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(kode)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        if self.path == "/api/data":
            return self.kirim(200, {n: baca(n) for n in ("produk", *PLATFORM)})
        super().do_GET()

    def do_POST(self):
        fungsi = RUTE.get(self.path)
        if not fungsi or "application/json" not in self.headers.get("Content-Type", ""):
            return self.kirim(404, {"error": "Permintaan tidak dikenal"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            hasil = fungsi(json.loads(self.rfile.read(n) or b"{}"))
        except (ValueError, KeyError, TypeError, IndexError) as e:
            return self.kirim(400, {"error": f"Data tidak valid: {e}"})
        self.kirim(200, {"ok": True, "catatan": hitung_ulang(), **hasil})


if __name__ == "__main__":
    hitung_ulang()
    url = f"http://localhost:{PORT}/input.html"
    print(f"Server berjalan di {url}  (Ctrl+C untuk berhenti)")
    webbrowser.open(url)
    try:
        HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\nBerhenti.")
