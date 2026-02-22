# ================================================================
#  مسجد لایو — Dockerfile
#  بدون Nginx، بدون Certbot
#  Node.js + FFmpeg در یک image سبک‌وزن
# ================================================================

# ── مرحله ۱: نصب dependencies ────────────────────────────────────
FROM node:20-alpine AS deps

WORKDIR /app

# فقط فایل‌های package برای کش لایه‌ها
COPY package.json package-lock.json* ./

# better-sqlite3 نیاز به build tools دارد
RUN apk add --no-cache python3 make g++ \
 && npm ci --omit=dev \
 && apk del python3 make g++


# ── مرحله ۲: image نهایی ─────────────────────────────────────────
FROM node:20-alpine

# برچسب‌های metadata
LABEL maintainer="Masjid Live"
LABEL description="پلتفرم پخش زنده مساجد — Node.js + FFmpeg"

# FFmpeg از Alpine repository (سبک‌ترین گزینه)
RUN apk add --no-cache ffmpeg tini

WORKDIR /app

# کپی node_modules از مرحله deps
COPY --from=deps /app/node_modules ./node_modules

# کپی سورس کد پروژه
COPY . .

# ساخت پوشه‌های مورد نیاز با مالکیت صحیح
RUN mkdir -p /data /hls /uploads/logos /logs \
 && chown -R node:node /app /data /hls /uploads /logs

# اجرا با کاربر غیر-root برای امنیت
USER node

# متغیرهای محیطی پیش‌فرض (override در docker-compose یا runtime)
ENV NODE_ENV=production \
    PORT=3000 \
    RTMP_PORT=1935 \
    DB_PATH=/data/masjid.db \
    HLS_ROOT=/hls \
    UPLOAD_DIR=/uploads \
    LOG_DIR=/logs \
    FFMPEG_PATH=ffmpeg \
    HLS_SEGMENT_TIME=4 \
    HLS_LIST_SIZE=10

# پورت‌های expose شده
EXPOSE 3000
EXPOSE 1935

# tini به عنوان init process — جلوگیری از zombie process
ENTRYPOINT ["/sbin/tini", "--"]

# دستور اجرا
CMD ["node", "src/server.js"]