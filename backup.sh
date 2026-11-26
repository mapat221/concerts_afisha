#!/bin/bash
BACKUP_DIR="$(pwd)/backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/concerthub_point_$TIMESTAMP.sql"

docker exec -t concerts_afisha_pg_db pg_dump -U postgres concerts_afisha_db > "$BACKUP_FILE"

echo "Контрольная точка создана: $BACKUP_FILE"
