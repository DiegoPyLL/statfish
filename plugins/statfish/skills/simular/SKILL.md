---
name: simular
description: Simula usuarios de un producto a partir de su código para responder quién no logra qué, en qué paso y por qué, con cifras reproducibles. Recorre el repo con evidencia archivo:línea, arma una red de perfiles y una cadena de uso, crea usuarios con cobertura por pares y genera el informe con el motor statfish, sin que un LLM muestree. Úsalo cuando pidan simular usuarios o personas sintéticas desde el código, encontrar fricciones de un flujo (contacto, registro, checkout, formularios), estimar qué cambia si se arregla algo, o correr Statfish en un repo.
argument-hint: "[pregunta de la corrida]"
---

# Statfish: simular usuarios desde el código

Tú lees el código, verbalizas priors y escribes la lectura. El motor `statfish` muestrea, calcula y arma el
informe. Esa división es el método: el LLM rinde leyendo código y describiendo distribuciones, y falla
muestreando y prediciendo acciones (ver `../../referencias/metodo.md`).

**El motor.** `statfish` queda en el PATH mientras el plugin está activo. Si no responde, usa
`python3 "${CLAUDE_SKILL_DIR}/../../bin/statfish"`. Necesita Python 3.11 o más y no usa la red.

**Referencias.** Cárgalas al llegar a la etapa que las usa:

| Archivo | Para qué |
|---|---|
| `../../referencias/metodo.md` | Por qué cada etapa, con su técnica y su fuente |
| `../../referencias/formato-modelo.md` | El esquema de `modelo.toml`, con ejemplos |
| `../../referencias/expresiones.md` | Expresiones y plantillas permitidas |
| `../../referencias/formulas.md` | F1 a F15, tal como las calcula el motor |
| `../../referencias/fuentes.md` | Registro de anclas y literatura |
| `../../referencias/informe.md` | Marcadores, `lectura.md`, `hallazgos.toml` e issues |

El caso Volutus completo está en `ejemplos/volutus/` del repo del plugin: es la mejor guía de cómo se ve
cada archivo terminado.

## Reglas que no se negocian

1. **Solo escribes en la carpeta de la corrida** (`<repo>/statfish/<fecha>-<slug>/`). No tocas el código del
   repo analizado.
2. **Sin cita no hay regla.** Toda regla, variable con soporte y patrón presente lleva evidencia
   `{ cita = "archivo:línea", extracto = "texto citado" }`. El extracto es texto literal de esas líneas.
3. **El LLM no muestrea ni elige acciones.** Cada peso es un ancla pública o un prior verbalizado (p10, p50,
   p90). Los usuarios, las trazas y los agregados los calcula el motor con su semilla.
4. **Ninguna cifra a mano.** En `lectura.md` y `hallazgos.toml` las cifras van como marcadores
   `{{ruta|filtro}}`. En tu respuesta, copia las cifras del `informe.md` generado.
5. **Las cifras describen el modelo, no el mercado.** Preséntalas como prior con intervalo, nunca como
   pronóstico.
6. **Nada hacia afuera sin confirmación.** No crees issues, commits ni PRs, ni consultes fuentes pagadas,
   sin que el usuario lo confirme.

## Etapas

Lleva una lista de tareas con las etapas. Cada una deja un archivo en la corrida y se cierra con un comando
del motor.

### 0. Pregunta y contexto

1. Acuerda la pregunta en una frase: quién no logra qué, en qué paso y por qué. Si llega como argumento
   (`$ARGUMENTS`), úsala. Pregunta el país y el público si no son obvios.
2. Crea la corrida:

   ```bash
   statfish contexto <repo> --slug <slug> --pregunta "…" --pais CL --publico "…"
   ```

   Deja `contexto.toml` (stack detectado, commit, cambios locales) y las plantillas. Si el repo tiene cambios
   locales sin commit, avísalo: la evidencia queda atada a un commit.

### 1. Recorrido

1. Lee primero el **índice**: rutas o páginas, formularios, endpoints, validaciones, límites y flags. Después
   haz la **lectura dirigida** por la pregunta. No leas el repo entero.
2. Corre `statfish patrones <corrida> --buscar`. Revisa cada patrón aplicable y regístralo en
   `recorrido.toml` como `presente`, `ausente` o `no_verificable`, con evidencia. Las hipótesis
   `descartada` del catálogo no se proponen sin evidencia nueva.
3. Escribe en `recorrido.toml`:
   - la bitácora (qué leíste, líneas y bytes);
   - las superficies, las entradas, el servidor y el entorno;
   - las hipótesis que el código descartó;
   - lo que el código no dice.
4. Corre `statfish evidencia <corrida>` hasta que todas las citas estén vigentes. Si falta un extracto, el
   comando sugiere uno.

### 2. Variables

1. En `modelo.toml`, declara cada variable con su **soporte** (`valores`, del código) y su evidencia.
2. Marca `relato = true` en las que el código no usa (rubro, región, edad): no pueden tocar el flujo.
3. Declara las restricciones duras (`[[restricciones]]`).
4. Corre `statfish validar <corrida>`.

### 3. Probabilidades

1. **Anclas.** Corre `statfish anclas --pais <país> --corrida <corrida> --copiar`. Si una falta o venció,
   consulta la fuente (su `plantilla_url`) y guarda la copia en `anclas/` con el formato del registro. Después
   propón sumarla al registro del plugin. Una distribución anclada lleva `fuente = "ancla:<id>"`.
2. **Sin ancla: K = 5 elicitaciones independientes.** Lanza el agente `statfish:elicitador` cinco veces, en
   paralelo, con el mismo mensaje y sin respuestas previas. El mensaje lleva tres cosas:
   - el contexto (producto, país, público, pregunta);
   - por cada parámetro: id, definición exacta (de quién, condicionado a qué) y su evidencia con extracto;
   - por cada distribución: id, valores y evidencia.

   Guarda cada respuesta, tal cual, como `elicitacion/k1.json` … `k5.json`.
3. Corre `statfish elicitar combinar <corrida> --toml` y pasa los bloques que imprime a `modelo.toml`
   (`fuente = "prior:elicitacion"`). Si alguna divergencia de Jensen-Shannon supera 0,05, revisa la
   definición, que suele estar ambigua, o busca un ancla.

### 4 a 6. Perfiles, usuarios y flujos

1. **Perfiles:** predicados en orden, donde se aplica el primero que calza y el último es `si = "True"`.
2. **Cadena de uso:** estados con argumentos, casos y ramas. Cada rama declara su probabilidad, su destino
   (otro estado o `FIN:<desenlace>`), la acción, la regla y su evidencia. El orden de las ramas importa.
3. **Recorrido cognitivo:** cada regla de fricción lleva sus cuatro respuestas (`cw`) y una `nota_cw` que
   explique cada «no» o «en parte».
4. **Cobertura:**
   - `[[factores]]`: de 3 a 13, donde haya interacción conocida;
   - `[[superficies]]`: con su clase de equivalencia;
   - `[cobertura.aplanada]`: lo raro inflado.
5. **Hipótesis:** solo cambios de parámetros. Un arreglo es un interruptor (`interruptor = true`) que las ramas
   leen como `p.arreglo_x`.
6. Itera con `statfish validar` y `statfish correr <corrida> --rapido`.
7. **Relatos:** con los usuarios ya sorteados, escribe una línea por usuario solo con sus atributos en
   `relatos.toml`, con la `huella` que trae `salida/usuarios.json`. Primero la estructura, después el
   relato.

### 7. Lectura

1. Escribe `lectura.md` y `hallazgos.toml` con marcadores (ver `../../referencias/informe.md`). Un hallazgo que
   merece issue lleva `titulo` y `cuerpo`.
2. Corre `statfish correr <corrida>`, la corrida completa sin `--rapido`. Escribe `informe.md`,
   `salida/issues/*.md` y `manifiesto.json`. Si un marcador no se resuelve, el comando lo dice.
3. Corre `statfish reproducir <corrida>`: debe decir «los mismos bytes».

### 8. Calibración

Si existen conteos reales sin datos personales, sigue `/statfish:calibrar`.

## Al terminar

Responde con:

- la pregunta;
- las tres fricciones principales, cada una con su evidencia;
- las cifras clave, copiadas del informe, con su intervalo;
- lo que no se puede afirmar, en especial los niveles que dependen de priors de intención;
- la ruta de `informe.md`.

Ofrece redactar los issues desde `salida/issues/`. Créalos solo si el usuario lo confirma, uno por uno.
