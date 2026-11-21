# Formato de `modelo.toml`

Un archivo por corrida. Lo lee `statfish validar` y lo calcula `statfish correr`. Las expresiones y
plantillas siguen [expresiones.md](expresiones.md). El ejemplo completo está en `ejemplos/volutus/modelo.toml`
del repo del plugin.

**El orden importa.** El orden de los parámetros y de las distribuciones fija el orden de los sorteos de la
incertidumbre. El de las variables es el orden de evaluación de la red: cada variable solo puede usar las
anteriores. El de los casos y las ramas fija qué se aplica y en qué orden se suman las probabilidades. Con el
mismo orden y la misma semilla salen los mismos bytes.

## Cabecera y tamaños

```toml
[modelo]
nombre = "Volutus, landing: quién no logra cotizar ni contactar"
descripcion = "…"
nota = "…"                     # aparece en el informe, debajo de la cabecera

[corrida]
semilla = 20261120
uniformes = 26                 # opcional: uniformes por usuario (por defecto, los que usa la red)
poblacion = 120000             # usuarios con desenlace exacto, parámetros en p50
representativos = 12           # usuarios sorteados tal cual
sorteos_parametros = 200       # sorteos de la incertidumbre (F9, F11)
usuarios_incertidumbre = 3000  # misma población en cada sorteo
usuarios_hipotesis = 20000

[informe]
titulo = "…"
metricas_principales = ["contacto_total", "perdida_por_codigo", "con_friccion"]
```

`statfish correr --rapido` divide los tamaños para iterar. El manifiesto deja constancia de que la corrida
fue rápida.

## Parámetros

```toml
[[parametros]]
id = "movil_si_redes"
texto = "Celular, si llega por redes"
p50 = 0.80
p10 = 0.65
p90 = 0.90
fuente = "prior:elicitacion"          # ancla:<id> | prior:elicitacion | codigo:<regla> | definicion
anclas = ["statcounter-CL-plataforma-2026-10"]   # opcional: anclas que informan el prior
nota = "…"

[[parametros]]
id = "arreglo_r1"                     # interruptor de una hipótesis: vale false, no se sortea
texto = "Arreglo de R1"
interruptor = true
```

- Se exige 0 ≤ p10 ≤ p50 ≤ p90 ≤ 1.
- En la incertidumbre cada parámetro se sortea con una Beta ajustada a sus cuantiles (F1).
- Si p10 = p90, el parámetro queda fijo.

## Distribuciones categóricas

```toml
[[distribuciones]]
id = "disp_base"
valores = { escritorio = 0.5005, movil = 0.4912, tablet = 0.0083 }
kappa = 200                                     # opcional: por defecto según la fuente (F2)
fuente = "ancla:statcounter-CL-plataforma-2026-10"
nota = "Tablet ajustada a 0,83 % para que la suma dé 1."
```

- Las probabilidades suman 1, con una tolerancia de 10⁻⁹.
- En la incertidumbre cada distribución se sortea como Dirichlet(κ·p).
- Con `fuente = "ancla:<id>"`, `validar` compara cada valor con el ancla copiada en `anclas/` y avisa si se
  aparta más de 1 punto.

## Variables (la red)

```toml
[[variables]]
id = "dispositivo"
valores = ["escritorio", "movil", "tablet"]     # el soporte, que sale del código
uniforme = 2                                    # opcional: índice de su uniforme (F4)
soporte = [{ cita = "CLAUDE.md:102-119", extracto = "## 5. Responsive Design" }]
relato = false                                  # true: solo relato, no puede tocar el flujo

  [[variables.casos]]                           # se aplica el primero que calza
  si = "relacion == 'cliente_brief'"
  dist = "disp_cliente"                         # una distribución declarada

  [[variables.casos]]
  si = "canal == 'redes'"
  dist = { movil = "p.movil_si_redes", tablet = "0.01", escritorio = "1 - p.movil_si_redes - 0.01" }

  [[variables.casos]]
  dist = "disp_base"                            # sin si: siempre calza
```

Cada caso lleva exactamente uno de estos:

| Clave | Qué hace | Consume su uniforme |
|---|---|---|
| `valor = "<expresión>"` | Valor determinista | No |
| `prob = "<expresión>"` | Booleana: `true` si u < p (la variable lleva `valores = [true, false]`) | Sí |
| `dist = "<id>"` | Sortea de una distribución declarada | Sí |
| `dist = { v = "<expr>", … }` | Sortea de una distribución en línea, con probabilidades como expresiones | Sí |

Con `dist` pueden ir dos modificadores:

- **`inclinacion = { v = factor, … }`** multiplica cada probabilidad por su factor, que vale 1 si falta, y
  normaliza. Una tabla vacía igual normaliza.
- **`transformar = "<expresión con x>"`** cambia el valor sorteado `x` por otro. La probabilidad del valor
  final suma la de los valores crudos que llevan a él.

Cada variable aleatoria tiene su propio uniforme. Por eso cambiar un peso no reordena a las demás (números
aleatorios comunes, F4). Los índices explícitos se respetan; los demás toman el siguiente libre en orden de
declaración.

## Restricciones

```toml
[[restricciones]]
texto = "iOS y iPadOS usan WebKit, sea cual sea el navegador"
expr = "sistema not in ('ios', 'ipados') or motor == 'webkit'"
evidencia = [{ cita = "CLAUDE.md:124", extracto = "…" }]
```

`validar` las revisa sobre usuarios sorteados con p50, con la red aplanada y con parámetros sorteados.
`correr` las revisa sobre todos los usuarios con traza.

## Reglas

```toml
[[reglas]]
id = "R1"
texto = "El nombre solo admite letras, marcas, espacio y apóstrofo recto"
friccion = true                       # puede hacer perder o demorar el objetivo
patron = "P-NOMBRE-SOLO-LETRAS"       # opcional: patrón del catálogo
cw = ["sí", "sí", "sí", "en parte"]   # recorrido cognitivo: intenta, nota, asocia, ve el progreso
nota_cw = "El aviso dice qué hacer, pero le pide escribir su nombre de otra forma."
evidencia = [{ cita = "src/lib/contacto.js:89-91", extracto = "export const NOMBRE_VALIDO = …" }]
```

La evidencia es obligatoria: sin cita no entra al modelo. Cada `cw` vale «sí», «no» o «en parte».

## La cadena de uso

```toml
[cadena]
inicio = "inicio"
profundidad_maxima = 30            # suma por caminos; si se pasa, se resuelve (I − Q)⁻¹R (F7)
atribuibles = ["abandono_por_friccion", "perdida_silenciosa", "correo_directo", "contacto_con_friccion"]
perdida = ["abandono_por_friccion", "perdida_silenciosa"]   # cuentan como «se pierden»
con_friccion = { contacto = "contacto_con_friccion" }       # el desenlace cambia si hubo fricción

[cadena.desenlaces]                # id = texto; el orden es el de las tablas
contacto = "Contacto sin fricción"
contacto_con_friccion = "Contacto después de una fricción"
abandono_por_friccion = "Se va por una fricción del código"
```

Un estado puede tener argumentos (`args`), con `por_defecto` opcional, y locales (`locales`), que se evalúan
en orden. Sus ramas van directas (`[[estados.ramas]]`) o por casos (`[[estados.casos]]`): se aplica el
primer caso que calza, con sus propios `locales` y `ramas`.

```toml
[[estados]]
id = "envio_correo"
args = ["intento"]
por_defecto = { intento = 1 }
nombre = "Envío por correo{' (2.º intento)' if intento == 2 else ''}"   # plantilla: el estado en la traza
superficies = ["POST /api/contacto"]                                     # se tocan al pasar por el estado

[estados.locales]
tn = "p.token_no_listo_normal if intento == 1 else 0.002"
tf = "p.turnstile_falla_normal"

  [[estados.ramas]]
  prob = "(1 - tn) * (1 - tf)"
  va = "FIN:contacto"                 # FIN:<desenlace>, <estado> o $<argumento>
  accion = "envía: «¡Gracias por escribirnos!»"

  [[estados.ramas]]
  si = "agente"                       # opcional: la rama existe solo si calza
  prob = "tn"
  va = "tras_error"
  con = { intento = "intento", causa = "'R4'" }   # argumentos del destino (expresiones)
  accion = "envía antes de que llegue el token: 403"
  arco = "403 sin token"              # opcional: identidad del arco en la cobertura (por defecto, accion)
  regla = "R4"                        # plantilla: puede ser "{causa}"
  superficies = ["aviso de error"]    # opcional: se tocan al tomar la rama
```

Las reglas de cada estado:

- Las ramas de un estado suman 1 para cada usuario. `validar` lo revisa.
- Las ramas con probabilidad 0 no existen: no se sortean, no se recorren y no cuentan como arcos.
- El desenlace de un camino se atribuye a la **última regla de fricción** del camino (F8). Si el desenlace
  está en `con_friccion` y hubo fricción, cambia.
- Un arco es el par (estado, `arco` o `accion`), sin los argumentos. Las rutas concretas se modelan como
  superficies.
- Un destino `$siguiente` toma el estado de un argumento. Los argumentos que el destino no recibe salen de
  su `por_defecto`.

## Métricas

```toml
[[metricas]]
id = "perdida_por_codigo"
texto = "Pérdida atribuible al código"
expr = "abandono_por_friccion + perdida_silenciosa"   # suma de desenlaces, en este orden
```

## Perfiles

```toml
[[perfiles]]          # se aplica el primero que calza; el último debería ser si = "True"
id = "S6"
nombre = "Cliente con el link del brief"
si = "relacion == 'cliente_brief'"
```

El informe los lista por id, en orden natural: S1, S2, …, S10.

## Cobertura

```toml
[[factores]]          # todos los pares de valores de estos factores deben aparecer (F6)
id = "plataforma"
expr = "'android' if sistema == 'android' else 'otra'"

[[superficies]]       # además de estas, cada regla cuenta como superficie
id = "/servicios/tiendas-online"
clase = "página de servicio (src/paginas/Servicio.jsx)"   # clase de equivalencia
usuario = "agente"    # opcional: se toca por el usuario, sin una rama propia

[cobertura]
candidatos_universo = 60000      # usuarios de q para estimar el universo de pares
candidatos_por_vuelta = 3000     # candidatos por vuelta del AETG
universo_arcos = 20000           # de esos, cuántos se usan para el universo de arcos

[cobertura.aplanada.parametros]  # q: la misma red con lo raro inflado
js_off = 0.15

[cobertura.aplanada.distribuciones]
canal = { google = 0.2, redes = 0.8 }
servicio_base = "uniforme"
```

## Sensibilidad

```toml
[sensibilidad]        # Morris (F10); el orden de los parámetros fija los sorteos
parametros = ["resuelve_nombre_claro", "pega_rapido_comparando"]
metricas = ["contacto_total", "perdida_por_codigo"]
ordenar_por = "perdida_por_codigo"
trayectorias = 10
niveles = 4
usuarios = 2000       # los primeros de la población de incertidumbre
```

## Hipótesis

```toml
[[hipotesis]]         # solo cambios de parámetros; un arreglo es un interruptor
id = "r9"
texto = "R9: «Cuéntanos tu proyecto» de la cabecera al formulario"
cambios = { usa_cta_brief_web = 0.0 }
```

## Fidelidad del generador

Además de la revisión automática de cada caso de la red (F12), se pueden declarar marginales:

```toml
[[fidelidad]]
texto = "iOS, dado celular (ancla)"
expr = "sistema == 'ios'"
dado = "dispositivo == 'movil'"
declarada = "d.sistema_movil.ios"
```

## Nombres sintéticos

```toml
[nombres.listas]
persona = ["Camila", "Matías"]
apellido = ["González", "Muñoz"]

[[nombres.casos]]     # se aplica el primero que calza; sorteos en orden, el último gana
si = "nombre_tipo == 'empresa_signos'"
sorteos = ["nombre:persona", "apellido:apellido", "empresa:empresa"]
plantilla = "{empresa}"
```

Los nombres no son de personas reales. Si uno se repite, se sortea de nuevo.

## Los otros archivos de la corrida

| Archivo | Quién lo escribe | Qué guarda |
|---|---|---|
| `contexto.toml` | `statfish contexto` | Pregunta, país, público, fecha, repo y su ruta relativa, commit, stack |
| `recorrido.toml` | El agente | Bitácora, mapa del código, checklist de patrones, hipótesis descartadas |
| `anclas/` | `statfish anclas --copiar` o el agente | Copias de las anclas que usa la corrida |
| `elicitacion/k*.json` | El agente `elicitador` | Las K respuestas, tal cual |
| `elicitacion/combinada.json` | `statfish elicitar combinar` | La mezcla (F3) y la divergencia (F13) |
| `relatos.toml` | El agente | Una línea por usuario, con su `huella` |
| `hallazgos.toml`, `lectura.md` | El agente | Con marcadores (ver [informe.md](informe.md)) |
| `conteos.toml`, `calibracion.toml` | El agente y `statfish calibrar` | Conteos reales y parámetros posteriores |
| `salida/`, `informe.md`, `manifiesto.json` | `statfish correr` | Lo calculado; no se edita a mano |
