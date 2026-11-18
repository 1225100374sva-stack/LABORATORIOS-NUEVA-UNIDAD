import io
import os
import tempfile
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak,
                                Table, TableStyle, KeepTogether, Preformatted)

# Rutas relativas a la carpeta del proyecto (este script vive en scripts/)
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVID = os.path.join(BASE, "evidencias")
CISCO = os.path.join(BASE, "original", "U4ACT01 RESTCONF with Postman.pdf")
OUT = os.path.join(BASE, "U4ACT01_RESTCONF_Sebastian_Villegas_Arredondo.pdf")
CROP = tempfile.mkdtemp()
REPORT = os.path.join(CROP, "reporte.pdf")


def recortar_capturas():
    """Recorta cada captura para que se lea en la hoja.

    Postman: arriba la franja del encabezado (nombre del workspace del alumno) y
    abajo solo el panel de la solicitud/respuesta, sin barras laterales. Ambas
    piezas salen de la misma captura original (evidencias/ conserva el original).
    """
    from PIL import Image as PI
    for f in sorted(os.listdir(EVID)):
        if not f.endswith(".png"):
            continue
        im = PI.open(os.path.join(EVID, f)).convert("RGB")
        if f.startswith("10"):                                   # captura de la Terminal
            c = im
        else:
            if f.startswith(("01", "02")):                       # ventana de Postman al centro
                cab, panel = (818, 293, 2243, 359), (1092, 427, 2516, 1886)
            else:                                                # Postman maximizado
                cab, panel = (391, 93, 2316, 166), (884, 232, 2809, 2174)
            a, b = im.crop(cab), im.crop(panel)
            c = PI.new("RGB", (b.width, a.height + 6 + b.height), (90, 90, 90))
            c.paste(a, (0, 0))
            c.paste(b, (0, a.height + 6))
        c.thumbnail((2400, 2400))
        c.save(os.path.join(CROP, f.replace(".png", ".jpg")), quality=88)


recortar_capturas()
ALUMNO = "Sebastian Villegas Arredondo"
ACCENT = colors.HexColor("#0B5CAD")

ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], textColor=ACCENT, fontSize=17, spaceBefore=6, spaceAfter=8)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], textColor=colors.HexColor("#1f2937"), fontSize=13, spaceBefore=10, spaceAfter=4)
P = ParagraphStyle("P", parent=ss["BodyText"], fontSize=10.5, leading=14.5, spaceAfter=6)
CAP = ParagraphStyle("CAP", parent=P, fontSize=9, leading=12, textColor=colors.HexColor("#4b5563"), spaceBefore=3, spaceAfter=12)
CODE = ParagraphStyle("CODE", fontName="Courier", fontSize=8.5, leading=11, backColor=colors.HexColor("#f3f4f6"),
                      borderPadding=6, spaceBefore=4, spaceAfter=10)
ANS = ParagraphStyle("ANS", parent=P, backColor=colors.HexColor("#eef5fc"), borderPadding=8,
                     borderColor=ACCENT, borderWidth=0.6, spaceBefore=6, spaceAfter=12)

W = 7.0 * inch
fig_n = [0]


def fig(name, caption):
    from PIL import Image as PI
    path = os.path.join(CROP, name + ".jpg")
    w, h = PI.open(path).size
    fig_n[0] += 1
    img = Image(path, width=W, height=W * h / w)
    return KeepTogether([img, Paragraph(f"<b>Figura {fig_n[0]}.</b> {caption}", CAP)])


def code(text):
    return Preformatted(text, CODE)


def table(rows, widths, header=True):
    t = Table(rows, colWidths=widths)
    st = [("FONT", (0, 0), (-1, -1), "Helvetica", 9),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
          ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5)]
    if header:
        st += [("BACKGROUND", (0, 0), (-1, 0), ACCENT), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
               ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9)]
    t.setStyle(TableStyle(st))
    return t


def para_rows(rows):
    s = ParagraphStyle("cell", parent=P, fontSize=9, leading=11.5, spaceAfter=0)
    return [[Paragraph(str(c), s) for c in r] for r in rows]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6b7280"))
    canvas.drawString(0.75 * inch, 0.5 * inch, f"U4ACT01 - RESTCONF con Postman  |  {ALUMNO}")
    canvas.restoreState()


s = []
# ---------- Portada ----------
s += [Spacer(1, 1.6 * inch),
      Paragraph("U4ACT01", ParagraphStyle("k", parent=P, fontSize=12, textColor=ACCENT)),
      Paragraph("Práctica RESTCONF con Postman", ParagraphStyle("T", parent=H1, fontSize=28, leading=34)),
      Spacer(1, 0.15 * inch),
      Paragraph("Consulta, creación, modificación y eliminación de configuración en un router Cisco "
                "IOS XE mediante la API RESTCONF y modelos YANG.", ParagraphStyle("st", parent=P, fontSize=12.5, leading=17)),
      Spacer(1, 0.6 * inch)]
s.append(table(para_rows([
    ["Alumno", ALUMNO],
    ["Matrícula", "1225100374"],
    ["Unidad / Actividad", "Unidad 4 - Actividad 01"],
    ["Equipo", "Cisco Catalyst 8000v, IOS XE 17.12 (DevNet Sandbox)"],
    ["Herramientas", "Postman, OpenConnect (VPN), SSH, Python 3"],
    ["Fecha", "10 de noviembre de 2026"],
]), [1.8 * inch, 4.6 * inch], header=False))
s.append(PageBreak())

# ---------- Introducción ----------
s += [Paragraph("Desarrollo de la práctica y evidencias", ParagraphStyle("big", parent=H1, fontSize=20, leading=24)),
      Paragraph("Las páginas anteriores son la guía original de Cisco con las respuestas escritas en los espacios correspondientes. A continuación se documenta cada paso con capturas de Postman, cuyas figuras se citan en esas respuestas.", P),
      Paragraph("1. Introducción y entorno", H1),
      Paragraph("RESTCONF (RFC 8040) es una interfaz HTTP que expone los datos de configuración y operación de un "
                "dispositivo de red según sus modelos YANG. Cada recurso tiene una URI bajo <font face='Courier'>/restconf/data/</font> "
                "y se manipula con los métodos HTTP estándar (GET, POST, PUT, PATCH, DELETE), usando JSON o XML.", P),
      Paragraph("Para esta práctica se reservó la sandbox <b>IOS XE on Catalyst 8000v</b> de Cisco DevNet. El acceso al "
                "router (10.10.20.48) se realizó por VPN con OpenConnect, y todas las solicitudes se enviaron desde Postman "
                "dentro de la colección <b>coleccion u3</b>. Para identificar al autor, cada solicitud incluye el encabezado "
                "personalizado <font face='Courier'>X-Alumno: Sebastian Villegas Arredondo</font>, y las interfaces creadas llevan "
                "su nombre en la descripción.", P)]
s.append(table(para_rows([
    ["Parámetro", "Valor"],
    ["URL base", "https://10.10.20.48/restconf/data/"],
    ["Autenticación", "Basic Auth (developer / C1sco12345)"],
    ["Encabezados", "Content-Type y Accept: application/yang-data+json o application/yang-data+xml; X-Alumno"],
    ["Loopback asignada", "Loopback74 (últimas dos cifras de la matrícula), IP 74.74.74.74/24"],
]), [1.8 * inch, 5.2 * inch]))

# ---------- Parte 1 ----------
s += [Paragraph("2. Parte 1 - Configuración de Postman y Desafío 1", H1),
      Paragraph("Primero se desactivó la verificación del certificado SSL, ya que el router usa un certificado autofirmado. "
                "La autenticación Basic Auth se definió a nivel de colección para que todas las solicitudes la hereden.", P),
      fig("01_ssl_off", "Postman: <i>SSL certificate verification</i> en OFF."),
      Paragraph("<b>Desafío 1.</b> Se consultó la configuración global del router "
                "(<font face='Courier'>GET /restconf/data/Cisco-IOS-XE-native:native</font>). Entre ambas solicitudes solo se "
                "cambiaron los encabezados <b>Accept</b> y <b>Content-Type</b>: con <font face='Courier'>application/yang-data+json</font> "
                "el router responde en JSON, y con <font face='Courier'>application/yang-data+xml</font> responde en XML.", P),
      fig("02_native_json", "GET native con encabezados JSON (X-Alumno visible). Respuesta 200 OK en JSON."),
      fig("03_native_xml", "GET native con encabezados XML. Respuesta 200 OK en XML; solo cambiaron los headers.")]

# ---------- Parte 2 ----------
s += [Paragraph("3. Parte 2 - Consulta de interfaces", H1),
      Paragraph("Se consultó el contenedor <font face='Courier'>interfaces</font> del modelo <b>ietf-interfaces</b>, primero en "
                "XML y luego en JSON. Después se consultó una sola interfaz agregando su clave a la URI "
                "(<font face='Courier'>/interface=Loopback0</font>). En esta sandbox no existe Loopback1, así que se usó Loopback0.", P),
      fig("04_interfaces_xml", "GET ietf-interfaces:interfaces en XML (200 OK)."),
      fig("05_interfaces_json", "GET ietf-interfaces:interfaces en JSON (200 OK)."),
      fig("06_loopback0", "GET de una sola interfaz: Loopback0 (200 OK)."),
      Paragraph("<b>Datos operacionales.</b> Los contadores y el estado de las interfaces no están en el contenedor de "
                "configuración, sino en <font face='Courier'>interfaces-state</font>.", P),
      fig("07_interfaces_state", "GET ietf-interfaces:interfaces-state: admin-status, oper-status, velocidad y estadísticas."),
      Paragraph("<b>Pregunta: ¿Cuál es la nueva URL?</b><br/>"
                "<font face='Courier'>https://10.10.20.48/restconf/data/ietf-interfaces:interfaces-state</font><br/>"
                "El modelo ietf-interfaces separa la configuración (<i>interfaces</i>) del estado operacional y las estadísticas "
                "(<i>interfaces-state</i>), donde aparecen oper-status, phys-address, speed y los contadores in/out.", ANS),
      Paragraph("<b>Desafío 2.</b> En lugar de pedir todas las interfaces, se modificó la URI para consultar solo GigabitEthernet1 en JSON:", P),
      code("GET https://10.10.20.48/restconf/data/ietf-interfaces:interfaces/interface=GigabitEthernet1"),
      fig("08_desafio2_gi1", "Desafío 2: solo GigabitEthernet1 en JSON (200 OK).")]

# ---------- Parte 3 ----------
s += [Paragraph("4. Parte 3 - Creación y eliminación de Loopback99", H1),
      Paragraph("Con el método <b>PUT</b> sobre la URI de la interfaz se creó Loopback99 con la IP 99.99.99.99/24. El cuerpo de la solicitud fue:", P),
      code('{\n  "ietf-interfaces:interface": {\n    "name": "Loopback99",\n'
           '    "description": "Loopback99 - Sebastian Villegas Arredondo",\n'
           '    "type": "iana-if-type:softwareLoopback",\n    "enabled": true,\n'
           '    "ietf-ip:ipv4": {"address": [{"ip": "99.99.99.99", "netmask": "255.255.255.0"}]}\n  }\n}'),
      fig("09_put_loopback99_201", "PUT Loopback99: el router responde 201 Created (el recurso no existía)."),
      fig("10_cli_show_ip_int_brief", "Verificación por SSH en la CLI del router: <i>show ip interface brief</i> muestra Loopback99 con 99.99.99.99."),
      fig("11_delete_loopback99", "DELETE Loopback99: 204 No Content."),
      Paragraph("<b>Pregunta: ¿Qué cambios fueron necesarios para eliminar la interfaz?</b><br/>"
                "Solo se cambió el método HTTP de <b>PUT</b> a <b>DELETE</b>, conservando la misma URI "
                "(<font face='Courier'>.../ietf-interfaces:interfaces/interface=Loopback99</font>), y se quitó el cuerpo (body), "
                "porque DELETE no envía datos. El router respondió <b>204 No Content</b>.", ANS)]

# ---------- Desafíos 3-5 ----------
s += [Paragraph("5. Desafíos 3, 4 y 5 - Loopback74", H1),
      Paragraph("<b>Desafío 3 (crear).</b> Se creó la interfaz <b>Loopback74</b> (últimas dos cifras de la matrícula) con la "
                "descripción <i>\"Interfaz creada por Sebastian Villegas Arredondo\"</i> y la IP 74.74.74.74/24:", P),
      code('PUT https://10.10.20.48/restconf/data/ietf-interfaces:interfaces/interface=Loopback74\n\n'
           '{\n  "ietf-interfaces:interface": {\n    "name": "Loopback74",\n'
           '    "description": "Interfaz creada por Sebastian Villegas Arredondo",\n'
           '    "type": "iana-if-type:softwareLoopback",\n    "enabled": true,\n'
           '    "ietf-ip:ipv4": {"address": [{"ip": "74.74.74.74", "netmask": "255.255.255.0"}]}\n  }\n}'),
      fig("12_desafio3_put_loopback74_201", "Desafío 3: PUT Loopback74, respuesta 201 Created."),
      fig("13_verificar_loopback74", "Verificación: el router devuelve Loopback74 con la descripción \"Interfaz creada por Sebastian Villegas Arredondo\"."),
      Paragraph("<b>Desafío 4 (modificar con PATCH).</b> PATCH modifica solo los campos enviados, sin reemplazar el recurso "
                "completo. Se deshabilitó la interfaz y se actualizó la descripción:", P),
      code('PATCH .../ietf-interfaces:interfaces/interface=Loopback74\n\n'
           '{\n  "ietf-interfaces:interface": {\n    "name": "Loopback74",\n'
           '    "description": "Interfaz creada por Sebastian Villegas Arredondo - deshabilitada con PATCH",\n'
           '    "enabled": false\n  }\n}'),
      fig("14_desafio4_patch_204", "Desafío 4: PATCH Loopback74, respuesta 204 No Content."),
      fig("15_verificar_patch", "Verificación del PATCH: \"enabled\": false y descripción actualizada; la IP se conservó."),
      Paragraph("<b>Desafío 5 (eliminar).</b> Se eliminó Loopback74 con DELETE sobre la misma URI.", P),
      fig("16_desafio5_delete_204", "Desafío 5: DELETE Loopback74, respuesta 204 No Content.")]

# ---------- Errores ----------
s += [Paragraph("6. Errores provocados y depuración", H1),
      Paragraph("Para comprender los códigos de error de RESTCONF se provocaron cuatro fallos a propósito. En cada caso el "
                "router devuelve un objeto <font face='Courier'>ietf-restconf:errors</font> que indica la causa.", P),
      fig("17_error_401", "Credenciales incorrectas (developer / Cisco123): 401 Unauthorized, error-tag access-denied."),
      fig("18_error_404", "URI mal escrita (ietf-interfaces:interfases): 404 Not Found, \"uri keypath not found\"."),
      fig("19_error_400", "POST con JSON mal formado (falta una coma): 400 Bad Request, malformed-message / Syntax error."),
      fig("20_error_415", "POST con Content-Type: text/plain: 415 Unsupported Media Type; el router indica los tipos aceptados.")]

# ---------- Reflexión ----------
s += [PageBreak(), Paragraph("7. Preguntas de reflexión y análisis", H1),
      Paragraph("<b>¿Qué encabezado HTTP le indica al servidor en qué formato queremos recibir la información?</b>", H2),
      Paragraph("El encabezado <b>Accept</b>. Con <font face='Courier'>Accept: application/yang-data+json</font> el router "
                "responde en JSON, y con <font face='Courier'>application/yang-data+xml</font> (o sin Accept, porque XML es el "
                "valor por defecto) responde en XML. Los datos son los mismos porque vienen del mismo modelo YANG; solo cambia "
                "la codificación. JSON es más compacto y fácil de procesar en scripts, mientras que XML usa etiquetas y "
                "espacios de nombres (xmlns) que reflejan directamente el modelo YANG. En cambio, <b>Content-Type</b> indica el "
                "formato de los datos que <i>enviamos</i> en el body; por eso, al ponerlo en text/plain se obtuvo un 415.", P),
      Paragraph("<b>¿Qué código de estado devuelve el router tras eliminar exitosamente la interfaz?</b>", H2),
      Paragraph("<b>204 No Content</b>: la operación se realizó correctamente y la respuesta no trae cuerpo, porque no hay "
                "nada que devolver.", P),
      Paragraph("<b>Diferencia entre los métodos HTTP utilizados</b>", H2)]
s.append(table(para_rows([
    ["Método", "Uso en RESTCONF", "Respuesta obtenida"],
    ["GET", "Lee datos de configuración u operación. No modifica nada.", "200 OK con los datos"],
    ["POST", "Crea un recurso hijo dentro del contenedor padre (por ejemplo, en /interfaces). Si ya existe, falla (409).", "201 Created / 400 / 415 en las pruebas"],
    ["PUT", "Crea o reemplaza por completo el recurso indicado en la URI.", "201 si no existía; 204 si lo reemplazó"],
    ["PATCH", "Modifica solo los campos enviados y conserva el resto.", "204 No Content"],
    ["DELETE", "Elimina el recurso indicado en la URI. No lleva body.", "204 No Content"],
]), [0.9 * inch, 3.9 * inch, 2.2 * inch]))
s += [Spacer(1, 10), Paragraph("<b>Significado de los códigos de estado obtenidos</b>", H2)]
s.append(table(para_rows([
    ["Código", "Significado", "Cuándo apareció"],
    ["200 OK", "Solicitud exitosa con datos en la respuesta.", "Todas las consultas GET"],
    ["201 Created", "El recurso se creó.", "PUT de Loopback99 y Loopback74"],
    ["204 No Content", "Éxito sin cuerpo de respuesta.", "PATCH, DELETE y PUT sobre un recurso existente"],
    ["400 Bad Request", "El cuerpo tiene errores de sintaxis.", "POST con JSON mal formado"],
    ["401 Unauthorized", "Credenciales inválidas o ausentes.", "Basic Auth con contraseña incorrecta"],
    ["404 Not Found", "La URI no corresponde a ningún recurso del modelo.", "URI con \"interfases\""],
    ["415 Unsupported Media Type", "El Content-Type enviado no es aceptado.", "POST con text/plain"],
]), [1.6 * inch, 3.0 * inch, 2.4 * inch]))
s += [Spacer(1, 6), Paragraph(
    "Observación: el primer PUT de Loopback99 que se envió devolvió 204 en lugar de 201 porque la interfaz ya existía de un "
    "envío anterior. Esto confirma que PUT es <i>idempotente</i>: crea el recurso si no existe y lo reemplaza si ya existe.", P)]

# ---------- Scripts ----------
s += [Paragraph("8. Archivos entregados en el repositorio", H1),
      Paragraph("Junto con este documento se entregan en GitHub (rama <font face='Courier'>feat/unidad4_act01</font>):", P)]
s.append(table(para_rows([
    ["Archivo", "Descripción"],
    ["U4ACT01-RESTCONF.postman_collection.json", "Colección de Postman \"coleccion u3\" exportada con las 18 solicitudes, la autenticación y una prueba automática del código esperado en cada solicitud."],
    ["restconf_u4act01.py", "Script en Python (solo librería estándar) que reproduce toda la práctica e indica OK/ERR según el código de estado esperado."],
    ["conectar-vpn.sh", "Script para conectar la VPN de la sandbox con OpenConnect (las credenciales se piden al ejecutarlo)."],
    ["generar_pdf.py", "Script que arma este PDF: recorta las capturas, escribe las respuestas sobre la guía de Cisco y une todo."],
    ["evidencias/", "Las 20 capturas de pantalla de este reporte."],
    ["original/", "La guía original de Cisco de la actividad."],
]), [2.6 * inch, 4.4 * inch]))
s += [Spacer(1, 8), Paragraph("Salida del script de Python ejecutado contra el router:", P),
      code("[OK ] GET native (JSON): HTTP 200 (esperado 200)\n"
           "[OK ] GET native (XML): HTTP 200 (esperado 200)\n"
           "[OK ] GET interfaces (JSON): HTTP 200 (esperado 200)\n"
           "[OK ] GET datos operacionales (interfaces-state): HTTP 200 (esperado 200)\n"
           "[OK ] Desafío 2 - GET GigabitEthernet1: HTTP 200 (esperado 200)\n"
           "[OK ] Desafío 3 - PUT Loopback74: HTTP 201 (esperado 201)\n"
           "[OK ] GET Loopback74: HTTP 200 (esperado 200)\n"
           "[OK ] Desafío 4 - PATCH Loopback74: HTTP 204 (esperado 204)\n"
           "[OK ] GET Loopback74 tras PATCH: HTTP 200 (esperado 200)\n"
           "[OK ] Desafío 5 - DELETE Loopback74: HTTP 204 (esperado 204)\n"
           "[OK ] 401 - credenciales incorrectas: HTTP 401 (esperado 401)\n"
           "[OK ] 404 - URL mal escrita: HTTP 404 (esperado 404)\n"
           "[OK ] 400 - JSON mal formado: HTTP 400 (esperado 400)\n"
           "[OK ] 415 - Content-Type incorrecto: HTTP 415 (esperado 415)"),
      Paragraph("9. Conclusión", H1),
      Paragraph("RESTCONF permite administrar un router como si fuera un servicio web: cada parte de la configuración tiene "
                "una URI derivada de su modelo YANG, y basta con elegir el método HTTP correcto para leerla, crearla, "
                "modificarla o eliminarla. En la práctica se comprobó que los encabezados Accept y Content-Type controlan el "
                "formato de los datos, que PUT, PATCH y DELETE tienen efectos distintos sobre un recurso, y que los códigos de "
                "estado y los mensajes ietf-restconf:errors facilitan mucho la depuración. Esto hace que las tareas de red se "
                "puedan automatizar y repetir con herramientas como Postman o scripts en Python, en lugar de configurarlas a "
                "mano en la CLI.", P)]

doc = SimpleDocTemplate(REPORT, pagesize=letter, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                        topMargin=0.7 * inch, bottomMargin=0.8 * inch,
                        title="U4ACT01 - RESTCONF con Postman", author=ALUMNO)
doc.build(s, onFirstPage=footer, onLaterPages=footer)


# ---------- Respuestas escritas sobre el documento original de Cisco ----------
def overlay_page(dibujar):
    """Crea una página transparente con texto que luego se superpone al PDF de Cisco."""
    from reportlab.pdfgen import canvas as rl_canvas
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=letter)
    dibujar(c)
    c.save()
    buf.seek(0)
    from pypdf import PdfReader
    return PdfReader(buf).pages[0]


AZUL = colors.HexColor("#0B5CAD")
FONDO = colors.HexColor("#EEF5FC")


def caja(c, x, y_top, w, lineas, size=9, titulo=None):
    """Dibuja un recuadro azul con texto. y_top se mide desde arriba de la página."""
    lh = size + 3
    h = lh * len(lineas) + (lh + 2 if titulo else 0) + 8
    y = 792 - y_top - h
    c.setFillColor(FONDO)
    c.setStrokeColor(AZUL)
    c.setLineWidth(0.6)
    c.rect(x, y, w, h, fill=1, stroke=1)
    ty = y + h - 4 - size
    if titulo:
        c.setFillColor(AZUL)
        c.setFont("Helvetica-Bold", size)
        c.drawString(x + 6, ty, titulo)
        ty -= lh + 2
    for ln in lineas:
        fuente, texto = ln if isinstance(ln, tuple) else ("Helvetica", ln)
        c.setFillColor(colors.HexColor("#111827"))
        c.setFont(fuente, size)
        c.drawString(x + 6, ty, texto)
        ty -= lh


def pagina3(c):
    # Parte 2, Paso 3 b: "What is the new URL?"
    caja(c, 90, 355, 470, [
        ("Courier-Bold", "https://10.10.20.48/restconf/data/ietf-interfaces:interfaces-state"),
        "Contenedor de estado operacional y estadísticas (oper-status, speed, contadores). Ver Figura 7.",
    ], size=8.5)


def pagina4(c):
    # Parte 3 h: cambios para eliminar la interfaz
    caja(c, 90, 179.5, 470, [
        "Solo se cambió el método PUT por DELETE en la misma URI (.../interface=Loopback99), sin body. Resultado: 204 No Content.",
    ], size=7.5)
    # Respuestas a las preguntas de reflexión
    caja(c, 90, 540, 470, [
        "1. El encabezado Accept. Con application/yang-data+json responde en JSON y con application/yang-data+xml",
        "    (o sin Accept) responde en XML. Content-Type, en cambio, indica el formato de lo que se envía.",
        "2. 204 No Content: la interfaz se eliminó y la respuesta no trae cuerpo (Figuras 11 y 16).",
        "3. developer / Cisco123  ->  401 Unauthorized, error-tag access-denied (Figura 17).",
        "4. /ietf-interfaces:interfases  ->  404 Not Found, \"uri keypath not found\" (Figura 18).",
        "5. JSON sin una coma  ->  400 Bad Request (Figura 19).  Content-Type: text/plain  ->  415 (Figura 20).",
        "Desafíos 1 a 5 resueltos con Loopback74 (\"Interfaz creada por Sebastian Villegas Arredondo\"): Figuras 2-3, 8, 12-16.",
    ], size=8.5, titulo="Respuestas - Sebastian Villegas Arredondo")


def unir():
    from pypdf import PdfReader, PdfWriter
    reporte = PdfReader(REPORT)
    cisco = PdfReader(CISCO)
    w = PdfWriter()
    w.add_page(reporte.pages[0])                      # portada
    for i, pg in enumerate(cisco.pages):              # documento de Cisco con respuestas
        nueva = w.add_page(pg)
        if i == 2:
            nueva.merge_page(overlay_page(pagina3))
        if i == 3:
            nueva.merge_page(overlay_page(pagina4))
    for pg in reporte.pages[1:]:                      # desarrollo y evidencias
        w.add_page(pg)
    w.add_metadata({"/Title": "U4ACT01 - RESTCONF con Postman", "/Author": ALUMNO})
    with open(OUT, "wb") as f:
        w.write(f)
    print("PDF generado:", OUT, f"({len(w.pages)} páginas)")


unir()
