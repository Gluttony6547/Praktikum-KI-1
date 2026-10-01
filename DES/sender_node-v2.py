# sender_node-v2.py
import socket
import threading
import sys
from cipher_manual import ManualDES

# --- PENGELOLAAN KEY (PRE-SHARED KEY / PSK) ---
# DES menggunakan kunci 8 Byte (64 bit).
# Key sudah disepakati dan dikonfigurasi di kedua pihak sebelum transmisi.
# Key TIDAK DIKIRIMKAN melalui jaringan/socket.
PRE_SHARED_KEY = b"KunciDES"

def receive_handler(sock):
    """
    Thread penerima pesan balasan: Menerima ciphertext dari Receiver,
    mendekripsinya menggunakan PSK dengan algoritma DES, dan menampilkan plaintext.
    """
    while True:
        try:
            ciphertext = sock.recv(4096)
            if not ciphertext:
                print("\n[INFO] Receiver telah memutuskan koneksi.")
                break
            
            # Instansiasi DES manual dengan PSK
            cipher = ManualDES(PRE_SHARED_KEY)
            
            # Dekripsi ciphertext -> plaintext
            plaintext_bytes = cipher.decrypt(ciphertext)
            pesan_terdekripsi = plaintext_bytes.decode('utf-8', errors='replace')
            
            print("\n" + "="*50)
            print(f"[DITERIMA] Ciphertext DES (HEX) : {ciphertext.hex()}")
            print(f"[DITERIMA] Plaintext Hasil      : {pesan_terdekripsi}")
            print("="*50)
            print("[SENDER] Masukkan pesan untuk dikirim: ", end="", flush=True)
        except Exception as e:
            print(f"\n[ERROR] Terjadi kesalahan penerimaan: {e}")
            break

def main():
    # Mengambil IP Target Receiver dan Port dari argumen CLI jika tersedia
    host = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 65432

    print("="*60)
    print("   SIMULASI KOMUNIKASI ENKRIPSI DES 2 ARAH - SENDER (NODE B)")
    print("="*60)
    print(f"[ALGORITMA ] Data Encryption Standard (DES) Manual")
    print(f"[PSK CONFIG] Pre-Shared Key : {PRE_SHARED_KEY.decode()}")
    print(f"[STATUS    ] Menghubungkan ke Receiver di {host}:{port}...\n")

    client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Mencoba koneksi
    try:
        client_sock.connect((host, port))
        print("[SUCCESS] Berhasil terhubung ke Receiver!\n")
    except ConnectionRefusedError:
        print("[ERROR] Receiver belum aktif. Jalankan receiver_node-v2.py di VM/Target terlebih dahulu!")
        return

    # Jalankan thread penerima pesan balasan
    recv_thread = threading.Thread(target=receive_handler, args=(client_sock,), daemon=True)
    recv_thread.start()

    # Loop pengiriman pesan
    try:
        while True:
            pesan = input("[SENDER] Masukkan pesan untuk dikirim: ")
            if pesan.lower() == 'exit':
                print("[INFO] Menghentikan program...")
                break
            if not pesan.strip():
                continue
            
            # Enkripsi manual DES pesan
            cipher = ManualDES(PRE_SHARED_KEY)
            ciphertext = cipher.encrypt(pesan.encode('utf-8'))
            
            # Kirim ciphertext via TCP Socket
            client_sock.sendall(ciphertext)
            print(f"[TERKIRIM] Ciphertext DES (HEX) : {ciphertext.hex()}\n")

    except KeyboardInterrupt:
        print("\n[INFO] Program dihentikan pengguna.")
    finally:
        client_sock.close()

if __name__ == "__main__":
    main()
