"""Incertidumbre de los parámetros: F1, F2, F3, F9, F11 y F13 (referencias/formulas.md)."""
import math

from .modelo import KAPPA_POR_FUENTE


# --------------------------------------------------------------------------------------------
# F1. Beta desde (p10, p50, p90)
# --------------------------------------------------------------------------------------------
def beta_desde(p50, p10, p90):
    """σ = (p90 − p10)/2,563; var ≤ 0,95·m(1−m); κ = m(1−m)/var − 1; α = mκ, β = (1−m)κ (mínimo 0,05).

    Devuelve None si no hay rango (p10 = p90) o si m es 0 o 1: el parámetro queda fijo.
    """
    sd = (p90 - p10) / 2.563
    var = sd * sd
    tope = p50 * (1 - p50) * 0.95
    var = min(var, tope)
    if var <= 0:
        return None
    k = p50 * (1 - p50) / var - 1
    return max(p50 * k, 0.05), max((1 - p50) * k, 0.05)


def beta_media_var(a, b):
    s = a + b
    return a / s, a * b / (s * s * (s + 1))


# --------------------------------------------------------------------------------------------
# F2. Dirichlet(κ·p): κ según la fuente
# --------------------------------------------------------------------------------------------
def kappa_por_fuente(fuente):
    """ancla 200, prior 12 (de 10 a 15), definición o código 1.000."""
    return KAPPA_POR_FUENTE[fuente]


# --------------------------------------------------------------------------------------------
# Beta: función de distribución e inversa (para p10 y p90 de una Beta ajustada)
# --------------------------------------------------------------------------------------------
def _betacf(a, b, x):
    """Fracción continua de la beta incompleta (Lentz modificado)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return h


def beta_cdf(x, a, b):
    """I_x(a, b), la beta incompleta regularizada."""
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    ln = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log1p(-x)
    bt = math.exp(ln)
    if x < (a + 1) / (a + b + 2):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def beta_cuantil(q, a, b):
    """Inversa de I_x(a, b) por bisección (determinista, 80 pasos)."""
    lo, hi = 0.0, 1.0
    for _ in range(80):
        mid = (lo + hi) / 2
        if beta_cdf(mid, a, b) < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# --------------------------------------------------------------------------------------------
# F3. Mezcla de K elicitaciones
# --------------------------------------------------------------------------------------------
def combinar_binarias(elicitaciones):
    """Mezcla en partes iguales de K Betas (cada una por F1).

    p̄ es la media de las K; la varianza de la mezcla suma la de cada elicitación y la dispersión
    entre ellas (varianza total). κ sale por momentos, con el mismo tope de F1.
    """
    momentos = []
    for p10, p50, p90 in elicitaciones:
        ab = beta_desde(p50, p10, p90)
        if ab is None:
            momentos.append((p50, 0.0))
        else:
            momentos.append(beta_media_var(*ab))
    K = len(momentos)
    m = sum(x for x, _ in momentos) / K
    var = sum(v + x * x for x, v in momentos) / K - m * m
    var = min(max(var, 0.0), 0.95 * m * (1 - m))
    salida = {'k': K, 'p50': m, 'p50_por_k': [e[1] for e in elicitaciones],
              'jsd': jsd([[e[1], 1 - e[1]] for e in elicitaciones]) if K > 1 else None}
    if var <= 0:
        salida.update({'p10': m, 'p90': m, 'kappa': None, 'alfa': None, 'beta': None})
        return salida
    kappa = m * (1 - m) / var - 1
    a, b = max(m * kappa, 0.05), max((1 - m) * kappa, 0.05)
    salida.update({'kappa': kappa, 'alfa': a, 'beta': b,
                   'p10': beta_cuantil(0.10, a, b), 'p90': beta_cuantil(0.90, a, b)})
    return salida


def combinar_categoricas(elicitaciones, kappa_previo=12.0):
    """Mezcla de K vectores de probabilidad (cada uno con su κ o el del prior por defecto).

    p̄ = media de las K; κ = Σ p̄(1−p̄) / Σ var − 1, con var la varianza de la mezcla.
    """
    K = len(elicitaciones)
    valores = list(elicitaciones[0][0])
    vecs, kappas = [], []
    for probs, kappa in elicitaciones:
        vecs.append([float(probs[v]) for v in valores])
        kappas.append(kappa or kappa_previo)
    m = [sum(v[i] for v in vecs) / K for i in range(len(valores))]
    var = []
    for i in range(len(valores)):
        dentro = [v[i] * (1 - v[i]) / (k + 1) for v, k in zip(vecs, kappas)]
        var.append(sum(d + v[i] ** 2 for d, v in zip(dentro, vecs)) / K - m[i] ** 2)
    num = sum(x * (1 - x) for x in m)
    den = sum(max(x, 0.0) for x in var)
    kappa = num / den - 1 if den > 0 else 1000.0
    return {'k': K, 'valores': dict(zip(valores, m)), 'kappa': max(min(kappa, 1000.0), 2.0),
            'jsd': jsd(vecs) if K > 1 else None}


# --------------------------------------------------------------------------------------------
# F9. Cuantiles de S sorteos
# --------------------------------------------------------------------------------------------
def cuantil(ordenados, q):
    """q ≤ 0,5: el elemento ⌊q·S⌋; q > 0,5: el elemento S − 1 − ⌊(1−q)·S⌋ (simétrico)."""
    S = len(ordenados)
    if q <= 0.5:
        return ordenados[min(int(q * S), S - 1)]
    return ordenados[max(S - 1 - int((1 - q) * S), 0)]


def intervalo(valores):
    xs = sorted(valores)
    return {'p5': cuantil(xs, 0.05), 'p50': cuantil(xs, 0.5), 'p95': cuantil(xs, 0.95)}


# --------------------------------------------------------------------------------------------
# F11. Robustez del orden
# --------------------------------------------------------------------------------------------
def robustez(sorteos, k=3):
    """Frecuencia con que cada regla queda 1.ª y entre las k primeras, a través de los sorteos.

    `sorteos` es una lista de dict regla → valor (pérdida o fricción) de cada sorteo.
    """
    n = len(sorteos)
    top1, topk = {}, {}
    for valores in sorteos:
        orden = sorted(valores, key=lambda r: -valores[r])
        if orden:
            top1[orden[0]] = top1.get(orden[0], 0) + 1
        for r in orden[:k]:
            topk[r] = topk.get(r, 0) + 1
    ordenar = lambda d: {r: c / n for r, c in sorted(d.items(), key=lambda kv: (-kv[1], kv[0]))}
    return {'n': n, 'top1': ordenar(top1), f'top{k}': ordenar(topk)}


# --------------------------------------------------------------------------------------------
# F13. Divergencia de Jensen-Shannon en base 2
# --------------------------------------------------------------------------------------------
def entropia(p):
    return -sum(x * math.log2(x) for x in p if x > 0)


def jsd(distribuciones):
    """JSD de K distribuciones con pesos iguales: H(mezcla) − media de H. Va de 0 a log2(K)."""
    K = len(distribuciones)
    n = len(distribuciones[0])
    mezcla = [sum(d[i] for d in distribuciones) / K for i in range(n)]
    return max(entropia(mezcla) - sum(entropia(d) for d in distribuciones) / K, 0.0)


UMBRAL_JSD = 0.05
