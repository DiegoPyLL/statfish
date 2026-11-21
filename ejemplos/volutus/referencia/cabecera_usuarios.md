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
