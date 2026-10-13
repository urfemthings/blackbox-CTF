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
