"""
Genera el PDF de entrega de U4ACT02 - RESTCONF con Python.
Alumno: Sebastian Villegas Arredondo

Une: portada + guía original de Cisco (con la respuesta escrita en su espacio)
     + desarrollo con las capturas de evidencias/ y el código de los scripts.
Uso:  pip install -r requirements.txt  &&  python3 generar_pdf.py
"""
import io
import os
import tempfile

from PIL import Image as PI
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(BASE, "scripts")
EVID = os.path.join(BASE, "evidencias")
CISCO = os.path.join(BASE, "original", "U4ACT02 RESTCONF with Python.pdf")
OUT = os.path.join(BASE, "U4ACT02_RESTCONF_Python_Sebastian_Villegas_Arredondo.pdf")
TMP = tempfile.mkdtemp()
REPORT = os.path.join(TMP, "reporte.pdf")

ALUMNO = "Sebastian Villegas Arredondo"
ACCENT = colors.HexColor("#0B5CAD")

# Recorte de cada captura (x0, y0, x1, y1) sobre la imagen original de 3420x2224
RECORTES = {
    "01_codigo_lab25": (0, 80, 1500, 790),
    "02a_get_200_json": (0, 75, 1500, 2224),
    "02b_get_json_final": (0, 75, 1500, 2224),
    "03_codigo_part2": (126, 126, 2600, 1450),
    "04_put_201": (184, 258, 1404, 700),
    "05a_cli_antes": (58, 137, 1778, 1131),
    "05b_cli_loopback99": (58, 137, 1778, 1131),
    "06_codigo_delete": (126, 200, 2600, 1100),
    "07_delete_204": (184, 258, 1404, 700),
    "08_cli_despues": (58, 137, 1778, 1131),
    "09_gui_listar": (66, 145, 1867, 1644),
    "10_gui_desafio1_gi1": (66, 145, 1867, 1644),
    "11_gui_desafio2_showinfo_201": (17, 85, 2240, 1583),
    "12_gui_consultar_loopback74": (17, 85, 1812, 1583),
    "13_cli_loopback74": (58, 137, 1778, 1181),
    "14_gui_desafio3_askyesno": (17, 85, 1990, 1583),
    "15_gui_delete_204": (17, 85, 1812, 1583),
    "16_gui_error_404": (17, 85, 1812, 1583),
    "17_gui_error_401": (13, 87, 1810, 1586),
}


def recortar():
    for nombre, box in RECORTES.items():
        im = PI.open(os.path.join(EVID, nombre + ".png")).convert("RGB").crop(box)
        im.thumbnail((2000, 2000))
        im.save(os.path.join(TMP, nombre + ".jpg"), quality=88)


# Fuente monoespaciada para el código (Menlo trae los símbolos ✔ y ✖; si no existe se usa Courier)
FUENTE_CODIGO = "Courier"
try:
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    pdfmetrics.registerFont(TTFont("Menlo", "/System/Library/Fonts/Menlo.ttc", subfontIndex=0))
    FUENTE_CODIGO = "Menlo"
except Exception:
    pass

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=ACCENT, fontSize=17, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12.5, spaceBefore=8, spaceAfter=4)
P = ParagraphStyle("P", parent=ss["BodyText"], fontSize=10.5, leading=14.5, spaceAfter=6)
CAP = ParagraphStyle("CAP", parent=P, fontSize=9, leading=12, textColor=colors.HexColor("#4b5563"),
                     spaceBefore=3, spaceAfter=12)
CODE = ParagraphStyle("CODE", fontName=FUENTE_CODIGO, fontSize=6.8, leading=8.6, backColor=colors.HexColor("#f3f4f6"),
                      borderPadding=6, spaceBefore=4, spaceAfter=10)
ANS = ParagraphStyle("ANS", parent=P, backColor=colors.HexColor("#eef5fc"), borderPadding=8,
                     borderColor=ACCENT, borderWidth=0.6, spaceBefore=6, spaceAfter=12)
n_fig = [0]


def fig(nombre, texto, ancho=7.0):
    path = os.path.join(TMP, nombre + ".jpg")
    w, h = PI.open(path).size
    W = ancho * inch
    H = W * h / w
    if H > 6.6 * inch:                       # capturas muy altas: limitar altura
        H = 6.6 * inch
        W = H * w / h
    n_fig[0] += 1
    return KeepTogether([Image(path, width=W, height=H),
                         Paragraph(f"<b>Figura {n_fig[0]}.</b> {texto}", CAP)])


def codigo(archivo):
    with open(os.path.join(SCRIPTS, archivo), encoding="utf-8") as f:
        return Preformatted(f.read().rstrip(), CODE)


def tabla(filas, anchos, encabezado=True):
    s = ParagraphStyle("c", parent=P, fontSize=9, leading=11.5, spaceAfter=0)
    t = Table([[Paragraph(str(c), s) for c in r] for r in filas], colWidths=anchos)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db"))]
    if encabezado:
        st.append(("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dbe7f5")))
    t.setStyle(TableStyle(st))
    return t


def pie(c, doc):
    c.saveState()
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#6b7280"))
    c.drawString(0.75 * inch, 0.5 * inch, f"U4ACT02 - RESTCONF con Python  |  {ALUMNO}")
    c.restoreState()


def reporte():
    s = [Spacer(1, 1.6 * inch),
         Paragraph("U4ACT02", ParagraphStyle("k", parent=P, fontSize=12, textColor=ACCENT)),
         Paragraph("Práctica RESTCONF con Python", ParagraphStyle("T", parent=H1, fontSize=28, leading=34)),
         Spacer(1, 0.15 * inch),
         Paragraph("Consulta, creación y eliminación de configuración en un router Cisco IOS XE mediante "
                   "solicitudes RESTCONF enviadas desde scripts de Python con la librería requests.",
                   ParagraphStyle("st", parent=P, fontSize=12.5, leading=17)),
         Spacer(1, 0.6 * inch),
         tabla([["Alumno", ALUMNO],
                ["Matrícula", "1225100374"],
                ["Unidad / Actividad", "Unidad 4 - Actividad 02"],
                ["Equipo", "Cisco Catalyst 8000v, IOS XE 17.12 (DevNet Sandbox), 10.10.20.48"],
                ["Herramientas", "Python 3.14, requests, Tkinter, IDLE, OpenConnect (VPN), SSH"],
                ["Fecha", "11 de noviembre de 2026"]], [1.8 * inch, 4.6 * inch], encabezado=False),
         PageBreak()]

    s += [Paragraph("Desarrollo de la práctica y evidencias", ParagraphStyle("big", parent=H1, fontSize=20, leading=24)),
          Paragraph("Las páginas anteriores son la guía original de Cisco, con la respuesta escrita en su espacio. "
                    "A continuación se documenta cada paso con el código y las capturas de IDLE y de la CLI del router.", P),
          Paragraph("1. Entorno", H1),
          Paragraph("Se reservó la sandbox <b>IOS XE on Catalyst 8000v</b> de Cisco DevNet y se accedió por VPN con "
                    "OpenConnect. Los scripts se ejecutaron en <b>IDLE</b> con Python 3.14 y la librería <b>requests</b>. "
                    "Respecto a la guía, se ajustaron la IP del router (10.10.20.48) y las credenciales de la sandbox "
                    "(developer / C1sco12345). Cada script imprime el nombre del alumno, y la interfaz creada lleva la "
                    "descripción <i>\"Interfaz creada por Sebastian Villegas Arredondo\"</i>.", P),

          Paragraph("2. Parte 1 - RESTCONF en Python (GET)", H1),
          Paragraph("El script <b>lab 2.5.py</b> importa json y requests, desactiva las advertencias de SSL, define la URL "
                    "del contenedor <font face='Courier'>ietf-interfaces:interfaces</font>, los encabezados JSON y la "
                    "autenticación, y envía un GET con <font face='Courier'>requests.get()</font>. La respuesta se "
                    "convierte con <font face='Courier'>resp.json()</font> y se imprime con "
                    "<font face='Courier'>json.dumps(response_json, indent=4)</font>.", P),
          codigo("lab 2.5.py"),
          fig("01_codigo_lab25", "Script lab 2.5.py en el editor de IDLE."),
          fig("02a_get_200_json", "Ejecución (F5): el router responde 200 y se imprime el JSON con formato (inicio).", 5.2),
          fig("02b_get_json_final", "Continuación del JSON: GigabitEthernet1-3, Loopback0, 10, 109 y VirtualPortGroup0.", 5.2),

          Paragraph("3. Parte 2 - Crear Loopback99 con PUT", H1),
          Paragraph("El script <b>lab 2.5 part2.py</b> apunta a <font face='Courier'>.../interface=Loopback99</font> y "
                    "define el diccionario <font face='Courier'>yangConfig</font> con los datos de la interfaz. En Python el "
                    "booleano se escribe <font face='Courier'>True</font>. El diccionario se convierte a JSON con "
                    "<font face='Courier'>json.dumps()</font> y se envía con <font face='Courier'>requests.put()</font>; "
                    "si el código está entre 200 y 299 se imprime STATUS OK.", P),
          codigo("lab 2.5 part2.py"),
          fig("03_codigo_part2", "Script lab 2.5 part2.py con la descripción \"Interfaz creada por Sebastian Villegas Arredondo\"."),
          fig("04_put_201", "Ejecución: STATUS OK: 201 (Created), la interfaz no existía y se creó.", 4.5),
          fig("05a_cli_antes", "CLI del router antes de ejecutar el PUT: no existe Loopback99.", 5.5),
          fig("05b_cli_loopback99", "CLI después del PUT (sh ip int brief): aparece Loopback99 con 99.99.99.99.", 5.5),

          Paragraph("4. Eliminar Loopback99 con DELETE", H1),
          Paragraph("Para eliminar la interfaz se creó <b>lab 2.5 part2 delete.py</b> a partir del script anterior:", P),
          tabla([["Cambio", "Motivo"],
                 ["requests.put(...) se reemplazó por requests.delete(...)", "DELETE es el método HTTP que elimina el recurso indicado en la URL."],
                 ["Se quitó data=json.dumps(yangConfig) y el diccionario yangConfig", "DELETE no envía cuerpo; basta con la URL de la interfaz."],
                 ["La URL, los headers y basicauth no cambiaron", "Se sigue apuntando a .../interface=Loopback99 con la misma autenticación."]],
                [3.3 * inch, 3.7 * inch]),
          Spacer(1, 8),
          codigo("lab 2.5 part2 delete.py"),
          fig("06_codigo_delete", "Script lab 2.5 part2 delete.py con requests.delete()."),
          fig("07_delete_204", "Ejecución: STATUS OK: 204 (No Content), la interfaz se eliminó.", 4.5),
          fig("08_cli_despues", "CLI después del DELETE: Loopback99 ya no aparece.", 5.5),
          Paragraph("<b>Pregunta: ¿Qué cambios se aplicaron al código para eliminar la interfaz Loopback99?</b><br/>"
                    "Se cambió <font face='Courier'>requests.put()</font> por <font face='Courier'>requests.delete()</font> y "
                    "se eliminó el parámetro <font face='Courier'>data=json.dumps(yangConfig)</font> (y el diccionario "
                    "yangConfig), porque DELETE no lleva cuerpo. La URL con <font face='Courier'>interface=Loopback99</font>, "
                    "los encabezados y la autenticación se mantuvieron. El router respondió <b>204 No Content</b>.", ANS),

          PageBreak(),
          Paragraph("5. Desafíos - Interfaz gráfica con Tkinter", H1),
          Paragraph("Se desarrolló la aplicación <b>restconf_gui.py</b>, un cliente RESTCONF con ventana de Tkinter. "
                    "La IP del router, el usuario y la contraseña se escriben en la propia ventana, y cada botón llama "
                    "a una función que arma la petición con requests usando Basic Auth y los encabezados "
                    "application/yang-data+json. Las peticiones se hacen en segundo plano para que la ventana no se "
                    "congele mientras el router responde.", P),
          tabla([["Desafío", "Cómo se resolvió"],
                 ["1. Buscador de interfaces", "Campo tk.Entry para el nombre, botón \"Consultar Interfaz\" (requests.get) y una tabla ttk.Treeview con IP, máscara, si está habilitada y su estado (up/down). También hay un botón \"Listar todas\"."],
                 ["2. Formulario de creación", "Campos para nombre, IP, máscara y descripción. El botón \"Crear/Actualizar Interfaz\" arma el diccionario yangConfig y lo envía con requests.put(); si responde 200/201 sale messagebox.showinfo."],
                 ["3. Eliminación con confirmación", "El botón \"Eliminar Interfaz\" pregunta con messagebox.askyesno() y solo si se acepta hace requests.delete()."],
                 ["4. Barra de estado y errores", "Un tk.Label abajo que se pone verde con \"Operación exitosa\" o rojo con el error (401, 404, 500 o falta de conexión), capturado con try-except."]],
                [1.9 * inch, 5.1 * inch]),
          Spacer(1, 10),
          fig("09_gui_listar", "Ventana de la aplicación: \"Listar todas\" muestra las 7 interfaces del router con su IP, máscara y estado (200)."),
          fig("10_gui_desafio1_gi1", "Desafío 1: consulta de GigabitEthernet1 con el buscador. La barra de estado se pone verde."),
          fig("11_gui_desafio2_showinfo_201", "Desafío 2: el formulario crea Loopback74; el router responde 201 y aparece messagebox.showinfo con el JSON armado."),
          fig("12_gui_consultar_loopback74", "Consulta de Loopback74: descripción \"Interfaz creada por Sebastian Villegas Arredondo\", IP 74.74.74.74 y estado up."),
          fig("13_cli_loopback74", "Verificación en la CLI del router: Loopback74 con 74.74.74.74.", 5.5),
          fig("14_gui_desafio3_askyesno", "Desafío 3: antes de eliminar se pide confirmación con messagebox.askyesno()."),
          fig("15_gui_delete_204", "Después de confirmar: STATUS 204, Loopback74 eliminada (barra verde)."),
          fig("16_gui_error_404", "Desafío 4: al consultar una interfaz que ya no existe, la barra se pone roja con el error 404."),
          fig("17_gui_error_401", "Desafío 4: con una contraseña incorrecta la barra muestra el error 401 en rojo."),
          Paragraph("Código de la aplicación (restconf_gui.py)", H2),
          codigo("restconf_gui.py"),

          PageBreak(),
          Paragraph("6. Preguntas de reflexión", H1),
          Paragraph("¿Cómo se convierten los datos capturados en la GUI (tk.Entry) al diccionario yangConfig?", H2),
          Paragraph("Cada campo tk.Entry guarda texto. Al presionar el botón, el programa lee cada campo con "
                    "<font face='Courier'>.get()</font> (por ejemplo <font face='Courier'>self.f_ip.get()</font>), le quita "
                    "los espacios sobrantes con <font face='Courier'>.strip()</font> y lo coloca en su lugar dentro del "
                    "diccionario: el nombre en <i>name</i>, la descripción en <i>description</i> y la IP y la máscara dentro de "
                    "<i>ietf-ip:ipv4 → address</i>. La casilla \"Habilitada\" usa un <font face='Courier'>tk.BooleanVar</font>, "
                    "que devuelve True o False para <i>enabled</i>. Al final, <font face='Courier'>json.dumps(yangConfig)</font> "
                    "convierte el diccionario en texto JSON, que es lo que se manda en el body del PUT.", P),
          Paragraph("¿Qué ventaja tiene usar eventos y funciones manejadoras (callbacks) en lugar de scripts lineales?", H2),
          Paragraph("Un script lineal hace siempre lo mismo y termina; para cambiar la interfaz o la IP hay que editar el código "
                    "y volver a correrlo. Con Tkinter, cada botón tiene una función asociada "
                    "(<font face='Courier'>command=self.consultar</font>, <font face='Courier'>command=self.crear</font>…) que "
                    "solo se ejecuta cuando el usuario la pide, con los datos que escribió en ese momento. Así una sola "
                    "aplicación sirve para consultar, crear y borrar cuantas veces se quiera sin tocar el código. Además, "
                    "cada acción maneja sus propios errores: un 401 o un 404 se muestran en la barra de estado y el programa "
                    "sigue funcionando, y como las peticiones van en segundo plano, la ventana no se congela mientras "
                    "el router responde.", P),

          Paragraph("7. Resultados", H1),
          tabla([["Script", "Método", "Código", "Resultado"],
                 ["lab 2.5.py", "GET", "200 OK", "JSON con todas las interfaces"],
                 ["lab 2.5 part2.py", "PUT", "201 Created", "Loopback99 creada (99.99.99.99/24)"],
                 ["lab 2.5 part2 delete.py", "DELETE", "204 No Content", "Loopback99 eliminada"],
                 ["restconf_gui.py - Consultar / Listar", "GET", "200 OK", "Datos en la tabla de la ventana"],
                 ["restconf_gui.py - Crear", "PUT", "201 Created", "Loopback74 creada + showinfo"],
                 ["restconf_gui.py - Eliminar", "DELETE", "204 No Content", "Loopback74 eliminada tras askyesno"],
                 ["restconf_gui.py - Errores", "GET", "404 / 401", "Barra de estado en rojo"]],
                [2.0 * inch, 0.9 * inch, 1.3 * inch, 2.8 * inch]),
          Paragraph("8. Conclusión", H1),
          Paragraph("Con Python y la librería requests se reproducen las mismas operaciones RESTCONF que en Postman, pero "
                    "de forma automatizable: la URL, los encabezados y la autenticación se guardan en variables, los datos "
                    "YANG se escriben como diccionarios de Python y el código de estado permite validar el resultado sin "
                    "revisar la respuesta a mano. Cambiar de una operación a otra (crear o eliminar) solo requiere cambiar "
                    "el método de requests y el cuerpo enviado. Al llevarlo a una interfaz gráfica con Tkinter, cualquier "
                    "persona puede consultar, crear y eliminar interfaces con botones y formularios, con confirmaciones "
                    "antes de borrar y mensajes claros cuando algo falla.", P)]

    doc = SimpleDocTemplate(REPORT, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.8 * inch)
    doc.build(s, onFirstPage=pie, onLaterPages=pie)


def respuesta_cisco(c):
    """Escribe la respuesta de la pregunta y. en la página 4 de la guía de Cisco."""
    lineas = [
        "Se cambió requests.put(...) por requests.delete(...) y se quitó el parámetro",
        "data=json.dumps(yangConfig) (y el diccionario yangConfig), porque DELETE no envía cuerpo.",
        "La URL (interface=Loopback99), los headers y basicauth no cambian. Respuesta: STATUS OK: 204.",
    ]
    x, y_top, w, size = 90, 668, 470, 8.5
    h = (size + 3) * len(lineas) + 8
    y = 792 - y_top - h
    c.setFillColor(colors.HexColor("#EEF5FC"))
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.6)
    c.rect(x, y, w, h, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#111827"))
    c.setFont("Helvetica", size)
    ty = y + h - 4 - size
    for ln in lineas:
        c.drawString(x + 6, ty, ln)
        ty -= size + 3


def nota_desafios(c):
    """Recuadro en la página 5 de la guía indicando dónde están resueltos los desafíos."""
    lineas = [
        "Desafíos 1 a 4 resueltos en la aplicación restconf_gui.py (sección 5 y Figuras 11-19):",
        "1) Buscador con tk.Entry + requests.get() y tabla ttk.Treeview con IP, máscara y estado.",
        "2) Formulario que arma yangConfig y lo envía con requests.put(): 201 + messagebox.showinfo.",
        "3) Botón Eliminar con messagebox.askyesno() antes de requests.delete(): 204.",
        "4) Barra de estado verde (200/201/204) y roja (401/404/sin conexión) con try-except.",
    ]
    x, y_top, w, size = 72, 600, 468, 8.5
    h = (size + 3) * len(lineas) + 8
    y = 792 - y_top - h
    c.setFillColor(colors.HexColor("#EEF5FC"))
    c.setStrokeColor(ACCENT)
    c.setLineWidth(0.6)
    c.rect(x, y, w, h, fill=1, stroke=1)
    ty = y + h - 4 - size
    for i, ln in enumerate(lineas):
        c.setFillColor(ACCENT if i == 0 else colors.HexColor("#111827"))
        c.setFont("Helvetica-Bold" if i == 0 else "Helvetica", size)
        c.drawString(x + 6, ty, ln)
        ty -= size + 3


def capa(dibujar):
    from pypdf import PdfReader
    from reportlab.pdfgen import canvas as rl_canvas
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=letter)
    dibujar(c)
    c.save()
    buf.seek(0)
    return PdfReader(buf).pages[0]


def unir():
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas as rl_canvas
    rep, cisco = PdfReader(REPORT), PdfReader(CISCO)
    w = PdfWriter()
    w.add_page(rep.pages[0])
    for i, pg in enumerate(cisco.pages):
        nueva = w.add_page(pg)
        if i == 3:
            nueva.merge_page(capa(respuesta_cisco))
        if i == 4:
            nueva.merge_page(capa(nota_desafios))
    for pg in rep.pages[1:]:
        w.add_page(pg)
    w.add_metadata({"/Title": "U4ACT02 - RESTCONF con Python", "/Author": ALUMNO})
    with open(OUT, "wb") as f:
        w.write(f)
    print("PDF generado:", OUT, f"({len(w.pages)} páginas)")


if __name__ == "__main__":
    recortar()
    reporte()
    unir()
