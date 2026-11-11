# U4ACT02 - RESTCONF con Python - Parte 2
# Alumno: Sebastian Villegas Arredondo
# Crea la interfaz Loopback99 con un PUT de RESTCONF.

# Paso 6: importar módulos y desactivar las advertencias de SSL
import json
import requests
requests.packages.urllib3.disable_warnings()

print("Alumno: Sebastian Villegas Arredondo")

# Paso 7: componentes de la solicitud
api_url = "https://10.10.20.48/restconf/data/ietf-interfaces:interfaces/interface=Loopback99"

headers = {"Accept": "application/yang-data+json",
           "Content-type": "application/yang-data+json"
           }

basicauth = ("developer", "C1sco12345")

yangConfig = {
    "ietf-interfaces:interface": {
        "name": "Loopback99",
        "description": "Interfaz creada por Sebastian Villegas Arredondo",
        "type": "iana-if-type:softwareLoopback",
        "enabled": True,
        "ietf-ip:ipv4": {
            "address": [
                {
                    "ip": "99.99.99.99",
                    "netmask": "255.255.255.0"
                }
            ]
        },
        "ietf-ip:ipv6": {}
    }
}

# Paso 8: enviar la solicitud PUT
resp = requests.put(api_url, data=json.dumps(yangConfig), auth=basicauth,
                    headers=headers, verify=False)

if (resp.status_code >= 200 and resp.status_code <= 299):
    print("STATUS OK: {}".format(resp.status_code))
else:
    print("Error code {}, reply: {}".format(resp.status_code, resp.json()))
