#!/usr/bin/env python3
"""Tablas en markdown a partir de salida/*.json (script desechable)."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo  # noqa: E402

S = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'salida')
a = json.load(open(os.path.join(S, 'agregados.json')))
us = json.load(open(os.path.join(S, 'usuarios.json')))
tr = json.load(open(os.path.join(S, 'trazas.json')))


def pct(x, d=1):
    return f'{x * 100:.{d}f}'.replace('.', ',') + ' %'


def num(x, cifras=3):
    return f'{x:.{cifras}g}'.replace('.', ',')


def pp(x, d=2):
    return f'{x * 100:.{d}f}'.replace('.', ',')


out = []
w = out.append

# --- perfiles
w('## TABLA_PERFILES')
w('| Perfil | Quién | P(perfil) p50 | p5–p95 | Contacto | Pérdida por código | Contacto con fricción |')
w('|---|---|---|---|---|---|---|')
for s, nombre in modelo.SEGMENTOS.items():
    d = a['por_segmento'][s]
    contacto = d['contacto'] + d['contacto_con_friccion'] + d['correo_directo']
    perdida = d['abandono_por_friccion'] + d['perdida_silenciosa']
    iv = a['intervalos']['masa_' + s]
    w(f"| {s} | {nombre} | {pct(a['masa'][s])} | {pct(iv['p5'])} – {pct(iv['p95'])} | {pct(contacto)} | "
      f"{pct(perdida, 2)} | {pct(d['contacto_con_friccion'] + d['correo_directo'], 2)} |")

# --- desenlaces
w('\n## TABLA_DESENLACES')
w('| Desenlace | De cada 100 llegadas |')
w('|---|---|')
nombres = {'contacto': 'Contacto sin fricción', 'contacto_con_friccion': 'Contacto después de una fricción',
           'correo_directo': 'Escribe al correo tras un error', 'no_envia_whatsapp': 'Abre WhatsApp y no envía',
           'abandono_sin_intento': 'Se va sin intentar contactar', 'abandono_por_friccion': 'Se va por una fricción del código',
           'perdida_silenciosa': 'Envía y no llega nada (silencio)'}
for k in modelo.DESENLACES:
    w(f"| {nombres[k]} | {pp(a['desenlaces_p50'][k])} |")

# --- reglas
w('\n## TABLA_REGLAS')
w('| Regla | Qué pasa | Se pierde (de cada 1.000 llegadas) | Llega con fricción (de cada 1.000) |')
w('|---|---|---|---|')
agg = {}
for k, v in a['por_regla'].items():
    regla, d = k.split('|')
    e = agg.setdefault(regla, [0.0, 0.0])
    if d in ('abandono_por_friccion', 'perdida_silenciosa'):
        e[0] += v
    else:
        e[1] += v
for regla, (perd, fric) in sorted(agg.items(), key=lambda kv: -(kv[1][0] + kv[1][1] / 4)):
    w(f"| {regla} | {modelo.REGLAS[regla][0]} | {pp(perd / 100 * 1000)} | {pp(fric / 100 * 1000)} |")

# --- intervalos
w('\n## TABLA_INTERVALOS')
w('| Métrica | p5 | p50 | p95 |')
w('|---|---|---|---|')
for k, nombre in [('contacto_total', 'Contacto (todas las vías)'), ('perdida_por_codigo', 'Pérdida atribuible al código'),
                  ('con_friccion', 'Pasa por alguna fricción')]:
    iv = a['intervalos'][k]
    w(f"| {nombre} | {pct(iv['p5'], 2)} | {pct(iv['p50'], 2)} | {pct(iv['p95'], 2)} |")

# --- morris
w('\n## TABLA_MORRIS')
w('| Supuesto | Rango probado | μ* sobre la pérdida (pp) | σ | μ* sobre el contacto (pp) |')
w('|---|---|---|---|---|')
for f in a['morris']:
    r = f['rango']
    w(f"| `{f['parametro']}` | {pp(r[0], 1)}–{pp(r[1], 1)} % | {pp(f['perdida_por_codigo']['mu_estrella'])} | "
      f"{pp(f['perdida_por_codigo']['sigma'])} | {pp(f['contacto_total']['mu_estrella'])} |")

# --- hipótesis
w('\n## TABLA_HIPOTESIS')
w('| Escenario | Contacto | Pérdida por código | Pasa por fricción |')
w('|---|---|---|---|')
for k, v in a['hipotesis'].items():
    w(f"| {'Hoy (modelo)' if k == 'base' else k} | {pct(v['contacto_total'], 2)} | {pct(v['perdida_por_codigo'], 2)} | "
      f"{pct(v['con_friccion'], 2)} |")

# --- fidelidad
w('\n## TABLA_FIDELIDAD')
w('| Variable | Declarada | En la muestra | n |')
w('|---|---|---|---|')
for f in a['fidelidad']:
    n = f"{f['n']:,}".replace(',', '.')
    w(f"| {f['variable']} | {pct(f['declarada'], 2)} | {pct(f['muestra'], 2)} | {n} |")

# --- cobertura
cp, ca, cs = a['cobertura_pares'], a['cobertura_arcos'], a['cobertura_superficies']
w('\n## COBERTURA')
w(f"pares {cp['cubiertos']}/{cp['universo']} ; arcos sorteo {ca['cubiertos_sorteo']}/{ca['universo']}, total "
  f"{ca['cubiertos_total']}/{ca['universo']} ; superficies sorteo {len(cs['vistas_en_sorteo'])}/{len(cs['universo'])}, "
  f"total {len(cs['vistas_total'])}/{len(cs['universo'])} ; faltan {cs['faltan_total']}")

# --- usuarios
w('\n## TABLA_USUARIOS')
w('| Id | Cómo se creó | Peso p/q | Perfil | Nombre (sintético) | Equipo | Lo raro | Busca | Llega a | Desenlace sorteado | P(contacto) esperada |')
w('|---|---|---|---|---|---|---|---|---|---|---|')
trs = {t['id']: t for t in tr if not t['forzada']}
DES = {'contacto': 'contacto', 'contacto_con_friccion': 'contacto con fricción', 'correo_directo': 'escribe al correo',
       'no_envia_whatsapp': 'no envía el WhatsApp', 'abandono_sin_intento': 'se va sin intentar',
       'abandono_por_friccion': 'se va por fricción', 'perdida_silenciosa': 'pérdida silenciosa'}
DISP = {'movil': 'celular', 'escritorio': 'escritorio', 'tablet': 'tablet'}
SIS = {'android': 'Android', 'ios': 'iOS', 'ipados': 'iPadOS', 'windows': 'Windows', 'macos': 'macOS', 'linux': 'Linux'}
NAV = {'chrome': 'Chrome', 'edge': 'Edge', 'firefox': 'Firefox', 'opera': 'Opera', 'samsung': 'Samsung Internet',
       'safari': 'Safari', 'otro': 'otro', 'webview de la app': 'navegador de la app'}
SERV = {'web': 'página web', 'tienda': 'tienda online', 'gestion': 'sistema de gestión', 'automatizacion': 'automatización',
        'agente': 'agente de IA', 'app': 'app', 'prospeccion': 'prospección', 'datos': 'Ley 21.719', 'no_sabe': 'no sabe aún'}
DEST = {'home': 'portada', 'servicio': 'su servicio', 'ley': '/ley21719', 'articulo': 'un artículo', 'brief': '/brief-web'}
for x in us:
    u = x['atributos']
    equipo = f"{DISP[u['dispositivo']]} {SIS[u['sistema']]}, {NAV[u['navegador']]}"
    raro = []
    if u['js_off']:
        raro.append('sin JS')
    elif u['js_brief_falla']:
        raro.append('brief.js no carga')
    if u['estricta']:
        raro.append('privacidad estricta')
    if u['almacen_bloqueado']:
        raro.append('sin almacenamiento')
    if u['agente']:
        raro.append('agente WebMCP')
    if u['inapp']:
        raro.append('navegador de app')
    if u['movimiento_reducido']:
        raro.append('movimiento reducido')
    if u['gpu'] != 'ok':
        raro.append('GPU ' + ('lenta' if u['gpu'] == 'lenta' else 'sin WebGL'))
    if u['nombre_tipo'] != 'simple':
        raro.append({'apostrofo': 'apóstrofo', 'guion_punto': 'guion o punto', 'empresa_signos': 'nombre de empresa'}[u['nombre_tipo']]
                    + (' + Smart Punctuation' if u['smart_punct'] and u['nombre_tipo'] == 'apostrofo' else ''))
    if u['pega_rapido']:
        raro.append('pega y envía rápido')
    peso = '—' if x['peso'] is None else f"{x['peso']:.1e}"
    e = x['esperado']
    pc = e['contacto'] + e['contacto_con_friccion'] + e['correo_directo']
    busca = 'brief (cliente)' if u['relacion'] == 'cliente_brief' else f"{SERV[u['servicio']]}, {u['etapa']}"
    w(f"| {x['id']} | {x['tipo']} | {peso} | {x['segmento']} | {x['nombre']} | {equipo} | {', '.join(raro) or '—'} | "
      f"{busca} | {DEST[u['destino']]} | {DES[trs[x['id']]['desenlace']]} | {pct(pc)} |")

# --- trazas
w('\n## TRAZAS')
for t in tr:
    if t['forzada']:
        continue
    w(f"\n#### {t['id']} · {DES[t['desenlace']]} · P(camino) = {num(t['prob_camino'])}")
    w('| # | Estado | Sorteo | P | Acción | Regla y evidencia | CW |')
    w('|---|---|---|---|---|---|---|')
    for i, p in enumerate(t['pasos'], 1):
        ev = ''
        if p['regla']:
            ev = f"{p['regla']}: " + ', '.join(f'`{e}`' for e in p['evidencia'][:2])
        cw = '—' if all(c == 'sí' for c in p['cw']) else '/'.join(p['cw'])
        sorteo = '—' if p['sorteo'] is None else num(p['sorteo'])
        w(f"| {i} | {p['estado']} | {sorteo} | {num(p['prob'])} | {p['accion']} | {ev} | {cw} |".replace('|  |', '| |'))
        if p['nota_cw']:
            w(f"| | | | | ↳ *{p['nota_cw']}* | | |")

w('\n## FORZADAS')
w('| Arco que faltaba | Usuario | P(camino) | Desenlace | Camino |')
w('|---|---|---|---|---|')
for t in tr:
    if not t['forzada']:
        continue
    camino = ' → '.join(p['accion'] for p in t['pasos'][1:])
    w(f"| {t['arco'][0]}: {t['arco'][1]} | {t['id']} | {num(t['prob_camino'], 2)} | {DES[t['desenlace']]} | {camino} |")

open(os.path.join(S, 'tablas.md'), 'w').write('\n'.join(out) + '\n')
print('ok', len(out))
