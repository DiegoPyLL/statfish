import sys, os, json, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo as m
t = m.theta_p50()
# 1. Las categóricas suman 1
malas = [k for k, (lista, _, _) in m.C.items() if abs(sum(p for _, p in lista) - 1) > 1e-9]
print('categóricas que no suman 1:', malas)
# 2. Ramas de cada nodo suman 1 y los desenlaces de cada usuario suman 1
US = m.uniformes(random.Random(99), 20000)
peor_nodo = 0.0; peor_usuario = 0.0; viol = []
def recorrer(u, s, prof=0):
    global peor_nodo
    rs = m.ramas(u, t, s)
    peor_nodo = max(peor_nodo, abs(sum(p for p, *_ in rs) - 1))
    for p, s2, *_ in rs:
        if p > 0 and s2[0] != m.FIN and prof < 30: recorrer(u, s2, prof + 1)
for U in US:
    u, _ = m.muestrear(U, t)
    recorrer(u, ('inicio',))
    acum, _ = m.evaluar(u, t)
    peor_usuario = max(peor_usuario, abs(sum(acum.values()) - 1))
    # 3. Restricciones duras
    if u['sistema'] in ('ios', 'ipados') and u['motor'] != 'webkit': viol.append(('ios-webkit', u))
    if u['inapp'] and u['navegador'] != 'webview de la app': viol.append(('webview', u))
    if u['agente'] and not (u['dispositivo'] == 'escritorio' and u['navegador'] in ('chrome', 'edge') and not u['js_off']): viol.append(('agente', u))
    if u['destino'] == 'brief' and u['relacion'] != 'cliente_brief': viol.append(('brief', u))
    if u['smart_punct'] and u['sistema'] not in ('ios', 'ipados'): viol.append(('smart', u))
    if u['servicio'] == 'datos' and u['destino'] == 'servicio': viol.append(('ley', u))
print('máx |Σ ramas − 1| en un nodo:', peor_nodo)
print('máx |Σ desenlaces − 1| en un usuario:', peor_usuario)
print('violaciones de restricciones en 20.000 usuarios:', len(viol))
us = json.load(open('salida/usuarios.json'))
v34 = []
for x in us:
    u = x['atributos']
    if u['sistema'] in ('ios', 'ipados') and u['motor'] != 'webkit': v34.append(x['id'])
    if u['inapp'] and u['navegador'] != 'webview de la app': v34.append(x['id'])
    if u['agente'] and not (u['dispositivo'] == 'escritorio' and u['navegador'] in ('chrome', 'edge') and not u['js_off']): v34.append(x['id'])
    if u['destino'] == 'brief' and u['relacion'] != 'cliente_brief': v34.append(x['id'])
print('violaciones entre los 34 usuarios:', v34)
# 4. Representativos frente a P(perfil)
a = json.load(open('salida/agregados.json'))
from collections import Counter
c = Counter(x['segmento'] for x in us if x['tipo'] == 'representativo')
print('representativos por perfil (observado / esperado de 12):', {s: (c.get(s, 0), round(12 * a['masa'][s], 1)) for s in m.SEGMENTOS})
# 5. Las trazas tienen sorteo y evidencia donde hay regla
tr = json.load(open('salida/trazas.json'))
sin_sorteo = sum(1 for t_ in tr if not t_['forzada'] for p in t_['pasos'] if p['sorteo'] is None)
sin_evid = sum(1 for t_ in tr for p in t_['pasos'] if p['regla'] and not p['evidencia'])
print('pasos sorteados sin número:', sin_sorteo, '| pasos con regla sin evidencia:', sin_evid, '| trazas:', len(tr))
