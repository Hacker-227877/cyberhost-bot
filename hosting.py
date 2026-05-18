#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ╔══════════════════════════════════════════════════════════════════════╗
#   CyberHost BOT HOSTING PANEL v5.0 — by CyberSameer
#   Platform: Termux | VPS | Render | Railway | Koyeb | Heroku | Replit
#             Workers | Any Python 3.8+ environment
#   Features:
#     ✅ Multi-level Admin (Super Admin + Admins)
#     ✅ Premium Plans + Payment System (UPI + Screenshot)
#     ✅ Auto-install missing modules
#     ✅ Broadcast + Premium Broadcast
#     ✅ Full User/Admin Info + Bio + Profile Photo
#     ✅ Welcome Message + Auto-Reply + Referral System
#     ✅ Backup & Restore | IP/Message Logger
#     ✅ Custom Plans | Scheduled Restart/Stop
#     ✅ Health Check | Anti-Spam | Forward Detection
#     ✅ Coupon System | Warning System | Ban System
#     ✅ Multi-language File Support (UTF-8, UTF-16, Latin, etc.)
#     ✅ Perfect Error Messages in User's Language
#     ✅ Inline Stats | Revenue Stats | System Info
#     ✅ Auto-restart bots on crash
#     ✅ ALL bugs fixed (ValueError, int() crash, etc.)
# ╚══════════════════════════════════════════════════════════════════════╝

import os, re, sys, json, time, signal, threading, traceback
import subprocess, zipfile, resource, math, random, string, hashlib
from urllib import request, parse
from datetime import datetime, timedelta

PYTHON_BIN = sys.executable or "python3"
PIP_CMD    = [PYTHON_BIN, "-m", "pip"]

# ── Multi-Language Runtime Map ──
LANG_MAP = {
    ".py":   {"cmd": [PYTHON_BIN, "-u"], "name": "Python",     "emoji": "🐍"},
    ".js":   {"cmd": ["node"],           "name": "Node.js",    "emoji": "🟩"},
    ".ts":   {"cmd": ["npx", "ts-node"],"name": "TypeScript",  "emoji": "🔷"},
    ".mjs":  {"cmd": ["node"],           "name": "Node.js ESM","emoji": "🟩"},
    ".cjs":  {"cmd": ["node"],           "name": "Node.js CJS","emoji": "🟩"},
    ".go":   {"cmd": ["go", "run"],      "name": "Go",         "emoji": "🔵"},
    ".rb":   {"cmd": ["ruby"],           "name": "Ruby",       "emoji": "💎"},
    ".php":  {"cmd": ["php"],            "name": "PHP",        "emoji": "🐘"},
    ".sh":   {"cmd": ["bash"],           "name": "Shell",      "emoji": "🐚"},
    ".pl":   {"cmd": ["perl"],           "name": "Perl",       "emoji": "🔮"},
    ".java": {"cmd": ["java"],           "name": "Java",       "emoji": "☕"},
    ".lua":  {"cmd": ["lua"],            "name": "Lua",        "emoji": "🌙"},
    ".r":    {"cmd": ["Rscript"],        "name": "R",          "emoji": "📊"},
}
BOT_EXTS = set(LANG_MAP.keys())

def get_lang(fpath):
    """Return lang info dict for a file, defaults to Python."""
    ext = os.path.splitext(fpath)[1].lower()
    return LANG_MAP.get(ext, LANG_MAP[".py"])

def get_runner_cmd(fpath):
    """Return the command list to run a file."""
    return get_lang(fpath)["cmd"] + [fpath]

# ╔══════════════════════════════════════════╗
#   ★  CONFIG — Yahan apni info daalo  ★
# ╚══════════════════════════════════════════╝
HOST_TOKEN   = os.environ.get("HOST_BOT_TOKEN", "")    # ← Host bot token (set in secrets)
SUPER_ADMIN  = 8701736436                # ← Aapka Telegram ID (integer)
ADMIN_IDS    = {8701736436}              # Runtime mein add hote hain
ALLOW_ALL    = True
FREE_LIMIT_DEFAULT = 2
BOT_NAME     = "CyberHost"             # ← Aapke bot ka naam
OWNER_NAME   = "CyberSameer"           # ← Aapka naam
UPI_ID       = "yourname@upi"          # ← Aapka UPI ID
CHANNEL_LINK = "https://t.me/cybersameer_jarvis"
SUPPORT_LINK = "https://t.me/cybersameer_jarvis"
REFERRAL_BONUS_DAYS = 2

# ── Plans ──
PLANS = {3: 39, 7: 79, 15: 149, 30: 299, 90: 699, 120: 899, 180: 1299, 365: 2499}
PLAN_BOT_LIMITS = {3: 3, 7: 4, 15: 5, 30: 7, 90: 10, 120: 12, 180: 15, 365: 25}

# ── Files ──
USERS_FILE       = "users.json"
BOTS_USERS_FILE  = "bots_users.json"
BOTS_ADMIN_FILE  = "bots_admin.json"
QR_FILE          = "qr.json"
ADMINS_FILE      = "extra_admins.json"
BANNED_FILE      = "banned.json"
NOTICES_FILE     = "notices.json"
MAINTENANCE_FILE = "maintenance.json"
REFERRALS_FILE   = "referrals.json"
WELCOME_FILE     = "welcome.json"
AUTOREPLY_FILE   = "autoreply.json"
COUPON_FILE      = "coupons.json"
SCHEDULED_FILE   = "scheduled.json"
ANTISPAM_FILE    = "antispam.json"
CUSTOM_CMD_FILE  = "custom_cmds.json"
FORCE_JOIN_FILE  = "force_join.json"

# ── Default Force-Join Channels (admins can add/remove via /addfj) ──
DEFAULT_FORCE_JOINS = [
    {"id": -1003461219766, "link": "https://t.me/+2z-EBfs-FpUzMGQ9",      "name": "🔒 Group 1"},
    {"id": -1003914709003, "link": "https://t.me/cybersameer_jarvis",       "name": "🤖 CyberSameer Jarvis"},
    {"id": -1003817971024, "link": "https://t.me/CyberSameerAPIs",          "name": "📡 CyberSameer APIs"},
]

BASE_DIR       = os.path.join(os.path.dirname(os.path.abspath(__file__)), "botdata")
BOTS_USERS_DIR = os.path.join(BASE_DIR, "bots_users")
BOTS_ADMIN_DIR = os.path.join(BASE_DIR, "bots_admin")
DEPS_DIR       = os.path.join(BASE_DIR, "deps")
LOGS_DIR       = os.path.join(BASE_DIR, "logs")
BACKUP_DIR     = os.path.join(BASE_DIR, "backups")
MEDIA_DIR      = os.path.join(BASE_DIR, "media")

# ── Settings ──
LONG_POLL_TIMEOUT       = 50
SLEEP_ON_ERROR          = 0.3
START_PROBE_SECONDS     = 2
AUTO_INSTALL            = True
AUTO_INSTALL_MAX_TRIES  = 5
RESTART_ON_EXIT         = True
RESTART_BACKOFF_SECONDS = 2
MAX_RESTARTS_IN_ROW     = 30
MAX_FILE_SIZE_BYTES     = 2000 * 1024 * 1024  # 2 GB (Telegram itself limits ~2GB)
MAX_USER_LIST           = 500
MAX_ALLBOTS_LIST        = 500
ANTISPAM_LIMIT          = 5
ANTISPAM_WINDOW         = 3

TOKEN_RE      = re.compile(r'^\s*(BOT_TOKEN|TOKEN|bot_token|token|API_TOKEN|API_KEY)\s*=\s*[\'"]([^\'"]*)[\'"]', re.M|re.I)
BOT_TOKEN_FMT = re.compile(r"^\d{5,}:[A-Za-z0-9_-]{20,}$")
MNF_RE        = re.compile(r"ModuleNotFoundError:\s+No module named '([^']+)'")
NPM_MNF_RE    = re.compile(r"Cannot find module '([^']+)'")
RUBY_MNF_RE   = re.compile(r"cannot load such file -- ([^\s\n]+)")
PHP_MNF_RE    = re.compile(r"require\(\): Failed opening required '([^']+)'")

PIP_MAP = {
    "telegram":"python-telegram-bot","bs4":"beautifulsoup4","PIL":"Pillow",
    "cv2":"opencv-python","yaml":"PyYAML","Crypto":"pycryptodome","lxml":"lxml",
    "aiogram":"aiogram","pyrogram":"pyrogram","telethon":"telethon",
    "pymongo":"pymongo","mysql":"mysql-connector-python","psycopg2":"psycopg2-binary",
    "redis":"redis","sqlalchemy":"SQLAlchemy","requests":"requests","aiohttp":"aiohttp",
    "flask":"flask","fastapi":"fastapi","numpy":"numpy","pandas":"pandas",
    "dotenv":"python-dotenv","motor":"motor","httpx":"httpx","tgcrypto":"tgcrypto",
    "apscheduler":"APScheduler","celery":"celery","pydantic":"pydantic",
}

# ── Unicode Art Dividers ──
DIV  = "━" * 33
DIV2 = "┅" * 33
STAR = "✦"
DOT  = "◈"

def box(title, rows, w=30):
    """╭━━━〔 title 〕━━━╮ / ┃├ row / ╰━━━━━╯"""
    top  = f"╭━━━〔 {title} 〕━━━╮"
    body = "\n".join(f"┃├ {r}" for r in rows)
    bot  = "╰" + "━" * w + "╯"
    return f"{top}\n{body}\n{bot}"

def hbox(title, rows, w=32):
    """HTML version of box() — bold title, aligned rows."""
    top  = f"╭━━━〔 <b>{title}</b> 〕━━━╮"
    body = "\n".join(f"┃├ {r}" for r in rows)
    bot  = "╰" + "━" * w + "╯"
    return f"{top}\n{body}\n{bot}"

# ════════════════════════════════════════════
#   SAFE INT — THE ROOT FIX
#   Yeh function kabhi crash nahi karta
# ════════════════════════════════════════════
def safe_int(val, default=0):
    """Safely convert any value to int, never raises ValueError."""
    try:
        if val is None: return default
        s = str(val).strip()
        if not s: return default
        # Remove any non-numeric prefix/suffix
        return int(float(s)) if '.' in s else int(s)
    except (ValueError, TypeError, OverflowError):
        return default

def is_valid_uid(val):
    """Check if a value is a valid numeric Telegram user ID."""
    try:
        n = int(str(val).strip())
        return n > 0
    except (ValueError, TypeError):
        return False

# ════════════════════════════════════════
#   HELPERS
# ════════════════════════════════════════
def now_ts(): return int(time.time())

def fmt_time(ts):
    try: return datetime.fromtimestamp(int(ts)).strftime("%d %b %Y  %I:%M %p")
    except: return str(ts)

def fmt_size(b):
    try:
        b = int(b)
        if b < 1024: return f"{b} B"
        elif b < 1024**2: return f"{b//1024} KB"
        elif b < 1024**3: return f"{b//1024//1024} MB"
        else: return f"{b//1024//1024//1024:.1f} GB"
    except: return "N/A"

def uptime_str(secs):
    try:
        h, r = divmod(int(secs), 3600); m, s = divmod(r, 60)
        if h > 0: return f"{h}h {m}m {s}s"
        elif m > 0: return f"{m}m {s}s"
        else: return f"{s}s"
    except: return "N/A"

def ensure_dirs():
    for p in (BASE_DIR, BOTS_USERS_DIR, BOTS_ADMIN_DIR, DEPS_DIR, LOGS_DIR, BACKUP_DIR, MEDIA_DIR):
        os.makedirs(p, exist_ok=True)

def safe_name(s):
    s = "".join(c for c in (s or "").strip() if c.isalnum() or c in "-_")
    return s[:30] or "bot"

def bot_key(oid, name): return f"{safe_int(oid)}:{safe_name(name)}"
def log_path(oid, name): return os.path.join(LOGS_DIR, f"{safe_int(oid)}_{safe_name(name)}.log")

def read_tail(path, n=200):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return "\n".join(f.read().splitlines()[-n:])
    except: return ""

def load_json(path):
    if not os.path.exists(path): return {}
    try:
        with open(path, "r", encoding="utf-8") as f: d = json.load(f)
        return d if isinstance(d, dict) else {}
    except: return {}

def save_json(path, data):
    try:
        with open(path + ".tmp", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(path + ".tmp", path)
    except Exception as e:
        print(f"[SAVE_JSON ERROR] {path}: {e}")

def list_bot_files(root):
    """List all supported bot files from a directory."""
    out = []
    for base, _, files in os.walk(root):
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in BOT_EXTS:
                out.append(os.path.join(base, fn))
    return out

def list_py(root):  # kept for compatibility
    return [f for f in list_bot_files(root) if f.endswith(".py")]

def extract_token(py_path):
    """Extract Telegram bot token from any source file."""
    try:
        with open(py_path, "r", encoding="utf-8", errors="ignore") as f: src = f.read()
        # Python-style: BOT_TOKEN = "..."
        m = TOKEN_RE.search(src)
        if m:
            t = m.group(2).strip()
            if BOT_TOKEN_FMT.match(t): return t
        # Universal patterns (works for JS, TS, Go, Ruby, PHP, etc.)
        for pat in (
            r'["\']([0-9]{5,}:[A-Za-z0-9_-]{20,})["\']',
            r'(?:bot_token|token|BOT_TOKEN|TOKEN|api_key|api_token|TELEGRAM_TOKEN|TG_TOKEN)[\s:=`]+["\']?([0-9]{5,}:[A-Za-z0-9_-]{20,})["\']?',
            r'os\.environ\.get\(["\'](?:BOT_TOKEN|TOKEN)["\'],\s*["\']([0-9]{5,}:[A-Za-z0-9_-]{20,})["\']',
            r'process\.env\.(?:BOT_TOKEN|TOKEN)\s*\|\|\s*["\']([0-9]{5,}:[A-Za-z0-9_-]{20,})["\']',
        ):
            for mm in re.findall(pat, src, re.I):
                tok = mm if isinstance(mm, str) else (mm[-1] if mm else "")
                if tok and BOT_TOKEN_FMT.match(tok): return tok
        # .env style: TOKEN=123:abc
        for mm in re.findall(r'^(?:BOT_)?TOKEN\s*=\s*([0-9]{5,}:[A-Za-z0-9_-]{20,})', src, re.M|re.I):
            if BOT_TOKEN_FMT.match(mm): return mm
    except: pass
    return ""

PREFERRED_ENTRIES = {
    "main.py","bot.py","app.py","run.py","start.py","__main__.py","index.py",
    "main.js","bot.js","app.js","index.js","server.js","start.js",
    "main.ts","bot.ts","app.ts","index.ts",
    "main.go","bot.go","main.rb","bot.rb","index.php","bot.php","main.sh",
}

def choose_entry(extract_dir):
    """Find the best entry file with token from any supported language."""
    files = list_bot_files(extract_dir)
    if not files: return "", ""
    # First: file with a token
    for p in files:
        t = extract_token(p)
        if t: return p, t
    # Second: preferred filename
    for p in files:
        if os.path.basename(p).lower() in PREFERRED_ENTRIES:
            return p, extract_token(p)
    # Third: check .env file for token
    env_file = os.path.join(extract_dir, ".env")
    if os.path.exists(env_file):
        t = extract_token(env_file)
        if t and files: return files[0], t
    return files[0], extract_token(files[0])

def rm_tree(path):
    if not os.path.exists(path): return
    for base, dirs, files in os.walk(path, topdown=False):
        for f in files:
            try: os.remove(os.path.join(base, f))
            except: pass
        for d in dirs:
            try: os.rmdir(os.path.join(base, d))
            except: pass
    try: os.rmdir(path)
    except: pass

def clip(s, n=3900):
    s = s or ""
    return s if len(s) <= n else s[:n-20] + "\n...(trimmed)"

def py_ok(path):
    p = subprocess.run([PYTHON_BIN, "-m", "py_compile", path],
                       capture_output=True, text=True, timeout=10)
    return p.returncode == 0, (p.stderr or p.stdout or "")

def detect_encoding(path):
    """Detect file encoding for multi-language support."""
    encodings = ["utf-8", "utf-8-sig", "utf-16", "latin-1", "cp1252", "iso-8859-1",
                 "gbk", "big5", "shift_jis", "euc-kr", "cp1251"]
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f: f.read()
            return enc
        except (UnicodeDecodeError, LookupError): continue
    return "utf-8"

def auto_fix(path):
    """Auto-fix common Python file issues — supports all languages/encodings."""
    try:
        enc = detect_encoding(path)
        with open(path, "rb") as f: raw = f.read()
        # Remove BOM
        for bom in (b"\xef\xbb\xbf", b"\xff\xfe\x00\x00", b"\x00\x00\xfe\xff", b"\xff\xfe", b"\xfe\xff"):
            if raw.startswith(bom): raw = raw[len(bom):]; break
        src = raw.decode(enc, errors="replace")
        # Fix common Unicode issues
        replacements = {
            "\ufeff": "", "\u00a0": " ", "\u201c": '"', "\u201d": '"',
            "\u2018": "'", "\u2019": "'", "\u2014": "-", "\u2013": "-",
            "\u0009": "\t",  # preserve tabs
        }
        for k, v in replacements.items(): src = src.replace(k, v)
        # Normalize line endings
        src = src.replace("\r\n", "\n").replace("\r", "\n")
        with open(path, "w", encoding="utf-8") as f: f.write(src)
        ok, _ = py_ok(path)
        return ok
    except Exception as e:
        print(f"[AUTO_FIX] {e}")
        return False

def gen_coupon(length=8):
    return "CYBER" + "".join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_disk_usage():
    try:
        stat = os.statvfs("/")
        total = stat.f_blocks * stat.f_frsize
        free  = stat.f_bfree  * stat.f_frsize
        used  = total - free
        pct   = (used / total * 100) if total > 0 else 0
        return fmt_size(used), fmt_size(total), fmt_size(free), f"{pct:.1f}%"
    except: return "N/A", "N/A", "N/A", "N/A"

def get_system_stats():
    try:
        with open("/proc/loadavg") as f: load = f.read().split()[:3]
        load_str = " | ".join(load)
    except: load_str = "N/A"
    try:
        mem = {}
        for line in open("/proc/meminfo"):
            parts = line.split(":")
            if len(parts) == 2:
                mem[parts[0].strip()] = int(parts[1].strip().split()[0])
        mem_total = mem.get("MemTotal", 0)
        mem_free  = mem.get("MemAvailable", 0)
        mem_used  = mem_total - mem_free
        pct = (mem_used / mem_total * 100) if mem_total > 0 else 0
        mem_str = f"{fmt_size(mem_used*1024)} / {fmt_size(mem_total*1024)} ({pct:.1f}%)"
    except: mem_str = "N/A"
    return load_str, mem_str

def get_cpu_info():
    try:
        count = 0
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("processor"): count += 1
        return f"{count} cores"
    except: return "N/A"

# ════════════════════════════════════════
#   TELEGRAM API
# ════════════════════════════════════════
def tg(token, method, params=None, timeout=30):
    if params is None: params = {}
    url  = f"https://api.telegram.org/bot{token}/{method}"
    data = parse.urlencode({k: v for k, v in params.items() if v is not None}).encode("utf-8")
    req  = request.Request(url, data=data, method="POST")
    try:
        with request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8", errors="replace"))
    except Exception as e:
        return {"ok": False, "error": str(e)}

def send(cid, text, pm=None, reply_markup=None):
    p = {"chat_id": cid, "text": clip(text)}
    if pm:           p["parse_mode"] = pm
    if reply_markup: p["reply_markup"] = json.dumps(reply_markup)
    try: return tg(HOST_TOKEN, "sendMessage", p)
    except: return {"ok": False}

def sendh(cid, text, reply_markup=None):
    return send(cid, text, pm="HTML", reply_markup=reply_markup)

send_html = sendh  # alias used in process_upload

def check_force_join(uid):
    """Check all required channels. Returns list of channels user hasn't joined."""
    try:
        fj_data = load_json(FORCE_JOIN_FILE)
        channels = fj_data.get("channels", DEFAULT_FORCE_JOINS)
    except: channels = DEFAULT_FORCE_JOINS
    not_joined = []
    for ch in channels:
        try:
            r = tg(HOST_TOKEN, "getChatMember", {"chat_id": ch["id"], "user_id": uid})
            if r.get("ok"):
                status = r.get("result", {}).get("status", "left")
                if status in ("member", "administrator", "creator", "restricted"):
                    continue
            not_joined.append(ch)
        except:
            not_joined.append(ch)
    return not_joined

def answer_callback(query_id, text="", alert=False):
    try: tg(HOST_TOKEN, "answerCallbackQuery",
             {"callback_query_id": query_id, "text": text[:200], "show_alert": alert})
    except: pass

def mk_inline_kb(rows):
    """rows = list of lists of (text, callback_data) tuples"""
    return {"inline_keyboard": [[{"text": t, "callback_data": d} for t, d in row] for row in rows]}

def mk_url_kb(rows):
    """rows = list of lists of (text, url) tuples"""
    return {"inline_keyboard": [[{"text": t, "url": u} for t, u in row] for row in rows]}

def mk_reply_kb(rows, resize=True, one_time=False):
    """rows = list of lists of button text strings"""
    return {
        "keyboard": [[{"text": t} for t in row] for row in rows],
        "resize_keyboard": resize,
        "one_time_keyboard": one_time,
    }

def remove_kb():
    return {"remove_keyboard": True}

def send_photo(cid, fid, cap=""):
    try: return tg(HOST_TOKEN, "sendPhoto", {"chat_id": cid, "photo": fid, "caption": clip(cap, 1000)})
    except: return {"ok": False}

def send_doc(cid, fid, cap=""):
    try: return tg(HOST_TOKEN, "sendDocument", {"chat_id": cid, "document": fid, "caption": clip(cap, 1000)})
    except: return {"ok": False}

def send_sticker(cid, sticker_id):
    try: return tg(HOST_TOKEN, "sendSticker", {"chat_id": cid, "sticker": sticker_id})
    except: return {"ok": False}

def del_webhook():
    try: tg(HOST_TOKEN, "deleteWebhook", {"drop_pending_updates": "true"})
    except: pass

def del_webhook_tok(tok):
    try: tg(tok, "deleteWebhook", {"drop_pending_updates": "true"})
    except: pass

def get_fpath(fid):
    if not fid: return None
    r = tg(HOST_TOKEN, "getFile", {"file_id": fid})
    return (r.get("result") or {}).get("file_path") if r.get("ok") else None

def dl_file(fpath, dest):
    url = f"https://api.telegram.org/file/bot{HOST_TOKEN}/{fpath}"
    try:
        with request.urlopen(url, timeout=120) as r: data = r.read()
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f: f.write(data)
        return True
    except: return False

def get_pfp(uid):
    try:
        r = tg(HOST_TOKEN, "getUserProfilePhotos", {"user_id": uid, "limit": 1})
        if r.get("ok"):
            photos = r.get("result", {}).get("photos", [])
            if photos: return photos[0][-1]["file_id"]
    except: pass
    return None

def get_bot_photo(bot_id_or_uname):
    """Get a bot's profile photo file_id via getChat."""
    if not bot_id_or_uname: return None
    try:
        target = f"@{bot_id_or_uname}" if not str(bot_id_or_uname).lstrip("-").isdigit() else str(bot_id_or_uname)
        r = tg(HOST_TOKEN, "getChat", {"chat_id": target})
        if r.get("ok"):
            photo = (r.get("result") or {}).get("photo", {})
            fid = photo.get("big_file_id") or photo.get("small_file_id")
            return fid
    except: pass
    return None

def send_photo_html(cid, file_id, caption=""):
    """Send photo with HTML caption."""
    try:
        return tg(HOST_TOKEN, "sendPhoto", {
            "chat_id": cid, "photo": file_id,
            "caption": clip(caption, 1024), "parse_mode": "HTML"
        })
    except: return {"ok": False}

def get_user_info_tg(uid):
    try:
        r = tg(HOST_TOKEN, "getChat", {"chat_id": uid})
        if r.get("ok"): return r.get("result", {})
    except: pass
    return {}

def notify_admins(text, photo=None):
    for aid in list(ADMIN_IDS):
        try:
            if photo:
                res = send_photo(aid, photo, text[:900])
                if not res.get("ok"): send(aid, text)
            else:
                send(aid, text)
        except: pass

def fwd_file_admins(fid, cap):
    for aid in list(ADMIN_IDS):
        try: send_doc(aid, fid, cap)
        except: pass

def fwd_photo_admins(fid, cap):
    for aid in list(ADMIN_IDS):
        try: send_photo(aid, fid, cap)
        except: pass

def pin_msg(cid, msg_id):
    try: return tg(HOST_TOKEN, "pinChatMessage", {"chat_id": cid, "message_id": msg_id})
    except: return {"ok": False}

# ════════════════════════════════════════
#   BOT RUNNER
# ════════════════════════════════════════
class BotRunner(threading.Thread):
    def __init__(self, oid, ocid, name, bot_file, work_dir, deps, notify_fn):
        super().__init__(daemon=True)
        self.oid       = safe_int(oid)
        self.ocid      = safe_int(ocid)
        self.name      = safe_name(name)
        self.bot_file  = bot_file
        self.work_dir  = work_dir
        self.deps      = deps
        self.proc      = None
        self.stop_flag = threading.Event()
        self.notify    = notify_fn
        self.started_at = now_ts()
        self.restarts  = 0
        self.announced = False
        self.bot_uname = ""
        self.bot_id    = ""
        self.total_uptime = 0
        self.error_count  = 0

    def stop(self):
        self.stop_flag.set()
        if self.proc and self.proc.poll() is None:
            try:
                os.kill(self.proc.pid, signal.SIGTERM)
                time.sleep(1.5)
                if self.proc.poll() is None:
                    os.kill(self.proc.pid, signal.SIGKILL)
            except: pass

    def pip_install(self, mod, logf):
        pkg = PIP_MAP.get(mod, mod)
        os.makedirs(self.deps, exist_ok=True)
        logf.write(f"\n[pip] Installing {pkg}...\n"); logf.flush()
        try:
            subprocess.run(
                PIP_CMD + ["install", "-q", "-t", self.deps, pkg],
                capture_output=True, text=True, timeout=120
            )
        except Exception as e:
            logf.write(f"[pip ERROR] {e}\n")

    def cpu_limit(self):
        try: resource.setrlimit(resource.RLIMIT_CPU, (7200, 7200))  # 2 hour CPU cap
        except: pass

    def run(self):
        lp   = log_path(self.oid, self.name)
        tries = 0
        while not self.stop_flag.is_set():
            tries += 1
            try:
                with open(lp, "a", encoding="utf-8", errors="ignore") as logf:
                    logf.write(f"\n{'='*45}\n[START] {self.oid}/{self.name} attempt={tries}\n{'='*45}\n")
                    logf.flush()
                    env = os.environ.copy()
                    cur = env.get("PYTHONPATH", "")
                    env["PYTHONPATH"] = self.deps + (os.pathsep + cur if cur else "")
                    # Node/npm path support
                    node_modules = os.path.join(self.work_dir, "node_modules", ".bin")
                    if os.path.isdir(node_modules):
                        env["PATH"] = node_modules + os.pathsep + env.get("PATH","")
                    env["NODE_PATH"] = self.deps + (os.pathsep + env.get("NODE_PATH","") if env.get("NODE_PATH") else "")
                    lang   = get_lang(self.bot_file)
                    cmd    = lang["cmd"] + [self.bot_file]
                    logf.write(f"[LANG] {lang['name']} {lang['emoji']} — cmd: {' '.join(cmd)}\n")
                    logf.flush()
                    self.proc = subprocess.Popen(
                        cmd, stdout=logf, stderr=logf, env=env,
                        cwd=self.work_dir, preexec_fn=self.cpu_limit
                    )
                    self.started_at = now_ts()
                    time.sleep(START_PROBE_SECONDS)

                    if self.proc.poll() is None:
                        if not self.announced:
                            self.announced = True
                            # Fetch bot's profile photo
                            dp = get_bot_photo(self.bot_uname or self.bot_id)
                            # Owner info
                            owner_info = get_user_info_tg(self.oid)
                            owner_name = (owner_info.get("first_name","") + " " + owner_info.get("last_name","")).strip() or str(self.oid)
                            owner_uname = owner_info.get("username", "")
                            status_caption = (
                                f"✅ <b>BOT STARTED SUCCESSFULLY</b>\n"
                                f"╭━━━〔 🤖 BOT STATUS 〕━━━╮\n"
                                f"┃├ 📂 File Name      : <code>{os.path.basename(self.bot_file)}</code>\n"
                                f"┃├ 🤖 Bot Name       : <b>{self.name}</b>\n"
                                f"┃├ 📛 Bot Username   : @{self.bot_uname or 'detecting...'}\n"
                                f"┃├ 🆔 Bot ID         : <code>{self.bot_id or 'N/A'}</code>\n"
                                f"┃├ 👑 Owner Name     : {owner_name}\n"
                                f"┃├ 🔰 Owner Username : @{owner_uname or 'N/A'}\n"
                                f"┃├ 🆔 Owner ID       : <code>{self.oid}</code>\n"
                                f"┃├ ⏰ Started At     : {fmt_time(self.started_at)}\n"
                                f"┃├ 🔒 Status         : 🟢 Running\n"
                                f"╰━━━━━━━━━━━━━━━━━━━━━━╯"
                            )
                            if dp:
                                res = send_photo_html(self.ocid, dp, status_caption)
                                if not res.get("ok"):
                                    send(self.ocid, status_caption, pm="HTML")
                            else:
                                send(self.ocid, status_caption, pm="HTML")
                        self.restarts = 0
                        while not self.stop_flag.is_set() and self.proc.poll() is None:
                            time.sleep(1)
                        self.total_uptime += now_ts() - self.started_at
                        if self.stop_flag.is_set(): return
                        self.restarts += 1
                        ec   = self.proc.poll()
                        tail = read_tail(lp, 60)
                        if not RESTART_ON_EXIT or self.restarts >= MAX_RESTARTS_IN_ROW:
                            self.notify(self.ocid,
                                f"⛔ BOT PERMANENTLY STOPPED\n"
                                f"╭━━━〔 💀 STOPPED 〕━━━╮\n"
                                f"┃├ 🤖 Bot Name  : {self.name}\n"
                                f"┃├ ❌ Exit Code : {ec}\n"
                                f"┃├ 🔁 Restarts  : {self.restarts}\n"
                                f"╰━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
                                f"📋 Last logs:\n<code>{clip(tail, 700)}</code>"
                            )
                            return
                        self.notify(self.ocid,
                            f"🔄 BOT RESTARTING...\n"
                            f"╭━━━〔 🔁 RESTART 〕━━━╮\n"
                            f"┃├ 🤖 Bot     : {self.name}\n"
                            f"┃├ ❌ Exit    : {ec}\n"
                            f"┃├ 🔁 Attempt : #{self.restarts}/{MAX_RESTARTS_IN_ROW}\n"
                            f"╰━━━━━━━━━━━━━━━━━━━━━━╯"
                        )
                        time.sleep(RESTART_BACKOFF_SECONDS)
                        continue

                    # Bot crashed immediately
                    if not AUTO_INSTALL or tries > AUTO_INSTALL_MAX_TRIES:
                        tail = read_tail(lp, 80)
                        self.notify(self.ocid,
                            f"❌ BOT FAILED TO START\n"
                            f"╭━━━〔 ❌ ERROR 〕━━━╮\n"
                            f"┃├ 🤖 Bot  : {self.name}\n"
                            f"┃├ 📋 Logs :\n"
                            f"╰━━━━━━━━━━━━━━━━━━━━╯\n"
                            f"<code>{clip(tail, 900)}</code>"
                        )
                        return
                    tail = read_tail(lp, 100)
                    lang = get_lang(self.bot_file)
                    ext  = os.path.splitext(self.bot_file)[1].lower()
                    installed = False
                    # Python auto-install
                    mm = MNF_RE.search(tail)
                    if mm and ext == ".py":
                        mod = mm.group(1).split(".")[0]
                        self.notify(self.ocid,
                            f"╭━━━〔 ⏳ AUTO INSTALL 〕━━━╮\n"
                            f"┃├ 🐍 Python\n"
                            f"┃├ 📦 Module : <code>{mod}</code>\n"
                            f"┃├ 🔄 Status : Installing...\n"
                            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                        )
                        self.pip_install(mod, logf)
                        installed = True
                    # Node.js auto-install
                    nm = NPM_MNF_RE.search(tail)
                    if nm and ext in (".js",".ts",".mjs",".cjs") and not nm.group(1).startswith("."):
                        pkg = nm.group(1).split("/")[0]
                        self.notify(self.ocid,
                            f"╭━━━〔 ⏳ AUTO INSTALL 〕━━━╮\n"
                            f"┃├ 🟩 Node.js\n"
                            f"┃├ 📦 Package : <code>{pkg}</code>\n"
                            f"┃├ 🔄 Status  : npm install...\n"
                            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                        )
                        try:
                            subprocess.run(["npm","install","--prefix",self.work_dir,"--silent",pkg],
                                           capture_output=True, timeout=120)
                        except Exception as ne:
                            logf.write(f"[npm ERROR] {ne}\n")
                        installed = True
                    # Ruby auto-install
                    rm = RUBY_MNF_RE.search(tail)
                    if rm and ext == ".rb":
                        gem = rm.group(1).strip()
                        self.notify(self.ocid,
                            f"╭━━━〔 ⏳ AUTO INSTALL 〕━━━╮\n"
                            f"┃├ 💎 Ruby\n"
                            f"┃├ 📦 Gem : <code>{gem}</code>\n"
                            f"┃├ 🔄 Status : gem install...\n"
                            f"╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯"
                        )
                        try:
                            subprocess.run(["gem","install","--no-document",gem],
                                           capture_output=True, timeout=120)
                        except Exception as ge:
                            logf.write(f"[gem ERROR] {ge}\n")
                        installed = True
                    if installed: continue
                    tail = read_tail(lp, 80)
                    self.notify(self.ocid,
                        f"╭━━━〔 ❌ <b>BOT CRASHED</b> 〕━━━╮\n"
                        f"┃├ {lang['emoji']} {lang['name']}\n"
                        f"┃├ 🤖 Bot  : {self.name}\n"
                        f"┃├ 📋 Log  :\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯\n"
                        f"<code>{clip(tail, 900)}</code>"
                    )
                    return
            except Exception as e:
                try:
                    with open(lp, "a") as lf: lf.write(f"\n[RUNNER ERROR] {e}\n")
                except: pass
                self.notify(self.ocid, f"❌ Runner Error:\n{str(e)[:300]}")
                return
            time.sleep(SLEEP_ON_ERROR)

# ════════════════════════════════════════
#   HOST BOT
# ════════════════════════════════════════
class HostBot:
    def __init__(self):
        self.offset      = 0
        self.runners     = {}
        self.users_db    = load_json(USERS_FILE)
        self.bots_users  = load_json(BOTS_USERS_FILE)
        self.bots_admin  = load_json(BOTS_ADMIN_FILE)
        self.qr_db       = load_json(QR_FILE)
        self.banned_db   = load_json(BANNED_FILE)
        self.notices_db  = load_json(NOTICES_FILE)
        self.maint_db    = load_json(MAINTENANCE_FILE)
        self.referrals   = load_json(REFERRALS_FILE)
        self.welcome_db  = load_json(WELCOME_FILE)
        self.autoreply   = load_json(AUTOREPLY_FILE)
        self.coupons     = load_json(COUPON_FILE)
        self.custom_cmds = load_json(CUSTOM_CMD_FILE)
        self.antispam_db = {}
        self.qr_db.setdefault("file_id", "")
        self.qr_db.setdefault("pending_admin", 0)

        # Load extra admins
        extra = load_json(ADMINS_FILE)
        for x in extra.get("admins", []):
            if is_valid_uid(x):
                ADMIN_IDS.add(safe_int(x))

        self.start_time  = now_ts()
        self.user_busy   = set()
        self.lock        = threading.Lock()
        self._cleanup_db()
        self.msg_count   = 0
        self.upload_count = 0
        self.cmd_count   = 0

        # Background threads
        threading.Thread(target=self._health_check_loop, daemon=True).start()
        threading.Thread(target=self._scheduler_loop,    daemon=True).start()
        threading.Thread(target=self._plan_expiry_loop,  daemon=True).start()

    # ── Anti-Spam ──
    def is_spam(self, uid):
        now = now_ts()
        uid = str(safe_int(uid))
        if uid not in self.antispam_db: self.antispam_db[uid] = []
        self.antispam_db[uid] = [t for t in self.antispam_db[uid] if now - t < ANTISPAM_WINDOW]
        self.antispam_db[uid].append(now)
        return len(self.antispam_db[uid]) > ANTISPAM_LIMIT

    # ── Health Check ──
    def _health_check_loop(self):
        while True:
            time.sleep(300)
            try:
                dead = [kk for kk, r in list(self.runners.items())
                        if r.proc and r.proc.poll() is not None]
                if dead:
                    rows = [f"💀 Crashed : {len(dead)} bot(s)"] + [f"🔴 {k}" for k in dead[:10]]
                    notify_admins(box("⚠️ HEALTH CHECK ALERT", rows))
            except: pass

    # ── Plan Expiry Notifier ──
    def _plan_expiry_loop(self):
        while True:
            time.sleep(3600)
            try:
                for uid_str, u in list(self.users_db.items()):
                    if not is_valid_uid(uid_str): continue
                    uid = safe_int(uid_str)
                    days = self.days_left(uid)
                    if days in (3, 1):
                        send(uid, box("⚠️ PLAN EXPIRY ALERT", [
                            f"📅 Plan khatam hoga  : {days} din mein!",
                            f"💎 Renew karo        : /buy",
                            f"🎟️ Coupon use karo   : /redeem <code>",
                        ]))
            except: pass

    # ── Scheduler ──
    def _scheduler_loop(self):
        while True:
            time.sleep(60)
            try:
                sched   = load_json(SCHEDULED_FILE)
                now     = now_ts()
                changed = False
                for task_id, task in list(sched.items()):
                    if task.get("run_at", 0) <= now and not task.get("done"):
                        action = task.get("action", "")
                        uid    = safe_int(task.get("uid", 0))
                        name   = task.get("name", "")
                        if action == "restart" and uid and name:
                            self.restart_bot(uid, uid, name)
                            send(uid, f"⏰ SCHEDULED RESTART\n🤖 {name} restart ho gaya!")
                        elif action == "stop" and uid and name:
                            self.stop_bot(uid, name, delete=False)
                            send(uid, f"⏰ SCHEDULED STOP\n🤖 {name} band ho gaya!")
                        task["done"] = True
                        changed = True
                if changed: save_json(SCHEDULED_FILE, sched)
            except: pass

    # ── Permission ──
    def is_super(self, uid):    return safe_int(uid) == SUPER_ADMIN
    def is_admin(self, uid):    return safe_int(uid) in ADMIN_IDS
    def is_banned(self, uid):   return str(safe_int(uid)) in self.banned_db
    def is_maintenance(self):   return bool(self.maint_db.get("on"))
    def allowed(self, uid):
        if self.is_admin(uid):  return True
        if self.is_banned(uid): return False
        if self.is_maintenance(): return False
        return ALLOW_ALL

    def _save_admins(self):
        save_json(ADMINS_FILE, {"admins": [str(x) for x in ADMIN_IDS if x != SUPER_ADMIN]})

    # ── User DB ──
    def _get_u(self, uid):
        return self.users_db.get(str(safe_int(uid)), {})

    def _save_u(self, uid, u):
        self.users_db[str(safe_int(uid))] = u
        save_json(USERS_FILE, self.users_db)

    def register(self, u, ref_id=None):
        uid = safe_int(u.get("id", 0))
        if not uid: return
        cur    = self._get_u(uid) or {}
        is_new = not cur.get("first_seen")
        cur.update({
            "user_id": uid,
            "username":  u.get("username", ""),
            "first_name": u.get("first_name", ""),
            "last_name":  u.get("last_name", ""),
            "last_seen":  now_ts(),
            "language_code": u.get("language_code", "en"),
        })
        cur.setdefault("first_seen",     now_ts())
        cur.setdefault("uploads",        [])
        cur.setdefault("pay_requests",   [])
        cur.setdefault("pending_token",  {})
        cur.setdefault("total_uploads",  0)
        cur.setdefault("notes",          "")
        cur.setdefault("referred_by",    0)
        cur.setdefault("referral_count", 0)
        cur.setdefault("total_messages", 0)
        cur.setdefault("warning_count",  0)
        cur["total_messages"] = cur.get("total_messages", 0) + 1
        self._save_u(uid, cur)

        if is_new:
            if ref_id:
                try:
                    ref_id = safe_int(ref_id)
                    if ref_id and ref_id != uid and is_valid_uid(str(ref_id)):
                        ref_u = self._get_u(ref_id)
                        if ref_u:
                            ref_u["referral_count"] = ref_u.get("referral_count", 0) + 1
                            exp = safe_int(ref_u.get("premium_expires", now_ts()))
                            if exp < now_ts(): exp = now_ts()
                            ref_u["premium_expires"] = exp + (REFERRAL_BONUS_DAYS * 86400)
                            ref_u.setdefault("premium_days", REFERRAL_BONUS_DAYS)
                            self._save_u(ref_id, ref_u)
                            cur["referred_by"] = ref_id
                            self._save_u(uid, cur)
                            send(ref_id,
                                box("🎉 REFERRAL BONUS!", [
                                    f"✅ Naya user aaya aapki referral se!",
                                    f"👤 Name   : {u.get('first_name','')} @{u.get('username','-')}",
                                    f"🎁 Bonus  : +{REFERRAL_BONUS_DAYS} days FREE!",
                                ])
                            )
                except: pass

            if not self.is_admin(uid):
                total = len([x for x in self.users_db if is_valid_uid(x) and safe_int(x) not in ADMIN_IDS])
                pfp      = get_pfp(uid)
                tg_info  = get_user_info_tg(uid)
                notify_admins(
                    box("👤 NEW USER JOINED", [
                        f"🆔 ID       : {uid}",
                        f"👤 Name     : {u.get('first_name','')} {u.get('last_name','')}",
                        f"📛 Username : @{u.get('username','-')}",
                        f"🌐 Language : {u.get('language_code','N/A')}",
                        f"📝 Bio      : {tg_info.get('bio','—')}",
                        f"🔗 Referred : {'✅ by ' + str(ref_id) if ref_id else '❌ No'}",
                        f"⏰ Time     : {fmt_time(now_ts())}",
                        f"👥 Total    : {total} users",
                    ]),
                    pfp
                )
                wm = self.welcome_db.get("message", "")
                if wm:
                    wm = (wm.replace("{name}", u.get("first_name", "User"))
                           .replace("{username}", "@" + u.get("username", "N/A"))
                           .replace("{id}", str(uid))
                           .replace("{bots}", str(self.effective_limit(uid)))
                           .replace("{plan}", "Free" if not self.is_premium(uid) else "Premium"))
                    send(uid, wm)

    # ── Warning System ──
    def warn_user(self, admin_id, uid, reason=""):
        uid = safe_int(uid)
        u   = self._get_u(uid) or {}
        u["warning_count"] = u.get("warning_count", 0) + 1
        u.setdefault("warnings", []).append({
            "reason": reason or "N/A",
            "by": safe_int(admin_id),
            "at": now_ts()
        })
        self._save_u(uid, u)
        wc = u["warning_count"]
        send(uid, box(f"⚠️ WARNING #{wc}/3", [
            f"📝 Reason  : {reason or 'N/A'}",
            f"🚫 3 warnings = permanent ban!",
            f"💬 Support : {SUPPORT_LINK}",
        ]))
        if wc >= 3:
            return self.ban_user(admin_id, uid, f"3 warnings — last: {reason or 'N/A'}")
        return box(f"✅ WARNING #{wc} DIYA", [
            f"🆔 User    : {uid}",
            f"📝 Reason  : {reason or 'N/A'}",
            f"⚠️ Baki    : {3-wc} warnings before ban",
        ])

    def unwarn_user(self, uid):
        uid = safe_int(uid)
        u   = self._get_u(uid) or {}
        if u.get("warning_count", 0) <= 0: return "⚠️ Koi warning nahi hai."
        u["warning_count"] = max(0, u.get("warning_count", 0) - 1)
        if u.get("warnings"): u["warnings"].pop()
        self._save_u(uid, u)
        return f"✅ {uid} ki ek warning hatayi.\n⚠️ Remaining: {u['warning_count']}/3"

    # ── Ban System ──
    def ban_user(self, admin_id, uid, reason=""):
        uid = safe_int(uid)
        if uid == SUPER_ADMIN: return "❌ Super Admin ko ban nahi kar sakte."
        if self.is_admin(uid): return "❌ Admin ko ban nahi kar sakte."
        u = self._get_u(uid) or {}
        self.banned_db[str(uid)] = {
            "banned_by": safe_int(admin_id),
            "reason":    reason or "N/A",
            "banned_at": now_ts(),
            "name":      u.get("first_name", ""),
            "username":  u.get("username", ""),
        }
        save_json(BANNED_FILE, self.banned_db)
        # Stop all bots of banned user
        for kk in list(self.runners.keys()):
            info = self.bots_users.get(kk, {})
            if safe_int(info.get("owner_id", 0)) == uid:
                self.runners[kk].stop()
                self.runners.pop(kk, None)
        send(uid, box("🚫 ACCOUNT BANNED", [
            f"Aapko is service se ban kar diya gaya.",
            f"📝 Reason  : {reason or 'N/A'}",
            f"💬 Appeal  : {SUPPORT_LINK}",
        ]))
        return box("✅ USER BANNED", [
            f"🆔 ID      : {uid}",
            f"👤 Name    : {u.get('first_name', '-')}",
            f"📛 User    : @{u.get('username', '-')}",
            f"📝 Reason  : {reason or 'N/A'}",
            f"⏰ Time    : {fmt_time(now_ts())}",
        ])

    def unban_user(self, admin_id, uid):
        uid = safe_int(uid)
        if str(uid) not in self.banned_db: return "⚠️ Yeh user banned nahi hai."
        del self.banned_db[str(uid)]
        save_json(BANNED_FILE, self.banned_db)
        send(uid, f"✅ Aapka ban hata diya gaya!\nAb dobara use kar sakte ho.\n{CHANNEL_LINK}")
        return f"✅ {uid} ka ban hata diya."

    def banned_list_text(self):
        if not self.banned_db: return "✅ Koi banned user nahi hai."
        lines = [f"🚫 BANNED USERS ({len(self.banned_db)})", DIV, ""]
        for uid_str, info in self.banned_db.items():
            lines.append(
                f"🆔 {uid_str} | {info.get('name','-')} @{info.get('username','-')}\n"
                f"   📝 {info.get('reason','N/A')}\n"
                f"   ⏰ {fmt_time(info.get('banned_at',0))}\n"
                f"   ✅ /unban {uid_str}\n"
            )
        return "\n".join(lines)

    # ── Notice & Welcome ──
    def set_notice(self, admin_id, text):
        self.notices_db.update({"notice": text, "set_by": safe_int(admin_id), "set_at": now_ts()})
        save_json(NOTICES_FILE, self.notices_db)
        return "✅ Notice set! Users ko /start pe dikhega."

    def clear_notice(self):
        self.notices_db["notice"] = ""
        save_json(NOTICES_FILE, self.notices_db)
        return "✅ Notice hata diya."

    def get_notice(self): return self.notices_db.get("notice", "")

    def set_welcome(self, text):
        self.welcome_db["message"] = text
        save_json(WELCOME_FILE, self.welcome_db)
        return (
            "✅ Welcome message set!\n\n"
            "📌 Available variables:\n"
            "  {name}     — User ka naam\n"
            "  {username} — @username\n"
            "  {id}       — User ID\n"
            "  {bots}     — Bot limit\n"
            "  {plan}     — Free/Premium"
        )

    def clear_welcome(self):
        self.welcome_db["message"] = ""
        save_json(WELCOME_FILE, self.welcome_db)
        return "✅ Welcome message hata diya."

    # ── Auto Reply ──
    def set_autoreply(self, keyword, reply):
        self.autoreply[keyword.lower()] = reply
        save_json(AUTOREPLY_FILE, self.autoreply)
        return f"✅ Auto-reply set!\n🔑 Keyword: '{keyword}'\n💬 Reply: {reply[:50]}"

    def del_autoreply(self, keyword):
        if keyword.lower() in self.autoreply:
            del self.autoreply[keyword.lower()]
            save_json(AUTOREPLY_FILE, self.autoreply)
            return f"✅ Auto-reply deleted: '{keyword}'"
        return f"❌ Keyword '{keyword}' nahi mila."

    def list_autoreplies(self):
        if not self.autoreply: return "📭 Koi auto-reply nahi hai."
        lines = [f"🤖 AUTO-REPLIES ({len(self.autoreply)})", DIV]
        for i, (k, v) in enumerate(list(self.autoreply.items())[:25], 1):
            lines.append(f"{i}) 🔑 {k}\n    💬 {v[:60]}")
        return "\n".join(lines)

    def check_autoreply(self, text):
        text_lower = text.lower()
        for keyword, reply in self.autoreply.items():
            if keyword in text_lower: return reply
        return None

    # ── Maintenance ──
    def set_maintenance(self, admin_id, on_off):
        self.maint_db.update({"on": on_off, "by": safe_int(admin_id), "at": now_ts()})
        save_json(MAINTENANCE_FILE, self.maint_db)
        status = "🔴 ON" if on_off else "🟢 OFF"
        if on_off: notify_admins(f"🔧 MAINTENANCE MODE ON\n⏰ {fmt_time(now_ts())}")
        return (
            f"✅ MAINTENANCE MODE: {status}\n{DIV}\n"
            f"{'🔴 Users bot use nahi kar sakte.' if on_off else '🟢 Users phir se access kar sakte hain.'}"
        )

    # ── Coupon System ──
    def create_coupon(self, admin_id, days, limit=1, code=None):
        code = (code or gen_coupon()).upper().strip()
        self.coupons[code] = {
            "days": safe_int(days), "limit": safe_int(limit), "used": 0,
            "created_by": safe_int(admin_id), "created_at": now_ts(), "users": []
        }
        save_json(COUPON_FILE, self.coupons)
        return (
            f"🎟️ COUPON CREATED\n{DIV}\n"
            f"🔑 Code  : {code}\n"
            f"💎 Days  : {days}\n"
            f"🔢 Limit : {limit} use(s)\n"
            f"{DIV}\n"
            f"📲 User /redeem {code} se use kar sakta hai"
        )

    def redeem_coupon(self, uid, code):
        uid = safe_int(uid)
        code = (code or "").upper().strip()
        if code not in self.coupons: return "❌ Invalid coupon code."
        c = self.coupons[code]
        if uid in c.get("users", []):  return "❌ Aap yeh coupon pehle use kar chuke hain."
        if c.get("used", 0) >= c.get("limit", 1): return "❌ Coupon limit khatam ho gayi."
        days = safe_int(c.get("days", 0))
        self.set_plan(uid, days)
        c["used"] = c.get("used", 0) + 1
        c.setdefault("users", []).append(uid)
        save_json(COUPON_FILE, self.coupons)
        return (
            f"🎉 COUPON REDEEMED!\n{DIV}\n"
            f"🔑 Code    : {code}\n"
            f"💎 Days    : {days} Days Premium\n"
            f"🤖 Bot Slots: {PLAN_BOT_LIMITS.get(days, FREE_LIMIT_DEFAULT)}\n"
            f"📅 Expires  : {self.premium_exp(uid)}\n"
            f"📆 Days Left: {self.days_left(uid)}\n{DIV}"
        )

    def del_coupon(self, code):
        code = (code or "").upper()
        if code not in self.coupons: return f"❌ Coupon '{code}' nahi mila."
        del self.coupons[code]
        save_json(COUPON_FILE, self.coupons)
        return f"✅ Coupon {code} delete kiya."

    def list_coupons(self):
        if not self.coupons: return "📭 Koi coupon nahi."
        lines = [f"🎟️ ALL COUPONS ({len(self.coupons)})", DIV]
        for i, (code, c) in enumerate(self.coupons.items(), 1):
            status = "✅ Active" if c.get("used", 0) < c.get("limit", 1) else "❌ Expired"
            lines.append(
                f"{i}) 🔑 {code} | {status}\n"
                f"    💎 {c['days']} days | 🔢 {c['used']}/{c['limit']} used"
            )
        return "\n".join(lines)

    # ── Custom Commands ──
    def set_custom_cmd(self, cmd, reply, admin_id):
        cmd = cmd.lower().lstrip("/")
        self.custom_cmds[cmd] = {"reply": reply, "by": safe_int(admin_id), "at": now_ts()}
        save_json(CUSTOM_CMD_FILE, self.custom_cmds)
        return f"✅ Custom command /{cmd} set!\n💬 Reply: {reply[:50]}"

    def del_custom_cmd(self, cmd):
        cmd = cmd.lower().lstrip("/")
        if cmd in self.custom_cmds:
            del self.custom_cmds[cmd]
            save_json(CUSTOM_CMD_FILE, self.custom_cmds)
            return f"✅ /{cmd} deleted."
        return f"❌ Command '/{cmd}' nahi mila."

    def list_custom_cmds(self):
        if not self.custom_cmds: return "📭 Koi custom command nahi."
        lines = [f"⚡ CUSTOM COMMANDS ({len(self.custom_cmds)})", DIV]
        for i, (cmd, info) in enumerate(self.custom_cmds.items(), 1):
            lines.append(f"{i}) /{cmd}\n    💬 {info['reply'][:50]}")
        return "\n".join(lines)

    # ── Admin Management ──
    def add_admin(self, caller, target):
        if not self.is_super(caller): return "❌ Sirf Super Admin yeh kar sakta hai."
        target = safe_int(target)
        if not target: return "❌ Invalid user ID."
        if target in ADMIN_IDS: return f"⚠️ {target} already admin hai."
        ADMIN_IDS.add(target)
        self._save_admins()
        u      = self._get_u(target)
        tg_info = get_user_info_tg(target)
        pfp    = get_pfp(target)
        notify_admins(
            f"🛡️ NEW ADMIN ADDED\n{DIV}\n"
            f"🆔 ID     : {target}\n"
            f"👤 Name   : {u.get('first_name','')} {u.get('last_name','')}\n"
            f"📛 @{u.get('username','-')}\n"
            f"📝 Bio    : {tg_info.get('bio','—')}\n"
            f"👑 By     : Super Admin\n"
            f"⏰ {fmt_time(now_ts())}", pfp
        )
        send(target,
            f"🎉 ADMIN PROMOTION!\n{DIV}\n"
            f"Aapko Admin bana diya gaya hai!\n"
            f"👑 By   : Super Admin\n"
            f"⏰ Time : {fmt_time(now_ts())}\n"
            f"{DIV}\n/help se commands dekho."
        )
        return (
            f"✅ ADMIN ADDED\n{DIV}\n"
            f"🆔 ID      : {target}\n"
            f"👤 Name    : {u.get('first_name','')} {u.get('last_name','')}\n"
            f"📛 @{u.get('username','-')}\n"
            f"⏰ Time    : {fmt_time(now_ts())}\n{DIV}"
        )

    def remove_admin(self, caller, target):
        if not self.is_super(caller): return "❌ Sirf Super Admin yeh kar sakta hai."
        target = safe_int(target)
        if target == SUPER_ADMIN: return "❌ Super Admin ko remove nahi kar sakte."
        if target not in ADMIN_IDS: return f"⚠️ {target} admin nahi hai."
        ADMIN_IDS.discard(target)
        self._save_admins()
        send(target, f"⚠️ Aapka Admin access hata diya gaya.\n⏰ {fmt_time(now_ts())}")
        return f"✅ {target} ko Admin se remove kar diya."

    def admin_list(self):
        lines = [f"👑 ADMIN LIST ({len(ADMIN_IDS)})", DIV, ""]
        for i, uid in enumerate(sorted(ADMIN_IDS), 1):
            tag = " ⭐ SUPER ADMIN" if uid == SUPER_ADMIN else " 🛡️ Admin"
            u   = self._get_u(uid)
            lines.append(
                f"{i}) {u.get('first_name','?')} | @{u.get('username','-')} | `{uid}`{tag}\n"
                f"    🤖 Bots: {self.bot_count(uid)} | 📅 {fmt_time(u.get('last_seen',0))}"
            )
        return "\n".join(lines)

    # ── Full User Info ──
    def full_userinfo(self, uid):
        uid = safe_int(uid)
        if not is_valid_uid(uid): return "❌ Invalid user ID.", None
        u = self.users_db.get(str(uid))
        if not u: return "❌ User database mein nahi mila.", None
        tg_info = get_user_info_tg(uid)
        pfp     = get_pfp(uid)
        bots    = []
        for kk, info in {**self.bots_users, **self.bots_admin}.items():
            if safe_int(info.get("owner_id", 0)) == uid:
                running = kk in self.runners and self.runners[kk].proc and self.runners[kk].proc.poll() is None
                ut = uptime_str(now_ts() - self.runners[kk].started_at) if running else "—"
                bots.append(f"{'🟢' if running else '🔴'} {info.get('name','')} | @{info.get('bot_username','-')} | ⏱ {ut}")
        pay_reqs    = u.get("pay_requests", [])
        total_spent = sum(safe_int(r.get("price", 0)) for r in pay_reqs if r.get("status") == "APPROVED")
        result = (
            f"🔍 FULL USER INFO\n{DIV}\n"
            f"🆔 ID          : {uid}\n"
            f"👤 Name        : {u.get('first_name','')} {u.get('last_name','')}\n"
            f"📛 Username    : @{u.get('username','-')}\n"
            f"🌐 Language    : {u.get('language_code','N/A')}\n"
            f"📝 TG Bio      : {tg_info.get('bio','—')}\n"
            f"🔗 Profile     : tg://user?id={uid}\n"
            f"{DIV2}\n"
            f"💎 Premium     : {'✅ Yes' if self.is_premium(uid) else '❌ No'}\n"
            f"📅 Plan Exp    : {self.premium_exp(uid)}\n"
            f"📆 Days Left   : {self.days_left(uid)} days\n"
            f"🤖 Bot Limit   : {self.effective_limit(uid)}\n"
            f"🔢 Active Bots : {self.bot_count(uid)}\n"
            f"📤 Total Uploads: {u.get('total_uploads',0)}\n"
            f"💬 Msgs Sent   : {u.get('total_messages',0)}\n"
            f"{DIV2}\n"
            f"⚠️ Warnings    : {u.get('warning_count',0)}/3\n"
            f"🚫 Banned      : {'Yes ❌' if self.is_banned(uid) else 'No ✅'}\n"
            f"🔗 Referred By : {u.get('referred_by','None')}\n"
            f"👥 Referrals   : {u.get('referral_count',0)} users\n"
            f"💰 Total Spent : ₹{total_spent}\n"
            f"📝 Notes       : {u.get('notes','—')}\n"
            f"{DIV2}\n"
            f"📆 Joined      : {fmt_time(u.get('first_seen',0))}\n"
            f"🕐 Last Seen   : {fmt_time(u.get('last_seen',0))}\n"
            f"{DIV}\n"
            f"🤖 BOTS ({len(bots)}):\n"
        )
        for b in bots[:10]: result += f"  {b}\n"
        if not bots: result += "  Koi bot nahi\n"
        result += f"\n{DIV}\n"
        result += f"💳 PAYMENT HISTORY ({len(pay_reqs)}):\n"
        for r in pay_reqs[-5:]:
            icon = {"APPROVED":"✅","REJECTED":"❌","PAID":"💰","PENDING":"⏳"}.get(r.get("status",""), "❓")
            result += f"  {icon} {r.get('days','?')}d ₹{r.get('price','?')} | {r.get('status','?')} | {fmt_time(r.get('created_at',0))}\n"
        return result, pfp

    # ── User Note ──
    def set_note(self, admin_id, uid, note):
        u = self._get_u(uid) or {}
        u.update({"notes": note, "note_by": safe_int(admin_id), "note_at": now_ts()})
        self._save_u(uid, u)
        return f"✅ Note saved for {uid}:\n📝 {note}"

    # ── QR ──
    def get_qr(self): return self.qr_db.get("file_id", "")
    def set_qr_pending(self, aid):
        self.qr_db["pending_admin"] = safe_int(aid)
        save_json(QR_FILE, self.qr_db)
        send(aid, "✅ QR mode active!\n📸 Ab QR photo bhejo.")
    def is_qr_pending(self, aid): return safe_int(self.qr_db.get("pending_admin", 0)) == safe_int(aid)
    def set_qr(self, fid, aid):
        self.qr_db.update({"file_id": fid, "set_by": safe_int(aid), "set_at": now_ts(), "pending_admin": 0})
        save_json(QR_FILE, self.qr_db)
        send(aid, "✅ QR Payment image save ho gaya!")

    def credit_ended(self, cid, uid):
        qr = self.get_qr()
        msg = (
            f"🚫 BOT LIMIT REACHED!\n{DIV}\n"
            f"Aapka free limit khatam ho gaya.\n"
            f"🤖 Current: {self.bot_count(uid)}/{self.effective_limit(uid)} bots\n\n"
            f"💎 UPGRADE PLANS:\n{DIV2}\n"
        )
        for d in sorted(PLANS):
            star = "🌟" if d >= 180 else ("⭐" if d >= 30 else "🔹")
            msg += f"  {star} {d:>3} Days — ₹{PLANS[d]:<6} | 🤖 {PLAN_BOT_LIMITS[d]} bots\n"
        msg += f"\n{DIV}\n💳 /plan — Plan list\n/buy <days> — Plan lo\n🎟️ /redeem <code> — Coupon use karo"
        if qr: send_photo(cid, qr, msg)
        else:   send(cid, msg)

    # ── Premium ──
    def is_premium(self, uid):
        return safe_int(self._get_u(uid).get("premium_expires", 0)) > now_ts()

    def premium_exp(self, uid):
        exp = safe_int(self._get_u(uid).get("premium_expires", 0))
        return fmt_time(exp) if exp > now_ts() else "Active nahi"

    def effective_limit(self, uid):
        uid = safe_int(uid)
        if self.is_admin(uid): return 10**9
        u  = self._get_u(uid)
        le = safe_int(u.get("limit_expires", 0))
        tl = u.get("limit_override")
        if tl is not None and le > now_ts(): return max(0, safe_int(tl))
        if self.is_premium(uid):
            days = safe_int(u.get("premium_days", 0))
            return PLAN_BOT_LIMITS.get(days, FREE_LIMIT_DEFAULT)
        return FREE_LIMIT_DEFAULT

    def days_left(self, uid):
        exp  = safe_int(self._get_u(uid).get("premium_expires", 0))
        secs = exp - now_ts()
        if secs <= 0: return 0
        return math.ceil(secs / 86400)

    def extend_plan(self, uid, extra_days):
        uid = safe_int(uid)
        u   = self._get_u(uid) or {}
        exp = safe_int(u.get("premium_expires", now_ts()))
        if exp < now_ts(): exp = now_ts()
        exp += extra_days * 86400
        u["premium_expires"] = exp
        self._save_u(uid, u)
        return (
            f"✅ PLAN EXTENDED\n{DIV}\n"
            f"🆔 User   : {uid}\n"
            f"➕ Added  : {extra_days} days\n"
            f"📅 New Exp: {fmt_time(exp)}\n{DIV}"
        )

    # ── Payment ──
    def create_pay_req(self, uid, days):
        uid  = safe_int(uid)
        days = safe_int(days)
        if days not in PLANS: return "", f"❌ Invalid plan.\nValid: {sorted(PLANS.keys())}\n/plan se dekho."
        req_id = f"REQ{uid}{now_ts()}"
        u = self._get_u(uid) or {}
        u.setdefault("pay_requests", []).append({
            "req_id": req_id, "days": days, "price": PLANS[days],
            "status": "PENDING", "created_at": now_ts(),
            "txn_id": "", "paid_at": 0, "approved_at": 0,
            "approved_by": 0, "reason": ""
        })
        self._save_u(uid, u)
        return req_id, ""

    def mark_paid(self, uid, req_id, txn):
        uid = safe_int(uid)
        u   = self._get_u(uid)
        for r in (u.get("pay_requests") or []):
            if r.get("req_id") == req_id:
                r.update({"status": "PAID", "txn_id": (txn or "").strip()[:90], "paid_at": now_ts()})
                self._save_u(uid, u)
                return (
                    f"✅ PAYMENT SUBMITTED!\n{DIV}\n"
                    f"🧾 Request ID : {req_id}\n"
                    f"💳 Txn ID     : {txn}\n"
                    f"{DIV}\n"
                    f"📸 Screenshot bhi bhejo:\n"
                    f"/payss {req_id} [screenshot attach karke]"
                )
        return "❌ Request nahi mili. ID check karo."

    def find_req(self, req_id):
        for uid_str, u in self.users_db.items():
            if not is_valid_uid(uid_str): continue
            for r in (u.get("pay_requests") or []):
                if r.get("req_id") == req_id:
                    return safe_int(uid_str), r
        return None, None

    def set_plan(self, uid, days):
        uid  = safe_int(uid)
        days = safe_int(days)
        u    = self._get_u(uid) or {}
        exp  = now_ts() + days * 86400
        u.update({
            "premium_expires": exp,
            "premium_days":    days,
            "premium_price":   PLANS.get(days, 0),
            "limit_override":  PLAN_BOT_LIMITS.get(days, FREE_LIMIT_DEFAULT),
            "limit_expires":   exp,
        })
        self._save_u(uid, u)

    def approve_req(self, admin_id, req_id):
        uid, r = self.find_req(req_id)
        if not r: return "❌ Request nahi mili. ID check karo."
        if r.get("status") not in ("PAID", "PENDING"):
            return f"⚠️ Already processed: {r.get('status')}"
        days = safe_int(r.get("days", 0))
        self.set_plan(uid, days)
        r.update({"status": "APPROVED", "approved_at": now_ts(), "approved_by": safe_int(admin_id)})
        save_json(USERS_FILE, self.users_db)
        u = self._get_u(uid)
        send(uid,
            f"🎉 PAYMENT APPROVED!\n{DIV}\n"
            f"✅ Plan activate ho gaya!\n\n"
            f"💎 Plan      : {days} Days Premium\n"
            f"🤖 Bot Slots : {PLAN_BOT_LIMITS.get(days,'?')}\n"
            f"📅 Expires   : {self.premium_exp(uid)}\n"
            f"📆 Days Left : {self.days_left(uid)} days\n"
            f"{DIV}\n"
            f"🚀 /bots se manage karo!\n"
            f"📢 {CHANNEL_LINK}"
        )
        return (
            f"✅ PAYMENT APPROVED\n{DIV}\n"
            f"🧾 Req ID  : {req_id}\n"
            f"👤 User    : {u.get('first_name','')} (@{u.get('username','-')})\n"
            f"🆔 ID      : {uid}\n"
            f"💎 Plan    : {days} days\n"
            f"💰 Amount  : ₹{r.get('price','?')}\n"
            f"⏰ Time    : {fmt_time(now_ts())}\n{DIV}"
        )

    def reject_req(self, admin_id, req_id, reason=""):
        uid, r = self.find_req(req_id)
        if not r: return "❌ Request nahi mili."
        if r.get("status") == "APPROVED": return "⚠️ Already approved."
        r.update({
            "status":      "REJECTED",
            "approved_at": now_ts(),
            "approved_by": safe_int(admin_id),
            "reason":      (reason or "")[:200]
        })
        save_json(USERS_FILE, self.users_db)
        send(uid,
            f"❌ PAYMENT REJECTED\n{DIV}\n"
            f"🧾 Req ID : {req_id}\n"
            f"📝 Reason : {reason or 'N/A'}\n"
            f"{DIV}\nHelp ke liye: {SUPPORT_LINK}"
        )
        return f"❌ {req_id} reject kar diya.\n📝 Reason: {reason or 'N/A'}"

    def pending_pays(self):
        lines = [f"💰 PENDING PAYMENTS", DIV, ""]
        found = 0
        for uid_str, u in self.users_db.items():
            if not is_valid_uid(uid_str): continue
            for r in (u.get("pay_requests") or []):
                if r.get("status") in ("PENDING", "PAID"):
                    found += 1
                    icon = "💰" if r["status"] == "PAID" else "⏳"
                    lines.append(
                        f"{icon} {r['req_id']}\n"
                        f"   👤 {u.get('first_name','')} (@{u.get('username','-')}) | {uid_str}\n"
                        f"   💎 {r['days']} Days ₹{r['price']} | {r['status']}\n"
                        f"   💳 Txn: {r.get('txn_id','-')}\n"
                        f"   ⏰ {fmt_time(r['created_at'])}\n"
                        f"   ✅ /approve {r['req_id']}  ❌ /reject {r['req_id']}\n"
                    )
        if not found: lines.append("✅ Koi pending payment nahi.")
        else: lines.insert(2, f"Total Pending: {found}\n")
        return "\n".join(lines)

    def pay_history(self, uid):
        u    = self._get_u(uid)
        reqs = u.get("pay_requests", [])
        if not reqs: return "📭 Koi payment history nahi."
        lines = [f"📜 PAYMENT HISTORY ({len(reqs)})", DIV, ""]
        total_spent = sum(safe_int(r.get("price", 0)) for r in reqs if r.get("status") == "APPROVED")
        for r in reqs[-10:]:
            icon = {"APPROVED":"✅","REJECTED":"❌","PAID":"💰","PENDING":"⏳"}.get(r["status"],"❓")
            lines.append(
                f"{icon} {r['req_id']}\n"
                f"   💎 {r['days']}d ₹{r['price']} | {r['status']}\n"
                f"   ⏰ {fmt_time(r['created_at'])}\n"
            )
        lines.append(f"{DIV}\n💰 Total Spent: ₹{total_spent}")
        return "\n".join(lines)

    def revenue_stats(self):
        total   = 0
        monthly = 0
        pending_amount = 0
        now_month = datetime.now().month
        now_year  = datetime.now().year
        for uid_str, u in self.users_db.items():
            if not is_valid_uid(uid_str): continue
            for r in u.get("pay_requests", []):
                price = safe_int(r.get("price", 0))
                if r.get("status") == "APPROVED":
                    total += price
                    try:
                        d = datetime.fromtimestamp(safe_int(r.get("approved_at", 0)))
                        if d.month == now_month and d.year == now_year: monthly += price
                    except: pass
                elif r.get("status") in ("PENDING", "PAID"):
                    pending_amount += price
        return (
            f"💰 REVENUE STATS\n{DIV}\n"
            f"✅ Total Revenue   : ₹{total}\n"
            f"📅 This Month      : ₹{monthly}\n"
            f"⏳ Pending (unverified): ₹{pending_amount}\n"
            f"{DIV}"
        )

    # ── Bot DB ──
    def _bots_db(self, uid):   return self.bots_admin if self.is_admin(uid) else self.bots_users
    def _bots_file(self, uid): return BOTS_ADMIN_FILE if self.is_admin(uid) else BOTS_USERS_FILE
    def _bots_dir(self, uid):  return BOTS_ADMIN_DIR  if self.is_admin(uid) else BOTS_USERS_DIR

    def _cleanup_db(self):
        def valid(i):
            try:
                return (isinstance(i, dict)
                        and is_valid_uid(i.get("owner_id", 0))
                        and safe_name(i.get("name", ""))
                        and str(i.get("file", "")).strip())
            except: return False
        for db, f in [(self.bots_users, BOTS_USERS_FILE), (self.bots_admin, BOTS_ADMIN_FILE)]:
            changed = False
            for k in list(db.keys()):
                if not valid(db[k]): del db[k]; changed = True
            if changed: save_json(f, db)

    def bot_count(self, uid):
        uid = safe_int(uid)
        return sum(1 for _, i in self._bots_db(uid).items() if safe_int(i.get("owner_id", -1)) == uid)

    def detect_bot(self, token):
        try: del_webhook_tok(token)
        except: pass
        for _ in range(3):
            try:
                r = tg(token, "getMe", timeout=10)
                if r.get("ok"):
                    res = r.get("result") or {}
                    return str(res.get("id", "")), str(res.get("username", "")), str(res.get("first_name", ""))
            except: pass
            time.sleep(0.5)
        return "", "", ""

    def _start_bot(self, oid, ocid, name, bot_file, work_dir, deps,
                   persist=True, bot_id=None, bot_uname=None, bot_dname=None, entry_label=""):
        oid  = safe_int(oid)
        ocid = safe_int(ocid)
        name = safe_name(name)
        kk   = bot_key(oid, name)
        if not self.is_admin(oid) and self.bot_count(oid) >= self.effective_limit(oid):
            self.credit_ended(ocid, oid); return "❌ Bot limit khatam."
        if kk in self.runners and self.runners[kk].proc and self.runners[kk].proc.poll() is None:
            return "✅ Bot pehle se chal raha hai."
        tok = extract_token(bot_file)
        if not tok:
            u    = self._get_u(oid) or {}
            pend = u.get("pending_token", {})
            pend[name] = bot_file
            u["pending_token"] = pend
            self._save_u(oid, u)
            return (
                f"⚠️ BOT TOKEN NAHI MILA\n{DIV}\n"
                f"File mein BOT_TOKEN variable nahi hai.\n\n"
                f"Fix karo:\n"
                f"  /save <your_bot_token>\n\n"
                f"Token format: 1234567890:ABCdef...\n{DIV}"
            )
        if not BOT_TOKEN_FMT.match(tok):
            return (
                f"❌ TOKEN FORMAT GALAT!\n{DIV}\n"
                f"Correct format:\n"
                f"  BOT_TOKEN = \"1234567890:ABCdefGHIjkl\"\n\n"
                f"@BotFather se token lo.\n{DIV}"
            )
        if not bot_id or not bot_uname:
            bot_id, bot_uname, bot_dname = self.detect_bot(tok)

        def nfn(cid, txt): send(safe_int(cid), txt)
        r = BotRunner(oid, ocid, name, bot_file, work_dir, deps, nfn)
        r.bot_uname = bot_uname or ""
        r.bot_id    = bot_id    or ""
        self.runners[kk] = r
        r.start()

        if persist:
            db = self._bots_db(oid)
            db[kk] = {
                "owner_id":        oid,
                "name":            name,
                "file":            bot_file,
                "work_dir":        work_dir,
                "token":           tok,
                "bot_id":          bot_id    or "",
                "bot_username":    bot_uname or "",
                "bot_display_name": bot_dname or "",
                "entrypoint":      entry_label or os.path.basename(bot_file),
                "created_at":      now_ts(),
            }
            save_json(self._bots_file(oid), db)
        return ""

    def stop_bot(self, oid, name, delete=False):
        oid  = safe_int(oid)
        name = safe_name(name)
        kk   = bot_key(oid, name)
        r    = self.runners.get(kk)
        if r: r.stop(); self.runners.pop(kk, None)
        if delete:
            base = self._bots_dir(oid)
            rm_tree(os.path.join(base, str(oid), name))
            rm_tree(os.path.join(DEPS_DIR, str(oid), name))
            lp = log_path(oid, name)
            try:
                if os.path.exists(lp): os.remove(lp)
            except: pass
            db = self._bots_db(oid)
            db.pop(kk, None)
            save_json(self._bots_file(oid), db)
            return f"🗑️ Bot deleted: {name}"
        return f"🛑 Bot stopped: {name}"

    def on_bot(self, oid, cid, name):
        oid  = safe_int(oid)
        name = safe_name(name)
        kk   = bot_key(oid, name)
        info = self._bots_db(oid).get(kk)
        if not info: return f"❌ Bot '{name}' nahi mila.\n/bots se dekho."
        deps = os.path.join(DEPS_DIR, str(oid), name)
        return self._start_bot(oid, cid, name, info["file"],
                               info.get("work_dir") or os.path.dirname(info["file"]),
                               deps, persist=True,
                               bot_id=info.get("bot_id"),
                               bot_uname=info.get("bot_username"),
                               bot_dname=info.get("bot_display_name"),
                               entry_label=info.get("entrypoint", ""))

    def restart_bot(self, oid, cid, name):
        self.stop_bot(oid, name, delete=False)
        time.sleep(0.5)
        result = self.on_bot(oid, cid, name)
        return result or f"🔄 Bot restarting: {name}"

    def start_saved(self):
        for db in [self.bots_users, self.bots_admin]:
            for kk, info in list(db.items()):
                try:
                    oid      = safe_int(info.get("owner_id", 0))
                    name     = safe_name(info.get("name", ""))
                    bot_file = info.get("file", "")
                    work_dir = info.get("work_dir", "") or os.path.dirname(bot_file)
                    if not oid or not name or not bot_file: continue
                    if not os.path.exists(bot_file): continue
                    if kk in self.runners: continue
                    deps = os.path.join(DEPS_DIR, str(oid), name)
                    self._start_bot(oid, oid, name, bot_file, work_dir, deps,
                                    persist=True,
                                    bot_id=info.get("bot_id"),
                                    bot_uname=info.get("bot_username"),
                                    bot_dname=info.get("bot_display_name"),
                                    entry_label=info.get("entrypoint", ""))
                except: pass

    def save_token(self, uid, token):
        uid   = safe_int(uid)
        token = (token or "").strip()
        if not BOT_TOKEN_FMT.match(token):
            return (
                f"❌ TOKEN FORMAT GALAT!\n{DIV}\n"
                f"Correct format:\n"
                f"  1234567890:ABCdefGHIjklmnopqr\n\n"
                f"@BotFather se token lo.\n{DIV}"
            )
        u    = self._get_u(uid) or {}
        pend = u.get("pending_token") or {}
        if not pend: return "❌ Koi pending bot nahi.\nPehle .py ya .zip file upload karo."
        name  = list(pend.keys())[-1]
        fpath = pend.get(name)
        if not fpath or not os.path.exists(fpath):
            pend.pop(name, None)
            u["pending_token"] = pend
            self._save_u(uid, u)
            return "❌ Pending file nahi mili. Dobara upload karo."
        try:
            enc = detect_encoding(fpath)
            with open(fpath, "r", encoding=enc, errors="ignore") as f: src = f.read()
            replaced = False
            for pat, rep in [
                (r'(BOT_TOKEN|TOKEN|bot_token|token|API_TOKEN|API_KEY)\s*=\s*["\'][^"\']*["\']',
                 f'\\1 = "{token}"'),
                (r'["\'][0-9]{5,}:[A-Za-z0-9_-]{20,}["\']', f'"{token}"')
            ]:
                if re.search(pat, src, re.I):
                    src      = re.sub(pat, rep, src, flags=re.I)
                    replaced = True
                    break
            if not replaced: src = f'BOT_TOKEN = "{token}"\n' + src
            with open(fpath, "w", encoding="utf-8") as f: f.write(src)
            pend.pop(name, None)
            u["pending_token"] = pend
            self._save_u(uid, u)
            base = self._bots_dir(uid)
            udir = os.path.join(base, str(uid), name)
            deps = os.path.join(DEPS_DIR, str(uid), name)
            self._start_bot(uid, uid, name, fpath, udir, deps, persist=True)
            return f"✅ Token save hua!\n🚀 Bot start ho raha hai: {name}"
        except Exception as e:
            return f"❌ Failed: {str(e)[:300]}"

    def find_user_by_uname(self, uname):
        uname = uname.lstrip("@").lower()
        for uid_str, u in self.users_db.items():
            if not is_valid_uid(uid_str): continue
            if (u.get("username") or "").lower() == uname:
                return safe_int(uid_str), u
        return None, None

    def schedule_task(self, uid, bot_name, action, delay_minutes):
        sched   = load_json(SCHEDULED_FILE)
        task_id = f"TASK{uid}{now_ts()}"
        run_at  = now_ts() + (delay_minutes * 60)
        sched[task_id] = {
            "uid": safe_int(uid), "name": safe_name(bot_name),
            "action": action, "run_at": run_at,
            "done": False, "created_at": now_ts()
        }
        save_json(SCHEDULED_FILE, sched)
        return (
            f"✅ TASK SCHEDULED\n{DIV}\n"
            f"🆔 Task ID : {task_id}\n"
            f"🤖 Bot     : {bot_name}\n"
            f"⚡ Action  : {action}\n"
            f"⏰ Run At  : {fmt_time(run_at)}\n"
            f"⏱ Delay   : {delay_minutes} min\n{DIV}"
        )

    def backup_data(self, admin_id):
        ts          = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{ts}.zip")
        files_to_backup = [
            USERS_FILE, BOTS_USERS_FILE, BOTS_ADMIN_FILE, BANNED_FILE,
            NOTICES_FILE, QR_FILE, ADMINS_FILE, REFERRALS_FILE,
            WELCOME_FILE, AUTOREPLY_FILE, COUPON_FILE, CUSTOM_CMD_FILE,
            SCHEDULED_FILE, MAINTENANCE_FILE,
        ]
        try:
            with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as z:
                for f in files_to_backup:
                    if os.path.exists(f): z.write(f)
            size = os.path.getsize(backup_path)
            return backup_path, f"✅ Backup created!\n📦 Size: {fmt_size(size)}\n📁 {backup_path}"
        except Exception as e:
            return None, f"❌ Backup failed: {str(e)[:300]}"

    # ══════════════════════════════════════════
    #   TEXT BUILDERS — Beautiful formatting
    # ══════════════════════════════════════════

    def plan_text(self):
        lines = [
            f"╭━━━〔 💎 <b>{BOT_NAME} — PREMIUM PLANS</b> 〕━━━╮",
            f"┃├ 🚀 24/7 Hosting   ┃  ⚡ Auto-restart",
            f"┃├ 🌐 All Languages  ┃  🛡️ Perfect errors",
            f"╰{'━'*34}╯\n",
        ]
        for d in sorted(PLANS):
            if d >= 180:   badge = "🌟 BEST VALUE"
            elif d >= 90:  badge = "⭐ Popular"
            elif d >= 30:  badge = "🔷 Standard"
            elif d >= 7:   badge = "🔹 Basic"
            else:          badge = "▫️ Starter"
            lines.append(
                f"╭━━━〔 {badge} 〕━━━╮\n"
                f"┃├ ⏳ Duration : <b>{d} Days</b>\n"
                f"┃├ 💰 Price   : ₹{PLANS[d]}\n"
                f"┃├ 🤖 Bots    : {PLAN_BOT_LIMITS[d]} slots\n"
                f"╰{'━'*28}╯"
            )
        lines += [
            f"\n╭━━━〔 💳 HOW TO BUY 〕━━━╮",
            f"┃├ 1️⃣  /buy &lt;days&gt;",
            f"┃├ 2️⃣  UPI pe pay: <code>{UPI_ID}</code>",
            f"┃├ 3️⃣  /paid &lt;req_id&gt; &lt;txn_id&gt;",
            f"┃├ 4️⃣  /payss &lt;req_id&gt; + screenshot",
            f"┃├ 5️⃣  Admin verify karega ⚡",
            f"╰{'━'*28}╯\n",
            f"👤 Pay to  : <b>{OWNER_NAME}</b>",
            f"📲 UPI ID  : <code>{UPI_ID}</code>",
            f"🎟️ Coupon  : /redeem &lt;code&gt;",
            f"📢 <a href='{CHANNEL_LINK}'>Join Our Channel</a>",
        ]
        return "\n".join(lines)

    def about_text(self):
        langs = [
            ("🐍", "Python",     ".py",        "python-telegram-bot, aiogram, telethon, pyrogram"),
            ("🟩", "Node.js",    ".js .mjs",   "node-telegram-bot-api, telegraf, grammy"),
            ("🔷", "TypeScript", ".ts",        "grammy, telegraf (ts-node)"),
            ("🔵", "Go",        ".go",         "telebot, telegram-bot-api"),
            ("💎", "Ruby",      ".rb",         "telegram-bot-ruby"),
            ("🐘", "PHP",       ".php",        "irazasyed/telegram-bot-sdk"),
            ("🐚", "Shell",     ".sh",         "curl + Telegram API"),
            ("🔮", "Perl",      ".pl",         "Perl Telegram Bot"),
            ("🌙", "Lua",       ".lua",        "Lua Telegram Bot"),
        ]
        lang_lines = "\n".join(
            f"┃├ {em} <b>{name}</b> (<code>{ext}</code>)\n┃├    ↳ {libs}"
            for em, name, ext, libs in langs
        )
        return (
            f"╭━━━〔 ℹ️ <b>ABOUT {BOT_NAME}</b> 〕━━━╮\n"
            f"┃├ 🤖 <b>{BOT_NAME}</b> — Bot Hosting Panel v5.0\n"
            f"┃├ 👨‍💻 Developer : <b>{OWNER_NAME}</b>\n"
            f"┃├ 🌐 Platform  : Replit / VPS / Termux\n"
            f"╰{'━'*34}╯\n\n"

            f"╭━━━〔 🌐 <b>SUPPORTED LANGUAGES</b> 〕━━━╮\n"
            f"{lang_lines}\n"
            f"╰{'━'*34}╯\n\n"

            f"╭━━━〔 📦 <b>SUPPORTED FILE TYPES</b> 〕━━━╮\n"
            f"┃├ 📄 Single file  : .py .js .ts .go .rb .php .sh\n"
            f"┃├ 📦 Project ZIP  : Any language (.zip)\n"
            f"┃├ 🗂️ Project .env : Token auto-detect\n"
            f"┃├ 📋 requirements.txt → auto pip install\n"
            f"┃├ 📋 package.json → auto npm install\n"
            f"┃├ 📋 go.mod → auto go mod download\n"
            f"┃├ 📋 Gemfile → auto bundle install\n"
            f"╰{'━'*34}╯\n\n"

            f"╭━━━〔 ✨ <b>FEATURES</b> 〕━━━╮\n"
            f"┃├ ✅ Multi-language bot hosting\n"
            f"┃├ ✅ Auto dependency install\n"
            f"┃├ ✅ Live boot progress bar\n"
            f"┃├ ✅ Error detection + code block\n"
            f"┃├ ✅ Auto restart on crash\n"
            f"┃├ ✅ Premium Plans + Coupons\n"
            f"┃├ ✅ Referral system\n"
            f"┃├ ✅ Inline keyboard buttons\n"
            f"┃├ ✅ Broadcast + Auto-reply\n"
            f"┃├ ✅ Full Admin panel\n"
            f"╰{'━'*34}╯\n\n"
            f"📢 <a href='{CHANNEL_LINK}'>Channel</a>  ┃  "
            f"💬 <a href='{SUPPORT_LINK}'>Support</a>"
        )

    def user_kb(self):
        """Reply keyboard for regular users — 2 buttons per row."""
        return mk_reply_kb([
            ["🤖 My Bots",      "📊 My Status"],
            ["💳 My Plan",      "📋 Help"],
            ["🔗 Referral",     "💰 Buy Plan"],
            ["ℹ️ About",        "📢 Support"],
        ])

    def admin_kb(self):
        """Reply keyboard for admins — 2 buttons per row."""
        return mk_reply_kb([
            ["📊 Stats",        "💻 System Info"],
            ["🤖 My Bots",      "🟢 Running Bots"],
            ["👥 All Users",    "👑 Premium Users"],
            ["📋 Admin Help",   "💰 Revenue"],
            ["⚙️ Maintenance",  "📢 Broadcast"],
            ["ℹ️ About",        "🔗 Channel"],
        ])

    def handle_keyboard_text(self, cid, uid, text, ia):
        """Handle reply keyboard button presses (text that matches a button label)."""
        m = {
            "🤖 My Bots":      lambda: sendh(cid, self.my_bots(uid)),
            "📊 My Status":    lambda: sendh(cid, self.mystatus(uid)),
            "💳 My Plan":      lambda: sendh(cid, self.myplan(uid)),
            "📋 Help":         lambda: sendh(cid, self.help_admin(uid) if ia else self.help_user(uid)),
            "📋 Admin Help":   lambda: sendh(cid, self.help_admin(uid)),
            "🔗 Referral":     lambda: send(cid, self.referral_info(uid)),
            "💰 Buy Plan":     lambda: sendh(cid, self.plan_text()),
            "💰 Revenue":      lambda: sendh(cid, self.revenue_stats()),
            "ℹ️ About":        lambda: sendh(cid, self.about_text(), reply_markup=mk_url_kb([[("📢 Channel", CHANNEL_LINK),("💬 Support", SUPPORT_LINK)]])),
            "📢 Support":      lambda: send(cid, f"💬 Support: {SUPPORT_LINK}"),
            "📊 Stats":        lambda: sendh(cid, self.stats()),
            "💻 System Info":  lambda: sendh(cid, self.system_info()),
            "🟢 Running Bots": lambda: sendh(cid, self.running_bots()),
            "👥 All Users":    lambda: send(cid, self.users_text()),
            "👑 Premium Users":lambda: send(cid, self.premium_users()),
            "⚙️ Maintenance":  lambda: sendh(cid, self.toggle_maintenance_quick(uid)),
            "📢 Broadcast":    lambda: send(cid, "Usage: /broadcast <message>"),
            "🔗 Channel":      lambda: send(cid, f"📢 Channel: {CHANNEL_LINK}"),
        }
        fn = m.get(text)
        if fn:
            fn()
            return True
        return False

    def toggle_maintenance_quick(self, uid):
        curr = self.is_maintenance()
        return self.set_maintenance(uid, "off" if curr else "on")

    def handle_callback(self, cbq):
        """Handle inline keyboard callback queries."""
        try:
            cid  = (cbq.get("message") or {}).get("chat", {}).get("id")
            uid  = safe_int((cbq.get("from") or {}).get("id", 0))
            qid  = cbq.get("id")
            data = cbq.get("data", "")
            ia   = self.is_admin(uid)
            answer_callback(qid)
            if not cid or not uid: return
            if data == "cb_bots":    sendh(cid, self.my_bots(uid))
            elif data == "cb_status": sendh(cid, self.mystatus(uid))
            elif data == "cb_plan":  sendh(cid, self.myplan(uid))
            elif data == "cb_help":  sendh(cid, self.help_admin(uid) if ia else self.help_user(uid))
            elif data == "cb_stats" and ia: sendh(cid, self.stats())
            elif data == "cb_sysinfo" and ia: sendh(cid, self.system_info())
            elif data == "cb_running" and ia: sendh(cid, self.running_bots())
            elif data == "cb_about": sendh(cid, self.about_text())
            elif data == "cb_check_join":
                # Re-check force join status
                not_joined = check_force_join(uid)
                if not_joined:
                    answer_callback(qid, "❌ Abhi bhi join nahi kiya!", alert=True)
                    kb = {"inline_keyboard": [[{"text": ch["name"], "url": ch["link"]}] for ch in not_joined]
                          + [[{"text": "✅ Maine Join Kar Liya!", "callback_data": "cb_check_join"}]]}
                    sendh(cid,
                        f"╭━━━〔 ❌ <b>ABHI BHI JOIN NAHI KIYA</b> 〕━━━╮\n"
                        f"┃├ Pehle neeche wale channels join karo:\n"
                        + "".join(f"┃├ ⚠️ <b>{ch['name']}</b>\n" for ch in not_joined)
                        + f"╰━━━━━━━━━━━━━━━━━━━━━━━━━╯",
                        reply_markup=kb
                    )
                else:
                    answer_callback(qid, "✅ Sab join ho gaya! Ab bot use karo.", alert=True)
                    kb = self.admin_kb() if ia else self.user_kb()
                    sendh(cid,
                        f"╭━━━〔 ✅ <b>VERIFIED!</b> 〕━━━╮\n"
                        f"┃├ 🎉 Sab channels join kar liye!\n"
                        f"┃├ Ab bot use kar sakte ho.\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━╯",
                        reply_markup=kb
                    )
        except Exception as e:
            print(f"[CB ERROR] {e}")

    # ── Force-Join Management Methods ──
    def fj_list(self):
        try:
            d = load_json(FORCE_JOIN_FILE)
            return d.get("channels", DEFAULT_FORCE_JOINS)
        except: return list(DEFAULT_FORCE_JOINS)

    def fj_add(self, chat_id, link, name=""):
        chat_id = safe_int(chat_id)
        channels = self.fj_list()
        for ch in channels:
            if ch["id"] == chat_id:
                return f"⚠️ Chat ID {chat_id} pehle se hai!"
        channels.append({"id": chat_id, "link": link, "name": name or str(chat_id)})
        save_json(FORCE_JOIN_FILE, {"channels": channels})
        return f"✅ Force-join channel add ho gaya!\n🆔 ID: {chat_id}\n🔗 Link: {link}"

    def fj_remove(self, chat_id):
        chat_id = safe_int(chat_id)
        channels = self.fj_list()
        new = [ch for ch in channels if ch["id"] != chat_id]
        if len(new) == len(channels):
            return f"❌ Chat ID {chat_id} nahi mila."
        save_json(FORCE_JOIN_FILE, {"channels": new})
        return f"✅ Force-join channel remove ho gaya! ID: {chat_id}"

    def fj_show(self):
        channels = self.fj_list()
        if not channels: return "📭 Koi force-join channel nahi."
        lines = [f"╭━━━〔 📋 <b>FORCE-JOIN CHANNELS</b> 〕━━━╮\n"]
        for i, ch in enumerate(channels, 1):
            lines.append(f"┃├ {i}. <b>{ch['name']}</b>\n┃├   🆔 {ch['id']}\n┃├   🔗 {ch['link']}\n")
        lines.append("╰━━━━━━━━━━━━━━━━━━━━━━━━━╯")
        return "".join(lines)

    def help_user(self, uid):
        prem     = "✅ <b>Premium Active</b>" if self.is_premium(uid) else "🔓 <i>Free Plan</i>"
        used     = self.bot_count(uid)
        lim      = self.effective_limit(uid)
        notice   = self.get_notice()
        notice_line = f"\n╭━━━〔 🔔 NOTICE 〕━━━╮\n┃├ {notice}\n╰━━━━━━━━━━━━━━━━━╯\n" if notice else ""
        ref_link = f"https://t.me/{BOT_NAME}bot?start=ref{uid}"
        days     = self.days_left(uid)
        exp      = self.premium_exp(uid)
        bar_fill = min(used, lim)
        bar      = "🟩" * bar_fill + "⬜" * (lim - bar_fill) if lim <= 10 else f"{used}/{lim}"
        badge    = "👑" if self.is_super(uid) else ("🛡️" if self.is_admin(uid) else "👤")
        return (
            f"╭━━━〔 🤖 <b>{BOT_NAME} BOT HOSTING</b> 〕━━━╮\n"
            f"┃├ ✦ <i>v5.0 — by {OWNER_NAME}</i>  {badge}\n"
            f"╰{'━'*34}╯"
            f"{notice_line}\n\n"

            f"╭━━━〔 📊 <b>YOUR STATUS</b> 〕━━━╮\n"
            f"┃├ 💎 Plan      : {prem}\n"
            f"┃├ 📅 Expires   : {exp}\n"
            f"┃├ ⏳ Days Left : <b>{days}</b> days\n"
            f"┃├ 🤖 Bots Used : {bar}\n"
            f"╰{'━'*26}╯\n\n"

            f"╭━━━〔 📤 <b>HOW TO HOST</b> 〕━━━╮\n"
            f"┃├ 1️⃣  .py ya .zip file yahan bhejo\n"
            f"┃├ 2️⃣  Token file mein hona chahiye\n"
            f"┃├ 3️⃣  Token nahi? /save &lt;token&gt;\n"
            f"┃├ ✅  All coding languages supported\n"
            f"╰{'━'*26}╯\n\n"

            f"╭━━━〔 🎮 <b>BOT CONTROL</b> 〕━━━╮\n"
            f"┃├ /bots              — Apne bots dekho\n"
            f"┃├ /botinfo &lt;name&gt;    — Bot ki details\n"
            f"┃├ /on &lt;name&gt;         — Bot start karo\n"
            f"┃├ /stop &lt;name&gt;       — Bot band karo\n"
            f"┃├ /restart &lt;name&gt;    — Restart karo\n"
            f"┃├ /delete &lt;name&gt;     — Bot delete karo\n"
            f"┃├ /logs &lt;name&gt;       — Logs dekho\n"
            f"┃├ /clearlogs &lt;name&gt;  — Logs clear karo\n"
            f"┃├ /save &lt;token&gt;      — Token set karo\n"
            f"┃├ /schedule &lt;n&gt; &lt;act&gt; &lt;min&gt; — Schedule\n"
            f"╰{'━'*26}╯\n\n"

            f"╭━━━〔 👤 <b>MY ACCOUNT</b> 〕━━━╮\n"
            f"┃├ /mystatus          — Full account info\n"
            f"┃├ /myplan            — Plan details\n"
            f"┃├ /payhistory        — Payment history\n"
            f"┃├ /referral          — Referral link\n"
            f"┃├ /redeem &lt;code&gt;     — Coupon use karo\n"
            f"╰{'━'*26}╯\n\n"

            f"╭━━━〔 💳 <b>PLANS &amp; PAYMENT</b> 〕━━━╮\n"
            f"┃├ /plan              — Plans &amp; pricing\n"
            f"┃├ /buy &lt;days&gt;        — Plan kharido\n"
            f"┃├ /paid &lt;id&gt; &lt;txn&gt;   — Confirm payment\n"
            f"┃├ /payss &lt;id&gt;        — Screenshot bhejo\n"
            f"╰{'━'*26}╯\n\n"

            f"╭━━━〔 ⌨️ <b>KEYBOARD &amp; TOOLS</b> 〕━━━╮\n"
            f"┃├ /convertbutton     — Reply keyboard ON\n"
            f"┃├ /convertcommand    — Text commands mode\n"
            f"┃├ /buttons           — Quick buttons show\n"
            f"┃├ /about             — Language support info\n"
            f"╰{'━'*26}╯\n\n"

            f"🔗 <b>Referral Link:</b>\n"
            f"<code>{ref_link}</code>\n"
            f"🎁 Har referral = <b>{REFERRAL_BONUS_DAYS} free days!</b>\n\n"
            f"{'━'*32}\n"
            f"📢 <a href='{CHANNEL_LINK}'>Channel</a>  ┃  "
            f"💬 <a href='{SUPPORT_LINK}'>Support</a>  ┃  "
            f"⚡ <b>{BOT_NAME}</b>"
        )

    def help_admin(self, uid):
        role = "👑 Super Admin" if self.is_super(uid) else "🛡️ Admin"
        return (
            f"╭━━━〔 🛡️ <b>{BOT_NAME} ADMIN PANEL</b> 〕━━━╮\n"
            f"┃├ 🎭 Role  : <b>{role}</b>\n"
            f"┃├ ⚡ By    : <i>{OWNER_NAME}</i>  v5.0\n"
            f"╰{'━'*34}╯\n\n"

            f"╭━━━〔 👥 <b>USER MANAGEMENT</b> 〕━━━╮\n"
            f"┃├ /users                 — All users list\n"
            f"┃├ /userinfo &lt;id&gt;         — Basic info\n"
            f"┃├ /fulluserinfo &lt;id&gt;     — Full info + photo\n"
            f"┃├ /finduser &lt;@u or id&gt;   — User search\n"
            f"┃├ /activeusers           — Aaj active users\n"
            f"┃├ /premiumusers          — Premium list\n"
            f"┃├ /ban &lt;id&gt; [reason]     — User ban\n"
            f"┃├ /unban &lt;id&gt;            — Unban\n"
            f"┃├ /banlist               — Banned users\n"
            f"┃├ /warn &lt;id&gt; [reason]    — Warning do\n"
            f"┃├ /unwarn &lt;id&gt;           — Warning hatao\n"
            f"┃├ /setnote &lt;id&gt; &lt;note&gt;   — Note add karo\n"
            f"╰{'━'*30}╯\n\n"

            f"╭━━━〔 🤖 <b>BOT MANAGEMENT</b> 〕━━━╮\n"
            f"┃├ /allbots               — Sabhi bots\n"
            f"┃├ /runningbots           — Active bots\n"
            f"┃├ /alllogs               — Sabhi logs\n"
            f"┃├ /botlog &lt;uid&gt; &lt;name&gt;   — Specific log\n"
            f"┃├ /allbotsstop           — Sab bots band\n"
            f"┃├ /allbotson             — Sab bots start\n"
            f"┃├ /adminbots             — Admin ke bots\n"
            f"┃├ /delete &lt;uid&gt; &lt;name&gt;   — Bot delete\n"
            f"┃├ /deletealluserbots     — User ke sab bots\n"
            f"╰{'━'*30}╯\n\n"

            f"╭━━━〔 💰 <b>PAYMENT &amp; PLANS</b> 〕━━━╮\n"
            f"┃├ /pendingpay            — Pending list\n"
            f"┃├ /approve &lt;req_id&gt;      — Approve payment\n"
            f"┃├ /reject &lt;req_id&gt; [r]   — Reject payment\n"
            f"┃├ /giveplan &lt;id&gt; &lt;days&gt;  — Manual plan do\n"
            f"┃├ /extendplan &lt;id&gt; &lt;d&gt;   — Plan extend\n"
            f"┃├ /usergivebot &lt;id&gt; &lt;l&gt; &lt;d&gt; — Bot limit\n"
            f"┃├ /allusergive &lt;l&gt; &lt;d&gt;   — Sab ko plan\n"
            f"┃├ /resetallusercredit    — Sab reset\n"
            f"┃├ /revenue               — Revenue stats\n"
            f"┃├ /cybersameersetqr      — QR code set\n"
            f"╰{'━'*30}╯\n\n"

            f"╭━━━〔 🎟️ <b>COUPONS &amp; COMMANDS</b> 〕━━━╮\n"
            f"┃├ /addcoupon &lt;d&gt; &lt;l&gt; [code] — Add coupon\n"
            f"┃├ /delcoupon &lt;code&gt;      — Delete coupon\n"
            f"┃├ /coupons               — Coupon list\n"
            f"┃├ /setcmd &lt;cmd&gt; &lt;reply&gt;  — Custom command\n"
            f"┃├ /delcmd &lt;cmd&gt;          — Delete command\n"
            f"┃├ /listcmds              — Commands list\n"
            f"╰{'━'*30}╯\n\n"

            f"╭━━━〔 💬 <b>WELCOME &amp; AUTO-REPLY</b> 〕━━━╮\n"
            f"┃├ /setwelcome &lt;text&gt;     — Welcome message\n"
            f"┃├ /clearwelcome          — Welcome hatao\n"
            f"┃├ /setreply &lt;kw&gt; &lt;rep&gt;   — Auto-reply set\n"
            f"┃├ /delreply &lt;keyword&gt;    — Reply delete\n"
            f"┃├ /listreplies           — Replies list\n"
            f"╰{'━'*30}╯\n\n"

            f"╭━━━〔 📢 <b>BROADCAST &amp; NOTICE</b> 〕━━━╮\n"
            f"┃├ /broadcast &lt;text&gt;      — Sab ko message\n"
            f"┃├ /broadcastpremium &lt;t&gt;  — Premium only\n"
            f"┃├ /setnotice &lt;text&gt;      — Notice set\n"
            f"┃├ /clearnotice           — Notice hatao\n"
            f"╰{'━'*30}╯\n\n"

            f"╭━━━〔 ⚙️ <b>SYSTEM</b> 〕━━━╮\n"
            f"┃├ /stats                 — Full statistics\n"
            f"┃├ /systeminfo            — Server info\n"
            f"┃├ /backup                — Data backup\n"
            f"┃├ /maintenance on/off    — Maintenance mode\n"
            f"╰{'━'*30}╯\n\n"

            f"╭━━━〔 🔒 <b>FORCE-JOIN MANAGEMENT</b> 〕━━━╮\n"
            f"┃├ /listfj                — Force-join channels\n"
            f"┃├ /addfj &lt;id&gt; &lt;link&gt; [name] — Add channel\n"
            f"┃├ /removefj &lt;id&gt;        — Remove channel\n"
            f"╰{'━'*30}╯\n\n"

            + (f"╭━━━〔 👑 <b>SUPER ADMIN ONLY</b> 〕━━━╮\n"
            f"┃├ /addadmin &lt;id&gt;         — Admin add\n"
            f"┃├ /removeadmin &lt;id&gt;      — Admin hatao\n"
            f"┃├ /adminlist             — Admins list\n"
            f"┃├ /admininfo &lt;id&gt;        — Admin full info\n"
            f"┃├ /sa                    — Super Admin panel\n"
            f"┃├ /deleteallbots         — ⚠️ Sabhi delete\n"
            f"╰{'━'*30}╯" if self.is_super(uid) else "")
        )

    def super_admin_panel(self):
        running  = sum(1 for r in self.runners.values() if r.proc and r.proc.poll() is None)
        total_u  = len([x for x in self.users_db if is_valid_uid(x) and safe_int(x) not in ADMIN_IDS])
        prem_u   = sum(1 for x in self.users_db if is_valid_uid(x) and self.is_premium(safe_int(x)) and safe_int(x) not in ADMIN_IDS)
        disk_used, disk_total, disk_free, disk_pct = get_disk_usage()
        load, mem = get_system_stats()
        cpu = get_cpu_info()
        return (
            f"╭━━━〔 👑 <b>SUPER ADMIN PANEL</b> 〕━━━╮\n"
            f"┃├ 🤖 {BOT_NAME} v5.0  by {OWNER_NAME}\n"
            f"╰{'━'*32}╯\n\n"

            f"╭━━━〔 📊 <b>QUICK STATS</b> 〕━━━╮\n"
            f"┃├ 👥 Users      : {total_u}\n"
            f"┃├ 💎 Premium    : {prem_u}\n"
            f"┃├ 🤖 Bots (DB)  : {len(self.bots_users) + len(self.bots_admin)}\n"
            f"┃├ 🟢 Running    : {running}\n"
            f"┃├ 🛡️ Admins    : {len(ADMIN_IDS)}\n"
            f"┃├ 🚫 Banned     : {len(self.banned_db)}\n"
            f"┃├ 🎟️ Coupons   : {len(self.coupons)}\n"
            f"╰{'━'*28}╯\n\n"

            f"╭━━━〔 💻 <b>SERVER INFO</b> 〕━━━╮\n"
            f"┃├ 🖥️ CPU        : {cpu}\n"
            f"┃├ 📊 CPU Load   : {load}\n"
            f"┃├ 🧠 Memory     : {mem}\n"
            f"┃├ 💾 Disk       : {disk_used} / {disk_total} ({disk_pct})\n"
            f"┃├ 🆓 Free       : {disk_free}\n"
            f"┃├ 🐍 Python     : {sys.version.split()[0]}\n"
            f"┃├ ⏱️ Uptime     : {uptime_str(now_ts() - self.start_time)}\n"
            f"╰{'━'*28}╯\n\n"

            f"╭━━━〔 ⚡ <b>SA COMMANDS</b> 〕━━━╮\n"
            f"┃├ /addadmin      /removeadmin\n"
            f"┃├ /adminlist     /admininfo\n"
            f"┃├ /deleteallbots /backup\n"
            f"┃├ /revenue       /systeminfo\n"
            f"┃├ /allusergive   /resetallusercredit\n"
            f"┃├ /broadcastpremium\n"
            f"╰{'━'*28}╯"
        )

    def admin_full_info(self, target_id):
        target_id = safe_int(target_id)
        if not is_valid_uid(target_id): return "❌ Invalid ID.", None
        if target_id not in ADMIN_IDS: return "❌ Yeh admin nahi hai.", None
        u       = self._get_u(target_id)
        tg_info = get_user_info_tg(target_id)
        pfp     = get_pfp(target_id)
        bots    = []
        for kk, info in {**self.bots_users, **self.bots_admin}.items():
            if safe_int(info.get("owner_id", 0)) == target_id:
                running = kk in self.runners and self.runners[kk].proc and self.runners[kk].proc.poll() is None
                bots.append(f"{'🟢' if running else '🔴'} {info.get('name','')} @{info.get('bot_username','-')}")
        role = "⭐ SUPER ADMIN" if target_id == SUPER_ADMIN else "🛡️ Admin"
        result = (
            f"👑 ADMIN FULL INFO\n{DIV}\n"
            f"🎭 Role        : {role}\n"
            f"🆔 ID          : {target_id}\n"
            f"👤 Name        : {u.get('first_name','')} {u.get('last_name','')}\n"
            f"📛 Username    : @{u.get('username','-')}\n"
            f"🌐 Language    : {u.get('language_code','N/A')}\n"
            f"📝 TG Bio      : {tg_info.get('bio','—')}\n"
            f"🔗 Profile     : tg://user?id={target_id}\n"
            f"{DIV2}\n"
            f"📤 Uploads     : {u.get('total_uploads',0)}\n"
            f"💬 Messages    : {u.get('total_messages',0)}\n"
            f"🤖 Bots Hosted : {self.bot_count(target_id)}\n"
            f"{DIV2}\n"
            f"📆 Joined      : {fmt_time(u.get('first_seen',0))}\n"
            f"🕐 Last Seen   : {fmt_time(u.get('last_seen',0))}\n"
            f"{DIV}\n"
            f"🤖 BOTS ({len(bots)}):\n"
        )
        for b in bots[:10]: result += f"  {b}\n"
        return result, pfp

    def my_bots(self, uid):
        uid   = safe_int(uid)
        db    = self._bots_db(uid)
        found = 0
        lines = [
            f"╭━━━〔 🤖 <b>YOUR BOTS</b> 〕━━━╮",
            f"┃├ 📊 Slots: <b>{self.bot_count(uid)}/{self.effective_limit(uid)}</b>",
            f"╰{'━'*26}╯\n",
        ]
        for kk, info in db.items():
            if safe_int(info.get("owner_id", 0)) != uid: continue
            found += 1
            running = kk in self.runners and self.runners[kk].proc and self.runners[kk].proc.poll() is None
            st  = "🟢 <b>RUNNING</b>" if running else "🔴 <i>STOPPED</i>"
            ut  = ""
            if running:
                r  = self.runners[kk]
                ut = f"\n┃├ ⏱️ Uptime    : {uptime_str(now_ts() - r.started_at)}  🔁 {r.restarts}x"
            lines.append(
                f"╭━━━〔 {found}. 🤖 <b>{info.get('name','bot')}</b> 〕━━━╮\n"
                f"┃├ 📛 Username  : @{info.get('bot_username','-')}\n"
                f"┃├ 📶 Status    : {st}{ut}\n"
                f"┃├ 🆔 Bot ID    : <code>{info.get('bot_id','-')}</code>\n"
                f"╰{'━'*28}╯"
            )
        if not found:
            lines.append(
                "╭━━━〔 📭 NO BOTS YET 〕━━━╮\n"
                "┃├ .py ya .zip file bhejo yahan!\n"
                "╰━━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
        lines += [f"\n{'━'*28}", f"📊 Total: <b>{found}</b> bot(s)"]
        return "\n".join(lines)

    def mystatus(self, uid):
        uid  = safe_int(uid)
        u    = self._get_u(uid) or {}
        prem = "✅ <b>Premium Active</b>" if self.is_premium(uid) else "🔓 <i>Free Plan</i>"
        role = "👑 <b>Super Admin</b>" if self.is_super(uid) else ("🛡️ <b>Admin</b>" if self.is_admin(uid) else "👤 <i>User</i>")
        name = f"{u.get('first_name','')} {u.get('last_name','')}".strip() or "—"
        return (
            f"╭━━━〔 📊 <b>MY STATUS</b> 〕━━━╮\n"
            f"┃├ 🆔 ID       : <code>{uid}</code>\n"
            f"┃├ 🎭 Role     : {role}\n"
            f"╰{'━'*26}╯\n\n"

            f"╭━━━〔 👤 <b>PROFILE</b> 〕━━━╮\n"
            f"┃├ 🏷️  Name     : {name}\n"
            f"┃├ 📛 Username : @{u.get('username','-')}\n"
            f"┃├ 🌐 Language : {u.get('language_code','N/A')}\n"
            f"╰{'━'*26}╯\n\n"

            f"╭━━━〔 💎 <b>PLAN INFO</b> 〕━━━╮\n"
            f"┃├ 💳 Plan      : {prem}\n"
            f"┃├ 📅 Expires   : {self.premium_exp(uid)}\n"
            f"┃├ ⏳ Days Left : <b>{self.days_left(uid)} days</b>\n"
            f"┃├ 🤖 Bots Used : {self.bot_count(uid)} / {self.effective_limit(uid)}\n"
            f"╰{'━'*26}╯\n\n"

            f"╭━━━〔 📈 <b>ACTIVITY</b> 〕━━━╮\n"
            f"┃├ 📤 Uploads   : {u.get('total_uploads',0)}\n"
            f"┃├ 💬 Messages  : {u.get('total_messages',0)}\n"
            f"┃├ ⚠️  Warnings : {u.get('warning_count',0)} / 3\n"
            f"┃├ 👥 Referrals : {u.get('referral_count',0)} users\n"
            f"╰{'━'*26}╯\n\n"

            f"╭━━━〔 🕐 <b>TIMELINE</b> 〕━━━╮\n"
            f"┃├ 📆 Joined    : {fmt_time(u.get('first_seen',0))}\n"
            f"┃├ 🟢 Last Seen : {fmt_time(u.get('last_seen',0))}\n"
            f"╰{'━'*26}╯"
        )

    def myplan(self, uid):
        uid = safe_int(uid)
        u   = self._get_u(uid) or {}
        if not self.is_premium(uid):
            return f"❌ Koi active plan nahi hai.\n\n{self.plan_text()}"
        days = safe_int(u.get("premium_days", 0))
        lim  = self.effective_limit(uid)
        return (
            f"╭━━━〔 💎 <b>MY ACTIVE PLAN</b> 〕━━━╮\n"
            f"┃├ 📦 Plan      : <b>{days} Days Premium</b>\n"
            f"┃├ 🤖 Bot Slots : {lim} bots\n"
            f"┃├ 💰 Price     : ₹{PLANS.get(days,'N/A')}\n"
            f"┃├ 📅 Expires   : {self.premium_exp(uid)}\n"
            f"┃├ ⏳ Days Left : <b>{self.days_left(uid)} days</b>\n"
            f"╰{'━'*28}╯\n\n"
            f"{'━'*28}\n"
            f"📋 /plan   — Doosre plans dekho\n"
            f"🔄 /buy &lt;d&gt; — Renew karo\n"
            f"🎟️ /redeem — Coupon use karo"
        )

    def botinfo(self, uid, name):
        uid  = safe_int(uid)
        name = safe_name(name)
        kk   = bot_key(uid, name)
        info = self._bots_db(uid).get(kk)
        if not info: return f"❌ Bot '{name}' nahi mila.\n/bots se list dekho."
        running = kk in self.runners and self.runners[kk].proc and self.runners[kk].proc.poll() is None
        r   = self.runners.get(kk)
        st  = "🟢 RUNNING" if running else "🔴 STOPPED"
        ut  = uptime_str(now_ts() - r.started_at) if running and r else "N/A"
        tot = uptime_str((r.total_uptime + (now_ts() - r.started_at)) if running else (r.total_uptime if r else 0))
        return (
            f"╭━━━〔 📌 <b>BOT INFO</b> 〕━━━╮\n"
            f"┃├ 🤖 Name      : <b>{name}</b>\n"
            f"┃├ 📛 Username  : @{info.get('bot_username','-')}\n"
            f"┃├ 🆔 Bot ID    : <code>{info.get('bot_id','-')}</code>\n"
            f"┃├ 📝 Display   : {info.get('bot_display_name','-')}\n"
            f"┃├ 📁 File      : {info.get('entrypoint','-')}\n"
            f"╰{'━'*26}╯\n\n"
            f"╭━━━〔 📊 <b>RUNTIME</b> 〕━━━╮\n"
            f"┃├ 📶 Status    : {st}\n"
            f"┃├ ⏱️ Session   : {ut}\n"
            f"┃├ ⏱️ Total Up  : {tot}\n"
            f"┃├ 🔁 Restarts  : {r.restarts if r else 0}\n"
            f"┃├ 📅 Added     : {fmt_time(info.get('created_at',0))}\n"
            f"╰{'━'*26}╯\n\n"
            f"⚡ /on {name}  ┃  /stop {name}\n"
            f"  /restart {name}  |  /delete {name}\n"
            f"  /logs {name}"
        )

    def send_logs(self, cid, oid, name):
        lp = log_path(safe_int(oid), safe_name(name))
        if not os.path.exists(lp):
            send(cid, f"📭 '{name}' ke koi logs nahi hain.")
            return
        txt = read_tail(lp, 150)
        if not txt.strip():
            send(cid, f"📭 '{name}' ke logs empty hain.")
            return
        send(cid,
            f"📄 LOGS — {name}\n{DIV}\n"
            f"👤 Owner: {oid}\n"
            f"{DIV}\n"
            f"{clip(txt, 3000)}"
        )

    def clear_logs(self, oid, name):
        lp = log_path(safe_int(oid), safe_name(name))
        if os.path.exists(lp):
            open(lp, "w").close()
            return f"✅ Logs cleared: {name}"
        return "❌ Log file nahi mili."

    # ── Admin views ──
    def stats(self):
        running = sum(1 for r in self.runners.values() if r.proc and r.proc.poll() is None)
        total_u = len([x for x in self.users_db if is_valid_uid(x) and safe_int(x) not in ADMIN_IDS])
        prem_u  = sum(1 for x in self.users_db if is_valid_uid(x) and self.is_premium(safe_int(x)) and safe_int(x) not in ADMIN_IDS)
        banned  = len(self.banned_db)
        maint   = "🔴 ON" if self.is_maintenance() else "🟢 OFF"
        active_today = sum(1 for uid_str, u in self.users_db.items()
                          if is_valid_uid(uid_str)
                          and now_ts() - safe_int(u.get("last_seen", 0)) < 86400
                          and safe_int(uid_str) not in ADMIN_IDS)
        total_rev = sum(
            safe_int(r.get("price", 0))
            for uid_str, u in self.users_db.items()
            if is_valid_uid(uid_str)
            for r in u.get("pay_requests", [])
            if r.get("status") == "APPROVED"
        )
        disk_used, disk_total, disk_free, disk_pct = get_disk_usage()
        load, mem = get_system_stats()
        return (
            f"╭━━━〔 📊 <b>{BOT_NAME} v5.0 — STATS</b> 〕━━━╮\n"
            f"┃├ 👥 Total Users    : <b>{total_u}</b>\n"
            f"┃├ 💎 Premium Users  : {prem_u}\n"
            f"┃├ 🕐 Active Today   : {active_today}\n"
            f"┃├ 🚫 Banned         : {banned}\n"
            f"┃├ 🛡️ Admins        : {len(ADMIN_IDS)}\n"
            f"╰{'━'*32}╯\n\n"

            f"╭━━━〔 🤖 <b>BOT STATS</b> 〕━━━╮\n"
            f"┃├ 🤖 User Bots (DB) : {len(self.bots_users)}\n"
            f"┃├ 👑 Admin Bots(DB) : {len(self.bots_admin)}\n"
            f"┃├ 🟢 Running Now    : <b>{running}</b>\n"
            f"┃├ 📤 Uploads        : {self.upload_count}\n"
            f"┃├ 🎟️ Coupons       : {len(self.coupons)}\n"
            f"╰{'━'*32}╯\n\n"

            f"╭━━━〔 💬 <b>ACTIVITY</b> 〕━━━╮\n"
            f"┃├ 💬 Messages       : {self.msg_count}\n"
            f"┃├ ⚡ Commands       : {self.cmd_count}\n"
            f"┃├ 💰 Total Revenue  : ₹{total_rev}\n"
            f"╰{'━'*32}╯\n\n"

            f"╭━━━〔 💻 <b>SERVER</b> 〕━━━╮\n"
            f"┃├ ⏱️ Uptime         : {uptime_str(now_ts() - self.start_time)}\n"
            f"┃├ 🔧 Maintenance    : {maint}\n"
            f"┃├ 🖼️ QR Set         : {'✅' if self.get_qr() else '❌'}\n"
            f"┃├ 🐍 Python         : {sys.version.split()[0]}\n"
            f"┃├ 🧠 Memory         : {mem}\n"
            f"┃├ 💾 Disk           : {disk_used}/{disk_total} ({disk_pct})\n"
            f"┃├ 📊 CPU Load       : {load}\n"
            f"╰{'━'*32}╯"
        )

    def system_info(self):
        disk_used, disk_total, disk_free, disk_pct = get_disk_usage()
        load, mem = get_system_stats()
        cpu = get_cpu_info()
        bot_data_size = "N/A"
        try:
            total_b = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, dn, fn in os.walk(BASE_DIR) for f in fn
            )
            bot_data_size = fmt_size(total_b)
        except: pass
        # Check available runtimes
        runtimes = []
        for rt in ["python3","node","go","ruby","php","bash","java","perl","lua"]:
            try:
                r = subprocess.run(["which", rt], capture_output=True, timeout=3)
                if r.returncode == 0:
                    runtimes.append(rt)
            except: pass
        return (
            f"╭━━━〔 💻 <b>SYSTEM INFO</b> 〕━━━╮\n"
            f"┃├ 🐍 Python     : {sys.version.split()[0]}\n"
            f"┃├ 💻 Platform   : {sys.platform}\n"
            f"┃├ 🖥️ CPU        : {cpu}\n"
            f"┃├ 📊 CPU Load   : {load}\n"
            f"┃├ 🧠 Memory     : {mem}\n"
            f"┃├ 💾 Disk       : {disk_used} / {disk_total} ({disk_pct})\n"
            f"┃├ 🆓 Free Disk  : {disk_free}\n"
            f"┃├ 📁 Data Dir   : {BASE_DIR}\n"
            f"┃├ 📦 Data Size  : {bot_data_size}\n"
            f"┃├ ⏱️ Uptime     : {uptime_str(now_ts() - self.start_time)}\n"
            f"┃├ 📅 Started    : {fmt_time(self.start_time)}\n"
            f"╰{'━'*30}╯\n\n"
            f"╭━━━〔 🌐 <b>RUNTIMES AVAILABLE</b> 〕━━━╮\n"
            + "\n".join(f"┃├ ✅ {rt}" for rt in runtimes) + "\n"
            f"╰{'━'*32}╯"
        )

    def running_bots(self):
        count = 0
        lines = [
            f"╭━━━〔 🟢 <b>RUNNING BOTS</b> 〕━━━╮",
        ]
        for kk, r in list(self.runners.items()):
            if r.proc and r.proc.poll() is None:
                count += 1
                info = self.bots_users.get(kk) or self.bots_admin.get(kk) or {}
                lang = get_lang(r.bot_file)
                lines.append(
                    f"┃├ {count}. {lang['emoji']} <b>{info.get('name', kk)}</b>\n"
                    f"┃├    📛 @{info.get('bot_username','-')}\n"
                    f"┃├    👤 Owner  : {info.get('owner_id','?')}\n"
                    f"┃├    ⏱️ Uptime : {uptime_str(now_ts() - r.started_at)}\n"
                    f"┃├    🔁 Restarts: {r.restarts}"
                )
        if not count:
            lines.append("┃├ 📭 Koi bot nahi chal raha.")
        lines.append(f"┃├ 📊 Total Running : <b>{count}</b>")
        lines.append(f"╰{'━'*30}╯")
        return "\n".join(lines)

    def users_text(self):
        # FIX: Filter out non-numeric keys like 'HHAB'
        users = [
            (safe_int(uid), u)
            for uid, u in self.users_db.items()
            if is_valid_uid(uid) and safe_int(uid) not in ADMIN_IDS
        ]
        users.sort(key=lambda x: safe_int(x[1].get("last_seen", 0)), reverse=True)
        lines = [f"👥 ALL USERS ({len(users)})", DIV, ""]
        for uid, u in users[:MAX_USER_LIST]:
            p = "💎" if self.is_premium(uid) else "  "
            b = "🚫" if self.is_banned(uid)   else "  "
            w = "⚠️" if safe_int(u.get("warning_count", 0)) > 0 else "  "
            lines.append(
                f"{p}{b}{w} {uid} | @{u.get('username','-'):15} | "
                f"{u.get('first_name','')[:12]} | 🤖{self.bot_count(uid)}"
            )
        lines += [DIV, f"Total: {len(users)} users"]
        return "\n".join(lines)

    def active_users(self):
        # FIX: Safe int conversion
        users = [
            (safe_int(uid), u)
            for uid, u in self.users_db.items()
            if is_valid_uid(uid)
            and safe_int(uid) not in ADMIN_IDS
            and now_ts() - safe_int(u.get("last_seen", 0)) < 86400
        ]
        users.sort(key=lambda x: safe_int(x[1].get("last_seen", 0)), reverse=True)
        lines = [f"🕐 ACTIVE TODAY ({len(users)})", DIV, ""]
        for uid, u in users[:50]:
            lines.append(
                f"  {uid} | @{u.get('username','-'):12} | "
                f"{u.get('first_name','')[:10]} | {fmt_time(safe_int(u.get('last_seen',0)))}"
            )
        if not users: lines.append("📭 Koi active user nahi.")
        return "\n".join(lines)

    def premium_users(self):
        # FIX: Safe int conversion
        users = [
            (safe_int(uid), u)
            for uid, u in self.users_db.items()
            if is_valid_uid(uid)
            and safe_int(uid) not in ADMIN_IDS
            and self.is_premium(safe_int(uid))
        ]
        users.sort(key=lambda x: safe_int(x[1].get("premium_expires", 0)), reverse=True)
        lines = [f"💎 PREMIUM USERS ({len(users)})", DIV, ""]
        for uid, u in users:
            days = self.days_left(uid)
            lines.append(
                f"  💎 {uid} | @{u.get('username','-'):12} | "
                f"{u.get('first_name','')[:10]} | {days}d left"
            )
        if not users: lines.append("📭 Koi premium user nahi.")
        return "\n".join(lines)

    def userinfo(self, uid):
        uid = safe_int(uid)
        if not is_valid_uid(uid): return "❌ Invalid user ID."
        u = self.users_db.get(str(uid))
        if not u: return "❌ User nahi mila."
        return (
            f"🧾 USER INFO\n{DIV}\n"
            f"🆔 ID        : {uid}\n"
            f"👤 Name      : {u.get('first_name','')} {u.get('last_name','')}\n"
            f"📛 Username  : @{u.get('username','-')}\n"
            f"🌐 Language  : {u.get('language_code','N/A')}\n"
            f"{DIV2}\n"
            f"💎 Premium   : {'✅ Yes' if self.is_premium(uid) else '❌ No'}\n"
            f"📅 Expires   : {self.premium_exp(uid)}\n"
            f"📆 Days Left : {self.days_left(uid)}\n"
            f"🤖 Bot Limit : {self.effective_limit(uid)}\n"
            f"🔢 Active    : {self.bot_count(uid)}\n"
            f"📤 Uploads   : {u.get('total_uploads',0)}\n"
            f"💬 Messages  : {u.get('total_messages',0)}\n"
            f"🚫 Banned    : {'Yes ❌' if self.is_banned(uid) else 'No ✅'}\n"
            f"⚠️ Warnings  : {u.get('warning_count',0)}/3\n"
            f"📝 Notes     : {u.get('notes','—')}\n"
            f"👥 Referrals : {u.get('referral_count',0)}\n"
            f"{DIV2}\n"
            f"📆 Joined    : {fmt_time(safe_int(u.get('first_seen',0)))}\n"
            f"🕐 Last seen : {fmt_time(safe_int(u.get('last_seen',0)))}\n"
            f"{DIV}\n"
            f"/fulluserinfo {uid} — Full info with photo"
        )

    def allbots_text(self):
        lines = [f"🤖 ALL BOTS", DIV, ""]
        count = 0
        for db, label in [(self.bots_users, "USER"), (self.bots_admin, "ADMIN")]:
            for kk, info in db.items():
                count += 1
                st = "🟢" if (kk in self.runners and self.runners[kk].proc and self.runners[kk].proc.poll() is None) else "🔴"
                lines.append(
                    f"{count}) [{label}] {st} {info.get('name','')}\n"
                    f"    📛 @{info.get('bot_username','-')} | 👤 {info.get('owner_id','')}\n"
                    f"    📁 {info.get('entrypoint','-')}\n"
                )
                if count >= MAX_ALLBOTS_LIST: break
        if not count: lines.append("📭 Koi bot nahi.")
        lines += [DIV, f"Total: {count} bots"]
        return "\n".join(lines)

    def alllogs(self):
        running = [kk for kk, r in self.runners.items() if r.proc and r.proc.poll() is None]
        lines   = [f"📄 ALL LOGS (Running: {len(running)})", DIV, ""]
        for kk in running[:8]:
            info = self.bots_users.get(kk) or self.bots_admin.get(kk) or {}
            lines.append(f"🤖 {info.get('name','')} | 👤 {info.get('owner_id','')}")
            tail = read_tail(log_path(info.get('owner_id', '?'), info.get('name', 'bot')), 20)
            lines.append(tail or "(no logs)")
            lines.append(DIV2)
        if not running: lines.append("📭 Koi running bot nahi.")
        return "\n".join(lines)

    def broadcast(self, text, premium_only=False):
        if not text.strip(): return "Usage: /broadcast <text>"
        sent = failed = 0
        for uid_str in self.users_db:
            if not is_valid_uid(uid_str): continue
            uid = safe_int(uid_str)
            if uid in ADMIN_IDS or self.is_banned(uid): continue
            if premium_only and not self.is_premium(uid): continue
            if send(uid, text).get("ok"): sent += 1
            else: failed += 1
        target = "Premium users" if premium_only else "All users"
        return (
            f"📢 BROADCAST DONE\n{DIV}\n"
            f"🎯 Target  : {target}\n"
            f"✅ Sent    : {sent}\n"
            f"❌ Failed  : {failed}\n"
            f"📊 Total   : {sent + failed}\n{DIV}"
        )

    def del_all_user_bots(self, aid):
        if not self.is_admin(aid): return "❌ Admin only."
        stopped = 0
        for kk in list(self.runners.keys()):
            if kk in self.bots_users:
                self.runners[kk].stop()
                self.runners.pop(kk, None)
                stopped += 1
        rm_tree(BOTS_USERS_DIR)
        self.bots_users = {}
        save_json(BOTS_USERS_FILE, {})
        return f"🗑️ Sabhi user bots delete ho gaye. ({stopped} stopped)"

    def del_all_bots(self, aid):
        if not self.is_admin(aid): return "❌ Admin only."
        count = len(self.runners)
        for kk in list(self.runners.keys()):
            self.runners[kk].stop()
            self.runners.pop(kk, None)
        rm_tree(BOTS_USERS_DIR)
        rm_tree(BOTS_ADMIN_DIR)
        self.bots_users = {}
        self.bots_admin = {}
        save_json(BOTS_USERS_FILE, {})
        save_json(BOTS_ADMIN_FILE, {})
        return f"🗑️ SABHI {count} bots delete ho gaye."

    def usergivebot(self, aid, tuid, bl, days):
        tuid = safe_int(tuid)
        bl   = safe_int(bl)
        days = safe_int(days)
        u    = self._get_u(tuid) or {}
        exp  = now_ts() + days * 86400
        u.update({"premium_expires": exp, "premium_days": days, "limit_override": bl, "limit_expires": exp})
        self._save_u(tuid, u)

    def reset_all_credits(self):
        for uid_str in list(self.users_db.keys()):
            if not is_valid_uid(uid_str): continue
            if safe_int(uid_str) in ADMIN_IDS: continue
            u = self.users_db[uid_str]
            u.update({"premium_expires": 0, "premium_days": 0, "limit_override": None, "limit_expires": 0})
        save_json(USERS_FILE, self.users_db)
        return "✅ Sabhi users ka credit reset kar diya."

    def all_user_give(self, bl, days):
        bl   = safe_int(bl)
        days = safe_int(days)
        exp  = now_ts() + days * 86400
        count = 0
        for uid_str in list(self.users_db.keys()):
            if not is_valid_uid(uid_str): continue
            if safe_int(uid_str) in ADMIN_IDS: continue
            u = self.users_db[uid_str]
            u.update({"premium_expires": exp, "premium_days": days, "limit_override": bl, "limit_expires": exp})
            count += 1
        save_json(USERS_FILE, self.users_db)
        return f"✅ {count} users ko {bl} bots {days} days ke liye de diya."

    def admin_bots(self):
        lines = [f"👑 ADMIN BOTS", DIV, ""]
        i = 0
        for kk, info in self.bots_admin.items():
            if safe_int(info.get("owner_id", 0)) not in ADMIN_IDS: continue
            i += 1
            st = "🟢" if (kk in self.runners and self.runners[kk].proc and self.runners[kk].proc.poll() is None) else "🔴"
            lines.append(
                f"{i}) {st} {info.get('name','')}\n"
                f"   📛 @{info.get('bot_username','-')} | 👤 {info.get('owner_id','')}"
            )
        if not i: lines.append("📭 Koi admin bot nahi.")
        return "\n".join(lines)

    def referral_info(self, uid):
        uid       = safe_int(uid)
        u         = self._get_u(uid) or {}
        ref_count = u.get("referral_count", 0)
        ref_link  = f"https://t.me/{BOT_NAME}bot?start=ref{uid}"
        return (
            f"🔗 REFERRAL INFO\n{DIV}\n"
            f"👥 Your Referrals : {ref_count} users\n"
            f"🎁 Bonus per ref  : {REFERRAL_BONUS_DAYS} days\n"
            f"🏆 Total Bonus    : {ref_count * REFERRAL_BONUS_DAYS} days\n"
            f"🔗 Referred By    : {u.get('referred_by','None')}\n"
            f"{DIV}\n"
            f"📲 Your Referral Link:\n{ref_link}\n"
            f"{DIV}\n"
            f"💡 Share karo aur free premium days pao!\n"
            f"  {DOT} Har referral = {REFERRAL_BONUS_DAYS} din free\n"
            f"  {DOT} Unlimited referrals"
        )

    # ════════════════════════════════════════
    #   UPLOAD PROCESSOR — Multi-language
    # ════════════════════════════════════════
    # ── Live boot progress bar helper (edit-in-place, no message flood) ──
    def _boot_progress(self, cid, step, total=6, label="", mid=None):
        filled = int((step / total) * 10)
        bar    = "█" * filled + "░" * (10 - filled)
        pct    = int(step / total * 100)
        txt = (
            f"╭━━━〔 🚀 <b>BOOTING</b> 〕━━━╮\n"
            f"┃├ [{bar}] {pct}%\n"
            f"┃├ {label}\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        if mid:
            tg(HOST_TOKEN, "editMessageText", {
                "chat_id": cid, "message_id": mid,
                "text": txt, "parse_mode": "HTML"
            })
            return mid
        else:
            r = sendh(cid, txt)
            return (r.get("result") or {}).get("message_id") if r and r.get("ok") else None

    def _check_syntax(self, fpath):
        """Check syntax for any supported language. Returns (ok, error_text)."""
        ext = os.path.splitext(fpath)[1].lower()
        try:
            if ext == ".py":
                p = subprocess.run([PYTHON_BIN, "-m", "py_compile", fpath],
                                   capture_output=True, text=True, timeout=10)
                return p.returncode == 0, (p.stderr or p.stdout or "")
            elif ext in (".js", ".mjs", ".cjs"):
                p = subprocess.run(["node", "--check", fpath],
                                   capture_output=True, text=True, timeout=10)
                return p.returncode == 0, (p.stderr or p.stdout or "")
            elif ext == ".sh":
                p = subprocess.run(["bash", "-n", fpath],
                                   capture_output=True, text=True, timeout=10)
                return p.returncode == 0, (p.stderr or p.stdout or "")
            elif ext == ".php":
                p = subprocess.run(["php", "-l", fpath],
                                   capture_output=True, text=True, timeout=10)
                return p.returncode == 0, (p.stderr or p.stdout or "")
            elif ext == ".rb":
                p = subprocess.run(["ruby", "-c", fpath],
                                   capture_output=True, text=True, timeout=10)
                return p.returncode == 0, (p.stderr or p.stdout or "")
            # Go, Java, Lua etc. — no quick syntax check, assume ok
            return True, ""
        except FileNotFoundError:
            return True, ""   # runtime not found — let it try
        except Exception as e:
            return False, str(e)

    def _auto_fix_and_check(self, cid, fpath, lang_name):
        """Try to auto-fix, check syntax, report error in code block. Returns ok bool."""
        ok, err = self._check_syntax(fpath)
        if ok: return True
        send_html(cid,
            f"╭━━━〔 ⚠️ <b>SYNTAX ERROR</b> 〕━━━╮\n"
            f"┃├ 🔧 Auto-fix try kar raha hoon...\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        # Auto-fix (encoding, BOM, line endings)
        auto_fix(fpath)
        ok2, err2 = self._check_syntax(fpath)
        if ok2: return True
        final_err = clip(err2 or err, 2000)
        send_html(cid,
            f"╭━━━〔 ❌ <b>{lang_name.upper()} ERROR</b> 〕━━━╮\n"
            f"┃├ 📁 File mein yeh errors hain:\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯\n\n"
            f"<code>{final_err}</code>\n\n"
            f"╭━━━〔 💡 <b>FIX KARO</b> 〕━━━╮\n"
            f"┃├ Upar wali errors fix karo\n"
            f"┃├ Phir dobara upload karo\n"
            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
        )
        return False

    def _install_deps_for_lang(self, fpath, work_dir, deps_dir):
        """Install dependencies based on manifest files (requirements.txt, package.json, etc.)."""
        ext = os.path.splitext(fpath)[1].lower()
        req = os.path.join(work_dir, "requirements.txt")
        pkg = os.path.join(work_dir, "package.json")
        gom = os.path.join(work_dir, "go.mod")
        gem = os.path.join(work_dir, "Gemfile")
        try:
            if os.path.exists(req):
                subprocess.run([PYTHON_BIN, "-m", "pip", "install", "-q", "-t", deps_dir, "-r", req],
                               capture_output=True, timeout=180)
            if os.path.exists(pkg) and ext in (".js",".ts",".mjs",".cjs"):
                subprocess.run(["npm", "install", "--prefix", work_dir, "--silent"],
                               capture_output=True, timeout=180)
            if os.path.exists(gom):
                subprocess.run(["go", "mod", "download"], capture_output=True,
                               timeout=180, cwd=work_dir)
            if os.path.exists(gem):
                subprocess.run(["bundle", "install", "--path", deps_dir],
                               capture_output=True, timeout=180, cwd=work_dir)
        except: pass

    def process_upload(self, cid, u, doc, caption=""):
        uid   = safe_int(u.get("id", 0))
        fname = doc.get("file_name", "file")
        fid   = doc.get("file_id")
        size  = safe_int(doc.get("file_size", 0))
        ext   = os.path.splitext(fname)[1].lower()
        bname = safe_name(os.path.splitext(fname)[0])
        try:
            self.upload_count += 1
            if size > MAX_FILE_SIZE_BYTES:
                send_html(cid,
                    f"╭━━━〔 ❌ <b>FILE TOO LARGE</b> 〕━━━╮\n"
                    f"┃├ 📦 Max Size  : {fmt_size(MAX_FILE_SIZE_BYTES)}\n"
                    f"┃├ 📤 Your File : {fmt_size(size)}\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                )
                return
            if not self.is_admin(uid) and self.bot_count(uid) >= self.effective_limit(uid):
                self.credit_ended(cid, uid); return

            # ── Step 1: Download (first progress message — all later edits use same msg) ──
            mid = self._boot_progress(cid, 1, label="⬇️ File download ho rahi hai...")
            fp = get_fpath(fid)
            if not fp:
                send_html(cid, "╭━━━〔 ❌ 〕━━━╮\n┃├ Download link nahi mila.\n╰━━━━━━━━━━━━╯"); return

            base = self._bots_dir(uid)
            udir = os.path.join(base, str(uid), bname)
            os.makedirs(udir, exist_ok=True)
            self.stop_bot(uid, bname, delete=False)

            # ── Single file upload (any language) ──
            if ext in BOT_EXTS:
                lang_info = get_lang(fname)
                lang_name = lang_info["name"]
                lang_emoji = lang_info["emoji"]

                # ── Runtime availability check ──
                runtime_bin = lang_info["cmd"][0]
                if runtime_bin not in (PYTHON_BIN, "python3", "python"):
                    import shutil
                    if not shutil.which(runtime_bin):
                        send_html(cid,
                            f"╭━━━〔 ❌ <b>RUNTIME NOT FOUND</b> 〕━━━╮\n"
                            f"┃├ {lang_emoji} <b>{lang_name}</b> install nahi hai\n"
                            f"┃├ 🔧 Runtime: <code>{runtime_bin}</code>\n"
                            f"┃├\n"
                            f"┃├ 💡 <b>Solution:</b>\n"
                            f"┃├ Python bots fully supported hain.\n"
                            f"┃├ {lang_name} bots ke liye server par\n"
                            f"┃├ <code>{runtime_bin}</code> install karna hoga.\n"
                            f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                        )
                        return

                save_to = os.path.join(udir, fname)
                if not dl_file(fp, save_to):
                    send_html(cid,
                        f"╭━━━〔 ❌ <b>DOWNLOAD FAILED</b> 〕━━━╮\n"
                        f"┃├ Network error. Dobara try karo.\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                    return

                # ── Step 2: Encode fix ──
                mid = self._boot_progress(cid, 2, label=f"{lang_emoji} {lang_name} file verify kar raha hoon...", mid=mid)
                enc = detect_encoding(save_to)

                # ── Step 3: Syntax check ──
                mid = self._boot_progress(cid, 3, label="🔍 Syntax check ho raha hai...", mid=mid)
                if not self._auto_fix_and_check(cid, save_to, lang_name):
                    return

                # ── Step 4: Token extract ──
                mid = self._boot_progress(cid, 4, label="🔑 Bot token dhundh raha hoon...", mid=mid)
                tok = extract_token(save_to)
                if not tok:
                    # Try .env in same dir
                    env_f = os.path.join(udir, ".env")
                    if os.path.exists(env_f): tok = extract_token(env_f)
                if not tok:
                    u_db = self._get_u(uid) or {}
                    pend = u_db.get("pending_token", {})
                    pend[bname] = save_to
                    u_db["pending_token"] = pend
                    self._save_u(uid, u_db)
                    send_html(cid,
                        f"╭━━━〔 ⚠️ <b>TOKEN NAHI MILA</b> 〕━━━╮\n"
                        f"┃├ {lang_emoji} Language : {lang_name}\n"
                        f"┃├ 📁 File     : {fname}\n"
                        f"┃├\n"
                        f"┃├ <b>File mein token hardcode karo:</b>\n"
                        f"┃├ 🐍 Python: <code>BOT_TOKEN = \"1234:ABCdef\"</code>\n"
                        f"┃├ 🟩 Node  : <code>const TOKEN = \"1234:ABCdef\"</code>\n"
                        f"┃├ 🔵 Go    : <code>token := \"1234:ABCdef\"</code>\n"
                        f"┃├ 💎 Ruby  : <code>TOKEN = \"1234:ABCdef\"</code>\n"
                        f"┃├ 📄 .env  : <code>BOT_TOKEN=1234:ABCdef</code>\n"
                        f"┃├\n"
                        f"┃├ 📌 Ya /save command se token set karo:\n"
                        f"┃├ <code>/save 1234567890:ABCdef...</code>\n"
                        f"┃├\n"
                        f"┃├ 🔗 Token lene ke liye: @BotFather\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                    return

                # ── Step 5: Install deps ──
                mid = self._boot_progress(cid, 5, label="📦 Dependencies install ho rahi hain...", mid=mid)
                deps = os.path.join(DEPS_DIR, str(uid), bname)
                os.makedirs(deps, exist_ok=True)
                self._install_deps_for_lang(save_to, udir, deps)

                # ── Step 6: Start bot ──
                mid = self._boot_progress(cid, 6, label="🚀 Bot launch ho raha hai!", mid=mid)
                bid, buser, bdname = self.detect_bot(tok)
                u_db = self._get_u(uid) or {}
                u_db["total_uploads"] = u_db.get("total_uploads", 0) + 1
                self._save_u(uid, u_db)
                pfp = get_pfp(uid)
                notify_admins(
                    f"╭━━━〔 📥 <b>NEW BOT UPLOADED</b> 〕━━━╮\n"
                    f"┃├ 👤 User     : {uid} @{u.get('username','-')}\n"
                    f"┃├    Name     : {u.get('first_name','')}\n"
                    f"┃├    Plan     : {'💎 Premium' if self.is_premium(uid) else '🆓 Free'}\n"
                    f"┃├ {lang_emoji} Language  : {lang_name}\n"
                    f"┃├ 📁 File     : {fname} ({fmt_size(size)})\n"
                    f"┃├ 🌐 Encoding : {enc}\n"
                    f"┃├ 🤖 Bot      : @{buser or 'N/A'} ({bid or 'N/A'})\n"
                    f"┃├ ⏰ Time     : {fmt_time(now_ts())}\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━╯",
                    pfp
                )
                fwd_file_admins(fid, f"{lang_emoji} {fname} | {uid} @{u.get('username','-')}")
                res = self._start_bot(uid, cid, bname, save_to, udir, deps,
                                      persist=True, bot_id=bid, bot_uname=buser,
                                      bot_dname=bdname, entry_label=fname)
                if not res:
                    send_html(cid,
                        f"╭━━━〔 ✅ <b>BOT STARTING</b> 〕━━━╮\n"
                        f"┃├ {lang_emoji} Language : <b>{lang_name}</b>\n"
                        f"┃├ 🤖 Name    : <b>{bname}</b>\n"
                        f"┃├ 📛 Username: @{buser or 'detecting...'}\n"
                        f"┃├ 🆔 Bot ID  : {bid or 'N/A'}\n"
                        f"┃├ 📁 File    : {fname}\n"
                        f"┃├\n"
                        f"┃├ 🔔 Notification milegi jab start ho jaye!\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                else:
                    send(cid, res)

            elif ext == ".zip":
                # ── ZIP upload ──
                zip_path = os.path.join(udir, f"{bname}.zip")
                exdir    = os.path.join(udir, "project")
                rm_tree(exdir)
                os.makedirs(exdir, exist_ok=True)
                if not dl_file(fp, zip_path):
                    send_html(cid,
                        f"╭━━━〔 ❌ 〕━━━╮\n┃├ ZIP download failed. Dobara try karo.\n╰━━━━━━━━━━━━╯"
                    ); return
                try:
                    with zipfile.ZipFile(zip_path) as z: z.extractall(exdir)
                except zipfile.BadZipFile:
                    send_html(cid,
                        f"╭━━━〔 ❌ <b>INVALID ZIP</b> 〕━━━╮\n"
                        f"┃├ File corrupt hai ya valid ZIP nahi hai.\n"
                        f"┃├ Dobara ZIP banao aur upload karo.\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                    ); return
                except Exception as e:
                    send_html(cid, f"╭━━━〔 ❌ 〕━━━╮\n┃├ ZIP error:\n┃├ <code>{clip(str(e),300)}</code>\n╰━━━━━━━╯"); return

                # ── Step 2: Find entry file (any language) ──
                mid = self._boot_progress(cid, 2, label="🔍 Entry file dhundh raha hoon...", mid=mid)
                entry, tok = choose_entry(exdir)
                if not entry:
                    send_html(cid,
                        f"╭━━━〔 ❌ <b>NO ENTRY FILE FOUND</b> 〕━━━╮\n"
                        f"┃├ ZIP mein koi supported file nahi mili.\n"
                        f"┃├\n"
                        f"┃├ <b>Supported extensions:</b>\n"
                        f"┃├ <code>.py .js .ts .go .rb .php .sh</code>\n"
                        f"┃├ <code>.pl .java .lua .mjs .cjs</code>\n"
                        f"┃├\n"
                        f"┃├ Sahi file ZIP mein rakh ke dobara upload karo.\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                    return

                lang_info  = get_lang(entry)
                lang_name  = lang_info["name"]
                lang_emoji = lang_info["emoji"]

                # ── Step 3: Syntax check ──
                mid = self._boot_progress(cid, 3, label=f"{lang_emoji} {lang_name} syntax check ho raha hai...", mid=mid)
                if not self._auto_fix_and_check(cid, entry, lang_name):
                    return

                # ── Step 4: Token ──
                mid = self._boot_progress(cid, 4, label="🔑 Bot token dhundh raha hoon...", mid=mid)
                if not tok:
                    env_f = os.path.join(exdir, ".env")
                    if os.path.exists(env_f): tok = extract_token(env_f)
                if not tok:
                    u_db = self._get_u(uid) or {}
                    pend = u_db.get("pending_token", {})
                    pend[bname] = entry
                    u_db["pending_token"] = pend
                    self._save_u(uid, u_db)
                    send_html(cid,
                        f"╭━━━〔 ⚠️ <b>TOKEN NOT FOUND IN ZIP</b> 〕━━━╮\n"
                        f"┃├ {lang_emoji} Language : {lang_name}\n"
                        f"┃├ 📁 Entry    : {os.path.relpath(entry, exdir)}\n"
                        f"┃├\n"
                        f"┃├ File mein token hardcode karo ya:\n"
                        f"┃├ <code>/save 1234567890:ABCdef...</code>\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                    return

                # ── Step 5: Install deps ──
                mid = self._boot_progress(cid, 5, label="📦 Dependencies install ho rahi hain...", mid=mid)
                deps = os.path.join(DEPS_DIR, str(uid), bname)
                os.makedirs(deps, exist_ok=True)
                self._install_deps_for_lang(entry, exdir, deps)

                # ── Step 6: Start ──
                mid = self._boot_progress(cid, 6, label="🚀 Bot launch ho raha hai!", mid=mid)
                bid, buser, bdname = self.detect_bot(tok)
                pfp = get_pfp(uid)
                notify_admins(
                    f"╭━━━〔 📥 <b>NEW BOT UPLOADED (ZIP)</b> 〕━━━╮\n"
                    f"┃├ 👤 User      : {uid} @{u.get('username','-')}\n"
                    f"┃├ {lang_emoji} Language   : {lang_name}\n"
                    f"┃├ 📁 File      : {fname} ({fmt_size(size)})\n"
                    f"┃├ 📂 Entry     : {os.path.relpath(entry, exdir)}\n"
                    f"┃├ 📛 @{buser or 'N/A'} | 🆔 {bid or 'N/A'}\n"
                    f"┃├ ⏰ Time      : {fmt_time(now_ts())}\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━╯",
                    pfp
                )
                fwd_file_admins(fid, f"📦 ZIP {fname} | {uid}")
                res = self._start_bot(uid, cid, bname, entry, exdir, deps,
                                      persist=True, bot_id=bid, bot_uname=buser,
                                      bot_dname=bdname, entry_label=os.path.relpath(entry, exdir))
                if not res:
                    send_html(cid,
                        f"╭━━━〔 ✅ <b>BOT STARTING (ZIP)</b> 〕━━━╮\n"
                        f"┃├ {lang_emoji} Language : <b>{lang_name}</b>\n"
                        f"┃├ 🤖 Name    : <b>{bname}</b>\n"
                        f"┃├ 📛 Username: @{buser or '?'}\n"
                        f"┃├ 📂 Entry   : {os.path.relpath(entry, exdir)}\n"
                        f"┃├\n"
                        f"┃├ 🔔 Notification aayegi jab start ho jaye!\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                else:
                    send(cid, res)
            else:
                supported_str = " • ".join(sorted(BOT_EXTS)) + " • .zip"
                send_html(cid,
                    f"╭━━━〔 ⚠️ <b>UNSUPPORTED FILE</b> 〕━━━╮\n"
                    f"┃├ Extension '<b>{ext or 'unknown'}</b>' support nahi hai.\n"
                    f"┃├\n"
                    f"┃├ <b>Supported file types:</b>\n"
                    f"┃├ <code>.py</code>  — Python\n"
                    f"┃├ <code>.js .ts .mjs</code> — Node.js / TypeScript\n"
                    f"┃├ <code>.go</code>  — Go (Golang)\n"
                    f"┃├ <code>.rb</code>  — Ruby\n"
                    f"┃├ <code>.php</code> — PHP\n"
                    f"┃├ <code>.sh</code>  — Shell Script\n"
                    f"┃├ <code>.lua</code> — Lua\n"
                    f"┃├ <code>.zip</code> — Any language (Project folder)\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                )
        except Exception as e:
            send_html(cid,
                f"╭━━━〔 ❌ <b>UPLOAD ERROR</b> 〕━━━╮\n"
                f"┃├ Kuch gadbad ho gayi:\n"
                f"┃├ <code>{clip(str(e), 500)}</code>\n"
                f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
            )
            print(f"[UPLOAD ERROR] {e}")
            traceback.print_exc()
        finally:
            with self.lock: self.user_busy.discard(uid)

    # ════════════════════════════════════════
    #   COMMAND PARSER
    # ════════════════════════════════════════
    def parse(self, text):
        parts = (text or "").strip().split()
        cmd   = parts[0].split("@")[0].lower() if parts else ""
        return cmd, parts[1:]

    # ════════════════════════════════════════
    #   MAIN HANDLER
    # ════════════════════════════════════════
    def handle(self, msg):
        try:
            cid = (msg.get("chat") or {}).get("id")
            u   = msg.get("from") or {}
            uid = safe_int(u.get("id", 0))
            if not cid or not uid: return

            self.msg_count += 1

            # Anti-spam
            if not self.is_admin(uid) and self.is_spam(uid): return

            text   = (msg.get("text") or "").strip()
            ref_id = None
            if text.startswith("/start"):
                parts = text.split()
                if len(parts) > 1 and parts[1].startswith("ref"):
                    try: ref_id = safe_int(parts[1][3:])
                    except: pass

            self.register(u, ref_id)

            # Banned
            if self.is_banned(uid) and not self.is_admin(uid):
                send(cid, f"🚫 Aap banned hain.\n💬 Appeal: {SUPPORT_LINK}"); return

            # ── Force Join Check ──
            if not self.is_admin(uid):
                not_joined = check_force_join(uid)
                if not_joined:
                    btn_rows = [[ch["name"], ch["link"]] for ch in not_joined]
                    kb = {"inline_keyboard": [[{"text": ch["name"], "url": ch["link"]}] for ch in not_joined]
                          + [[{"text": "✅ Maine Join Kar Liya!", "callback_data": "cb_check_join"}]]}
                    sendh(cid,
                        f"╭━━━〔 ⚠️ <b>JOIN KARO PEHLE</b> 〕━━━╮\n"
                        f"┃├ Bot use karne ke liye\n"
                        f"┃├ neeche wale channels join karo!\n"
                        f"┃├\n"
                        + "".join(f"┃├ ✅ <b>{ch['name']}</b>\n" for ch in not_joined)
                        + f"╰━━━━━━━━━━━━━━━━━━━━━━━━━╯",
                        reply_markup=kb
                    )
                    return

            # Maintenance
            if self.is_maintenance() and not self.is_admin(uid):
                send(cid,
                    f"🔧 MAINTENANCE MODE\n{DIV}\n"
                    f"Bot abhi maintenance par hai.\n"
                    f"⏰ Thodi der mein dobara try karo.\n"
                    f"📢 Updates: {CHANNEL_LINK}"
                ); return

            if not self.allowed(uid) and not self.is_admin(uid):
                send(cid, "❌ Access nahi hai."); return

            ia  = self.is_admin(uid)
            isp = self.is_super(uid)
            doc     = msg.get("document")
            photo   = msg.get("photo")
            caption = (msg.get("caption") or "").strip()
            cmd, args = self.parse(text) if text else ("", [])
            if cmd: self.cmd_count += 1

            # QR pending
            if ia and self.is_qr_pending(uid) and (photo or doc):
                if photo: self.set_qr(photo[-1]["file_id"], uid); return
                if doc:   self.set_qr(doc["file_id"],        uid); return

            # Custom commands
            if cmd:
                cmd_key = cmd.lstrip("/")
                if cmd_key in self.custom_cmds:
                    send(cid, self.custom_cmds[cmd_key]["reply"]); return

            # Auto reply (non-command text)
            if text and not cmd.startswith("/"):
                reply = self.check_autoreply(text)
                if reply: send(cid, reply); return

            # Handle keyboard button presses (reply keyboard text)
            if text and not cmd.startswith("/"):
                if self.handle_keyboard_text(cid, uid, text, ia): return

            # ══ COMMON COMMANDS ══
            if cmd in ("/start", "/help"):
                kb = self.admin_kb() if ia else self.user_kb()
                help_txt = self.help_admin(uid) if ia else self.help_user(uid)
                if cmd == "/start":
                    # Send user photo + short welcome, then full help
                    pfp = get_pfp(uid)
                    uname = u.get("username", "")
                    fname_u = u.get("first_name", "")
                    welcome = (
                        f"╭━━━〔 👋 <b>WELCOME!</b> 〕━━━╮\n"
                        f"┃├ 👤 Name     : <b>{fname_u}</b>\n"
                        f"┃├ 📛 Username : @{uname or 'N/A'}\n"
                        f"┃├ 🆔 User ID  : <code>{uid}</code>\n"
                        f"┃├ 💎 Plan     : {'✅ Premium' if self.is_premium(uid) else '🔓 Free'}\n"
                        f"┃├ 🤖 Bots     : {self.bot_count(uid)}/{self.effective_limit(uid)}\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                    if pfp:
                        tg(HOST_TOKEN, "sendPhoto", {
                            "chat_id": cid, "photo": pfp,
                            "caption": welcome, "parse_mode": "HTML",
                        })
                    else:
                        sendh(cid, welcome)
                sendh(cid, help_txt, reply_markup=kb)
                return

            if cmd == "/mystatus":   sendh(cid, self.mystatus(uid));   return
            if cmd == "/myplan":     sendh(cid, self.myplan(uid));     return
            if cmd == "/payhistory": send(cid, self.pay_history(uid)); return
            if cmd == "/plan":       sendh(cid, self.plan_text());     return
            if cmd == "/referral":   send(cid, self.referral_info(uid)); return
            if cmd == "/adminlist":  send(cid, self.admin_list());    return

            if cmd == "/redeem":
                if len(args) < 1: send(cid, "Usage: /redeem <coupon_code>"); return
                send(cid, self.redeem_coupon(uid, args[0])); return

            if cmd == "/schedule":
                if len(args) < 3:
                    send(cid,
                        f"❌ Usage: /schedule <botname> <action> <minutes>\n{DIV2}\n"
                        f"Actions: restart, stop\n"
                        f"Example: /schedule mybot restart 30"
                    ); return
                try:
                    mins   = safe_int(args[2])
                    action = args[1].lower()
                    if mins < 1 or mins > 1440:
                        send(cid, "❌ Minutes: 1 se 1440 ke beech hona chahiye."); return
                    if action not in ("restart", "stop"):
                        send(cid, "❌ Action sirf 'restart' ya 'stop' ho sakta hai."); return
                    send(cid, self.schedule_task(uid, args[0], action, mins))
                except:
                    send(cid, "❌ Invalid. Usage: /schedule <botname> <restart/stop> <minutes>")
                return

            if cmd == "/buy":
                if len(args) < 1:
                    send(cid, f"Usage: /buy <days>\nExample: /buy 30\n\n{self.plan_text()}"); return
                try: days = safe_int(args[0])
                except: send(cid, "❌ Valid number do."); return
                req_id, err = self.create_pay_req(uid, days)
                if err: send(cid, err); return
                qr       = self.get_qr()
                msg_text = (
                    f"🛒 PAYMENT REQUEST CREATED\n{DIV}\n"
                    f"🧾 Request ID  : {req_id}\n"
                    f"💎 Plan        : {days} Days Premium\n"
                    f"🤖 Bot Slots   : {PLAN_BOT_LIMITS.get(days,'?')}\n"
                    f"💰 Amount      : ₹{PLANS[days]}\n"
                    f"{DIV}\n"
                    f"📲 UPI ID  : {UPI_ID}\n"
                    f"👤 Pay to  : {OWNER_NAME}\n"
                    f"{DIV}\n"
                    f"STEPS:\n"
                    f"  1️⃣  UPI se pay karo\n"
                    f"  2️⃣  /paid {req_id} <txn_id>\n"
                    f"  3️⃣  /payss {req_id} [screenshot]\n"
                    f"  4️⃣  Admin verify karega ⚡\n"
                    f"{DIV}"
                )
                if qr: send_photo(cid, qr, msg_text)
                else:  send(cid, msg_text)
                notify_admins(
                    f"🛒 NEW PAYMENT REQUEST\n{DIV}\n"
                    f"🧾 {req_id}\n"
                    f"👤 {u.get('first_name','')} (@{u.get('username','-')}) | {uid}\n"
                    f"💎 {days} Days ₹{PLANS[days]}\n"
                    f"⏰ {fmt_time(now_ts())}"
                )
                return

            if cmd == "/paid":
                if len(args) < 2: send(cid, "Usage: /paid <req_id> <txn_id>"); return
                req_id = args[0]
                txn    = " ".join(args[1:])
                send(cid, self.mark_paid(uid, req_id, txn))
                notify_admins(
                    f"💰 PAYMENT MARKED AS PAID\n{DIV}\n"
                    f"🧾 {req_id}\n"
                    f"👤 {u.get('first_name','')} (@{u.get('username','-')}) | {uid}\n"
                    f"💳 Txn: {txn}\n"
                    f"⏰ {fmt_time(now_ts())}\n"
                    f"{DIV}\n✅ /approve {req_id}\n❌ /reject {req_id}"
                )
                return

            # /payss with screenshot
            if caption and caption.lower().startswith("/payss"):
                parts2 = caption.split()
                if len(parts2) < 2: send(cid, "Usage: /payss <req_id> [screenshot]"); return
                req_id = parts2[1]
                if photo:
                    fwd_photo_admins(photo[-1]["file_id"],
                        f"📸 PAYMENT SCREENSHOT\n{DIV2}\n"
                        f"🧾 {req_id}\n"
                        f"👤 {u.get('first_name','')} | {uid}\n"
                        f"✅ /approve {req_id}\n❌ /reject {req_id}"
                    )
                    send(cid, "✅ Screenshot bhej diya!\nAdmin jald verify karega."); return
                if doc:
                    fwd_file_admins(doc["file_id"], f"📎 Screenshot {req_id} | {uid}")
                    send(cid, "✅ Screenshot bhej diya!"); return
                send(cid, "📸 Photo ke saath /payss <req_id> bhejo."); return

            if cmd == "/save":
                if len(args) < 1: send(cid, "Usage: /save <bot_token>"); return
                send(cid, self.save_token(uid, args[0])); return

            if cmd in ("/bots", "/botlist"): sendh(cid, self.my_bots(uid)); return

            if cmd == "/botinfo":
                if len(args) < 1: send(cid, "Usage: /botinfo <name>"); return
                send(cid, self.botinfo(uid, args[0])); return

            if cmd == "/stop":
                if len(args) < 1: send(cid, "Usage: /stop <name>"); return
                send(cid, self.stop_bot(uid, args[0], delete=False)); return

            if cmd == "/on":
                if len(args) < 1: send(cid, "Usage: /on <name>"); return
                res = self.on_bot(uid, cid, args[0])
                if res: send(cid, res)
                else:   send(cid, f"🚀 Bot starting: {args[0]}...")
                return

            if cmd == "/restart":
                if len(args) < 1: send(cid, "Usage: /restart <name>"); return
                res = self.restart_bot(uid, cid, args[0])
                if res: send(cid, res)
                return

            if cmd == "/delete":
                if ia and len(args) >= 2:
                    try:
                        tuid = safe_int(args[0])
                        send(cid, self.stop_bot(tuid, args[1], delete=True)); return
                    except: send(cid, "Usage (admin): /delete <uid> <name>"); return
                if len(args) < 1: send(cid, "Usage: /delete <name>"); return
                send(cid, self.stop_bot(uid, args[0], delete=True)); return

            if cmd == "/logs":
                if len(args) < 1: send(cid, "Usage: /logs <name>"); return
                self.send_logs(cid, uid, args[0]); return

            if cmd == "/clearlogs":
                if len(args) < 1: send(cid, "Usage: /clearlogs <name>"); return
                send(cid, self.clear_logs(uid, args[0])); return

            # ══ ADMIN COMMANDS ══
            if not ia:
                # Unknown command for normal user
                if cmd and cmd.startswith("/"): send(cid, f"❓ Command nahi pehchana.\n/help se commands dekho.")
                return

            # QR set
            if cmd == "/cybersameersetqr": self.set_qr_pending(uid); return
            if caption.lower().startswith("/cybersameersetqr"):
                if photo: self.set_qr(photo[-1]["file_id"], uid); send(cid, "✅ QR saved."); return
                if doc:   self.set_qr(doc["file_id"], uid);       send(cid, "✅ QR saved."); return
                send(cid, "📸 QR photo bhejo."); return

            if cmd == "/stats":      send(cid, self.stats());        return
            if cmd == "/systeminfo": send(cid, self.system_info());  return
            if cmd == "/runningbots": send(cid, self.running_bots()); return
            if cmd in ("/users", "/user"): send(cid, self.users_text()); return
            if cmd == "/activeusers":  send(cid, self.active_users());  return
            if cmd == "/premiumusers": send(cid, self.premium_users()); return
            if cmd == "/revenue":      send(cid, self.revenue_stats()); return

            if cmd == "/userinfo":
                if len(args) < 1: send(cid, "Usage: /userinfo <id or @username>"); return
                try: send(cid, self.userinfo(safe_int(args[0])))
                except:
                    uid_f, _ = self.find_user_by_uname(args[0])
                    send(cid, self.userinfo(uid_f) if uid_f else "❌ User nahi mila.")
                return

            if cmd == "/fulluserinfo":
                if len(args) < 1: send(cid, "Usage: /fulluserinfo <id>"); return
                try:
                    result = self.full_userinfo(safe_int(args[0]))
                    if isinstance(result, tuple):
                        text_result, pfp = result
                        if pfp: send_photo(cid, pfp, text_result[:900])
                        send(cid, text_result)
                    else: send(cid, result)
                except Exception as e: send(cid, f"❌ Error: {str(e)[:200]}")
                return

            if cmd == "/finduser":
                if len(args) < 1: send(cid, "Usage: /finduser <@username or id>"); return
                try: send(cid, self.userinfo(safe_int(args[0])))
                except:
                    uid_f, _ = self.find_user_by_uname(args[0])
                    send(cid, self.userinfo(uid_f) if uid_f else "❌ User nahi mila.")
                return

            if cmd == "/ban":
                if len(args) < 1: send(cid, "Usage: /ban <uid> [reason]"); return
                send(cid, self.ban_user(uid, safe_int(args[0]), " ".join(args[1:]))); return

            if cmd == "/unban":
                if len(args) < 1: send(cid, "Usage: /unban <uid>"); return
                send(cid, self.unban_user(uid, safe_int(args[0]))); return

            if cmd == "/banlist": send(cid, self.banned_list_text()); return

            if cmd == "/warn":
                if len(args) < 1: send(cid, "Usage: /warn <uid> [reason]"); return
                send(cid, self.warn_user(uid, safe_int(args[0]), " ".join(args[1:]))); return

            if cmd == "/unwarn":
                if len(args) < 1: send(cid, "Usage: /unwarn <uid>"); return
                send(cid, self.unwarn_user(safe_int(args[0]))); return

            if cmd == "/setnote":
                if len(args) < 2: send(cid, "Usage: /setnote <uid> <note>"); return
                send(cid, self.set_note(uid, safe_int(args[0]), " ".join(args[1:]))); return

            if cmd == "/allbots":  send(cid, self.allbots_text()); return
            if cmd == "/alllogs":  send(cid, self.alllogs());      return

            if cmd == "/botlog":
                if len(args) < 2: send(cid, "Usage: /botlog <uid> <name>"); return
                self.send_logs(cid, safe_int(args[0]), args[1]); return

            if cmd in ("/broadcast", "/brodcast"):
                if not args: send(cid, "Usage: /broadcast <text>"); return
                send(cid, self.broadcast(" ".join(args))); return

            if cmd == "/broadcastpremium":
                if not args: send(cid, "Usage: /broadcastpremium <text>"); return
                send(cid, self.broadcast(" ".join(args), premium_only=True)); return

            if cmd == "/allbotsstop":
                c = sum(1 for r in self.runners.values() if r.proc and r.proc.poll() is None)
                for kk, r in list(self.runners.items()): r.stop(); self.runners.pop(kk, None)
                send(cid, f"✅ {c} bots band kar diye."); return

            if cmd == "/allbotson":
                self.start_saved(); send(cid, "✅ Sabhi saved bots start ho rahe hain."); return

            if cmd == "/usergivebot":
                if len(args) < 3: send(cid, "Usage: /usergivebot <id> <limit> <days>"); return
                try:
                    tuid = safe_int(args[0]); bl = safe_int(args[1]); days = safe_int(args[2])
                    self.usergivebot(uid, tuid, bl, days)
                    send(cid, f"✅ {tuid} ko {bl} bots {days} days ke liye diya.")
                    send(tuid,
                        f"🎁 CREDIT RECEIVED!\n{DIV}\n"
                        f"🤖 Bot Slots : {bl}\n"
                        f"📅 Duration  : {days} days\n"
                        f"📅 Expires   : {self.premium_exp(tuid)}\n"
                        f"⏰ {fmt_time(now_ts())}\n{DIV}\n🚀 Upload karo!"
                    )
                except: send(cid, "❌ Invalid numbers.")
                return

            if cmd == "/giveplan":
                if len(args) < 2: send(cid, "Usage: /giveplan <id> <days>"); return
                try: tuid = safe_int(args[0]); days = safe_int(args[1])
                except: send(cid, "❌ Invalid."); return
                if days not in PLANS: send(cid, f"❌ Valid days: {sorted(PLANS.keys())}"); return
                self.set_plan(tuid, days)
                send(cid, f"✅ {tuid} ko {days} days plan de diya.")
                send(tuid,
                    f"🎉 PLAN ACTIVATED!\n{DIV}\n"
                    f"💎 Plan: {days} Days Premium\n"
                    f"🤖 Bots: {PLAN_BOT_LIMITS.get(days,'?')}\n"
                    f"📅 Expires: {self.premium_exp(tuid)}\n{DIV}"
                )
                return

            if cmd == "/extendplan":
                if len(args) < 2: send(cid, "Usage: /extendplan <id> <days>"); return
                try: tuid = safe_int(args[0]); days = safe_int(args[1])
                except: send(cid, "❌ Invalid."); return
                send(cid, self.extend_plan(tuid, days))
                send(tuid, f"🎁 Plan {days} days extend ho gaya!\n📅 New exp: {self.premium_exp(tuid)}")
                return

            if cmd == "/resetallusercredit": send(cid, self.reset_all_credits()); return

            if cmd == "/allusergive":
                if len(args) < 2: send(cid, "Usage: /allusergive <limit> <days>"); return
                try: bl = safe_int(args[0]); days = safe_int(args[1])
                except: send(cid, "❌ Invalid."); return
                send(cid, self.all_user_give(bl, days)); return

            if cmd == "/approve":
                if len(args) < 1: send(cid, "Usage: /approve <req_id>"); return
                send(cid, self.approve_req(uid, args[0])); return

            if cmd == "/reject":
                if len(args) < 1: send(cid, "Usage: /reject <req_id> [reason]"); return
                send(cid, self.reject_req(uid, args[0], " ".join(args[1:]))); return

            if cmd == "/pendingpay": send(cid, self.pending_pays()); return

            if cmd == "/setnotice":
                if len(args) < 1: send(cid, "Usage: /setnotice <text>"); return
                send(cid, self.set_notice(uid, " ".join(args))); return

            if cmd == "/clearnotice": send(cid, self.clear_notice()); return

            if cmd == "/setwelcome":
                if len(args) < 1: send(cid, "Usage: /setwelcome <text>"); return
                send(cid, self.set_welcome(" ".join(args))); return

            if cmd == "/clearwelcome": send(cid, self.clear_welcome()); return

            if cmd == "/setreply":
                if len(args) < 2: send(cid, "Usage: /setreply <keyword> <reply>"); return
                send(cid, self.set_autoreply(args[0], " ".join(args[1:]))); return

            if cmd == "/delreply":
                if len(args) < 1: send(cid, "Usage: /delreply <keyword>"); return
                send(cid, self.del_autoreply(args[0])); return

            if cmd == "/listreplies": send(cid, self.list_autoreplies()); return

            if cmd == "/addcoupon":
                if len(args) < 1: send(cid, "Usage: /addcoupon <days> [limit] [code]"); return
                try:
                    days  = safe_int(args[0])
                    limit = safe_int(args[1]) if len(args) > 1 else 1
                    code  = args[2] if len(args) > 2 else None
                    send(cid, self.create_coupon(uid, days, limit, code))
                except: send(cid, "❌ Invalid. Usage: /addcoupon <days> [limit] [code]")
                return

            if cmd == "/delcoupon":
                if len(args) < 1: send(cid, "Usage: /delcoupon <code>"); return
                send(cid, self.del_coupon(args[0])); return

            if cmd == "/coupons": send(cid, self.list_coupons()); return

            if cmd == "/setcmd":
                if len(args) < 2: send(cid, "Usage: /setcmd <command> <reply>"); return
                send(cid, self.set_custom_cmd(args[0], " ".join(args[1:]), uid)); return

            if cmd == "/delcmd":
                if len(args) < 1: send(cid, "Usage: /delcmd <command>"); return
                send(cid, self.del_custom_cmd(args[0])); return

            if cmd == "/listcmds": send(cid, self.list_custom_cmds()); return

            # ══ FORCE-JOIN MANAGEMENT ══
            if cmd == "/listfj":
                sendh(cid, self.fj_show()); return

            if cmd == "/addfj":
                if len(args) < 2: send(cid, "Usage: /addfj <chat_id> <link> [name]"); return
                chat_id = args[0]; link = args[1]
                name_fj = " ".join(args[2:]) if len(args) > 2 else link
                send(cid, self.fj_add(chat_id, link, name_fj)); return

            if cmd == "/removefj":
                if len(args) < 1: send(cid, "Usage: /removefj <chat_id>"); return
                send(cid, self.fj_remove(args[0])); return

            if cmd == "/maintenance":
                if len(args) < 1: send(cid, "Usage: /maintenance on/off"); return
                on_off = args[0].lower() in ("on", "1", "yes", "true")
                send(cid, self.set_maintenance(uid, on_off)); return

            if cmd == "/deletealluserbots": send(cid, self.del_all_user_bots(uid)); return
            if cmd == "/adminbots":         send(cid, self.admin_bots());           return

            if cmd == "/backup":
                send(cid, "⏳ Backup ban raha hai...")
                bpath, bmsg = self.backup_data(uid)
                send(cid, bmsg)
                if bpath and os.path.exists(bpath):
                    send(cid, f"📦 Backup location: {bpath}")
                return

            # ══ SUPER ADMIN COMMANDS ══
            if cmd == "/sa":
                if not isp: send(cid, "❌ Sirf Super Admin."); return
                send(cid, self.super_admin_panel()); return

            if cmd == "/addadmin":
                if not isp: send(cid, "❌ Sirf Super Admin."); return
                if len(args) < 1: send(cid, "Usage: /addadmin <id>"); return
                send(cid, self.add_admin(uid, safe_int(args[0]))); return

            if cmd == "/removeadmin":
                if not isp: send(cid, "❌ Sirf Super Admin."); return
                if len(args) < 1: send(cid, "Usage: /removeadmin <id>"); return
                send(cid, self.remove_admin(uid, safe_int(args[0]))); return

            if cmd == "/admininfo":
                if not isp: send(cid, "❌ Sirf Super Admin."); return
                if len(args) < 1: send(cid, "Usage: /admininfo <id>"); return
                result = self.admin_full_info(safe_int(args[0]))
                if isinstance(result, tuple):
                    text_result, pfp = result
                    if pfp: send_photo(cid, pfp, text_result[:900])
                    send(cid, text_result)
                else: send(cid, result)
                return

            if cmd == "/deleteallbots":
                if not isp: send(cid, "❌ Sirf Super Admin."); return
                send(cid, self.del_all_bots(uid)); return

            # Forward user photos to admins
            if photo and not ia:
                fwd_photo_admins(photo[-1]["file_id"],
                    f"📷 Photo from {u.get('first_name','')} (@{u.get('username','-')}) | {uid}")

            # File uploads — all supported languages + zip
            if doc:
                fname = doc.get("file_name", "") or ""
                fext  = os.path.splitext(fname)[1].lower()
                if fext not in BOT_EXTS and fext != ".zip":
                    if not ia:
                        fwd_file_admins(doc["file_id"],
                            f"📎 {fname} from {uid} @{u.get('username','-')}")
                    sendh(cid,
                        f"╭━━━〔 ⚠️ <b>UNSUPPORTED FILE</b> 〕━━━╮\n"
                        f"┃├ Extension '<b>{fext or 'unknown'}</b>' support nahi hai.\n"
                        f"┃├\n"
                        f"┃├ <b>Supported file types:</b>\n"
                        f"┃├ 🐍 <code>.py</code>   — Python\n"
                        f"┃├ 🟩 <code>.js .mjs .cjs</code> — Node.js\n"
                        f"┃├ 🔷 <code>.ts</code>   — TypeScript\n"
                        f"┃├ 🔵 <code>.go</code>   — Go (Golang)\n"
                        f"┃├ 💎 <code>.rb</code>   — Ruby\n"
                        f"┃├ 🐘 <code>.php</code>  — PHP\n"
                        f"┃├ 🐚 <code>.sh</code>   — Shell/Bash\n"
                        f"┃├ 🔮 <code>.pl</code>   — Perl\n"
                        f"┃├ 🌙 <code>.lua</code>  — Lua\n"
                        f"┃├ 📦 <code>.zip</code>  — Any language project\n"
                        f"╰━━━━━━━━━━━━━━━━━━━━━━━╯"
                    )
                    return
                with self.lock:
                    if uid in self.user_busy:
                        sendh(cid, "⚠️ Ruko, pichla upload process ho raha hai."); return
                    self.user_busy.add(uid)
                threading.Thread(target=self.process_upload, args=(cid, u, doc, caption), daemon=True).start()
                return

            if cmd == "/about":
                sendh(cid, self.about_text(), reply_markup=mk_url_kb([
                    [("📢 Channel", CHANNEL_LINK), ("💬 Support", SUPPORT_LINK)],
                ])); return

            if cmd == "/convertbutton":
                if not ia: send(cid, "❌ Sirf admins."); return
                sendh(cid,
                    f"╭━━━〔 ⌨️ <b>KEYBOARD MODE ON</b> 〕━━━╮\n"
                    f"┃├ ✅ Ab /start pe buttons aayenge\n"
                    f"┃├ 💡 /convertcommand se wapas text mode\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━╯",
                    reply_markup=self.admin_kb() if ia else self.user_kb()
                ); return

            if cmd == "/convertcommand":
                if not ia: send(cid, "❌ Sirf admins."); return
                sendh(cid,
                    f"╭━━━〔 📝 <b>COMMAND MODE ON</b> 〕━━━╮\n"
                    f"┃├ ✅ Ab text commands use karo\n"
                    f"┃├ 💡 /convertbutton se button mode\n"
                    f"╰━━━━━━━━━━━━━━━━━━━━━━━╯",
                    reply_markup=remove_kb()
                ); return

            if cmd == "/buttons":
                kb = self.admin_kb() if ia else self.user_kb()
                sendh(cid, "╭━━━〔 ⌨️ <b>QUICK BUTTONS</b> 〕━━━╮\n┃├ Neeche buttons se kaam karo:\n╰━━━━━━━━━━━━━━━━━━━━━━━╯",
                      reply_markup=kb); return

            # Unknown command
            if cmd and cmd.startswith("/"):
                send(cid, f"❓ Command '{cmd}' nahi pehchana.\n/help se commands dekho.")

        except Exception as e:
            print(f"[HANDLE ERROR] {e}")
            traceback.print_exc()

    # ════════════════════════════════════════
    #   MAIN LOOP
    # ════════════════════════════════════════
    def run(self):
        del_webhook()
        ensure_dirs()
        self.start_saved()
        print(
            f"\n╔{'═'*50}╗\n"
            f"║  {BOT_NAME} — BOT HOSTING PANEL v5.0{' '*14}║\n"
            f"║  Developer : {OWNER_NAME:<36}║\n"
            f"║  Platform  : Termux | VPS | Render | Railway║\n"
            f"║              Koyeb | Replit | Any Python 3.8║\n"
            f"╚{'═'*50}╝\n"
            f"[*] Python       : {PYTHON_BIN}\n"
            f"[*] Version      : {sys.version.split()[0]}\n"
            f"[*] Started      : {fmt_time(now_ts())}\n"
            f"[*] Super Admin  : {SUPER_ADMIN}\n"
            f"[*] Auto-install : {AUTO_INSTALL}\n"
            f"[*] Running...\n"
        )
        while True:
            try:
                res = tg(HOST_TOKEN, "getUpdates", {
                    "offset":          self.offset,
                    "timeout":         LONG_POLL_TIMEOUT,
                    "limit":           100,
                    "allowed_updates": json.dumps(["message", "callback_query"]),
                }, timeout=LONG_POLL_TIMEOUT + 15)
                if res.get("ok"):
                    for upd in res.get("result", []):
                        self.offset = max(self.offset, safe_int(upd.get("update_id", 0)) + 1)
                        msg = upd.get("message")
                        cbq = upd.get("callback_query")
                        if msg:
                            threading.Thread(target=self.handle, args=(msg,), daemon=True).start()
                        if cbq:
                            threading.Thread(target=self.handle_callback, args=(cbq,), daemon=True).start()
                else:
                    err = res.get("error", "Unknown error")
                    if "401" in str(err):
                        print(f"[FATAL] Invalid HOST_TOKEN! Check config.")
                        break
                    time.sleep(SLEEP_ON_ERROR)
            except KeyboardInterrupt:
                print("\n[!] Stopped by user.")
                break
            except Exception as e:
                print(f"[LOOP ERROR] {e}")
                traceback.print_exc()
                time.sleep(SLEEP_ON_ERROR)

# ════════════════════════════════════════
#   KEEP-ALIVE SERVER (24/7 Free Hosting)
# ════════════════════════════════════════
def start_keepalive():
    from http.server import BaseHTTPRequestHandler, HTTPServer
    port = int(os.environ.get("PORT", 5000))
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"CyberHost Bot is Running!")
        def log_message(self, *args): pass
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"[KEEP-ALIVE] Web server started on port {port}")
    server.serve_forever()

# ════════════════════════════════════════
#   ENTRY POINT
# ════════════════════════════════════════
if __name__ == "__main__":
    if not HOST_TOKEN or HOST_TOKEN == "YOUR_BOT_TOKEN_HERE" or "YOUR_" in HOST_TOKEN:
        print("═" * 55)
        print("  ❌ HOST_TOKEN SET NAHI HAI!")
        print("═" * 55)
        print("\n  config section mein yeh set karo:\n")
        print(f'    HOST_TOKEN   = "1234567890:ABCdefGHIjkl..."')
        print(f'    SUPER_ADMIN  = <aapka_telegram_id>')
        print(f'    BOT_NAME     = "{BOT_NAME}"')
        print(f'    OWNER_NAME   = "{OWNER_NAME}"')
        print(f'    UPI_ID       = "yourname@upi"')
        print(f'    CHANNEL_LINK = "https://t.me/yourchannel"')
        print(f'    SUPPORT_LINK = "https://t.me/yoursupport"')
        print("\n  Token kaise milega?")
        print("    1. Telegram pe @BotFather open karo")
        print("    2. /newbot type karo")
        print("    3. Token copy karo aur yahan paste karo")
        print("═" * 55)
    else:
        threading.Thread(target=start_keepalive, daemon=True).start()
        HostBot().run()
