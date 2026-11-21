---
name: calibrar
description: Actualiza los parámetros de una corrida de Statfish con conteos reales (sin datos personales) en forma conjugada, Beta y Dirichlet, y muestra cuánto cambian el prior y las métricas.
argument-hint: "<carpeta de la corrida> [archivo de conteos]"
disable-model-invocation: true
---

# Calibrar con conteos reales

El motor es `statfish`, que está en el PATH con el plugin activo. Si no responde, usa
`python3 "${CLAUDE_SKILL_DIR}/../../bin/statfish"`.

La calibración corrige los priors con datos. **Solo acepta conteos agregados**: sin IP, sin correo, sin
contenido y sin identificadores. Si te pasan registros con datos personales, agrégalos tú en conteos y no
copies los registros a la corrida.

1. Ubica la corrida en `$ARGUMENTS` y lee su `modelo.toml`: qué parámetros y distribuciones existen y qué
   significa cada uno (`texto`).
2. Arma `conteos.toml`, asignando cada conteo al parámetro que mide.
   - Para un parámetro binario: cuántos casos salieron sí (`exitos`) y cuántos no (`fracasos`), dentro de
     la población que el parámetro condiciona.
   - Para una distribución: cuántos casos cayeron en cada valor (`n`).

   ```toml
   [[conteos]]
   parametro = "token_no_listo_normal"
   exitos = 4         # envíos con token vacío
   fracasos = 996     # envíos con token
   fuente = "contadores del Worker, 2026-12-01 a 2026-12-31"

   [[conteos]]
   distribucion = "canal"
   n = { google = 120, articulo = 40, recomendacion = 60, redes = 50, directo = 20, ia = 30 }
   fuente = "una línea por consulta real, diciembre 2026"
   ```

   Si un conteo no calza exacto con la definición del parámetro, por ejemplo porque cuenta otra población,
   dilo y no lo fuerces.
3. Corre `statfish calibrar <corrida> --conteos conteos.toml`. Escribe `calibracion.toml`, con los
   posteriores, y `salida/calibracion.json`, con el prior y el posterior de cada parámetro y el efecto en las
   métricas.
4. Corre `statfish correr <corrida>`. El informe queda calibrado y el manifiesto registra `calibracion.toml`.
5. Informa:
   - qué parámetros se movieron y cuánto;
   - qué métricas cambiaron;
   - qué tan dependiente de los supuestos era el informe anterior, que se mide por la diferencia entre prior
     y posterior.

   Un parámetro con mucho μ* en la sensibilidad y sin conteos es el próximo dato que conviene medir.
