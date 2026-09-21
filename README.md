# Ejemplo de pipeline CI/CD — microservicio en Python

Estructura pensada para un microservicio pequeño (FastAPI) empaquetado en Docker,
con GitHub Actions como motor de CI/CD. La misma lógica se traslada casi 1:1 a
GitLab CI, Jenkins o Azure Pipelines; lo que cambia es la sintaxis, no las etapas.

## Estructura de archivos

```
ci-cd-microservicio/
├── .github/workflows/ci-cd.yml   # Pipeline completo
├── app/
│   ├── __init__.py
│   └── main.py                   # Microservicio de ejemplo (FastAPI)
├── tests/
│   └── test_main.py
├── Dockerfile                    # Build multi-stage
├── requirements.txt              # Dependencias de producción
└── requirements-dev.txt          # Lint, tipos, tests
```

## Etapas del pipeline y por qué van en ese orden

1. **Lint + formato** (`ruff`, `black`, `mypy`)
   Es la etapa más barata y rápida. Si el código ni siquiera pasa estilo o
   tipado, no tiene sentido gastar minutos de CI en tests o build.

2. **Tests + cobertura** (`pytest`, `pytest-cov`)
   Corre solo si el lint pasó. Se exige un mínimo de cobertura
   (`--cov-fail-under=80`) para que el pipeline falle si baja la calidad.

3. **Seguridad** (`pip-audit` para dependencias, `bandit` para código)
   Corre en paralelo a los tests (ambos dependen solo de `lint`), así no
   alarga el tiempo total del pipeline.

4. **Build y push de la imagen Docker**
   Solo se ejecuta si `test` y `security` pasaron, y solo en push directo
   (no en pull requests, para no llenar el registry de imágenes de prueba).
   Usa cache de capas (`cache-from`/`cache-to`) para acelerar builds sucesivos.

5. **Deploy**
   - `develop` → despliegue automático a *staging*.
   - `main` → despliegue a *producción*, protegido con un `environment` de
     GitHub que puede configurarse para pedir aprobación manual antes de
     ejecutarse.

## Buenas prácticas aplicadas

- **Dockerfile multi-stage**: la etapa de build instala dependencias; la etapa
  final solo copia lo necesario, reduciendo el tamaño de la imagen y la
  superficie de ataque.
- **Usuario sin privilegios** dentro del contenedor (`appuser`).
- **HEALTHCHECK** nativo de Docker apuntando al mismo endpoint `/health` que
  usaría un orquestador (Kubernetes, ECS, etc.).
- **Separación de dependencias** de producción (`requirements.txt`) y
  desarrollo (`requirements-dev.txt`), para no meter herramientas de testing
  en la imagen final.
- **Jobs paralelos** donde no hay dependencia real entre ellos (`test` y
  `security` corren a la vez).

## Cómo adaptarlo

- Cambiar `docker/build-push-action` y el paso de deploy por tu orquestador
  real (Kubernetes con `kubectl`/Helm, AWS ECS, Cloud Run, etc.).
- Si usás GitLab en vez de GitHub, la estructura de `stages:` y `jobs:` es
  conceptualmente igual; solo cambia la sintaxis de triggers y secrets.
- Para monorepos con varios microservicios, se puede usar `paths:` en el
  trigger para que el pipeline de cada servicio solo corra si cambiaron sus
  propios archivos.
