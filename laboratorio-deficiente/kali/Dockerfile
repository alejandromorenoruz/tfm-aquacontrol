FROM kalilinux/kali-rolling

# Herramientas para el ataque Modbus (Fase 3 del TFM): escaneo + lectura/escritura de registros
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
