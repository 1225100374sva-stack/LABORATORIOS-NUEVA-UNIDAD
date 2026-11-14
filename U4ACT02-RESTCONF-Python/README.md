# U4ACT02 – RESTCONF con Python

**Alumno:** Sebastian Villegas Arredondo
**Equipo:** Cisco Catalyst 8000v, IOS XE 17.12 (DevNet Sandbox), `10.10.20.48`

Envío de solicitudes RESTCONF desde Python con la librería `requests`: consulta de
interfaces (GET), creación de Loopback99 (PUT) y su eliminación (DELETE). Además, una
aplicación con interfaz gráfica en **Tkinter** (`restconf_gui.py`) que resuelve los 4 desafíos.

## Contenido

```
U4ACT02-RESTCONF-Python/
├── U4ACT02_RESTCONF_Python_Sebastian_Villegas_Arredondo.pdf   # Entrega: guía de Cisco con respuesta + evidencias
├── README.md
├── original/                    # Guía original de la actividad
├── evidencias/                  # Capturas de IDLE, de la app Tkinter y de la CLI del router
└── scripts/
    ├── lab 2.5.py               # Parte 1: GET de ietf-interfaces (200)
    ├── lab 2.5 part2.py         # Parte 2: PUT crea Loopback99 (201)
    ├── lab 2.5 part2 delete.py  # Parte 2: DELETE elimina Loopback99 (204)
    ├── restconf_gui.py          # Desafíos 1-4: aplicación con interfaz gráfica (Tkinter)
    ├── abrir-idle.sh            # Abre IDLE con el entorno virtual del proyecto
    ├── generar_pdf.py           # Genera el PDF de entrega
    └── requirements.txt
```

## Resultados

| Script | Método | Código | Resultado |
|---|---|---|---|
| `lab 2.5.py` | GET | 200 OK | JSON con todas las interfaces |
| `lab 2.5 part2.py` | PUT | 201 Created | Loopback99 creada (99.99.99.99/24), descripción "Interfaz creada por Sebastian Villegas Arredondo" |
| `lab 2.5 part2 delete.py` | DELETE | 204 No Content | Loopback99 eliminada |

**¿Qué cambios se aplicaron para eliminar Loopback99?** Se cambió `requests.put()` por
`requests.delete()` y se quitó `data=json.dumps(yangConfig)`, porque DELETE no envía cuerpo.
La URL, los encabezados y la autenticación no cambian.

## Aplicación Tkinter (`restconf_gui.py`)

| Desafío | Qué hace |
|---|---|
| 1. Buscador de interfaces | Campo para el nombre, botón **Consultar Interfaz** (`requests.get`) y tabla con IP, máscara y estado. Botón **Listar todas**. |
| 2. Formulario de creación | Campos de nombre, IP, máscara y descripción. **Crear/Actualizar Interfaz** arma `yangConfig` y hace `requests.put`; si responde 200/201 aparece `messagebox.showinfo`. |
| 3. Eliminación con confirmación | **Eliminar Interfaz** pregunta con `messagebox.askyesno` antes de `requests.delete`. |
| 4. Barra de estado | Verde cuando sale bien (200/201/204) y roja con el error (401, 404, 500 o sin conexión), usando `try-except`. |

La IP del router, el usuario y la contraseña se escriben en la ventana. Las peticiones se
hacen en segundo plano para que la ventana no se congele, y la app no permite modificar
GigabitEthernet1 (la interfaz de administración).

## Cómo ejecutarlo

```bash
python3 -m venv .venv
.venv/bin/pip install -r scripts/requirements.txt
cd scripts
../.venv/bin/python "lab 2.5.py"
../.venv/bin/python "lab 2.5 part2.py"
../.venv/bin/python "lab 2.5 part2 delete.py"
../.venv/bin/python restconf_gui.py     # abre la interfaz gráfica
../.venv/bin/python generar_pdf.py      # regenera el PDF
```

Se requiere la VPN de la sandbox DevNet conectada. Rama de entrega: `feat/unidad4_act02`.
