#!/usr/bin/env python3
"""
U4ACT01 - RESTCONF con Postman (versión en script)
Alumno: Sebastian Villegas Arredondo

Reproduce todas las solicitudes de la práctica contra el Catalyst 8000v
de la DevNet Sandbox (IOS XE 17.12) usando solo la librería estándar.
Requiere la VPN de la sandbox conectada.

Uso:  python3 restconf_u4act01.py
"""
import base64
import json
import ssl
import urllib.error
import urllib.request

HOST = "10.10.20.48"
USER = "developer"
PASSWORD = "C1sco12345"
ALUMNO = "Sebastian Villegas Arredondo"
LOOPBACK_ID = 74  # últimas dos cifras de la matrícula

BASE = f"https://{HOST}/restconf/data"
JSON = "application/yang-data+json"
XML = "application/yang-data+xml"

# La sandbox usa un certificado autofirmado (equivale a SSL verification OFF en Postman)
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def restconf(method, path, body=None, accept=JSON, ctype=JSON,
             user=USER, password=PASSWORD, raw_body=None):
    """Envía una solicitud RESTCONF y devuelve (status, texto de respuesta)."""
    url = path if path.startswith("http") else BASE + path
    data = raw_body.encode() if raw_body is not None else (
        json.dumps(body).encode() if body is not None else None)
    token = base64.b64encode(f"{user}:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {token}", "Accept": accept,
               "Content-Type": ctype, "X-Alumno": ALUMNO}
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=30) as r:
            return r.status, r.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def loopback(n, ip, description, enabled=True):
    return {"ietf-interfaces:interface": {
        "name": f"Loopback{n}",
        "description": description,
        "type": "iana-if-type:softwareLoopback",
        "enabled": enabled,
        "ietf-ip:ipv4": {"address": [{"ip": ip, "netmask": "255.255.255.0"}]},
    }}


def paso(titulo, esperado, status, texto, mostrar=400):
    ok = "OK " if status == esperado else "ERR"
    print(f"[{ok}] {titulo}: HTTP {status} (esperado {esperado})")
    if texto and mostrar:
        print("     " + texto[:mostrar].replace("\n", "\n     "))


def main():
    n = LOOPBACK_ID
    lo = f"/ietf-interfaces:interfaces/interface=Loopback{n}"
    print(f"=== U4ACT01 RESTCONF - {ALUMNO} ===\n")

    # Parte 1 / Desafío 1: configuración global en JSON y XML
    paso("GET native (JSON)", 200, *restconf("GET", "/Cisco-IOS-XE-native:native"), mostrar=200)
    paso("GET native (XML)", 200, *restconf("GET", "/Cisco-IOS-XE-native:native", accept=XML, ctype=XML), mostrar=200)

    # Parte 2: interfaces
    paso("GET interfaces (JSON)", 200, *restconf("GET", "/ietf-interfaces:interfaces"), mostrar=0)
    paso("GET datos operacionales (interfaces-state)", 200,
         *restconf("GET", "/ietf-interfaces:interfaces-state"), mostrar=0)
    paso("Desafío 2 - GET GigabitEthernet1", 200,
         *restconf("GET", "/ietf-interfaces:interfaces/interface=GigabitEthernet1"))

    # Desafío 3: crear Loopback propia
    paso(f"Desafío 3 - PUT Loopback{n}", 201,
         *restconf("PUT", lo, loopback(n, f"{n}.{n}.{n}.{n}", f"Interfaz creada por {ALUMNO}")))
    paso(f"GET Loopback{n}", 200, *restconf("GET", lo))

    # Desafío 4: PATCH -> deshabilitar y cambiar descripción
    patch = {"ietf-interfaces:interface": {
        "name": f"Loopback{n}",
        "description": f"Interfaz creada por {ALUMNO} - deshabilitada con PATCH",
        "enabled": False}}
    paso(f"Desafío 4 - PATCH Loopback{n}", 204, *restconf("PATCH", lo, patch))
    paso(f"GET Loopback{n} tras PATCH", 200, *restconf("GET", lo))

    # Desafío 5: eliminar
    paso(f"Desafío 5 - DELETE Loopback{n}", 204, *restconf("DELETE", lo))

    # Reflexión: errores provocados
    paso("401 - credenciales incorrectas", 401,
         *restconf("GET", "/ietf-interfaces:interfaces", password="Cisco123"), mostrar=0)
    paso("404 - URL mal escrita", 404, *restconf("GET", "/ietf-interfaces:interfases"), mostrar=0)
    paso("400 - JSON mal formado", 400,
         *restconf("POST", "/ietf-interfaces:interfaces",
                   raw_body='{"ietf-interfaces:interface": {"name": "Loopback74" "enabled": true}'))
    paso("415 - Content-Type incorrecto", 415,
         *restconf("POST", "/ietf-interfaces:interfaces",
                   loopback(n, "10.0.0.1", f"Prueba 415 - {ALUMNO}"), ctype="text/plain"))


if __name__ == "__main__":
    main()
