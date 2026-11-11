# U4ACT02 - RESTCONF con Python - Parte 2 (eliminar)
# Alumno: Sebastian Villegas Arredondo
# Elimina la interfaz Loopback99 con un DELETE de RESTCONF.
#
# Cambios respecto a "lab 2.5 part2.py":
#   1. requests.put(...) se cambió por requests.delete(...)
#   2. Se quitó el parámetro data=json.dumps(yangConfig) y el diccionario yangConfig,
#      porque DELETE no envía cuerpo.
#   La URL (interface=Loopback99), los headers y la autenticación no cambian.

import json
import requests
requests.packages.urllib3.disable_warnings()

print("Alumno: Sebastian Villegas Arredondo")

api_url = "https://10.10.20.48/restconf/data/ietf-interfaces:interfaces/interface=Loopback99"

headers = {"Accept": "application/yang-data+json",
           "Content-type": "application/yang-data+json"
           }

basicauth = ("developer", "C1sco12345")

resp = requests.delete(api_url, auth=basicauth, headers=headers, verify=False)

if (resp.status_code >= 200 and resp.status_code <= 299):
    print("STATUS OK: {}".format(resp.status_code))
else:
    print("Error code {}, reply: {}".format(resp.status_code, resp.json()))
