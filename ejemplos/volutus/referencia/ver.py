import json, sys
us = json.load(open('usuarios.json'))
tr = {t['id']: t for t in json.load(open('trazas.json')) if not t['forzada']}
for x in us:
    a = x['atributos']
    w = '-' if x['peso'] is None else '%.2e' % x['peso']
    js = 'OFF' if a['js_off'] else ('briefjs!' if a['js_brief_falla'] else 'ok')
    print(x['id'], x['tipo'][:5], 'w=' + w, x['segmento'], '|', x['nombre'], '|', a['relacion'], a['canal'],
          a['dispositivo'] + '/' + a['sistema'] + '/' + a['navegador'] + ('/app' if a['inapp'] else ''),
          'gpu=' + a['gpu'], 'mov=' + ('red' if a['movimiento_reducido'] else '-'), 'js=' + js,
          'alm=' + ('BLOQ' if a['almacen_bloqueado'] else 'ok'), 'priv=' + ('ESTR' if a['estricta'] else '-'),
          'ag=' + ('AG' if a['agente'] else '-'), 'smart=' + str(a['smart_punct']), 'nombre=' + a['nombre_tipo'], '|',
          a['tamano'], a['servicio'], a['etapa'], 'pega=' + str(a['pega_rapido']), 'envio=' + a['canal_envio'],
          'dest=' + a['destino'], '|', a['rubro'] + ',', a['region'] + ',', a['edad'])
    t = tr[x['id']]
    print('     ->', t['desenlace'], '| ', ' > '.join('%s[%s]' % (p['accion'], p['sorteo']) for p in t['pasos']))
