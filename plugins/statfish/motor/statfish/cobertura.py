"""Cobertura: pares de valores (F6, AETG voraz), arcos de la cadena (con F15) y superficies."""
import math

from .red import pares


def cubrir_pares(red, theta_p50, theta_q, rng, representativos, candidatos_universo, por_vuelta):
    """AETG voraz con candidatos de la red aplanada q.

    El universo de pares se estima con `candidatos_universo` usuarios de q. En cada vuelta se sortean
    `por_vuelta` candidatos y se elige el primero que cubre más pares nuevos. Cada elegido lleva su peso
    de importancia p/q (F5). Devuelve (universo, cubiertos, uniformes del universo, usuarios nuevos).
    """
    universo = set()
    candidatos = []
    for _ in range(candidatos_universo):
        U = red.uno(rng)
        u, _ = red.muestrear(U, theta_q)
        universo |= pares(red.factores(u))
        candidatos.append(U)
    cubiertos = set()
    for x in representativos:
        cubiertos |= pares(red.factores(x['u']))
    nuevos = []
    while not universo <= cubiertos:
        mejor, mejor_n, mejor_U = None, -1, None
        for _ in range(por_vuelta):
            U = red.uno(rng)
            u, _ = red.muestrear(U, theta_q)
            n = len(pares(red.factores(u)) - cubiertos)
            if n > mejor_n:
                mejor, mejor_n, mejor_U = u, n, U
        if mejor_n <= 0:
            break
        lq = red.muestrear(mejor_U, theta_q)[1]
        lp = red.logp(mejor, theta_p50)
        nuevos.append({'u': mejor, 'U': mejor_U, 'tipo': 'cobertura', 'peso': math.exp(lp - lq),
                       'logp': lp, 'nuevos_pares': mejor_n})
        cubiertos |= pares(red.factores(mejor))
    return universo, cubiertos, candidatos, nuevos


def universo_arcos(red, cadena, theta_p50, theta_q, candidatos):
    """Todos los arcos alcanzables desde usuarios de q, evaluados con los parámetros p50.

    Devuelve también los arcos de cada candidato, para sumar usuarios si alguno queda sin cubrir.
    """
    arcos = set()
    por_candidato = []
    for U in candidatos:
        u, _ = red.muestrear(U, theta_q)
        a = cadena.arcos_alcanzables(u, theta_p50)
        arcos |= a
        por_candidato.append((U, a))
    return arcos, por_candidato


def usuarios_para_arcos(red, theta_p50, theta_q, por_candidato, restantes):
    """Voraz: suma el candidato de q que alcanza más arcos sin cubrir, hasta que no quede ninguno.

    Solo se usa si ningún usuario con traza alcanza un arco del universo (F15 no tiene de dónde forzarlo).
    """
    nuevos = []
    restantes = set(restantes)
    while restantes:
        mejor, mejor_n = None, 0
        for U, a in por_candidato:
            n = len(a & restantes)
            if n > mejor_n:
                mejor, mejor_n = (U, a), n
        if mejor is None:
            break
        U, a = mejor
        u, lq = red.muestrear(U, theta_q)
        lp = red.logp(u, theta_p50)
        nuevos.append({'u': u, 'U': U, 'tipo': 'cobertura de arcos', 'peso': math.exp(lp - lq), 'logp': lp,
                       'nuevos_pares': None})
        restantes -= a
    return nuevos


def forzar_arcos(cadena, theta, usuarios, faltan):
    """F15: por cada arco que falta, el camino más probable que lo contiene entre los usuarios."""
    forzadas = []
    for arco in sorted(faltan):
        mejor = None
        for x in usuarios:
            camino = cadena.mejor_camino(x['u'], theta, arco)
            if camino and (mejor is None or camino[1] > mejor[2]):
                mejor = (x, camino[0], camino[1])
        if mejor:
            x, idx, pc = mejor
            pasos, d, _ = cadena.trazar(x['u'], theta, None, forzar=idx)
            forzadas.append({'id': x['id'], 'forzada': True, 'arco': list(arco), 'pasos': pasos,
                             'desenlace': d, 'prob_camino': pc})
    return forzadas


def superficies_de(red, usuario, pasos):
    """Superficies que toca una traza: las del estado, las de la rama, las reglas y las del usuario."""
    vistas = set()
    for p in pasos:
        vistas.update(p['superficies'])
        if p['regla']:
            vistas.add(p['regla'])
    vistas.update(red.superficies_usuario(usuario))
    return vistas


def universo_superficies(modelo):
    """Las superficies declaradas más cada regla, con su clase de equivalencia."""
    clases = {s['id']: s['clase'] for s in modelo.superficies}
    for r in modelo.reglas:
        clases.setdefault(r, 'regla ' + r)
    return clases


def resumen_superficies(clases, vistas_sorteo, vistas_total):
    todas = list(clases)
    por_clase = {}
    for s, c in clases.items():
        por_clase.setdefault(c, []).append(s)
    clases_cubiertas = [c for c, ss in por_clase.items() if any(s in vistas_total for s in ss)]
    return {
        'universo': todas,
        'vistas_sorteo': [s for s in todas if s in vistas_sorteo],
        'vistas_total': [s for s in todas if s in vistas_total],
        'faltan_sorteo': [s for s in todas if s not in vistas_sorteo],
        'faltan_total': [s for s in todas if s not in vistas_total],
        'clases': len(por_clase),
        'clases_cubiertas': len(clases_cubiertas),
        'faltan_por_clase': [{'superficie': s, 'clase': clases[s],
                              'cubierta_por': [x for x in por_clase[clases[s]] if x in vistas_total]}
                             for s in todas if s not in vistas_total],
    }
