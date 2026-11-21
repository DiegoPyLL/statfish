# Expresiones y plantillas

Las condiciones, probabilidades y valores de `modelo.toml` son expresiones: un subconjunto seguro de
Python. El motor valida cada una sobre `ast` antes de compilarla, así que una expresión que se sale de la
lista es un error de `validar`, no una ejecución.

## Qué se permite

| Elemento | Ejemplo |
|---|---|
| Atributos del usuario | `canal`, `js_off` |
| Argumentos y locales del estado | `intento`, `q` |
| Parámetros | `p.movil_si_redes` |
| Valor de una distribución | `d.sistema_movil.ios` |
| Números, textos y `True`/`False` | `0.01`, `'redes'` |
| Comparaciones | `==`, `!=`, `<`, `<=`, `>`, `>=` |
| Pertenencia | `in`, `not in`, con tuplas o listas literales: `sistema in ('ios', 'ipados')` |
| Lógica | `and`, `or`, `not` |
| Aritmética | `+`, `-`, `*`, `/` y el signo `-x` |
| Condicional | `x if c else y` |
| Funciones | `min(a, b, …)` y `max(a, b, …)` |

No se permite nada más: ni llamadas a otras funciones, ni subíndices, ni `**`, ni comprensiones, ni
f-strings, ni lambdas, ni atributos fuera de `p.` y `d.`. Tampoco se permiten nombres que empiecen con `_`.

## Qué puede usar cada expresión

| Dónde | Nombres disponibles |
|---|---|
| Casos de una variable (`si`, `valor`, `prob`, `dist`) | Las variables declaradas **antes**; `p.` y `d.` |
| `transformar` | `x`, el valor sorteado, más lo anterior |
| Estados (`si`, `prob`, `con`, `locales`) | Todas las variables, los `args` del estado y sus `locales` (en orden) |
| Perfiles, factores, restricciones, superficies (`usuario`) | Todas las variables |
| Métricas | Los ids de los desenlaces |
| `fidelidad.declarada` | Solo `p.`, `d.` y números |
| `aplica_si` de un patrón | `rasgos`, `formularios`, `paginas`, `origin_trial`, `idioma` y `pais` |

Las variables con `relato = true` no se pueden usar en la cadena.

**Sumas y orden.** La aritmética es la de Python, de izquierda a derecha: `1 - a - b` es `(1 - a) - b`. Si
una probabilidad se escribe distinto, por ejemplo `1 - (a + b)`, el resultado puede cambiar en el último
dígito. Para reproducir un modelo anterior, copia las expresiones tal cual.

## Plantillas de texto

`accion`, `arco`, `regla`, `nombre` y `superficies` son plantillas: texto fijo con expresiones entre llaves.

```toml
accion = "llega a {'/' if destino == 'home' else ruta_servicio}"
nombre = "Envío por correo{' (2.º intento)' if intento == 2 else ''}"
regla = "{causa}"
```

- `{{` y `}}` escriben una llave literal.
- Una plantilla de `regla` que da texto vacío equivale a no tener regla.

## Errores comunes

- **`usa «x», que no es una variable definida antes`:** mueve la variable que se usa más arriba.
- **`las ramas suman 0.999…`:** alguna rama falta o una probabilidad está mal compuesta. Las ramas
  complementarias se escriben como `1 - q` y `q`, no con valores redondeados.
- **`probabilidades fuera de [0, 1]` con parámetros sorteados:** una expresión del tipo `1 - a - b` puede
  quedar negativa en los extremos. Usa `max(1 - a - b, 0)` solo si el caso lo justifica: cambia el modelo.
