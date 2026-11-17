"""
generar_pdf.py
U4ACT03 - DevOps con Python y GitHub Actions
Autor: Sebastian Villegas Arredondo

Genera el PDF de entrega:
  1. Portada.
  2. La guía original con cada respuesta escrita (en azul) en su espacio.
  3. Anexo de evidencias (capturas de evidencias/) y el código documentado.

Uso:  pip install reportlab pypdf pillow  &&  python3 scripts/generar_pdf.py
Si falta una captura, en su lugar aparece un recuadro "Captura pendiente".
"""
import io
import os

from PIL import Image as PI
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer)

# ----------------------------------------------------------------- rutas y datos
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(BASE)
EVID = os.path.join(BASE, "evidencias")
GUIA = os.path.join(BASE, "original", "U4ACT03 DevOps con python A.pdf")
OUT = os.path.join(BASE, "U4ACT03_DevOps_Python_Sebastian_Villegas_Arredondo.pdf")

ALUMNO = "Sebastian Villegas Arredondo"
FECHA = "17/11/2026"
CLASE = ""                      # escribe aquí el nombre/grupo de la clase si lo piden
REPO_URL = "github.com/1225100374sva-stack/LABORATORIOS-NUEVA-UNIDAD"
AZUL = colors.HexColor("#0B4FA0")
H = 792                          # alto de la página carta en puntos

# Capturas: (archivo en evidencias/, pie de figura)
FIGURAS = [
    ("01_pytest_local.png", "Pruebas locales: <b>pytest -v</b> en mi computadora, 5 passed."),
    ("02_actions_verde.png", "Pestaña Actions, primer push: el workflow <b>CI del validador de correos</b> "
                             "con los jobs <b>test → deploy</b> en check verde."),
    ("03_log_deploy.png", "Log del job <b>deploy</b>: se ejecutó después de test y simuló el despliegue."),
    ("04_actions_rojo.png", "Push con la prueba rota a propósito: <b>test</b> falla (cruz roja) y "
                            "<b>deploy</b> queda omitido (skipped)."),
    ("05_log_error.png", "Log del job test que falló: <b>AssertionError: assert True == False</b> "
                         "en test_correo_valido."),
    ("06_actions_corregido.png", "Push con la corrección: los dos jobs vuelven al check verde."),
]

# ----------------------------------------------------------------- fuentes
SUP = "/System/Library/Fonts/Supplemental/"
pdfmetrics.registerFont(TTFont("AU", SUP + "Arial Unicode.ttf"))      # símbolos ✔ └ ├
for nombre, archivo in [("AR", "Arial.ttf"), ("AR-B", "Arial Bold.ttf"),
                        ("AR-I", "Arial Italic.ttf"), ("AR-BI", "Arial Bold Italic.ttf")]:
    pdfmetrics.registerFont(TTFont(nombre, SUP + archivo))
pdfmetrics.registerFontFamily("AR", normal="AR", bold="AR-B", italic="AR-I", boldItalic="AR-BI")
F = "AR"
SIM = "<font name='AU'>%s</font>"            # para escribir símbolos dentro de un párrafo
MONO = "Courier"
try:
    pdfmetrics.registerFont(TTFont("Menlo", "/System/Library/Fonts/Menlo.ttc", subfontIndex=0))
    MONO = "Menlo"
except Exception:
    pass


def estilo(tam, fuente=F, color=AZUL):
    return ParagraphStyle("r", fontName=fuente, fontSize=tam, leading=tam * 1.22, textColor=color)


# ----------------------------------------------------------------- dibujo sobre la guía
def caja(c, x0, y0, x1, y1, html, tam=10.0, fuente=F, tapar=True):
    """Escribe html dentro del rectángulo (coordenadas con origen arriba-izquierda).
    Reduce la letra hasta que el texto quepa. tapar=True borra las líneas punteadas."""
    w, h = x1 - x0, y1 - y0
    if tapar:
        c.setFillColor(colors.white)
        c.rect(x0 - 2, H - y1 - 2, w + 4, h + 4, stroke=0, fill=1)
    while True:
        p = Paragraph(html, estilo(tam, fuente))
        _, ph = p.wrap(w, h)
        if ph <= h or tam <= 6:
            break
        tam -= 0.25
    p.drawOn(c, x0, H - y0 - ph)


def texto(c, x, y, s, tam=9, fuente=F):
    c.setFont(fuente, tam)
    c.setFillColor(AZUL)
    c.drawString(x, H - y, s)


def marcar(c, x0, y0, x1, y1):
    """Encierra una opción de opción múltiple y pone una palomita."""
    c.setStrokeColor(AZUL)
    c.setLineWidth(1.2)
    c.roundRect(x0 - 4, H - y1 - 3, x1 - x0 + 8, y1 - y0 + 6, 4, stroke=1, fill=0)
    c.setFont("AU", 13)
    c.setFillColor(AZUL)
    c.drawString(x1 + 8, H - y1, "✔")


def miniatura(c, nombre, x0, y0, x1, y1):
    ruta = os.path.join(EVID, nombre)
    c.setFillColor(colors.white)
    c.rect(x0 - 2, H - y1 - 2, x1 - x0 + 4, y1 - y0 + 4, stroke=0, fill=1)
    if not os.path.exists(ruta):
        pendiente(c, x0, y0, x1, y1)
        return
    w, h = PI.open(ruta).size
    W, Hh = x1 - x0, y1 - y0
    esc = min(W / w, Hh / h)
    c.drawImage(ruta, x0, H - y0 - h * esc, w * esc, h * esc)


def pendiente(c, x0, y0, x1, y1):
    c.setStrokeColor(colors.HexColor("#d14343"))
    c.setDash(3, 2)
    c.rect(x0, H - y1, x1 - x0, y1 - y0)
    c.setDash()
    c.setFont(F, 9)
    c.setFillColor(colors.HexColor("#d14343"))
    c.drawCentredString((x0 + x1) / 2, H - (y0 + y1) / 2, "Captura pendiente")


def nombre_fecha(c, y, x_nombre=342, x_fecha=520, clase_x=None):
    texto(c, x_nombre, y - 1, ALUMNO, 8.5)
    texto(c, x_fecha, y - 1, FECHA, 8.5)
    if clase_x and CLASE:
        texto(c, clase_x, y - 1, CLASE, 8.5)


# Respuestas por página (página de la guía, empezando en 1)
def pagina(c, n):
    if n == 1:
        nombre_fecha(c, 40)
    elif n == 2:
        caja(c, 41, 22, 570, 128,
             "<b>1.</b> Las ocho etapas en orden: <b>Plan → Code → Build → Test → Release → Deploy → "
             "Operate → Monitor</b>, y de Monitor se regresa a Plan. En <b>Test</b> se ejecutan pruebas "
             "automáticas (por ejemplo con pytest) que comprueban que el código hace lo que debe. Si alguna "
             "falla, el error se detecta de inmediato y antes de publicar la versión, sin que nadie tenga que "
             "probar todo a mano.")
        marcar(c, 41, 176, 400, 188)                       # 2 -> B
        marcar(c, 41, 314, 452, 326)                       # 3 -> D
        caja(c, 41, 392, 570, 490,
             "<b>Pipeline:</b> «CI del validador de correos» (desde el push hasta producción)<br/>"
             "&nbsp;&nbsp;" + SIM % "└" + " <b>Workflow:</b> ci.yml (se activa con push a main)<br/>"
             "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + SIM % "└" + " <b>Job:</b> test (corre en el runner ubuntu-latest)<br/>"
             "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + SIM % "├" + " <b>Step 1:</b> Configurar Python 3.12 "
             "(actions/setup-python@v5)<br/>"
             "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" + SIM % "└" + " <b>Step 2:</b> Ejecutar pruebas "
             "(pytest -v)", tam=10.5)
        caja(c, 41, 545, 570, 631,
             "Al monitorear el validador, los registros muestran que muchos usuarios no pueden registrarse "
             "porque escriben su correo con un espacio al final («alumno@escuela.org ») y el programa lo "
             "rechaza. En la siguiente etapa de <b>Plan</b> el equipo decide limpiar los espacios con "
             "<i>strip()</i> antes de validar y agregar la prueba <i>test_correo_con_espacios</i>, para que "
             "el problema no vuelva a aparecer.")
        nombre_fecha(c, 645)
    elif n == 4:
        for y in (500, 537, 574, 627):                     # columna Resultado de la tabla
            c.setFillColor(colors.white)
            c.rect(402, H - y - 9, 164, 18, stroke=0, fill=1)
            texto(c, 410, y + 4, "Pasó ✔", 10.5, fuente="AU")
    elif n == 5:
        caja(c, 41, 22, 570, 128,
             "<b>1.</b> Porque así detecto los errores en segundos en mi propia computadora, antes de que "
             "lleguen al repositorio. Se evita subir código roto: que el pipeline falle en la nube, que se "
             "bloquee el despliegue y que mis compañeros descarguen código con errores; además ahorro tiempo "
             "y ejecuciones del runner. En esta práctica mi prueba nueva falló en local y la corregí antes de "
             "subirla.")
        caja(c, 41, 170, 570, 330,
             "Función: <b>test_dos_arrobas</b>. Verifica que <i>es_correo_valido(\"alumno@@escuela.org\")</i> "
             "devuelva <b>False</b>, porque un correo solo puede tener una @. La primera vez <b>falló</b> "
             "(assert True == False): el validador original aceptaba ese correo porque solo revisaba que el "
             "dominio tuviera un punto. Corregí validador.py agregando la condición <i>\"@\" in dominio</i> "
             "→ False, y ahora las <b>5 pruebas pasan</b> (Figura 1).")
    elif n == 6:
        nombre_fecha(c, 40)
    elif n == 7:
        caja(c, 41, 547, 570, 592,
             "Lo activa el evento <b>push</b> (<i>on: push</i>), y solo cuando el push se hace a la rama "
             "<b>main</b> (<i>branches: [ main ]</i>).")
        caja(c, 41, 615, 570, 662,
             "Descarga (clona) el código del repositorio dentro del runner. Debe ser el primer paso porque el "
             "runner empieza vacío: sin el código, los pasos siguientes no tendrían requirements.txt que "
             "instalar ni pruebas que ejecutar.")
    elif n == 8:
        caja(c, 41, 22, 570, 92,
             "<b>3.</b> Porque requirements.txt reúne en un solo archivo todas las dependencias del proyecto. "
             "Así el runner instala exactamente lo mismo que uso en mi computadora con un solo comando, y si "
             "agrego una librería solo edito ese archivo, sin tocar el workflow.")
        filas = [(289, "línea 1:  runs-on: ubuntu-latest"),
                 (326, "línea 2:  uses: actions/checkout@v4"),
                 (384, "línea 3:  run: pip install -r requirements.txt"),
                 (409, "línea 4:  run: pytest")]
        c.setFillColor(colors.white)
        c.rect(336, H - 445, 232, 250, stroke=0, fill=1)
        for y, s in filas:
            texto(c, 340, y + 4, s, 8.8)
    elif n == 9:
        marcar(c, 41, 49, 321, 61)                         # 4 -> D
        marcar(c, 41, 166, 197, 177)                       # 5 -> C
        caja(c, 41, 324, 570, 447,
             "<b>Error 1:</b> a <i>test</i> le faltan los dos puntos; debe escribirse <b>test:</b> y con "
             "sangría de 2 espacios dentro de <i>jobs:</i>.<br/>"
             "<b>Error 2:</b> <i>Steps:</i> está en mayúscula y con más sangría que <i>runs-on</i>; las claves "
             "van en minúsculas y al mismo nivel: <b>steps:</b> alineado con <b>runs-on:</b>.<br/>"
             "<font name='%s'>jobs:<br/>&nbsp;&nbsp;test:<br/>&nbsp;&nbsp;&nbsp;&nbsp;runs-on: ubuntu-latest"
             "<br/>&nbsp;&nbsp;&nbsp;&nbsp;steps:</font>" % MONO)
        caja(c, 41, 485, 570, 608,
             "Con integración continua las pruebas se ejecutan solas en cada push, siempre igual y en un "
             "entorno limpio, así que nadie puede olvidarlas ni saltarlas por prisa. Los errores se detectan "
             "en minutos y se sabe exactamente qué commit los causó. Si dependemos de que cada programador las "
             "corra a mano, alguien se olvidará, las correrá con otra versión de Python o dirá «en mi máquina "
             "sí funciona», y el error terminará llegando a producción.")
        nombre_fecha(c, 621)
    elif n == 11:
        caja(c, 41, 22, 570, 152,
             "<b>1.</b> Porque <i>needs: test</i> hace que deploy espere a que el job test termine y solo "
             "arranque si terminó con check verde. Si la eliminara, los dos jobs correrían al mismo tiempo, "
             "en paralelo: aunque una prueba fallara, deploy se ejecutaría igual y se publicaría a producción "
             "código con errores, rompiendo la regla de oro del CD.")
        caja(c, 41, 192, 570, 258,
             "Sí se ejecutaron los dos, con check verde. Primero corrió <b>test</b> (checkout, Python 3.12, "
             "pip install, pytest: 5 passed) y cuando terminó arrancó <b>deploy</b>, que imprimió «Desplegando "
             "a producción...» y «Versión lista para usar.». En el diagrama aparecen unidos: test → deploy "
             "(Figuras 2 y 3).")
        caja(c, 41, 294, 570, 358,
             "Cambié test_correo_valido para que esperara False. El job <b>test</b> falló con cruz roja "
             "(1 failed, 4 passed) y el job <b>deploy no se ejecutó</b>: aparece como omitido (skipped) porque "
             "depende de test con needs. No se desplegó nada (Figuras 4 y 5).")
        caja(c, 41, 395, 570, 445,
             "Regresé la línea a <i>assert es_correo_valido(\"alumno@escuela.org\") == True</i>, hice commit y "
             "push, y los dos jobs volvieron al check verde: 5 passed y deploy ejecutado (Figura 6).")
        caja(c, 41, 578, 570, 735,
             "Porque el archivo YAML se guarda en el repositorio y queda en el historial de git: cualquiera con "
             "acceso (o todo el mundo, si el repositorio es público como este) podría leer la contraseña y "
             "entrar al servidor, y aunque después la borrara seguiría en los commits anteriores. Los "
             "<b>Secrets</b> guardan la credencial cifrada en la configuración del repositorio; el workflow la "
             "usa con <i>${{ secrets.NOMBRE }}</i>, no aparece en el código y en los logs se muestra como ***. "
             "Solo los administradores del repositorio pueden crearla o reemplazarla, y ni siquiera ellos "
             "pueden volver a leer su valor; quien vea el código o los logs no ve la credencial.")
    elif n == 12:
        nombre_fecha(c, 40, x_nombre=252, x_fecha=430, clase_x=505)
        miniatura(c, "02_actions_verde.png", 205, 266, 560, 364)
        texto(c, 205, 375, "Figura 2 (anexo de evidencias).", 7.5)
        caja(c, 205, 392, 560, 448,
             "Workflow: <b>CI del validador de correos</b>.<br/>Jobs: <b>test</b> y <b>deploy</b> "
             "(deploy depende de test con needs).")
        caja(c, 205, 461, 560, 494, "<b>Check verde " + SIM % "✔" + "</b> en los dos jobs.", tam=10.5)
        caja(c, 41, 600, 570, 665,
             "En <i>U4ACT03-DevOps-Python/test_validador.py</i>, función <b>test_correo_valido</b>: cambié "
             "<i>assert es_correo_valido(\"alumno@escuela.org\") == True</i> por <b>== False</b>, para que la "
             "prueba esperara un resultado incorrecto. Hice commit y push del cambio.")
    elif n == 13:
        caja(c, 41, 22, 570, 152,
             "<b>3.</b> Falló el job <b>test</b>, en el step «Ejecutar pruebas» (Process completed with exit "
             "code 1); el job <b>deploy</b> quedó omitido (skipped).<br/>Mensaje: "
             "<i>FAILED test_validador.py::test_correo_valido - AssertionError: assert True == False</i>. "
             "Resumen: <b>1 failed, 4 passed</b> (Figuras 4 y 5).")
        caja(c, 41, 192, 570, 292,
             "El log indica que test_correo_valido falló en el assert: la función devolvió <b>True</b> "
             "(<i>where True = es_correo_valido('alumno@escuela.org')</i>) pero la prueba esperaba "
             "<b>False</b>. O sea, el código de la aplicación funcionaba bien; el error estaba en el resultado "
             "esperado de la prueba. pytest terminó con código 1, por eso GitHub marcó el step como fallido y "
             "no ejecutó el despliegue.")
        caja(c, 41, 314, 570, 412,
             "Volví a poner <b>== True</b> en test_correo_valido, porque alumno@escuela.org sí es un correo "
             "válido y la prueba debe aceptarlo. Antes de subirlo corrí <i>pytest -v</i> en mi computadora "
             "(5 passed) y después hice commit y push de la corrección.")
        caja(c, 41, 450, 570, 515,
             "El pipeline volvió al <b>check verde</b>: test pasó (5 passed) y después corrió deploy, que "
             "mostró «Desplegando a producción...». Ver Figura 6 en el anexo de evidencias.")
        caja(c, 41, 578, 570, 730,
             "Lo puede provocar un compañero que cambia una función sin revisar las pruebas, un merge mal "
             "resuelto, la actualización de una librería, un error de dedo en el YAML o yo mismo con prisa. "
             "El pipeline lo detecta en minutos, en cada push y sin depender de nadie; al fallar bloquea el "
             "despliegue, así el error nunca llega a los usuarios, se sabe qué commit lo causó y corregirlo "
             "es rápido y barato.")


def guia_contestada():
    out = PdfWriter(clone_from=GUIA)
    for i, pag in enumerate(out.pages, 1):
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        pagina(c, i)
        c.save()
        buf.seek(0)
        capa = PdfReader(buf).pages
        if len(capa):                       # páginas sin respuestas no traen capa
            pag.merge_page(capa[0])
    return out


# ----------------------------------------------------------------- portada y anexo
T = ParagraphStyle("T", fontName=F, fontSize=24, leading=30, textColor=AZUL, spaceAfter=10)
H1 = ParagraphStyle("H1", fontName=F, fontSize=16, leading=20, textColor=AZUL, spaceBefore=4, spaceAfter=10)
H2 = ParagraphStyle("H2", fontName=F, fontSize=12, leading=15, spaceBefore=8, spaceAfter=5)
P = ParagraphStyle("P", fontName=F, fontSize=10.5, leading=15, spaceAfter=6)
CAP = ParagraphStyle("CAP", parent=P, fontSize=9, leading=12, textColor=colors.HexColor("#4b5563"),
                     spaceBefore=3, spaceAfter=14)
CODE = ParagraphStyle("CODE", fontName=MONO, fontSize=7.4, leading=9.4, backColor=colors.HexColor("#f3f4f6"),
                      borderPadding=6, spaceBefore=4, spaceAfter=12)


def figura(i, archivo, pie):
    ruta = os.path.join(EVID, archivo)
    leyenda = Paragraph(f"<b>Figura {i}.</b> {pie}", CAP)
    if not os.path.exists(ruta):
        return KeepTogether([Paragraph(f"<font color='#d14343'>[Captura pendiente: evidencias/{archivo}]</font>", P),
                             leyenda])
    w, h = PI.open(ruta).size
    W = 7.0 * inch
    Hh = W * h / w
    if Hh > 6.4 * inch:
        Hh = 6.4 * inch
        W = Hh * w / h
    return KeepTogether([Image(ruta, width=W, height=Hh), leyenda])


def codigo(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as f:
        return Preformatted(f.read().rstrip(), CODE)


def pie_pagina(c, doc):
    c.saveState()
    c.setFont(F, 8)
    c.setFillColor(colors.HexColor("#6b7280"))
    c.drawString(0.75 * inch, 0.5 * inch, f"U4ACT03 - DevOps con Python y GitHub Actions  |  {ALUMNO}")
    c.restoreState()


def portada_y_anexo():
    buf_p, buf_a = io.BytesIO(), io.BytesIO()
    portada = [Spacer(1, 2.2 * inch),
               Paragraph("U4ACT03 – DevOps con Python y GitHub Actions", T),
               Paragraph("Pruebas automatizadas con pytest y pipeline CI/CD", H2),
               Spacer(1, 0.5 * inch),
               Paragraph(f"<b>Alumno:</b> {ALUMNO}", P),
               Paragraph(f"<b>Fecha:</b> {FECHA}", P),
               Paragraph(f"<b>Repositorio:</b> {REPO_URL} (rama main)", P),
               Paragraph("<b>Carpeta:</b> U4ACT03-DevOps-Python/ &nbsp;·&nbsp; "
                         "<b>Workflow:</b> .github/workflows/ci.yml", P),
               Spacer(1, 0.4 * inch),
               Paragraph("Contenido: guía de la actividad contestada (respuestas en azul), anexo de evidencias "
                         "con las capturas del pipeline y código fuente documentado.", P)]
    SimpleDocTemplate(buf_p, pagesize=letter).build(portada)

    anexo = [Paragraph("Anexo A. Evidencias", H1)]
    for i, (archivo, pie) in enumerate(FIGURAS, 1):
        anexo.append(figura(i, archivo, pie))
    anexo += [PageBreak(), Paragraph("Anexo B. Código fuente documentado", H1),
              Paragraph("U4ACT03-DevOps-Python/validador.py", H2), codigo("U4ACT03-DevOps-Python/validador.py"),
              Paragraph("U4ACT03-DevOps-Python/test_validador.py", H2),
              codigo("U4ACT03-DevOps-Python/test_validador.py"),
              Paragraph(".github/workflows/ci.yml", H2), codigo(".github/workflows/ci.yml")]
    SimpleDocTemplate(buf_a, pagesize=letter, topMargin=0.7 * inch, bottomMargin=0.8 * inch,
                      leftMargin=0.75 * inch, rightMargin=0.75 * inch).build(
        anexo, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
    return PdfReader(buf_p), PdfReader(buf_a)


def main():
    portada, anexo = portada_y_anexo()
    out = PdfWriter()
    for p in portada.pages:
        out.add_page(p)
    for p in guia_contestada().pages:
        out.add_page(p)
    for p in anexo.pages:
        out.add_page(p)
    with open(OUT, "wb") as f:
        out.write(f)
    faltan = [a for a, _ in FIGURAS if not os.path.exists(os.path.join(EVID, a))]
    print(f"PDF generado: {OUT} ({len(out.pages)} páginas)")
    if faltan:
        print("Capturas pendientes:", ", ".join(faltan))


if __name__ == "__main__":
    main()
