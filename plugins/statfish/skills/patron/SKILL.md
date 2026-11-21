---
name: patron
description: Convierte un hallazgo confirmado de una corrida de Statfish en una entrada del catálogo compartido de patrones (datos/patrones), con su regla genérica, cómo detectarlo y sus parámetros por defecto, y prepara el cambio para revisión.
argument-hint: "<carpeta de la corrida> <id del hallazgo>"
disable-model-invocation: true
---

# Promover un hallazgo al catálogo

El catálogo vive en el repo del plugin, en `plugins/statfish/datos/patrones/`. Con cada proyecto crece la
checklist del recorrido.

1. **Ubica el repo del plugin.** No edites la copia instalada en la caché de Claude Code: se pisa al
   actualizar. Pregunta la ruta de un clon de `DiegoPyLL/statfish`, o usa `${CLAUDE_PLUGIN_ROOT}/../..` si el
   plugin se cargó con `--plugin-dir`. Revisa que esté en una rama nueva y no en `main`.
2. **Lee el hallazgo** en `<corrida>/hallazgos.toml`. Su regla está en `modelo.toml` y su evidencia, en
   `salida/evidencia.json`. Debe estar `confirmado` o tener issue; si es `nuevo`, pide confirmarlo antes.
3. **Revisa si ya existe** un patrón parecido en `datos/patrones/`. Si existe, suma el caso a su
   `[[casos]]` en vez de duplicarlo.
4. **Escribe `datos/patrones/<ID>.toml`.** El id es `P-<NOMBRE-EN-MAYÚSCULAS>`; las hipótesis descartadas usan
   `N-…` y `tipo = "descartada"`. Lleva estas partes:
   - `aplica_si`: una expresión sobre el contexto. Puede usar `rasgos`, `formularios`, `paginas`,
     `origin_trial`, `idioma` y `pais`; los rasgos posibles están en `motor/statfish/contexto.py`.
   - `[deteccion]`:
     - `regex`: expresiones regulares de Python que encuentren candidatos en otros repos, no solo en este;
     - `pistas`: qué mirar y qué probar.
   - `[regla]`: el texto genérico, sin nombres del proyecto, más `friccion`, `cw` y `nota_cw`.
   - `[[parametros]]`: los priors que usó la corrida, con p50, p10, p90 y `fuente`.
   - `[[casos]]`: repo, commit, reglas, issue y fuentes.
5. **Verifica:**
   - que el TOML carga: `python3 -c "import tomllib; tomllib.load(open('<archivo>', 'rb'))"`;
   - que `statfish patrones <corrida>` lista el patrón nuevo;
   - que `python3 -m unittest` pasa desde `tests/`.
6. **Prepara el cambio:** muestra el diff y propón el mensaje de commit. Haz el commit y abre el PR solo si el
   usuario lo confirma.
