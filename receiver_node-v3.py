# receiver_node-v3.py
import socket
import threading
import sys
from cipher_manual import ManualDES

# --- PENGELOLAAN KEY (PRE-SHARED KEY / PSK FOR DES) ---
# DES membutuhkan kunci 8 byte (64 bit).
# Key sudah disepakati dan dikonfigurasi di kedua pihak sebelum transmisi.
# Key TIDAK DIKIRIMKAN melalui jaringan/socket.
PRE_SHARED_KEY = b"KunciDES67"

def receive_handler(sock):
    """
    Thread penerima pesan: Menerima ciphertext DES secara asynchronous,
    mendekripsinya menggunakan PSK 8-byte, dan menampilkan hasil dekripsi.
    """
    while True:
        try:
            ciphertext = sock.recv(4096)
            if not ciphertext:
                print("\n[INFO] Sender telah memutuskan koneksi.")
                break
            
            # Instansiasi cipher manual DES dengan PSK
            cipher = ManualDES(PRE_SHARED_KEY)
            
            # Dekripsi ciphertext -> plaintext
            plaintext_bytes = cipher.decrypt(ciphertext)
            pesan_terdekripsi = plaintext_bytes.decode('utf-8', errors='replace')
            
            print("\n" + "="*50)
            print(f"[DITERIMA] Ciphertext DES (HEX) : {ciphertext.hex()}")
            print(f"[DITERIMA] Plaintext Hasil      : {pesan_terdekripsi}")
            print("="*50)
            print("[RECEIVER] Masukkan pesan balasan: ", end="", flush=True)
        except Exception as e:
            print(f"\n[ERROR] Terjadi kesalahan penerimaan: {e}")
            break

def main():
    # Mengambil IP Binding dan Port dari argumen CLI jika ada
    host = sys.argv[1] if len(sys.argv) > 1 else '0.0.0.0'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 65432

    print("="*60)
    print("      SIMULASI KOMUNIKASI ENKRIPSI DES 2 ARAH - RECEIVER (NODE A)")
    print("="*60)
    print(f"[PSK CONFIG] Pre-Shared Key : {PRE_SHARED_KEY.decode()}")
    print(f"[ALGORITMA]  Cipher Engine  : Manual DES (Data Encryption Standard)")
    print(f"[STATUS]     Menunggu koneksi dari Sender di {host}:{port}...")
    print("="*60 + "\n")

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_sock.bind((host, port))
        server_sock.listen(1)
        conn, addr = server_sock.accept()
        print(f"[SUCCESS] Terhubung dengan Sender dari IP/Port: {addr}\n")

        # Jalankan thread penerima pesan agar receiver bisa menerima & mengirim sekaligus
        recv_thread = threading.Thread(target=receive_handler, args=(conn,), daemon=True)
        recv_thread.start()

        # Loop pengiriman pesan balasan (Komunikasi 2 Arah)
        while True:
            pesan = input("[RECEIVER] Masukkan pesan balasan: ")
            if pesan.lower() == 'exit':
                print("[INFO] Menghentikan program...")
                break
            if not pesan.strip():
                continue
            
            # Enkripsi manual pesan balasan dengan DES
            cipher = ManualDES(PRE_SHARED_KEY)
            ciphertext = cipher.encrypt(pesan.encode('utf-8'))
            
            # Kirim ciphertext via TCP Socket
            conn.sendall(ciphertext)
            print(f"[TERKIRIM] Ciphertext DES (HEX) : {ciphertext.hex()}\n")

    except KeyboardInterrupt:
        print("\n[INFO] Program dihentikan pengguna.")
    finally:
        server_sock.close()

if __name__ == "__main__":
    main()
