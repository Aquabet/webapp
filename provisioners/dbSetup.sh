#!/bin/bash

set -e

username=$(yq '.database.username' /tmp/db_config.yaml | tr -d '"')
password=$(yq '.database.password' /tmp/db_config.yaml | tr -d '"')
dbname=$(yq '.database.dbname' /tmp/db_config.yaml | tr -d '"')
dbhost=$(yq '.database.dbhost' /tmp/db_config.yaml | tr -d '"')
dbport=$(yq '.database.dbport' /tmp/db_config.yaml | tr -d '"')

sudo mysql -u root -e "CREATE USER IF NOT EXISTS '${username}'@'${dbhost}' IDENTIFIED BY '${password}';"

sudo mysql -u root -e "CREATE DATABASE IF NOT EXISTS \`${dbname}\`;"

sudo mysql -u root -e "GRANT ALL PRIVILEGES ON \`${dbname}\`.* TO '${username}'@'${dbhost}';"

sudo mysql -u root -e "FLUSH PRIVILEGES;"

sudo bash -c "cat <<EOT > /opt/webapp/.env
DATABASE_URI=mysql+mysqlconnector://${username}:${password}@${dbhost}:${dbport}/${dbname}
EOT"

sudo chown csye6225:csye6225 /opt/webapp/.env
sudo chmod 600 /opt/webapp/.env
