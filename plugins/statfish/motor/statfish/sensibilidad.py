"""Sensibilidad por Morris (F10): qué supuesto mueve más cada métrica."""
import statistics


def morris(evaluar, modelo, parametros, metricas, r, niveles, rng, base):
    """r trayectorias de un paso por parámetro, con p niveles en [0, 1] y Δ = p/(2(p−1)).

    Cada parámetro k toma el valor p10 + x·(p90 − p10). El efecto elemental es EE = ΔY/Δ (con su
    signo); μ* es la media de |EE| y σ la desviación de EE. `evaluar(theta)` da las métricas.
    """
    delta = niveles / (2 * (niveles - 1))
    inicio = [i / (niveles - 1) for i in range(niveles // 2)]
    efectos = {k: {m: [] for m in metricas} for k in parametros}

    def evaluar_x(x):
        cambios = {}
        for k, v in zip(parametros, x):
            p = modelo.param[k]
            cambios[k] = p.p10 + v * (p.p90 - p.p10)
        return evaluar(base.con(cambios))

    for _ in range(r):
        x = [rng.choice(inicio) for _ in parametros]
        y = evaluar_x(x)
        orden = list(range(len(parametros)))
        rng.shuffle(orden)
        for i in orden:
            x2 = list(x)
            x2[i] = x[i] + delta if x[i] + delta <= 1 + 1e-9 else x[i] - delta
            y2 = evaluar_x(x2)
            signo = 1 if x2[i] > x[i] else -1
            for m in metricas:
                efectos[parametros[i]][m].append(signo * (y2[m] - y[m]) / delta)
            x, y = x2, y2
    salida = []
    for k in parametros:
        p = modelo.param[k]
        fila = {'parametro': k, 'rango': [p.p10, p.p90]}
        for m in metricas:
            ee = efectos[k][m]
            fila[m] = {'mu_estrella': statistics.fmean(abs(e) for e in ee), 'sigma': statistics.pstdev(ee)}
        salida.append(fila)
    return salida
