
### Relatos

Una línea por usuario, escrita después del sorteo y solo con sus atributos.

| Id | Relato |
|---|---|
| U01 | Tiene una consultora chica en la Araucanía. Un colega le pasó el link por WhatsApp y está mirando si le convendría vender sus asesorías en línea. |
| U02 | Vende artículos de pesca en Coquimbo y quiere su primera página. Ya lo decidió: escribe por WhatsApp desde el computador. |
| U03 | Profesora jubilada que hace clases particulares en el Maule. Buscaba cuánto cuesta una página y se va desde la portada. |
| U04 | Socio de un estudio contable chico en el Biobío. Llega a una guía sobre planillas y escribe desde el formulario del artículo, que ya trae el servicio marcado. |
| U05 | Distribuye insumos de aseo y busca clientes nuevos. Lee un artículo y no escribe. |
| U06 | Tiene una ferretería en Coquimbo. Llega desde Instagram con el texto ya escrito en sus notas, lo pega y envía; esta vez el token alcanzó a llegar. |
| U07 | Lleva una tienda de ropa en Santiago con pedidos por WhatsApp. Calcula un estimado de automatización y lo deja para después. |
| U08 | Administra restaurantes en la Araucanía. Un asistente de IA le nombró a Volutus cuando preguntó por la Ley 21.719; se va desde la portada. Con movimiento reducido la nube queda quieta, sin problema (R13). |
| U09 | Jefe comercial de una fábrica de envases. Un asistente le recomendó la página de prospección y se va sin buscar más. |
| U10 | Dueña de una constructora en Antofagasta. Ve un post en Instagram, calcula la prospección desde el navegador de la app y escribe por WhatsApp. |
| U11 | Vende repuestos en Arica con el inventario en un cuaderno. Llega a sistemas de gestión y se va. |
| U12 | Hace tortas por encargo en el Maule. Escribe la dirección de memoria y se va desde la portada. |
| U13 | Dueño de una cafetería en Santiago y cliente de Volutus. Navega con JavaScript apagado en Firefox. Llena el brief entero y la página le dice «Recibimos tu brief.», pero no llega nada (R21). |
| U14 | Un taller de bicicletas en Coquimbo. Quien llena el brief escribe el nombre del negocio en «Tu nombre». Lo llena en dos sesiones en un navegador sin almacenamiento y al volver no queda nada (R12). |
| U15 | Transportista independiente de Santiago. Llega desde Instagram a la guía de la ley; su apellido lleva apóstrofo y su iPhone lo escribe `’`. |
| U16 | Abogada independiente que lee con Safari y JavaScript apagado. Lee un artículo sobre datos y se va. |
| U17 | Dueño de una sanguchería en Antofagasta. Abre el link desde Facebook en un teléfono viejo y se va desde la portada. |
| U18 | Encargado de una tienda en Antofagasta que usa un agente de IA en Chrome. Llega a `/ley21719` y se va. |
| U19 | Kinesiólogo independiente en Coquimbo, con Firefox en modo estricto. Consulta la Ley 21.719 y se va. |
| U20 | Tiene un centro de estética en Santiago y firma «Ma. Paz». Llega a prospección y se va. |
| U21 | Emprendedor de 25 años con una tienda de accesorios. Viene de Instagram decidido a pedir una página. Sin JavaScript, el envío nativo le responde «Faltan datos o el correo no es válido…» por el guion de su nombre, y se va (R7, R1). |
| U22 | Ingeniero de una consultora pequeña, con Linux y JavaScript apagado. Un asistente le citó un artículo y se va. |
| U23 | Pastelera independiente y clienta de Volutus. Usa un agente de IA para llenar el brief; esta vez lo envía con calma y llega con número de referencia. |
| U24 | Nutricionista joven con consulta en Coquimbo. Le recomendaron la guía de la Ley 21.719 por WhatsApp; navega sin JavaScript. |
| U25 | Vende productos importados en Antofagasta. Llega a desarrollo web listo para encargar su sitio y escribe por WhatsApp. |
| U26 | Dueña de una picada en Santiago y clienta de Volutus. Llena el brief en su iPhone con JavaScript desactivado: «Recibimos tu brief.», y no llega nada (R21). |
| U27 | Gerenta de una constructora pequeña; firma «Marie-Ange». El formulario le pide «Usa solo letras.»: cambia su nombre y envía (R1). |
| U28 | Arquitecto con oficina chica. En Android el apóstrofo es recto y pasa. Calcula el estimado y lo envía con el mensaje ya escrito (R14). |
| U29 | Tiene una distribuidora de huevos en Santiago y usa Opera con JavaScript apagado. Mira automatización y se va. |
| U30 | Administra un bar en Santiago. Un asistente le habló de agentes de IA; calcula el estimado y lo deja para después. |
| U31 | Dueña de un restaurante en Valparaíso. Lee un artículo sobre datos con JavaScript apagado y no escribe. |
| U32 | Vende vinos de Ñuble y recibió el brief, pero no lo termina. |
| U33 | Psicóloga en el Biobío que prueba un agente de IA en Chrome. Lee una guía sobre agentes y no escribe. |
| U34 | Tiene una amasandería en el Maule y usa un agente de IA en Chrome. Mira prospección y no escribe. |

## Los flujos

Cada paso separa tres cosas:

1. **La acción**, sorteada con P(transición | usuario). La columna *Sorteo* es el número al azar con su semilla y *P*, la
   probabilidad de la rama elegida.
2. **La consecuencia**, que sale del código real. La columna *Regla y evidencia* dice cuál.
3. **La percepción**, con las cuatro preguntas del recorrido cognitivo (Wharton et al.): ¿intenta lograr el efecto
   correcto?, ¿nota que la acción está disponible?, ¿la asocia con el efecto?, ¿ve el progreso? «—» quiere decir que las
   cuatro dan «sí».

Ningún LLM elige acciones. Predicen mal la próxima acción de una persona real: 11,86 % de acierto en ShopCART, de
Lu et al. 2025.

### Trazas sorteadas
