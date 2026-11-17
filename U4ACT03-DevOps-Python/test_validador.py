"""
test_validador.py
U4ACT03 - DevOps con Python y GitHub Actions
Autor: Sebastian Villegas Arredondo

Pruebas automatizadas de validador.py. pytest encuentra este archivo porque
su nombre empieza con "test_" y ejecuta cada función que empieza con "test_".
Cada prueba usa assert: si la condición es falsa, la prueba falla.

Ejecutar:  pytest -v
"""
from validador import es_correo_valido


def test_correo_valido():
    """Un correo correcto se acepta."""
    assert es_correo_valido("alumno@escuela.org") == False


def test_sin_arroba():
    """Un texto sin @ se rechaza."""
    assert es_correo_valido("alumno.escuela.org") == False


def test_dominio_sin_punto():
    """Un dominio sin punto se rechaza."""
    assert es_correo_valido("alumno@escuela") == False


def test_usuario_vacio():
    """Un correo sin usuario (nada antes de la @) se rechaza."""
    assert es_correo_valido("@escuela.org") == False


def test_dos_arrobas():
    """Prueba propia: un correo con dos @ seguidas se rechaza."""
    assert es_correo_valido("alumno@@escuela.org") == False
