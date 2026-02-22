# 🕌 مسجد لایو — سیستم پخش زنده مساجد

پلتفرم production-ready پخش زنده مساجد بر پایه Node.js — بدون Redis، Docker یا سرویس خارجی.
قابل اجرا روی VPS با **۱ گیگابایت RAM**.

---

## 📁 ساختار پوشه‌بندی

```
masjid-live/
├── src/
│   ├── server.js              # نقطه ورود Express
│   ├── config.js              # مدیریت متمرکز متغیرهای محیطی
│   ├── db/
│   │   └── database.js        # SQLite + اسکیما + دستورات آماده
│   ├── middleware/
│   │   └── auth.js            # محافظت مسیرها با session
│   ├── routes/
│   │   ├── public.js          # صفحه اصلی + تماشای استریم
│   │   ├── auth.js            # ورود / خروج / ثبت‌نام
│   │   ├── streamer.js        # داشبورد استریمر
│   │   └── admin.js           # داشبورد مدیر
│   └── utils/
│       ├── ffmpeg.js          # مدیریت پراسس‌های FFmpeg
│       ├── rtmp.js            # NodeMediaServer + اعتبارسنجی
│       ├── upload.js          # تنظیمات Multer
│       ├── template.js        # موتور قالب سبک‌وزن
│       └── logger.js          # لاگ‌گذاری با چرخش فایل
├── views/
│   ├── public/
│   │   ├── home.html          # صفحه اصلی (فارسی RTL)
│   │   └── watch.html         # صفحه پخش با hls.js
│   ├── auth/
│   │   ├── login.html         # صفحه ورود
│   │   └── register.html      # صفحه ثبت‌نام
│   ├── streamer/
│   │   ├── dashboard.html     # داشبورد استریمر
│   │   ├── create.html        # ساخت استریم
│   │   └── detail.html        # جزئیات + مدیریت استریم
│   ├── admin/
│   │   ├── overview.html      # مرور کلی سیستم
│   │   ├── users.html         # مدیریت کاربران
│   │   ├── create-user.html   # ساخت کاربر
│   │   ├── streams.html       # مدیریت استریم‌ها
│   │   └── logs.html          # لاگ‌های سیستم
│   └── error.html
├── public/css/main.css        # طراحی فارسی RTL
├── scripts/seed.js            # ساخت ادمین اولیه
├── nginx/masjid-live.conf     # Nginx reverse proxy
├── masjid-live.service        # systemd unit
├── .env.example
└── package.json
```

---

## 🗄 اسکیمای SQLite

```sql
-- کاربران (ادمین + استریمر)
CREATE TABLE users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  username      TEXT    NOT NULL UNIQUE,
  password_hash TEXT    NOT NULL,         -- bcrypt(12)
  role          TEXT    NOT NULL DEFAULT 'streamer',
  is_approved   INTEGER NOT NULL DEFAULT 0,
  is_active     INTEGER NOT NULL DEFAULT 1,
  created_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- استریم‌ها
CREATE TABLE streams (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title        TEXT    NOT NULL,
  mosque_name  TEXT    NOT NULL,
  logo_path    TEXT,                      -- /logos/<uuid>.ext
  stream_key   TEXT    NOT NULL UNIQUE,   -- UUID بدون خط تیره (۳۲ کاراکتر hex)
  is_live      INTEGER NOT NULL DEFAULT 0,
  created_at   TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- جلسات پخش
CREATE TABLE live_sessions (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  stream_id  INTEGER NOT NULL REFERENCES streams(id) ON DELETE CASCADE,
  started_at TEXT    NOT NULL DEFAULT (datetime('now')),
  ended_at   TEXT
);

-- لاگ حسابرسی
CREATE TABLE audit_logs (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  actor      TEXT,
  action     TEXT NOT NULL,
  detail     TEXT,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

**بهینه‌سازی SQLite:**

| Pragma | مقدار | دلیل |
|--------|-------|------|
| `journal_mode` | WAL | خواندن همزمان بدون قفل |
| `synchronous` | NORMAL | ایمن + سریع‌تر از FULL |
| `cache_size` | ۱۶ MB | کاهش I/O دیسک |
| `temp_store` | MEMORY | جداول موقت در RAM |
| `mmap_size` | ۱۲۸ MB | حافظه mapped |

---

## 📺 تنظیمات FFmpeg

### بدون لوگو — کپی مستقیم (مصرف CPU ≈ صفر)
```bash
ffmpeg -i rtmp://127.0.0.1:1935/live/<key> \
  -c copy \
  -f hls -hls_time 4 -hls_list_size 10 \
  -hls_flags delete_segments+append_list+omit_endlist \
  hls/<key>/index.m3u8
```

### با لوگو — encode سبک
```bash
ffmpeg \
  -i rtmp://127.0.0.1:1935/live/<key> \
  -i /uploads/logos/<file> \
  -filter_complex '[1:v]scale=iw*0.09:-1,format=rgba,colorchannelmixer=aa=0.85[logo];[0:v][logo]overlay=W-w-14:14[vout]' \
  -map [vout] -map 0:a \
  -c:v libx264 -preset ultrafast -tune zerolatency -crf 28 -profile:v baseline \
  -c:a aac -b:a 128k \
  -f hls -hls_time 4 -hls_list_size 10 \
  -hls_flags delete_segments+append_list+omit_endlist \
  hls/<key>/index.m3u8
```

**دلیل انتخاب‌ها:**
- `-preset ultrafast` → کمترین مصرف CPU
- `-crf 28` → کیفیت ثابت بدون spike بیت‌ریت
- `-tune zerolatency` → کمترین تأخیر
- `delete_segments` → پاکسازی خودکار قطعات قدیمی

---

## 🚀 اجرا در محیط محلی

### پیش‌نیازها
```bash
node --version  # 18+
ffmpeg -version
```

### راه‌اندازی
```bash
git clone <repo>
cd masjid-live
npm install

# ساخت ادمین اولیه
node scripts/seed.js admin MyPass@123

# اجرا در محیط توسعه
npm run dev
```

- صفحه اصلی: http://localhost:3000
- داشبورد: http://localhost:3000/auth/login

### تنظیم OBS
- سرویس: Custom
- سرور: `rtmp://localhost:1935/live`
- کلید: از داشبورد استریمر کپی کنید

---

## 🖥 استقرار در سرور (VPS)

### ۱. نصب پیش‌نیازها
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y nginx ffmpeg nodejs npm certbot python3-certbot-nginx
```

### ۲. استقرار
```bash
sudo mkdir -p /var/www/masjid-live
sudo chown www-data:www-data /var/www/masjid-live

sudo -u www-data git clone <repo> /var/www/masjid-live
cd /var/www/masjid-live
sudo -u www-data npm install --omit=dev

# پیکربندی
sudo -u www-data cp .env.example .env
sudo -u www-data nano .env  # SESSION_SECRET و رمز ادمین را تنظیم کنید

# ادمین اولیه
sudo -u www-data node scripts/seed.js admin StrongPass@2025
```

### ۳. systemd
```bash
sudo cp masjid-live.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now masjid-live
```

### ۴. Nginx
```bash
sudo cp nginx/masjid-live.conf /etc/nginx/sites-available/masjid-live
sudo nano /etc/nginx/sites-available/masjid-live  # yourdomain.com را جایگزین کنید
sudo ln -s /etc/nginx/sites-available/masjid-live /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### ۵. SSL
```bash
sudo certbot --nginx -d yourdomain.com
```

### ۶. فایروال
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 1935/tcp # RTMP
sudo ufw enable
```

---

## 🔐 توضیح امنیت

| تهدید | راه‌حل |
|-------|---------|
| انتشار RTMP غیرمجاز | اعتبارسنجی کلید استریم در `prePublish` hook — رد در سطح RTMP |
| hijacking جلسه | Cookie session با HMAC، httpOnly، SameSite=Lax، Secure |
| brute force رمز | bcrypt cost=12 |
| path traversal در آپلود | `path.basename()` نام فایل را تمیز می‌کند |
| XSS | موتور قالب همه متغیرها را escape می‌کند |
| ورود غیرمجاز به داشبورد | بررسی مجدد is_active/is_approved در هر درخواست |
| zombie process | SIGTERM + SIGKILL با تأخیر ۵ ثانیه |
| تزریق SQL | دستورات آماده (prepared statements) |
| آپلود مخرب | فیلتر پسوند + محدودیت حجم ۳ مگابایت |

---

## ⚡ بهینه‌سازی مصرف منابع

### مصرف تقریبی RAM در VPS یک گیگ

| مؤلفه | مصرف تقریبی |
|-------|------------|
| Node.js (بیکار) | ~۳۵ مگابایت |
| SQLite page cache | ~۱۶ مگابایت |
| هر استریم (بدون لوگو) | ~۵ مگابایت FFmpeg |
| هر استریم (با لوگو) | ~۳۵-۶۰ مگابایت FFmpeg |
| Nginx | ~۵ مگابایت |
| OS | ~۱۵۰ مگابایت |
| **کل (۱ استریم + لوگو)** | **~۲۷۰ مگابایت** |
| **کل (۳ استریم + لوگو)** | **~۵۵۰ مگابایت** |

### تصمیمات طراحی برای صرفه‌جویی منابع

1. **Cookie session** — بدون ذخیره سمت سرور، صفر مصرف RAM
2. **Prepared statements** — کامپایل یک‌بار در بوت، استفاده همیشگی
3. **WAL mode** — خوانندگان writer را بلاک نمی‌کنند
4. **gop_cache: false** — ۱۰-۵۰ مگابایت صرفه‌جویی به ازای هر استریم
5. **HLS توسط Nginx** — bypass کامل Node.js برای media files
6. **delete_segments** — پاکسازی خودکار فایل‌های .ts قدیمی
7. **موتور قالب سبک** — بدون EJS/Pug، ~۵۰ خط کد
8. **بدون Redis/broker** — وضعیت در SQLite + NMS hooks
9. **یک کیفیت** — یک پراسس FFmpeg به ازای هر استریم
10. **ultrafast preset** — کمترین مصرف CPU هنگام encode

---

## 📊 مانیتورینگ

```bash
# لاگ‌های اپلیکیشن
sudo journalctl -u masjid-live -f

# مصرف منابع
htop

# دیتابیس
sqlite3 /var/www/masjid-live/data/masjid.db \
  "SELECT title, mosque_name, is_live FROM streams;"

# بکاپ
sqlite3 /var/www/masjid-live/data/masjid.db \
  ".backup /var/backups/masjid-$(date +%Y%m%d).db"
```