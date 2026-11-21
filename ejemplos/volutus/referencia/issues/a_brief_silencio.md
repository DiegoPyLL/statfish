Hallado en el caso de prueba de Statfish: recorrido del código de `main` @ `76b713a`, 20-11-2026, sin cambiar nada del repo. El detalle está en `docs/caso-volutus/` del repo `statfish`.

## Qué pasa

Sin JavaScript, o si `brief.js` no llega a cargar, el brief se envía como formulario nativo. El campo oculto `transcurrido` va vacío, el Worker lo lee como 0 ms, lo toma por un robot apurado y responde **en silencio, con un éxito**:

- `src/paginas/Brief.jsx:326`: `<input type="hidden" name="transcurrido" />`, sin valor en el HTML.
- `src/comportamiento/brief/brief.js:640`: solo el JS le pone valor.
- `src/client.js:299-302`: `brief.js` se descarga aparte con `import()`; si falla, el formulario queda nativo.
- `worker/brief.js:282-285`: `Number('')` da 0, entonces `!(0 >= 8000)` responde `MENSAJES.silencio`.
- `worker/brief.js:85`: «Recibimos tu brief.», con estado 200. La página de respuesta sale en verde.

Quien llenó 35 a 45 minutos de preguntas ve un éxito, sin número de referencia, y a contacto@volutus.cl no llega nada. El contacto, en cambio, sin JS responde con la página que ofrece el correo (`worker/index.js:34-40`).

Lo mismo pasa (R10) si un agente de IA llena el brief por WebMCP y la persona lo envía antes de 8 s desde que abrió la página (`src/lib/brief/reglas.js:38-40`). Ahí, además, el navegador borra lo guardado al recibir el 200 (`src/comportamiento/brief/brief.js:669-680`).

## Quién lo encontró

- **U13:** cliente con el link, Firefox con JavaScript apagado. Completa el brief y ve «Recibimos tu brief.».
- **U26:** clienta en iPhone con JavaScript desactivado. Mismo desenlace.
- **U23:** clienta que usa un agente en Chrome. En la traza forzada envía antes de 8 s.

## Impacto (cifras del modelo, no del mercado)

Unos **7 de cada 1.000 clientes** que llenan el brief lo perderían así. Es poca masa, porque cuántos navegan sin JS o con fallas de carga es un supuesto, pero son clientes y la respuesta les dice lo contrario de lo que pasó.

## Propuesta (para discutir, no implementada)

- [ ] Distinguir «sin JS» de «apurado»: si `transcurrido` llega vacío, responder como el contacto sin JS (la página con el correo directo) y no con el silencio.
- [ ] Que el navegador borre lo guardado solo si la respuesta trae la referencia `B-…` del envío real. El silencio de la trampa no la lleva.
- [ ] Probar el envío del brief con JS desactivado; hoy `pnpm verificar` no cubre `/brief-web`.
- [ ] Relacionado (R7): la página sin JS del contacto trae el correo como texto, sin enlace (`worker/comun.js:32-46`), y lo escrito se pierde.
