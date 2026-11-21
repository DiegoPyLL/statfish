"""Población y usuarios: el agregado exacto, los representativos, los nombres sintéticos y la fidelidad."""
import math

from . import expresiones as ex


def compilar_metricas(modelo):
    """Cada métrica es una suma de desenlaces: f(desenlaces) → valor."""
    fs = []
    for x in modelo.metricas:
        fs.append((x['id'], ex.compilar(x['expr'].texto, atributos='o')))
    return fs


def metricas(fs, desenlaces):
    return {mid: f(desenlaces, None, None, None) for mid, f in fs}


def poblacion(red, cadena, modelo, theta, US, registro=None):
    """Desenlaces exactos de cada usuario, promediados. `registro` junta marginales y fidelidad."""
    desenlaces = list(modelo.cadena['desenlaces'])
    perfiles = [p['id'] for p in modelo.perfiles]
    tot = {}
    seg_masa = {}
    seg_des = {}
    regla = {}
    seg_regla = {}
    muestrear = red.muestrear_con_registro if registro is not None else red.muestrear
    for U in US:
        r = muestrear(U, theta)
        u = r[0]
        if registro is not None:
            registro.anotar(u, r[2])
        s = red.perfil(u)
        seg_masa[s] = seg_masa.get(s, 0) + 1
        acum, pr = cadena.evaluar(u, theta)
        sd = seg_des.setdefault(s, {})
        for d, p in acum.items():
            tot[d] = tot.get(d, 0.0) + p
            sd[d] = sd.get(d, 0.0) + p
        sr = seg_regla.setdefault(s, {})
        for k, p in pr.items():
            regla[k] = regla.get(k, 0.0) + p
            sr[k] = sr.get(k, 0.0) + p
    n = len(US)
    return {
        'desenlaces': {d: tot.get(d, 0.0) / n for d in desenlaces},
        'masa': {s: seg_masa.get(s, 0) / n for s in perfiles},
        'n_perfil': {s: seg_masa.get(s, 0) for s in perfiles},
        'por_perfil': {s: {d: seg_des.get(s, {}).get(d, 0.0) / max(seg_masa.get(s, 0), 1e-9)
                           for d in desenlaces} for s in perfiles},
        'por_regla': {k: v / n for k, v in regla.items()},
        'por_perfil_regla': {s: {k: v / max(seg_masa.get(s, 0), 1e-9) for k, v in seg_regla.get(s, {}).items()}
                             for s in perfiles},
        'sin_perfil': seg_masa.get(None, 0),
    }


class RegistroFidelidad:
    """Marginales y fidelidad (F12) del generador, sobre la población grande."""

    def __init__(self, modelo):
        self.modelo = modelo
        self.n = 0
        self.marginal = {v.id: {} for v in modelo.variables}
        self.casos = {}     # (variable, caso) → [n, {valor: suma declarada}, {valor: observados}]
        self.declaradas = []
        for f in modelo.fidelidad:
            self.declaradas.append({
                'texto': f['texto'],
                'expr': ex.compilar(f['expr'].texto),
                'dado': ex.compilar(f['dado'].texto) if f['dado'] is not None else None,
                'declarada': f['declarada'],
                'n': 0, 'si': 0,
            })

    def anotar(self, u, reg):
        self.n += 1
        for k, v in u.items():
            m = self.marginal.setdefault(k, {})
            m[v] = m.get(v, 0) + 1
        for var, (caso, dist) in reg.items():
            if dist is None:
                continue
            c = self.casos.get((var, caso))
            if c is None:
                c = self.casos[(var, caso)] = [0, {}, {}]
            c[0] += 1
            dec = c[1]
            for val, p in dist:
                dec[val] = dec.get(val, 0.0) + p
            obs = c[2]
            obs[u[var]] = obs.get(u[var], 0) + 1
        for d in self.declaradas:
            if d['dado'] is not None and not d['dado'](u, None, None, None):
                continue
            d['n'] += 1
            if d['expr'](u, None, None, None):
                d['si'] += 1

    def resultado(self, theta):
        """Tabla de fidelidad declarada y la revisión automática caso por caso (F12)."""
        declaradas = []
        for d in self.declaradas:
            p = ex.compilar(d['declarada'].texto)(None, theta.P, theta.D, None)
            obs = d['si'] / d['n'] if d['n'] else None
            declaradas.append({'variable': d['texto'], 'declarada': p, 'muestra': obs, 'n': d['n'],
                               'dentro': None if obs is None else fiel(p, obs, d['n'])})
        automaticas = []
        for (var, caso), (n, dec, obs) in self.casos.items():
            for val, suma in dec.items():
                p = suma / n
                o = obs.get(val, 0) / n
                automaticas.append({'variable': var, 'caso': caso + 1, 'valor': val, 'declarada': p,
                                    'muestra': o, 'n': n, 'dentro': fiel(p, o, n)})
        marginal = {k: {str(v): c / self.n for v, c in sorted(cnt.items(), key=lambda kv: (-kv[1], str(kv[0])))}
                    for k, cnt in self.marginal.items()}
        fuera = [a for a in automaticas if not a['dentro']]
        return {'declaradas': declaradas,
                'automatica': {'revisadas': len(automaticas), 'fuera': len(fuera),
                               'peor': sorted(automaticas, key=lambda a: -abs(a['declarada'] - a['muestra']))[:10],
                               'fuera_de_rango': fuera},
                'marginales': marginal}


def fiel(declarada, muestra, n):
    """F12: |declarada − muestra| ≤ 3·√(p(1−p)/n)."""
    if n == 0:
        return True
    return abs(declarada - muestra) <= 3 * math.sqrt(max(declarada * (1 - declarada), 0.0) / n) + 1e-12


def representativos(red, theta, rng, n):
    usuarios = []
    for _ in range(n):
        U = red.uno(rng)
        u, lp = red.muestrear(U, theta)
        usuarios.append({'u': u, 'U': U, 'tipo': 'representativo', 'peso': None, 'logp': lp})
    return usuarios


def nombrar(modelo, usuarios, rng, usados=None):
    """Nombres sintéticos: cada caso sortea, en orden, de sus listas y arma la plantilla.

    `usados` guarda los nombres ya dados, para seguir nombrando sin repetir en una segunda tanda.
    """
    conf = modelo.nombres
    if not conf:
        for x in usuarios:
            x['nombre'] = None
        return
    casos = [(ex.compilar(c['si'].texto), c) for c in conf['casos']]
    listas = conf['listas']
    usados = set() if usados is None else usados
    for x in usuarios:
        u = x['u']
        caso = next((c for f, c in casos if f(u, None, None, None)), None)
        if caso is None:
            x['nombre'] = None
            continue
        for _ in range(10_000):
            huecos = {}
            for hueco, lista in caso['sorteos']:
                huecos[hueco] = rng.choice(listas[lista])
            texto = caso['plantilla'].format_map(huecos)
            if texto not in usados:
                usados.add(texto)
                x['nombre'] = texto
                break
        else:
            x['nombre'] = None
