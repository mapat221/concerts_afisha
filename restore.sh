#!/bin/bash
cd "$(dirname "$0")"
if [ -n "$1" ]; then
    TARGET_BACKUP="$1"
else
    FILES=($(ls -t backups/concerthub_point_*.sql 2>/dev/null))
    if [ ${#FILES[@]} -eq 0 ]; then
        echo "Ошибка: в папке backups/ отсутсвуют сохранения"
        exit 1
    fi
    echo "Доступные контрольные точки:"
    for i in "${!FILES[@]}"; do
        SIZE=$(ls -lh "${FILES[$i]}" | awk '{print $5}')
        echo "  [$((i+1))] ${FILES[$i]} ($SIZE)"
    done

    read -p "Введите номер точки для отката, по умолчанию самая новая: " CHOICE
    CHOICE=${CHOICE:-1}
    INDEX=$((CHOICE-1))
    TARGET_BACKUP="${FILES[$INDEX]}"
fi
if [ ! -f "$TARGET_BACKUP" ]; then
    echo "Ошибка: файл $TARGET_BACKUP не найден!"
    exit 1
fi
echo "Откат БД к выбранной контрольной точке: $TARGET_BACKUP"
docker exec concerts_afisha_pg_db sh -c 'psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-concerts_afisha_db}" -c "CREATE TEMP TABLE tmp_log AS SELECT * FROM main_log; \copy tmp_log TO '\''/tmp/main_log_saved.csv'\'' WITH CSV"' >/dev/null 2>&1 || true
docker exec concerts_afisha_pg_db sh -c 'psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-concerts_afisha_db}" -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"' >/dev/null
docker exec -i concerts_afisha_pg_db sh -c 'psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-concerts_afisha_db}"' < "$TARGET_BACKUP" >/dev/null
docker exec concerts_afisha_pg_db sh -c 'psql -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-concerts_afisha_db}" -c "CREATE TEMP TABLE tmp_import (LIKE main_log); \copy tmp_import FROM '\''/tmp/main_log_saved.csv'\'' WITH CSV; INSERT INTO main_log SELECT * FROM tmp_import ON CONFLICT (log_item_id) DO NOTHING; SELECT setval(pg_get_serial_sequence('\''main_log'\'', '\''log_item_id'\''), COALESCE(MAX(log_item_id), 1)) FROM main_log;"' >/dev/null 2>&1 || true

echo "Готово! База полностью восстановлена из сейва: $TARGET_BACKUP"
