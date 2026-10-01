# PANDUAN PENGUJIAN DES MANUAL V3 (CROSS-PLATFORM & CROSS-OS)

Panduan ini berisi langkah-langkah pengujian komunikasi terenkripsi 2 arah menggunakan algoritma **DES (Data Encryption Standard)** yang diimplementasikan secara **manual dari nol**.

## Daftar Berkas V3:
1. `cipher_manual-v3.py` (Rename menjadi `cipher_manual.py` saat disimpan di folder kerja)
2. `receiver_node-v3.py`
3. `sender_node-v3.py`

---

## Langkah Setup & Pengujian (Windows Host vs VM Linux NAT)

### 1. Persiapan File
Pastikan ketiga berkas (`cipher_manual.py`, `receiver_node-v3.py`, dan `sender_node-v3.py`) disimpan dalam **satu folder yang sama** baik di Windows Host maupun di VM Linux.

> **Penting**: Rename `cipher_manual-v3.py` menjadi `cipher_manual.py` agar impor modul berjalan lancar.

---

### 2. Eksekusi Program

#### A. Di VM Linux (Receiver / Node A)
Buka Terminal di VM Linux, lalu jalankan:
```bash
python3 receiver_node-v3.py 0.0.0.0 65432
```
*(Argumen `0.0.0.0` memastikan Receiver menerima koneksi dari antarmuka VMnet8 NAT).*

#### B. Di Windows Host (Sender / Node B)
Buka Command Prompt / PowerShell di Windows Host, lalu jalankan:
```cmd
python sender_node-v3.py 192.168.207.128 65432
```
*(Ganti `192.168.207.128` dengan IP VM Linux Anda).*

---

## Penjelasan Terkait Output Mismatch (Troubleshooting)

Jika pada terminal muncul karakter acak seperti `ǨFV?J0`:
- **Penyebab**: Terjadi ketidakcocokan algoritma/berkas antara kedua mesin (misalnya salah satu mesin menjalankan script versi lama `RC4`, sedangkan mesin lainnya menjalankan versi `DES`).
- **Solusi**: Pastikan **KEDUA MESIN** (Windows dan VM Linux) memperbarui seluruh berkas ke versi **V3 (DES)** yang menggunakan kunci 8-byte `b"KunciDES"`.
