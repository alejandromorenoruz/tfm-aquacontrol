"""
Sensor de Modbus para AquaControl S.A.
Escucha el trafico Modbus TCP dirigido a OpenPLC (puerto 502) y envia una
alerta por syslog a Wazuh cuando detecta un codigo de funcion de ESCRITURA
(coil o registro), que es el vector de ataque demostrado en la Fase 3
(T0855 - Unauthorized Command Message).

Se ejecuta compartiendo la interfaz de red del contenedor openplc
(network_mode: "service:openplc" en docker-compose.yml), por lo que ve
directamente el trafico entrante sin depender del comportamiento de un
switch/bridge de Docker con las MAC ya aprendidas.
"""

import socket
from scapy.all import sniff, TCP, IP, Raw

WAZUH_HOST = "172.21.0.20"   # IP del wazuh.manager en la red_ot
WAZUH_PORT = 514             # syslog UDP

WRITE_FUNCTION_CODES = {
    5: "Write Single Coil",
    6: "Write Single Register",
    15: "Write Multiple Coils",
    16: "Write Multiple Registers",
}

udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def send_alert(message: str) -> None:
    try:
        udp_sock.sendto(message.encode(), (WAZUH_HOST, WAZUH_PORT))
    except OSError as exc:
        print(f"[modbus-sensor] error enviando syslog: {exc}", flush=True)
    print(f"[modbus-sensor] {message}", flush=True)


def handle_packet(pkt) -> None:
    if not (pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt[TCP].dport == 502):
        return

    payload = bytes(pkt[Raw].load)
    if len(payload) < 8:
        return  # no llega ni a completar la cabecera MBAP + codigo de funcion

    unit_id = payload[6]
    function_code = payload[7]

    if function_code not in WRITE_FUNCTION_CODES:
        return

    src_ip = pkt[IP].src
    address = None
    value = None
    if len(payload) >= 12 and function_code in (5, 6):
        address = int.from_bytes(payload[8:10], "big")
        value = int.from_bytes(payload[10:12], "big")

    message = (
        "ModbusIDS: Unauthorized write detected "
        f"src={src_ip} function_code={function_code} "
        f'function_name="{WRITE_FUNCTION_CODES[function_code]}" '
        f"unit_id={unit_id}"
    )
    if address is not None:
        message += f" address={address} value={value}"

    send_alert(message)


if __name__ == "__main__":
    print("[modbus-sensor] iniciado, escuchando puerto 502...", flush=True)
    sniff(filter="tcp port 502", prn=handle_packet, store=False)
