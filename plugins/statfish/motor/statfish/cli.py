"""statfish: el motor determinista de Statfish (sin LLM y sin red).

    statfish contexto <repo> --slug <slug> --pregunta "…" [--pais CL] [--publico "…"]
    statfish patrones <corrida> [--buscar] [--json]
    statfish anclas [--pais CL] [--corrida <corrida> [--copiar]] [--hoy AAAA-MM-DD]
    statfish evidencia <corrida> [--repo <ruta>]
    statfish validar <corrida>
    statfish elicitar combinar <corrida> [--toml]
    statfish correr <corrida> [--semilla N] [--rapido] [--repo <ruta>]
    statfish reproducir <corrida> [--repo <ruta>]
    statfish comparar <a> <b> [--json]
    statfish calibrar <corrida> --conteos conteos.toml
"""
import argparse
import datetime
import json
import os
import random
import shutil
import sys
import tempfile

from . import cadena as C
from . import calibracion as CAL
from . import contexto as CTX
from . import corrida as CR
from . import evidencia as EV
from . import incertidumbre as I
from . import informe as INF
from . import modelo as M
from . import muestreo as MU
from . import red as R
from . import util

PLANTILLAS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'plantillas')


def _err(msg):
    print(f'statfish: {msg}', file=sys.stderr)


def _cargar(corrida):
    try:
        return corrida.modelo()
    except M.ErrorModelo as e:
        _err('el modelo tiene errores:')
        for x in e.errores:
            print(f'  ✗ {x}', file=sys.stderr)
        sys.exit(1)


def _hoy(texto):
    return datetime.date.fromisoformat(texto) if texto else datetime.date.today()


# --------------------------------------------------------------------------------------------
# contexto
# --------------------------------------------------------------------------------------------
def cmd_contexto(a):
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        _err(f'no existe el repo {repo}')
        return 1
    fecha = _hoy(a.fecha)
    if a.corrida:
        destino = os.path.abspath(a.corrida)
    else:
        if not a.slug:
            _err('indica --slug (la carpeta será statfish/<fecha>-<slug> dentro del repo) o --corrida')
            return 1
        destino = os.path.join(repo, 'statfish', f'{fecha.isoformat()}-{a.slug}')
    os.makedirs(destino, exist_ok=True)
    ctx = CTX.armar_contexto(repo, destino, a.pregunta, a.pais, a.publico or '', fecha)
    CR.escribir(os.path.join(destino, 'contexto.toml'),
                util.a_toml(ctx, 'Contexto de la corrida: lo escribe `statfish contexto` (determinista).'))
    copiadas = []
    for nombre in ('modelo.toml', 'hallazgos.toml', 'lectura.md', 'recorrido.toml'):
        origen = os.path.join(PLANTILLAS, nombre)
        if os.path.exists(origen) and not os.path.exists(os.path.join(destino, nombre)):
            shutil.copy(origen, os.path.join(destino, nombre))
            copiadas.append(nombre)
    print(f'corrida: {destino}')
    print(f'repo: {ctx["repo"]["nombre"]} @ {ctx["repo"]["commit_corto"]}'
          + (' (con cambios locales)' if ctx['repo']['cambios_locales'] else ''))
    st = ctx['stack']
    print(f'stack: {", ".join(st["rasgos"]) or "—"}')
    print(f'formularios: {st["formularios"]} · páginas: {st["paginas"]} · archivos: {st["archivos"]}')
    if copiadas:
        print(f'plantillas copiadas: {", ".join(copiadas)}')
    return 0


# --------------------------------------------------------------------------------------------
# patrones
# --------------------------------------------------------------------------------------------
def cmd_patrones(a):
    corrida = M.Corrida(a.corrida)
    ctx = corrida.contexto()
    if not ctx:
        _err('la corrida no tiene contexto.toml: corre primero `statfish contexto`')
        return 1
    catalogo = CTX.leer_patrones(a.catalogo)
    aplican, _ = CTX.patrones_aplicables(ctx, catalogo)
    estado = {}
    rec = corrida.toml('recorrido.toml') or {}
    for p in rec.get('patrones', []):
        estado[p.get('id')] = p.get('estado')
    repo = None
    if a.buscar:
        rel = ctx.get('repo', {}).get('ruta')
        repo = a.repo or (os.path.normpath(os.path.join(corrida.raiz, rel)) if rel else None)
    salida = []
    for p in aplican:
        fila = {'id': p['id'], 'tipo': p.get('tipo', 'patron'), 'titulo': p.get('titulo', ''),
                'estado': estado.get(p['id'], 'sin revisar'), 'pistas': p.get('deteccion', {}).get('pistas', [])}
        if repo:
            fila['lugares'] = CTX.buscar_pistas(repo, p)
        salida.append(fila)
    if a.json:
        print(json.dumps(salida, ensure_ascii=False, indent=1))
        return 0
    pat = [x for x in salida if x['tipo'] != 'descartada']
    des = [x for x in salida if x['tipo'] == 'descartada']
    print(f'{len(pat)} patrones aplican a este contexto (revisa cada uno: presente, ausente o no verificable):')
    for x in pat:
        print(f'\n  [{x["estado"]}] {x["id"]}: {x["titulo"]}')
        for pista in x['pistas']:
            print(f'      · {pista}')
        for l in x.get('lugares', []):
            print(f'      → {l["cita"]}: {l["texto"]}')
    if des:
        print(f'\n{len(des)} hipótesis ya descartadas en otros casos (no las propongas sin evidencia nueva):')
        for x in des:
            print(f'  - {x["id"]}: {x["titulo"]}')
    return 0


# --------------------------------------------------------------------------------------------
# anclas
# --------------------------------------------------------------------------------------------
def cmd_anclas(a):
    hoy = _hoy(a.hoy)
    registro = CTX.leer_registro(a.registro)
    filas = []
    for aid, (an, archivo) in sorted(registro.items()):
        if a.pais and an.get('pais') not in (a.pais, None, ''):
            continue
        estado, vence = CTX.estado_ancla(an, hoy)
        filas.append((aid, an, archivo, estado, vence))
    print(f'Registro de anclas ({len(filas)}), al {hoy.isoformat()}:')
    for aid, an, archivo, estado, vence in filas:
        marca = '⚠ vencida' if estado == 'vencida' else estado
        print(f'  {aid}  [{marca}, vence {vence}]  {an.get("titulo", "")}  ({archivo})')
    vencidas = [f for f in filas if f[3] == 'vencida']
    if vencidas:
        print(f'\n{len(vencidas)} anclas vencidas: consúltalas de nuevo con su plantilla de URL antes de usarlas.')
    if a.corrida:
        corrida = M.Corrida(a.corrida)
        m = _cargar(corrida)
        usadas = m.anclas_usadas()
        propias = corrida.anclas()
        print(f'\nLa corrida usa {len(usadas)} anclas:')
        faltan = []
        for aid, ids in sorted(usadas.items()):
            if aid in propias:
                print(f'  ✓ {aid} (copiada) ← {", ".join(sorted(ids))}')
            elif aid in registro:
                faltan.append(aid)
                print(f'  · {aid} (en el registro, sin copiar) ← {", ".join(sorted(ids))}')
            else:
                print(f'  ✗ {aid}: no está en el registro ni en la corrida ← {", ".join(sorted(ids))}')
        if a.copiar:
            for archivo in sorted({registro[aid][1] for aid in faltan}):
                origen = os.path.join(a.registro or os.path.join(CTX.DATOS, 'anclas'), archivo)
                destino = corrida.ruta('anclas', archivo)
                os.makedirs(os.path.dirname(destino), exist_ok=True)
                shutil.copy(origen, destino)
                print(f'  copiada: anclas/{archivo}')
    return 1 if vencidas and a.estricto else 0


# --------------------------------------------------------------------------------------------
# evidencia
# --------------------------------------------------------------------------------------------
def cmd_evidencia(a):
    corrida = M.Corrida(a.corrida)
    ev = EV.verificar(corrida, a.repo)
    CR.escribir(corrida.ruta('salida', 'evidencia.json'), M.json_estable(ev))
    r = ev['resumen']
    print(f'{r["citas"]} citas ({r["unicas"]} distintas) contra {(ev.get("commit_actual") or "—")[:7]} '
          f'(corrida: {ev["commit_corrida"][:7] or "—"}):')
    for k in ('vigente', 'desplazada', 'vencida', 'sin_extracto', 'no_verificable'):
        if r.get(k):
            print(f'  {k}: {r[k]}')
    vistos = set()
    for c in ev['citas']:
        if c['estado'] == 'vigente' or (c['cita'], c['estado']) in vistos:
            continue
        vistos.add((c['cita'], c['estado']))
        extra = f' → {c["nueva_cita"]}' if c.get('nueva_cita') else ''
        sug = f' (sugerido: «{c["sugerido"]}»)' if c.get('sugerido') else ''
        print(f'  ✗ {c["cita"]} [{c["estado"]}{extra}] {c.get("motivo", "")}{sug} — {c["origen"]}')
    if ev.get('precision') is not None:
        print(f'precisión automática: {util.pct(ev["precision"])}')
    return 0 if not any(r.get(k) for k in ('vencida', 'sin_extracto')) else 1


# --------------------------------------------------------------------------------------------
# validar
# --------------------------------------------------------------------------------------------
def validar(corrida, m, n=4000, sorteos=8):
    """Revisión dinámica sobre una muestra de usuarios (p50, aplanada y parámetros sorteados)."""
    errores, avisos = [], list(m.avisos)
    red = R.Red(m)
    cad = C.Cadena(m)
    rng = random.Random(m.corrida['semilla'] + 99)
    thetas = [('p50', M.theta_p50(m), n), ('aplanada', M.theta_aplanado(m), n)]
    rng_t = random.Random(m.corrida['semilla'] + 98)
    for i in range(sorteos):
        thetas.append((f'sorteo {i + 1}', M.theta_sorteado(m, rng_t), max(n // 10, 50)))
    valores = {v.id: set(map(_clave, v.valores)) for v in m.variables}
    vistos = set()
    negativos = 0

    def anotar(lista, msg):
        if msg not in vistos:
            vistos.add(msg)
            lista.append(msg)

    for nombre, th, k in thetas:
        for _ in range(k):
            try:
                u, _ = red.muestrear(red.uno(rng), th)
            except R.SinCaso as e:
                anotar(errores, f'red ({nombre}): ningún caso de la variable {e} calzó con un usuario')
                continue
            except Exception as e:
                anotar(errores, f'red ({nombre}): {type(e).__name__}: {e}')
                continue
            for var, val in u.items():
                if _clave(val) not in valores[var]:
                    anotar(errores, f'variable {var}: el valor «{val}» no está en valores')
            for i in red.restricciones(u):
                anotar(errores, f'restricción violada ({nombre}): {m.restricciones[i]["texto"]}')
            if red.perfil(u) is None:
                anotar(errores, 'un usuario no calzó con ningún perfil: el último debería ser si = "True"')
            try:
                red.factores(u)
            except Exception as e:
                anotar(errores, f'factores: {type(e).__name__}: {e}')
            # Ramas de cada estado alcanzable.
            try:
                pila, visto = [cad.inicio], set()
                cache = {}
                while pila:
                    s = pila.pop()
                    if s in visto:
                        continue
                    visto.add(s)
                    rs = cad.ramas(u, th, s, cache)
                    total = sum(r[0] for r in rs)
                    if abs(total - 1) > 1e-9:
                        anotar(errores, f'estado {s[0]} ({nombre}): las ramas suman {total!r}, no 1')
                    for r in rs:
                        if r[0] < -1e-12 or r[0] > 1 + 1e-12:
                            if nombre.startswith('sorteo'):
                                negativos += 1
                            else:
                                anotar(errores, f'estado {s[0]} ({nombre}): probabilidad fuera de [0, 1]: {r[0]!r}')
                        if r[3] and r[3] not in m.reglas:
                            anotar(errores, f'estado {s[0]}: la regla «{r[3]}» no está en [[reglas]]')
                        if r[1][0] != C.FIN and r[0] > 0:
                            pila.append(r[1])
                acum, _ = cad.evaluar(u, th)
                if abs(sum(acum.values()) - 1) > 1e-9:
                    anotar(errores, f'cadena ({nombre}): los desenlaces de un usuario suman {sum(acum.values())!r}')
            except (C.SinCaso, C.ErrorCadena) as e:
                anotar(errores, f'cadena ({nombre}): {e}')
            except Exception as e:
                anotar(errores, f'cadena ({nombre}): {type(e).__name__}: {e}')
    if negativos:
        avisos.append(f'con parámetros sorteados aparecen {negativos} probabilidades fuera de [0, 1]: '
                      'revisa las expresiones del tipo 1 − a − b')
    # Anclas: copiadas en la corrida y vigentes a la fecha de la corrida.
    propias = corrida.anclas()
    ctx = corrida.contexto()
    fecha = ctx.get('corrida', {}).get('fecha')
    for aid, ids in sorted(m.anclas_usadas().items()):
        if aid not in propias:
            errores.append(f'ancla {aid}: no está copiada en anclas/ (statfish anclas --corrida … --copiar)')
            continue
        an, _ = propias[aid]
        if isinstance(fecha, datetime.date):
            estado, vence = CTX.estado_ancla(an, fecha)
            if estado == 'vencida':
                avisos.append(f'ancla {aid}: venció el {vence}, antes de la fecha de la corrida')
        for did in ids:
            x = m.dist.get(did)
            if x is not None and x.fuente == ('ancla', aid) and isinstance(an.get('valores'), dict):
                for val, p in x.valores:
                    if val in an['valores'] and abs(p - an['valores'][val] / 100) > 0.01:
                        avisos.append(f'distribución {did}: «{val}» = {p} se aparta más de 1 pp del ancla '
                                      f'({an["valores"][val]} %)')
    # Patrones citados por las reglas.
    ids_patrones = {p['id'] for p in CTX.leer_patrones()}
    for r in m.reglas.values():
        if r.patron and r.patron not in ids_patrones:
            avisos.append(f'regla {r.id}: el patrón {r.patron} no está en el catálogo')
    # Lectura: cifras a mano.
    if corrida.existe('lectura.md'):
        avisos += INF.cifras_a_mano(M.leer_texto(corrida.ruta('lectura.md')))
    return errores, avisos


def _clave(v):
    return ('b', v) if isinstance(v, bool) else ('v', v)


def cmd_validar(a):
    corrida = M.Corrida(a.corrida)
    try:
        m = corrida.modelo()
    except M.ErrorModelo as e:
        for x in e.errores:
            print(f'  ✗ {x}')
        for x in e.avisos:
            print(f'  ⚠ {x}')
        print(f'{len(e.errores)} errores')
        return 1
    errores, avisos = validar(corrida, m)
    for x in errores:
        print(f'  ✗ {x}')
    for x in avisos:
        print(f'  ⚠ {x}')
    print(f'{len(m.variables)} variables, {len(m.parametros)} parámetros, {len(m.distribuciones)} distribuciones, '
          f'{len(m.reglas)} reglas ({len(m.fricciones)} de fricción), {len(m.estados)} estados, '
          f'{len(m.perfiles)} perfiles, {len(m.factores)} factores, {len(m.hipotesis)} hipótesis')
    print('válido' if not errores else f'{len(errores)} errores', f'· {len(avisos)} avisos')
    return 1 if errores else 0


# --------------------------------------------------------------------------------------------
# elicitar combinar
# --------------------------------------------------------------------------------------------
def cmd_elicitar(a):
    corrida = M.Corrida(a.corrida)
    base = corrida.ruta('elicitacion')
    archivos = sorted(f for f in os.listdir(base) if f.startswith('k') and f.endswith('.json')) if os.path.isdir(base) else []
    if not archivos:
        _err('no hay elicitacion/k*.json: lanza antes el agente statfish:elicitador K veces')
        return 1
    ks = [M.leer_json(os.path.join(base, f)) for f in archivos]
    params = {}
    for k in ks:
        for pid, v in k.get('parametros', {}).items():
            params.setdefault(pid, []).append((float(v['p10']), float(v['p50']), float(v['p90'])))
    dists = {}
    for k in ks:
        for did, v in k.get('distribuciones', {}).items():
            dists.setdefault(did, []).append((v['valores'], v.get('kappa')))
    salida = {'k': len(ks), 'archivos': archivos, 'parametros': {}, 'distribuciones': {}}
    jsds = []
    for pid, lista in params.items():
        r = I.combinar_binarias(lista)
        salida['parametros'][pid] = r
        if r['jsd'] is not None:
            jsds.append((r['jsd'], pid))
        if len(lista) != len(ks):
            r['aviso'] = f'solo {len(lista)} de {len(ks)} elicitaciones lo responden'
    for did, lista in dists.items():
        r = I.combinar_categoricas(lista)
        salida['distribuciones'][did] = r
        if r['jsd'] is not None:
            jsds.append((r['jsd'], did))
    salida['jsd_max'] = max(jsds)[0] if jsds else None
    salida['inestables'] = [x for j, x in sorted(jsds, reverse=True) if j > I.UMBRAL_JSD]
    CR.escribir(os.path.join(base, 'combinada.json'), M.json_estable(salida))
    print(f'K = {len(ks)} elicitaciones: {len(params)} parámetros y {len(dists)} distribuciones → elicitacion/combinada.json')
    if salida['jsd_max'] is not None:
        print(f'JSD máxima: {util.dec(salida["jsd_max"], 3)} (umbral {util.dec(I.UMBRAL_JSD, 2)})')
    for x in salida['inestables']:
        print(f'  ⚠ {x}: las elicitaciones no coinciden (JSD > 0,05); revisa la definición o busca un ancla')
    if a.toml:
        print()
        for pid, r in salida['parametros'].items():
            print(f'[[parametros]]\nid = "{pid}"\np50 = {r["p50"]!r}\np10 = {r["p10"]!r}\np90 = {r["p90"]!r}\n'
                  f'fuente = "prior:elicitacion"\n')
        for did, r in salida['distribuciones'].items():
            vals = ', '.join(f'{_clave_toml(v)} = {p!r}' for v, p in r['valores'].items())
            print(f'[[distribuciones]]\nid = "{did}"\nvalores = {{ {vals} }}\nkappa = {r["kappa"]!r}\n'
                  f'fuente = "prior:elicitacion"\n')
    return 0


def _clave_toml(k):
    return util._clave(k)


# --------------------------------------------------------------------------------------------
# correr
# --------------------------------------------------------------------------------------------
def correr(corrida, semilla=None, rapido=False, repo=None, reusar_evidencia=False, silencioso=False):
    m = _cargar(corrida)
    errores, avisos = validar(corrida, m, n=1500, sorteos=4)
    if errores:
        _err('el modelo no pasa validar:')
        for x in errores:
            print(f'  ✗ {x}', file=sys.stderr)
        return 1
    log = CR.Bitacora(silencioso)
    out = CR.calcular(m, semilla=semilla, rapido=rapido, bitacora=log)
    res = out['resultados']
    ctx = corrida.contexto()
    # Evidencia: se verifica contra el repo, salvo que se reuse la guardada (reproducir).
    ruta_ev = corrida.ruta('salida', 'evidencia.json')
    if reusar_evidencia and os.path.exists(ruta_ev):
        ev = M.leer_json(ruta_ev)
    else:
        ev = EV.verificar(corrida, repo)
    CR.escribir(corrida.ruta('salida', 'usuarios.json'), M.json_estable(out['usuarios']))
    CR.escribir(corrida.ruta('salida', 'trazas.json'), M.json_estable(out['trazas']))
    CR.escribir(corrida.ruta('salida', 'resultados.json'), M.json_estable(res))
    CR.escribir(ruta_ev, M.json_estable(ev))
    hallazgos = (corrida.toml('hallazgos.toml') or {}).get('hallazgos', [])
    relatos = (corrida.toml('relatos.toml') or {}).get('relatos', [])
    lectura = M.leer_texto(corrida.ruta('lectura.md')) if corrida.existe('lectura.md') else ''
    fecha = ctx.get('corrida', {}).get('fecha')
    anclas = {}
    for aid, (an, _) in corrida.anclas().items():
        if isinstance(fecha, datetime.date):
            estado, vence = CTX.estado_ancla(an, fecha)
        else:
            estado, vence = 'sin fecha de corrida', None
        anclas[aid] = (an, estado, vence)
    elic = None
    if corrida.existe('elicitacion/combinada.json'):
        elic = M.leer_json(corrida.ruta('elicitacion', 'combinada.json'))
    texto, err = INF.generar(m, res, ctx, lectura, ev, hallazgos, relatos, anclas, elic, out['usuarios'], out['trazas'])
    borradores, err2 = INF.issues(res, ctx, hallazgos)
    err += err2
    if err:
        _err('hay marcadores que no se resuelven:')
        for x in err:
            print(f'  ✗ {x}', file=sys.stderr)
        return 1
    CR.escribir(corrida.ruta('informe.md'), texto)
    salidas = ['salida/usuarios.json', 'salida/trazas.json', 'salida/resultados.json', 'salida/evidencia.json',
               'informe.md']
    dir_issues = corrida.ruta('salida', 'issues')
    if os.path.isdir(dir_issues):
        shutil.rmtree(dir_issues)
    for hid, cuerpo in sorted(borradores.items()):
        CR.escribir(os.path.join(dir_issues, f'{hid}.md'), cuerpo)
        salidas.append(f'salida/issues/{hid}.md')
    man = CR.manifiesto(corrida, res['semilla'], rapido, salidas)
    CR.escribir(corrida.ruta('manifiesto.json'), M.json_estable(man))
    if not silencioso:
        for x in avisos:
            print(f'  ⚠ {x}', file=sys.stderr)
        met = res['metricas']
        print('métricas (p50): ' + ', '.join(f'{k} = {util.pct(v, 2)}' for k, v in met.items()))
        cp, ca = res['cobertura']['pares'], res['cobertura']['arcos']
        print(f'cobertura: {cp["cubiertos"]}/{cp["universo"]} pares, {ca["cubiertos_total"]}/{ca["universo"]} arcos')
        print(f'evidencia: {ev["resumen"].get("vigente", 0)} vigentes de {ev["resumen"]["citas"]} citas')
        print(f'escrito: informe.md, manifiesto.json, {", ".join(s for s in salidas if s.startswith("salida/"))}')
    return 0


def cmd_correr(a):
    return correr(M.Corrida(a.corrida), a.semilla, a.rapido, a.repo)


# --------------------------------------------------------------------------------------------
# reproducir
# --------------------------------------------------------------------------------------------
def cmd_reproducir(a):
    corrida = M.Corrida(a.corrida)
    if not corrida.existe('manifiesto.json'):
        _err('la corrida no tiene manifiesto.json: córrela primero con `statfish correr`')
        return 1
    man = M.leer_json(corrida.ruta('manifiesto.json'))
    informe = {'motor_guardado': man['motor'], 'motor_actual': M.VERSION_MOTOR, 'entradas_cambiadas': [],
               'salidas': {}, 'evidencia': {}, 'hallazgos': []}
    for r, h in man['entradas'].items():
        if not corrida.existe(r):
            informe['entradas_cambiadas'].append(f'{r} (ya no está)')
        elif CR.sha256(corrida.ruta(r)) != h:
            informe['entradas_cambiadas'].append(r)
    nuevas = [r for r in corrida.archivos_entrada() if r not in man['entradas'] and r != 'manifiesto.json']
    informe['entradas_cambiadas'] += [f'{r} (nueva)' for r in nuevas]
    with tempfile.TemporaryDirectory(prefix='statfish-') as tmp:
        copia = os.path.join(tmp, 'corrida')
        shutil.copytree(corrida.raiz, copia, ignore=shutil.ignore_patterns('informe.md', 'manifiesto.json'))
        for x in os.listdir(os.path.join(copia, 'salida')) if os.path.isdir(os.path.join(copia, 'salida')) else []:
            if x != 'evidencia.json':
                p = os.path.join(copia, 'salida', x)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        codigo = correr(M.Corrida(copia), man['semilla'], man['rapido'], reusar_evidencia=True, silencioso=True)
        if codigo:
            _err('no se pudo recalcular la corrida')
            return 1
        iguales = True
        for r in man['salidas']:
            if r == 'salida/evidencia.json':
                continue
            nuevo = os.path.join(copia, r)
            ok = os.path.exists(nuevo) and corrida.existe(r) and CR.sha256(nuevo) == CR.sha256(corrida.ruta(r))
            informe['salidas'][r] = 'idéntico' if ok else 'distinto'
            iguales &= ok
    # Evidencia contra el commit actual.
    ev = EV.verificar(corrida, a.repo)
    guardada = M.leer_json(corrida.ruta('salida', 'evidencia.json')) \
        if corrida.existe('salida/evidencia.json') else {'citas': []}
    antes = {(c['cita'], c['extracto']): c['estado'] for c in guardada['citas']}
    cambios = []
    for c in ev['citas']:
        previo = antes.get((c['cita'], c['extracto']))
        if previo and previo != c['estado']:
            cambios.append({'cita': c['cita'], 'antes': previo, 'ahora': c['estado'], 'nueva_cita': c.get('nueva_cita')})
    informe['evidencia'] = {'commit_corrida': man.get('commit', ''), 'commit_actual': ev.get('commit_actual'),
                            'resumen': ev['resumen'], 'cambios': list({x['cita']: x for x in cambios}.values())}
    informe['hallazgos'] = EV.hallazgos_afectados(corrida, ev)
    CR.escribir(corrida.ruta('salida', 'reproduccion.json'), M.json_estable(informe))
    print(f'motor: guardado {man["motor"]}, actual {M.VERSION_MOTOR}')
    if informe['entradas_cambiadas']:
        print('entradas que cambiaron desde la corrida: ' + ', '.join(informe['entradas_cambiadas']))
    for r, e in informe['salidas'].items():
        print(f'  {"✓" if e == "idéntico" else "✗"} {r}: {e}')
    print(f'evidencia contra {(ev.get("commit_actual") or "—")[:7]} (corrida: {man.get("commit", "")[:7]}): '
          + ', '.join(f'{v} {k}' for k, v in ev['resumen'].items() if k not in ('citas', 'unicas', 'vigentes_unicas')))
    for c in informe['evidencia']['cambios']:
        print(f'  · {c["cita"]}: {c["antes"]} → {c["ahora"]}' + (f' ({c["nueva_cita"]})' if c.get('nueva_cita') else ''))
    for h in informe['hallazgos']:
        print(f'  ⚠ hallazgo {h["id"]}: {h["aviso"]} ({", ".join(h["citas_vencidas"])})')
    print('reproducible: los mismos bytes' if iguales else 'NO reproducible: hay salidas distintas')
    return 0 if iguales else 1


# --------------------------------------------------------------------------------------------
# comparar
# --------------------------------------------------------------------------------------------
def cmd_comparar(a):
    ra = M.leer_json(os.path.join(a.a, 'salida', 'resultados.json'))
    rb = M.leer_json(os.path.join(a.b, 'salida', 'resultados.json'))
    salida = {'metricas': {}, 'desenlaces_jsd': None, 'perfiles_jsd': None, 'reglas': {}, 'top3': {}, 'hallazgos': {}}
    for k in sorted(set(ra['metricas']) | set(rb['metricas'])):
        va, vb = ra['metricas'].get(k), rb['metricas'].get(k)
        salida['metricas'][k] = {'a': va, 'b': vb, 'diferencia': None if va is None or vb is None else vb - va}
    ds = list(dict.fromkeys(list(ra['desenlaces']) + list(rb['desenlaces'])))
    salida['desenlaces_jsd'] = I.jsd([[ra['desenlaces'].get(d, 0) for d in ds], [rb['desenlaces'].get(d, 0) for d in ds]])
    ps = list(dict.fromkeys(list(ra['perfiles']) + list(rb['perfiles'])))
    salida['perfiles_jsd'] = I.jsd([[ra['perfiles'].get(s, {}).get('masa', 0) for s in ps],
                                    [rb['perfiles'].get(s, {}).get('masa', 0) for s in ps]])
    for r in sorted(set(ra['reglas']) | set(rb['reglas'])):
        pa = ra['reglas'].get(r, {}).get('perdida')
        pb = rb['reglas'].get(r, {}).get('perdida')
        salida['reglas'][r] = {'a': pa, 'b': pb, 'estado': 'nueva' if pa is None else ('desaparece' if pb is None else 'en las dos')}
    top = lambda res: [r for r, _ in sorted(res['reglas'].items(), key=lambda kv: -kv[1]['perdida'])[:3]]
    salida['top3'] = {'a': top(ra), 'b': top(rb)}
    for nombre, ruta in (('a', a.a), ('b', a.b)):
        h = M.Corrida(ruta).toml('hallazgos.toml') or {}
        salida['hallazgos'][nombre] = sorted(x.get('id', '') for x in h.get('hallazgos', []))
    if a.json:
        print(json.dumps(salida, ensure_ascii=False, indent=1))
        return 0
    print(f'| Métrica | {os.path.basename(os.path.normpath(a.a))} | {os.path.basename(os.path.normpath(a.b))} | Diferencia (pp) |')
    print('|---|---|---|---|')
    for k, v in salida['metricas'].items():
        f = lambda x: '—' if x is None else util.pct(x, 2)
        print(f'| {k} | {f(v["a"])} | {f(v["b"])} | {"—" if v["diferencia"] is None else util.pp(v["diferencia"])} |')
    print(f'\nJSD de los desenlaces: {util.dec(salida["desenlaces_jsd"], 4)} · de los perfiles: '
          f'{util.dec(salida["perfiles_jsd"], 4)} (umbral 0,05)')
    print(f'Tres fricciones principales: {", ".join(salida["top3"]["a"])} → {", ".join(salida["top3"]["b"])}')
    for r, v in salida['reglas'].items():
        if v['estado'] != 'en las dos':
            print(f'  regla {r}: {v["estado"]}')
    ha, hb = set(salida['hallazgos']['a']), set(salida['hallazgos']['b'])
    for x in sorted(hb - ha):
        print(f'  hallazgo nuevo: {x}')
    for x in sorted(ha - hb):
        print(f'  hallazgo que desaparece: {x}')
    return 0


# --------------------------------------------------------------------------------------------
# calibrar
# --------------------------------------------------------------------------------------------
def cmd_calibrar(a):
    corrida = M.Corrida(a.corrida)
    try:
        m = M.cargar_modelo(corrida.ruta('modelo.toml'))
    except M.ErrorModelo as e:
        for x in e.errores:
            print(f'  ✗ {x}')
        return 1
    ruta = a.conteos if os.path.isabs(a.conteos) or os.path.exists(a.conteos) else corrida.ruta(a.conteos)
    import tomllib
    with open(ruta, 'rb') as f:
        conteos = tomllib.load(f)
    if os.path.abspath(ruta) != corrida.ruta('conteos.toml'):
        shutil.copy(ruta, corrida.ruta('conteos.toml'))
    cal = CAL.calibrar(m, conteos)
    for x in cal['avisos']:
        print(f'  ⚠ {x}')
    datos = CAL.a_calibracion_toml(cal)
    CR.escribir(corrida.ruta('calibracion.toml'), util.a_toml(
        datos, 'Parámetros posteriores: los escribe `statfish calibrar` desde conteos.toml.\n'
               'statfish correr los aplica sobre los priors de modelo.toml.'))
    # Efecto en las métricas: p50 del prior contra p50 de la posterior, con la misma población.
    red, cad = R.Red(m), C.Cadena(m)
    fs = MU.compilar_metricas(m)
    US = red.uniformes(random.Random(m.corrida['semilla'] + CR.SEMILLA_HIPOTESIS), min(m.corrida['usuarios_hipotesis'], 20_000))
    t_prior = M.theta_p50(m)
    cambios_p = {pid: r['posterior']['p50'] for pid, r in cal['parametros'].items()}
    cambios_d = {did: [(v, r['posterior']['valores'][v]) for v, _ in m.dist[did].valores]
                 for did, r in cal['distribuciones'].items()}
    t_post = t_prior.con(cambios_p, cambios_d)
    antes = MU.metricas(fs, MU.poblacion(red, cad, m, t_prior, US)['desenlaces'])
    despues = MU.metricas(fs, MU.poblacion(red, cad, m, t_post, US)['desenlaces'])
    informe = {'parametros': cal['parametros'], 'distribuciones': cal['distribuciones'],
               'metricas': {k: {'prior': antes[k], 'posterior': despues[k], 'diferencia': despues[k] - antes[k]}
                            for k in antes}}
    CR.escribir(corrida.ruta('salida', 'calibracion.json'), M.json_estable(informe))
    print('| Parámetro | Prior p50 [p10–p90] | n | Posterior p50 [p10–p90] |')
    print('|---|---|---|---|')
    for pid, r in cal['parametros'].items():
        p, q = r['prior'], r['posterior']
        print(f'| {pid} | {util.pct(p["p50"], 2)} [{util.pct(p["p10"], 2)}–{util.pct(p["p90"], 2)}] | {r["n"]} | '
              f'{util.pct(q["p50"], 2)} [{util.pct(q["p10"], 2)}–{util.pct(q["p90"], 2)}] |')
    for did, r in cal['distribuciones'].items():
        print(f'| {did} (κ {util.dec(r["prior"]["kappa"], 0)} → {util.dec(r["posterior"]["kappa"], 0)}) | '
              + ', '.join(f'{v} {util.pct(p, 1)}' for v, p in r['prior']['valores'].items()) + f' | {r["n"]} | '
              + ', '.join(f'{v} {util.pct(p, 1)}' for v, p in r['posterior']['valores'].items()) + ' |')
    print('\nEfecto en las métricas (p50, misma población):')
    for k, v in informe['metricas'].items():
        print(f'  {k}: {util.pct(v["prior"], 2)} → {util.pct(v["posterior"], 2)} ({util.pp(v["diferencia"])} pp)')
    print('escrito: calibracion.toml, salida/calibracion.json · corre `statfish correr` para el informe calibrado')
    return 0


# --------------------------------------------------------------------------------------------
def main(argv=None):
    p = argparse.ArgumentParser(prog='statfish', description='Motor determinista de Statfish (sin LLM, sin red).')
    sub = p.add_subparsers(dest='comando', required=True)

    s = sub.add_parser('contexto', help='detecta el stack y escribe contexto.toml')
    s.add_argument('repo')
    s.add_argument('--corrida', help='carpeta de la corrida (por defecto <repo>/statfish/<fecha>-<slug>)')
    s.add_argument('--slug')
    s.add_argument('--pregunta', required=True)
    s.add_argument('--pais', default='CL')
    s.add_argument('--publico', default='')
    s.add_argument('--fecha', help='AAAA-MM-DD (por defecto hoy)')
    s.set_defaults(f=cmd_contexto)

    s = sub.add_parser('patrones', help='patrones del catálogo que aplican al contexto')
    s.add_argument('corrida')
    s.add_argument('--buscar', action='store_true', help='busca las pistas de cada patrón en el repo')
    s.add_argument('--repo')
    s.add_argument('--catalogo', help=argparse.SUPPRESS)
    s.add_argument('--json', action='store_true')
    s.set_defaults(f=cmd_patrones)

    s = sub.add_parser('anclas', help='lista el registro de anclas y avisa las vencidas')
    s.add_argument('--pais')
    s.add_argument('--corrida')
    s.add_argument('--copiar', action='store_true', help='copia a la corrida las anclas que usa y le faltan')
    s.add_argument('--hoy', help='AAAA-MM-DD (por defecto hoy)')
    s.add_argument('--estricto', action='store_true', help='sale con 1 si hay anclas vencidas')
    s.add_argument('--registro', help=argparse.SUPPRESS)
    s.set_defaults(f=cmd_anclas)

    s = sub.add_parser('evidencia', help='verifica cada cita contra el commit actual')
    s.add_argument('corrida')
    s.add_argument('--repo')
    s.set_defaults(f=cmd_evidencia)

    s = sub.add_parser('validar', help='revisa el modelo: esquema, sumas, restricciones y ramas')
    s.add_argument('corrida')
    s.set_defaults(f=cmd_validar)

    s = sub.add_parser('elicitar', help='junta las K elicitaciones independientes')
    ss = s.add_subparsers(dest='sub', required=True)
    s2 = ss.add_parser('combinar')
    s2.add_argument('corrida')
    s2.add_argument('--toml', action='store_true', help='imprime los bloques para modelo.toml')
    s2.set_defaults(f=cmd_elicitar)

    s = sub.add_parser('correr', help='calcula usuarios, trazas, resultados, informe y manifiesto')
    s.add_argument('corrida')
    s.add_argument('--semilla', type=int)
    s.add_argument('--rapido', action='store_true', help='poblaciones más chicas, para iterar')
    s.add_argument('--repo')
    s.set_defaults(f=cmd_correr)

    s = sub.add_parser('reproducir', help='recalcula y compara byte a byte; verifica la evidencia')
    s.add_argument('corrida')
    s.add_argument('--repo')
    s.set_defaults(f=cmd_reproducir)

    s = sub.add_parser('comparar', help='diferencias entre dos corridas')
    s.add_argument('a')
    s.add_argument('b')
    s.add_argument('--json', action='store_true')
    s.set_defaults(f=cmd_comparar)

    s = sub.add_parser('calibrar', help='actualiza los parámetros con conteos reales (conjugada)')
    s.add_argument('corrida')
    s.add_argument('--conteos', required=True)
    s.set_defaults(f=cmd_calibrar)

    a = p.parse_args(argv)
    try:
        return a.f(a) or 0
    except M.ErrorModelo as e:
        for x in e.errores:
            print(f'  ✗ {x}', file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        _err(f'no existe {e.filename}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
