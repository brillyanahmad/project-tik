# Dashboard Penjualan UMKM

Memantau penjualan Shopee dan Tokopedia dalam satu tampilan: produk terlaris, laba, dan stok gudang.

## Cara menjalankan

1. Pastikan Python 3.8+ terpasang (tanpa pustaka tambahan).
2. Jalankan `python analisis.py`, lalu buka `index.html` dengan klik dua kali.
   Atau cukup `python jalankan.py` untuk analisis sekaligus membuka browser.
3. Setiap data berubah, jalankan ulang `python analisis.py` lalu refresh browser.

## Input data lewat browser

Jalankan `python server.py` (halaman `input.html` terbuka otomatis). Ada tiga tab:

- **Catat penjualan**: pilih produk, isi jumlah dan harga. Biaya platform terisi otomatis dari persentase yang bisa Anda atur.
- **Produk dan stok**: tambah atau ubah produk, dan tombol Tambah stok saat barang masuk gudang.
- **Impor CSV**: tarik file ekspor Shopee atau Tokopedia, cocokkan kolomnya (ditebak otomatis dan diingat), lalu impor. Data ganda dilewati.

Setiap simpan, `data/*.csv` diperbarui dan `data.js` dihitung ulang. Cukup refresh `index.html`.
Server hanya bisa diakses dari komputer Anda sendiri.

## Struktur folder

```
index.html            tampilan dashboard
input.html            form input dan impor data (butuh server.py)
server.py             server lokal untuk menyimpan input ke CSV
analisis.py           fungsi analisis (menghasilkan data.js)
jalankan.py           analisis + buka browser
buat_contoh_data.py   pembuat data contoh
data.js               hasil analisis (dibuat otomatis)
data/produk.csv       master produk
data/shopee.csv       penjualan Shopee
data/tokopedia.csv    penjualan Tokopedia
```

## Format CSV

`data/produk.csv`
```
sku,nama_produk,harga_modal,stok_awal,stok_minimum
KRP-01,Keripik Tempe Original,9000,900,100
```

`data/shopee.csv` dan `data/tokopedia.csv` (format sama)
```
tanggal,order_id,sku,jumlah,harga_jual,biaya_platform
2026-10-28,SPE10280001,KRP-01,2,18000,2880
```

- `harga_jual`: harga per unit. `biaya_platform`: total biaya admin/komisi untuk baris itu.
- `sku` harus sama dengan yang ada di `produk.csv`.
- Laba = omzet - modal (HPP) - biaya platform.
- Sisa stok = `stok_awal` - total unit terjual di semua marketplace.
  Perbarui `stok_awal` saat Anda restock, lalu hapus transaksi lama atau sesuaikan nilainya.

Untuk memakai data asli, ganti isi ketiga CSV di atas (hapus data contoh), lalu jalankan `python analisis.py`.

## Upload ke GitHub

Unggah seluruh folder. Agar dashboard bisa dibuka online, aktifkan GitHub Pages
(Settings > Pages > Deploy from branch). Data bisnis Anda ikut terunggah,
jadi gunakan repositori private bila datanya tidak untuk umum.
