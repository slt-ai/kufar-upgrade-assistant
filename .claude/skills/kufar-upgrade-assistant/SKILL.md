---
name: kufar-upgrade-assistant
description: Скилл для развёртывания и работы с репозиторием kufar-upgrade-assistant — подбор б/у комплектующих на kufar.by. Помогает понять структуру, запустить конвейер, обновить README, проверить ошибки и подготовить отчёт.
---

# kufar-upgrade-assistant skill

Используй этот скилл при работе с репозиторием `kufar-upgrade-assistant`.

## Назначение проекта

Агент-оркестратор подбора б/у комплекта «материнская плата + процессор» на kufar.by для модернизации домашнего ПК. Мат. плата и процессор берутся из разных объявлений и комбинируются по совместимости. Результат — топ-3 Intel и топ-3 AMD с ценами, ссылками и заметками.

## Входные файлы

- `Report.txt` — текущая конфигурация ПК (CPU, плата, ОЗУ, GPU, накопители, форм-фактор).
- `апгрейд-пк — пожелания.md` — все параметры апгрейда (scope, ограничения, URL категорий, справочник сокетов, тиры, бюджет, скоринг, приоритеты под LLM, план по ОЗУ).

Оба файла — единый источник параметров. Агенты читают их при каждом запуске и не хранят значения в своих определениях.

## Конвейер

```
scripts/kufar_parse.py   → _out.json (+ _out_delta.json, .cache/_last_run.json)
scripts/kufar_details.py → _items.json (детали + defect-флаги)
scripts/kufar_filter.py  → _candidates.json ({intel_mb, amd_mb, intel_cpus, amd_cpus})
scripts/_build_report.py → reports/YYYY-MM-DD HHMM — тема — подбор.{md,json}
```

Альтернативные ранжировщики:
- `scripts/kit_analyzer_run.py`
- `scripts/reprocess_kits.py`

Вспомогательные:
- `scripts/enrich_seen.py` — обновляет `.cache/seen_ids.json`.
- `scripts/transform_for_delivery.py` — плоская схема выгрузки.
- `scripts/md_to_html.py` — .md → standalone .html.

## Команды

### Полный подбор Intel + AMD
```bash
cd scripts
python kufar_parse.py "https://www.kufar.by/l/r~minsk/materinskie-platy" "https://www.kufar.by/l/r~minsk/processory" --full
python kufar_details.py
python kufar_filter.py
python _build_report.py
```

### Работа по кешу (без повторного парсинга)
```bash
cd scripts
python kufar_filter.py
python _build_report.py
```

### Перепроверка актуальности прошлого отчёта
Используй skill `kufar-refresh`:
```
/kufar-refresh reports/2026-07-07 0059 — intel+amd ddr4 upgrade — подбор.md
```

## Границы

- Не удалять файлы без одобрения пользователя.
- Не переименовывать существующие файлы.
- Не отправлять сообщения на kufar.by.
- Не выходить за пределы рабочей папки проекта.
- Сбор данных с kufar.by — через агент `kufar-listings-fetcher`.

## Типичные задачи

1. Подобрать комплект Intel/AMD/both.
2. Сравнить Intel vs AMD под текущую видеокарту.
3. Проверить актуальность прошлой выгрузки.
4. Прочитать конфигурацию ПК из `Report.txt`.

## Связанные файлы

- `CLAUDE.md` — инструкции главному агенту.
- `апгрейд-пк — пожелания.md` — параметры апгрейда.
- `проект — документация.md` — полная документация.
- `README.md` — публичное описание.
