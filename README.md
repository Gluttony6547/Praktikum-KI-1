# Dokumentasi Alur Komunikasi DES Manual V3

## Cakupan

Dokumen ini menjelaskan implementasi `ManualDES` pada `cipher_manual.py`, komunikasi dua arah pada `sender_node-v3.py` dan `receiver_node-v3.py`, serta cara menguji program berdasarkan `README_Pengujian-v3.md`.

Program ini merupakan simulasi pengiriman **pesan teks** terenkripsi melalui TCP. Kode yang tersedia belum mengimplementasikan transfer berkas.

## Susunan Program

| Berkas | Tanggung jawab |
|---|---|
| `cipher_manual.py` | Konversi bit, jadwal kunci, putaran DES, padding, enkripsi, dan dekripsi. |
| `receiver_node-v3.py` | Membuka server TCP, menerima koneksi sender, membaca pesan, dan mengirim balasan. |
| `sender_node-v3.py` | Membuat koneksi ke receiver, mengirim pesan, dan membaca balasan. |
| `README_Pengujian-v3.md` | Petunjuk menjalankan simulasi Windows Host dengan VM Linux. |

## Alur Komunikasi

Receiver bertindak sebagai server dan sender sebagai client. Keduanya menggunakan kunci yang telah dikonfigurasi di program; kunci tidak dikirimkan lewat socket.

```text
Sender                                        Receiver
  |                                               |
  |                         bind, listen, accept  |
  |--- TCP connect ----------------------------->|
  |                                               |
  | input teks                                   |
  | DES.encrypt(UTF-8)                           |
  |--- ciphertext melalui sendall() ------------>|
  |                            recv() -> decrypt  |
  |                            tampilkan teks     |
  |                                               |
  |              input balasan                    |
  |              DES.encrypt(UTF-8)              |
  |<--- ciphertext melalui sendall() ------------|
  | recv() -> decrypt                             |
  | tampilkan teks                                |
```

### Receiver

1. `main()` membaca alamat bind dan port dari argumen command line. Nilai bawaan adalah `0.0.0.0:65432`, sehingga server mendengarkan pada semua antarmuka IPv4.
2. Receiver membuat socket TCP, mengaktifkan `SO_REUSEADDR`, lalu menjalankan `bind()`, `listen(1)`, dan `accept()`.
3. Setelah sender tersambung, receiver menjalankan `receive_handler()` pada thread daemon. Thread ini memanggil `recv(4096)`, mendekripsi data, lalu menampilkan ciphertext dalam heksadesimal dan plaintext UTF-8.
4. Thread utama tetap menerima input balasan. Receiver mengenkripsi balasan dan mengirim ciphertext dengan `sendall()`.

### Sender

1. `main()` membaca alamat receiver dan port dari argumen. Jika alamat tidak diberikan, program meminta IP dan menggunakan `127.0.0.1` sebagai nilai bawaan; port bawaan adalah `65432`.
2. Sender membuka koneksi TCP dengan `connect()`.
3. Thread daemon menjalankan `receive_handler()` untuk menerima dan mendekripsi balasan secara bersamaan dengan input pengiriman.
4. Untuk setiap pesan nonkosong, sender mengubah teks menjadi UTF-8, mengenkripsinya, dan mengirimkan ciphertext melalui `sendall()`.
5. Ketik `exit` untuk menghentikan loop input. `finally` menutup socket client.

## Metode Enkripsi dan Dekripsi

### Kunci dan jadwal subkunci

Konstruktor `ManualDES` menormalkan kunci menjadi tepat 8 byte: kunci yang lebih pendek ditambah byte nol, sedangkan kunci yang lebih panjang dipotong. Sesudah itu `_generate_subkeys()` menjalankan PC-1, membagi hasil 56 bit menjadi dua bagian 28 bit, melakukan rotasi kiri sesuai `SHIFT_SCHEDULE`, lalu menggunakan PC-2 untuk menghasilkan 16 subkunci, masing-masing 48 bit.

Pada kedua program node, nilai yang tertulis adalah `PRE_SHARED_KEY = b"KunciDES67"` (10 byte). Karena konstruktor memotongnya menjadi 8 byte, kunci efektifnya adalah `b"KunciDES"`. Ini sesuai nilai kunci 8 byte yang disebut dalam README. Kedua node harus memakai nilai efektif yang sama.

### Proses satu blok

`_process_block()` memproses satu blok berukuran 8 byte (64 bit):

1. `_bytes_to_bits()` mengubah setiap byte menjadi bit dari most-significant bit ke least-significant bit.
2. Initial Permutation (IP) mengatur ulang 64 bit, lalu membaginya menjadi bagian kiri dan kanan, masing-masing 32 bit.
3. Enam belas putaran Feistel menjalankan fungsi `_feistel_function()`: ekspansi E dari 32 menjadi 48 bit, XOR dengan subkunci, substitusi melalui delapan S-Box (masing-masing 6 bit menjadi 4 bit), kemudian permutasi P. Hasilnya di-XOR dengan bagian kiri; bagian kanan menjadi bagian kiri putaran berikutnya.
4. Setelah putaran terakhir, bagian kanan dan kiri digabung dalam urutan terbalik, lalu Final Permutation (FP) menghasilkan ciphertext 64 bit.

### Enkripsi pesan

`encrypt()` menerima byte plaintext. `_pad_pkcs7()` menambahkan padding agar panjang data merupakan kelipatan 8 byte. Padding tetap ditambahkan bila panjang plaintext sudah kelipatan 8; setiap byte padding berisi jumlah byte padding. Data dibagi menjadi blok 8 byte dan setiap blok diproses dengan 16 subkunci dalam urutan normal.

Setiap blok dienkripsi secara mandiri tanpa IV atau chaining antarblok. Dengan demikian implementasi ini berperilaku seperti mode ECB. Ciphertext yang dikirim berupa byte mentah; tampilan HEX hanya untuk log.

### Dekripsi pesan

`decrypt()` menolak panjang ciphertext yang bukan kelipatan 8 dengan mengembalikan byte kosong. Untuk setiap blok, `_process_block()` dijalankan dengan 16 subkunci dalam urutan terbalik. Setelah semua blok digabung, `_unpad_pkcs7()` membuang padding yang valid. Node kemudian mendekode hasilnya sebagai UTF-8 dengan `errors="replace"`.

## Metode Pengiriman Data dan Batas Transfer Berkas

Pengiriman memakai TCP IPv4 (`socket.SOCK_STREAM`). TCP menyediakan aliran byte yang andal dan berurutan, bukan batas pesan. `sendall()` mengirim seluruh buffer ke socket, tetapi satu kali `recv(4096)` tidak dijamin menerima tepat satu ciphertext: data dapat terpecah di beberapa `recv()` atau beberapa pengiriman dapat tergabung dalam satu `recv()`.

Kode saat ini langsung mendekripsi setiap hasil `recv()` seolah-olah itu satu pesan utuh. Karena itu, lalu lintas berulang dapat gagal atau menghasilkan plaintext yang salah jika batas baca TCP berbeda dari batas pesan. Untuk demo singkat hal ini mungkin tidak terlihat, tetapi protokol sebaiknya menambahkan framing, misalnya header panjang pesan yang dibaca sampai lengkap sebelum ciphertext diproses.

**Transfer berkas belum tersedia.** Program membaca teks dari `input()` dan menampilkan hasil dekripsi di terminal; tidak ada pemilihan berkas, pembacaan berkas, metadata nama/ukuran, penulisan hasil ke disk, atau penanda akhir transfer. Agar mendukung berkas, protokol perlu mendefinisikan header (misalnya nama dan ukuran), mengirim data dalam potongan dengan framing yang jelas, menerima hingga ukuran yang dinyatakan, lalu menyimpan hasilnya. Integritas berkas juga perlu diverifikasi dengan MAC atau hash terautentikasi. Implementasi saat ini tidak menyediakan hal-hal tersebut.

## Langkah Pengujian

### Persiapan

1. Letakkan `cipher_manual.py`, `receiver_node-v3.py`, dan `sender_node-v3.py` dalam satu folder pada kedua mesin.
2. Pastikan kedua salinan memakai implementasi DES yang sama dan kunci efektif yang sama (`b"KunciDES"`).
3. Pastikan port TCP `65432` dapat dijangkau; pada Windows/Linux, izinkan koneksi masuk melalui firewall bila diperlukan.
4. Untuk pengujian lintas OS pada topologi README, cari alamat IPv4 VM Linux yang dapat dijangkau dari Windows Host. Contoh README menggunakan `192.168.207.128`; ganti dengan alamat aktual VM.

### Menjalankan

Di VM Linux, jalankan receiver terlebih dahulu:

```bash
python3 receiver_node-v3.py 0.0.0.0 65432
```

Di Windows Host, jalankan sender dengan IP VM:

```powershell
python sender_node-v3.py 192.168.207.128 65432
```

Untuk uji pada satu komputer, jalankan receiver pada satu terminal lalu sender pada terminal lain dengan alamat loopback:

```powershell
python sender_node-v3.py 127.0.0.1 65432
```

### Skenario yang diperiksa

- Pastikan sender berhasil terhubung setelah receiver mulai mendengarkan.
- Kirim pesan pendek, pesan lebih dari 8 byte, teks Unicode, dan pesan dengan panjang kelipatan 8 byte. Receiver harus menampilkan plaintext yang sama.
- Kirim balasan dari receiver dan pastikan sender menampilkan plaintext yang sama.
- Amati ciphertext HEX: hasilnya berupa data terenkripsi dan panjangnya kelipatan 8 byte. Jangan mengharapkan nilai ciphertext yang sama untuk setiap pesan yang berbeda.
- Ketik `exit` untuk mengakhiri loop masing-masing node.
- Uji ini adalah pemeriksaan fungsional manual. Untuk membuktikan ketahanan terhadap pemecahan/penggabungan TCP, perlu pengujian framing khusus; kode sekarang belum menangani framing pesan.

### Troubleshooting

- `ConnectionRefusedError`: pastikan receiver sudah berjalan, IP/port benar, dan firewall mengizinkan koneksi.
- Tidak dapat menjangkau VM: periksa mode jaringan VM/NAT dan alamat IPv4 VM; `0.0.0.0` adalah alamat bind receiver, bukan alamat tujuan sender.
- Plaintext acak atau rusak: pastikan versi cipher dan kunci efektif sama di kedua mesin. Perbedaan versi RC4/DES juga menyebabkan hasil tidak dapat dibaca. Periksa pula kemungkinan satu pesan TCP terpecah atau beberapa pesan tergabung pada `recv()`.
- Karakter pengganti `�`: byte hasil dekripsi tidak membentuk UTF-8 yang valid, yang biasanya menandakan ciphertext/kunci/framing tidak cocok.

## Batas Keamanan

DES memiliki kunci efektif 56 bit karena delapan bit parity tidak dipakai oleh PC-1, dan algoritma ini sudah tidak layak untuk melindungi data nyata. Implementasi ini juga tidak mengautentikasi ciphertext; data yang diubah dapat didekripsi menjadi data rusak tanpa terdeteksi secara andal. Gunakan hanya untuk pembelajaran. Untuk aplikasi nyata, gunakan protokol TLS dan algoritma modern terautentikasi, bukan DES buatan sendiri.
