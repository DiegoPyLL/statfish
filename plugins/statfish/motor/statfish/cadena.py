"""Cadena de Markov de uso: ramas por estado, absorción exacta (F7), atribución (F8), trazas y arcos.

Cada estado se compila a una función que, para un usuario y unos parámetros, devuelve sus ramas:
(probabilidad, destino, acción, regla, arco, superficies). El destino es otro estado
(id, argumentos) o un desenlace (FIN, id).
"""
from . import expresiones as ex

FIN = '§'


class Ciclo(Exception):
    """La suma por caminos pasó la profundidad máxima: hay un ciclo o un camino muy largo."""


class ErrorCadena(Exception):
    """Un error al evaluar el modelo para un usuario (con el estado donde ocurrió)."""


def _py(a, locales):
    return ex.a_python(a, locales=locales, prefijo='l_')


def _pl(pl_texto, locales):
    return ex.plantilla_a_python(pl_texto, locales=locales, prefijo='l_')


def generar_cadena(modelo, textos):
    """Código de una función por estado. `textos` da el texto crudo de cada plantilla."""
    L = []
    nombres_func = {}
    for n, (sid, e) in enumerate(modelo.estados.items()):
        f = f'_e{n}'
        nombres_func[sid] = f
        locs_estado = list(e.args) + [k for k, _ in e.locales]
        L.append(f'def {f}(u, P, D, A):  # {sid}')
        if e.args:
            destino = ', '.join(f'l_{a}' for a in e.args)
            L.append(f'    {destino}{"," if len(e.args) == 1 else ""} = A')
        for k, a in e.locales:
            L.append(f'    l_{k} = {_py(a, locs_estado)}')
        for i, c in enumerate(e.casos):
            locs = locs_estado + [k for k, _ in c.locales]
            L.append(f'    if {_py(c.si, locs)}:')
            for k, a in c.locales:
                L.append(f'        l_{k} = {_py(a, locs)}')
            L.append('        _r = []')
            for j, r in enumerate(c.ramas):
                s = '        '
                if r.si is not None:
                    L.append(f'{s}if {_py(r.si, locs)}:')
                    s += '    '
                L.append(f'{s}_t = {_pl(textos[(sid, i, j, "accion")], locs)}')
                arco = _pl(textos[(sid, i, j, 'arco')], locs) if r.arco else '_t'
                regla = _pl(textos[(sid, i, j, 'regla')], locs) if r.regla else 'None'
                sups = ', '.join(_pl(t, locs) for t in textos[(sid, i, j, 'superficies')])
                sups = f'({sups},)' if sups else '()'
                L.append(f'{s}_r.append(({_py(r.prob, locs)}, {_destino(modelo, r, locs)}, _t, '
                         f'({regla}) or None, {arco}, {sups}))')
            L.append('        return _r')
        L.append(f'    raise SinCaso({sid!r})')
        L.append('')
        # Nombre legible y superficies del estado.
        L.append(f'def {f}_nombre(u, A):')
        if e.args:
            destino = ', '.join(f'l_{a}' for a in e.args)
            L.append(f'    {destino}{"," if len(e.args) == 1 else ""} = A')
        L.append(f'    return {_pl(textos[(sid, "nombre")], list(e.args))}')
        L.append('')
        L.append(f'def {f}_sup(u, A):')
        if e.args:
            destino = ', '.join(f'l_{a}' for a in e.args)
            L.append(f'    {destino}{"," if len(e.args) == 1 else ""} = A')
        sups = ', '.join(_pl(t, list(e.args)) for t in textos[(sid, 'superficies')])
        L.append(f'    return ({sups},)' if sups else '    return ()')
        L.append('')
    return '\n'.join(L) + '\n', nombres_func


def _destino(modelo, r, locs):
    if r.va.startswith('FIN:'):
        return repr((FIN, r.va[4:]))
    con = {k: _py(a, locs) for k, a in r.con}
    if r.va.startswith('$'):
        items = ', '.join(f'{k!r}: {v}' for k, v in con.items())
        return f'_dest(l_{r.va[1:]}, {{{items}}})'
    dest = modelo.estados[r.va]
    args = []
    for a in dest.args:
        args.append(con[a] if a in con else repr(dest.por_defecto[a]))
    tupla = '(' + ', '.join(args) + (',)' if len(args) == 1 else ')') if args else '()'
    return f'({r.va!r}, {tupla})'


def textos_de(modelo):
    """Los textos crudos de las plantillas de la cadena, tal como vienen del TOML."""
    textos = {}
    for sid, t in zip(modelo.estados, modelo.crudo.get('estados', [])):
        assert t['id'] == sid
        textos[(sid, 'nombre')] = t.get('nombre', sid)
        textos[(sid, 'superficies')] = list(t.get('superficies', []))
        casos = [{'ramas': t['ramas']}] if 'ramas' in t else t.get('casos', [])
        for i, c in enumerate(casos):
            for j, r in enumerate(c.get('ramas', [])):
                textos[(sid, i, j, 'accion')] = r.get('accion', '')
                textos[(sid, i, j, 'arco')] = r.get('arco')
                textos[(sid, i, j, 'regla')] = r.get('regla')
                textos[(sid, i, j, 'superficies')] = list(r.get('superficies', []))
    return textos


class SinCaso(Exception):
    """Ningún caso del estado calzó con el usuario."""


class Cadena:
    """La cadena compilada de un modelo."""

    def __init__(self, modelo):
        self.modelo = modelo
        self.inicio = (modelo.cadena['inicio'], ())
        ini = modelo.estados[modelo.cadena['inicio']]
        if ini.args:
            self.inicio = (ini.id, tuple(ini.por_defecto[a] for a in ini.args))
        self.fricciones = frozenset(modelo.fricciones)
        self.con_friccion = dict(modelo.cadena['con_friccion'])
        self.atribuibles = frozenset(modelo.cadena['atribuibles'])
        self.profundidad = modelo.cadena['profundidad_maxima']
        self.codigo, nombres = generar_cadena(modelo, textos_de(modelo))
        entorno = dict(ex.ENTORNO)
        entorno.update({'_s': str, '_dest': self._dest, 'SinCaso': SinCaso})
        exec(compile(self.codigo, f'<cadena: {modelo.nombre or "modelo"}>', 'exec'), entorno)
        self.funcs = {sid: entorno[f] for sid, f in nombres.items()}
        self.nombres = {sid: entorno[f + '_nombre'] for sid, f in nombres.items()}
        self.sups = {sid: entorno[f + '_sup'] for sid, f in nombres.items()}
        self.reglas = modelo.reglas

    def _dest(self, sid, con):
        e = self.modelo.estados.get(sid)
        if e is None:
            raise ErrorCadena(f'destino «{sid}» no es un estado')
        try:
            return (sid, tuple(con[a] if a in con else e.por_defecto[a] for a in e.args))
        except KeyError as x:
            raise ErrorCadena(f'al ir a {sid} falta el argumento {x}') from None

    def ramas(self, u, theta, s, cache=None):
        if cache is not None:
            r = cache.get(s)
            if r is not None:
                return r
        try:
            r = self.funcs[s[0]](u, theta.P, theta.D, s[1])
        except (SinCaso, ErrorCadena):
            raise
        except Exception as e:
            raise ErrorCadena(f'estado {s[0]}{s[1]!r}: {type(e).__name__}: {e}') from e
        if cache is not None:
            cache[s] = r
        return r

    # ---------------------------------------------------------------- F7 + F8
    def evaluar(self, u, theta):
        """Probabilidad exacta de cada desenlace y su atribución a la última regla de fricción."""
        try:
            return self._suma_por_caminos(u, theta)
        except Ciclo:
            return self._absorcion_lineal(u, theta)

    def _suma_por_caminos(self, u, theta):
        acum = {}
        por_regla = {}
        cache = {}
        fr, conf, atrib, maxp = self.fricciones, self.con_friccion, self.atribuibles, self.profundidad

        def rec(s, prob, causa, prof):
            if prof > maxp:
                raise Ciclo()
            rs = cache.get(s)
            if rs is None:
                rs = self.ramas(u, theta, s)
                cache[s] = rs
            for p, s2, _, regla, _, _ in rs:
                if p <= 0:
                    continue
                c2 = regla if regla in fr else causa
                if s2[0] == FIN:
                    d = s2[1]
                    if c2 and d in conf:
                        d = conf[d]
                    acum[d] = acum.get(d, 0.0) + prob * p
                    if d in atrib:
                        k = (c2, d)
                        por_regla[k] = por_regla.get(k, 0.0) + prob * p
                else:
                    rec(s2, prob * p, c2, prof + 1)

        rec(self.inicio, 1.0, None, 0)
        return acum, por_regla

    def _absorcion_lineal(self, u, theta):
        """B = (I − Q)⁻¹R sobre estados aumentados con la última fricción (F7, F8)."""
        fr, conf, atrib = self.fricciones, self.con_friccion, self.atribuibles
        cache = {}
        inicio = (self.inicio, None)
        indice = {inicio: 0}
        orden = [inicio]
        transiciones = []
        absorbentes = {}
        i = 0
        while i < len(orden):
            s, causa = orden[i]
            fila_q, fila_r = {}, {}
            for p, s2, _, regla, _, _ in self.ramas(u, theta, s, cache):
                if p <= 0:
                    continue
                c2 = regla if regla in fr else causa
                if s2[0] == FIN:
                    d = s2[1]
                    if c2 and d in conf:
                        d = conf[d]
                    k = (d, c2)
                    absorbentes.setdefault(k, len(absorbentes))
                    fila_r[k] = fila_r.get(k, 0.0) + p
                else:
                    k = (s2, c2)
                    if k not in indice:
                        indice[k] = len(orden)
                        orden.append(k)
                    fila_q[indice[k]] = fila_q.get(indice[k], 0.0) + p
            transiciones.append((fila_q, fila_r))
            i += 1
        n = len(orden)
        # (I − Q)ᵀ x = e₀  →  x = visitas esperadas desde el inicio.
        A = [[0.0] * n for _ in range(n)]
        for fi, (fila_q, _) in enumerate(transiciones):
            A[fi][fi] += 1.0
            for j, p in fila_q.items():
                A[j][fi] -= p
        b = [0.0] * n
        b[0] = 1.0
        x = resolver(A, b)
        acum, por_regla = {}, {}
        for fi, (_, fila_r) in enumerate(transiciones):
            for (d, c2), p in fila_r.items():
                v = x[fi] * p
                acum[d] = acum.get(d, 0.0) + v
                if d in atrib:
                    por_regla[(c2, d)] = por_regla.get((c2, d), 0.0) + v
        return acum, por_regla

    # ---------------------------------------------------------------- trazas
    def trazar(self, u, theta, rng, forzar=None, limite=500):
        """Una traza sorteada (o forzada por índices de rama): pasos, desenlace y P(camino)."""
        s = self.inicio
        pasos = []
        causa = None
        prob = 1.0
        i = 0
        cache = {}
        while True:
            opciones = [o for o in self.ramas(u, theta, s, cache) if o[0] > 0]
            if not opciones:
                raise ErrorCadena(f'estado {s[0]} sin ramas con probabilidad positiva')
            if forzar is not None:
                j, x = forzar[i], None
            else:
                x = rng.random()
                acc = 0.0
                j = len(opciones) - 1
                for idx, o in enumerate(opciones):
                    acc += o[0]
                    if x < acc:
                        j = idx
                        break
            p, s2, accion, regla, arco, sups_rama = opciones[j]
            prob *= p
            if regla in self.fricciones:
                causa = regla
            r = self.reglas.get(regla) if regla in self.fricciones else None
            pasos.append({
                'estado': self.nombres[s[0]](u, s[1]),
                'sorteo': None if x is None else round(x, 3),
                'prob': round(p, 4),
                'accion': accion,
                'regla': regla,
                'evidencia': [e['cita'] for e in self.reglas[regla].evidencia] if regla in self.reglas else None,
                'cw': list(r.cw) if r else ['sí', 'sí', 'sí', 'sí'],
                'nota_cw': r.nota_cw if r else None,
                'arco': [s[0], arco],
                'superficies': list(self.sups[s[0]](u, s[1])) + list(sups_rama),
            })
            i += 1
            if s2[0] == FIN:
                d = s2[1]
                if causa and d in self.con_friccion:
                    d = self.con_friccion[d]
                return pasos, d, prob
            s = s2
            if i > limite:
                raise ErrorCadena('la traza pasó el límite de pasos: revisa los ciclos de la cadena')

    def arcos_alcanzables(self, u, theta):
        """Todos los arcos (estado, arco) con probabilidad positiva para este usuario."""
        arcos = set()
        vistos = set()
        pila = [self.inicio]
        cache = {}
        while pila:
            s = pila.pop()
            if s in vistos:
                continue
            vistos.add(s)
            for p, s2, _, _, arco, _ in self.ramas(u, theta, s, cache):
                if p <= 0:
                    continue
                arcos.add((s[0], arco))
                if s2[0] != FIN and s2 not in vistos:
                    pila.append(s2)
        return arcos

    def mejor_camino(self, u, theta, arco):
        """F15: índices de rama del camino más probable que pasa por `arco`, y su probabilidad."""
        mejor = [None, 0.0]
        cache = {}
        arco = tuple(arco)

        def rec(s, idx, prob, visto, en_camino, prof):
            if prof > self.profundidad:
                return
            opciones = [o for o in self.ramas(u, theta, s, cache) if o[0] > 0]
            for j, (p, s2, _, _, a, _) in enumerate(opciones):
                v2 = visto or (s[0], a) == arco
                if s2[0] == FIN:
                    if v2 and prob * p > mejor[1]:
                        mejor[0], mejor[1] = idx + [j], prob * p
                elif s2 not in en_camino:
                    rec(s2, idx + [j], prob * p, v2, en_camino | {s2}, prof + 1)

        rec(self.inicio, [], 1.0, False, frozenset([self.inicio]), 0)
        return (mejor[0], mejor[1]) if mejor[0] else None


def resolver(A, b):
    """Eliminación de Gauss con pivoteo parcial (sistemas chicos; solo biblioteca estándar)."""
    n = len(A)
    M = [fila[:] + [b[i]] for i, fila in enumerate(A)]
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[piv][c]) < 1e-15:
            raise ErrorCadena('la cadena no es absorbente: hay un ciclo del que no se sale')
        M[c], M[piv] = M[piv], M[c]
        pc = M[c][c]
        for r in range(c + 1, n):
            f = M[r][c] / pc
            if f:
                filar, filac = M[r], M[c]
                for k in range(c, n + 1):
                    filar[k] -= f * filac[k]
    x = [0.0] * n
    for r in range(n - 1, -1, -1):
        s = M[r][n] - sum(M[r][k] * x[k] for k in range(r + 1, n))
        x[r] = s / M[r][r]
    return x
