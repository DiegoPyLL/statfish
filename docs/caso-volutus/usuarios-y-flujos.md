# Usuarios y flujos

Cuarto paso del caso ([recorrido](recorrido.md) → [modelo](modelo.md) → [perfiles](perfiles.md) → usuarios y flujos →
[resultados](resultados.md)). Aquí la red se convierte en **personas concretas**, y cada una **recorre el sitio**.

## Cómo se crearon los usuarios

**Primero la estructura, después el relato.** Los atributos de cada usuario los sortea el script con semilla, desde la
red del modelo. El LLM no elige a nadie: solo escribe el relato de atributos que ya están fijos. Es la defensa contra el
sesgo que documenta «LLM Generated Persona is a Promise with a Catch» (NeurIPS 2025): cuanto más inventa el modelo,
más se sesga la persona.

| Grupo | Cuántos | Cómo | Para qué |
|---|---|---|---|
| Representativos | 12 | Muestreo ancestral de la red tal cual (p50), semilla 20261120 | Que la muestra se parezca a la población |
| Cobertura y cola | 22 | AETG voraz. En cada vuelta se sortean 3.000 candidatos de una red **aplanada** (q), con lo raro inflado, y se elige el que cubre más pares nuevos. Las restricciones del código se cumplen solas, porque los candidatos salen de la misma red. | Que cada par de valores posible de 13 factores aparezca al menos una vez: 514 de 514 |

Cada usuario de cobertura lleva su **peso de importancia p/q**: cuánta población real representa frente a lo que se
infló para encontrarlo. Un peso de 10⁻⁶ dice que ese usuario existe para cubrir una combinación, no porque sea común.
Para reponderar a la población se usan esos pesos.

Los 13 factores de la cobertura son:

- plataforma;
- motor del navegador;
- navegador de app;
- canal de envío;
- JS;
- almacenamiento;
- movimiento;
- GPU;
- persona o agente;
- tipo de nombre;
- ritmo;
- privacidad;
- destino.

El plan estimaba de 24 a 30 usuarios. Salieron 34, porque es lo que pidió cubrir todos los pares.

Los nombres son **sintéticos**: combinaciones de nombres y apellidos comunes, sin personas reales. Rubro, región y edad
son variables de relato y no cambian el flujo.

## Los 34 usuarios

| Id | Cómo se creó | Peso p/q | Perfil | Nombre (sintético) | Equipo | Lo raro | Busca | Llega a | Desenlace sorteado | P(contacto) esperada |
|---|---|---|---|---|---|---|---|---|---|---|
| U01 | representativo | — | S1 | Marcelo Sánchez | celular Android, Chrome | — | tienda online, explorando | portada | se va sin intentar | 8,3 % |
| U02 | representativo | — | S2 | Luis Soto | escritorio Windows, Edge | — | página web, listo | portada | contacto | 52,7 % |
| U03 | representativo | — | S2 | Claudia Álvarez | escritorio Windows, Chrome | — | página web, explorando | portada | se va sin intentar | 6,9 % |
| U04 | representativo | — | S3 | Ignacio Rojas | escritorio Windows, Chrome | — | sistema de gestión, comparando | un artículo | contacto | 21,5 % |
| U05 | representativo | — | S3 | Tomás Vásquez | escritorio Windows, Edge | — | prospección, comparando | un artículo | se va sin intentar | 21,5 % |
| U06 | representativo | — | S1 | Cristóbal López | celular Android, Samsung Internet | pega y envía rápido | automatización, listo | portada | contacto | 54,1 % |
| U07 | representativo | — | S4 | Claudia González | celular iOS, Safari | — | automatización, comparando | su servicio | se va sin intentar | 22,7 % |
| U08 | representativo | — | S5 | Valentina Díaz | escritorio Windows, Chrome | movimiento reducido | Ley 21.719, explorando | portada | se va sin intentar | 6,9 % |
| U09 | representativo | — | S3 | Gonzalo Castillo | escritorio Windows, Opera | — | prospección, explorando | su servicio | se va sin intentar | 10,8 % |
| U10 | representativo | — | S4 | Andrea Gutiérrez | celular iOS, navegador de la app | navegador de app | prospección, comparando | su servicio | contacto | 21,7 % |
| U11 | representativo | — | S3 | Paula Tapia | escritorio Windows, Chrome | — | sistema de gestión, comparando | su servicio | se va sin intentar | 22,7 % |
| U12 | representativo | — | S1 | Constanza Sepúlveda | celular Android, Samsung Internet | — | página web, comparando | portada | se va sin intentar | 19,3 % |
| U13 | cobertura | 4.9e-07 | S6 | Jean-Pierre Hernández | escritorio macOS, Firefox | sin JS, privacidad estricta, movimiento reducido, GPU lenta, guion o punto, pega y envía rápido | brief (cliente) | /brief-web | pérdida silenciosa | 0,0 % |
| U14 | cobertura | 3.1e-07 | S6 | Taller 2 Ruedas | escritorio Windows, Edge | privacidad estricta, sin almacenamiento, agente WebMCP, GPU sin WebGL, nombre de empresa | brief (cliente) | /brief-web | se va por fricción | 20,4 % |
| U15 | cobertura | 5.5e-06 | S7 | Constanza D'Amico | celular iOS, navegador de la app | privacidad estricta, navegador de app, movimiento reducido, GPU sin WebGL, apóstrofo + Smart Punctuation | Ley 21.719, explorando | /ley21719 | se va sin intentar | 3,9 % |
| U16 | cobertura | 3.2e-07 | S7 | Fernanda O'Neill | escritorio macOS, Safari | sin JS, sin almacenamiento, movimiento reducido, GPU lenta, apóstrofo, pega y envía rápido | Ley 21.719, explorando | un artículo | se va sin intentar | 2,3 % |
| U17 | cobertura | 4.8e-04 | S7 | Héctor Díaz | celular Android, navegador de la app | sin JS, privacidad estricta, sin almacenamiento, navegador de app, GPU lenta, pega y envía rápido | sistema de gestión, explorando | portada | se va sin intentar | 3,3 % |
| U18 | cobertura | 7.7e-05 | S8 | Matías D'Etigny | escritorio macOS, Chrome | agente WebMCP, movimiento reducido, apóstrofo | Ley 21.719, explorando | /ley21719 | se va sin intentar | 6,0 % |
| U19 | cobertura | 5.9e-02 | S7 | Nicolás Araya | escritorio Linux, Firefox | privacidad estricta, sin almacenamiento, GPU lenta | Ley 21.719, explorando | /ley21719 | se va sin intentar | 7,2 % |
| U20 | cobertura | 9.8e-06 | S7 | Ma. Paz Sánchez | celular Android, Firefox | privacidad estricta, movimiento reducido, GPU sin WebGL, guion o punto, pega y envía rápido | prospección, explorando | su servicio | se va sin intentar | 7,9 % |
| U21 | cobertura | 3.3e-06 | S7 | Jean-Baptiste Gutiérrez | celular iOS, navegador de la app | sin JS, sin almacenamiento, navegador de app, GPU sin WebGL, guion o punto, pega y envía rápido | página web, listo | un artículo | se va por fricción | 23,6 % |
| U22 | cobertura | 3.4e-05 | S7 | Tomás O'Brien | escritorio Linux, Firefox | sin JS, privacidad estricta, sin almacenamiento, apóstrofo | sistema de gestión, explorando | un artículo | se va sin intentar | 2,6 % |
| U23 | cobertura | 3.5e-05 | S6 | Macarena Sepúlveda | escritorio macOS, Chrome | agente WebMCP, GPU sin WebGL, pega y envía rápido | brief (cliente) | /brief-web | contacto | 40,0 % |
| U24 | cobertura | 1.3e-02 | S7 | Jean-Pierre Muñoz | celular Android, Chrome | sin JS, guion o punto, pega y envía rápido | Ley 21.719, comparando | /ley21719 | se va sin intentar | 9,4 % |
| U25 | cobertura | 3.5e-04 | S8 | Nicolás Torres | escritorio macOS, Chrome | sin almacenamiento, agente WebMCP, GPU lenta, pega y envía rápido | página web, listo | su servicio | contacto | 47,4 % |
| U26 | cobertura | 5.1e-04 | S6 | Rocío O'Ryan | celular iOS, Safari | sin JS, apóstrofo + Smart Punctuation | brief (cliente) | /brief-web | pérdida silenciosa | 0,0 % |
| U27 | cobertura | 6.4e-03 | S3 | Marie-Ange Vásquez | escritorio macOS, Safari | GPU sin WebGL, guion o punto | prospección, explorando | portada | contacto con fricción | 7,0 % |
| U28 | cobertura | 1.1e-02 | S1 | Claudio O'Brien | celular Android, Firefox | GPU sin WebGL, apóstrofo | página web, explorando | portada | contacto | 7,9 % |
| U29 | cobertura | 9.2e-05 | S7 | Claudia O'Neill | escritorio Windows, Opera | sin JS, GPU lenta, apóstrofo, pega y envía rápido | automatización, explorando | su servicio | se va sin intentar | 4,3 % |
| U30 | cobertura | 3.3e-01 | S4 | Patricio Flores | celular iOS, Safari | GPU lenta | agente de IA, explorando | portada | se va sin intentar | 8,3 % |
| U31 | cobertura | 8.2e-04 | S7 | Patricia D'Etigny | celular Android, Chrome | sin JS, movimiento reducido, apóstrofo | Ley 21.719, explorando | un artículo | se va sin intentar | 2,3 % |
| U32 | cobertura | 6.2e-07 | S6 | Francisca O'Brien | celular Android, Firefox | privacidad estricta, sin almacenamiento, GPU sin WebGL, apóstrofo, pega y envía rápido | brief (cliente) | /brief-web | se va sin intentar | 48,0 % |
| U33 | cobertura | 5.3e-05 | S8 | Ma. Paz Reyes | escritorio Linux, Chrome | agente WebMCP, GPU sin WebGL, guion o punto | agente de IA, explorando | un artículo | se va sin intentar | 3,8 % |
| U34 | cobertura | 6.6e-02 | S8 | Andrés Silva | escritorio Windows, Chrome | agente WebMCP, pega y envía rápido | prospección, comparando | portada | se va sin intentar | 16,7 % |

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

#### U01 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,556 | 1 | llega a / | | — |
| 2 | En / | 0,31 | 0,55 | se va sin buscar más | | — |

#### U02 · contacto · P(camino) = 0,106
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,14 | 1 | llega a / | | — |
| 2 | En / | 0,362 | 0,54 | va a /servicios/desarrollo-web | | — |
| 3 | En /servicios/desarrollo-web | 0,916 | 0,55 | lee la página sin calcular | | — |
| 4 | ¿Escribe? | 0,828 | 0,42 | baja al formulario | | — |
| 5 | Formulario | 0,787 | 1 | elige WhatsApp y escribe | | — |
| 6 | Validación del nombre | 0,931 | 1 | el nombre pasa | | — |
| 7 | WhatsApp | 0,414 | 0,85 | se abre WhatsApp con el mensaje escrito y lo envía | | — |

#### U03 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,236 | 1 | llega a / | | — |
| 2 | En / | 0,236 | 0,55 | se va sin buscar más | | — |

#### U04 · contacto · P(camino) = 0,134
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,991 | 1 | llega a un artículo | | — |
| 2 | En un artículo | 0,757 | 0,455 | termina el artículo | | — |
| 3 | ¿Escribe? | 0,824 | 0,3 | va al formulario | | — |
| 4 | Formulario | 0,785 | 1 | elige correo y escribe | | — |
| 5 | Validación del nombre | 0,99 | 1 | el nombre pasa | | — |
| 6 | Envío por correo | 0,018 | 0,983 | envía: «¡Gracias por escribirnos!» | | — |

#### U05 · se va sin intentar · P(camino) = 0,318
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,596 | 1 | llega a un artículo | | — |
| 2 | En un artículo | 0,893 | 0,455 | termina el artículo | | — |
| 3 | ¿Escribe? | 0,049 | 0,7 | decide no escribir por ahora | | — |

#### U06 · contacto · P(camino) = 0,163
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,688 | 1 | llega a / | | — |
| 2 | En / | 0,923 | 0,36 | sigue en la portada | | — |
| 3 | ¿Escribe? | 0,768 | 0,7 | va al formulario | | — |
| 4 | Formulario de la portada | 0,941 | 1 | elige correo y escribe | | — |
| 5 | Validación del nombre | 0,046 | 1 | el nombre pasa | | — |
| 6 | Envío por correo | 0,479 | 0,645 | envía: «¡Gracias por escribirnos!» | | — |

#### U07 · se va sin intentar · P(camino) = 0,133
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,395 | 1 | llega a /servicios/automatizacion-procesos | | — |
| 2 | En /servicios/automatizacion-procesos | 0,405 | 0,292 | calcula un estimado | | — |
| 3 | Estimado | 0,894 | 0,65 | mira el precio y sigue leyendo | | — |
| 4 | ¿Escribe? | 0,048 | 0,7 | decide no escribir por ahora | | — |

#### U08 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,63 | 1 | llega a / | | — |
| 2 | En / | 0,398 | 0,55 | se va sin buscar más | | — |

#### U09 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,434 | 1 | llega a /servicios/prospeccion-de-clientes | | — |
| 2 | En /servicios/prospeccion-de-clientes | 0,378 | 0,55 | se va sin buscar más | | — |

#### U10 · contacto · P(camino) = 0,0436
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,622 | 1 | llega a /servicios/prospeccion-de-clientes | | — |
| 2 | En /servicios/prospeccion-de-clientes | 0,638 | 0,292 | calcula un estimado | | — |
| 3 | Estimado | 0,842 | 0,65 | mira el precio y sigue leyendo | | — |
| 4 | ¿Escribe? | 0,707 | 0,3 | va al formulario | | — |
| 5 | Formulario | 0,702 | 1 | elige WhatsApp y escribe | | — |
| 6 | Validación del nombre | 0,601 | 1 | el nombre pasa | | — |
| 7 | WhatsApp | 0,68 | 0,765 | se abre WhatsApp con el mensaje escrito y lo envía | | — |

#### U11 · se va sin intentar · P(camino) = 0,35
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,659 | 1 | llega a /servicios/sistemas-de-gestion | | — |
| 2 | En /servicios/sistemas-de-gestion | 0,268 | 0,35 | se va sin buscar más | | — |

#### U12 · se va sin intentar · P(camino) = 0,35
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,766 | 1 | llega a / | | — |
| 2 | En / | 0,294 | 0,35 | se va sin buscar más | | — |

#### U13 · pérdida silenciosa · P(camino) = 0,8
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,922 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,777 | 0,8 | completa el brief y llega a la revisión | | — |
| 3 | Validación del nombre | 0,867 | 1 | sin brief.js no hay validación en el navegador | | — |
| 4 | Envío del brief | 0,467 | 1 | POST nativo con «transcurrido» vacío: «Recibimos tu brief.» y no llega nada | R21: `src/paginas/Brief.jsx:326`, `src/comportamiento/brief/brief.js:640` | sí/sí/sí/no |
| | | | | ↳ *La página dice «Recibimos tu brief.» y no llegó nada.* | | |

#### U14 · se va por fricción · P(camino) = 0,4
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,549 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,087 | 0,4 | lo llena en dos sesiones y al volver no hay nada guardado | R12: `src/lib/almacen.js:1-3`, `src/comportamiento/brief/brief.js:163-166` | — |
| | | | | ↳ *Avisó que no puede guardar («No cierres la página hasta enviar»).* | | |

#### U15 · se va sin intentar · P(camino) = 0,243
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,213 | 1 | llega a /ley21719 | | — |
| 2 | En /ley21719 | 0,838 | 0,27 | lee la guía sin calcular | | — |
| 3 | ¿Escribe? | 0,194 | 0,9 | decide no escribir por ahora | | — |

#### U16 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,252 | 1 | llega a un artículo | | — |
| 2 | En un artículo | 0,349 | 0,55 | se va sin buscar más | | — |

#### U17 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,542 | 1 | llega a / | | — |
| 2 | En / | 0,533 | 0,55 | se va sin buscar más | | — |

#### U18 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,171 | 1 | llega a /ley21719 | | — |
| 2 | En /ley21719 | 0,02 | 0,55 | se va sin buscar más | | — |

#### U19 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,537 | 1 | llega a /ley21719 | | — |
| 2 | En /ley21719 | 0,458 | 0,55 | se va sin buscar más | | — |

#### U20 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,351 | 1 | llega a /servicios/prospeccion-de-clientes | | — |
| 2 | En /servicios/prospeccion-de-clientes | 0,227 | 0,55 | se va sin buscar más | | — |

#### U21 · se va por fricción · P(camino) = 0,0374
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,169 | 1 | llega a un artículo | | — |
| 2 | En un artículo | 0,223 | 0,27 | va a /servicios/desarrollo-web | | — |
| 3 | En /servicios/desarrollo-web | 0,487 | 0,55 | lee la página sin calcular | | — |
| 4 | ¿Escribe? | 0,896 | 0,42 | baja al formulario | | — |
| 5 | Formulario | 0,218 | 1 | envía sin JavaScript: POST nativo | R7: `src/components/Contacto.jsx:23-25`, `worker/index.js:34-40` | sí/sí/sí/no |
| | | | | ↳ *La página de respuesta trae el correo como texto, sin enlace, y lo escrito se pierde al salir.* | | |
| 6 | Respuesta sin JavaScript | 0,756 | 0,6 | página «Faltan datos o el correo no es válido…»: se va | R7: `src/components/Contacto.jsx:23-25`, `worker/index.js:34-40` | sí/sí/sí/no |
| | | | | ↳ *La página de respuesta trae el correo como texto, sin enlace, y lo escrito se pierde al salir.* | | |

#### U22 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,271 | 1 | llega a un artículo | | — |
| 2 | En un artículo | 0,529 | 0,55 | se va sin buscar más | | — |

#### U23 · contacto · P(camino) = 0,378
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,144 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,375 | 0,8 | completa el brief y llega a la revisión | | — |
| 3 | Validación del nombre | 0,76 | 1 | el nombre pasa | | — |
| 4 | Envío del brief | 0,901 | 0,473 | envía: «Tu número de referencia es B-…» | | — |

#### U24 · se va sin intentar · P(camino) = 0,273
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,316 | 1 | llega a /ley21719 | | — |
| 2 | En /ley21719 | 0,811 | 0,39 | lee la guía sin calcular | | — |
| 3 | ¿Escribe? | 0,506 | 0,7 | decide no escribir por ahora | | — |

#### U25 · contacto · P(camino) = 0,177
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,029 | 1 | llega a /servicios/desarrollo-web | | — |
| 2 | En /servicios/desarrollo-web | 0,717 | 0,495 | lee la página sin calcular | | — |
| 3 | ¿Escribe? | 0,759 | 0,42 | baja al formulario | | — |
| 4 | Formulario | 0,109 | 1 | elige WhatsApp y escribe | | — |
| 5 | Validación del nombre | 0,503 | 1 | el nombre pasa | | — |
| 6 | WhatsApp | 0,198 | 0,85 | se abre WhatsApp con el mensaje escrito y lo envía | | — |

#### U26 · pérdida silenciosa · P(camino) = 0,8
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,004 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,042 | 0,8 | completa el brief y llega a la revisión | | — |
| 3 | Validación del nombre | 0,649 | 1 | sin brief.js no hay validación en el navegador | | — |
| 4 | Envío del brief | 0,878 | 1 | POST nativo con «transcurrido» vacío: «Recibimos tu brief.» y no llega nada | R21: `src/paginas/Brief.jsx:326`, `src/comportamiento/brief/brief.js:640` | sí/sí/sí/no |
| | | | | ↳ *La página dice «Recibimos tu brief.» y no llegó nada.* | | |

#### U27 · contacto con fricción · P(camino) = 0,0066
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,221 | 1 | llega a / | | — |
| 2 | En / | 0,701 | 0,27 | va a /servicios/prospeccion-de-clientes | | — |
| 3 | En /servicios/prospeccion-de-clientes | 0,018 | 0,45 | calcula un estimado | | — |
| 4 | Estimado | 0,469 | 0,65 | mira el precio y sigue leyendo | | — |
| 5 | ¿Escribe? | 0,976 | 0,1 | va al formulario | | — |
| 6 | Formulario | 0,258 | 1 | elige correo y escribe | | — |
| 7 | Validación del nombre | 0,075 | 0,85 | «Usa solo letras.»: reescribe el nombre | R1: `src/lib/contacto.js:89-91`, `src/client.js:82-85` | sí/sí/sí/en parte |
| | | | | ↳ *El aviso dice qué hacer, pero le pide escribir su nombre (o el de su negocio) de otra forma.* | | |
| 8 | Envío por correo | 0,542 | 0,983 | envía: «¡Gracias por escribirnos!» | | — |

#### U28 · contacto · P(camino) = 0,0418
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,251 | 1 | llega a / | | — |
| 2 | En / | 0,654 | 0,27 | va a /servicios/desarrollo-web | | — |
| 3 | En /servicios/desarrollo-web | 0,35 | 0,45 | calcula un estimado | | — |
| 4 | Estimado | 0,3 | 0,35 | pulsa «Pedir esta cotización»: el mensaje llega escrito | R14: `src/comportamiento/estimado.js:61-72` | — |
| 5 | Formulario | 0,391 | 1 | elige correo y escribe | | — |
| 6 | Validación del nombre | 0,068 | 1 | el nombre pasa | | — |
| 7 | Envío por correo | 0,681 | 0,983 | envía: «¡Gracias por escribirnos!» | | — |

#### U29 · se va sin intentar · P(camino) = 0,55
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,213 | 1 | llega a /servicios/automatizacion-procesos | | — |
| 2 | En /servicios/automatizacion-procesos | 0,548 | 0,55 | se va sin buscar más | | — |

#### U30 · se va sin intentar · P(camino) = 0,0711
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,175 | 1 | llega a / | | — |
| 2 | En / | 0,756 | 0,27 | va a /servicios/agentes-ia | | — |
| 3 | En /servicios/agentes-ia | 0,088 | 0,45 | calcula un estimado | | — |
| 4 | Estimado | 0,401 | 0,65 | mira el precio y sigue leyendo | | — |
| 5 | ¿Escribe? | 0,215 | 0,9 | decide no escribir por ahora | | — |

#### U31 · se va sin intentar · P(camino) = 0,283
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,548 | 1 | llega a un artículo | | — |
| 2 | En un artículo | 0,775 | 0,315 | termina el artículo | | — |
| 3 | ¿Escribe? | 0,179 | 0,9 | decide no escribir por ahora | | — |

#### U32 · se va sin intentar · P(camino) = 0,12
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,315 | 1 | abre el link del brief que le mandó Volutus | R17: `src/comportamiento/brief/brief.js:134-139`, `src/comportamiento/brief/brief.js:163` | — |
| 2 | Brief (cliente) | 0,9 | 0,12 | no lo termina | | — |

#### U33 · se va sin intentar · P(camino) = 0,283
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,554 | 1 | llega a un artículo | | — |
| 2 | En un artículo | 0,712 | 0,315 | termina el artículo | | — |
| 3 | ¿Escribe? | 0,19 | 0,9 | decide no escribir por ahora | | — |

#### U34 · se va sin intentar · P(camino) = 0,15
| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |
|---|---|---|---|---|---|---|
| 1 | Llegada | 0,025 | 1 | llega a / | | — |
| 2 | En / | 0,64 | 0,39 | va a /servicios/prospeccion-de-clientes | | — |
| 3 | En /servicios/prospeccion-de-clientes | 0,644 | 0,55 | lee la página sin calcular | | — |
| 4 | ¿Escribe? | 0,139 | 0,7 | decide no escribir por ahora | | — |

### Trazas forzadas: cobertura de arcos

Con 34 trazas sorteadas se recorrieron 31 de los 61 arcos de la cadena. Los demás son caminos poco probables, y ahí
están casi todas las fricciones. Para cubrirlos se usa la técnica de los modelos de uso estadísticos (Whittaker y
Thomason; JUMBL): por cada arco que falta se busca, entre los 34 usuarios, el camino **más probable** que pasa por él y
se recorre forzado. *P(camino)* dice cuán raro es. Así quedan cubiertos los 61 arcos.

| Arco que faltaba | Usuario | P(camino) | Desenlace | Camino |
|---|---|---|---|---|
| brief_envio: el agente lo llena y la persona envía antes de 8 s: «Recibimos tu brief.» y no llega nada | U23 | 0,4 | pérdida silenciosa | completa el brief y llega a la revisión → el nombre pasa → el agente lo llena y la persona envía antes de 8 s: «Recibimos tu brief.» y no llega nada |
| brief_envio: falla el envío; copia sus respuestas y las manda por correo | U32 | 0,024 | escribe al correo | completa el brief y llega a la revisión → el nombre pasa → falla el envío; copia sus respuestas y las manda por correo |
| brief_envio: falla el envío; sus respuestas siguen guardadas y reintenta | U32 | 0,14 | contacto con fricción | completa el brief y llega a la revisión → el nombre pasa → falla el envío; sus respuestas siguen guardadas y reintenta |
| brief_prospecto: llena lo obligatorio y llega a la revisión | U02 | 0,035 | contacto | va a /servicios/desarrollo-web → lee la página sin calcular → pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief → llena lo obligatorio y llega a la revisión → el nombre pasa → envía: «Tu número de referencia es B-…» |
| brief_prospecto: ve «35 a 45 min» y lo deja para después | U25 | 0,05 | se va por fricción | lee la página sin calcular → pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief → ve «35 a 45 min» y lo deja para después |
| brief_prospecto: ve «35 a 45 min», vuelve y usa el formulario | U25 | 0,023 | contacto con fricción | lee la página sin calcular → pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief → ve «35 a 45 min», vuelve y usa el formulario → elige WhatsApp y escribe → el nombre pasa → se abre WhatsApp con el mensaje escrito y lo envía |
| decide: pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief | U25 | 0,05 | se va por fricción | lee la página sin calcular → pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief → ve «35 a 45 min» y lo deja para después |
| decide: pulsa «Cuéntanos tu proyecto»: va al formulario de la portada | U24 | 0,07 | se va por fricción | lee la guía sin calcular → pulsa «Cuéntanos tu proyecto»: va al formulario de la portada → envía sin JavaScript: POST nativo → página «Faltan datos o el correo no es válido…»: se va |
| envio_correo: Resend no responde: 502 | U06 | 0,00021 | se va por fricción | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → Resend no responde: 502 → cree que el sitio falla y se va |
| envio_correo: Turnstile no pasa: 403 «No pudimos enviar tu mensaje…» | U19 | 0,0068 | se va por fricción | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → elige correo y escribe → el nombre pasa → Turnstile no pasa: 403 «No pudimos enviar tu mensaje…» → cree que el sitio falla y se va |
| envio_correo: envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» | U06 | 0,043 | se va por fricción | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» → cree que el sitio falla y se va |
| estimado: pulsa «Pedir esta cotización»: va a la portada | U24 | 0,041 | se va por fricción | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → envía sin JavaScript: POST nativo → página «Faltan datos o el correo no es válido…»: se va |
| form: el agente rellena el formulario y la persona lo revisa | U34 | 0,031 | contacto | sigue en la portada → va al formulario → el agente rellena el formulario y la persona lo revisa → el nombre pasa → envía: «¡Gracias por escribirnos!» |
| ley_a_portada: escribe de nuevo lo que necesita | U24 | 0,041 | se va por fricción | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → envía sin JavaScript: POST nativo → página «Faltan datos o el correo no es válido…»: se va |
| ley_a_portada: llega a un formulario vacío, sin lo que marcó, y se va | U24 | 0,023 | se va por fricción | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → llega a un formulario vacío, sin lo que marcó, y se va |
| nojs: página «Faltan datos o el correo no es válido…»: escribe desde su correo | U21 | 0,18 | escribe al correo | termina el artículo → va al formulario → envía sin JavaScript: POST nativo → página «Faltan datos o el correo no es válido…»: escribe desde su correo |
| nojs: página «No pudimos enviar tu mensaje. Escríbenos directamente a…»: escribe desde su correo | U29 | 0,028 | escribe al correo | calcula un estimado → pulsa «Pedir esta cotización»: el mensaje llega escrito → envía sin JavaScript: POST nativo → página «No pudimos enviar tu mensaje. Escríbenos directamente a…»: escribe desde su correo |
| nojs: página «No pudimos enviar tu mensaje. Escríbenos directamente a…»: se va | U29 | 0,043 | se va por fricción | calcula un estimado → pulsa «Pedir esta cotización»: el mensaje llega escrito → envía sin JavaScript: POST nativo → página «No pudimos enviar tu mensaje. Escríbenos directamente a…»: se va |
| pagina: calcula un estimado de la ley de datos | U24 | 0,12 | se va sin intentar | calcula un estimado de la ley de datos → mira el precio y sigue leyendo → decide no escribir por ahora |
| pagina: el agente usa «estimar_precio» y recibe el estimado | U25 | 0,12 | contacto | el agente usa «estimar_precio» y recibe el estimado → pulsa «Pedir esta cotización»: el mensaje llega escrito → elige WhatsApp y escribe → el nombre pasa → se abre WhatsApp con el mensaje escrito y lo envía |
| pagina: va a /ley21719 | U08 | 0,15 | se va sin intentar | va a /ley21719 → lee la guía sin calcular → decide no escribir por ahora |
| tras_error: cierra el aviso y vuelve a enviar | U06 | 0,021 | contacto con fricción | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» → cierra el aviso y vuelve a enviar → envía: «¡Gracias por escribirnos!» |
| tras_error: copia el correo del aviso y escribe desde su correo | U06 | 0,023 | escribe al correo | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» → copia el correo del aviso y escribe desde su correo |
| tras_error: cree que el sitio falla y se va | U06 | 0,043 | se va por fricción | sigue en la portada → va al formulario → elige correo y escribe → el nombre pasa → envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…» → cree que el sitio falla y se va |
| validar_nombre: «Usa solo letras.» sobre su nombre bien escrito: se rinde | U15 | 0,021 | se va por fricción | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → elige correo y escribe → «Usa solo letras.» sobre su nombre bien escrito: se rinde |
| validar_nombre: «Usa solo letras.»: no sabe cómo escribirlo y se va | U14 | 0,072 | se va por fricción | completa el brief y llega a la revisión → «Usa solo letras.»: no sabe cómo escribirlo y se va |
| validar_nombre: «Usa solo letras.»: quita el apóstrofo y sigue | U15 | 0,018 | contacto con fricción | calcula un estimado de la ley de datos → pulsa «Pedir esta cotización»: va a la portada → escribe de nuevo lo que necesita → elige correo y escribe → «Usa solo letras.»: quita el apóstrofo y sigue → envía: «¡Gracias por escribirnos!» |
| whatsapp: WhatsApp no abre desde la app: cambia a correo | U10 | 0,0053 | contacto con fricción | lee la página sin calcular → va al formulario → elige WhatsApp y escribe → el nombre pasa → WhatsApp no abre desde la app: cambia a correo → envía: «¡Gracias por escribirnos!» |
| whatsapp: WhatsApp no abre desde la app: se va | U10 | 0,0054 | se va por fricción | lee la página sin calcular → va al formulario → elige WhatsApp y escribe → el nombre pasa → WhatsApp no abre desde la app: se va |
| whatsapp: se abre WhatsApp pero no lo envía | U02 | 0,038 | no envía el WhatsApp | sigue en la portada → va al formulario → elige WhatsApp y escribe → el nombre pasa → se abre WhatsApp pero no lo envía |
