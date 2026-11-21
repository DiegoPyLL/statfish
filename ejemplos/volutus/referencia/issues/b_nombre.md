Hallado en el caso de prueba de Statfish: recorrido del código de `main` @ `76b713a`, 20-11-2026, sin cambiar nada del repo. El detalle está en `docs/caso-volutus/` del repo `statfish`.

## Qué pasa

`NOMBRE_VALIDO` (`src/lib/contacto.js:89-91`) acepta letras, marcas, espacio y el apóstrofo recto. Se aplica en el contacto (`src/client.js:82-85` y `worker/index.js:99-101`) y en el brief (`src/comportamiento/brief/brief.js:350` y `worker/brief.js:292-294`).

1. **En iPhone y iPad no pasa ni «O'Higgins», el ejemplo del propio comentario.** Smart Punctuation, activo por defecto en iOS, convierte `'` en `’` (U+2019), que no es `\p{L}`, ni `\p{M}`, ni `'`. El aviso «Usa solo letras.» contradice lo que la persona ve, y el campo (`src/components/Contacto.jsx:121-130`) no tiene nada que lo evite. Es un comportamiento documentado de iOS ([ejemplo](https://github.com/candrikanich/recruiting-compass-ios/pull/281)). **Por confirmar en un iPhone real**: no se levantó el sitio.
2. **Guion y punto.** Jean-Baptiste y Marie-Claire (frecuentes en nombres de origen francés o haitiano), «Ma. José» o «M. Ignacia» reciben «Usa solo letras.».
3. **El nombre del negocio en el campo nombre**, como «Taller 2 Ruedas» o «Pinturas & Más», recibe el mismo aviso.

## Quién lo encontró

- **U27:** firma «Marie-Ange» en Safari para macOS. Recibe «Usa solo letras.», cambia su nombre y envía.
- **U15:** iPhone con apóstrofo en el apellido. En las trazas forzadas, se rinde o quita el apóstrofo.
- **U21:** sin JS y con guion. El envío nativo responde «Faltan datos o el correo no es válido…».

## Impacto (cifras del modelo, no del mercado)

Es la fricción **más robusta** del modelo: queda entre las tres mayores en el 98,5 % de 200 sorteos de los supuestos. Unos 9 de cada 1.000 visitantes pasan por este aviso antes de contactar, y cerca de 2 se van. El caso del apóstrofo en iPhone es raro, un 0,4 % de los nombres, pero es un error de corrección.

## Propuesta (para discutir, no implementada)

- [ ] Normalizar `’`, `‘` y `ʼ` a `'` antes de validar, en el navegador y en el Worker.
- [ ] Aceptar guion y punto. Quizás también dígitos y `&`: el riesgo real en el asunto son los caracteres de control, y `limpiar` ya los quita (`worker/comun.js:17-22`).
- [ ] Si queda algún aviso, que diga qué carácter no se acepta.
