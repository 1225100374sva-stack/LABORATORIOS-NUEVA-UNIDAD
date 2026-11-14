#!/bin/zsh
# Conecta a la VPN de la sandbox DevNet (Catalyst 8000v) con OpenConnect.
# Uso: ./conectar-vpn.sh <usuario_vpn> <endpoint:puerto>
# La contraseña de la VPN se pide al ejecutar (no se guarda en el repositorio).
sudo openconnect --protocol=anyconnect --background --user="$1" "$2"
