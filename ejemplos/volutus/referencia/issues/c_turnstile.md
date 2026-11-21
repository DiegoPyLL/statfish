Hallado en el caso de prueba de Statfish: recorrido del código de `main` @ `76b713a`, 20-11-2026, sin cambiar nada del repo. El detalle está en `docs/caso-volutus/` del repo `statfish`.

## Qué pasa

- Turnstile se descarga **al primer foco** dentro del formulario (`src/lib/turnstile.js:53`), y el widget se monta cuando termina de cargar el script (`src/lib/turnstile.js:27-51`).
- El envío **no espera el token** (`src/client.js:191-245`). Si alguien envía antes, el Worker recibe `cf-turnstile-response` vacío y responde 403 (`worker/index.js:103-105`, `worker/comun.js:137`).
- El aviso que ve dice «No pudimos enviar tu mensaje. Escríbenos directamente a contacto@volutus.cl.». No dice que basta reintentar.

Le pasa a dos tipos de visitante:

- Quien **pega un texto ya escrito** y envía de inmediato, sobre todo en el celular. La guía «Qué preparar antes de cotizar» sugiere justamente prepararlo antes.
- Un **agente de IA** que rellena el formulario por WebMCP: el foco recién cae en «Enviar mensaje» (`src/components/Contacto.jsx:40-43`) y en ese momento empieza a bajar Turnstile.

En el brief pasa lo mismo al llegar a la revisión (`src/comportamiento/brief/brief.js:408`), pero ahí la salida es buena: las respuestas quedan guardadas y se puede reintentar.

Que el mensaje sea largo no causa el problema: el token dura 300 s y Cloudflare lo renueva solo (`refresh-expired: auto`, que el sitio no cambia).

## Quién lo encontró

- **U06:** Android y Samsung Internet; llega desde Instagram con el texto en sus notas. En la traza sorteada el token alcanzó a llegar. En las forzadas recibe el 403 y reintenta, escribe al correo o se va.
- **El perfil de agentes WebMCP.**

## Impacto (cifras del modelo, no del mercado)

Queda entre las tres mayores pérdidas en el 75,5 % de 200 sorteos de los supuestos. Cerca de 3 de cada 1.000 visitantes se van por esto, y en el perfil de agentes, 68 de cada 1.000. **Por confirmar con tiempos reales** (Playwright contra un build local, o un celular con 4G): el modelo supone que entre el 15 y el 55 % de quienes pegan y envían en el celular lo hacen antes del token.

## Propuesta (para discutir, no implementada)

- [ ] Al enviar sin token, esperarlo con un tope de unos segundos en lugar de mandar el POST vacío. Por ejemplo, con una promesa que resuelva el `callback` del widget.
- [ ] O cargar Turnstile antes: al asomar el formulario en pantalla y no al primer foco, si no pesa en Lighthouse.
- [ ] Si igual falla, que el aviso diga primero «Vuelve a enviarlo» y después ofrezca el correo.
