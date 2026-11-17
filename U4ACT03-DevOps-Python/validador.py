"""
validador.py
U4ACT03 - DevOps con Python y GitHub Actions
Autor: Sebastian Villegas Arredondo

Módulo con la lógica de la aplicación: decide si un texto es un correo
electrónico válido. Sus pruebas automatizadas están en test_validador.py
y se ejecutan con pytest, en local y en el pipeline de GitHub Actions.
"""


def es_correo_valido(correo):
    """Devuelve True si el correo tiene @ y un punto después del @.

    Reglas que debe cumplir un correo válido:
      1. Contener una arroba (@).
      2. Tener un usuario (texto antes de la @) que no esté vacío.
      3. Tener un dominio (texto después de la @) con al menos un punto.
      4. Tener una sola @ (el dominio no puede contener otra @).

    Ejemplo:
        >>> es_correo_valido("alumno@escuela.org")
        True
        >>> es_correo_valido("alumno@escuela")
        False
    """
    # Regla 1: sin arroba no puede ser un correo
    if "@" not in correo:
        return False

    # Separa el correo en usuario y dominio en la primera @
    usuario, dominio = correo.split("@", 1)

    # Reglas 2, 3 y 4: usuario no vacío, dominio con punto y una sola @
    if usuario == "" or "." not in dominio or "@" in dominio:
        return False

    return True
