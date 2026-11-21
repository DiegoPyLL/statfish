## Lectura

**De cada 100 llegadas, el modelo da {{metricas.contacto_total|pp:1}} contactos** (intervalo de
{{intervalos.contacto_total.p5|pp:1}} a {{intervalos.contacto_total.p95|pp:1}}) y **{{metricas.perdida_por_codigo|pp}} se
pierden por el código** ({{intervalos.perdida_por_codigo.p5|pp}} a {{intervalos.perdida_por_codigo.p95|pp}}). Otras
{{desenlaces.contacto_con_friccion|pp:1}} llegan, pero después de una fricción.

**Cuatro fricciones del código explican casi toda la pérdida**, todas verificadas en `archivo:línea`:

- **R9**, la doble ruta de «Cuéntanos tu proyecto» en desarrollo web: {{reglas.R9.perdida|mil}} de cada 1.000 llegadas
  se pierden, y {{perfiles.S2.reglas.R9.perdida|mil:1}} de cada 1.000 entre quienes buscan una página web desde el
  escritorio.
- **R4**, el envío que no espera el token de Turnstile: {{reglas.R4.perdida|mil}} de cada 1.000, y
  {{perfiles.S8.reglas.R4.perdida|mil:0}} de cada 1.000 agentes de IA.
- **R1**, el nombre que solo acepta letras: {{reglas.R1.friccion|mil}} de cada 1.000 llegan con fricción y
  {{reglas.R1.perdida|mil}} se pierden.
- **R8**, el estimado que se pierde al cotizar desde `/ley21719`: {{perfiles.S5.reglas.R8.friccion|mil:1}} de cada
  1.000 de quienes buscan la ley llegan con fricción y {{perfiles.S5.reglas.R8.perdida|mil:1}} se van.

**Hay una pérdida silenciosa con respuesta de éxito: R21.** Sin JavaScript, o si `brief.js` no carga, el brief se
descarta y la página dice «Recibimos tu brief.». Tiene poca masa ({{desenlaces.perdida_silenciosa|pp}} de cada 100
llegadas), pero cae sobre **clientes**: {{perfiles.S6.reglas.R21.perdida|mil:1}} de cada 1.000 que llenan el brief lo
pierden creyendo que llegó.

**El orden es robusto donde importa.** En {{robustez.n}} sorteos de los parámetros, R1 queda entre las tres fricciones
mayores en el {{robustez.top3_friccion.R1|pct}}; R9 y R4 quedan entre las tres que más contactos hacen perder en el
{{robustez.top3_perdida.R9|pct}} y el {{robustez.top3_perdida.R4|pct}}. R8 solo en el {{robustez.top3_perdida.R8|pct}}:
depende de cuánta gente busca la ley de datos, el supuesto peor anclado (su perfil pesa entre el
{{intervalos.masa_S5.p5|pct}} y el {{intervalos.masa_S5.p95|pct}} de las llegadas).

**Arreglar las cuatro reduce la pérdida por código de {{hipotesis.base.perdida_por_codigo|pct:2}} a
{{hipotesis.todos.perdida_por_codigo|pct:2}}** de las llegadas
({{ ( hipotesis.todos.perdida_por_codigo - hipotesis.base.perdida_por_codigo ) / hipotesis.base.perdida_por_codigo |pct:0}})
y sube el contacto en {{ hipotesis.todos.contacto_total - hipotesis.base.contacto_total |pp:1}} puntos. Esa es la
«predicción» de Statfish: no un pronóstico del mercado, sino cuánto cambia el modelo si cambia el código.

**El contacto total lo mueven supuestos de intención, no el código.** En la sensibilidad, los supuestos con más efecto
sobre el contacto son cuántos clientes reciben el brief, cuánto escribe quien compara, cuántos piden la cotización y
cuántos salen de inmediato. Ninguno lo informa el código: son los primeros que conviene medir, y la cifra de contacto no
debe presentarse como predicción sin datos.

**Ningún supuesto domina la pérdida por código.** El que más la mueve es `{{morris.0.parametro|texto}}`, con
{{morris.0.perdida_por_codigo.mu_estrella|pp}} puntos al recorrer su rango, sobre una base de
{{metricas.perdida_por_codigo|pp}}. El nivel es incierto, pero no depende de un solo número inventado: la v0 tenía el
problema contrario, donde el primer lugar del precio venía de los pesos asignados.

### Lo que el código no ve

Las dudas de negocio del issue #40 y de la v0: plazos, una prueba parecida, factura, «ya probé algo que no sirvió». Los
textos que las responden están en el código, pero convertirlos en dudas pide la capa de catálogo que hizo la v0. Statfish
y la v0 se complementan: esta cadena de uso podría recibir ese catálogo como un freno más en el paso «¿Escribe?».

### Calibración

El sitio no usa analítica, y eso se respeta. La calibración mínima sin datos personales son contadores en el Worker por
motivo de respuesta (200, trampa, 400, 403 sin token, 403 con token inválido, 429 y 502; en el brief, también
`transcurrido` vacío y menos de 8 s). Calibran directamente R4, R4b, R5, R7, R10 y R21 con `statfish calibrar`.
