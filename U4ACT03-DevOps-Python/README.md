# U4ACT03 – DevOps con Python y GitHub Actions

**Alumno:** Sebastian Villegas Arredondo

Validador de correos en Python con pruebas automatizadas (pytest) y un pipeline CI/CD en GitHub Actions.

```
U4ACT03-DevOps-Python/
├── validador.py        # es_correo_valido(correo)
├── test_validador.py   # 5 pruebas pytest
├── requirements.txt    # pytest
└── original/           # Guía de la actividad
.github/workflows/ci.yml  # (raíz del repo) job test + job deploy (needs: test)
```

## Ejecutar localmente
```bash
cd U4ACT03-DevOps-Python
pip install -r requirements.txt
pytest -v
```
