#!/usr/bin/env bash
# Activa el listener de syslog UDP (puerto 514) en Wazuh manager para poder
# recibir las alertas del modbus-sensor.
# Uso: ./configure-wazuh-syslog.sh   (ejecutar una vez, tras el primer "docker compose up")

set -euo pipefail

CONTAINER="wazuh.manager"
LOCAL_FILE="wazuh-config/remote-syslog.xml"
REMOTE_TMP="/tmp/remote-syslog.xml"
CONF_FILE="/var/ossec/etc/ossec.conf"

echo "Comprobando si la configuración de syslog ya está aplicada..."
if docker exec "$CONTAINER" grep -q "<connection>syslog</connection>" "$CONF_FILE"; then
  echo "Ya estaba configurado. No se hace nada."
  exit 0
fi

echo "Copiando el bloque de configuración al contenedor..."
docker cp "$LOCAL_FILE" "$CONTAINER:$REMOTE_TMP"

echo "Insertando el bloque <remote> en ossec.conf..."
docker exec "$CONTAINER" sed -i "1r $REMOTE_TMP" "$CONF_FILE"

echo "Reiniciando Wazuh manager para aplicar el cambio..."
docker exec "$CONTAINER" /var/ossec/bin/wazuh-control restart

echo "Listo. Wazuh debería estar escuchando syslog UDP en el puerto 514."
