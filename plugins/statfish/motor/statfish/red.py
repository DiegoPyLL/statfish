"""Red de perfiles: muestreo ancestral con números aleatorios comunes (F4) y log p de cada usuario.

El modelo se traduce a una función de Python generada a partir de expresiones ya validadas
(expresiones.py). Cada variable aleatoria usa su propio uniforme, así que cambiar un peso no
reordena a las demás.
"""
import math

from . import expresiones as ex

_LOG_MIN = math.log(1e-300)


def _log(v):
    return math.log(v) if v > 1e-300 else _LOG_MIN


def _elegir(dist, x):
    acc = 0.0
    for v, p in dist:
        acc += p
        if x < acc:
            return v, p
    return dist[-1]


def _prob_de(dist, valor):
    for v, p in dist:
        if v == valor:
            return p
    return 0.0


class SinCaso(Exception):
    """Ningún caso calzó: el modelo no cubre a este usuario."""


def _py(a, locales=(), prefijo='l_'):
    return ex.a_python(a, locales=locales, prefijo=prefijo)


def _dist_codigo(k, lineas, sangria, modelo):
    """Líneas que dejan en `_d` la lista [(valor, p)] del caso `k`."""
    s = sangria
    if k.dist is not None:
        lineas.append(f'{s}_d = DL[{k.dist!r}]')
    else:
        items = ', '.join(f'({v!r}, {_py(e)})' for v, e in k.dist_inline)
        lineas.append(f'{s}_d = [{items}]')
    if k.inclinacion is not None:
        fac = ', '.join(f'{v!r}: {_py(e)}' for v, e in k.inclinacion)
        lineas.append(f'{s}_f = {{{fac}}}')
        lineas.append(f'{s}_w = [(_v, _q * _f.get(_v, 1.0)) for _v, _q in _d]')
        lineas.append(f'{s}_s = sum(_q for _, _q in _w)')
        lineas.append(f'{s}_d = [(_v, _q / _s) for _v, _q in _w]')


def generar_red(modelo):
    """Código de tres funciones: muestrear, muestrear con registro (para la fidelidad) y logp."""
    L = []
    for nombre, registro in (('_muestrear', False), ('_muestrear_reg', True)):
        L.append(f'def {nombre}(X, P, D, DL):')
        L.append('    u = {}')
        L.append('    lp = 0.0')
        if registro:
            L.append('    R = {}')
        for v in modelo.variables:
            L.append(f'    # {v.id}')
            for i, k in enumerate(v.casos):
                kw = 'if' if i == 0 else 'elif'
                L.append(f'    {kw} {_py(k.si)}:')
                s = '        '
                if k.tipo == 'valor':
                    L.append(f'{s}u[{v.id!r}] = {_py(k.valor)}')
                    if registro:
                        L.append(f'{s}R[{v.id!r}] = ({i}, None)')
                elif k.tipo == 'prob':
                    L.append(f'{s}_p = {_py(k.prob)}')
                    L.append(f'{s}_r = X[{v.uniforme}] < _p')
                    L.append(f'{s}u[{v.id!r}] = _r')
                    L.append(f'{s}lp += _log(_p if _r else 1 - _p)')
                    if registro:
                        L.append(f'{s}R[{v.id!r}] = ({i}, ((True, _p), (False, 1 - _p)))')
                else:
                    _dist_codigo(k, L, s, modelo)
                    L.append(f'{s}_v, _q = _elegir(_d, X[{v.uniforme}])')
                    if k.transformar is not None:
                        L.append(f'{s}_tf = lambda x: {_py(k.transformar, locales=("x",), prefijo="")}')
                        L.append(f'{s}_v = _tf(_v)')
                        L.append(f'{s}_q = sum(_q2 for _v2, _q2 in _d if _tf(_v2) == _v)')
                        if registro:
                            L.append(f'{s}_fd = {{}}')
                            L.append(f'{s}for _v2, _q2 in _d: _fd[_tf(_v2)] = _fd.get(_tf(_v2), 0.0) + _q2')
                            L.append(f'{s}R[{v.id!r}] = ({i}, tuple(_fd.items()))')
                    elif registro:
                        L.append(f'{s}R[{v.id!r}] = ({i}, tuple(_d))')
                    L.append(f'{s}u[{v.id!r}] = _v')
                    L.append(f'{s}lp += _log(_q)')
            L.append('    else:')
            L.append(f'        raise SinCaso({v.id!r})')
        L.append('    return (u, lp, R)' if registro else '    return (u, lp)')
        L.append('')

    # log p de un usuario ya fijado (para el peso p/q de la cobertura, F5).
    L.append('def _logp(u, P, D, DL):')
    L.append('    lp = 0.0')
    for v in modelo.variables:
        if not v.aleatoria:
            continue
        L.append(f'    # {v.id}')
        primero = True
        for i, k in enumerate(v.casos):
            kw = 'if' if primero else 'elif'
            primero = False
            L.append(f'    {kw} {_py(k.si)}:')
            s = '        '
            if k.tipo == 'valor':
                L.append(f'{s}pass')
            elif k.tipo == 'prob':
                L.append(f'{s}_p = {_py(k.prob)}')
                L.append(f'{s}lp += _log(_p if u[{v.id!r}] else 1 - _p)')
            else:
                _dist_codigo(k, L, s, modelo)
                if k.transformar is not None:
                    L.append(f'{s}_tf = lambda x: {_py(k.transformar, locales=("x",), prefijo="")}')
                    L.append(f'{s}lp += _log(sum(_q2 for _v2, _q2 in _d if _tf(_v2) == u[{v.id!r}]))')
                else:
                    L.append(f'{s}lp += _log(_prob_de(_d, u[{v.id!r}]))')
    L.append('    return lp')
    L.append('')

    # Perfiles: el primero que calza.
    L.append('def _perfil(u):')
    for p in modelo.perfiles:
        L.append(f'    if {_py(p["si"])}:')
        L.append(f'        return {p["id"]!r}')
    L.append('    return None')
    L.append('')
    # Factores de cobertura.
    L.append('def _factores(u):')
    items = ', '.join(f'{f["id"]!r}: {_py(f["expr"])}' for f in modelo.factores)
    L.append(f'    return {{{items}}}')
    L.append('')
    # Restricciones: devuelve los índices de las que se violan.
    L.append('def _restricciones(u):')
    L.append('    malas = []')
    for i, r in enumerate(modelo.restricciones):
        L.append(f'    if not {_py(r["expr"])}:')
        L.append(f'        malas.append({i})')
    L.append('    return malas')
    L.append('')
    # Superficies que dependen solo del usuario.
    L.append('def _superficies_usuario(u):')
    L.append('    s = []')
    for x in modelo.superficies:
        if x['usuario'] is not None:
            L.append(f'    if {_py(x["usuario"])}:')
            L.append(f'        s.append({x["id"]!r})')
    L.append('    return s')
    return '\n'.join(L) + '\n'


class Red:
    """La red compilada de un modelo."""

    def __init__(self, modelo):
        self.modelo = modelo
        self.n_uniformes = modelo.corrida['uniformes']
        self.codigo = generar_red(modelo)
        entorno = dict(ex.ENTORNO)
        entorno.update({'_log': _log, '_elegir': _elegir, '_prob_de': _prob_de, 'SinCaso': SinCaso,
                        'sum': sum, 'tuple': tuple})
        exec(compile(self.codigo, f'<red: {modelo.nombre or "modelo"}>', 'exec'), entorno)
        self._m = entorno['_muestrear']
        self._mr = entorno['_muestrear_reg']
        self._lp = entorno['_logp']
        self.perfil = entorno['_perfil']
        self.factores = entorno['_factores']
        self.restricciones = entorno['_restricciones']
        self.superficies_usuario = entorno['_superficies_usuario']

    def muestrear(self, X, theta):
        """Un usuario a partir de sus uniformes X: devuelve (atributos, log p)."""
        return self._m(X, theta.P, theta.D, theta.DL)

    def muestrear_con_registro(self, X, theta):
        """Igual, más el caso aplicado y la distribución declarada de cada variable."""
        return self._mr(X, theta.P, theta.D, theta.DL)

    def logp(self, u, theta):
        """log p de un usuario ya fijado, bajo theta."""
        return self._lp(u, theta.P, theta.D, theta.DL)

    def uniformes(self, rng, n):
        k = self.n_uniformes
        return [[rng.random() for _ in range(k)] for _ in range(n)]

    def uno(self, rng):
        return [rng.random() for _ in range(self.n_uniformes)]


def pares(f):
    """Los pares de valores de dos factores distintos que tiene un usuario (F6)."""
    ks = sorted(f)
    return {(a, str(f[a]), b, str(f[b])) for i, a in enumerate(ks) for b in ks[i + 1:]}
