# Resultados del caso Volutus

Último paso del caso ([recorrido](recorrido.md) → [modelo](modelo.md) → [perfiles](perfiles.md) →
[usuarios y flujos](usuarios-y-flujos.md) → resultados). Todas las cifras **describen el modelo, no el mercado**: salen
del código más priors con rango, sin un solo dato real de visitas. Su valor está en el orden y en la evidencia de cada
fricción, no en el nivel exacto.

## Lo principal

- **De cada 100 llegadas, el modelo da 23,6 contactos** (intervalo de 15,6 a 30,8) y **1,27 se pierden por el código**
  (0,65 a 2,11). Otras 2,2 llegan, pero después de una fricción.
- **Cuatro fricciones del código explican casi toda la pérdida**, todas verificadas en `archivo:línea`:
  - **R9**, la doble ruta de «Cuéntanos tu proyecto» en desarrollo web.
  - **R4**, el envío que no espera el token de Turnstile.
  - **R1**, el nombre que solo acepta letras.
  - **R8**, el estimado que se pierde al cotizar desde `/ley21719`.
- **Hay una pérdida silenciosa con respuesta de éxito: R21.** Sin JavaScript, o si `brief.js` no carga, el brief se
  descarta y la página dice «Recibimos tu brief.». Tiene poca masa (0,04 por cada 100 llegadas), pero cae sobre
  **clientes**: 7 de cada 1.000 que llenan el brief lo pierden creyendo que llegó.
- **El orden es robusto donde importa.** En 200 sorteos de los parámetros:
  - R1 queda entre las tres fricciones mayores en el 98,5 %.
  - R9 y R4 quedan entre las tres que más contactos hacen perder en el 83 % y el 75,5 %.
  - R8 solo en el 26,5 %: depende de cuánta gente busca la ley de datos, el supuesto peor anclado.
- **Arreglar las cuatro reduce la pérdida por código de 1,30 % a 0,42 %** de las llegadas (−68 %) y sube el contacto en
  0,8 puntos.
- El contacto **total** lo mueven supuestos de intención, no el código: cuántos clientes reciben el brief, cuánto
  escribe quien compara, cuántos piden la cotización. Statfish no debe presentar esa cifra como predicción sin datos.

## Desenlaces

Son 120.000 usuarios sorteados de la red, con el desenlace exacto de cada uno.

| Desenlace | De cada 100 llegadas |
|---|---|
| Contacto sin fricción | 21,39 |
| Contacto después de una fricción | 1,86 |
| Escribe al correo tras un error | 0,31 |
| Abre WhatsApp y no envía | 1,07 |
| Se va sin intentar contactar | 74,10 |
| Se va por una fricción del código | 1,23 |
| Envía y no llega nada (silencio) | 0,04 |

Casi tres de cada cuatro se van sin intentar. Eso no es una fricción del código: es la intención con que llegan (prior)
y está fuera del alcance de esta pregunta.

## Por perfil

| Perfil | P(perfil) | Contacto | Pérdida por código | Fricción que más pesa (por cada 1.000 del perfil) |
|---|---|---|---|---|
| S1 Celular o tablet Android | 36,6 % | 20,8 % | 1,02 % | R1: 7,6 con fricción; R9: 4,0 perdidos |
| S2 Escritorio, busca una página web | 9,0 % | 20,3 % | 1,94 % | **R9: 15,0 perdidos** |
| S3 Escritorio, otros servicios | 24,0 % | 21,5 % | 0,49 % | R1: 8,0 con fricción |
| S4 iPhone o iPad | 9,9 % | 21,0 % | 1,09 % | R1: 7,2; R4: 3,6 perdidos |
| S5 Negocio ante la Ley 21.719 | 9,1 % | 20,1 % | 1,88 % | **R8: 35,5 con fricción y 13,5 perdidos** |
| S6 Cliente con el link del brief | 5,0 % | 77,8 % | 2,49 % | R12: 11,5 perdidos; **R21: 6,9 en silencio** |
| S7 Entorno restrictivo | 6,4 % | 18,9 % | 3,09 % | R4b: 11,7 perdidos; R7: 8,9 |
| S8 Agente de IA por WebMCP | 0,1 % | 19,7 % | 7,50 % | **R4: 68 perdidos** |

El detalle de cada perfil está en sus [fichas](perfiles.md).

## Por regla

| Regla | Qué pasa | Se pierden (de cada 1.000 llegadas) | Llegan con fricción (de cada 1.000) |
|---|---|---|---|
| R1 | El nombre solo admite letras, marcas, espacio y apóstrofo recto: rechaza guion, punto, dígitos y & | 1,75 | 9,02 |
| R9 | En desarrollo web, «Cuéntanos tu proyecto» de la cabecera abre el brief de 35 a 45 min; el de la barra, el formulario | 3,59 | 1,65 |
| R4 | Turnstile se descarga al primer foco y el envío no espera su token: sin token, 403 | 2,97 | 3,06 |
| R8 | En `/ley21719`, «Pedir esta cotización» lleva a `/#contacto` sin lo marcado ni el servicio | 1,31 | 3,40 |
| R4b | Turnstile no se resuelve con privacidad estricta: 403 | 1,08 | 0,98 |
| R11 | En el brief, Turnstile se monta al llegar a la revisión; si falla, las respuestas siguen guardadas | 0,00 | 2,78 |
| R7 | Sin JavaScript el contacto se rechaza; la respuesta no enlaza el correo | 0,56 | 0,37 |
| R12 | Sin almacenamiento el brief no se guarda (y lo avisa) | 0,63 | 0,00 |
| R21 | Sin JavaScript, o si `brief.js` no carga, el brief se descarta en silencio con «Recibimos tu brief.» | 0,36 | 0,00 |
| R6 | WhatsApp con `window.open`; en el navegador de una app puede no abrir (por confirmar) | 0,25 | 0,23 |
| R5 | Resend no responde: 502 con el correo directo | 0,17 | 0,09 |
| R1+R2 | En iPhone y iPad el apóstrofo llega como `’` y se rechaza | 0,04 | 0,05 |
| R10 | Brief enviado antes de 8 s: descarte silencioso | 0,02 | 0,00 |

R1+R2 tiene poca masa, porque solo el 0,4 % de los nombres lleva apóstrofo. Aun así es un error de corrección: el propio
comentario de la regla quiere aceptar «O'Higgins» (`src/lib/contacto.js:89-90`), y en iPhone falla justo ese caso. El
aviso, además, es opaco.

## Incertidumbre

Son 200 sorteos de todos los parámetros (Beta para los escalares, Dirichlet para las categóricas) sobre la misma
población de 3.000 usuarios, con números aleatorios comunes.

| Métrica | p5 | p50 | p95 |
|---|---|---|---|
| Contacto (todas las vías) | 15,61 % | 22,86 % | 30,77 % |
| Pérdida atribuible al código | 0,65 % | 1,15 % | 2,11 % |
| Pasa por alguna fricción | 1,96 % | 3,35 % | 5,44 % |

**Robustez del orden.** Así se compara con la v0, donde solo el precio quedaba arriba en el 93 % de las pruebas.

| Regla | 1.ª en pérdida | Entre las 3 primeras en pérdida | Entre las 3 primeras en fricción total |
|---|---|---|---|
| R9 | 43,0 % | 83,0 % | 57,0 % |
| R4 | 29,0 % | 75,5 % | 64,0 % |
| R1 | 12,5 % | 50,0 % | **98,5 %** |
| R8 | 7,5 % | 26,5 % | 43,5 % |
| R4b | 4,0 % | 26,5 % | 11,0 % |
| R12 | 2,5 % | 17,5 % | 1,5 % |
| R7 | 1,0 % | 12,5 % | 5,0 % |
| R21 | 0,5 % | 3,0 % | 0,5 % |

## Sensibilidad

Se usó la detección de Morris: 10 trayectorias, 4 niveles y 24 supuestos movidos entre su p10 y su p90. μ* es el efecto
medio, en puntos, de recorrer el rango completo, y σ mide cuánto depende ese efecto de los demás supuestos.

| Supuesto | Rango probado | μ* sobre la pérdida (pp) | σ | μ* sobre el contacto (pp) |
|---|---|---|---|---|
| `resuelve_nombre_claro` | 70–95 % | 0,34 | 0,14 | 0,33 |
| `pega_rapido_comparando` | 5–20 % | 0,34 | 0,11 | 0,34 |
| `js_off` | 0,2–1,5 % | 0,25 | 0,04 | 0,23 |
| `contacta_comparando` | 20–45 % | 0,22 | 0,05 | 3,60 |
| `envia_brief_prospecto` | 25–65 % | 0,22 | 0,05 | 0,22 |
| `token_no_listo_rapido_movil` | 15–55 % | 0,21 | 0,14 | 0,21 |
| `abandona_seleccion_perdida` | 10–45 % | 0,21 | 0,08 | 0,20 |
| `usa_cta_brief_web` | 25–55 % | 0,20 | 0,10 | 0,17 |
| `correo_directo_tras_error` | 20–50 % | 0,19 | 0,11 | 0,19 |
| `pide_cotizacion` | 20–50 % | 0,19 | 0,08 | 2,72 |
| `nombre_empresa_signos` | 1–5 % | 0,18 | 0,10 | 0,18 |
| `sale_explorando` | 40–70 % | 0,16 | 0,06 | 2,43 |
| `estricta_base` | 1–6 % | 0,16 | 0,08 | 0,16 |
| `reintenta_tras_403` | 10–40 % | 0,15 | 0,07 | 0,15 |
| `vuelve_al_formulario` | 20–50 % | 0,14 | 0,07 | 0,13 |
| `nombre_guion_punto` | 1–4 % | 0,12 | 0,08 | 0,12 |
| `relacion_cliente_brief` | 2–10 % | 0,12 | 0,03 | 4,50 |
| `turnstile_falla_estricta` | 10–50 % | 0,12 | 0,05 | 0,12 |
| `usa_estimado_ley` | 25–55 % | 0,10 | 0,09 | 0,16 |
| `token_no_listo_rapido_escritorio` | 5–30 % | 0,06 | 0,03 | 0,06 |
| `nombre_apostrofo` | 0,1–1 % | 0,04 | 0,03 | 0,04 |
| `resuelve_nombre_opaco` | 30–80 % | 0,01 | 0,01 | 0,01 |
| `movil_si_recomendacion` | 55–85 % | 0,01 | 0,01 | 0,05 |
| `smart_punct_on` | 85–99 % | 0,00 | 0,00 | 0,00 |

Cómo se lee:

- **Ningún supuesto domina la pérdida por código:** los diez primeros mueven entre 0,19 y 0,34 puntos sobre una base de
  1,3. El nivel es incierto, pero no depende de un solo número inventado. La v0 tenía el problema contrario: el primer
  lugar del precio venía de los pesos asignados.
- **El contacto total sí lo dominan supuestos de intención** (`relacion_cliente_brief`, `contacta_comparando`,
  `pide_cotizacion`, `sale_explorando`), que el código no puede informar. Son los primeros que conviene medir.
- **Valor de la información.** Los supuestos de arriba son los que más vale la pena reemplazar por un dato: cuánto se
  resuelve el aviso del nombre, cuántos pegan y envían rápido, cuántos llegan sin JS.

## Hipótesis: qué cambia si se arregla

Se aplica cada arreglo sobre una población de 20.000 usuarios, con la misma semilla.

| Escenario | Contacto | Pérdida por código | Pasa por fricción |
|---|---|---|---|
| Hoy (modelo) | 23,74 % | 1,30 % | 3,47 % |
| R1+R2: aceptar `’`, guion y punto en el nombre | 23,82 % | 1,22 % | 3,01 % |
| R4: esperar el token antes de enviar | 24,02 % | 1,02 % | 2,95 % |
| R8: llevar lo marcado y el servicio desde `/ley21719` | 23,86 % | 1,17 % | 3,03 % |
| R9: «Cuéntanos tu proyecto» de la cabecera al formulario | 24,05 % | 0,94 % | 2,95 % |
| R21+R10: el brief sin JS (o apurado) responde como el contacto | 23,76 % | 1,27 % | 3,47 % |
| Todos | 24,56 % | 0,42 % | 1,44 % |

Esto es la «predicción» de Statfish: no un pronóstico del mercado, sino **cuánto cambia el modelo si cambia el código**.
El arreglo de R21 casi no mueve el agregado, pero su efecto está en otra unidad: 7 briefs perdidos por cada 1.000
clientes.

## Cobertura

| Medida | Resultado | Cómo |
|---|---|---|
| Pares de valores de 13 factores | **514 de 514** | 12 representativos + 22 de cobertura |
| Arcos de la cadena de uso | 31 de 61 con las trazas sorteadas; **61 de 61** con las 30 forzadas | Camino más probable por cada arco que faltaba |
| Superficies (rutas, formularios, endpoints y reglas) | 23 de 37 en el sorteo; **35 de 37** en total | Faltan `/servicios/tiendas-online` y `/servicios/desarrollo-software-a-medida` |

Las dos páginas que faltan usan el mismo marco (`src/paginas/Servicio.jsx`), el mismo estimado y las mismas reglas que
las cinco cubiertas, así que quedan cubiertas **por clase de equivalencia**. En un PoC, la cobertura de superficies
tiene que pedirse explícitamente (§ [criterios](../viabilidad.md#criterios-para-un-poc)).

## Fidelidad del generador

¿Reproduce la red lo que se declaró? Muestra de 120.000:

| Variable | Declarada | En la muestra | n |
|---|---|---|---|
| Relación: cliente con link | 5,00 % | 4,95 % | 120.000 |
| Sin JavaScript | 0,50 % | 0,45 % | 120.000 |
| Sin almacenamiento | 3,00 % | 2,97 % | 120.000 |
| Movimiento reducido | 5,00 % | 5,06 % | 120.000 |
| Nombre con apóstrofo | 0,40 % | 0,37 % | 120.000 |
| Nombre con guion o punto | 2,10 % | 2,14 % | 120.000 |
| iOS, dado celular (ancla 20,72 %) | 20,72 % | 20,72 % | 67.330 |
| Windows, dado escritorio (ancla 85,02 %) | 85,02 % | 85,12 % | 51.087 |
| Celular, dado que llega por Google (ancla 49,12 %) | 49,12 % | 48,88 % | 36.490 |
| Smart Punctuation, dado iOS o iPadOS | 95,00 % | 94,79 % | 14.891 |

La diferencia máxima es de 0,24 puntos: el generador no agrega sesgo propio. Como en la v0, esta prueba **no** dice si
los pesos son correctos. Solo dice que el script hace lo que el modelo declara.

## Comparación con el #40 y la v0

| | Issue #40 (8 y luego 80 perfiles) | v0 (100.000 perfiles, commit `87e3c0d`) | Statfish (este caso) |
|---|---|---|---|
| Fuente | El texto de las páginas, leído como 8 clientes | El texto de la página de Sistemas de gestión, convertido en un catálogo de dudas | El código entero: superficies, reglas, servidor y entorno |
| Qué encuentra | Dudas de negocio sin respuesta: plazos, qué pasa después, prueba, datos de empresa | Frenos por duda; el precio fue el único robusto | Fricciones de flujo y de entorno, con evidencia `archivo:línea` |
| Probabilidad | No | Pesos explícitos y semilla | Anclas y priors con rango; desenlace exacto por usuario; Monte Carlo y Morris |
| Validación | Revisión del equipo | Fidelidad, modelo nulo y sensibilidad | Fidelidad, robustez del orden, Morris, cobertura de pares, arcos y superficies |

**Lo que se repite.**

- El tope de 500 caracteres del #40 ya está resuelto: el código dice 2.000 (`src/lib/contacto.js:83`).
- «Qué pasa después de enviar el formulario» sigue abierto en el #40, y el código lo confirma: el aviso sigue siendo solo
  «Te responderemos pronto.» (`src/client.js:52`).
- El freno más robusto de la v0, el precio, hoy tiene respuesta en el código: el estimado está en todas las páginas de
  servicio (`src/lib/precios.js:52-150`).

**Lo que solo ve el código.** R1 y R1+R2, R4, R8, R9, R21 y R10, el estado de WebMCP sin token de origin trial, y las
hipótesis que el código descartó (§ [recorrido](recorrido.md#hipótesis-que-el-código-descartó)). Ninguno estaba en el
#40 ni en la v0.

**Lo que el código no ve.** Las dudas de negocio del #40 y de la v0: plazos, prueba parecida, factura, «ya probé algo
que no sirvió». Los textos que las responden están en el código (`src/data/paginas-de-servicio.js`), pero convertirlos en
dudas pide la capa de catálogo que hizo la v0. **Statfish y la v0 se complementan:** la cadena de uso de este caso podría
recibir el catálogo de dudas de la v0 como otro freno más en el paso «¿Escribe?».

## Hallazgos llevados a issues

Son las fricciones que salieron de las trazas, que se verificaron en el código y que afectan a alguien real.

| Issue | Regla | Por qué |
|---|---|---|
| [#74](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/74) · bug | R21 (+R10) | Pérdida silenciosa de briefs de clientes con respuesta de éxito |
| [#75](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/75) · bug | R1, R1+R2 | Fricción más robusta (98,5 %); el caso de iPhone contradice el comentario de la propia regla |
| [#76](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/76) · bug | R4 | Entre las tres mayores pérdidas en el 75,5 % de los sorteos; el aviso no dice que basta reintentar |
| [#77](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/77) · enhancement | R9 | Mayor pérdida en el 43 % de los sorteos; dos destinos con el mismo texto |
| [#78](https://github.com/VolutusDevelopment/VolutusLandingPage/issues/78) · enhancement | R8 | El único servicio cuyo estimado no llega al formulario |

No se abrieron issues por:

- R4b, R5 y R12: ya tienen salida y aviso.
- R6: falta confirmarla en un dispositivo real.
- R7: se menciona dentro del issue de R21.
- WebMCP sin token: hoy no afecta a nadie.

## Calibración

El sitio no usa analítica, y eso es una decisión que hay que respetar. La calibración mínima que no pide datos personales
tiene dos partes:

1. **Contadores en el Worker por motivo de respuesta**, sin IP ni contenido. Por ejemplo, en `/api/contacto`: 200,
   trampa, 400, 403 con token vacío, 403 con token inválido, 429 y 502. En `/api/brief`: 200, trampa,
   `transcurrido` vacío, menos de 8 s, 403, 429 y 502. Calibran directamente R4, R4b, R5, R7, R10 y R21. El Worker ya
   tiene la observabilidad activa (`wrangler.jsonc:53-60`).
2. **Una línea por consulta real**: en qué paso estaba y qué lo frenó, con los mismos códigos de regla. Es lo que
   recomendaba la v0.

Con esos conteos n, cada parámetro se actualiza en forma conjugada:

- un parámetro binario con prior Beta(α, β) pasa a Beta(α + éxitos, β + fracasos);
- una categórica con prior Dirichlet(κ·p) pasa a Dirichlet(κ·p + n).

Con κ entre 10 y 15, unas pocas decenas de casos ya mueven los pesos de forma visible. La diferencia entre el prior y el
posterior mide cuánto dependía este informe de los supuestos.
