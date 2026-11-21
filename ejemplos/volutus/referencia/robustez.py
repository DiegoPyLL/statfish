import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from collections import Counter, defaultdict
import modelo as m
US = m.uniformes(random.Random(m.SEMILLA + 4), 3000)
rng = random.Random(m.SEMILLA + 5)
top3 = Counter(); top1 = Counter(); top3_fric = Counter(); n = 200
for _ in range(n):
    t = m.theta_sorteado(rng)
    _, _, _, pr = m.poblacion(t, US)
    perd = defaultdict(float); fric = defaultdict(float)
    for (r, d), v in pr.items():
        if d in ('abandono_por_friccion', 'perdida_silenciosa'): perd[r] += v
        fric[r] += v
    orden = sorted(perd, key=lambda r: -perd[r])
    top1[orden[0]] += 1
    for r in orden[:3]: top3[r] += 1
    for r in sorted(fric, key=lambda r: -fric[r])[:3]: top3_fric[r] += 1
res = {'n': n, 'top1_perdida': {r: c / n for r, c in top1.most_common()},
       'top3_perdida': {r: c / n for r, c in top3.most_common()},
       'top3_friccion_total': {r: c / n for r, c in top3_fric.most_common()}}
json.dump(res, open('salida/robustez.json', 'w'), indent=1)
print(json.dumps(res, indent=1))
