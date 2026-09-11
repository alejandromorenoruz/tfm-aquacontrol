FROM debian:bookworm-slim

# Herramientas para el ataque Modbus (Fase 3 del TFM): escaneo + lectura/escritura de registros
# Nota de reproducibilidad: se usa Debian en lugar de kalilinux/kali-rolling porque los
# mirrors de Kali resultaron poco fiables al reconstruir la imagen en un ordenador distinto
# (fallo real detectado durante la prueba de reproducibilidad de este TFM). Las mismas
# herramientas (nmap, mbpoll) estan disponibles como paquetes oficiales de Debian, con una
# red de mirrors mucho mas redundante.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        nmap \
        mbpoll \
        python3-pip \
        iproute2 \
        net-tools \
        curl \
    && pip install --break-system-packages pymodbus \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /root
CMD ["/bin/bash"]
