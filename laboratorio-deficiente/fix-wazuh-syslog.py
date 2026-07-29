"""
Corrige la configuracion de syslog en Wazuh manager.

Problema detectado: el bloque <remote> de syslog se insertó con
`sed -i '1r archivo'`, que asume que la linea 1 de ossec.conf es
<ossec_config>. En realidad la linea 1 es el inicio de un comentario
XML (<!--), asi que el bloque quedo comentado y wazuh-remoted nunca
lo cargo.

Este script:
  1. Copia ossec.conf fuera del contenedor.
  2. Elimina cualquier bloque <remote> que contenga "syslog" (el mal insertado).
  3. Inserta un bloque limpio justo despues de la apertura real <ossec_config>.
  4. Copia el archivo corregido de vuelta y reinicia Wazuh manager.

Uso: python3 fix-wazuh-syslog.py
"""

import re
import subprocess
import sys

CONTAINER = "wazuh.manager"
CONF_PATH = "/var/ossec/etc/ossec.conf"
LOCAL_TMP = "/tmp/ossec.conf.fixed"

REMOTE_BLOCK = (
    "  <remote>\n"
    "    <connection>syslog</connection>\n"
    "    <port>514</port>\n"
    "    <protocol>udp</protocol>\n"
    "    <allowed-ips>172.21.0.0/24</allowed-ips>\n"
    "  </remote>\n"
)


def run(cmd):
    subprocess.run(cmd, check=True)


def main():
    raw = subprocess.check_output(["docker", "exec", CONTAINER, "cat", CONF_PATH]).decode()

    # 1) Quitar cualquier bloque <remote>...</remote> que contenga "syslog"
    #    (elimina el que quedo mal insertado dentro del comentario).
    cleaned = re.sub(
        r"[ \t]*<remote>\s*<connection>syslog</connection>.*?</remote>\s*\n?",
        "",
        raw,
        flags=re.S,
    )

    if "<ossec_config>" not in cleaned:
        print("No se encontró la etiqueta <ossec_config>. Abortando sin hacer cambios.")
        sys.exit(1)

    # 2) Insertar el bloque limpio justo despues de la apertura real
    fixed = cleaned.replace("<ossec_config>", "<ossec_config>\n" + REMOTE_BLOCK, 1)

    with open(LOCAL_TMP, "w") as f:
        f.write(fixed)

    print("Copiando el archivo corregido al contenedor...")
    run(["docker", "cp", LOCAL_TMP, f"{CONTAINER}:{CONF_PATH}"])

    print("Reiniciando Wazuh manager...")
    run(["docker", "exec", CONTAINER, "/var/ossec/bin/wazuh-control", "restart"])

    print("Listo. Verifica con:")
    print(f'  docker exec {CONTAINER} grep -i "remoted" /var/ossec/logs/ossec.log')


if __name__ == "__main__":
    main()
