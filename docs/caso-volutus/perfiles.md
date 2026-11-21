# Perfiles: los segmentos y su P(perfil)

Tercer paso del caso ([recorrido](recorrido.md) → [modelo](modelo.md) → perfiles →
[usuarios y flujos](usuarios-y-flujos.md) → [resultados](resultados.md)).

Un perfil es una **región de la red** del modelo, no un personaje. Los ocho de abajo dividen toda la población, sin
traslapes: cada usuario queda en el primero que le calza, en el orden S6, S8, S7, S5, S4, S1, S2, S3. Su masa,
P(perfil), sale de 120.000 usuarios sorteados de la red. El intervalo sale de 200 sorteos de los parámetros (p5–p95).
Las cifras **describen el modelo, no el mercado**.

## Resumen

| Perfil | Quién | P(perfil) p50 | p5–p95 | Contacto | Pérdida por código | Contacto con fricción |
|---|---|---|---|---|---|---|
| S1 | Celular o tablet Android | 36,6 % | 29,2 % – 45,5 % | 20,8 % | 1,02 % | 1,46 % |
| S2 | Escritorio, busca una página web | 9,0 % | 2,8 % – 16,4 % | 20,3 % | 1,94 % | 1,93 % |
| S3 | Escritorio, otros servicios | 24,0 % | 14,1 % – 31,4 % | 21,5 % | 0,49 % | 1,17 % |
| S4 | iPhone o iPad (WebKit, Smart Punctuation) | 9,9 % | 7,2 % – 14,4 % | 21,0 % | 1,09 % | 1,51 % |
| S5 | Negocio ante la Ley 21.719 | 9,1 % | 0,7 % – 22,5 % | 20,1 % | 1,88 % | 4,71 % |
| S6 | Cliente con el link del brief | 5,0 % | 0,9 % – 10,5 % | 77,8 % | 2,49 % | 7,89 % |
| S7 | Entorno restrictivo (sin JS, privacidad estricta o sin almacenamiento) | 6,4 % | 2,4 % – 11,4 % | 18,9 % | 3,09 % | 3,15 % |
| S8 | Agente de IA por WebMCP | 0,1 % | 0,0 % – 0,2 % | 19,7 % | 7,50 % | 8,26 % |

*Contacto* suma las tres vías: sin fricción, con fricción y al correo tras un error. *Pérdida por código* es lo que se va
por una fricción o se pierde en silencio. *Contacto con fricción* llega, pero después de un tropiezo del código.

La masa de S5 tiene el intervalo más ancho (0,7 % a 22,5 %): cuánta gente busca la ley de datos es el supuesto peor
anclado del modelo, y es donde más pesaría un dato real.

## Fichas

Cada ficha dice de dónde sale cada dato: **[código]** con su evidencia en el [recorrido](recorrido.md), **[ancla]**
pública o **[prior]** del LLM. Las fricciones se dan por cada 1.000 usuarios del perfil.

### S1 · Celular o tablet Android: 36,6 %

- **Quién [ancla + prior].**
  - Un 99 % llega desde el celular.
  - Llega por Google (27 %), por recomendación (24 %) o por redes (20 %).
  - Es micro (41 %), independiente (26 %) o pequeña empresa (24 %).
  - Busca una página web (27 %), una tienda (15 %) o un sistema de gestión (14 %).
- **Equipo [código + ancla].**
  - Chrome o Samsung Internet (Blink).
  - El 45 % envía por WhatsApp.
- **Recorrido probable [prior].**
  - Llega a la portada (52 %), a su servicio (26 %) o a un artículo (21 %).
  - La mitad está explorando.
- **Fricciones [código].**
  - R1: «Usa solo letras.» en nombres con guion, punto o de empresa. 7,6 llegan con fricción.
  - R9: la doble ruta de «Cuéntanos tu proyecto» en desarrollo web. 4,0 se pierden.
  - R4: envío antes del token de Turnstile, sobre todo quien pega su texto. 3,5 se pierden.
- **Resultado.** Contacta el 20,8 %; el código hace perder el 1,02 %.

### S2 · Escritorio, busca una página web: 9,0 %

- **Quién [prior].**
  - Busca una página web.
  - Es independiente (35 %) o micro (42 %).
  - Llega por Google (38 %), un artículo (17 %) o un asistente de IA (15 %).
- **Equipo [ancla].**
  - Windows con Chrome o Edge.
  - Envía por correo (80 %).
- **Recorrido probable.**
  - Llega a `/servicios/desarrollo-web`.
  - Ahí ve dos «Cuéntanos tu proyecto»: el de la cabecera abre un brief de 35 a 45 min y el de la barra, el formulario.
- **Fricciones [código].**
  - R9 es la mayor del modelo para un perfil grande: **15,0 se pierden** y 7,2 llegan después de volver.
  - R1: 8,4 llegan con fricción.
- **Resultado.** Contacta el 20,3 %; pierde el 1,94 %.

### S3 · Escritorio, otros servicios: 24,0 %

- **Quién [prior].**
  - Busca una tienda (21 %), un sistema de gestión (18 %) o una automatización (16 %).
  - Es más a menudo pyme.
- **Equipo [ancla].** Windows; envía por correo (80 %).
- **Recorrido probable.** Su página de servicio, con el formulario abajo y el servicio ya marcado (R14 si usa el estimado).
- **Fricciones [código].**
  - R1: 8,0 llegan con fricción y 1,5 se pierden.
  - R4: 2,7 se pierden.
- **Resultado.** Contacta el 21,5 %; pierde el 0,49 %. Es el perfil con menos fricción.

### S4 · iPhone o iPad: 9,9 %

- **Quién [ancla + prior].**
  - El 21 % de los celulares de Chile es iOS; un 4 % del perfil llega desde un iPad.
  - Si llega por redes, la mitad lo hace dentro del navegador de Instagram o Facebook.
- **Equipo [código].**
  - WebKit en todo navegador.
  - Smart Punctuation activo (95 %): `'` se escribe `’`.
  - iPads con Safari 18 que no actualizan (`CLAUDE.md:124`).
- **Fricciones [código].**
  - Las mismas que S1.
  - Se suma R1+R2: quien tiene apóstrofo en el nombre (O'Ryan, D'Alessandro) recibe «Usa solo letras.» sobre su nombre
    bien escrito. Es raro (0,4 % de los nombres), pero el aviso es **opaco**: no ve qué cambió.
  - R6, por confirmar: WhatsApp podría no abrir desde el navegador de una app.
- **Resultado.** Contacta el 21,0 %; pierde el 1,09 %.

### S5 · Negocio ante la Ley 21.719: 9,1 %

- **Quién [prior].**
  - Busca adaptarse a la ley de datos, que rige desde el 1 de diciembre de 2026: en 11 días.
  - Es pequeña (32 %) o micro (38 %).
- **Recorrido probable [código].**
  - Llega a la portada, a un artículo o a `/ley21719`, la página de su servicio.
  - Esa página tiene estimado y no tiene formulario.
  - Sus dos llamados van a `/#contacto` de la portada. «Pedir esta cotización» llega **sin lo marcado**, y el formulario,
    **sin el servicio** (R8, R8b). En los otros servicios, el mensaje llega escrito.
- **Fricciones [código].**
  - R8: **35,5 llegan con fricción y 13,5 se pierden**.
  - R1: 8,2.
- **Resultado.** Contacta el 20,1 % y pierde el 1,88 %, pero el **4,71 % llega con fricción**, el doble que cualquier
  perfil de prospectos.

### S6 · Cliente con el link del brief: 5,0 %

- **Quién [código + prior].**
  - Volutus le mandó `/brief-web`.
  - Ya decidió (etapa «listo»).
  - Escritorio (60 %), celular (30 %) o tablet (10 %).
- **Recorrido probable.** Llena el brief en partes; se guarda solo en el navegador (R17).
- **Fricciones [código].**
  - R11: carrera de Turnstile en la revisión, con buena salida. 50 llegan tras reintentar.
  - R1: 29 llegan tras corregir el nombre.
  - R12: sin almacenamiento, lo pierde si lo llena en dos veces. 11,5 se pierden.
  - **R21: sin JS, o si `brief.js` no carga, el envío se descarta en silencio y la página dice «Recibimos tu brief.».**
    6,9 de cada 1.000 clientes pierden el brief creyendo que llegó.
- **Resultado.** Contacta el 77,8 %; pierde el 2,49 %. Son clientes, así que cada pérdida pesa más que la de un prospecto.

### S7 · Entorno restrictivo: 6,4 %

- **Quién [prior].** Sin JS, con privacidad estricta (Firefox estricto, bloqueadores, modo bloqueo) o sin almacenamiento.
- **Fricciones [código].**
  - R4b: Turnstile no pasa. 11,7 se pierden.
  - R7: sin JS el contacto se rechaza y lo escrito se pierde. 8,9 se pierden.
  - R1: 7,6.
- **Resultado.** Contacta el 18,9 %; pierde el 3,09 %, el peor entre los prospectos humanos.

### S8 · Agente de IA por WebMCP: 0,1 %

- **Quién [código + prior].**
  - Un agente que rellena los formularios en Chrome o Edge de escritorio.
  - Sin token de origin trial, hoy solo existe donde alguien activó el flag de pruebas.
  - Es la cola por diseño: casi no tiene masa, pero es el usuario que el sitio quiere servir (`CLAUDE.md:135-145`).
- **Recorrido probable [código].**
  - `estimar_precio` funciona y responde (R16).
  - `escribir_a_volutus` rellena y deja el foco en «Enviar mensaje» (R15).
  - Turnstile recién se descarga entonces, con ese foco.
- **Fricciones [código].**
  - R4: si la persona envía enseguida, 403. **68 se pierden.**
  - R10: un brief enviado antes de 8 s se descarta en silencio.
- **Resultado.** Contacta el 19,7 %; pierde el 7,50 %.
