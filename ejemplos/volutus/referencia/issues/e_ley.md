Hallado en el caso de prueba de Statfish: recorrido del código de `main` @ `76b713a`, 20-11-2026, sin cambiar nada del repo. El detalle está en `docs/caso-volutus/` del repo `statfish`.

## Qué pasa

- `/ley21719` es la página del servicio «Ley de datos». Tiene estimado, pero no formulario.
- «Pedir esta cotización» lleva a `/#contacto` (`src/paginas/Ley21719.jsx:429`). Como el formulario no está en la misma página, lo marcado no se escribe en el mensaje (`src/components/Estimado.jsx:48`, `src/components/Estimado.jsx:204-207`).
- El formulario de la portada llega sin «Adaptarme a la ley de datos» marcado (`src/paginas/Inicio.jsx:33`). Lo mismo pasa con el «Cuéntanos tu proyecto» del cierre (`src/paginas/Ley21719.jsx:264`).
- En los otros siete servicios, el mensaje llega escrito y el servicio marcado (`src/comportamiento/estimado.js:61-72`, `src/paginas/Servicio.jsx:72-74`).

## Quién lo encontró

- **U24:** Coquimbo, le recomendaron la guía de la ley. En las trazas forzadas calcula el estimado y pulsa «Pedir esta cotización». Llega a un formulario vacío y se va, o reescribe lo que había marcado.

## Impacto (cifras del modelo, no del mercado)

Entre quienes buscan adaptarse a la ley de datos, **35 de cada 1.000** llegan al contacto después de reescribir lo que habían marcado, y **13,5 de cada 1.000 se van**. Es el perfil con más fricción entre los prospectos. Cuántos buscan la ley es el supuesto más incierto del modelo, entre el 0,7 y el 22,5 % de las visitas, y la ley rige desde el 1 de diciembre.

## Propuesta (para discutir, no implementada)

- [ ] Poner el formulario de contacto al final de `/ley21719`, con el servicio marcado, como en las páginas de servicio.
- [ ] O llevar lo marcado en el enlace o en `sessionStorage`, y escribirlo al llegar al formulario de la portada.
