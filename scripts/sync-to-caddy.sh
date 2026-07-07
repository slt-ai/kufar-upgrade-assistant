#!/usr/bin/env bash
# Синхронизация отчётов на Caddy LXC (172.21.21.238 -> /var/www/kufar-reports).
#
# На сервере лежат ТОЛЬКО *.html — конвертированные из reports/*.md.
# .md/.json/.csv и прочее на сервер не попадают (и подтираются, если были).
#
# Запуск из корня проекта: bash scripts/sync-to-caddy.sh

set -euo pipefail

REMOTE="caddy"
DST_DIR="/var/www/kufar-reports"
SRC_DIR="reports"
HTML_DIR="${HTML_DIR:-reports}"   # куда складывать сгенерированный .html локально

# 1) Генерируем HTML из всех reports/*.md
echo ">> Генерация HTML из ${SRC_DIR}/*.md"
python scripts/md_to_html.py --all --out-dir "$HTML_DIR"

# 2) Пушим на сервер только *.html (плоско, без подкаталогов), остальное подтираем
echo ">> Загрузка только *.html -> ${REMOTE}:${DST_DIR}"
( cd "$HTML_DIR" && find . -maxdepth 1 -name '*.html' -print0 \
    | tar --owner=0 --group=0 --null -cf - --files-from - ) \
  | ssh "$REMOTE" "
	set -e
	rm -rf '$DST_DIR'/*
	mkdir -p '$DST_DIR'
	tar --no-same-owner -C '$DST_DIR' -xf -
	chown -R caddy:caddy '$DST_DIR'
	find '$DST_DIR' -type f -exec chmod 644 {} +
	find '$DST_DIR' -type d -exec chmod 755 {} +
	# Гарантия: на сервере нет ничего, кроме *.html
	find '$DST_DIR' -type f ! -name '*.html' -delete
	echo '>> На сервере файлов:' \$(find '$DST_DIR' -type f | wc -l)
	echo '>> Не-html (должно быть 0):' \$(find '$DST_DIR' -type f ! -name '*.html' | wc -l)
"