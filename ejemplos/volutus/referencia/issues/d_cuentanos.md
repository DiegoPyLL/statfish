Hallado en el caso de prueba de Statfish: recorrido del código de `main` @ `76b713a`, 20-11-2026, sin cambiar nada del repo. El detalle está en `docs/caso-volutus/` del repo `statfish`.

## Qué pasa

- En `/servicios/desarrollo-web`, el «Cuéntanos tu proyecto» de la cabecera lleva a `/brief-web` (`src/data/paginas-de-servicio.js:66`, `src/paginas/Servicio.jsx:89`). Ese brief tiene 9 partes y toma de 35 a 45 min (`src/lib/brief/preguntas.js:89-93`), y está pensado para clientes que ya recibieron el link.
- El «Cuéntanos tu proyecto» de la barra lleva al formulario corto de la misma página (`src/components/Barra.jsx:158`).
- En las otras seis páginas de servicio, el de la cabecera también lleva al formulario.
- La documentación no coincide: `src/paginas/Brief.jsx:10-12` dice que el brief «No se enlaza desde el sitio», pero `src/lib/meta.js:301-302` y el README dicen que sí.

Es una decisión documentada en el README, no un error. Este issue es para decidirla con datos.

## Quién lo encontró

- **U25:** Antofagasta, listo para encargar su sitio. En las trazas forzadas abre el brief, ve «35 a 45 min» y lo deja para después, o vuelve y usa el formulario.
- **El perfil de escritorio que busca una página web.**

## Impacto (cifras del modelo, no del mercado)

Es la **mayor pérdida del modelo** en el 43 % de 200 sorteos de los supuestos, y queda entre las tres mayores en el 83 %. Se pierden cerca de 3,6 de cada 1.000 visitantes, y 15 de cada 1.000 entre quienes buscan una página web desde el escritorio. Si la cabecera llevara al formulario, la pérdida atribuible al código bajaría de 1,30 % a 0,94 % de las visitas. El supuesto que más pesa es cuántos prospectos completan el brief: entre el 25 y el 65 %.

## Propuesta (para discutir, no implementada)

- [ ] Que la cabecera lleve al formulario, como en los otros servicios, y ofrecer el brief después: en la respuesta o en la reunión.
- [ ] O cambiar el texto del botón para que diga lo que abre, por ejemplo «Llena el brief (35 a 45 min)».
- [ ] Corregir el comentario de `src/paginas/Brief.jsx:10-12`.
