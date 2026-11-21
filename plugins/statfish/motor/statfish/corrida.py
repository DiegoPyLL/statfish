"""Orquestación de `statfish correr`: del modelo a salida/*.json, informe.md y manifiesto.json.

Todo sale de la semilla: cada etapa usa su propio generador (semilla + desplazamiento fijo), así que
cambiar el tamaño de una etapa no cambia los sorteos de las demás.
"""
import hashlib
import json
import os
import platform
import random
import sys
import time

from . import cadena as C
from . import cobertura as CO
from . import incertidumbre as I
from . import modelo as M
from . import muestreo as MU
from . import red as R
from . import sensibilidad as S

# Desplazamientos de semilla por etapa (los del caso Volutus; fijos para siempre).
SEMILLA_REPRESENTATIVOS = 0
SEMILLA_POBLACION = 1
SEMILLA_COBERTURA = 2
SEMILLA_NOMBRES = 3
SEMILLA_INCERTIDUMBRE_USUARIOS = 4
SEMILLA_INCERTIDUMBRE_PARAMETROS = 5
SEMILLA_MORRIS = 6
SEMILLA_HIPOTESIS = 7
# La traza sorteada del usuario i (1, 2, …) usa la semilla × 100 + i.

ESCALA_RAPIDA = {'poblacion': 10, 'sorteos_parametros': 4, 'usuarios_incertidumbre': 3, 'usuarios_hipotesis': 4,
                 'candidatos_universo': 3, 'candidatos_por_vuelta': 3, 'universo_arcos': 4,
                 'trayectorias': 2, 'usuarios_morris': 4}

SALIDAS = ('salida/usuarios.json', 'salida/trazas.json', 'salida/resultados.json')


class Bitacora:
    def __init__(self, silencioso=False):
        self.t0 = time.time()
        self.silencioso = silencioso

    def __call__(self, msg):
        if not self.silencioso:
            print(f'[{time.time() - self.t0:6.1f} s] {msg}', file=sys.stderr, flush=True)


def tamanos(m, rapido=False):
    t = {
        'poblacion': m.corrida['poblacion'],
        'representativos': m.corrida['representativos'],
        'sorteos_parametros': m.corrida['sorteos_parametros'],
        'usuarios_incertidumbre': m.corrida['usuarios_incertidumbre'],
        'usuarios_hipotesis': m.corrida['usuarios_hipotesis'],
        'candidatos_universo': m.cobertura['candidatos_universo'],
        'candidatos_por_vuelta': m.cobertura['candidatos_por_vuelta'],
        'universo_arcos': m.cobertura['universo_arcos'],
        'trayectorias': m.sensibilidad['trayectorias'],
        'niveles': m.sensibilidad['niveles'],
        'usuarios_morris': m.sensibilidad['usuarios'],
    }
    if rapido:
        for k, d in ESCALA_RAPIDA.items():
            t[k] = max(1, t[k] // d)
    t['usuarios_morris'] = min(t['usuarios_morris'], t['usuarios_incertidumbre'])
    t['universo_arcos'] = min(t['universo_arcos'], t['candidatos_universo'])
    return t


def huella(atributos):
    texto = json.dumps(atributos, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(texto.encode('utf-8')).hexdigest()[:12]


def calcular(m, semilla=None, rapido=False, bitacora=None, etapas=None):
    """Corre el modelo completo y devuelve los objetos de salida (sin escribir nada)."""
    log = bitacora or Bitacora(silencioso=True)
    semilla = m.corrida['semilla'] if semilla is None else semilla
    tam = tamanos(m, rapido)
    red = R.Red(m)
    cad = C.Cadena(m)
    fs = MU.compilar_metricas(m)
    t50 = M.theta_p50(m)
    tq = M.theta_aplanado(m)
    ids_metricas = [x['id'] for x in m.metricas]
    perdida = set(m.cadena['perdida'])

    # 1. Población grande con los parámetros en p50: desenlaces exactos, marginales y fidelidad.
    log(f'población de {tam["poblacion"]:,} usuarios'.replace(',', '.'))
    US = red.uniformes(random.Random(semilla + SEMILLA_POBLACION), tam['poblacion'])
    reg = MU.RegistroFidelidad(m)
    pob = MU.poblacion(red, cad, m, t50, US, registro=reg)
    fidelidad = reg.resultado(t50)
    del US

    # 2. Representativos.
    usuarios = MU.representativos(red, t50, random.Random(semilla + SEMILLA_REPRESENTATIVOS), tam['representativos'])

    # 3. Cobertura por pares (AETG) con la red aplanada.
    log('cobertura por pares')
    rng_c = random.Random(semilla + SEMILLA_COBERTURA)
    universo, cubiertos, candidatos, nuevos = CO.cubrir_pares(
        red, t50, tq, rng_c, usuarios, tam['candidatos_universo'], tam['candidatos_por_vuelta'])
    usuarios += nuevos
    cobertura_pares = {'factores': [f['id'] for f in m.factores], 'universo': len(universo),
                       'cubiertos': len(cubiertos & universo),
                       'faltan': sorted([list(p) for p in universo - cubiertos])}

    # 4. Nombres, perfiles, desenlace esperado y trazas sorteadas.
    rng_nombres = random.Random(semilla + SEMILLA_NOMBRES)
    nombres_usados = set()
    MU.nombrar(m, usuarios, rng_nombres, nombres_usados)
    trazas = []
    arcos_cubiertos = set()
    vistas = set()

    def trazar_usuarios(desde):
        for i, x in enumerate(usuarios[desde:], desde + 1):
            x['id'] = f'U{i:02d}'
            x['perfil'] = red.perfil(x['u'])
            acum, _ = cad.evaluar(x['u'], t50)
            x['esperado'] = {d: round(acum.get(d, 0), 4) for d in m.cadena['desenlaces']}
            pasos, d, pc = cad.trazar(x['u'], t50, random.Random(semilla * 100 + i))
            trazas.append({'id': x['id'], 'forzada': False, 'pasos': pasos, 'desenlace': d, 'prob_camino': pc})
            arcos_cubiertos.update(tuple(p['arco']) for p in pasos)
            vistas.update(CO.superficies_de(red, x['u'], pasos))

    trazar_usuarios(0)

    # 5. Arcos: universo alcanzable y trazas forzadas para los que faltan (F15).
    log('cobertura de arcos')
    arcos, por_candidato = CO.universo_arcos(red, cad, t50, tq, candidatos[:tam['universo_arcos']])
    del candidatos
    faltan_arcos = arcos - arcos_cubiertos
    forzadas = CO.forzar_arcos(cad, t50, usuarios, faltan_arcos)
    for t in forzadas:
        arcos_cubiertos.update(tuple(p['arco']) for p in t['pasos'])
    # Si ningún usuario alcanza un arco, se suma un usuario de q que lo alcance y se fuerza su camino.
    restantes = arcos - arcos_cubiertos
    if restantes:
        extra = CO.usuarios_para_arcos(red, t50, tq, por_candidato, restantes)
        if extra:
            desde = len(usuarios)
            usuarios += extra
            MU.nombrar(m, extra, rng_nombres, nombres_usados)
            trazar_usuarios(desde)
            mas = CO.forzar_arcos(cad, t50, usuarios, arcos - arcos_cubiertos)
            for t in mas:
                arcos_cubiertos.update(tuple(p['arco']) for p in t['pasos'])
            forzadas += mas
    del por_candidato
    faltan_arcos = arcos - {a for t in trazas for a in (tuple(p['arco']) for p in t['pasos'])}
    vistas_total = set(vistas)
    por_id = {x['id']: x for x in usuarios}
    for t in forzadas:
        vistas_total |= CO.superficies_de(red, por_id[t['id']]['u'], t['pasos'])
    cobertura_arcos = {'universo': len(arcos), 'cubiertos_sorteo': len(arcos - faltan_arcos),
                       'cubiertos_total': len(arcos & arcos_cubiertos),
                       'faltan': sorted([list(a) for a in arcos - arcos_cubiertos])}
    clases = CO.universo_superficies(m)
    cobertura_superficies = CO.resumen_superficies(clases, vistas, vistas_total)

    # 6. Incertidumbre: S sorteos de los parámetros sobre la misma población (números comunes).
    log(f'incertidumbre: {tam["sorteos_parametros"]} sorteos × {tam["usuarios_incertidumbre"]:,} usuarios'.replace(',', '.'))
    US_i = red.uniformes(random.Random(semilla + SEMILLA_INCERTIDUMBRE_USUARIOS), tam['usuarios_incertidumbre'])
    rng_t = random.Random(semilla + SEMILLA_INCERTIDUMBRE_PARAMETROS)
    corridas, perd_sorteos, fric_sorteos = [], [], []
    for _ in range(tam['sorteos_parametros']):
        tt = M.theta_sorteado(m, rng_t)
        r = MU.poblacion(red, cad, m, tt, US_i)
        fila = MU.metricas(fs, r['desenlaces'])
        fila.update({'masa_' + s: v for s, v in r['masa'].items()})
        corridas.append(fila)
        perd, fric = {}, {}
        for (regla, d), v in r['por_regla'].items():
            if d in perdida:
                perd[regla] = perd.get(regla, 0.0) + v
            fric[regla] = fric.get(regla, 0.0) + v
        perd_sorteos.append(perd)
        fric_sorteos.append(fric)
    intervalos = {k: I.intervalo([c[k] for c in corridas]) for k in corridas[0]} if corridas else {}
    rob_p = I.robustez(perd_sorteos)
    rob_f = I.robustez(fric_sorteos)
    robustez = {'n': rob_p['n'], 'top1_perdida': rob_p['top1'], 'top3_perdida': rob_p['top3'],
                'top3_friccion': rob_f['top3']}

    # 7. Sensibilidad (Morris) sobre los primeros usuarios de la misma población.
    morris = []
    sens = m.sensibilidad
    if sens.get('parametros'):
        log(f'Morris: {tam["trayectorias"]} trayectorias × {len(sens["parametros"]) + 1} puntos')
        US_m = US_i[:tam['usuarios_morris']]
        metricas_m = sens.get('metricas') or ids_metricas
        evaluar = lambda th: MU.metricas(fs, MU.poblacion(red, cad, m, th, US_m)['desenlaces'])
        morris = S.morris(evaluar, m, sens['parametros'], metricas_m, tam['trayectorias'], tam['niveles'],
                          random.Random(semilla + SEMILLA_MORRIS), t50)
        clave = sens.get('ordenar_por') or metricas_m[0]
        morris.sort(key=lambda f: -f[clave]['mu_estrella'])
    del US_i

    # 8. Hipótesis: qué cambia si se arregla, con la misma población.
    log(f'hipótesis: {len(m.hipotesis)} sobre {tam["usuarios_hipotesis"]:,} usuarios'.replace(',', '.'))
    US_h = red.uniformes(random.Random(semilla + SEMILLA_HIPOTESIS), tam['usuarios_hipotesis'])
    hipotesis = {'base': {'texto': 'Hoy (modelo)', 'cambios': {},
                          **MU.metricas(fs, MU.poblacion(red, cad, m, t50, US_h)['desenlaces'])}}
    for h in m.hipotesis:
        th = t50.con(h['cambios'])
        hipotesis[h['id']] = {'texto': h['texto'], 'cambios': h['cambios'],
                              **MU.metricas(fs, MU.poblacion(red, cad, m, th, US_h)['desenlaces'])}
    del US_h

    # Restricciones sobre los usuarios creados.
    violaciones = []
    for x in usuarios:
        for i in red.restricciones(x['u']):
            violaciones.append({'usuario': x['id'], 'restriccion': m.restricciones[i]['texto']})

    resultados = armar_resultados(m, semilla, tam, rapido, fs, pob, fidelidad, intervalos, robustez, morris,
                                  hipotesis, cobertura_pares, cobertura_arcos, cobertura_superficies,
                                  violaciones, usuarios, trazas)
    salida_usuarios = []
    for x in usuarios:
        salida_usuarios.append({
            'id': x['id'], 'tipo': x['tipo'], 'peso': x['peso'], 'perfil': x['perfil'], 'nombre': x['nombre'],
            'nuevos_pares': x.get('nuevos_pares'), 'logp': x['logp'], 'huella': huella(x['u']),
            'atributos': x['u'], 'factores': {k: v for k, v in red.factores(x['u']).items()},
            'esperado': x['esperado'],
        })
    log('listo')
    return {'usuarios': salida_usuarios, 'trazas': trazas + forzadas, 'resultados': resultados}


def armar_resultados(m, semilla, tam, rapido, fs, pob, fidelidad, intervalos, robustez, morris, hipotesis,
                     cobertura_pares, cobertura_arcos, cobertura_superficies, violaciones, usuarios, trazas):
    perdida = set(m.cadena['perdida'])
    met = MU.metricas(fs, pob['desenlaces'])
    reglas = {}
    for (regla, d), v in pob['por_regla'].items():
        r = reglas.setdefault(regla or 'sin_regla', {'perdida': 0.0, 'friccion': 0.0, 'por_desenlace': {}})
        if d in perdida:
            r['perdida'] += v
        else:
            r['friccion'] += v
        r['por_desenlace'][d] = r['por_desenlace'].get(d, 0.0) + v
    for rid, r in reglas.items():
        x = m.reglas.get(rid)
        r['texto'] = x.texto if x else ''
        r['total'] = r['perdida'] + r['friccion']
    reglas = dict(sorted(reglas.items(), key=lambda kv: (-(kv[1]['perdida'] + kv[1]['friccion'] / 4), kv[0])))
    perfiles = {}
    for p in sorted(m.perfiles, key=lambda p: _orden_natural(p['id'])):
        s = p['id']
        des = pob['por_perfil'][s]
        mt = MU.metricas(fs, des)
        por_regla = {}
        for (regla, d), v in pob['por_perfil_regla'][s].items():
            r = por_regla.setdefault(regla or 'sin_regla', {'perdida': 0.0, 'friccion': 0.0})
            r['perdida' if d in perdida else 'friccion'] += v
        por_regla = dict(sorted(por_regla.items(), key=lambda kv: (-(kv[1]['perdida'] + kv[1]['friccion']), kv[0])))
        iv = intervalos.get('masa_' + s, {})
        perfiles[s] = {'nombre': p['nombre'], 'masa': pob['masa'][s], 'n': pob['n_perfil'][s],
                       'masa_p5': iv.get('p5'), 'masa_p95': iv.get('p95'),
                       'desenlaces': des, 'metricas': mt, 'reglas': por_regla}
    desenlace_traza = {t['id']: t['desenlace'] for t in trazas}
    return {
        'motor': M.VERSION_MOTOR,
        'modelo': m.nombre,
        'semilla': semilla,
        'rapido': rapido,
        'tamanos': tam,
        'desenlaces': pob['desenlaces'],
        'textos_desenlaces': m.cadena['desenlaces'],
        'metricas': met,
        'textos_metricas': {x['id']: x['texto'] for x in m.metricas},
        'intervalos': intervalos,
        'perfiles': perfiles,
        'reglas': reglas,
        'robustez': robustez,
        'morris': morris,
        'hipotesis': hipotesis,
        'cobertura': {'pares': cobertura_pares, 'arcos': cobertura_arcos, 'superficies': cobertura_superficies},
        'fidelidad': fidelidad,
        'restricciones': {'revisadas': len(m.restricciones), 'violaciones': violaciones},
        'parametros': {x.id: {'p50': x.p50, 'p10': x.p10, 'p90': x.p90,
                              'fuente': ':'.join(y for y in x.fuente if y), 'texto': x.texto}
                       for x in m.parametros},
        'usuarios': {'total': len(usuarios),
                     'representativos': sum(1 for x in usuarios if x['tipo'] == 'representativo'),
                     'cobertura': sum(1 for x in usuarios if x['tipo'] == 'cobertura'),
                     'cobertura_arcos': sum(1 for x in usuarios if x['tipo'] == 'cobertura de arcos'),
                     'por_desenlace': _contar(desenlace_traza.get(x['id']) for x in usuarios)},
    }


def _contar(it):
    c = {}
    for x in it:
        c[x] = c.get(x, 0) + 1
    return dict(sorted(c.items(), key=lambda kv: (-kv[1], kv[0])))


def _orden_natural(texto):
    import re
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', texto)]


# --------------------------------------------------------------------------------------------
# Escritura y manifiesto
# --------------------------------------------------------------------------------------------
def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, 'rb') as f:
        for bloque in iter(lambda: f.read(1 << 16), b''):
            h.update(bloque)
    return h.hexdigest()


def escribir(ruta, texto):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, 'w', encoding='utf-8', newline='\n') as f:
        f.write(texto)


def manifiesto(corrida, semilla, rapido, salidas):
    ctx = corrida.contexto()
    entradas = {r: sha256(corrida.ruta(r)) for r in corrida.archivos_entrada() if r != 'manifiesto.json'}
    return {
        'motor': M.VERSION_MOTOR,
        'python': '.'.join(platform.python_version_tuple()[:2]),
        'semilla': semilla,
        'rapido': rapido,
        'fecha': str(ctx.get('corrida', {}).get('fecha', '')),
        'repo': ctx.get('repo', {}).get('nombre', ''),
        'commit': ctx.get('repo', {}).get('commit', ''),
        'entradas': entradas,
        'salidas': {r: sha256(corrida.ruta(r)) for r in salidas},
    }
