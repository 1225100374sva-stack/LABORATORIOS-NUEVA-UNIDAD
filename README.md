# U4ACT01 – RESTCONF con Postman

**Alumno:** Sebastian Villegas Arredondo
**Equipo:** Cisco Catalyst 8000v, IOS XE 17.12 (DevNet Sandbox), `10.10.20.48`

Práctica de consulta, creación, modificación y eliminación de configuración en un router
Cisco IOS XE mediante RESTCONF y modelos YANG, usando Postman.

## Contenido

```
U4ACT01-RESTCONF/
├── U4ACT01_RESTCONF_Sebastian_Villegas_Arredondo.pdf   # Entrega: guía de Cisco con respuestas + evidencias
├── README.md
├── original/
│   └── U4ACT01 RESTCONF with Postman.pdf               # Guía original de la actividad
├── evidencias/                                         # 20 capturas (Postman y CLI del router)
└── scripts/
    ├── U4ACT01-RESTCONF.postman_collection.json        # Colección de Postman "coleccion u3"
    ├── restconf_u4act01.py                             # La práctica completa en Python
    ├── conectar-vpn.sh                                 # Conexión a la VPN de la sandbox (OpenConnect)
    ├── generar_pdf.py                                  # Genera el PDF de entrega
    └── requirements.txt                                # Dependencias de generar_pdf.py
```

## Solicitudes realizadas

| Parte | Método | URI (`/restconf/data/...`) | Código |
|---|---|---|---|
| Desafío 1 | GET | `Cisco-IOS-XE-native:native` (JSON y XML) | 200 |
| Parte 2 | GET | `ietf-interfaces:interfaces` (XML y JSON) | 200 |
| Parte 2 | GET | `ietf-interfaces:interfaces/interface=Loopback0` | 200 |
| Parte 2 | GET | `ietf-interfaces:interfaces-state` | 200 |
| Desafío 2 | GET | `ietf-interfaces:interfaces/interface=GigabitEthernet1` | 200 |
| Parte 3 | PUT / DELETE | `ietf-interfaces:interfaces/interface=Loopback99` | 201 / 204 |
| Desafío 3 | PUT | `ietf-interfaces:interfaces/interface=Loopback74` | 201 |
| Desafío 4 | PATCH | `ietf-interfaces:interfaces/interface=Loopback74` (`enabled: false`) | 204 |
| Desafío 5 | DELETE | `ietf-interfaces:interfaces/interface=Loopback74` | 204 |
| Reflexión | GET / POST | credenciales malas, URI mal escrita, JSON roto, Content-Type incorrecto | 401 / 404 / 400 / 415 |

Todas las solicitudes llevan el encabezado `X-Alumno: Sebastian Villegas Arredondo`, y la
Loopback74 se creó con la descripción *"Interfaz creada por Sebastian Villegas Arredondo"*.

## Cómo usarlo

1. Reservar la sandbox *IOS XE on Catalyst 8000v* en DevNet y conectar la VPN:
   ```bash
   ./scripts/conectar-vpn.sh <usuario_vpn> <endpoint:puerto>
   ```
2. **Postman:** importar `scripts/U4ACT01-RESTCONF.postman_collection.json`, desactivar
   *SSL certificate verification* y enviar las solicitudes en orden.
3. **Python** (sin dependencias externas):
   ```bash
   python3 scripts/restconf_u4act01.py
   ```
4. **Regenerar el PDF:**
   ```bash
   pip install -r scripts/requirements.txt
   python3 scripts/generar_pdf.py
   ```
