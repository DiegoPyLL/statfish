# Recorrido del código: VolutusLandingPage

Primer paso del caso de prueba de Statfish ([viabilidad](../viabilidad.md)). Un solo agente recorre el código de la
landing de Volutus y deja un mapa de **lo que el código hace posible**: superficies, entradas, reglas del servidor y
del entorno, y estados de error. Cada afirmación lleva su `archivo:línea`. Lo que el código no dice (quién llega, con
qué intención) queda para los priors del [modelo](modelo.md).

| | |
|---|---|
| Repositorio | `VolutusDevelopment/VolutusLandingPage`, rama `main`, commit `76b713a`, sin cambios locales |
| Fecha | 2026-11-20 |
| Pregunta de la corrida | ¿Qué usuarios no logran cotizar ni contactar a Volutus, en qué paso y por qué? ¿Qué entornos técnicos rompen la experiencia? |
| Regla del recorrido | Primero el índice (rutas, formularios, endpoints, límites) y después la lectura dirigida. Sin evidencia no hay hallazgo. |
| Cambios en el repo | Ninguno: solo lectura (`git status` igual antes y después) |

Las rutas de este documento son relativas a la raíz de ese repositorio.

## Bitácora

| Paso | Qué se leyó | Líneas | Bytes |
|---|---|---|---|
| Contexto | `README.md`, `CLAUDE.md`, la nota del vault `1. Projects/LandingPage/LandingPage.md`, el issue #40 y el informe de 100.000 perfiles del commit `87e3c0d` | ≈ 1.000 | ≈ 58 KB |
| Índice | `src/lib/meta.js`, `src/paginas/rutas.js`, `public/robots.txt` | 656 | |
| Formularios | `src/components/Contacto.jsx`, `src/lib/contacto.js`, `src/lib/servicios.js`, `src/client.js`, `src/components/Estimado.jsx`, `src/comportamiento/estimado.js`, `src/lib/precios.js`, `src/data/uf.js` | 1.555 | |
| Servidor | `worker/index.js`, `worker/comun.js`, `worker/brief.js`, `wrangler.jsonc` | 822 | |
| Entorno | `src/lib/turnstile.js`, `src/lib/seguridad.js`, `src/lib/almacen.js`, `src/lib/movimiento.js`, `src/lib/campos.js`, `src/comportamiento/chat.js`, `src/comportamiento/copiar.js` | 266 | |
| Lectura parcial | `src/comportamiento/brief/brief.js` (462 de 781 líneas), `src/lib/brief/reglas.js`, `src/paginas/Brief.jsx`, `src/paginas/Ley21719.jsx`, `src/paginas/Servicio.jsx`, `src/data/paginas-de-servicio.js`, `src/comportamiento/nubes.js` | ≈ 844 | 34,8 KB |
| Búsquedas | `grep` de enlaces a `/brief-web`, de `<Contacto`/`<Estimado`, de `toolname`, de `origin-trial` y de `transcurrido` | — | — |
| **Total** | Lectura completa: 3.239 líneas de código (142,8 KB) | ≈ 5.100 | **≈ 235 KB ≈ 65 a 70 mil tokens** |

El código de `src/`, `worker/` y `scripts/` suma 52.872 líneas y 2,15 MB, así que la lectura dirigida cubrió cerca del 11 %
de los bytes. El resto son las escenas del juego, los estilos y los datos de bocetos y artículos, que no tocan la
pregunta de la corrida. Esta medida alimenta el [análisis de costos](../viabilidad.md#costos).

## Mapa del código

### Superficies

Todas las páginas salen de `PAGINAS` (`src/lib/meta.js:39-479`), y cada una tiene su componente en `COMPONENTES`
(`src/paginas/rutas.js:39-84`). Las que importan para la pregunta:

| Superficie | Qué tiene | Evidencia |
|---|---|---|
| `/` (portada) | Formulario de contacto **sin servicio marcado** | `src/paginas/Inicio.jsx:33` |
| `/servicios/*` (7 páginas) | Un solo marco: estimado + formulario con el servicio **ya marcado** | `src/paginas/Servicio.jsx:72-74`, `src/paginas/Servicio.jsx:102` |
| `/servicios/desarrollo-web` | Su «Cuéntanos tu proyecto» de la cabecera va a `/brief-web`; el de las demás, a `#contacto` | `src/data/paginas-de-servicio.js:66`, `src/paginas/Servicio.jsx:89` |
| `/ley21719` | Es la página del servicio «Ley de datos»: tiene estimado, pero **no formulario**; sus dos llamados van a `/#contacto` | `src/paginas/Ley21719.jsx:264`, `src/paginas/Ley21719.jsx:429` |
| Artículos (13 guías, 1 opinión) | Formulario con el servicio del artículo marcado | `src/components/Articulo.jsx:48` |
| `/brief-web` | Brief de 9 partes (35 a 45 min), con 2 obligatorios; `noindex` | `src/lib/meta.js:301-310`, `src/lib/brief/preguntas.js:89-93` |
| `/404`, `/500`, `/patos`, Operación Venganza, `/nosotros`, `/privacidad` | Fuera de la pregunta de esta corrida | `src/lib/meta.js:288-478` |

Una inconsistencia de documentación: `src/paginas/Brief.jsx:10-12` dice que el brief «No se enlaza desde el sitio», pero
la página de desarrollo web lo enlaza (`src/data/paginas-de-servicio.js:66`) y así lo cuentan `src/lib/meta.js:301-302`
y el README.

### Entradas

| Formulario | Campos y reglas | WebMCP | Evidencia |
|---|---|---|---|
| Contacto (`POST /api/contacto`) | «Enviar por» correo o WhatsApp; nombre (60), correo (100, opcional por WhatsApp), servicios (opcional), mensaje (2.000); trampa `hp_campo`; Turnstile | `escribir_a_volutus`, sin `toolautosubmit`: la persona envía | `src/components/Contacto.jsx:76-223`, `src/lib/contacto.js:83-91` |
| Estimado | Base, extras, urgencia, cuotas y mantención; se calcula en el navegador; «Pedir esta cotización» escribe lo marcado en el mensaje **si el formulario está en la misma página** | `estimar_precio`, con `toolautosubmit` y `respondWith` | `src/components/Estimado.jsx:48`, `src/components/Estimado.jsx:60-67`, `src/comportamiento/estimado.js:61-86` |
| Brief (`POST /api/brief`) | ≈ 85 preguntas en pantallas por ancla; solo nombre y un contacto; se guarda en el navegador; campos ocultos de envío (`transcurrido`, `pantalla`, `zona`…) | `enviar_brief`, sin `toolautosubmit` | `src/paginas/Brief.jsx:176-184`, `src/paginas/Brief.jsx:322-326`, `src/comportamiento/brief/brief.js:158-176` |

Reglas de validación compartidas por el navegador y el Worker (`src/lib/contacto.js:6-8`):

- **Nombre:** `/^[\p{L}\p{M}' ]+$/u`, solo letras, marcas, espacio y apóstrofo recto (`src/lib/contacto.js:89-91`). El
  comentario pone de ejemplo «O'Higgins».
- **Correo:** sin espacios ni separadores (`src/lib/contacto.js:85-87`).
- **Teléfono del brief:** `/^\+?[\d\s()-]{8,20}$/` (`src/lib/brief/reglas.js:30-32`).

### Servidor

Los dos endpoints recorren el mismo camino, en este orden (`worker/comun.js:3-8`):

1. Método.
2. Mismo origen: `worker/comun.js:76-80`.
3. Límite por IP, que se pregunta antes de leer: `worker/comun.js:90-99`.
4. Tamaño y tipo: `worker/comun.js:107-116`.
5. Trampa.
6. Validación.
7. Turnstile: `worker/comun.js:130-152`.
8. Resend: `worker/comun.js:163-192`.

| | Contacto | Brief |
|---|---|---|
| Límite | 5 por minuto e IP (`wrangler.jsonc:36-41`) | 2 por minuto e IP (`wrangler.jsonc:46-50`) |
| Trampa | 200 «Mensaje enviado…» sin enviar nada (`worker/index.js:83-85`) | 200 «Recibimos tu brief.» sin enviar nada (`worker/brief.js:280-285`) |
| Apuro | — | `transcurrido < 8000` ms: el mismo silencio (`worker/brief.js:282-285`, `src/lib/brief/reglas.js:38-40`) |
| Sin token de Turnstile | 403 «No pudimos enviar tu mensaje. Escríbenos directamente a…» (`worker/index.js:103-105`) | 403 «No pudimos enviar tu brief…» (`worker/brief.js:296-298`) |
| Respuesta | JSON con JS; página HTML sin JS (`worker/comun.js:48-56`) | Igual |

### Entorno

| Condición | Qué hace el código | Evidencia |
|---|---|---|
| Turnstile | El script se descarga **al primer foco** dentro del formulario y el widget se monta al cargar. El envío **no espera** el token. El token dura 300 s y se renueva solo (`refresh-expired: auto` por defecto en Cloudflare). | `src/lib/turnstile.js:27-53`, `src/client.js:191-245` |
| Sin JavaScript | Contacto: POST nativo sin token, 403 en una página aparte. Brief: POST nativo con `transcurrido` vacío, que el Worker toma por 0 ms. | `src/components/Contacto.jsx:23-25`, `worker/index.js:34-40`, `src/paginas/Brief.jsx:326` |
| `brief.js` no carga | Se baja con `import()` solo en su página; si falla, el formulario queda nativo | `src/client.js:299-302` |
| Sin almacenamiento | Todo acceso va envuelto; el brief avisa «No cierres la página hasta enviar» | `src/lib/almacen.js:1-3`, `src/comportamiento/brief/brief.js:163-166` |
| Sin GPU, sin WebGL o con movimiento reducido | Escena quieta o en video; «la página sigue entera» | `src/comportamiento/nubes.js:44-59`, `src/lib/movimiento.js:7` |
| iPhone y iPad | WebKit en todo navegador; el teclado convierte `'` en `’` (Smart Punctuation, activo por defecto). El campo nombre no lo evita. | `src/components/Contacto.jsx:121-130` |
| WhatsApp | `window.open` a `wa.me` con el texto armado, antes de cualquier `await` (por Safari) | `src/client.js:202-214`, `src/lib/contacto.js:39-44` |
| Agentes de IA (WebMCP) | Anotaciones declarativas en los tres formularios. **El sitio no declara token de origin trial**: en Chrome estable solo responde a quien activa el flag de pruebas. | `src/components/Contacto.jsx:40-43`, `grep origin-trial` vacío |
| Idioma | Solo `es-CL` | `index.html:2` |

### Contenido que el código expone

Hay 8 servicios en orden de necesidad (`src/lib/servicios.js:29-144`), que son las opciones del formulario más «Otro…»
(`src/lib/servicios.js:157-160`). Cada uno tiene su estimado en UF (`src/lib/precios.js:52-150`) con la UF del día
(`src/data/uf.js:2`). La Ley 21.719 rige desde el 1 de diciembre de 2026 (`src/lib/meta.js:216`, `src/paginas/Ley21719.jsx:33`).
Estos datos dan el **soporte** de las variables de intención. Sus pesos los da el [modelo](modelo.md).

## Reglas derivadas

Son las consecuencias que el modelo aplica en cada paso del flujo. «Fricción» quiere decir que la regla puede hacer perder
o demorar un contacto.

| Regla | Qué pasa | Evidencia | ¿Fricción? |
|---|---|---|---|
| R1 | El nombre rechaza guion, punto, dígitos y &: «Usa solo letras.» | `src/lib/contacto.js:89-91`, `src/client.js:82-85`, `worker/index.js:99-101`, `src/comportamiento/brief/brief.js:350`, `worker/brief.js:292-294` | Sí |
| R1+R2 | En iPhone y iPad el apóstrofo llega como `’` y la regla lo rechaza, aunque su comentario quiere aceptar «O'Higgins» | `src/lib/contacto.js:89-91`, `src/components/Contacto.jsx:121-130` | Sí |
| R4 | Envío antes de que llegue el token de Turnstile: 403 con un aviso que manda a escribir al correo, sin sugerir reintentar | `src/lib/turnstile.js:53`, `src/client.js:191-245`, `worker/comun.js:137` | Sí |
| R4b | Turnstile no se resuelve con privacidad estricta: 403 | `worker/comun.js:130-152` | Sí |
| R5 | Resend no responde: 502 con el correo directo | `worker/index.js:121-123` | Sí |
| R6 | WhatsApp con `window.open`; en el navegador de una app puede no abrir (por confirmar en un dispositivo real) | `src/client.js:202-214` | Sí |
| R7 | Sin JS, el contacto se rechaza y la página de respuesta trae el correo como texto, sin enlace | `worker/comun.js:32-46`, `worker/index.js:34-40` | Sí |
| R8 | En `/ley21719`, «Pedir esta cotización» lleva a `/#contacto`: el mensaje llega vacío y sin el servicio marcado | `src/paginas/Ley21719.jsx:429`, `src/components/Estimado.jsx:48`, `src/components/Estimado.jsx:204-207`, `src/paginas/Inicio.jsx:33` | Sí |
| R8b | Desde `/ley21719`, «Cuéntanos tu proyecto» llega al formulario de la portada sin el servicio marcado (campo opcional) | `src/paginas/Ley21719.jsx:264`, `src/components/Contacto.jsx:159-178` | No |
| R9 | En desarrollo web, el mismo «Cuéntanos tu proyecto» abre el brief de 35 a 45 min en la cabecera y el formulario en la barra | `src/data/paginas-de-servicio.js:66`, `src/paginas/Servicio.jsx:89`, `src/components/Barra.jsx:158` | Sí, si se abandona o se vuelve |
| R10 | Brief enviado antes de 8 s (un agente que lo llena de una vez): 200 «Recibimos tu brief.», no llega nada y se borra lo guardado | `src/lib/brief/reglas.js:38-40`, `worker/brief.js:280-285`, `src/comportamiento/brief/brief.js:669-680` | Sí |
| R11 | En el brief, Turnstile se monta al llegar a la revisión; si falla, las respuestas siguen guardadas y se puede reintentar o copiar | `src/comportamiento/brief/brief.js:408`, `src/comportamiento/brief/brief.js:681-684` | Sí (con buena salida) |
| R12 | Sin almacenamiento, el brief no se guarda (y lo avisa) | `src/comportamiento/brief/brief.js:163-166` | Sí, si se llena en dos veces |
| R13 | Sin GPU, sin WebGL o con movimiento reducido, la página sigue entera | `src/comportamiento/nubes.js:44-59` | No |
| R14 | El estimado escribe lo marcado en el mensaje del formulario de la misma página | `src/comportamiento/estimado.js:61-72` | No |
| R15 | Un agente WebMCP rellena el contacto y deja el foco en «Enviar mensaje» | `src/components/Contacto.jsx:40-43` | No |
| R16 | Un agente WebMCP recibe el estimado con `respondWith` | `src/comportamiento/estimado.js:78-86` | No |
| R17 | El brief guarda la hora de inicio con las respuestas: quien vuelve otro día no cae en los 8 s | `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | No |
| R21 | **Sin JS, o si `brief.js` no carga, el brief llega con `transcurrido` vacío: se descarta en silencio y la página dice «Recibimos tu brief.»** | `src/paginas/Brief.jsx:326`, `src/comportamiento/brief/brief.js:640`, `src/client.js:299-302`, `worker/brief.js:282-285`, `worker/brief.js:85` | Sí |

## Hipótesis que el código descartó

Revisar el código también sirve para no inventar fricciones:

- **«Quien retoma el brief otro día cae en el filtro de 8 s.»** No: `inicio` se guarda junto con las respuestas
  (`src/comportamiento/brief/brief.js:139`, `src/comportamiento/brief/brief.js:163`), así que el tiempo cuenta desde la
  primera visita.
- **«Un mensaje largo vence el token de Turnstile.»** No: el token dura 300 s y el widget lo renueva solo, porque el sitio
  no cambia `refresh-expired` (`src/lib/turnstile.js:42-50`).
- **«Sin GPU la portada se rompe.»** No: hay video o escena quieta, y la página sigue entera (`src/comportamiento/nubes.js:44-49`).
- **«El mensaje de 500 caracteres queda corto»** (issue #40). Ya está resuelto: el tope es 2.000 (`src/lib/contacto.js:83`).

## Lo que el código no dice

El código no dice quién llega ni cuántos, desde dónde, con qué urgencia ni qué le importa. Tampoco dice con qué
frecuencia ocurre cada entorno, por ejemplo cuántos llegan sin JS o con Smart Punctuation activo. El sitio declara que
no usa analítica, así que no hay datos reales para calibrar. Todo eso entra al [modelo](modelo.md) como anclas públicas
(StatCounter Chile, SII e INE) o como priors del LLM con rango, y se marca así en cada variable.
