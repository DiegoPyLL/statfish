# Plan: Statfish como herramienta reproducible e invocable

| | |
|---|---|
| Estado | Implementado: fases 0 a 6. La fase 7 espera permiso para escribir en dos repos ([estado](#estado-de-la-implementación)) |
| Fecha | 2026-11-21 |
| Antecede | [Análisis de viabilidad](viabilidad.md) y [caso Volutus](caso-volutus/recorrido.md) |

## Por qué

El análisis de viabilidad mostró que el método funciona, pero quedó atado a una conversación:

- El modelo vivía en un script temporal, fuera del repo.
- Las cifras de los docs y de los issues se escribieron a mano. Al corregir un error (la categórica `canal` sumaba
  0,94) hubo que actualizarlas a mano en cinco lugares.
- Las fuentes quedaron repartidas en el texto.
- Los hallazgos no quedaron en un formato que otro proyecto pueda reutilizar.

Este plan convierte Statfish en una **herramienta reproducible que cualquiera del equipo puede invocar**, con fórmulas,
fuentes y descubrimientos fijados según el contexto.

Decisiones tomadas:

- **Instalación:** plugin de Claude Code. Este repo (`DiegoPyLL/statfish`) es a la vez el marketplace y el plugin.
- **Corridas:** cada una se guarda en el repo analizado, en `statfish/`, versionada con su código.

## Principios

1. **Ningún número a mano.** Todo texto que cite una cifra usa un marcador, como
   `{{metricas.perdida_por_codigo|pct}}`, que el motor resuelve desde `resultados.json`. Si el modelo cambia, se
   regenera el texto; no se edita.
2. **El motor nunca llama a un LLM.** Lo que hace el LLM queda guardado como artefacto. Desde ahí, todo cálculo es
   determinista. Esos artefactos son:
   - el inventario del recorrido;
   - el modelo;
   - las elicitaciones crudas;
   - las cuatro respuestas del recorrido cognitivo;
   - los relatos.
3. **Evidencia con extracto.** Cada `archivo:línea` guarda el texto que cita. En cada corrida se verifica contra el
   commit actual y se marca vigente, desplazada (el texto está, en otras líneas) o vencida (el texto ya no está).
4. **Fuentes con fecha y vigencia.** Cada ancla registra su URL, cuándo se consultó y cuánto dura. La corrida guarda
   una copia de las que usó.
5. **Determinismo.** El mismo modelo, con la misma semilla y la misma versión del motor, da los mismos bytes.
   `reproducir` lo comprueba.

## Estructura del repo

```
statfish/
├── .claude-plugin/marketplace.json          # name "statfish"; plugins[0] = {name "statfish", source "./plugins/statfish"}
├── plugins/statfish/
│   ├── .claude-plugin/plugin.json           # name, version, description, author, repository, license
│   ├── skills/
│   │   ├── simular/SKILL.md                 # el flujo completo (etapas 0–8); Claude puede invocarlo solo
│   │   ├── reproducir/SKILL.md              # disable-model-invocation: true
│   │   ├── calibrar/SKILL.md                # disable-model-invocation: true
│   │   └── patron/SKILL.md                  # promueve un hallazgo al catálogo; disable-model-invocation: true
│   ├── agents/elicitador.md                 # subagente con contexto limpio: devuelve p10/p50/p90 en JSON
│   ├── bin/statfish                         # lanzador Python: queda en el PATH mientras el plugin está activo
│   ├── motor/statfish/                      # Python ≥ 3.11, sin dependencias (tomllib, json, random, ast)
│   │   ├── cli.py  modelo.py  expresiones.py  red.py  cadena.py  muestreo.py  cobertura.py
│   │   ├── incertidumbre.py  sensibilidad.py  calibracion.py  evidencia.py  contexto.py  informe.py
│   │   ├── corrida.py  util.py              # orquestación de `correr`; TOML y números en español
│   ├── referencias/                         # carga progresiva desde los SKILL.md
│   │   ├── metodo.md  formulas.md  formato-modelo.md  expresiones.md  fuentes.md  informe.md
│   ├── datos/
│   │   ├── anclas/<fuente>/<país>/<periodo>.toml      # p. ej. statcounter/CL/2026-10.toml
│   │   └── patrones/<id>.toml                         # catálogo compartido de descubrimientos
│   ├── plantillas/                          # modelo.toml, hallazgos.toml, lectura.md
│   └── evals/                               # casos de `claude plugin eval`
├── ejemplos/volutus/                        # el caso migrado al formato nuevo, con sus salidas esperadas
├── tests/                                   # python3 -m unittest (no viajan con el plugin)
└── docs/                                    # viabilidad.md, caso-volutus/ (histórico) y este plan
```

## Instalación y uso

```bash
# una vez por persona
claude plugin marketplace add DiegoPyLL/statfish
claude plugin install statfish@statfish
```

- **Correr una simulación:** en cualquier repo, `/statfish:simular "¿Quién no logra contactar, en qué paso y por qué?"`.
- **Recalcular sin Claude Code:** `plugins/statfish/bin/statfish reproducir statfish/<corrida>` recalcula sin ningún LLM.
- **Desarrollar el plugin:** `claude --plugin-dir ./plugins/statfish` y `claude plugin validate ./ --strict`.

## Skills y agente

| Skill | Quién lo invoca | Qué hace |
|---|---|---|
| `simular` | Usuario o Claude | Recorre las etapas 0–8 y deja la carpeta de corrida con su informe |
| `reproducir` | Usuario | Verifica la evidencia contra el commit actual, recalcula y compara con lo guardado |
| `calibrar` | Usuario | Recibe conteos reales y actualiza los parámetros en forma conjugada |
| `patron` | Usuario | Convierte un hallazgo confirmado en una entrada del catálogo y prepara el cambio para revisión |

Solo `simular` lo invoca Claude por su cuenta; los otros tres se invocan a mano. Según `claude plugin details`, el
plugin entero suma unos 388 tokens fijos por sesión: unos 140 de `simular`, entre 50 y 60 por cada uno de los otros
tres skills y 80 del agente.

**`statfish:elicitador`** se lanza K = 5 veces por cada parámetro sin ancla. Recibe solo la definición, el contexto y la
evidencia, y devuelve p10, p50 y p90 en JSON. No ve las respuestas anteriores, así que las elicitaciones son
independientes. Eso resuelve el límite que tenía el caso Volutus, donde un solo agente no podía repetir la pregunta sin
recordar su respuesta.

### Etapas de `simular`

| Etapa | Qué hace el agente | Qué deja | Qué comando la cierra |
|---|---|---|---|
| 0. Pregunta y contexto | Declara la pregunta, el país y el público; detecta el stack | `contexto.toml` | `statfish contexto` |
| 1. Recorrido | Lee primero el índice y después lo dirigido. Revisa cada patrón aplicable del catálogo y anota evidencia con extracto. | `recorrido.toml` | `statfish patrones`, `statfish evidencia` |
| 2. Variables | Declara el soporte y las restricciones a partir del código | `modelo.toml` | `statfish validar` |
| 3. Probabilidades | Usa anclas vigentes. Sin ancla, lanza K elicitaciones independientes. | `anclas/`, `elicitacion/` | `statfish anclas`, `statfish elicitar combinar` |
| 4–6. Perfiles, usuarios y flujos | Declara perfiles, factores, superficies, cadena e hipótesis | `modelo.toml` | `statfish correr` |
| 7. Lectura | Interpreta los resultados con marcadores, sin escribir cifras | `lectura.md`, `hallazgos.toml` | `statfish correr`, que genera `informe.md` |
| 8. Calibración | Recibe conteos reales | `conteos.toml` | `statfish calibrar` |

## Comandos del motor

| Comando | Qué hace |
|---|---|
| `statfish contexto <repo>` | Detecta el stack de forma determinista (package.json, wrangler, Turnstile, frameworks) y escribe `contexto.toml` |
| `statfish patrones <corrida>` | Lista los patrones del catálogo que aplican a ese contexto, como checklist del recorrido |
| `statfish anclas --pais CL` | Lista las anclas del registro y avisa las vencidas |
| `statfish evidencia <corrida>` | Verifica cada cita: que el archivo exista, que el rango sea válido y que el extracto esté; la marca vigente, desplazada o vencida |
| `statfish validar <corrida>` | Revisa el esquema, que las distribuciones sumen 1, las restricciones, que las ramas de cada estado sumen 1 y que los nombres existan |
| `statfish elicitar combinar <corrida>` | Junta las K respuestas en una mezcla y mide la divergencia de Jensen-Shannon entre ellas |
| `statfish correr <corrida> [--semilla N]` | Calcula usuarios, trazas, resultados y manifiesto, y genera `informe.md` |
| `statfish reproducir <corrida>` | Recalcula y compara byte a byte con lo guardado |
| `statfish comparar <a> <b>` | Diferencias entre dos corridas: métricas y hallazgos que aparecen o desaparecen |
| `statfish calibrar <corrida> --conteos conteos.toml` | Actualiza los parámetros con conteos reales |

## Formato del modelo

Un archivo `modelo.toml` por corrida. El esquema completo está en `referencias/formato-modelo.md` y el ejemplo
entero en `ejemplos/volutus/modelo.toml`.

- **`[[parametros]]`:** p50, p10 y p90, más una `fuente` (`ancla:<id>`, `prior:elicitacion`, `codigo:<regla>` o
  `definicion`) y, si corresponde, las `anclas` que informan el prior. Un interruptor de hipótesis lleva
  `interruptor = true` y no se sortea.
- **`[[distribuciones]]`:** las categóricas, con sus valores, su κ y su fuente. Con `fuente = "ancla:<id>"`, `validar`
  las compara con la copia del ancla.
- **`[[variables]]`:** sus valores, que son el soporte y llevan evidencia, y una lista de `casos`. Se aplica el primer
  caso que calza. Cada caso es un `valor`, una `prob` (booleana) o una `dist` (el id de una distribución o una tabla
  en línea), con `inclinacion` y `transformar` opcionales. Cada variable usa su propio uniforme, así que cambiar un
  peso no reordena a los demás (números aleatorios comunes).
- **`[[restricciones]]`:** expresiones que ningún usuario puede violar. `validar` lo comprueba sobre una muestra.
- **`[[reglas]]`:**
  - id y texto;
  - si es fricción;
  - el patrón del catálogo;
  - evidencia `{cita, extracto}`;
  - las cuatro respuestas del recorrido cognitivo, con su nota.
- **`[cadena]` y `[[estados]]`:** los estados tienen argumentos (`args`) y `locales`. Sus ramas van directas o por
  `casos`, donde se aplica el primero que calza. Cada rama lleva condición, probabilidad, destino (otro estado,
  `$argumento` o `FIN:<desenlace>`), argumentos del destino (`con`), acción, arco, regla y superficies.
- **`[[metricas]]`:** sumas de desenlaces.
- **`[[perfiles]]`:** predicados en orden; se aplica el primero que calza.
- **`[[factores]]`, `[[superficies]]` y `[cobertura]`:** lo que la corrida debe cubrir. Cada superficie lleva su clase
  de equivalencia, y `[cobertura.aplanada]` define la red q.
- **`[sensibilidad]`:** los supuestos de Morris, en orden.
- **`[[hipotesis]]`:** solo cambios de parámetros. Un arreglo se modela como un interruptor, por ejemplo
  `p.arreglo_r1`.
- **`[[fidelidad]]` y `[nombres]`:** marginales declaradas y nombres sintéticos.

Extracto del caso Volutus:

```toml
[[parametros]]
id = "movil_si_redes"
p50 = 0.80
p10 = 0.65
p90 = 0.90
fuente = "prior:elicitacion"

[[distribuciones]]
id = "disp_base"
valores = { escritorio = 0.5005, movil = 0.4912, tablet = 0.0083 }
kappa = 200
fuente = "ancla:statcounter-CL-plataforma-2026-10"

[[variables]]
id = "dispositivo"
valores = ["escritorio", "movil", "tablet"]
uniforme = 2
soporte = [{ cita = "CLAUDE.md:102-119", extracto = "## 5. Responsive Design" }]

  [[variables.casos]]
  si = "canal == 'redes'"
  dist = { movil = "p.movil_si_redes", tablet = "0.01", escritorio = "1 - p.movil_si_redes - 0.01" }

  [[variables.casos]]
  dist = "disp_base"

[[restricciones]]
texto = "iOS y iPadOS usan WebKit, sea cual sea el navegador"
expr = "sistema not in ('ios', 'ipados') or motor == 'webkit'"

[[reglas]]
id = "R1"
texto = "El nombre solo admite letras, marcas, espacio y apóstrofo recto"
friccion = true
patron = "P-NOMBRE-SOLO-LETRAS"
evidencia = [{ cita = "src/lib/contacto.js:89-91", extracto = "export const NOMBRE_VALIDO = /^[\\p{L}\\p{M}' ]+$/u" }]
cw = ["sí", "sí", "sí", "en parte"]

[[estados]]
id = "validar_nombre"
args = ["siguiente", "origen"]

  [[estados.casos]]
  si = "p.arreglo_r1 and nombre_tipo in ('apostrofo', 'guion_punto')"

    [[estados.casos.ramas]]
    prob = "1.0"
    va = "$siguiente"
    accion = "el nombre pasa"

  [[estados.casos]]
  si = "nombre_tipo in ('guion_punto', 'empresa_signos')"

    [[estados.casos.ramas]]
    prob = "p.resuelve_nombre_claro"
    va = "$siguiente"
    accion = "«Usa solo letras.»: reescribe el nombre"
    regla = "R1"
```

**Expresiones.** Un evaluador seguro sobre `ast` acepta solo lo siguiente:

- nombres de atributos, de argumentos y de locales;
- `p.<parámetro>` y `d.<distribución>.<valor>`;
- números, textos, `True` y `False`;
- comparaciones, `in` y `not in`, con tuplas o listas literales;
- `and`, `or` y `not`;
- `+`, `-`, `*` y `/`;
- `x if c else y`;
- `min` y `max`.

Cualquier otra cosa es un error de validación. Una expresión válida se traduce a Python y se compila, así que el
motor genérico corre a la velocidad del script del caso. Los textos (`accion`, `arco`, `regla`, `nombre`) son
plantillas con expresiones entre llaves.

## Carpeta de corrida (en el repo analizado)

```
statfish/<AAAA-MM-DD>-<slug>/
  contexto.toml          # pregunta, país, público, stack detectado, commit
  recorrido.toml         # superficies, entradas, reglas con evidencia, hipótesis descartadas, bitácora de lectura
  modelo.toml            # variables, restricciones, parámetros, cadena, perfiles, factores, hipótesis
  anclas/                # copia de las anclas usadas
  elicitacion/           # k1.json … k5.json y combinada.json
  relatos.toml           # una línea por usuario, con la huella de sus atributos
  salida/                # usuarios.json, trazas.json, resultados.json, evidencia.json, issues/<id>.md
                         # y, si se usaron, reproduccion.json y calibracion.json
  hallazgos.toml         # descubrimientos de esta corrida
  lectura.md             # interpretación, con marcadores
  conteos.toml           # opcional: conteos reales para calibrar
  calibracion.toml       # opcional: parámetros posteriores (los escribe `statfish calibrar`)
  informe.md             # generado: tablas fijas y lectura resuelta
  manifiesto.json        # semilla, versiones, commit, fecha y sha256 de cada entrada y salida
```

## Fórmulas fijas

Cada una vive en `referencias/formulas.md` y tiene un test con valores conocidos.

| Id | Fórmula |
|---|---|
| F1 | Beta desde (p10, p50, p90): σ = (p90 − p10)/2,563; κ = m(1−m)/σ² − 1; α = mκ, β = (1−m)κ; con var ≤ 0,95·m(1−m) |
| F2 | Dirichlet(κ·p), con κ según la fuente: ancla 200, prior de 10 a 15, definición 1.000 |
| F3 | Mezcla de K elicitaciones: p̄ = media de las K; κ por momentos de la varianza de la mezcla (la de cada elicitación más la dispersión entre ellas) |
| F4 | Muestreo ancestral con números aleatorios comunes (un uniforme por variable) y log p por usuario |
| F5 | Peso de importancia: w = exp(log p − log q) |
| F6 | Cobertura por pares (AETG voraz): universo estimado con la red aplanada q; M candidatos por vuelta; termina cuando no quedan pares |
| F7 | Absorción exacta: suma por caminos acotada, o B = (I − Q)⁻¹R |
| F8 | Atribución: cada pérdida se asigna a la última regla de fricción del camino |
| F9 | Monte Carlo de parámetros: S sorteos; el cuantil q ≤ 0,5 es el elemento ⌊q·S⌋ de los valores ordenados y el q > 0,5, el S − 1 − ⌊(1−q)·S⌋ (simétrico: con S = 200, p5 y p95 son los elementos 10 y 189) |
| F10 | Morris: r trayectorias, p niveles, Δ = p/(2(p−1)); EE = ΔY/Δ; μ* = media de \|EE\|; σ = desviación de EE |
| F11 | Robustez del orden: frecuencia de cada regla en el top-k a través de los sorteos |
| F12 | Fidelidad: \|declarada − muestra\| ≤ 3·√(p(1−p)/n) |
| F13 | Divergencia de Jensen-Shannon en base 2, para la estabilidad entre elicitaciones y entre corridas (umbral 0,05) |
| F14 | Calibración: Beta(α+s, β+f) y Dirichlet(α+n) |
| F15 | Arco forzado: el camino de máxima probabilidad que contiene el arco |

## Fuentes según el contexto

**Registro de anclas** (`datos/anclas/`). Cada archivo lleva:

- la URL;
- la fecha de consulta;
- la vigencia en meses;
- los valores;
- una plantilla de URL para renovarla en otro país o período.

Entradas iniciales, todas ya consultadas para el caso Volutus:

- StatCounter Chile, octubre de 2026: plataforma, sistema del celular, sistema del escritorio y navegador.
- SII 2024, empresas por tamaño.
- INE 2025, empresas activas.
- Estado de WebMCP (origin trial de Chrome y Edge).

**Orden de resolución** de cada peso:

1. Un ancla vigente del registro para el país y el período.
2. Si falta o venció, el agente la consulta, guarda la copia en la corrida y propone sumarla al registro.
3. Si no existe fuente pública, un prior de K elicitaciones independientes, marcado como prior en el informe.

**Literatura** (`referencias/fuentes.md`). Cada técnica con sus citas:

- perfil operacional (Musa) y cadena de uso (Whittaker y Thomason);
- distribuciones verbalizadas (Meister et al.) y mezcla de priors (AutoElicit);
- pruebas combinatorias (Kuhn);
- Morris;
- ShopCART;
- y las demás de [viabilidad.md](viabilidad.md#fuentes).

## Descubrimientos según el contexto

**Por corrida** (`hallazgos.toml`). Cada hallazgo lleva:

- id, regla y patrón;
- evidencia con extracto y commit;
- perfiles afectados;
- métricas por marcador;
- estado: `nuevo`, `confirmado`, `issue #…`, `resuelto` o `descartado`.

Al reproducir en un commit nuevo, la evidencia vencida marca el hallazgo como «posible arreglo, verificar».

**Entre proyectos** (`datos/patrones/`). Cada patrón lleva:

- `aplica_si`, una expresión sobre el contexto (stack, plataformas, formularios);
- cómo detectarlo, con regex o pistas;
- la regla genérica y su recorrido cognitivo;
- parámetros por defecto, con rango y fuente;
- los casos donde se confirmó.

En el recorrido, cada patrón aplicable se registra como presente, ausente o no verificable, siempre con evidencia. Así el
catálogo funciona como una checklist que crece con cada proyecto.

Patrones iniciales, todos del caso Volutus:

| Patrón | Qué detecta | Caso |
|---|---|---|
| P-NOMBRE-SOLO-LETRAS | Validación de nombre que rechaza guion, punto o `’` (Smart Punctuation en iOS) | [#75](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/75) |
| P-TURNSTILE-SIN-ESPERA | Turnstile cargado al primer foco y un envío que no espera el token | [#76](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/76) |
| P-ANTIBOT-SILENCIO-SIN-JS | Filtro de tiempo con un campo que solo llena JS y responde un éxito silencioso | [#74](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/74) |
| P-ESTADO-PERDIDO-ENTRE-PAGINAS | Un llamado que lleva a un formulario de otra página sin lo marcado | [#78](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/78) |
| P-MISMO-TEXTO-DOS-DESTINOS | El mismo texto de botón que lleva a destinos distintos | [#77](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/77) |
| P-RESPUESTA-SIN-JS-SIN-ENLACE | La respuesta sin JS trae el correo sin enlace y se pierde lo escrito | R7 |
| P-WEBMCP-SIN-ORIGIN-TRIAL | Anotaciones WebMCP sin token de origin trial: hoy casi nadie las usa | — |

También se guardan tres hipótesis que el código descartó, para no volver a proponerlas:

- **N-TOKEN-VENCE:** Turnstile renueva solo el token vencido.
- **N-REANUDAR-CUENTA-TIEMPO:** el inicio se guarda con las respuestas.
- **N-SIN-GPU-ROMPE:** hay escena quieta o video, y la página sigue entera.

Los issues se redactan desde `hallazgos.toml` con los marcadores ya resueltos, y se crean solo con la confirmación de
quien corre la herramienta.

## Fases de implementación

| Fase | Qué | Listo cuando |
|---|---|---|
| 0 | Rescatar el script del caso Volutus y sus salidas, que hoy están en el scratchpad de la sesión que hizo el caso, en `ejemplos/volutus/referencia/` | Los archivos están en el repo |
| 1 | Esqueleto instalable: marketplace, plugin, `simular` mínimo y `bin/statfish` | `claude plugin validate ./ --strict` pasa y se instala desde una ruta local |
| 2 | Núcleo del motor: modelo, validación, expresiones, red, cadena, muestreo y cobertura | El ejemplo Volutus reproduce exacto `contacto_total = 0,2355817451354591` y `perdida_por_codigo = 0,01271781635688427`, con 514/514 pares y 61/61 arcos |
| 3 | Análisis: incertidumbre, Morris, robustez, hipótesis, fidelidad, calibración y `comparar` | Cada fórmula de F1 a F15 pasa su test de valores conocidos |
| 4 | Evidencia con extractos, informe con marcadores, manifiesto y `reproducir` | Dos corridas con la misma semilla dan los mismos bytes; un extracto movido se marca desplazado |
| 5 | Registros: anclas de Chile, fuentes y patrones iniciales, más `contexto`, `patrones` y `anclas` | `statfish patrones` sobre Volutus devuelve los 7 patrones |
| 6 | Skills completos, agente `elicitador` y evals | `claude plugin eval` pasa los casos de activación, de artefactos y de comandos |
| 7 | Aceptación en dos repos | Ver abajo |

**Aceptación de la fase 7.** Correr de punta a punta en Volutus, con permiso para escribir `statfish/` ahí, y en un
segundo repo. Se miden los [criterios del PoC](viabilidad.md#criterios-para-un-poc):

- recall de reglas ≥ 80 %;
- precisión de la evidencia ≥ 95 %;
- divergencia de Jensen-Shannon ≤ 0,05 entre elicitaciones;
- cobertura completa de pares y arcos;
- costo ≤ USD 10 por corrida.

## Estado de la implementación

Al 2026-11-21, con el motor 0.1.0. Todo está en el repo, sin commit.

| Fase | Estado | Cómo se verificó |
|---|---|---|
| 0 | Hecha | El script del caso y sus salidas están en `ejemplos/volutus/referencia/`: copia idéntica, con el sha256 de cada archivo verificado. Al correr el script de nuevo se obtienen los mismos bytes en 40 s. |
| 1 | Hecha | `claude plugin validate ./ --strict` y `claude plugin validate ./plugins/statfish --strict` pasan. El plugin se instaló desde la ruta local con `claude plugin marketplace add` e `install` en una configuración aislada: 4 skills, el agente y unos 388 tokens fijos por sesión según `claude plugin details`. |
| 2 | Hecha | El ejemplo da exacto `contacto_total = 0,2355817451354591` y `perdida_por_codigo = 0,01271781635688427`, con 514 de 514 pares y 61 de 61 arcos. No solo esas cifras: coinciden bit a bit con el script los desenlaces, las masas, la atribución por regla, los 34 usuarios (atributos, nombres y pesos p/q) y las 64 trazas. La corrida completa tarda unos 42 s. |
| 3 | Hecha | F1 a F15 tienen tests de valores conocidos (`tests/test_formulas.py`). Los intervalos, Morris, la robustez y las hipótesis del ejemplo son iguales a los del script (`STATFISH_LENTO=1`). La suma por caminos y (I − Q)⁻¹R dan lo mismo en 200 usuarios del caso. |
| 4 | Hecha | `statfish reproducir ejemplos/volutus` da los mismos bytes en las 9 salidas. Un extracto movido se marca `desplazado`, con su cita nueva (test con un repo temporal). Las 162 citas del caso están vigentes contra `76b713a`. |
| 5 | Hecha | `statfish patrones ejemplos/volutus` devuelve los 7 patrones, más las 3 hipótesis descartadas. Hay 7 anclas en el registro (StatCounter ×4, SII, INE y WebMCP). |
| 6 | Hecha | `claude plugin eval` pasa los cuatro casos: `activa-simular`, `no-activa`, `validar-modelo-roto` y `correr-artefactos`. Fue 1 corrida por caso, sin la rama de comparación sin plugin, y costó USD 0,73. En la primera pasada, `no-activa` falló por un error del grader (`max: 0` sin `min: 0`), no del plugin. |
| 7 | Pendiente | Necesita permiso para escribir `statfish/` en Volutus y en un segundo repo |

`tests/`: 44 tests en unos 4 s, más uno lento de unos 47 s que compara la corrida completa con el script.

## Cambios respecto del plan

Lo que la implementación cambió o agregó, y por qué:

- **Distribuciones con nombre (`[[distribuciones]]`).** En el plan, una variable apuntaba al ancla dentro del caso
  (`ancla = "…"`). Ahora la distribución declara `fuente = "ancla:<id>"` y su κ, y `validar` la compara con la copia
  del ancla. Así el orden de los sorteos queda explícito, que es lo que permite reproducir exacto. Además, el caso usó
  valores ajustados para que sumaran 1, que no son los publicados.
- **Estados con argumentos y casos.** En vez de un estado por variante (`validar_nombre_formulario`, …), un estado
  recibe argumentos (`args`, `con`, `$siguiente`) y elige sus ramas por casos. El arco es (estado, acción), como en el
  caso. Por eso la cobertura sigue dando 61 arcos.
- **F3** usa la varianza de la mezcla, la de cada elicitación más la dispersión entre ellas, y no solo la dispersión.
  Con K elicitaciones idénticas, la dispersión sola daría κ infinito.
- **F9** es simétrica: el cuantil superior es S − 1 − ⌊(1−q)·S⌋. Con S = 200 coincide con el script (elementos 10 y
  189); la fórmula del plan daba 190.
- **Cobertura de arcos garantizada.** Si ningún usuario con traza alcanza un arco del universo, el motor suma un usuario
  de q que lo alcance («cobertura de arcos»). En el caso Volutus no hace falta, así que la reproducción exacta no
  cambia.
- **Agregados:**
  - `relatos.toml`, con la huella de cada usuario para marcar los relatos desactualizados;
  - `[[fidelidad]]` declarada, más la revisión automática de cada caso de la red (F12);
  - `[nombres]` para los nombres sintéticos;
  - `salida/issues/<id>.md`, los borradores de issue;
  - `statfish correr --rapido`, para iterar;
  - `corrida.py` (orquestación) y `util.py` (TOML y números en español).
- **El motor compila las expresiones.** Cada expresión validada se traduce a Python y se compila, así que el motor
  genérico corre a la velocidad del script del caso.
- **La detección del stack** ignora las carpetas de herramientas (`.claude`, `.github`…). El repo de Volutus versiona
  skills de terceros con HTML en otros idiomas.

## Lo que no hace

- No muestrea usuarios ni decide acciones con un LLM.
- El motor no accede a la red: las anclas las consulta el agente y quedan guardadas.
- No escribe fuera de la carpeta de la corrida.
- No crea issues ni commits sin confirmación.

## Riesgos y pendientes

- **Resuelto: el script del caso ya está en el repo,** en `ejemplos/volutus/referencia/`.
- **claude.ai y Cowork no instalan plugins con `bin/`:** los skills llaman a `statfish` y, si no está en el PATH, a
  `python3 "${CLAUDE_SKILL_DIR}/../../bin/statfish"`.
- **El repo en GitHub hoy es público, y está vacío.** El plan lo daba por privado. Antes del push hay que decidir si
  queda así. Lo que se sube incluye extractos del código de la landing de Volutus, que también es pública, y el
  análisis de sus fricciones, que ya está en los issues #74 a #78.
- **Requiere Python 3.11 o más,** por `tomllib`. Se probó con 3.15.
- **Sin commit ni push:** hasta subirlo, `claude plugin marketplace add DiegoPyLL/statfish` no encuentra el plugin.
  Mientras tanto se instala desde un clon local.
- **Licencia por decidir:** `plugin.json` dice `UNLICENSED` (todos los derechos reservados) como marcador.
- **Fase dinámica:** Playwright, para lo que solo existe en ejecución como la carrera de Turnstile, sigue fuera de
  este plan.
