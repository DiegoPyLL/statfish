"""Utilidades sin dependencias: escritura de TOML simple y formato de números en español."""
import datetime
import math
import re

_CLAVE_DESNUDA = re.compile(r'^[A-Za-z0-9_-]+$')


def _clave(k):
    return k if _CLAVE_DESNUDA.match(k) else _texto(k)


def _texto(s):
    s = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\t', '\\t')
    return f'"{s}"'


def _valor(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        if not math.isfinite(v):
            raise ValueError('TOML no admite NaN ni infinito aquí')
        return repr(v)
    if isinstance(v, str):
        return _texto(v)
    if isinstance(v, (datetime.date, datetime.datetime)):
        return v.isoformat()
    if isinstance(v, (list, tuple)):
        return '[' + ', '.join(_valor(x) for x in v) + ']'
    if isinstance(v, dict):
        return '{ ' + ', '.join(f'{_clave(k)} = {_valor(x)}' for k, x in v.items()) + ' }' if v else '{}'
    raise TypeError(f'tipo no admitido en TOML: {type(v).__name__}')


def a_toml(datos, comentario=None):
    """TOML de un dict con reglas fijas.

    Nivel superior: los escalares van primero; cada dict es una sección [a] y cada lista de dicts un
    arreglo de tablas [[a]]. Dentro de una sección, cada dict es una subsección [a.b]. Más adentro, los
    dicts van en línea.
    """
    lineas = []
    if comentario:
        lineas += [f'# {x}' if x else '#' for x in comentario.split('\n')]
    for k, v in datos.items():
        if not isinstance(v, dict) and not _es_arreglo_tablas(v):
            lineas.append(f'{_clave(k)} = {_valor(v)}')
    for k, v in datos.items():
        if isinstance(v, dict):
            _seccion(lineas, _clave(k), v)
        elif _es_arreglo_tablas(v):
            for t in v:
                lineas.append('')
                lineas.append(f'[[{_clave(k)}]]')
                for k2, v2 in t.items():
                    lineas.append(f'{_clave(k2)} = {_valor(v2)}')
    return '\n'.join(lineas).lstrip('\n') + '\n'


def _seccion(lineas, nombre, tabla):
    lineas.append('')
    lineas.append(f'[{nombre}]')
    for k, v in tabla.items():
        if not (isinstance(v, dict) and v):
            lineas.append(f'{_clave(k)} = {_valor(v)}')
    for k, v in tabla.items():
        if isinstance(v, dict) and v:
            lineas.append('')
            lineas.append(f'[{nombre}.{_clave(k)}]')
            for k2, v2 in v.items():
                lineas.append(f'{_clave(k2)} = {_valor(v2)}')


def _es_arreglo_tablas(v):
    return isinstance(v, list) and bool(v) and all(isinstance(x, dict) for x in v)


# --------------------------------------------------------------------------------------------
# Números en español: coma decimal y punto de miles.
# --------------------------------------------------------------------------------------------
def coma(texto):
    """1,234.5 → 1.234,5 y el signo menos tipográfico (−)."""
    return texto.replace(',', '§').replace('.', ',').replace('§', '.').replace('-', '−')


def pct_corto(x):
    """Porcentaje sin decimales de más: 70 %, 0,2 %, 12,5 %."""
    v = round(x * 100, 4)
    if v == int(v):
        return coma(f'{int(v)}')
    return coma(f'{v:.4f}'.rstrip('0').rstrip('.'))


def pct(x, d=1):
    return coma(f'{x * 100:,.{d}f}') + ' %'


def pp(x, d=2):
    return coma(f'{x * 100:,.{d}f}')


def mil(x, d=2):
    return coma(f'{x * 1000:,.{d}f}')


def dec(x, d=2):
    return coma(f'{x:,.{d}f}')


def num(x, cifras=3):
    if x == 0:
        return '0'
    return coma(f'{x:.{cifras}g}')


def entero(x):
    return coma(f'{int(round(x)):,}')


def cientifica(x, d=1):
    return f'{x:.{d}e}'.replace('.', ',').replace('e-', 'e−')
