# El envío no espera el token de Turnstile: 403 a quien pega y envía rápido, y a los agentes

Hallado en el caso de prueba de Statfish: recorrido del código de `main` @ `76b713a`, 2026-11-20, sin cambiar nada del repo.

## Qué pasa

- Turnstile se descarga **al primer foco** dentro del formulario (`src/lib/turnstile.js:53`), y el widget se monta cuando termina de cargar el script (`src/lib/turnstile.js:27-51`).
- El envío **no espera el token** (`src/client.js:191-245`). Si alguien envía antes, el Worker recibe `cf-turnstile-response` vacío y responde 403 (`worker/index.js:103-105`, `worker/comun.js:137`).
- El aviso dice «No pudimos enviar tu mensaje. Escríbenos directamente a contacto@volutus.cl.». No dice que basta reintentar.

Le pasa a quien **pega un texto ya escrito** y envía de inmediato, sobre todo en el celular, y a un **agente de IA** que rellena el formulario por WebMCP: el foco recién cae en «Enviar mensaje» (`src/components/Contacto.jsx:40-43`) y en ese momento empieza a bajar Turnstile.

Que el mensaje sea largo no causa el problema: el token dura 300 s y Cloudflare lo renueva solo (`refresh-expired: auto`, que el sitio no cambia).

## Quién lo encontró

- **U06:** Android y Samsung Internet; llega desde Instagram con el texto en sus notas. En la traza sorteada el token alcanzó a llegar; en las forzadas recibe el 403 y reintenta, escribe al correo o se va.
- **El perfil de agentes WebMCP.**

## Impacto (cifras del modelo, no del mercado)

Queda entre las tres mayores pérdidas en el 75,5 % de 200 sorteos de los supuestos. Cerca de 3 de cada 1.000 visitantes se van por esto, y en el perfil de agentes, 63 de cada 1.000. **Por confirmar con tiempos reales**: el modelo supone que entre el 15 % y el 55 % de quienes pegan y envían en el celular lo hacen antes del token.

## Propuesta (para discutir, no implementada)

- [ ] Al enviar sin token, esperarlo con un tope de unos segundos en lugar de mandar el POST vacío.
- [ ] O cargar Turnstile antes: al asomar el formulario en pantalla y no al primer foco.
- [ ] Si igual falla, que el aviso diga primero «Vuelve a enviarlo» y después ofrezca el correo.
