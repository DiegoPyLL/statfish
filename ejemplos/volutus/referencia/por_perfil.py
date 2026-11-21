import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, random
from collections import defaultdict, Counter
import modelo as m
t = m.theta_p50()
US = m.uniformes(random.Random(m.SEMILLA + 1), 60_000)
seg_n = Counter(); reg = defaultdict(lambda: defaultdict(float)); attrs = defaultdict(Counter)
for U in US:
    u, _ = m.muestrear(U, t)
    s = m.segmento(u); seg_n[s] += 1
    _, pr = m.evaluar(u, t)
    for (r, d), p in pr.items():
        reg[s][(r, 'perdida' if d in ('abandono_por_friccion', 'perdida_silenciosa') else 'friccion')] += p
    for k in ('canal', 'dispositivo', 'servicio', 'destino', 'etapa', 'canal_envio', 'tamano'):
        attrs[s][(k, u[k])] += 1
out = {}
for s in m.SEGMENTOS:
    n = seg_n[s]
    top = sorted(((k, v / n) for k, v in reg[s].items()), key=lambda kv: -kv[1])[:5]
    tops = {}
    for k in ('canal', 'dispositivo', 'servicio', 'destino', 'etapa', 'canal_envio', 'tamano'):
        c = Counter({v: cnt for (kk, v), cnt in attrs[s].items() if kk == k})
        tops[k] = [(v, round(cnt / n, 3)) for v, cnt in c.most_common(3)]
    out[s] = {'n': n, 'reglas': [(f'{r}:{tipo}', round(v * 1000, 2)) for (r, tipo), v in top], 'atributos': tops}
    print(s, n, out[s]['reglas']); print('   ', tops)
json.dump(out, open('salida/por_perfil.json', 'w'), ensure_ascii=False, indent=1)
