# U4ACT02 - Interfaz gráfica para RESTCONF con Tkinter
# Alumno: Sebastian Villegas Arredondo
#
# Desafío 1: buscar una interfaz y mostrar su IP, máscara y estado.
# Desafío 2: formulario para crear o actualizar una interfaz (PUT).
# Desafío 3: botón para eliminar una interfaz, pidiendo confirmación (DELETE).
# Desafío 4: barra de estado verde o roja y manejo de errores.

import json
import queue
import threading
import tkinter as tk
from tkinter import messagebox, ttk

import requests

# Quitar las advertencias de SSL
requests.packages.urllib3.disable_warnings()

ALUMNO = "Sebastian Villegas Arredondo"

# Encabezados para trabajar con JSON
HEADERS = {"Accept": "application/yang-data+json",
           "Content-type": "application/yang-data+json"}

# Colores de la barra de estado
VERDE = "#1b7f3b"
ROJO = "#c62828"
GRIS = "#555555"

# Interfaz que no se debe tocar porque es por donde nos conectamos al router
PROTEGIDAS = {"GigabitEthernet1"}

# Mensajes para los errores más comunes
MENSAJES_ERROR = {
    400: "400 Bad Request: datos mal formados",
    401: "401 Unauthorized: usuario o contraseña incorrectos",
    404: "404 Not Found: la interfaz no existe",
    409: "409 Conflict: el recurso ya existe",
    500: "500 Internal Server Error: error en el router",
}


class RestconfApp:
    def __init__(self, root):
        self.root = root
        root.title(f"Cliente RESTCONF - {ALUMNO}")
        root.geometry("900x720")
        root.minsize(820, 640)

        # Títulos
        ttk.Label(root, text="Cliente RESTCONF - Cisco IOS XE",
                  font=("Helvetica", 18, "bold")).pack(pady=(12, 0))
        ttk.Label(root, text=f"Alumno: {ALUMNO}", font=("Helvetica", 12)).pack(pady=(0, 8))

        cuerpo = ttk.Frame(root, padding=(14, 0))
        cuerpo.pack(fill="both", expand=True)

        # ----- Sección de conexión: IP del router, usuario y contraseña -----
        con = ttk.LabelFrame(cuerpo, text="Conexión", padding=8)
        con.pack(fill="x", pady=4)
        self.host = self._campo(con, "Router (IP):", "10.10.20.48", 0, 0, 16)
        self.usuario = self._campo(con, "Usuario:", "developer", 0, 2, 14)
        self.password = self._campo(con, "Contraseña:", "C1sco12345", 0, 4, 14, show="*")

        # ----- Desafío 1: buscar interfaz -----
        con1 = ttk.LabelFrame(cuerpo, text="Desafío 1 - Consultar interfaz (GET)", padding=8)
        con1.pack(fill="both", expand=True, pady=4)
        fila = ttk.Frame(con1)
        fila.pack(fill="x")
        ttk.Label(fila, text="Interfaz:").pack(side="left")
        self.buscar = ttk.Entry(fila, width=22)
        self.buscar.insert(0, "GigabitEthernet1")
        self.buscar.pack(side="left", padx=6)
        self.buscar.bind("<Return>", lambda e: self.consultar())  # Enter también consulta
        ttk.Button(fila, text="Consultar Interfaz", command=self.consultar).pack(side="left", padx=4)
        ttk.Button(fila, text="Listar todas", command=self.listar).pack(side="left", padx=4)

        # Tabla donde se muestran los resultados
        cols = ("interfaz", "descripcion", "ip", "mascara", "admin", "oper")
        titulos = ("Interfaz", "Descripción", "IP", "Máscara", "Habilitada", "Estado")
        anchos = (130, 260, 105, 105, 80, 70)
        self.tabla = ttk.Treeview(con1, columns=cols, show="headings", height=7)
        for c, t, w in zip(cols, titulos, anchos):
            self.tabla.heading(c, text=t)
            self.tabla.column(c, width=w, anchor="w")
        self.tabla.pack(fill="both", expand=True, pady=(8, 0))
        self.tabla.bind("<<TreeviewSelect>>", self._seleccion)

        # ----- Desafíos 2 y 3: formulario para crear, actualizar y eliminar -----
        form = ttk.LabelFrame(cuerpo, text="Desafíos 2 y 3 - Crear / Actualizar / Eliminar interfaz", padding=8)
        form.pack(fill="x", pady=4)
        self.f_nombre = self._campo(form, "Nombre:", "Loopback74", 0, 0, 18)
        self.f_ip = self._campo(form, "Dirección IP:", "74.74.74.74", 0, 2, 16)
        self.f_mascara = self._campo(form, "Máscara:", "255.255.255.0", 0, 4, 16)
        ttk.Label(form, text="Descripción:").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        self.f_desc = ttk.Entry(form, width=60)
        self.f_desc.insert(0, f"Interfaz creada por {ALUMNO}")
        self.f_desc.grid(row=1, column=1, columnspan=4, sticky="we", padx=4, pady=4)
        self.f_habilitada = tk.BooleanVar(value=True)
        ttk.Checkbutton(form, text="Habilitada", variable=self.f_habilitada).grid(row=1, column=5, sticky="w")
        botones = ttk.Frame(form)
        botones.grid(row=2, column=0, columnspan=6, pady=(6, 0))
        ttk.Button(botones, text="Crear/Actualizar Interfaz", command=self.crear).pack(side="left", padx=6)
        ttk.Button(botones, text="Eliminar Interfaz", command=self.eliminar).pack(side="left", padx=6)

        # ----- Desafío 4: barra de estado abajo -----
        self.estado = tk.Label(root, text="Listo", anchor="w", fg="white", bg=GRIS,
                               font=("Helvetica", 12, "bold"), padx=12, pady=8)
        self.estado.pack(fill="x", side="bottom")

        # Cola para recibir las respuestas del router sin congelar la ventana
        self.cola = queue.Queue()
        self.root.after(100, self._revisar_cola)

    # ---------- Funciones de ayuda ----------

    def _campo(self, padre, texto, valor, fila, col, ancho, show=None):
        """Crea una etiqueta con su cuadro de texto."""
        ttk.Label(padre, text=texto).grid(row=fila, column=col, sticky="e", padx=4, pady=4)
        if show:
            e = ttk.Entry(padre, width=ancho, show=show)
        else:
            e = ttk.Entry(padre, width=ancho)
        e.insert(0, valor)
        e.grid(row=fila, column=col + 1, sticky="w", padx=4, pady=4)
        return e

    def _estado(self, texto, color):
        """Cambia el texto y el color de la barra de estado."""
        self.estado.config(text=texto, bg=color)

    def _fallo(self, mensaje):
        """Muestra un error en rojo."""
        self._estado(f"✖ {mensaje}", ROJO)

    def _seleccion(self, _evento):
        """Al hacer clic en una fila, pone su nombre en el buscador."""
        sel = self.tabla.selection()
        if sel:
            nombre = self.tabla.item(sel[0], "values")[0]
            self.buscar.delete(0, "end")
            self.buscar.insert(0, nombre)

    def _conexion(self):
        """Lee la IP, el usuario y la contraseña escritos en la ventana."""
        base = f"https://{self.host.get().strip()}/restconf/data/"
        auth = (self.usuario.get().strip(), self.password.get())
        return base, auth

    def _revisar_cola(self):
        """Revisa cada 100 ms si ya llegó una respuesta y la muestra."""
        try:
            while True:
                al_terminar, resultado, error = self.cola.get_nowait()
                al_terminar(resultado, error)
        except queue.Empty:
            pass
        self.root.after(100, self._revisar_cola)

    def _ejecutar(self, descripcion, trabajo, al_terminar):
        """Hace la petición en segundo plano para que la ventana no se congele.
        Si falla la red, el error se atrapa con try-except."""
        self._estado(f"{descripcion}...", GRIS)

        def hilo():
            try:
                self.cola.put((al_terminar, trabajo(), None))
            except requests.exceptions.ConnectTimeout:
                self.cola.put((al_terminar, None, "Tiempo de espera agotado: el router no responde (¿VPN conectada?)"))
            except requests.exceptions.ConnectionError:
                self.cola.put((al_terminar, None, "Error de conexión: no se pudo llegar al router (¿VPN conectada?)"))
            except requests.exceptions.RequestException as e:
                self.cola.put((al_terminar, None, f"Error de red: {e}"))

        threading.Thread(target=hilo, daemon=True).start()

    def _error_http(self, resp):
        """Arma el mensaje de error con el código y lo que respondió el router."""
        mensaje = MENSAJES_ERROR.get(resp.status_code, f"Error HTTP {resp.status_code}")
        try:
            detalle = resp.json()["ietf-restconf:errors"]["error"][0].get("error-message")
            if detalle:
                mensaje += f" ({detalle})"
        except (ValueError, KeyError, IndexError, TypeError):
            pass
        return mensaje

    @staticmethod
    def _fila(cfg, oper):
        """Saca de la respuesta JSON los datos que van en la tabla."""
        direcciones = (cfg.get("ietf-ip:ipv4") or {}).get("address") or [{}]
        nombre = cfg.get("name", "")
        return (nombre,
                cfg.get("description", ""),
                direcciones[0].get("ip", "-"),
                direcciones[0].get("netmask", "-"),
                "Sí" if cfg.get("enabled") else "No",
                oper.get(nombre, "-"))

    @staticmethod
    def _oper(base, auth, nombre=None):
        """Pide si la interfaz está up o down (interfaces-state)."""
        recurso = "ietf-interfaces:interfaces-state"
        if nombre:
            recurso += f"/interface={nombre}"
        r = requests.get(base + recurso, auth=auth, headers=HEADERS, verify=False, timeout=15)
        if r.status_code != 200:
            return {}
        datos = r.json()
        lista = datos.get("ietf-interfaces:interface") or datos.get(
            "ietf-interfaces:interfaces-state", {}).get("interface", [])
        return {i["name"]: i.get("oper-status", "-") for i in lista}

    # ---------- Desafío 1: consultar (GET) ----------

    def consultar(self):
        nombre = self.buscar.get().strip()
        if not nombre:
            self._fallo("Escribe el nombre de una interfaz")
            return
        base, auth = self._conexion()

        def trabajo():
            r = requests.get(base + f"ietf-interfaces:interfaces/interface={nombre}",
                             auth=auth, headers=HEADERS, verify=False, timeout=15)
            oper = self._oper(base, auth, nombre) if r.status_code == 200 else {}
            return r, oper

        def fin(res, error):
            if error:
                return self._fallo(error)
            r, oper = res
            if r.status_code != 200:
                return self._fallo(self._error_http(r))
            # Llenar la tabla con la interfaz encontrada
            self.tabla.delete(*self.tabla.get_children())
            for cfg in r.json()["ietf-interfaces:interface"]:
                self.tabla.insert("", "end", values=self._fila(cfg, oper))
            self._estado(f"✔ STATUS {r.status_code}: Operación exitosa - {nombre} consultada", VERDE)

        self._ejecutar(f"Consultando {nombre}", trabajo, fin)

    def listar(self):
        base, auth = self._conexion()

        def trabajo():
            r = requests.get(base + "ietf-interfaces:interfaces", auth=auth,
                             headers=HEADERS, verify=False, timeout=15)
            oper = self._oper(base, auth) if r.status_code == 200 else {}
            return r, oper

        def fin(res, error):
            if error:
                return self._fallo(error)
            r, oper = res
            if r.status_code != 200:
                return self._fallo(self._error_http(r))
            # Llenar la tabla con todas las interfaces
            interfaces = r.json()["ietf-interfaces:interfaces"]["interface"]
            self.tabla.delete(*self.tabla.get_children())
            for cfg in interfaces:
                self.tabla.insert("", "end", values=self._fila(cfg, oper))
            self._estado(f"✔ STATUS {r.status_code}: Operación exitosa - {len(interfaces)} interfaces", VERDE)

        self._ejecutar("Consultando todas las interfaces", trabajo, fin)

    # ---------- Desafío 2: crear o actualizar (PUT) ----------

    def crear(self):
        nombre = self.f_nombre.get().strip()
        if nombre in PROTEGIDAS:
            self._fallo(f"{nombre} es la interfaz de administración y no se puede modificar")
            return
        if not nombre:
            self._fallo("El nombre de la interfaz es obligatorio")
            return

        # Armar el diccionario yangConfig con lo que se escribió en el formulario
        yangConfig = {
            "ietf-interfaces:interface": {
                "name": nombre,
                "description": self.f_desc.get().strip(),
                "type": "iana-if-type:softwareLoopback",
                "enabled": self.f_habilitada.get(),
                "ietf-ip:ipv4": {
                    "address": [{"ip": self.f_ip.get().strip(),
                                 "netmask": self.f_mascara.get().strip()}]
                },
                "ietf-ip:ipv6": {}
            }
        }
        base, auth = self._conexion()

        def trabajo():
            return requests.put(base + f"ietf-interfaces:interfaces/interface={nombre}",
                                data=json.dumps(yangConfig), auth=auth,
                                headers=HEADERS, verify=False, timeout=15)

        def fin(r, error):
            if error:
                return self._fallo(error)
            if r.status_code in (200, 201, 204):
                accion = "creada" if r.status_code == 201 else "actualizada"
                self._estado(f"✔ STATUS {r.status_code}: Operación exitosa - {nombre} {accion}", VERDE)
                # Ventana de aviso con el resultado
                messagebox.showinfo("Operación exitosa",
                                    f"Interfaz {nombre} {accion} correctamente.\n\n"
                                    f"Código HTTP: {r.status_code}\n\n"
                                    f"JSON enviado:\n{json.dumps(yangConfig, indent=2, ensure_ascii=False)}")
            else:
                self._fallo(self._error_http(r))

        self._ejecutar(f"Enviando PUT de {nombre}", trabajo, fin)

    # ---------- Desafío 3: eliminar (DELETE) con confirmación ----------

    def eliminar(self):
        nombre = self.f_nombre.get().strip()
        if nombre in PROTEGIDAS:
            self._fallo(f"{nombre} es la interfaz de administración y no se puede modificar")
            return
        if not nombre:
            self._fallo("Escribe el nombre de la interfaz a eliminar")
            return

        # Preguntar antes de borrar
        if not messagebox.askyesno("Confirmar eliminación",
                                   f"¿Seguro que deseas eliminar la interfaz {nombre}?\n\n"
                                   "Esta acción modifica la configuración del router."):
            self._estado(f"Eliminación de {nombre} cancelada", GRIS)
            return
        base, auth = self._conexion()

        def trabajo():
            return requests.delete(base + f"ietf-interfaces:interfaces/interface={nombre}",
                                   auth=auth, headers=HEADERS, verify=False, timeout=15)

        def fin(r, error):
            if error:
                return self._fallo(error)
            if r.status_code in (200, 204):
                self._estado(f"✔ STATUS {r.status_code}: Operación exitosa - {nombre} eliminada", VERDE)
            else:
                self._fallo(self._error_http(r))

        self._ejecutar(f"Eliminando {nombre}", trabajo, fin)


# Abrir la ventana
if __name__ == "__main__":
    root = tk.Tk()
    RestconfApp(root)
    root.mainloop()
