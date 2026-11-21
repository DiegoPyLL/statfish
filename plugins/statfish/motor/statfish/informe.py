"""informe.md: tablas fijas a partir de resultados.json y la lectura con sus marcadores resueltos.

Ninguna cifra se escribe a mano. Un marcador {{ruta|filtro}} toma el valor de resultados.json (o de
contexto.toml con `contexto.`) y lo formatea:

    {{metricas.perdida_por_codigo|pct}}            → 1,3 %
    {{reglas.R9.perdida|mil}}                      → 3,59   (de cada 1.000)
    {{ hipotesis.todos.perdida_por_codigo / metricas.perdida_por_codigo |pct:0}}

Filtros: pct[:d], pp[:d], mil[:d], dec[:d], num[:cifras], entero, texto. Sin filtro: entero para
enteros, num para decimales y el texto tal cual.
"""
import re

from . import util

MARCADOR = re.compile(r'\{\{(.+?)\}\}', re.S)
CIFRA_A_MANO = re.compile(r'(?<![\w{.])\d+(?:[.,]\d+)?\s?%|(?<![\w{.,])\d+,\d+(?![\w])')
_TOKEN = re.compile(r'\s*(\(|\)|\+|-(?!\S*[A-Za-z_])|\*|/|[^\s()]+)')


class ErrorMarcador(ValueError):
    pass


def _buscar(espacio, ruta):
    actual = espacio
    for parte in ruta.split('.'):
        if isinstance(actual, dict) and parte in actual:
            actual = actual[parte]
        elif isinstance(actual, list) and parte.isdigit() and int(parte) < len(actual):
            actual = actual[int(parte)]
        else:
            raise ErrorMarcador(f'«{ruta}»: no existe «{parte}»')
    return actual


def _evaluar(espacio, cuerpo):
    """Ruta sola, o expresión con + - * / y paréntesis separados por espacios."""
    cuerpo = cuerpo.strip()
    if ' ' not in cuerpo:
        return _buscar(espacio, cuerpo)
    tokens = cuerpo.split()
    pos = [0]

    def ver():
        return tokens[pos[0]] if pos[0] < len(tokens) else None

    def tomar():
        t = ver()
        pos[0] += 1
        return t

    def atomo():
        t = tomar()
        if t is None:
            raise ErrorMarcador(f'«{cuerpo}»: expresión incompleta')
        if t == '(':
            v = suma()
            if tomar() != ')':
                raise ErrorMarcador(f'«{cuerpo}»: falta «)»')
            return v
        if t == '-':
            return -atomo()
        try:
            return float(t) if any(c in t for c in '.e') else int(t)
        except ValueError:
            v = _buscar(espacio, t)
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                raise ErrorMarcador(f'«{t}» no es un número')
            return v

    def producto():
        v = atomo()
        while ver() in ('*', '/'):
            op = tomar()
            w = atomo()
            if op == '/' and w == 0:
                raise ErrorMarcador(f'«{cuerpo}»: división por cero')
            v = v * w if op == '*' else v / w
        return v

    def suma():
        v = producto()
        while ver() in ('+', '-'):
            op = tomar()
            w = producto()
            v = v + w if op == '+' else v - w
        return v

    v = suma()
    if ver() is not None:
        raise ErrorMarcador(f'«{cuerpo}»: sobra «{ver()}» (separa operadores con espacios)')
    return v


def formatear(valor, filtro):
    if filtro is None:
        if isinstance(valor, bool):
            return 'sí' if valor else 'no'
        if isinstance(valor, int):
            return util.entero(valor)
        if isinstance(valor, float):
            return util.num(valor)
        if valor is None:
            return '—'
        return str(valor)
    nombre, _, arg = filtro.partition(':')
    nombre = nombre.strip()
    if nombre == 'texto':
        return str(valor)
    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        raise ErrorMarcador(f'el filtro «{nombre}» necesita un número, no {valor!r}')
    d = int(arg) if arg.strip() else None
    if nombre == 'pct':
        return util.pct(valor, 1 if d is None else d)
    if nombre == 'pp':
        return util.pp(valor, 2 if d is None else d)
    if nombre == 'mil':
        return util.mil(valor, 2 if d is None else d)
    if nombre == 'dec':
        return util.dec(valor, 2 if d is None else d)
    if nombre == 'num':
        return util.num(valor, 3 if d is None else d)
    if nombre == 'entero':
        return util.entero(valor)
    raise ErrorMarcador(f'filtro desconocido «{nombre}»')


def resolver(texto, espacio):
    """Reemplaza cada marcador. Devuelve (texto, errores)."""
    errores = []

    def reemplazo(m):
        cuerpo, _, filtro = m.group(1).partition('|')
        try:
            return formatear(_evaluar(espacio, cuerpo), filtro.strip() or None)
        except ErrorMarcador as e:
            errores.append(str(e))
            return m.group(0)

    return MARCADOR.sub(reemplazo, texto), errores


def cifras_a_mano(texto):
    """Líneas con cifras escritas a mano fuera de los marcadores (porcentajes o decimales)."""
    avisos = []
    for i, linea in enumerate(texto.split('\n'), 1):
        limpia = MARCADOR.sub(' ', linea)
        limpia = re.sub(r'`[^`]*`', ' ', limpia)
        for m in CIFRA_A_MANO.finditer(limpia):
            avisos.append(f'lectura.md:{i}: «{m.group(0).strip()}» parece una cifra escrita a mano; usa un marcador')
    return avisos


# --------------------------------------------------------------------------------------------
# Tablas
# --------------------------------------------------------------------------------------------
def _tabla(cabecera, filas):
    if all(not c for c in cabecera):
        out = ['|' + ' |' * len(cabecera), '|' + '---|' * len(cabecera)]
    else:
        out = ['| ' + ' | '.join(cabecera) + ' |', '|' + '---|' * len(cabecera)]
    for f in filas:
        out.append('| ' + ' | '.join(str(x).replace('|', '\\|').replace('\n', ' ') for x in f) + ' |')
    return '\n'.join(out)


def _citas(evidencia, n=2):
    return ', '.join(f'`{e["cita"]}`' for e in evidencia[:n]) + (' …' if len(evidencia) > n else '')


def generar(modelo, res, ctx, lectura, evidencia, hallazgos, relatos, anclas, elicitacion, usuarios, trazas):
    """El texto completo de informe.md. Devuelve (texto, errores de marcadores)."""
    espacio = dict(res)
    espacio['contexto'] = ctx
    errores = []
    L = []
    w = L.append
    principales = modelo.informe.get('metricas_principales') or [x['id'] for x in modelo.metricas][:3]
    tm = res['textos_metricas']
    corr = ctx.get('corrida', {})
    repo = ctx.get('repo', {})
    w(f'# Statfish · {modelo.informe.get("titulo") or modelo.nombre}')
    w('')
    w(_tabla(['', ''], [
        ['Pregunta', corr.get('pregunta', '—')],
        ['Repositorio', f'`{repo.get("nombre", "—")}` @ `{repo.get("commit_corto") or repo.get("commit", "")[:7]}`'
         + (' (con cambios locales)' if repo.get('cambios_locales') else '')],
        ['Fecha', str(corr.get('fecha', '—'))],
        ['País y público', f'{corr.get("pais", "—")} · {corr.get("publico", "—")}'],
        ['Semilla y motor', f'{res["semilla"]} · statfish {res["motor"]}' + (' · corrida rápida' if res['rapido'] else '')],
        ['Población', f'{util.entero(res["tamanos"]["poblacion"])} usuarios con desenlace exacto; '
                      f'{res["usuarios"]["total"]} usuarios con traza'],
    ]))
    w('')
    w('Todas las cifras **describen el modelo, no el mercado**: salen del código, de anclas públicas y de priors '
      'con rango. Su valor está en el orden y en la evidencia de cada fricción, no en el nivel exacto.')
    if modelo.nota:
        w('')
        w(f'> {modelo.nota}')
    if lectura:
        texto, err = resolver(lectura.strip(), espacio)
        errores += err
        w('')
        w(texto)

    # Desenlaces
    w('')
    w('## Desenlaces')
    w('')
    w(_tabla(['Desenlace', 'De cada 100 llegadas'],
             [[res['textos_desenlaces'][d], util.pp(v)] for d, v in res['desenlaces'].items()]))

    # Métricas con intervalo
    w('')
    w('## Métricas con intervalo')
    w('')
    iv = res['intervalos']
    w(f'p5, p50 y p95 de {res["robustez"]["n"]} sorteos de todos los parámetros sobre '
      f'{util.entero(res["tamanos"]["usuarios_incertidumbre"])} usuarios, con números aleatorios comunes.')
    w('')
    w(_tabla(['Métrica', 'Modelo (p50)', 'p5', 'p50', 'p95'],
             [[tm[k], util.pct(res['metricas'][k], 2)] +
              ([util.pct(iv[k]['p5'], 2), util.pct(iv[k]['p50'], 2), util.pct(iv[k]['p95'], 2)] if k in iv else ['—'] * 3)
              for k in res['metricas']]))

    # Perfiles
    w('')
    w('## Perfiles')
    w('')
    filas = []
    for s, p in res['perfiles'].items():
        top = next(iter(p['reglas'].items()), None)
        peso = '—'
        if top:
            r, v = top
            peso = f'{r}: {util.mil(v["perdida"], 1)} perdidos, {util.mil(v["friccion"], 1)} con fricción'
        rango = (f'{util.pct(p["masa_p5"])} – {util.pct(p["masa_p95"])}' if p.get('masa_p5') is not None else '—')
        filas.append([s, p['nombre'], util.pct(p['masa']), rango] +
                     [util.pct(p['metricas'][k], 2) for k in principales] + [peso])
    w(_tabla(['Perfil', 'Quién', 'P(perfil)', 'p5–p95'] + [tm[k] for k in principales] +
             ['Regla que más pesa (por cada 1.000 del perfil)'], filas))

    # Reglas
    w('')
    w('## Reglas')
    w('')
    filas = []
    for rid, r in res['reglas'].items():
        regla = modelo.reglas.get(rid)
        filas.append([rid, r['texto'], util.mil(r['perdida']), util.mil(r['friccion']),
                      _citas(regla.evidencia) if regla else '—'])
    w(_tabla(['Regla', 'Qué pasa', 'Se pierden (de cada 1.000 llegadas)', 'Llegan con fricción (de cada 1.000)',
              'Evidencia'], filas))

    # Robustez
    rob = res['robustez']
    w('')
    w('## Robustez del orden')
    w('')
    w(f'En {rob["n"]} sorteos de los parámetros: con qué frecuencia cada regla queda primera o entre las tres '
      'primeras.')
    w('')
    reglas_rob = list(dict.fromkeys(list(rob['top3_perdida']) + list(rob['top3_friccion'])))
    reglas_rob.sort(key=lambda r: (-rob['top3_perdida'].get(r, 0), -rob['top3_friccion'].get(r, 0), r))
    w(_tabla(['Regla', '1.ª en pérdida', 'Entre las 3 primeras en pérdida', 'Entre las 3 primeras en fricción total'],
             [[r, util.pct(rob['top1_perdida'].get(r, 0)), util.pct(rob['top3_perdida'].get(r, 0)),
               util.pct(rob['top3_friccion'].get(r, 0))] for r in reglas_rob]))

    # Morris
    if res['morris']:
        ms = [k for k in res['morris'][0] if k not in ('parametro', 'rango')]
        orden = modelo.sensibilidad.get('ordenar_por')
        if orden in ms:
            ms = [orden] + [k for k in ms if k != orden]
        w('')
        w('## Sensibilidad (Morris)')
        w('')
        w(f'{res["tamanos"]["trayectorias"]} trayectorias y {res["tamanos"]["niveles"]} niveles, cada supuesto entre '
          'su p10 y su p90. μ* es el efecto medio, en puntos, de recorrer el rango completo; σ mide cuánto depende '
          'de los demás supuestos.')
        w('')
        cab = ['Supuesto', 'Rango probado']
        for i, k in enumerate(ms):
            cab += [f'μ* sobre {tm.get(k, k).lower()} (pp)'] + (['σ'] if i == 0 else [])
        filas = []
        for f in res['morris']:
            fila = [f'`{f["parametro"]}`', f'{util.pct_corto(f["rango"][0])}–{util.pct_corto(f["rango"][1])} %']
            for i, k in enumerate(ms):
                fila.append(util.pp(f[k]['mu_estrella']))
                if i == 0:
                    fila.append(util.pp(f[k]['sigma']))
            filas.append(fila)
        w(_tabla(cab, filas))

    # Hipótesis
    if len(res['hipotesis']) > 1:
        w('')
        w('## Hipótesis: qué cambia si se arregla')
        w('')
        w(f'Cada arreglo sobre la misma población de {util.entero(res["tamanos"]["usuarios_hipotesis"])} usuarios.')
        w('')
        w(_tabla(['Escenario'] + [tm[k] for k in principales],
                 [[h['texto']] + [util.pct(h[k], 2) for k in principales] for h in res['hipotesis'].values()]))

    # Cobertura
    cob = res['cobertura']
    cp, ca, cs = cob['pares'], cob['arcos'], cob['superficies']
    w('')
    w('## Cobertura')
    w('')
    w(_tabla(['Medida', 'Resultado', 'Cómo'], [
        [f'Pares de valores de {len(cp["factores"])} factores', f'**{cp["cubiertos"]} de {cp["universo"]}**',
         f'{res["usuarios"]["representativos"]} representativos + {res["usuarios"]["cobertura"]} de cobertura'],
        ['Arcos de la cadena de uso', f'{ca["cubiertos_sorteo"]} de {ca["universo"]} con las trazas sorteadas; '
                                      f'**{ca["cubiertos_total"]} de {ca["universo"]}** con las forzadas',
         'Camino más probable por cada arco que faltaba'],
        ['Superficies (rutas, formularios, endpoints y reglas)',
         f'{len(cs["vistas_sorteo"])} de {len(cs["universo"])} en el sorteo; **{len(cs["vistas_total"])} de '
         f'{len(cs["universo"])}** en total; {cs["clases_cubiertas"]} de {cs["clases"]} clases',
         'Las que faltan, con su clase de equivalencia, abajo'],
    ]))
    if cs['faltan_por_clase']:
        w('')
        for f in cs['faltan_por_clase']:
            por = ', '.join(f'`{x}`' for x in f['cubierta_por'][:3])
            w(f'- `{f["superficie"]}` ({f["clase"]}): ' +
              (f'cubierta por su clase ({por}).' if f['cubierta_por'] else '**sin cubrir, ni por clase**.'))

    # Fidelidad
    fid = res['fidelidad']
    w('')
    w('## Fidelidad del generador')
    w('')
    w('¿Reproduce la red lo que se declaró? No dice si los pesos son correctos: dice que el generador hace lo que '
      'el modelo declara (F12: |declarada − muestra| ≤ 3σ).')
    w('')
    if fid['declaradas']:
        w(_tabla(['Variable', 'Declarada', 'En la muestra', 'n', 'Dentro de 3σ'],
                 [[f['variable'], util.pct(f['declarada'], 2), '—' if f['muestra'] is None else util.pct(f['muestra'], 2),
                   util.entero(f['n']), 'sí' if f['dentro'] else '**no**'] for f in fid['declaradas']]))
        w('')
    a = fid['automatica']
    w(f'Revisión automática de cada caso de la red: {a["revisadas"]} valores, {a["fuera"]} fuera de 3σ.')
    for f in a['fuera_de_rango'][:10]:
        w(f'- **{f["variable"]}**, caso {f["caso"]}, «{f["valor"]}»: declarada {util.pct(f["declarada"], 2)}, '
          f'muestra {util.pct(f["muestra"], 2)} (n = {util.entero(f["n"])}).')
    viol = res['restricciones']
    w('')
    w(f'Restricciones duras: {viol["revisadas"]} revisadas sobre los {res["usuarios"]["total"]} usuarios, '
      f'{len(viol["violaciones"])} violaciones.')

    # Evidencia
    if evidencia:
        r = evidencia['resumen']
        w('')
        w('## Evidencia')
        w('')
        nombres_ev = {'vigente': 'vigentes', 'desplazada': 'desplazadas', 'vencida': 'vencidas',
                      'sin_extracto': 'sin extracto', 'no_verificable': 'no verificables'}
        estados = ', '.join(f'{r[k]} {nombres_ev[k]}' for k in nombres_ev if r.get(k))
        prec = evidencia.get('precision')
        w(f'{r["citas"]} citas ({r["unicas"]} distintas) verificadas contra `{(evidencia.get("commit_actual") or "—")[:7]}`: '
          f'{estados}.' + (f' Precisión automática: {util.pct(prec)}.' if prec is not None else ''))
        malas = [c for c in evidencia['citas'] if c['estado'] != 'vigente']
        vistas = set()
        for c in malas:
            if (c['cita'], c['estado']) in vistas:
                continue
            vistas.add((c['cita'], c['estado']))
            extra = f' → `{c["nueva_cita"]}`' if c.get('nueva_cita') else ''
            w(f'- `{c["cita"]}` ({c["estado"]}{extra}): {c.get("motivo", "")}. En {c["origen"]}.')

    # Fuentes
    w('')
    w('## Fuentes de los pesos')
    w('')
    conteo = {}
    for x in modelo.parametros + modelo.distribuciones:
        if getattr(x, 'interruptor', False):
            continue
        conteo[x.fuente[0]] = conteo.get(x.fuente[0], 0) + 1
    nombres = {'ancla': 'anclas públicas', 'prior': 'priors elicitados', 'codigo': 'fijados por el código',
               'definicion': 'por definición'}
    w('Parámetros y distribuciones por fuente: ' +
      ', '.join(f'{v} {nombres[k]}' for k, v in sorted(conteo.items(), key=lambda kv: -kv[1])) + '.')
    if elicitacion:
        k = elicitacion.get('k')
        jmax = elicitacion.get('jsd_max')
        w('')
        w(f'Elicitación: K = {k}.' + (f' Divergencia de Jensen-Shannon máxima entre elicitaciones: {util.dec(jmax, 3)} '
                                     f'(umbral 0,05).' if jmax is not None else ' Con K = 1 no hay estabilidad que medir.'))
    usadas = modelo.anclas_usadas()
    if usadas:
        w('')
        filas = []
        for aid in sorted(usadas):
            dato = anclas.get(aid)
            if dato is None:
                filas.append([f'`{aid}`', '**no está en la corrida**', '—', '—', ', '.join(sorted(usadas[aid]))])
                continue
            an, estado, vence = dato
            url = an.get('url', '')
            como_ancla = sorted(i for i in usadas[aid] if getattr(modelo.param.get(i) or modelo.dist.get(i), 'fuente', None) == ('ancla', aid))
            informa = sorted(set(usadas[aid]) - set(como_ancla))
            uso = '; '.join(x for x in (('ancla de ' + ', '.join(como_ancla)) if como_ancla else '',
                                         ('informa ' + ', '.join(informa)) if informa else '') if x)
            filas.append([f'`{aid}`', f'[{an.get("titulo", an.get("fuente", aid))}]({url})' if url else an.get('titulo', ''),
                          str(an.get('consultado', '—')), f'{vence} ({estado})' if vence else estado, uso])
        w(_tabla(['Ancla', 'Fuente', 'Consultada', 'Vence', 'Uso'], filas))

    # Hallazgos
    if hallazgos:
        w('')
        w('## Hallazgos')
        w('')
        filas = []
        for h in hallazgos:
            resumen, err = resolver(h.get('resumen', ''), espacio)
            errores += [f'hallazgo {h.get("id")}: {e}' for e in err]
            filas.append([h.get('id', ''), h.get('regla', '—'), h.get('estado', '—'),
                          ', '.join(h.get('perfiles', [])) or '—', resumen])
        w(_tabla(['Hallazgo', 'Regla', 'Estado', 'Perfiles', 'Resumen'], filas))

    # Anexos
    w('')
    w('## Anexo A: usuarios')
    w('')
    w('Los atributos los sortea el motor con la semilla; los nombres son sintéticos y el relato, si lo hay, se '
      'escribió después, solo con esos atributos.')
    w('')
    relato = {r['id']: r for r in (relatos or [])}
    pm = principales[0]
    f_metrica = next(x for x in modelo.metricas if x['id'] == pm)
    from .muestreo import compilar_metricas, metricas as _met
    fs = [f for f in compilar_metricas(modelo) if f[0] == pm]
    desenlace = {t['id']: t['desenlace'] for t in trazas if not t['forzada']}
    moda = {}
    for k in (usuarios[0]['factores'] if usuarios else {}):
        cuenta = {}
        for x in usuarios:
            cuenta[str(x['factores'][k])] = cuenta.get(str(x['factores'][k]), 0) + 1
        moda[k] = sorted(cuenta.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    filas = []
    for x in usuarios:
        peso = '—' if x['peso'] is None else util.cientifica(x['peso'])
        fac = ', '.join(f'{k}={v}' for k, v in x['factores'].items() if str(v) != moda[k]) or '—'
        r = relato.get(x['id'])
        texto_relato = '—'
        if r:
            texto_relato = r.get('texto', '')
            if r.get('huella') and r['huella'] != x['huella']:
                texto_relato = f'*(desactualizado: el usuario cambió)* {texto_relato}'
        filas.append([x['id'], x['tipo'], peso, x['perfil'], x['nombre'] or '—', fac,
                      res['textos_desenlaces'].get(desenlace.get(x['id']), '—'),
                      util.pct(_met(fs, x['esperado'])[pm]), texto_relato])
    w(_tabla(['Id', 'Cómo se creó', 'Peso p/q', 'Perfil', 'Nombre (sintético)', 'Lo distinto (factores)', 'Desenlace sorteado',
              f'{f_metrica["texto"]} esperado', 'Relato'], filas))
    w('')
    w('## Anexo B: trazas sorteadas')
    w('')
    w('Cada paso separa la acción (sorteada), la consecuencia (la regla del código) y la percepción (las cuatro '
      'preguntas del recorrido cognitivo; «—» quiere decir que las cuatro dan «sí»).')
    for t in trazas:
        if t['forzada']:
            continue
        w('')
        w(f'#### {t["id"]} · {res["textos_desenlaces"].get(t["desenlace"], t["desenlace"])} · '
          f'P(camino) = {util.num(t["prob_camino"])}')
        w('')
        filas = []
        for i, p in enumerate(t['pasos'], 1):
            ev = f'{p["regla"]}: ' + ', '.join(f'`{e}`' for e in (p['evidencia'] or [])[:2]) if p['regla'] else ''
            cw = '—' if all(c == 'sí' for c in p['cw']) else '/'.join(p['cw'])
            filas.append([i, p['estado'], '—' if p['sorteo'] is None else util.num(p['sorteo']), util.num(p['prob']),
                          p['accion'] + (f' ↳ *{p["nota_cw"]}*' if p['nota_cw'] else ''), ev, cw])
        w(_tabla(['#', 'Estado', 'Sorteo', 'P', 'Acción', 'Regla y evidencia', 'CW'], filas))
    forz = [t for t in trazas if t['forzada']]
    if forz:
        w('')
        w('## Anexo C: trazas forzadas')
        w('')
        w('Por cada arco que las trazas sorteadas no recorrieron, el camino más probable que pasa por él (F15).')
        w('')
        w(_tabla(['Arco que faltaba', 'Usuario', 'P(camino)', 'Desenlace', 'Camino'],
                 [[f'{t["arco"][0]}: {t["arco"][1]}', t['id'], util.num(t['prob_camino'], 2),
                   res['textos_desenlaces'].get(t['desenlace'], t['desenlace']),
                   ' → '.join(p['accion'] for p in t['pasos'][1:])] for t in forz]))
    return '\n'.join(L) + '\n', errores


def issues(res, ctx, hallazgos):
    """Borradores de issue: {id: texto} con los marcadores resueltos."""
    espacio = dict(res)
    espacio['contexto'] = ctx
    salida, errores = {}, []
    for h in hallazgos:
        if not h.get('cuerpo'):
            continue
        cuerpo, err = resolver(h['cuerpo'].strip(), espacio)
        errores += [f'hallazgo {h.get("id")}: {e}' for e in err]
        titulo, err = resolver(h.get('titulo', h.get('id', '')), espacio)
        errores += [f'hallazgo {h.get("id")}: {e}' for e in err]
        salida[h['id']] = f'# {titulo}\n\n{cuerpo}\n'
    return salida, errores
