#!/bin/bash
cd "$(dirname "$0")"
BACKUP_DIR="$(pwd)/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/concerthub_point_$TIMESTAMP.sql"
docker exec concerts_afisha_pg_db sh -c 'pg_dump -U "${POSTGRES_USER:-postgres}" "${POSTGRES_DB:-concerts_afisha_db}"' > "$BACKUP_FILE"
echo "Контрольная точка создана: $BACKUP_FILE"