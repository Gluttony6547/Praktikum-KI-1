# Panduan Pengujian Sistem Enkripsi DES Dua Arah (Host Windows & VM Linux)

## 📌 Ringkasan Implementasi

Pada pembaruan ini, seluruh sistem enkripsi telah disesuaikan untuk menggunakan **Data Encryption Standard (DES)** yang diimplementasikan **100% secara manual dari nol** tanpa menggunakan library kriptografi eksternal (murni standar Python).

### Fitur Utama Kode DES Manual (`cipher_manual.py`):
1. **Model Blok Simetris (Feistel Network 16 Round)**: Memproses data per blok 64-bit (8 Byte).
2. **Key Scheduling Algorithm**: Menggenerasi 16 subkey 48-bit dari Pre-Shared Key 64-bit (8 Byte).
3. **Fungsi Feistel ($F$-Function)**:
   - Expansion Permutation ($E$-Table: 32 bit -> 48 bit)
   - XOR dengan Subkey
   - S-Box Substitution (8 S-Box 6x4)
   - Permutation ($P$-Table: 32 bit)
4. **PKCS#7 Padding**: Menangani pesan dinamis dengan panjang arbitrary agar selalu genap kelipatan 8 Byte.

---

## 🛠️ Struktur Berkas

1. `cipher_manual.py` : Class `ManualDES` yang berisi logika enkripsi, dekripsi, KSA, S-Box, dan PKCS#7 Padding.
2. `receiver_node-v2.py` : Program Receiver (Node A) berbasis TCP Socket & Multithreading.
3. `sender_node-v2.py` : Program Sender (Node B) berbasis TCP Socket & Multithreading.

---

## 🌐 Skenario Pengujian: Laptop Utama (Windows Host) vs VM Linux (NAT)

### Langkah 1: Persiapan
1. Pastikan berkas `cipher_manual.py`, `receiver_node-v2.py`, dan `sender_node-v2.py` berada dalam satu folder yang sama di **Windows Host** dan **VM Linux**.

### Langkah 2: Mengetahui IP VM Linux
Di Terminal VM Linux, jalankan:
```bash
ip a
```
Catat IP pada interface `ens33` (contoh: `192.168.207.128`).

### Langkah 3: Eksekusi Receiver di VM Linux
Buka Terminal di **VM Linux** dan jalankan:
```bash
python3 receiver_node-v2.py 0.0.0.0 65432
```
*Catatan: Argumen `0.0.0.0` memastikan Receiver mendengarkan koneksi dari semua antarmuka jaringan VMnet8.*

### Langkah 4: Eksekusi Sender di Laptop Utama (Windows Host)
Buka Command Prompt (CMD) / PowerShell di **Windows Host** dan jalankan:
```cmd
python sender_node-v2.py 192.168.207.128 65432
```
*(Ganti `192.168.207.128` dengan IP VM Linux Anda).*

---

## 🧪 Pengujian Komunikasi 2 Arah

1. **Pengiriman dari Windows Host (Sender) ke VM Linux (Receiver)**:
   - Masukkan pesan pada CMD Windows: `Halo dari Windows Host menggunakan algoritma DES!`
   - Terminal VM Linux akan menampilkan:
     - **Ciphertext DES (HEX)** hasil enkripsi DES.
     - **Plaintext Hasil** setelah didekripsi secara otomatis dengan Pre-Shared Key DES.

2. **Pengiriman Balasan dari VM Linux (Receiver) ke Windows Host (Sender)**:
   - Masukkan pesan pada Terminal Linux: `Pesan terenkripsi DES diterima dengan sukses oleh VM Linux!`
   - CMD Windows akan menampilkan pesan hasil dekripsi secara real-time.

---

## 🛡️ Troubleshooting Firewall Linux
Jika koneksi ditolak (*Connection Refused* / *Timeout*), jalankan perintah berikut di VM Linux untuk mengizinkan port 65432:
```bash
sudo ufw allow 65432/tcp
```
