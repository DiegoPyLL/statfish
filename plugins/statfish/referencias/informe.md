# Informe, lectura, hallazgos e issues

`statfish correr` escribe `informe.md` con dos partes: las tablas fijas, que calcula el motor, y la
`lectura.md` del agente con sus marcadores resueltos. **Ninguna cifra se escribe a mano.** Si el modelo
cambia, se vuelve a correr y el texto se regenera; no se edita.

## Marcadores

`{{ruta|filtro}}` toma un valor de `salida/resultados.json`, o de `contexto.toml` con el prefijo
`contexto.`, y lo formatea:

| Marcador | Resultado |
|---|---|
| `{{metricas.perdida_por_codigo\|pct}}` | `1,3 %` |
| `{{metricas.perdida_por_codigo\|pct:2}}` | `1,27 %` |
| `{{metricas.contacto_total\|pp:1}}` | `23,6` (puntos, «de cada 100») |
| `{{reglas.R9.perdida\|mil}}` | `3,59` («de cada 1.000») |
| `{{robustez.n}}` | `200` |
| `{{morris.0.parametro\|texto}}` | `resuelve_nombre_claro` |
| `{{contexto.repo.commit_corto\|texto}}` | `76b713a` |
| `{{ ( hipotesis.todos.perdida_por_codigo - hipotesis.base.perdida_por_codigo ) / hipotesis.base.perdida_por_codigo \|pct:0}}` | `−67 %` |

Estos son los filtros:

| Filtro | Qué hace |
|---|---|
| `pct[:d]` | ×100 con `d` decimales (1 por defecto) y « %» |
| `pp[:d]` | ×100, sin «%» (2 por defecto) |
| `mil[:d]` | ×1.000 (2 por defecto) |
| `dec[:d]` | El número, con `d` decimales (2 por defecto) |
| `num[:c]` | `c` cifras significativas (3 por defecto) |
| `entero` | Entero con punto de miles |
| `texto` | El texto tal cual |

Sin filtro, un entero sale con `entero` y un decimal con `num`. Si la ruta no existe, el marcador queda
sin resolver y `correr` falla, con la lista de los marcadores malos.

Una expresión dentro de un marcador lleva espacios alrededor de cada operador y paréntesis: `+`, `-`, `*`,
`/`, `(` y `)`. Los ids con signos, como `R1+R2`, funcionan en una ruta sola, sin espacios.

## Qué hay en `resultados.json`

| Ruta | Qué es |
|---|---|
| `metricas.<id>` | Cada métrica en p50, sobre la población grande |
| `desenlaces.<id>` | Probabilidad de cada desenlace (de cada llegada) |
| `intervalos.<métrica>.p5\|p50\|p95` | Intervalo de los sorteos (F9); también `intervalos.masa_<perfil>` |
| `perfiles.<id>.masa`, `.masa_p5`, `.masa_p95`, `.n` | P(perfil) y su intervalo |
| `perfiles.<id>.metricas.<m>`, `.desenlaces.<d>` | Dentro del perfil |
| `perfiles.<id>.reglas.<regla>.perdida\|friccion` | Por cada usuario del perfil |
| `reglas.<id>.perdida`, `.friccion`, `.total`, `.por_desenlace.<d>` | Por cada llegada |
| `robustez.n`, `.top1_perdida.<regla>`, `.top3_perdida.<regla>`, `.top3_friccion.<regla>` | F11 |
| `morris.<i>.parametro`, `.rango`, `.<métrica>.mu_estrella\|sigma` | F10, ordenado por `ordenar_por` |
| `hipotesis.base\|<id>.<métrica>`, `.texto` | Cada escenario |
| `cobertura.pares\|arcos\|superficies.…` | Cubiertos, universo y faltantes |
| `fidelidad.declaradas`, `.automatica` | F12 |
| `parametros.<id>.p50\|p10\|p90\|fuente\|texto` | Los supuestos usados |
| `usuarios.total\|representativos\|cobertura` | Cuántos usuarios hay con traza |
| `tamanos.<etapa>` | Los tamaños con que se corrió |

## `lectura.md`

Va en el informe, debajo de la cabecera:

- **Primero lo principal:** el nivel con su intervalo, las fricciones que explican la pérdida, la pérdida
  silenciosa si la hay y el orden robusto.
- **Después qué cambia si se arregla** (hipótesis) y qué supuesto conviene medir (Morris).
- **Separa lo que el código explica de lo que dependen los priors de intención.** Sin datos, el nivel total no
  es una predicción.
- **Las cifras, como marcadores.** `validar` avisa si encuentra porcentajes o decimales escritos a mano.

## `hallazgos.toml`

```toml
[[hallazgos]]
id = "H-R9"
regla = "R9"
patron = "P-MISMO-TEXTO-DOS-DESTINOS"
titulo = "«Cuéntanos tu proyecto» lleva al brief en un lugar y al formulario en otro"
estado = "nuevo"                 # nuevo | confirmado | issue #77 | resuelto | descartado
perfiles = ["S2"]
commit = "76b713a"
evidencia = [{ cita = "src/data/paginas-de-servicio.js:66", extracto = "proyecto: '/brief-web'," }]
resumen = "La mayor pérdida en el {{robustez.top1_perdida.R9|pct}} de los sorteos."
cuerpo = '''
## Qué pasa
…con marcadores…
'''
```

- `resumen` va en la tabla de hallazgos del informe.
- Si el hallazgo tiene `cuerpo`, `correr` escribe `salida/issues/<id>.md` con el título y el cuerpo
  resueltos. El issue se crea con ese archivo, por ejemplo `gh issue create --body-file`, **solo con la
  confirmación de quien corre la herramienta**.
- Al reproducir en un commit nuevo, un hallazgo con evidencia vencida queda marcado como «posible arreglo,
  verificar».

## `relatos.toml`

```toml
[[relatos]]
id = "U13"
huella = "1f0c…"                 # la de salida/usuarios.json
texto = "Dueño de una cafetería y cliente de Volutus. Navega con JavaScript apagado…"
```

El relato se escribe con los atributos ya fijos. Si el usuario cambia porque cambió el modelo, el informe lo
marca como desactualizado.
