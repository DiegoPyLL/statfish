# Statfish

La alternativa de un solo agente a MiroFish. Un agente recorre el código de un producto con evidencia
`archivo:línea`, y un motor determinista arma con eso dos piezas: P(perfil), una red bayesiana, y P(flujo |
perfil), una cadena de Markov de uso. Después crea usuarios y los hace recorrer el producto.

Responde «¿quién no logra qué, en qué paso y por qué, y qué cambia si cambio el código?» con cifras
reproducibles, presentadas como prior con intervalo y nunca como pronóstico.

## Instalación

Se hace una vez por persona, cuando el repo esté en GitHub:

```bash
claude plugin marketplace add DiegoPyLL/statfish
claude plugin install statfish@statfish
```

Necesita Python 3.11 o más.

## Uso

En cualquier repo:

```text
/statfish:simular "¿Quién no logra contactar, en qué paso y por qué?"
```

Para recalcular una corrida sin Claude Code ni ningún LLM:

```bash
plugins/statfish/bin/statfish reproducir <repo>/statfish/<corrida>
```

El plugin, sus skills y sus comandos se describen en [plugins/statfish/README.md](plugins/statfish/README.md).

## Estructura

| Ruta | Qué es |
|---|---|
| `.claude-plugin/marketplace.json` | Este repo es el marketplace |
| `plugins/statfish/` | El plugin: skills, agente, motor, referencias, datos, plantillas y evals |
| `ejemplos/volutus/` | El caso Volutus migrado al formato de la herramienta, con sus salidas esperadas |
| `ejemplos/volutus/referencia/` | El script original del caso y sus salidas, rescatados del scratchpad |
| `tests/` | `python3 -m unittest` (no viajan con el plugin) |
| `docs/` | [Viabilidad](docs/viabilidad.md), [caso Volutus](docs/caso-volutus/recorrido.md) (histórico) y el [plan de la herramienta](docs/plan-herramienta.md) |

## Desarrollo

```bash
claude --plugin-dir ./plugins/statfish            # probar el plugin sin instalarlo
claude plugin validate ./ --strict                # marketplace
claude plugin validate ./plugins/statfish --strict
cd tests && python3 -m unittest                   # unos 4 s
STATFISH_LENTO=1 python3 -m unittest              # suma la corrida completa contra el script del caso
plugins/statfish/bin/statfish reproducir ejemplos/volutus
claude plugin eval ./plugins/statfish --scaffold --allow-tools Bash --runs 1 --no-publish
```

El ejemplo Volutus reproduce exacto el script del caso: `contacto_total = 0,2355817451354591` y
`perdida_por_codigo = 0,01271781635688427`, con 514 de 514 pares y 61 de 61 arcos.
