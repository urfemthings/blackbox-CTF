cat << 'EOF' > README.md
# Blackbox CTF - IPI System Exploration

Catatan investigasi dan *reconnaissance* target web CTF untuk modul *Quality Control Laboratory* (PT International Paint Indonesia).

## Target Information
- **URL:** `https://ftir.arifnurdiyansyah.my.id`
- **Framework:** Laravel v10+ (PHP)
- **System Name:** IPI System (FTIR Lab QC)

## Reconnaissance & Findings
1. **Directory Enumeration (`dirsearch`):**
   - `/login` : Halaman autentikasi utama dengan proteksi CSRF Token (`_token`).
   - `/samples/export` : Endpoint ekspor data (mengarah ke *redirect* `/login`).
   - `/samples/05`, `/samples/02`, dll. : Endpoint *resource controller* untuk data sampel laboratorium.
2. **Security Behavior Analysis:**
   - **Authentication Protection:** Setiap akses rute di dalam tanpa sesi login yang valid akan dilempar ke halaman *login* (Status `302`).
   - **CSRF Defense:** Pengiriman *request* metode `POST` tanpa menyertakan token yang valid memicu respons `419 Page Expired` dari Laravel.

## Conclusion
Target menggunakan pengaman standar industri modern (Laravel Sanctum/Middleware Session & CSRF). Eksploitasi langsung dari luar tanpa akun atau *credential leak* tidak dapat menembus lapisan validasi server.
EOF

Dan aku coba brute eh ternayta tembus Target: https://ftir.arifnurdiyansyah.my.id/login | User: admin | Password: password | Reason: Laravel: Error gone=True Form gone=False Diff=39



trus nih alur kerjanya 

# FTIR Blackbox - Brute Force with CSRF Bypass

> Lab: ftir.arifnurdiyansyah.my.id | Type: Blackbox Web Pentest

### Vulnerability
Login page menggunakan CSRF token dinamis + validasi panjang password.

### How I Solved It
1.  Ambil CSRF token dulu via GET /login
2.  Pakai session yang sama buat POST brute force
3.  Deteksi sukses pakai baseline diff (response length), bukan keyword

### Tool
Custom Python script (requests + threading) - tanpa root, jalan di Termux

### Proof
[https://github.com/urfemthings/blackbox-CTF/blob/main/Screenshot_20261013_180225.jpg] 

### How to Run
python3 brute.py

### fix

selalu menggunakan recapca ,gunakan password yang kuat, aktif kan firewall Dan setting yang bener Dan gunakan time limeted
