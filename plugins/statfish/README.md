# Statfish (plugin de Claude Code)

Statfish simula usuarios de un producto **a partir de su código**. Responde quién no logra qué, en qué paso y
por qué, y qué cambia si se arregla.

El trabajo se divide en dos:

- **El agente** recorre el repo con evidencia `archivo:línea` y verbaliza priors con rango.
- **El motor** (`statfish`, Python sin dependencias) arma una red de perfiles y una cadena de uso, crea
  usuarios con cobertura por pares y calcula los desenlaces exactos, la incertidumbre, la sensibilidad y las
  hipótesis.

Ninguna cifra del informe se escribe a mano y la misma semilla da los mismos bytes.

## Requisitos

- Claude Code con soporte de plugins.
- Python 3.11 o más (usa `tomllib`). El motor no usa la red.

## Uso

```text
/statfish:simular "¿Quién no logra contactar, en qué paso y por qué?"
```

El skill recorre las etapas 0 a 8 y deja todo en `<repo>/statfish/<fecha>-<slug>/`: modelo, evidencia,
usuarios, trazas, `informe.md` y `manifiesto.json`.

| Skill | Para qué |
|---|---|
| `/statfish:simular` | La corrida completa; Claude también lo usa solo cuando corresponde |
| `/statfish:reproducir` | Recalcula y compara byte a byte; verifica la evidencia contra el commit actual |
| `/statfish:calibrar` | Actualiza los priors con conteos reales sin datos personales |
| `/statfish:patron` | Promueve un hallazgo confirmado al catálogo compartido |

El agente `statfish:elicitador` verbaliza priors con contexto limpio: el skill lo lanza K = 5 veces en
paralelo.

## El motor

`statfish` queda en el PATH mientras el plugin está activo. También corre sin Claude Code:

```bash
bin/statfish validar <corrida>
bin/statfish correr <corrida> [--rapido]
bin/statfish reproducir <corrida>
```

| Comando | Qué hace |
|---|---|
| `contexto` | Detecta el stack y crea la corrida |
| `patrones` | Checklist del catálogo para ese contexto |
| `anclas` | Registro de cifras públicas y su vigencia |
| `evidencia` | Verifica cada cita contra el commit |
| `validar` | Esquema, sumas, restricciones y ramas |
| `elicitar combinar` | Junta las K elicitaciones (mezcla y divergencia de Jensen-Shannon) |
| `correr` | Usuarios, trazas, resultados, informe y manifiesto |
| `reproducir` | Recalcula y compara byte a byte |
| `comparar` | Diferencias entre dos corridas |
| `calibrar` | Actualización conjugada con conteos |

## Qué hay aquí

| Carpeta | Qué guarda |
|---|---|
| `skills/` | Los cuatro skills |
| `agents/` | El agente `elicitador` |
| `bin/` | El lanzador del motor |
| `motor/statfish/` | El motor |
| `referencias/` | Método, fórmulas F1 a F15, formato del modelo, expresiones, fuentes e informe |
| `datos/anclas/` | Registro de anclas |
| `datos/patrones/` | Catálogo de descubrimientos que crece con cada proyecto |
| `plantillas/` | Lo que copia `statfish contexto` |
| `evals/` | Casos de `claude plugin eval` |

El caso de referencia, la landing de Volutus, está en `ejemplos/volutus/` del repositorio.
