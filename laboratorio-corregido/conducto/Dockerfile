FROM alpine:3.20

RUN apk add --no-cache socat

# Conducto unico controlado (IEC 62443): solo reenvia el trafico de gestion
# web de OpenPLC (8080) desde la red IT hacia la red OT. El puerto Modbus
# (502) NO se reenvia -> queda inalcanzable desde IT.
CMD ["socat", "TCP-LISTEN:8080,fork,reuseaddr", "TCP:172.31.0.10:8080"]
