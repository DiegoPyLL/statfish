# Statfish · Volutus: quién no logra cotizar ni contactar

| | |
|---|---|
| Pregunta | ¿Qué usuarios no logran cotizar ni contactar a Volutus, en qué paso y por qué? ¿Qué entornos técnicos rompen la experiencia? |
| Repositorio | `VolutusDevelopment/VolutusLandingPage` @ `76b713a` |
| Fecha | 2026-11-20 |
| País y público | CL · Dueños de negocios chicos y medianos de Chile, y clientes de Volutus con el link del brief |
| Semilla y motor | 20261120 · statfish 0.1.0 |
| Población | 120.000 usuarios con desenlace exacto; 34 usuarios con traza |

Todas las cifras **describen el modelo, no el mercado**: salen del código, de anclas públicas y de priors con rango. Su valor está en el orden y en la evidencia de cada fricción, no en el nivel exacto.

> Caso de prueba de la viabilidad. Los priors salen de una sola elicitación del agente que hizo el caso (K = 1), sin mezcla de elicitaciones independientes.

## Lectura

**De cada 100 llegadas, el modelo da 23,6 contactos** (intervalo de
15,6 a 30,8) y **1,27 se
pierden por el código** (0,65 a 2,11). Otras
1,9 llegan, pero después de una fricción.

**Cuatro fricciones del código explican casi toda la pérdida**, todas verificadas en `archivo:línea`:

- **R9**, la doble ruta de «Cuéntanos tu proyecto» en desarrollo web: 3,59 de cada 1.000 llegadas
  se pierden, y 15,0 de cada 1.000 entre quienes buscan una página web desde el
  escritorio.
- **R4**, el envío que no espera el token de Turnstile: 2,97 de cada 1.000, y
  63 de cada 1.000 agentes de IA.
- **R1**, el nombre que solo acepta letras: 9,02 de cada 1.000 llegan con fricción y
  1,75 se pierden.
- **R8**, el estimado que se pierde al cotizar desde `/ley21719`: 35,4 de cada
  1.000 de quienes buscan la ley llegan con fricción y 13,5 se van.

**Hay una pérdida silenciosa con respuesta de éxito: R21.** Sin JavaScript, o si `brief.js` no carga, el brief se
descarta y la página dice «Recibimos tu brief.». Tiene poca masa (0,04 de cada 100
llegadas), pero cae sobre **clientes**: 6,3 de cada 1.000 que llenan el brief lo
pierden creyendo que llegó.

**El orden es robusto donde importa.** En 200 sorteos de los parámetros, R1 queda entre las tres fricciones
mayores en el 98,5 %; R9 y R4 quedan entre las tres que más contactos hacen perder en el
83,0 % y el 75,5 %. R8 solo en el 26,5 %:
depende de cuánta gente busca la ley de datos, el supuesto peor anclado (su perfil pesa entre el
0,7 % y el 22,5 % de las llegadas).

**Arreglar las cuatro reduce la pérdida por código de 1,30 % a
0,42 %** de las llegadas
(−67 %)
y sube el contacto en 0,8 puntos. Esa es la
«predicción» de Statfish: no un pronóstico del mercado, sino cuánto cambia el modelo si cambia el código.

**El contacto total lo mueven supuestos de intención, no el código.** En la sensibilidad, los supuestos con más efecto
sobre el contacto son cuántos clientes reciben el brief, cuánto escribe quien compara, cuántos piden la cotización y
cuántos salen de inmediato. Ninguno lo informa el código: son los primeros que conviene medir, y la cifra de contacto no
debe presentarse como predicción sin datos.

**Ningún supuesto domina la pérdida por código.** El que más la mueve es `resuelve_nombre_claro`, con
0,34 puntos al recorrer su rango, sobre una base de
1,27. El nivel es incierto, pero no depende de un solo número inventado: la v0 tenía el
problema contrario, donde el primer lugar del precio venía de los pesos asignados.

### Lo que el código no ve

Las dudas de negocio del issue #40 y de la v0: plazos, una prueba parecida, factura, «ya probé algo que no sirvió». Los
textos que las responden están en el código, pero convertirlos en dudas pide la capa de catálogo que hizo la v0. Statfish
y la v0 se complementan: esta cadena de uso podría recibir ese catálogo como un freno más en el paso «¿Escribe?».

### Calibración

El sitio no usa analítica, y eso se respeta. La calibración mínima sin datos personales son contadores en el Worker por
motivo de respuesta (200, trampa, 400, 403 sin token, 403 con token inválido, 429 y 502; en el brief, también
`transcurrido` vacío y menos de 8 s). Calibran directamente R4, R4b, R5, R7, R10 y R21 con `statfish calibrar`.

## Desenlaces

| Desenlace | De cada 100 llegadas |
|---|---|
| Contacto sin fricción | 21,39 |
| Contacto después de una fricción | 1,86 |
| Escribe al correo tras un error | 0,31 |
| Abre WhatsApp y no envía | 1,07 |
| Se va sin intentar contactar | 74,10 |
| Se va por una fricción del código | 1,23 |
| Envía y no llega nada (silencio) | 0,04 |

## Métricas con intervalo

p5, p50 y p95 de 200 sorteos de todos los parámetros sobre 3.000 usuarios, con números aleatorios comunes.

| Métrica | Modelo (p50) | p5 | p50 | p95 |
|---|---|---|---|---|
| Contacto (todas las vías) | 23,56 % | 15,61 % | 22,86 % | 30,77 % |
| Pérdida atribuible al código | 1,27 % | 0,65 % | 1,15 % | 2,11 % |
| Pasa por alguna fricción | 3,44 % | 1,96 % | 3,35 % | 5,44 % |

## Perfiles

| Perfil | Quién | P(perfil) | p5–p95 | Contacto (todas las vías) | Pérdida atribuible al código | Pasa por alguna fricción | Regla que más pesa (por cada 1.000 del perfil) |
|---|---|---|---|---|---|---|---|
| S1 | Celular o tablet Android | 36,6 % | 29,2 % – 45,5 % | 20,77 % | 1,02 % | 2,48 % | R1: 1,6 perdidos, 7,9 con fricción |
| S2 | Escritorio, busca una página web | 9,0 % | 2,8 % – 16,4 % | 20,33 % | 1,94 % | 3,86 % | R9: 15,0 perdidos, 7,2 con fricción |
| S3 | Escritorio, otros servicios | 24,0 % | 14,1 % – 31,4 % | 21,48 % | 0,49 % | 1,66 % | R1: 1,6 perdidos, 8,4 con fricción |
| S4 | iPhone o iPad (WebKit, Smart Punctuation) | 9,9 % | 7,2 % – 14,4 % | 20,96 % | 1,09 % | 2,59 % | R1: 1,6 perdidos, 7,9 con fricción |
| S5 | Negocio ante la Ley 21.719 | 9,1 % | 0,7 % – 22,5 % | 20,07 % | 1,88 % | 6,60 % | R8: 13,5 perdidos, 35,4 con fricción |
| S6 | Cliente con el link del brief | 5,0 % | 0,9 % – 10,5 % | 77,76 % | 2,49 % | 10,39 % | R11: 0,0 perdidos, 50,4 con fricción |
| S7 | Entorno restrictivo (sin JS, privacidad estricta o sin almacenamiento) | 6,4 % | 2,4 % – 11,4 % | 18,91 % | 3,09 % | 6,24 % | R4b: 12,0 perdidos, 10,4 con fricción |
| S8 | Agente de IA por WebMCP | 0,1 % | 0,0 % – 0,2 % | 19,67 % | 7,50 % | 15,76 % | R4: 62,5 perdidos, 64,6 con fricción |

## Reglas

| Regla | Qué pasa | Se pierden (de cada 1.000 llegadas) | Llegan con fricción (de cada 1.000) | Evidencia |
|---|---|---|---|---|
| R1 | El nombre solo admite letras, marcas, espacio y apóstrofo recto: rechaza guion, punto, dígitos y & | 1,75 | 9,02 | `src/lib/contacto.js:89-91`, `src/client.js:82-85` … |
| R9 | En desarrollo web, «Cuéntanos tu proyecto» de la cabecera abre el brief de 35 a 45 min; el de la barra, el formulario | 3,59 | 1,65 | `src/data/paginas-de-servicio.js:66`, `src/paginas/Servicio.jsx:89` … |
| R4 | Turnstile se descarga al primer foco del formulario y el envío no espera su token: sin token, 403 | 2,97 | 3,06 | `src/lib/turnstile.js:53`, `src/lib/turnstile.js:27-51` … |
| R8 | En /ley21719, «Pedir esta cotización» y «Cuéntanos tu proyecto» llevan a /#contacto: sin lo marcado ni el servicio | 1,31 | 3,40 | `src/paginas/Ley21719.jsx:429`, `src/paginas/Ley21719.jsx:264` … |
| R4b | Turnstile no se resuelve con privacidad estricta: 403 | 1,08 | 0,98 | `worker/comun.js:130-152` |
| R11 | En el brief, Turnstile se monta al llegar a la revisión; si falla, las respuestas siguen guardadas | 0,00 | 2,78 | `src/comportamiento/brief/brief.js:408`, `src/comportamiento/brief/brief.js:52-53` … |
| R7 | Sin JavaScript el envío llega sin token y se rechaza; la respuesta es una página aparte sin enlace al correo | 0,56 | 0,37 | `src/components/Contacto.jsx:23-25`, `worker/index.js:34-40` … |
| R12 | Sin almacenamiento, el brief no se guarda y lo avisa | 0,63 | 0,00 | `src/lib/almacen.js:1-3`, `src/comportamiento/brief/brief.js:163-166` |
| R21 | Sin JavaScript (o si brief.js no carga) el brief llega con «transcurrido» vacío: se descarta en silencio y la página dice «Recibimos tu brief.» | 0,36 | 0,00 | `src/paginas/Brief.jsx:326`, `src/comportamiento/brief/brief.js:640` … |
| R6 | WhatsApp se abre con window.open; en el navegador de una app puede no abrir | 0,25 | 0,23 | `src/client.js:202-214` |
| R5 | Resend no responde: 502 con el correo directo | 0,17 | 0,09 | `worker/index.js:121-123`, `worker/comun.js:163-192` |
| R1+R2 | En iPhone y iPad el apóstrofo se escribe ’ (Smart Punctuation) y la regla del nombre lo rechaza | 0,04 | 0,05 | `src/lib/contacto.js:89-91`, `src/components/Contacto.jsx:121-130` … |
| R10 | El brief enviado antes de 8 s se descarta en silencio con 200 y el navegador borra lo guardado | 0,02 | 0,00 | `src/lib/brief/reglas.js:38-40`, `worker/brief.js:280-285` … |

## Robustez del orden

En 200 sorteos de los parámetros: con qué frecuencia cada regla queda primera o entre las tres primeras.

| Regla | 1.ª en pérdida | Entre las 3 primeras en pérdida | Entre las 3 primeras en fricción total |
|---|---|---|---|
| R9 | 43,0 % | 83,0 % | 57,0 % |
| R4 | 29,0 % | 75,5 % | 64,0 % |
| R1 | 12,5 % | 50,0 % | 98,5 % |
| R8 | 7,5 % | 26,5 % | 43,5 % |
| R4b | 4,0 % | 26,5 % | 11,0 % |
| R12 | 2,5 % | 17,5 % | 1,5 % |
| R7 | 1,0 % | 12,5 % | 5,0 % |
| R6 | 0,0 % | 3,5 % | 0,0 % |
| R21 | 0,5 % | 3,0 % | 0,5 % |
| R5 | 0,0 % | 2,0 % | 0,0 % |
| R11 | 0,0 % | 0,0 % | 19,0 % |

## Sensibilidad (Morris)

10 trayectorias y 4 niveles, cada supuesto entre su p10 y su p90. μ* es el efecto medio, en puntos, de recorrer el rango completo; σ mide cuánto depende de los demás supuestos.

| Supuesto | Rango probado | μ* sobre pérdida atribuible al código (pp) | σ | μ* sobre contacto (todas las vías) (pp) |
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

## Hipótesis: qué cambia si se arregla

Cada arreglo sobre la misma población de 20.000 usuarios.

| Escenario | Contacto (todas las vías) | Pérdida atribuible al código | Pasa por alguna fricción |
|---|---|---|---|
| Hoy (modelo) | 23,74 % | 1,30 % | 3,47 % |
| R1+R2: aceptar ’, guion y punto en el nombre | 23,82 % | 1,22 % | 3,01 % |
| R4: esperar el token antes de enviar | 24,02 % | 1,02 % | 2,95 % |
| R8: llevar lo marcado y el servicio desde /ley21719 | 23,86 % | 1,17 % | 3,03 % |
| R9: «Cuéntanos tu proyecto» de la cabecera al formulario | 24,05 % | 0,94 % | 2,95 % |
| R21+R10: el brief sin JS (o apurado) responde como el contacto | 23,76 % | 1,27 % | 3,47 % |
| Todos | 24,56 % | 0,42 % | 1,44 % |

## Cobertura

| Medida | Resultado | Cómo |
|---|---|---|
| Pares de valores de 13 factores | **514 de 514** | 12 representativos + 22 de cobertura |
| Arcos de la cadena de uso | 31 de 61 con las trazas sorteadas; **61 de 61** con las forzadas | Camino más probable por cada arco que faltaba |
| Superficies (rutas, formularios, endpoints y reglas) | 23 de 37 en el sorteo; **35 de 37** en total; 31 de 31 clases | Las que faltan, con su clase de equivalencia, abajo |

- `/servicios/tiendas-online` (página de servicio (src/paginas/Servicio.jsx)): cubierta por su clase (`/servicios/desarrollo-web`, `/servicios/sistemas-de-gestion`, `/servicios/automatizacion-procesos`).
- `/servicios/desarrollo-software-a-medida` (página de servicio (src/paginas/Servicio.jsx)): cubierta por su clase (`/servicios/desarrollo-web`, `/servicios/sistemas-de-gestion`, `/servicios/automatizacion-procesos`).

## Fidelidad del generador

¿Reproduce la red lo que se declaró? No dice si los pesos son correctos: dice que el generador hace lo que el modelo declara (F12: |declarada − muestra| ≤ 3σ).

| Variable | Declarada | En la muestra | n | Dentro de 3σ |
|---|---|---|---|---|
| Relación: cliente con link | 5,00 % | 4,95 % | 120.000 | sí |
| Sin JavaScript | 0,50 % | 0,45 % | 120.000 | sí |
| Sin almacenamiento | 3,00 % | 2,97 % | 120.000 | sí |
| Movimiento reducido | 5,00 % | 5,06 % | 120.000 | sí |
| Nombre con apóstrofo | 0,40 % | 0,37 % | 120.000 | sí |
| Nombre con guion o punto | 2,10 % | 2,14 % | 120.000 | sí |
| iOS, dado celular (ancla) | 20,72 % | 20,72 % | 67.330 | sí |
| Windows, dado escritorio (ancla) | 85,02 % | 85,12 % | 51.087 | sí |
| Celular, dado que llega por Google (ancla) | 49,12 % | 48,88 % | 36.490 | sí |
| Smart Punctuation, dado iOS o iPadOS | 95,00 % | 94,79 % | 14.891 | sí |

Revisión automática de cada caso de la red: 192 valores, 0 fuera de 3σ.

Restricciones duras: 6 revisadas sobre los 34 usuarios, 0 violaciones.

## Evidencia

162 citas (95 distintas) verificadas contra `76b713a`: 162 vigentes. Precisión automática: 100,0 %.

## Fuentes de los pesos

Parámetros y distribuciones por fuente: 78 priors elicitados, 3 anclas públicas, 2 por definición.

Elicitación: K = 1. Con K = 1 no hay estabilidad que medir.

| Ancla | Fuente | Consultada | Vence | Uso |
|---|---|---|---|---|
| `ine-CL-empresas-activas-2025` | [Empresas activas en Chile, 2025 (1.207.333, alza de 3,9 %)](https://www.cnnchile.com/negocios/ine-registra-1207333-empresas-activas-chile-2025-alza-39/) | 2026-11-20 | 2027-11-20 (vigente) | informa region |
| `sii-CL-empresas-tamano-2024` | [Empresas con ventas por tamaño, Chile, 2024](https://www.sii.cl/sobre_el_sii/estadisticas_de_empresas.html) | 2026-11-20 | 2027-11-20 (vigente) | informa region, tamano |
| `statcounter-CL-navegador-2026-10` | [Navegador (todas las plataformas), Chile, oct-2026](https://gs.statcounter.com/browser-market-share/all/chile) | 2026-11-20 | 2027-05-20 (vigente) | informa nav_android, nav_windows |
| `statcounter-CL-plataforma-2026-10` | [Plataforma (escritorio, celular, tablet), Chile, oct-2026](https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet/chile) | 2026-11-20 | 2027-05-20 (vigente) | ancla de disp_base |
| `statcounter-CL-sistema-escritorio-2026-10` | [Sistema del escritorio, Chile, oct-2026](https://gs.statcounter.com/os-market-share/desktop/chile) | 2026-11-20 | 2027-05-20 (vigente) | ancla de sistema_escritorio |
| `statcounter-CL-sistema-movil-2026-10` | [Sistema del celular, Chile, oct-2026](https://gs.statcounter.com/os-market-share/mobile/chile) | 2026-11-20 | 2027-05-20 (vigente) | ancla de sistema_movil |
| `webmcp-estado-2026-11` | [WebMCP: origin trial de Chrome (149 a 156, extendido a 162) y de Edge; Safari se opone](https://www.spronta.com/blog/state-of-webmcp-july-2026/) | 2026-11-20 | 2027-01-20 (vigente) | informa agente_en_chrome_escritorio |

## Hallazgos

| Hallazgo | Regla | Estado | Perfiles | Resumen |
|---|---|---|---|---|
| H-R21 | R21 | issue #74 | S6, S8 | Pérdida silenciosa con respuesta de éxito: 6,3 de cada 1.000 clientes pierden el brief creyendo que llegó. |
| H-R1 | R1 | issue #75 | S1, S2, S3, S4, S5, S6, S7 | La fricción más robusta: entre las tres mayores en el 98,5 % de los sorteos; 9,0 de cada 1.000 llegan con fricción. |
| H-R4 | R4 | issue #76 | S1, S4, S8 | Entre las tres mayores pérdidas en el 75,5 % de los sorteos; en los agentes, 63 de cada 1.000 se pierden. |
| H-R9 | R9 | issue #77 | S2, S1 | La mayor pérdida en el 43,0 % de los sorteos; arreglarla baja la pérdida por código de 1,30 % a 0,94 %. |
| H-R8 | R8 | issue #78 | S5 | Entre quienes buscan la ley de datos, 35,4 de cada 1.000 reescriben lo marcado y 13,5 se van. |
| H-R7 | R7 | confirmado | S7 | 0,56 de cada 1.000 llegadas se pierden; se menciona dentro del issue de R21, sin issue propio. |
| H-WEBMCP | — | confirmado | S8 | Hoy casi no afecta a nadie: el perfil de agentes pesa 0,1 % de las llegadas. Sin issue. |

## Anexo A: usuarios

Los atributos los sortea el motor con la semilla; los nombres son sintéticos y el relato, si lo hay, se escribió después, solo con esos atributos.

| Id | Cómo se creó | Peso p/q | Perfil | Nombre (sintético) | Lo distinto (factores) | Desenlace sorteado | Contacto (todas las vías) esperado | Relato |
|---|---|---|---|---|---|---|---|---|
| U01 | representativo | — | S1 | Marcelo Sánchez | plataforma=android | Se va sin intentar contactar | 8,3 % | Tiene una consultora chica en la Araucanía. Un colega le pasó el link por WhatsApp y está mirando si le convendría vender sus asesorías en línea. |
| U02 | representativo | — | S2 | Luis Soto | canal_envio=whatsapp | Contacto sin fricción | 52,7 % | Vende artículos de pesca en Coquimbo y quiere su primera página. Ya lo decidió: escribe por WhatsApp desde el computador. |
| U03 | representativo | — | S2 | Claudia Álvarez | canal_envio=whatsapp | Se va sin intentar contactar | 6,9 % | Profesora jubilada que hace clases particulares en el Maule. Buscaba cuánto cuesta una página y se va desde la portada. |
| U04 | representativo | — | S3 | Ignacio Rojas | destino=articulo | Contacto sin fricción | 21,5 % | Socio de un estudio contable chico en el Biobío. Llega a una guía sobre planillas y escribe desde el formulario del artículo, que ya trae el servicio marcado. |
| U05 | representativo | — | S3 | Tomás Vásquez | destino=articulo | Se va sin intentar contactar | 21,5 % | Distribuye insumos de aseo y busca clientes nuevos. Lee un artículo y no escribe. |
| U06 | representativo | — | S1 | Cristóbal López | plataforma=android, ritmo=pega_rapido | Contacto sin fricción | 54,1 % | Tiene una ferretería en Coquimbo. Llega desde Instagram con el texto ya escrito en sus notas, lo pega y envía; esta vez el token alcanzó a llegar. |
| U07 | representativo | — | S4 | Claudia González | plataforma=ios_ipados, motor=webkit, canal_envio=whatsapp, destino=servicio | Se va sin intentar contactar | 22,7 % | Lleva una tienda de ropa en Santiago con pedidos por WhatsApp. Calcula un estimado de automatización y lo deja para después. |
| U08 | representativo | — | S5 | Valentina Díaz | movimiento=reducido | Se va sin intentar contactar | 6,9 % | Administra restaurantes en la Araucanía. Un asistente de IA le nombró a Volutus cuando preguntó por la Ley 21.719; se va desde la portada. Con movimiento reducido la nube queda quieta, sin problema (R13). |
| U09 | representativo | — | S3 | Gonzalo Castillo | destino=servicio | Se va sin intentar contactar | 10,8 % | Jefe comercial de una fábrica de envases. Un asistente le recomendó la página de prospección y se va sin buscar más. |
| U10 | representativo | — | S4 | Andrea Gutiérrez | plataforma=ios_ipados, motor=webkit, navegador_de_app=True, canal_envio=whatsapp, destino=servicio | Contacto sin fricción | 21,7 % | Dueña de una constructora en Antofagasta. Ve un post en Instagram, calcula la prospección desde el navegador de la app y escribe por WhatsApp. |
| U11 | representativo | — | S3 | Paula Tapia | canal_envio=whatsapp, destino=servicio | Se va sin intentar contactar | 22,7 % | Vende repuestos en Arica con el inventario en un cuaderno. Llega a sistemas de gestión y se va. |
| U12 | representativo | — | S1 | Constanza Sepúlveda | plataforma=android, canal_envio=whatsapp | Se va sin intentar contactar | 19,3 % | Hace tortas por encargo en el Maule. Escribe la dirección de memoria y se va desde la portada. |
| U13 | cobertura | 4,9e−07 | S6 | Jean-Pierre Hernández | plataforma=macos, motor=gecko, js=inactivo, movimiento=reducido, gpu=lenta, nombre=otros_signos, ritmo=pega_rapido, privacidad=estricta, destino=brief | Envía y no llega nada (silencio) | 0,0 % | Dueño de una cafetería en Santiago y cliente de Volutus. Navega con JavaScript apagado en Firefox. Llena el brief entero y la página le dice «Recibimos tu brief.», pero no llega nada (R21). |
| U14 | cobertura | 3,1e−07 | S6 | Taller 2 Ruedas | canal_envio=whatsapp, almacenamiento=bloqueado, gpu=sin_webgl, usuario=agente, nombre=otros_signos, privacidad=estricta, destino=brief | Se va por una fricción del código | 20,4 % | Un taller de bicicletas en Coquimbo. Quien llena el brief escribe el nombre del negocio en «Tu nombre». Lo llena en dos sesiones en un navegador sin almacenamiento y al volver no queda nada (R12). |
| U15 | cobertura | 5,5e−06 | S7 | Constanza D'Amico | plataforma=ios_ipados, motor=webkit, navegador_de_app=True, movimiento=reducido, gpu=sin_webgl, nombre=apostrofo, privacidad=estricta, destino=ley | Se va sin intentar contactar | 3,9 % | Transportista independiente de Santiago. Llega desde Instagram a la guía de la ley; su apellido lleva apóstrofo y su iPhone lo escribe `’`. |
| U16 | cobertura | 3,2e−07 | S7 | Fernanda O'Neill | plataforma=macos, motor=webkit, canal_envio=whatsapp, js=inactivo, almacenamiento=bloqueado, movimiento=reducido, gpu=lenta, nombre=apostrofo, ritmo=pega_rapido, destino=articulo | Se va sin intentar contactar | 2,3 % | Abogada independiente que lee con Safari y JavaScript apagado. Lee un artículo sobre datos y se va. |
| U17 | cobertura | 4,8e−04 | S7 | Héctor Díaz | plataforma=android, navegador_de_app=True, canal_envio=whatsapp, js=inactivo, almacenamiento=bloqueado, gpu=lenta, ritmo=pega_rapido, privacidad=estricta | Se va sin intentar contactar | 3,3 % | Dueño de una sanguchería en Antofagasta. Abre el link desde Facebook en un teléfono viejo y se va desde la portada. |
| U18 | cobertura | 7,7e−05 | S8 | Matías D'Etigny | plataforma=macos, movimiento=reducido, usuario=agente, nombre=apostrofo, destino=ley | Se va sin intentar contactar | 6,0 % | Encargado de una tienda en Antofagasta que usa un agente de IA en Chrome. Llega a `/ley21719` y se va. |
| U19 | cobertura | 5,9e−02 | S7 | Nicolás Araya | motor=gecko, almacenamiento=bloqueado, gpu=lenta, privacidad=estricta, destino=ley | Se va sin intentar contactar | 7,2 % | Kinesiólogo independiente en Coquimbo, con Firefox en modo estricto. Consulta la Ley 21.719 y se va. |
| U20 | cobertura | 9,8e−06 | S7 | Ma. Paz Sánchez | plataforma=android, motor=gecko, canal_envio=whatsapp, movimiento=reducido, gpu=sin_webgl, nombre=otros_signos, ritmo=pega_rapido, privacidad=estricta, destino=servicio | Se va sin intentar contactar | 7,9 % | Tiene un centro de estética en Santiago y firma «Ma. Paz». Llega a prospección y se va. |
| U21 | cobertura | 3,3e−06 | S7 | Jean-Baptiste Gutiérrez | plataforma=ios_ipados, motor=webkit, navegador_de_app=True, canal_envio=whatsapp, js=inactivo, almacenamiento=bloqueado, gpu=sin_webgl, nombre=otros_signos, ritmo=pega_rapido, destino=articulo | Se va por una fricción del código | 23,6 % | Emprendedor de 25 años con una tienda de accesorios. Viene de Instagram decidido a pedir una página. Sin JavaScript, el envío nativo le responde «Faltan datos o el correo no es válido…» por el guion de su nombre, y se va (R7, R1). |
| U22 | cobertura | 3,4e−05 | S7 | Tomás O'Brien | motor=gecko, js=inactivo, almacenamiento=bloqueado, nombre=apostrofo, privacidad=estricta, destino=articulo | Se va sin intentar contactar | 2,6 % | Ingeniero de una consultora pequeña, con Linux y JavaScript apagado. Un asistente le citó un artículo y se va. |
| U23 | cobertura | 3,5e−05 | S6 | Macarena Sepúlveda | plataforma=macos, gpu=sin_webgl, usuario=agente, ritmo=pega_rapido, destino=brief | Contacto sin fricción | 40,0 % | Pastelera independiente y clienta de Volutus. Usa un agente de IA para llenar el brief; esta vez lo envía con calma y llega con número de referencia. |
| U24 | cobertura | 1,3e−02 | S7 | Jean-Pierre Muñoz | plataforma=android, canal_envio=whatsapp, js=inactivo, nombre=otros_signos, ritmo=pega_rapido, destino=ley | Se va sin intentar contactar | 9,4 % | Nutricionista joven con consulta en Coquimbo. Le recomendaron la guía de la Ley 21.719 por WhatsApp; navega sin JavaScript. |
| U25 | cobertura | 3,5e−04 | S8 | Nicolás Torres | plataforma=macos, canal_envio=whatsapp, almacenamiento=bloqueado, gpu=lenta, usuario=agente, ritmo=pega_rapido, destino=servicio | Contacto sin fricción | 47,4 % | Vende productos importados en Antofagasta. Llega a desarrollo web listo para encargar su sitio y escribe por WhatsApp. |
| U26 | cobertura | 5,1e−04 | S6 | Rocío O'Ryan | plataforma=ios_ipados, motor=webkit, canal_envio=whatsapp, js=inactivo, nombre=apostrofo, destino=brief | Envía y no llega nada (silencio) | 0,0 % | Dueña de una picada en Santiago y clienta de Volutus. Llena el brief en su iPhone con JavaScript desactivado: «Recibimos tu brief.», y no llega nada (R21). |
| U27 | cobertura | 6,4e−03 | S3 | Marie-Ange Vásquez | plataforma=macos, motor=webkit, gpu=sin_webgl, nombre=otros_signos | Contacto después de una fricción | 7,0 % | Gerenta de una constructora pequeña; firma «Marie-Ange». El formulario le pide «Usa solo letras.»: cambia su nombre y envía (R1). |
| U28 | cobertura | 1,1e−02 | S1 | Claudio O'Brien | plataforma=android, motor=gecko, gpu=sin_webgl, nombre=apostrofo | Contacto sin fricción | 7,9 % | Arquitecto con oficina chica. En Android el apóstrofo es recto y pasa. Calcula el estimado y lo envía con el mensaje ya escrito (R14). |
| U29 | cobertura | 9,2e−05 | S7 | Claudia O'Neill | js=inactivo, gpu=lenta, nombre=apostrofo, ritmo=pega_rapido, destino=servicio | Se va sin intentar contactar | 4,3 % | Tiene una distribuidora de huevos en Santiago y usa Opera con JavaScript apagado. Mira automatización y se va. |
| U30 | cobertura | 3,3e−01 | S4 | Patricio Flores | plataforma=ios_ipados, motor=webkit, gpu=lenta | Se va sin intentar contactar | 8,3 % | Administra un bar en Santiago. Un asistente le habló de agentes de IA; calcula el estimado y lo deja para después. |
| U31 | cobertura | 8,2e−04 | S7 | Patricia D'Etigny | plataforma=android, canal_envio=whatsapp, js=inactivo, movimiento=reducido, nombre=apostrofo, destino=articulo | Se va sin intentar contactar | 2,3 % | Dueña de un restaurante en Valparaíso. Lee un artículo sobre datos con JavaScript apagado y no escribe. |
| U32 | cobertura | 6,2e−07 | S6 | Francisca O'Brien | plataforma=android, motor=gecko, canal_envio=whatsapp, almacenamiento=bloqueado, gpu=sin_webgl, nombre=apostrofo, ritmo=pega_rapido, privacidad=estricta, destino=brief | Se va sin intentar contactar | 48,0 % | Vende vinos de Ñuble y recibió el brief, pero no lo termina. |
| U33 | cobertura | 5,3e−05 | S8 | Ma. Paz Reyes | gpu=sin_webgl, usuario=agente, nombre=otros_signos, destino=articulo | Se va sin intentar contactar | 3,8 % | Psicóloga en el Biobío que prueba un agente de IA en Chrome. Lee una guía sobre agentes y no escribe. |
| U34 | cobertura | 6,6e−02 | S8 | Andrés Silva | usuario=agente, ritmo=pega_rapido | Se va sin intentar contactar | 16,7 % | Tiene una amasandería en el Maule y usa un agente de IA en Chrome. Mira prospección y no escribe. |

## Anexo B: trazas sorteadas

Cada paso separa la acción (sorteada), la consecuencia (la regla del código) y la percepción (las cuatro preguntas del recorrido cognitivo; «—» quiere decir que las cuatro dan «sí»).

#### U01 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,556 | 1 | llega a / |  | — |
| 2 | En / | 0,31 | 0,55 | se va sin buscar más |  | — |

#### U02 · Contacto sin fricción · P(camino) = 0,106

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,14 | 1 | llega a / |  | — |
| 2 | En / | 0,362 | 0,54 | va a /servicios/desarrollo-web |  | — |
| 3 | En /servicios/desarrollo-web | 0,916 | 0,55 | lee la página sin calcular |  | — |
| 4 | ¿Escribe? | 0,828 | 0,42 | baja al formulario |  | — |
| 5 | Formulario | 0,787 | 1 | elige WhatsApp y escribe |  | — |
| 6 | Validación del nombre | 0,931 | 1 | el nombre pasa |  | — |
| 7 | WhatsApp | 0,414 | 0,85 | se abre WhatsApp con el mensaje escrito y lo envía |  | — |

#### U03 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,236 | 1 | llega a / |  | — |
| 2 | En / | 0,236 | 0,55 | se va sin buscar más |  | — |

#### U04 · Contacto sin fricción · P(camino) = 0,134

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,991 | 1 | llega a un artículo |  | — |
| 2 | En un artículo | 0,757 | 0,455 | termina el artículo |  | — |
| 3 | ¿Escribe? | 0,824 | 0,3 | va al formulario |  | — |
| 4 | Formulario | 0,785 | 1 | elige correo y escribe |  | — |
| 5 | Validación del nombre | 0,99 | 1 | el nombre pasa |  | — |
| 6 | Envío por correo | 0,018 | 0,983 | envía: «¡Gracias por escribirnos!» |  | — |

#### U05 · Se va sin intentar contactar · P(camino) = 0,318

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,596 | 1 | llega a un artículo |  | — |
| 2 | En un artículo | 0,893 | 0,455 | termina el artículo |  | — |
| 3 | ¿Escribe? | 0,049 | 0,7 | decide no escribir por ahora |  | — |

#### U06 · Contacto sin fricción · P(camino) = 0,163

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,688 | 1 | llega a / |  | — |
| 2 | En / | 0,923 | 0,36 | sigue en la portada |  | — |
| 3 | ¿Escribe? | 0,768 | 0,7 | va al formulario |  | — |
| 4 | Formulario de la portada | 0,941 | 1 | elige correo y escribe |  | — |
| 5 | Validación del nombre | 0,046 | 1 | el nombre pasa |  | — |
| 6 | Envío por correo | 0,479 | 0,645 | envía: «¡Gracias por escribirnos!» |  | — |

#### U07 · Se va sin intentar contactar · P(camino) = 0,133

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,395 | 1 | llega a /servicios/automatizacion-procesos |  | — |
| 2 | En /servicios/automatizacion-procesos | 0,405 | 0,292 | calcula un estimado |  | — |
| 3 | Estimado | 0,894 | 0,65 | mira el precio y sigue leyendo |  | — |
| 4 | ¿Escribe? | 0,048 | 0,7 | decide no escribir por ahora |  | — |

#### U08 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,63 | 1 | llega a / |  | — |
| 2 | En / | 0,398 | 0,55 | se va sin buscar más |  | — |

#### U09 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,434 | 1 | llega a /servicios/prospeccion-de-clientes |  | — |
| 2 | En /servicios/prospeccion-de-clientes | 0,378 | 0,55 | se va sin buscar más |  | — |

#### U10 · Contacto sin fricción · P(camino) = 0,0436

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,622 | 1 | llega a /servicios/prospeccion-de-clientes |  | — |
| 2 | En /servicios/prospeccion-de-clientes | 0,638 | 0,292 | calcula un estimado |  | — |
| 3 | Estimado | 0,842 | 0,65 | mira el precio y sigue leyendo |  | — |
| 4 | ¿Escribe? | 0,707 | 0,3 | va al formulario |  | — |
| 5 | Formulario | 0,702 | 1 | elige WhatsApp y escribe |  | — |
| 6 | Validación del nombre | 0,601 | 1 | el nombre pasa |  | — |
| 7 | WhatsApp | 0,68 | 0,765 | se abre WhatsApp con el mensaje escrito y lo envía |  | — |

#### U11 · Se va sin intentar contactar · P(camino) = 0,35

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,659 | 1 | llega a /servicios/sistemas-de-gestion |  | — |
| 2 | En /servicios/sistemas-de-gestion | 0,268 | 0,35 | se va sin buscar más |  | — |

#### U12 · Se va sin intentar contactar · P(camino) = 0,35

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,766 | 1 | llega a / |  | — |
| 2 | En / | 0,294 | 0,35 | se va sin buscar más |  | — |

#### U13 · Envía y no llega nada (silencio) · P(camino) = 0,8

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,922 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,777 | 0,8 | completa el brief y llega a la revisión |  | — |
| 3 | Validación del nombre | 0,867 | 1 | sin brief.js no hay validación en el navegador |  | — |
| 4 | Envío del brief | 0,467 | 1 | POST nativo con «transcurrido» vacío: «Recibimos tu brief.» y no llega nada ↳ *La página dice «Recibimos tu brief.» y no llegó nada.* | R21: `src/paginas/Brief.jsx:326`, `src/comportamiento/brief/brief.js:640` | sí/sí/sí/no |

#### U14 · Se va por una fricción del código · P(camino) = 0,4

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,549 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,087 | 0,4 | lo llena en dos sesiones y al volver no hay nada guardado ↳ *Avisó que no puede guardar («No cierres la página hasta enviar»).* | R12: `src/lib/almacen.js:1-3`, `src/comportamiento/brief/brief.js:163-166` | — |

#### U15 · Se va sin intentar contactar · P(camino) = 0,243

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,213 | 1 | llega a /ley21719 |  | — |
| 2 | En /ley21719 | 0,838 | 0,27 | lee la guía sin calcular |  | — |
| 3 | ¿Escribe? | 0,194 | 0,9 | decide no escribir por ahora |  | — |

#### U16 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,252 | 1 | llega a un artículo |  | — |
| 2 | En un artículo | 0,349 | 0,55 | se va sin buscar más |  | — |

#### U17 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,542 | 1 | llega a / |  | — |
| 2 | En / | 0,533 | 0,55 | se va sin buscar más |  | — |

#### U18 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,171 | 1 | llega a /ley21719 |  | — |
| 2 | En /ley21719 | 0,02 | 0,55 | se va sin buscar más |  | — |

#### U19 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,537 | 1 | llega a /ley21719 |  | — |
| 2 | En /ley21719 | 0,458 | 0,55 | se va sin buscar más |  | — |

#### U20 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,351 | 1 | llega a /servicios/prospeccion-de-clientes |  | — |
| 2 | En /servicios/prospeccion-de-clientes | 0,227 | 0,55 | se va sin buscar más |  | — |

#### U21 · Se va por una fricción del código · P(camino) = 0,0374

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,169 | 1 | llega a un artículo |  | — |
| 2 | En un artículo | 0,223 | 0,27 | va a /servicios/desarrollo-web |  | — |
| 3 | En /servicios/desarrollo-web | 0,487 | 0,55 | lee la página sin calcular |  | — |
| 4 | ¿Escribe? | 0,896 | 0,42 | baja al formulario |  | — |
| 5 | Formulario | 0,218 | 1 | envía sin JavaScript: POST nativo ↳ *La página de respuesta trae el correo como texto, sin enlace, y lo escrito se pierde al salir.* | R7: `src/components/Contacto.jsx:23-25`, `worker/index.js:34-40` | sí/sí/sí/no |
| 6 | Respuesta sin JavaScript | 0,756 | 0,6 | página «Faltan datos o el correo no es válido…»: se va ↳ *La página de respuesta trae el correo como texto, sin enlace, y lo escrito se pierde al salir.* | R7: `src/components/Contacto.jsx:23-25`, `worker/index.js:34-40` | sí/sí/sí/no |

#### U22 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,271 | 1 | llega a un artículo |  | — |
| 2 | En un artículo | 0,529 | 0,55 | se va sin buscar más |  | — |

#### U23 · Contacto sin fricción · P(camino) = 0,378

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,144 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,375 | 0,8 | completa el brief y llega a la revisión |  | — |
| 3 | Validación del nombre | 0,76 | 1 | el nombre pasa |  | — |
| 4 | Envío del brief | 0,901 | 0,473 | envía: «Tu número de referencia es B-…» |  | — |

#### U24 · Se va sin intentar contactar · P(camino) = 0,273

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,316 | 1 | llega a /ley21719 |  | — |
| 2 | En /ley21719 | 0,811 | 0,39 | lee la guía sin calcular |  | — |
| 3 | ¿Escribe? | 0,506 | 0,7 | decide no escribir por ahora |  | — |

#### U25 · Contacto sin fricción · P(camino) = 0,177

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,029 | 1 | llega a /servicios/desarrollo-web |  | — |
| 2 | En /servicios/desarrollo-web | 0,717 | 0,495 | lee la página sin calcular |  | — |
| 3 | ¿Escribe? | 0,759 | 0,42 | baja al formulario |  | — |
| 4 | Formulario | 0,109 | 1 | elige WhatsApp y escribe |  | — |
| 5 | Validación del nombre | 0,503 | 1 | el nombre pasa |  | — |
| 6 | WhatsApp | 0,198 | 0,85 | se abre WhatsApp con el mensaje escrito y lo envía |  | — |

#### U26 · Envía y no llega nada (silencio) · P(camino) = 0,8

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,004 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,042 | 0,8 | completa el brief y llega a la revisión |  | — |
| 3 | Validación del nombre | 0,649 | 1 | sin brief.js no hay validación en el navegador |  | — |
| 4 | Envío del brief | 0,878 | 1 | POST nativo con «transcurrido» vacío: «Recibimos tu brief.» y no llega nada ↳ *La página dice «Recibimos tu brief.» y no llegó nada.* | R21: `src/paginas/Brief.jsx:326`, `src/comportamiento/brief/brief.js:640` | sí/sí/sí/no |

#### U27 · Contacto después de una fricción · P(camino) = 0,0066

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,221 | 1 | llega a / |  | — |
| 2 | En / | 0,701 | 0,27 | va a /servicios/prospeccion-de-clientes |  | — |
| 3 | En /servicios/prospeccion-de-clientes | 0,018 | 0,45 | calcula un estimado |  | — |
| 4 | Estimado | 0,469 | 0,65 | mira el precio y sigue leyendo |  | — |
| 5 | ¿Escribe? | 0,976 | 0,1 | va al formulario |  | — |
| 6 | Formulario | 0,258 | 1 | elige correo y escribe |  | — |
| 7 | Validación del nombre | 0,075 | 0,85 | «Usa solo letras.»: reescribe el nombre ↳ *El aviso dice qué hacer, pero le pide escribir su nombre (o el de su negocio) de otra forma.* | R1: `src/lib/contacto.js:89-91`, `src/client.js:82-85` | sí/sí/sí/en parte |
| 8 | Envío por correo | 0,542 | 0,983 | envía: «¡Gracias por escribirnos!» |  | — |

#### U28 · Contacto sin fricción · P(camino) = 0,0418

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,251 | 1 | llega a / |  | — |
| 2 | En / | 0,654 | 0,27 | va a /servicios/desarrollo-web |  | — |
| 3 | En /servicios/desarrollo-web | 0,35 | 0,45 | calcula un estimado |  | — |
| 4 | Estimado | 0,3 | 0,35 | pulsa «Pedir esta cotización»: el mensaje llega escrito | R14: `src/comportamiento/estimado.js:61-72` | — |
| 5 | Formulario | 0,391 | 1 | elige correo y escribe |  | — |
| 6 | Validación del nombre | 0,068 | 1 | el nombre pasa |  | — |
| 7 | Envío por correo | 0,681 | 0,983 | envía: «¡Gracias por escribirnos!» |  | — |

#### U29 · Se va sin intentar contactar · P(camino) = 0,55

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,213 | 1 | llega a /servicios/automatizacion-procesos |  | — |
| 2 | En /servicios/automatizacion-procesos | 0,548 | 0,55 | se va sin buscar más |  | — |

#### U30 · Se va sin intentar contactar · P(camino) = 0,0711

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,175 | 1 | llega a / |  | — |
| 2 | En / | 0,756 | 0,27 | va a /servicios/agentes-ia |  | — |
| 3 | En /servicios/agentes-ia | 0,088 | 0,45 | calcula un estimado |  | — |
| 4 | Estimado | 0,401 | 0,65 | mira el precio y sigue leyendo |  | — |
| 5 | ¿Escribe? | 0,215 | 0,9 | decide no escribir por ahora |  | — |

#### U31 · Se va sin intentar contactar · P(camino) = 0,283

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,548 | 1 | llega a un artículo |  | — |
| 2 | En un artículo | 0,775 | 0,315 | termina el artículo |  | — |
| 3 | ¿Escribe? | 0,179 | 0,9 | decide no escribir por ahora |  | — |

#### U32 · Se va sin intentar contactar · P(camino) = 0,12

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,315 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,9 | 0,12 | no lo termina |  | — |

#### U33 · Se va sin intentar contactar · P(camino) = 0,283

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,554 | 1 | llega a un artículo |  | — |
| 2 | En un artículo | 0,712 | 0,315 | termina el artículo |  | — |
| 3 | ¿Escribe? | 0,19 | 0,9 | decide no escribir por ahora |  | — |

#### U34 · Se va sin intentar contactar · P(camino) = 0,15

| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,025 | 1 | llega a / |  | — |
| 2 | En / | 0,64 | 0,39 | va a /servicios/prospeccion-de-clientes |  | — |
| 3 | En /servicios/prospeccion-de-clientes | 0,644 | 0,55 | lee la página sin calcular |  | — |
| 4 | ¿Escribe? | 0,139 | 0,7 | decide no escribir por ahora |  | — |

## Anexo C: trazas forzadas

Por cada arco que las trazas sorteadas no recorrieron, el camino más probable que pasa por él (F15).

| Arco que faltaba | Usuario | P(camino) | Desenlace | Camino |
|---|---|---|---|---|
| brief_envio: el agente lo llena y la persona envía antes de 8 s: «Recibimos tu brief.» y no llega nada | U23 | 0,4 | Envía y no llega nada (silencio) | completa el brief y llega a la revisión → el nombre pasa → el agente lo llena y la persona envía antes de 8 s: «Recibimos tu brief.» y no llega nada |
| brief_envio: falla el envío; copia sus respuestas y las manda por correo | U32 | 0,024 | Escribe al correo tras un error | completa el brief y llega a la revisión → el nombre pasa → falla el envío; copia sus respuestas y las manda por correo |
| brief_envio: falla el envío; sus respuestas siguen guardadas y reintenta | U32 | 0,14 | Contacto después de una fricción | completa el brief y llega a la revisión → el nombre pasa → falla el envío; sus respuestas siguen guardadas y reintenta |
| brief_prospecto: llena lo obligatorio y llega a la revisión | U02 | 0,035 | Contacto sin fricción | va a /servicios/desarrollo-web → lee la página sin calcular → pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief → llena lo obligatorio y llega a la revisión → el nombre pasa → envía: «Tu número de referencia es B-…» |
| brief_prospecto: ve «35 a 45 min» y lo deja para después | U25 | 0,05 | Se va por una fricción del código | lee la página sin calcular → pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief → ve «35 a 45 min» y lo deja para después |
| brief_prospecto: ve «35 a 45 min», vuelve y usa el formulario | U25 | 0,023 | Contacto después de una fricción | lee la página sin calcular → pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief → ve «35 a 45 min», vuelve y usa el formulario → elige WhatsApp y escribe → el nombre pasa → se abre WhatsApp con el mensaje escrito y lo envía |
| decide: pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief | U25 | 0,05 | Se va por una fricción del código | lee la página sin calcular → pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief → ve «35 a 45 min» y lo deja para después |
| decide: pulsa «Cuéntanos tu proyecto»: va al formulario de la portada | U24 | 0,07 | Se va por una fricción del código | lee la guía sin calcular → pulsa «Cuéntanos tu proyecto»: va al formulario de la portada → envía sin JavaScript: POST nativo → página «Faltan datos o el correo no es válido…»: se va |
| envio_correo: Resend no responde: 502 | U06 | 0,00021 | Se va por una fricción del código | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → Resend no responde: 502 → cree que el sitio falla y se va |
| envio_correo: Turnstile no pasa: 403 «No pudimos enviar tu mensaje…» | U19 | 0,0068 | Se va por una fricción del código | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → elige correo y escribe → el nombre pasa → Turnstile no pasa: 403 «No pudimos enviar tu mensaje…» → cree que el sitio falla y se va |
| envio_correo: envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» | U06 | 0,043 | Se va por una fricción del código | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» → cree que el sitio falla y se va |
| estimado: pulsa «Pedir esta cotización»: va a la portada | U24 | 0,041 | Se va por una fricción del código | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → envía sin JavaScript: POST nativo → página «Faltan datos o el correo no es válido…»: se va |
| form: el agente rellena el formulario y la persona lo revisa | U34 | 0,031 | Contacto sin fricción | sigue en la portada → va al formulario → el agente rellena el formulario y la persona lo revisa → el nombre pasa → envía: «¡Gracias por escribirnos!» |
| ley_a_portada: escribe de nuevo lo que necesita | U24 | 0,041 | Se va por una fricción del código | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → envía sin JavaScript: POST nativo → página «Faltan datos o el correo no es válido…»: se va |
| ley_a_portada: llega a un formulario vacío, sin lo que marcó, y se va | U24 | 0,023 | Se va por una fricción del código | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → llega a un formulario vacío, sin lo que marcó, y se va |
| nojs: página «Faltan datos o el correo no es válido…»: escribe desde su correo | U21 | 0,18 | Escribe al correo tras un error | termina el artículo → va al formulario → envía sin JavaScript: POST nativo → página «Faltan datos o el correo no es válido…»: escribe desde su correo |
| nojs: página «No pudimos enviar tu mensaje. Escríbenos directamente a…»: escribe desde su correo | U29 | 0,028 | Escribe al correo tras un error | calcula un estimado → pulsa «Pedir esta cotización»: el mensaje llega escrito → envía sin JavaScript: POST nativo → página «No pudimos enviar tu mensaje. Escríbenos directamente a…»: escribe desde su correo |
| nojs: página «No pudimos enviar tu mensaje. Escríbenos directamente a…»: se va | U29 | 0,043 | Se va por una fricción del código | calcula un estimado → pulsa «Pedir esta cotización»: el mensaje llega escrito → envía sin JavaScript: POST nativo → página «No pudimos enviar tu mensaje. Escríbenos directamente a…»: se va |
| pagina: calcula un estimado de la ley de datos | U24 | 0,12 | Se va sin intentar contactar | calcula un estimado de la ley de datos → mira el precio y sigue leyendo → decide no escribir por ahora |
| pagina: el agente usa «estimar_precio» y recibe el estimado | U25 | 0,12 | Contacto sin fricción | el agente usa «estimar_precio» y recibe el estimado → pulsa «Pedir esta cotización»: el mensaje llega escrito → elige WhatsApp y escribe → el nombre pasa → se abre WhatsApp con el mensaje escrito y lo envía |
| pagina: va a /ley21719 | U08 | 0,15 | Se va sin intentar contactar | va a /ley21719 → lee la guía sin calcular → decide no escribir por ahora |
| tras_error: cierra el aviso y vuelve a enviar | U06 | 0,021 | Contacto después de una fricción | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» → cierra el aviso y vuelve a enviar → envía: «¡Gracias por escribirnos!» |
| tras_error: copia el correo del aviso y escribe desde su correo | U06 | 0,023 | Escribe al correo tras un error | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» → copia el correo del aviso y escribe desde su correo |
| tras_error: cree que el sitio falla y se va | U06 | 0,043 | Se va por una fricción del código | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» → cree que el sitio falla y se va |
| validar_nombre: «Usa solo letras.» sobre su nombre bien escrito: se rinde | U15 | 0,021 | Se va por una fricción del código | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → elige correo y escribe → «Usa solo letras.» sobre su nombre bien escrito: se rinde |
| validar_nombre: «Usa solo letras.»: no sabe cómo escribirlo y se va | U14 | 0,072 | Se va por una fricción del código | completa el brief y llega a la revisión → «Usa solo letras.»: no sabe cómo escribirlo y se va |
| validar_nombre: «Usa solo letras.»: quita el apóstrofo y sigue | U15 | 0,018 | Contacto después de una fricción | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → elige correo y escribe → «Usa solo letras.»: quita el apóstrofo y sigue → envía: «¡Gracias por escribirnos!» |
| whatsapp: WhatsApp no abre desde la app: cambia a correo | U10 | 0,0053 | Contacto después de una fricción | lee la página sin calcular → va al formulario → elige WhatsApp y escribe → el nombre pasa → WhatsApp no abre desde la app: cambia a correo → envía: «¡Gracias por escribirnos!» |
| whatsapp: WhatsApp no abre desde la app: se va | U10 | 0,0054 | Se va por una fricción del código | lee la página sin calcular → va al formulario → elige WhatsApp y escribe → el nombre pasa → WhatsApp no abre desde la app: se va |
| whatsapp: se abre WhatsApp pero no lo envía | U02 | 0,038 | Abre WhatsApp y no envía | sigue en la portada → va al formulario → elige WhatsApp y escribe → el nombre pasa → se abre WhatsApp pero no lo envía |
