## TABLA_PERFILES
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

## TABLA_DESENLACES
| Desenlace | De cada 100 llegadas |
|---|---|
| Contacto sin fricción | 21,39 |
| Contacto después de una fricción | 1,86 |
| Escribe al correo tras un error | 0,31 |
| Abre WhatsApp y no envía | 1,07 |
| Se va sin intentar contactar | 74,10 |
| Se va por una fricción del código | 1,23 |
| Envía y no llega nada (silencio) | 0,04 |

## TABLA_REGLAS
| Regla | Qué pasa | Se pierde (de cada 1.000 llegadas) | Llega con fricción (de cada 1.000) |
|---|---|---|---|
| R1 | El nombre solo admite letras, marcas, espacio y apóstrofo recto: rechaza guion, punto, dígitos y & | 1,75 | 9,02 |
| R9 | En desarrollo web, «Cuéntanos tu proyecto» de la cabecera abre el brief de 35 a 45 min; el de la barra, el formulario | 3,59 | 1,65 |
| R4 | Turnstile se descarga al primer foco del formulario y el envío no espera su token: sin token, 403 | 2,97 | 3,06 |
| R8 | En /ley21719, «Pedir esta cotización» y «Cuéntanos tu proyecto» llevan a /#contacto: sin lo marcado ni el servicio | 1,31 | 3,40 |
| R4b | Turnstile no se resuelve con privacidad estricta: 403 | 1,08 | 0,98 |
| R11 | En el brief, Turnstile se monta al llegar a la revisión; si falla, las respuestas siguen guardadas | 0,00 | 2,78 |
| R7 | Sin JavaScript el envío llega sin token y se rechaza; la respuesta es una página aparte sin enlace al correo | 0,56 | 0,37 |
| R12 | Sin almacenamiento, el brief no se guarda y lo avisa | 0,63 | 0,00 |
| R21 | Sin JavaScript (o si brief.js no carga) el brief llega con «transcurrido» vacío: se descarta en silencio y la página dice «Recibimos tu brief.» | 0,36 | 0,00 |
| R6 | WhatsApp se abre con window.open; en el navegador de una app puede no abrir | 0,25 | 0,23 |
| R5 | Resend no responde: 502 con el correo directo | 0,17 | 0,09 |
| R1+R2 | En iPhone y iPad el apóstrofo se escribe ’ (Smart Punctuation) y la regla del nombre lo rechaza | 0,04 | 0,05 |
| R10 | El brief enviado antes de 8 s se descarta en silencio con 200 y el navegador borra lo guardado | 0,02 | 0,00 |

## TABLA_INTERVALOS
| Métrica | p5 | p50 | p95 |
|---|---|---|---|
| Contacto (todas las vías) | 15,61 % | 22,86 % | 30,77 % |
| Pérdida atribuible al código | 0,65 % | 1,15 % | 2,11 % |
| Pasa por alguna fricción | 1,96 % | 3,35 % | 5,44 % |

## TABLA_MORRIS
| Supuesto | Rango probado | μ* sobre la pérdida (pp) | σ | μ* sobre el contacto (pp) |
|---|---|---|---|---|
| `resuelve_nombre_claro` | 70,0–95,0 % | 0,34 | 0,14 | 0,33 |
| `pega_rapido_comparando` | 5,0–20,0 % | 0,34 | 0,11 | 0,34 |
| `js_off` | 0,2–1,5 % | 0,25 | 0,04 | 0,23 |
| `contacta_comparando` | 20,0–45,0 % | 0,22 | 0,05 | 3,60 |
| `envia_brief_prospecto` | 25,0–65,0 % | 0,22 | 0,05 | 0,22 |
| `token_no_listo_rapido_movil` | 15,0–55,0 % | 0,21 | 0,14 | 0,21 |
| `abandona_seleccion_perdida` | 10,0–45,0 % | 0,21 | 0,08 | 0,20 |
| `usa_cta_brief_web` | 25,0–55,0 % | 0,20 | 0,10 | 0,17 |
| `correo_directo_tras_error` | 20,0–50,0 % | 0,19 | 0,11 | 0,19 |
| `pide_cotizacion` | 20,0–50,0 % | 0,19 | 0,08 | 2,72 |
| `nombre_empresa_signos` | 1,0–5,0 % | 0,18 | 0,10 | 0,18 |
| `sale_explorando` | 40,0–70,0 % | 0,16 | 0,06 | 2,43 |
| `estricta_base` | 1,0–6,0 % | 0,16 | 0,08 | 0,16 |
| `reintenta_tras_403` | 10,0–40,0 % | 0,15 | 0,07 | 0,15 |
| `vuelve_al_formulario` | 20,0–50,0 % | 0,14 | 0,07 | 0,13 |
| `nombre_guion_punto` | 1,0–4,0 % | 0,12 | 0,08 | 0,12 |
| `relacion_cliente_brief` | 2,0–10,0 % | 0,12 | 0,03 | 4,50 |
| `turnstile_falla_estricta` | 10,0–50,0 % | 0,12 | 0,05 | 0,12 |
| `usa_estimado_ley` | 25,0–55,0 % | 0,10 | 0,09 | 0,16 |
| `token_no_listo_rapido_escritorio` | 5,0–30,0 % | 0,06 | 0,03 | 0,06 |
| `nombre_apostrofo` | 0,1–1,0 % | 0,04 | 0,03 | 0,04 |
| `resuelve_nombre_opaco` | 30,0–80,0 % | 0,01 | 0,01 | 0,01 |
| `movil_si_recomendacion` | 55,0–85,0 % | 0,01 | 0,01 | 0,05 |
| `smart_punct_on` | 85,0–99,0 % | 0,00 | 0,00 | 0,00 |

## TABLA_HIPOTESIS
| Escenario | Contacto | Pérdida por código | Pasa por fricción |
|---|---|---|---|
| Hoy (modelo) | 23,74 % | 1,30 % | 3,47 % |
| R1+R2: aceptar ’, guion y punto en el nombre | 23,82 % | 1,22 % | 3,01 % |
| R4: esperar el token antes de enviar | 24,02 % | 1,02 % | 2,95 % |
| R8: llevar lo marcado y el servicio desde /ley21719 | 23,86 % | 1,17 % | 3,03 % |
| R9: «Cuéntanos tu proyecto» de la cabecera al formulario | 24,05 % | 0,94 % | 2,95 % |
| R21+R10: el brief sin JS (o apurado) responde como el contacto | 23,76 % | 1,27 % | 3,47 % |
| Todos | 24,56 % | 0,42 % | 1,44 % |

## TABLA_FIDELIDAD
| Variable | Declarada | En la muestra | n |
|---|---|---|---|
| relación: cliente con link | 5,00 % | 4,95 % | 120.000 |
| sin JavaScript | 0,50 % | 0,45 % | 120.000 |
| sin almacenamiento | 3,00 % | 2,97 % | 120.000 |
| movimiento reducido | 5,00 % | 5,06 % | 120.000 |
| nombre con apóstrofo | 0,40 % | 0,37 % | 120.000 |
| nombre con guion o punto | 2,10 % | 2,14 % | 120.000 |
| iOS, dado celular (ancla 20,72 %) | 20,72 % | 20,72 % | 67.330 |
| Windows, dado escritorio (ancla 85,02 %) | 85,02 % | 85,12 % | 51.087 |
| celular, dado que llega por Google (ancla 49,12 %) | 49,12 % | 48,88 % | 36.490 |
| Smart Punctuation, dado iOS o iPadOS | 95,00 % | 94,79 % | 14.891 |

## COBERTURA
pares 514/514 ; arcos sorteo 31/61, total 61/61 ; superficies sorteo 23/37, total 35/37 ; faltan ['/servicios/tiendas-online', '/servicios/desarrollo-software-a-medida']

## TABLA_USUARIOS
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

## TRAZAS

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

## FORZADAS
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
