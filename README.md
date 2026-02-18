# LinkedIn Queens Solver

## Brute Force Implementation (Exhaustive Search)

## Deskripsi Program

Program ini merupakan implementasi algoritma Brute Force (Exhaustive Search) untuk menyelesaikan permainan Queens LinkedIn.

Permainan Queens LinkedIn adalah permainan logika pada papan persegi berwarna dengan aturan:

- Setiap baris harus memiliki tepat satu queen.
- Setiap kolom harus memiliki tepat satu queen.
- Setiap daerah warna harus memiliki tepat satu queen.
- Tidak ada queen yang boleh saling bersebelahan, termasuk secara diagonal.

Program ini menyediakan dua mode brute force:

**Mode Ruang Pencarian Kombinasi (pow)**
Mengenumerasi seluruh kemungkinan pemilihan n sel dari total n² sel papan, kemudian memvalidasi setiap konfigurasi.

**Mode Ruang Pencarian n! (fact)**
Mengenumerasi seluruh permutasi kolom sepanjang n, kemudian memvalidasi setiap konfigurasi.

Kedua mode tetap merupakan brute force karena seluruh kandidat dalam ruang pencarian diperiksa tanpa heuristik, pruning, atau optimasi lainnya.

Program dilengkapi dengan antarmuka GUI untuk mempermudah penggunaan.

## Requirement

Program dibuat menggunakan:

- Python 3.10 atau lebih baru

Library yang digunakan:

- tkinter (GUI) → biasanya sudah tersedia pada instalasi Python standar
- time
- typing
- pathlib

Jika tkinter belum tersedia:

**Windows**

Biasanya sudah tersedia otomatis bersama Python.

**Linux**

```
sudo apt install python3-tk
```

## Cara Kompilasi

Program ini tidak memerlukan proses kompilasi, karena menggunakan Python (interpreted language).

### Windows

1. Pastikan Python sudah terinstal dan berada di PATH:
   ```
   py --version
   ```
   atau
   ```
   python --version
   ```

2. Verifikasi library yang diperlukan tersedia:
   ```
   py -m pip list
   ```
   (tkinter sudah tersedia secara default pada instalasi Python Windows)

### Linux

1. Pastikan Python sudah terinstal:
   ```
   python3 --version
   ```

2. Instal tkinter jika belum tersedia:
   ```
   sudo apt update
   sudo apt install python3-tk
   ```

3. Verifikasi library:
   ```
   python3 -m pip list
   ```

## Cara Menjalankan Program

### Windows

1. Buka Command Prompt atau PowerShell
2. Navigasi ke folder utama project:
   ```
   cd D:\Tucil1_13524098
   ```
3. Jalankan program dengan salah satu cara:
   ```
   py src/main.py
   ```
   atau
   ```
   python src/main.py
   ```
4. GUI akan terbuka secara otomatis

**Catatan:** Jika mendapatkan error PATH, gunakan path absolut ke Python atau gunakan `python` dengan `.py` association.

### Linux

1. Buka Terminal
2. Navigasi ke folder utama project:
   ```
   cd ~/path/to/Tucil1_13524098
   ```
3. Jalankan program:
   ```
   python3 src/main.py
   ```
4. GUI akan terbuka secara otomatis

**Catatan:** Pastikan direktori project memiliki izin akses yang tepat dengan:
   ```
   chmod +x src/main.py
   ```

### Troubleshooting

- **Error: Module tkinter not found (Linux):** Install dengan `sudo apt install python3-tk`
- **Error: command not found:** Gunakan `python3` pada Linux, `py` atau `python` pada Windows
- **Error: GUI tidak muncul:** Pastikan X11/display server berjalan pada sistem remote

## Cara Menggunakan Program

1. Klik tombol Upload untuk memilih file testcase (.txt).
2. Pilih mode brute force (pow atau fact) dengan tombol Optimize.
3. Klik tombol Solve.
4. Hasil solusi akan ditampilkan di tengah.
5. Waktu eksekusi dan jumlah iterasi akan ditampilkan.
6. Klik Save untuk menyimpan solusi ke file.
7. Jika input tidak valid atau tidak ditemukan solusi, pesan error akan ditampilkan pada area papan.

## Format File Input

File input harus berupa papan persegi (n × n) dengan huruf kapital sebagai penanda daerah warna.

Contoh:

```
AAAB
ABBB
ACCB
ACCB
```

- Setiap baris harus memiliki panjang yang sama.
- Jumlah huruf unik harus sama dengan ukuran papan (n).

## Author

- Nama : Reva Natania Sitohang
- NIM : 13524098
- Tucil 1 – Penyelesaian Permainan Queens Linkedin Strategi Algoritma IF2211

