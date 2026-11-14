# U4ACT02 - RESTCONF con Python - Parte 1
# Alumno: Sebastian Villegas Arredondo
# Consulta las interfaces del router (ietf-interfaces) con un GET de RESTCONF.

# Paso 1: importar módulos y desactivar las advertencias de SSL
import json
import requests
requests.packages.urllib3.disable_warnings()

print("Alumno: Sebastian Villegas Arredondo")

# Paso 2: componentes de la solicitud
api_url = "https://10.10.20.48/restconf/data/ietf-interfaces:interfaces"

headers = {"Accept": "application/yang-data+json",
           "Content-type": "application/yang-data+json"
           }

basicauth = ("developer", "C1sco12345")

# Paso 3: enviar la solicitud
resp = requests.get(api_url, auth=basicauth, headers=headers, verify=False)
print("Código de estado:", resp.status_code)

# Paso 4: evaluar la respuesta
response_json = resp.json()
print(json.dumps(response_json, indent=4))
