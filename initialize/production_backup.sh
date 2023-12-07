#!/bin/bash
PRODUCTION_DB_MASTER_PASSWORD=$1
DB_NAME=$2
PRODUCTION_DB_URL=$3
echo 'Take backup from production server:' $PRODUCTION_DB_URL 
echo 'database :' $DB_NAME
# Create a backup
curl -X POST \
    -F "master_pwd=$PRODUCTION_DB_MASTER_PASSWORD" \
    -F "name=$DB_NAME" \
    -F "backup_format=zip" \
    -o restore_custom_db.zip \
    $PRODUCTION_DB_URL/web/database/backup
echo "Done"
