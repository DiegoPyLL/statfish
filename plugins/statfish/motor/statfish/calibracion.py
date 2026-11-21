"""Calibración conjugada (F14): Beta(α + s, β + f) y Dirichlet(κ·p + n) con conteos reales."""
from . import incertidumbre as I


def calibrar_binario(p50, p10, p90, exitos, fracasos):
    """Prior por F1, posterior conjugada; devuelve p50 (media), p10 y p90 de la posterior."""
    ab = I.beta_desde(p50, p10, p90)
    if ab is None:
        a, b = p50 * 1e6, (1 - p50) * 1e6
    else:
        a, b = ab
    a2, b2 = a + exitos, b + fracasos
    media, _ = I.beta_media_var(a2, b2)
    return {'prior': {'alfa': a, 'beta': b, 'p50': p50, 'p10': p10, 'p90': p90},
            'posterior': {'alfa': a2, 'beta': b2, 'p50': media,
                          'p10': I.beta_cuantil(0.10, a2, b2), 'p90': I.beta_cuantil(0.90, a2, b2)},
            'n': exitos + fracasos}


def calibrar_categorica(valores, kappa, conteos):
    """Dirichlet(κ·p) + n: p' = (κp + n)/(κ + N), κ' = κ + N."""
    N = sum(conteos.get(v, 0) for v, _ in valores)
    alfa = [(v, kappa * p + conteos.get(v, 0)) for v, p in valores]
    total = kappa + N
    return {'prior': {'valores': dict(valores), 'kappa': kappa},
            'posterior': {'valores': {v: a / total for v, a in alfa}, 'kappa': total}, 'n': N}


def calibrar(modelo, conteos):
    """Aplica todos los conteos de conteos.toml a los priors de modelo.toml (siempre desde el prior)."""
    salida = {'parametros': {}, 'distribuciones': {}, 'avisos': []}
    for c in conteos.get('conteos', []):
        if 'parametro' in c:
            pid = c['parametro']
            x = modelo.param.get(pid)
            if x is None or x.interruptor:
                salida['avisos'].append(f'«{pid}» no es un parámetro con rango')
                continue
            s, f = int(c.get('exitos', 0)), int(c.get('fracasos', 0))
            previo = salida['parametros'].get(pid)
            if previo:
                s += previo['exitos']
                f += previo['fracasos']
            r = calibrar_binario(x.p50, x.p10, x.p90, s, f)
            salida['parametros'][pid] = {'exitos': s, 'fracasos': f, 'fuente': c.get('fuente', ''), **r}
        elif 'distribucion' in c:
            did = c['distribucion']
            x = modelo.dist.get(did)
            if x is None:
                salida['avisos'].append(f'«{did}» no es una distribución')
                continue
            n = {k: int(v) for k, v in c.get('n', {}).items()}
            for k in n:
                if k not in dict(x.valores):
                    salida['avisos'].append(f'{did}: «{k}» no es un valor de la distribución')
            previo = salida['distribuciones'].get(did)
            if previo:
                for k, v in previo['conteos'].items():
                    n[k] = n.get(k, 0) + v
            r = calibrar_categorica(x.valores, x.kappa, n)
            salida['distribuciones'][did] = {'conteos': n, 'fuente': c.get('fuente', ''), **r}
        else:
            salida['avisos'].append('cada conteo lleva parametro (exitos, fracasos) o distribucion (n)')
    return salida


def a_calibracion_toml(cal):
    """La parte de calibracion.toml que lee el motor: los parámetros posteriores."""
    return {
        'parametros': {pid: {'p50': r['posterior']['p50'], 'p10': r['posterior']['p10'],
                             'p90': r['posterior']['p90'], 'n': r['n']}
                       for pid, r in cal['parametros'].items()},
        'distribuciones': {did: {'valores': r['posterior']['valores'], 'kappa': r['posterior']['kappa'], 'n': r['n']}
                           for did, r in cal['distribuciones'].items()},
    }
