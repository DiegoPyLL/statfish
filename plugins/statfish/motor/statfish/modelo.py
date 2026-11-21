"""Carga y validación estática de una corrida: modelo.toml y los archivos que la acompañan.

El formato está en referencias/formato-modelo.md. Aquí no se muestrea nada: se leen los archivos,
se revisan las claves y las expresiones, y se arman los parámetros (theta) en p50, aplanados o
sorteados.
"""
import json
import math
import os
import tomllib

from . import expresiones as ex

VERSION_MOTOR = '0.1.0'

FUENTES = ('ancla', 'prior', 'codigo', 'definicion')
KAPPA_POR_FUENTE = {'ancla': 200.0, 'prior': 12.0, 'definicion': 1000.0, 'codigo': 1000.0}
CW_VALIDAS = ('sí', 'no', 'en parte')

CLAVES = {
    'raiz': {'modelo', 'corrida', 'parametros', 'distribuciones', 'variables', 'restricciones', 'reglas',
             'cadena', 'estados', 'metricas', 'perfiles', 'factores', 'superficies', 'hipotesis',
             'fidelidad', 'cobertura', 'sensibilidad', 'nombres', 'informe'},
    'modelo': {'nombre', 'descripcion', 'nota'},
    'corrida': {'semilla', 'uniformes', 'poblacion', 'representativos', 'sorteos_parametros',
                'usuarios_incertidumbre', 'usuarios_hipotesis'},
    'parametro': {'id', 'p50', 'p10', 'p90', 'fuente', 'texto', 'nota', 'interruptor', 'anclas'},
    'distribucion': {'id', 'valores', 'kappa', 'fuente', 'texto', 'nota', 'anclas'},
    'variable': {'id', 'valores', 'soporte', 'uniforme', 'relato', 'texto', 'casos'},
    'caso_variable': {'si', 'valor', 'prob', 'dist', 'inclinacion', 'transformar'},
    'restriccion': {'expr', 'texto', 'evidencia'},
    'regla': {'id', 'texto', 'friccion', 'patron', 'evidencia', 'cw', 'nota_cw'},
    'cadena': {'inicio', 'profundidad_maxima', 'atribuibles', 'perdida', 'con_friccion', 'desenlaces'},
    'estado': {'id', 'args', 'por_defecto', 'nombre', 'superficies', 'locales', 'ramas', 'casos', 'texto'},
    'caso_estado': {'si', 'locales', 'ramas'},
    'rama': {'si', 'prob', 'va', 'con', 'accion', 'arco', 'regla', 'superficies'},
    'metrica': {'id', 'expr', 'texto'},
    'perfil': {'id', 'nombre', 'si', 'texto'},
    'factor': {'id', 'expr', 'texto'},
    'superficie': {'id', 'clase', 'usuario', 'texto', 'evidencia'},
    'hipotesis': {'id', 'texto', 'cambios'},
    'fidelidad': {'texto', 'expr', 'dado', 'declarada'},
    'cobertura': {'candidatos_universo', 'candidatos_por_vuelta', 'universo_arcos', 'aplanada'},
    'aplanada': {'parametros', 'distribuciones'},
    'sensibilidad': {'parametros', 'metricas', 'ordenar_por', 'trayectorias', 'niveles', 'usuarios'},
    'nombres': {'listas', 'casos'},
    'caso_nombre': {'si', 'sorteos', 'plantilla'},
    'informe': {'titulo', 'metricas_principales'},
    'evidencia': {'cita', 'extracto'},
}

CORRIDA_POR_DEFECTO = {
    'semilla': 20261120, 'uniformes': None, 'poblacion': 120_000, 'representativos': 12,
    'sorteos_parametros': 200, 'usuarios_incertidumbre': 3000, 'usuarios_hipotesis': 20_000,
}
COBERTURA_POR_DEFECTO = {'candidatos_universo': 60_000, 'candidatos_por_vuelta': 3000, 'universo_arcos': 20_000}
SENSIBILIDAD_POR_DEFECTO = {'trayectorias': 10, 'niveles': 4, 'usuarios': 2000}


class ErrorModelo(Exception):
    """Errores de validación: una lista de mensajes."""

    def __init__(self, errores, avisos=()):
        super().__init__('\n'.join(errores))
        self.errores = list(errores)
        self.avisos = list(avisos)


class Registro:
    """Junta errores y avisos con la ruta del elemento que los produjo."""

    def __init__(self):
        self.errores = []
        self.avisos = []

    def error(self, donde, msg):
        self.errores.append(f'{donde}: {msg}')

    def aviso(self, donde, msg):
        self.avisos.append(f'{donde}: {msg}')

    def claves(self, donde, tabla, tipo):
        if not isinstance(tabla, dict):
            self.error(donde, f'se esperaba una tabla, no {type(tabla).__name__}')
            return False
        sobran = set(tabla) - CLAVES[tipo]
        for k in sorted(sobran):
            self.error(donde, f'clave desconocida «{k}» (válidas: {", ".join(sorted(CLAVES[tipo]))})')
        return True


def _expr(reg, donde, texto):
    try:
        return ex.analizar(texto)
    except ex.ErrorExpresion as e:
        reg.error(donde, str(e))
        return None


def _plantilla(reg, donde, texto):
    try:
        return ex.analizar_plantilla(texto)
    except ex.ErrorExpresion as e:
        reg.error(donde, str(e))
        return None


def parsear_cita(cita):
    """'src/a.js:10-12' → ('src/a.js', 10, 12). Lanza ValueError si no tiene la forma."""
    if not isinstance(cita, str) or ':' not in cita:
        raise ValueError(f'cita sin «archivo:línea»: {cita!r}')
    ruta, _, lineas = cita.rpartition(':')
    if '-' in lineas:
        a, _, b = lineas.partition('-')
    else:
        a = b = lineas
    if not (a.isdigit() and b.isdigit()) or not ruta:
        raise ValueError(f'cita sin «archivo:línea» válido: {cita!r}')
    a, b = int(a), int(b)
    if a < 1 or b < a:
        raise ValueError(f'rango de líneas no válido en {cita!r}')
    return ruta, a, b


def _evidencias(reg, donde, lista, obligatoria=False):
    salida = []
    if lista is None:
        if obligatoria:
            reg.error(donde, 'falta la evidencia: sin cita no entra al modelo')
        return salida
    if not isinstance(lista, list):
        reg.error(donde, 'la evidencia es una lista de { cita, extracto }')
        return salida
    if obligatoria and not lista:
        reg.error(donde, 'la evidencia está vacía: sin cita no entra al modelo')
    for i, e in enumerate(lista):
        d = f'{donde}.evidencia[{i}]'
        if not reg.claves(d, e, 'evidencia'):
            continue
        try:
            parsear_cita(e.get('cita'))
        except ValueError as x:
            reg.error(d, str(x))
            continue
        if not e.get('extracto'):
            reg.error(d, f'la cita {e["cita"]} no trae extracto')
        salida.append({'cita': e['cita'], 'extracto': e.get('extracto', '')})
    return salida


def _fuente(reg, donde, texto):
    if not isinstance(texto, str) or not texto:
        reg.error(donde, 'falta la fuente (ancla:<id>, prior:elicitacion, codigo:<regla> o definicion)')
        return ('prior', '')
    tipo, _, resto = texto.partition(':')
    if tipo not in FUENTES:
        reg.error(donde, f'fuente «{texto}» no válida (ancla:<id>, prior:elicitacion, codigo:<regla>, definicion)')
        return ('prior', '')
    if tipo == 'ancla' and not resto:
        reg.error(donde, 'la fuente ancla necesita su id: ancla:<id>')
    if tipo == 'codigo' and not resto:
        reg.error(donde, 'la fuente codigo necesita la regla: codigo:<regla>')
    if tipo == 'prior' and resto not in ('elicitacion',):
        reg.error(donde, f'fuente «{texto}» no válida: el prior es prior:elicitacion')
    return (tipo, resto)


# --------------------------------------------------------------------------------------------
# Estructuras
# --------------------------------------------------------------------------------------------
class Parametro:
    __slots__ = ('id', 'p50', 'p10', 'p90', 'fuente', 'texto', 'nota', 'interruptor', 'anclas')


class Distribucion:
    __slots__ = ('id', 'valores', 'kappa', 'fuente', 'texto', 'nota', 'anclas')


class CasoVariable:
    __slots__ = ('si', 'tipo', 'valor', 'prob', 'dist', 'dist_inline', 'inclinacion', 'transformar')


class Variable:
    __slots__ = ('id', 'valores', 'soporte', 'uniforme', 'relato', 'texto', 'casos', 'aleatoria')


class Regla:
    __slots__ = ('id', 'texto', 'friccion', 'patron', 'evidencia', 'cw', 'nota_cw')


class Rama:
    __slots__ = ('si', 'prob', 'va', 'con', 'accion', 'arco', 'regla', 'superficies', 'donde')


class CasoEstado:
    __slots__ = ('si', 'locales', 'ramas')


class Estado:
    __slots__ = ('id', 'args', 'por_defecto', 'nombre', 'superficies', 'locales', 'casos', 'texto')


class Modelo:
    """Un modelo.toml ya leído y revisado (sin compilar)."""

    def __init__(self):
        self.ruta = None
        self.crudo = {}
        self.nombre = ''
        self.descripcion = ''
        self.nota = ''
        self.corrida = dict(CORRIDA_POR_DEFECTO)
        self.parametros = []
        self.param = {}
        self.distribuciones = []
        self.dist = {}
        self.variables = []
        self.var = {}
        self.restricciones = []
        self.reglas = {}
        self.fricciones = set()
        self.estados = {}
        self.cadena = {}
        self.metricas = []
        self.perfiles = []
        self.factores = []
        self.superficies = []
        self.hipotesis = []
        self.fidelidad = []
        self.cobertura = dict(COBERTURA_POR_DEFECTO)
        self.aplanada = {'parametros': {}, 'distribuciones': {}}
        self.sensibilidad = dict(SENSIBILIDAD_POR_DEFECTO)
        self.nombres = None
        self.informe = {}
        self.avisos = []

    # Anclas que la corrida usa: como fuente o como información de un prior.
    def anclas_usadas(self):
        usadas = {}
        for x in self.parametros + self.distribuciones:
            if x.fuente[0] == 'ancla':
                usadas.setdefault(x.fuente[1], set()).add(x.id)
            for a in x.anclas:
                usadas.setdefault(a, set()).add(x.id)
        return usadas


def cargar_modelo(ruta, calibracion=None):
    """Lee modelo.toml. Devuelve el Modelo o lanza ErrorModelo con todos los errores juntos."""
    with open(ruta, 'rb') as f:
        try:
            crudo = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise ErrorModelo([f'{ruta}: TOML no válido: {e}'])
    reg = Registro()
    m = Modelo()
    m.ruta = ruta
    m.crudo = crudo
    reg.claves('modelo.toml', crudo, 'raiz')

    cab = crudo.get('modelo', {})
    reg.claves('[modelo]', cab, 'modelo')
    m.nombre = cab.get('nombre', '')
    m.descripcion = cab.get('descripcion', '')
    m.nota = cab.get('nota', '')

    corr = crudo.get('corrida', {})
    reg.claves('[corrida]', corr, 'corrida')
    m.corrida.update(corr)

    _leer_parametros(reg, m, crudo.get('parametros', []))
    _leer_distribuciones(reg, m, crudo.get('distribuciones', []))
    if calibracion:
        aplicar_calibracion(m, calibracion)
    _leer_variables(reg, m, crudo.get('variables', []))
    _leer_restricciones(reg, m, crudo.get('restricciones', []))
    _leer_reglas(reg, m, crudo.get('reglas', []))
    _leer_cadena(reg, m, crudo.get('cadena', {}), crudo.get('estados', []))
    _leer_metricas(reg, m, crudo.get('metricas', []))
    _leer_perfiles(reg, m, crudo.get('perfiles', []))
    _leer_factores(reg, m, crudo.get('factores', []))
    _leer_superficies(reg, m, crudo.get('superficies', []))
    _leer_hipotesis(reg, m, crudo.get('hipotesis', []))
    _leer_fidelidad(reg, m, crudo.get('fidelidad', []))
    _leer_cobertura(reg, m, crudo.get('cobertura', {}))
    _leer_sensibilidad(reg, m, crudo.get('sensibilidad', {}))
    _leer_nombres(reg, m, crudo.get('nombres'))
    inf = crudo.get('informe', {})
    reg.claves('[informe]', inf, 'informe')
    m.informe = inf
    _revisar_referencias(reg, m)
    m.avisos = reg.avisos
    if reg.errores:
        raise ErrorModelo(reg.errores, reg.avisos)
    return m


def _id(reg, donde, tabla, vistos):
    i = tabla.get('id')
    if not isinstance(i, str) or not i:
        reg.error(donde, 'falta el id')
        return None
    if i in vistos:
        reg.error(donde, f'id repetido «{i}»')
    vistos.add(i)
    return i


def _leer_parametros(reg, m, lista):
    vistos = set()
    for i, t in enumerate(lista):
        donde = f'parametros[{i}]'
        if not reg.claves(donde, t, 'parametro'):
            continue
        pid = _id(reg, donde, t, vistos)
        if pid is None:
            continue
        donde = f'parámetro {pid}'
        x = Parametro()
        x.id = pid
        x.texto = t.get('texto', '')
        x.nota = t.get('nota', '')
        x.anclas = list(t.get('anclas', []))
        x.interruptor = bool(t.get('interruptor', False))
        if x.interruptor:
            x.p50 = x.p10 = x.p90 = False
            x.fuente = ('definicion', '')
            if any(k in t for k in ('p50', 'p10', 'p90')):
                reg.error(donde, 'un interruptor no lleva p50, p10 ni p90 (vale false hasta que una hipótesis lo prende)')
        else:
            x.fuente = _fuente(reg, donde, t.get('fuente'))
            try:
                x.p50, x.p10, x.p90 = float(t['p50']), float(t['p10']), float(t['p90'])
            except (KeyError, TypeError, ValueError):
                reg.error(donde, 'necesita p50, p10 y p90 numéricos')
                continue
            if not (0 <= x.p10 <= x.p50 <= x.p90 <= 1):
                reg.error(donde, f'se espera 0 ≤ p10 ≤ p50 ≤ p90 ≤ 1 (p10={x.p10}, p50={x.p50}, p90={x.p90})')
            if x.p10 == x.p90 and x.fuente[0] == 'prior':
                reg.aviso(donde, 'p10 = p90: un prior sin rango no aporta incertidumbre')
        m.parametros.append(x)
        m.param[pid] = x


def _leer_distribuciones(reg, m, lista):
    vistos = set()
    for i, t in enumerate(lista):
        donde = f'distribuciones[{i}]'
        if not reg.claves(donde, t, 'distribucion'):
            continue
        did = _id(reg, donde, t, vistos)
        if did is None:
            continue
        donde = f'distribución {did}'
        x = Distribucion()
        x.id = did
        x.texto = t.get('texto', '')
        x.nota = t.get('nota', '')
        x.anclas = list(t.get('anclas', []))
        x.fuente = _fuente(reg, donde, t.get('fuente'))
        vals = t.get('valores')
        if not isinstance(vals, dict) or not vals:
            reg.error(donde, 'valores es una tabla { valor = probabilidad }')
            continue
        try:
            x.valores = [(k, float(v)) for k, v in vals.items()]
        except (TypeError, ValueError):
            reg.error(donde, 'cada probabilidad es un número')
            continue
        s = sum(p for _, p in x.valores)
        if abs(s - 1) > 1e-9:
            reg.error(donde, f'las probabilidades suman {s!r}, no 1')
        if any(p < 0 for _, p in x.valores):
            reg.error(donde, 'hay probabilidades negativas')
        x.kappa = float(t['kappa']) if 'kappa' in t else KAPPA_POR_FUENTE[x.fuente[0]]
        if x.kappa <= 0:
            reg.error(donde, 'kappa debe ser positivo')
        m.distribuciones.append(x)
        m.dist[did] = x


def _leer_variables(reg, m, lista):
    vistos = set()
    definidos = set()
    for i, t in enumerate(lista):
        donde = f'variables[{i}]'
        if not reg.claves(donde, t, 'variable'):
            continue
        vid = _id(reg, donde, t, vistos)
        if vid is None:
            continue
        if vid in ex.RESERVADOS or not ex._ID.match(vid):
            reg.error(donde, f'«{vid}» no sirve como nombre de variable')
        donde = f'variable {vid}'
        v = Variable()
        v.id = vid
        v.texto = t.get('texto', '')
        v.relato = bool(t.get('relato', False))
        v.valores = list(t.get('valores', []))
        if not v.valores:
            reg.error(donde, 'falta valores (el soporte que admite el código)')
        v.soporte = _evidencias(reg, donde, t.get('soporte'), obligatoria=False)
        if not v.soporte and not v.relato:
            reg.aviso(donde, 'no trae soporte con evidencia del código')
        v.uniforme = t.get('uniforme')
        v.casos = []
        casos = t.get('casos', [])
        if not casos:
            reg.error(donde, 'necesita al menos un caso')
        for j, c in enumerate(casos):
            dc = f'{donde}, caso {j + 1}'
            if not reg.claves(dc, c, 'caso_variable'):
                continue
            k = CasoVariable()
            k.si = _expr(reg, dc + ' (si)', c.get('si', 'True'))
            k.valor = k.prob = k.dist = k.dist_inline = k.inclinacion = k.transformar = None
            tipos = [x for x in ('valor', 'prob', 'dist') if x in c]
            if len(tipos) != 1:
                reg.error(dc, 'cada caso lleva exactamente uno de: valor, prob o dist')
                continue
            k.tipo = tipos[0]
            if k.tipo == 'valor':
                k.valor = _expr(reg, dc + ' (valor)', c['valor'])
            elif k.tipo == 'prob':
                k.prob = _expr(reg, dc + ' (prob)', c['prob'])
                if set(v.valores) != {True, False}:
                    reg.error(dc, 'prob solo sirve en variables con valores = [true, false]')
            else:
                if isinstance(c['dist'], str):
                    k.dist = c['dist']
                elif isinstance(c['dist'], dict):
                    k.dist_inline = [(val, _expr(reg, f'{dc} (dist.{val})', e)) for val, e in c['dist'].items()]
                else:
                    reg.error(dc, 'dist es el id de una distribución o una tabla { valor = "expresión" }')
            if 'inclinacion' in c:
                if k.tipo != 'dist' or not isinstance(c['inclinacion'], dict):
                    reg.error(dc, 'inclinacion es una tabla { valor = factor } y va con dist')
                else:
                    k.inclinacion = [(val, _expr(reg, f'{dc} (inclinacion.{val})', e))
                                     for val, e in c['inclinacion'].items()]
            if 'transformar' in c:
                if k.tipo != 'dist':
                    reg.error(dc, 'transformar va con dist')
                else:
                    k.transformar = _expr(reg, dc + ' (transformar)', c['transformar'])
            # Nombres usados: deben estar definidos antes (orden topológico de la red).
            for a in [k.si, k.valor, k.prob, k.transformar] + [e for _, e in (k.dist_inline or [])] + \
                     [e for _, e in (k.inclinacion or [])]:
                if a is None:
                    continue
                for n in a.nombres - definidos - ({'x'} if a is k.transformar else set()):
                    reg.error(dc, f'usa «{n}», que no es una variable definida antes')
            v.casos.append(k)
        v.aleatoria = any(k.tipo in ('prob', 'dist') for k in v.casos)
        definidos.add(vid)
        m.variables.append(v)
        m.var[vid] = v
    # Uniformes: los explícitos se respetan; los demás toman el siguiente libre.
    usados = {}
    for v in m.variables:
        if v.aleatoria and v.uniforme is not None:
            if not isinstance(v.uniforme, int) or v.uniforme < 0:
                reg.error(f'variable {v.id}', 'uniforme es un entero ≥ 0')
            elif v.uniforme in usados:
                reg.error(f'variable {v.id}', f'el uniforme {v.uniforme} ya lo usa {usados[v.uniforme]}')
            else:
                usados[v.uniforme] = v.id
        elif not v.aleatoria and v.uniforme is not None:
            reg.aviso(f'variable {v.id}', 'es determinista: el uniforme declarado no se usa')
    libre = 0
    for v in m.variables:
        if v.aleatoria and v.uniforme is None:
            while libre in usados:
                libre += 1
            v.uniforme = libre
            usados[libre] = v.id
    necesarios = (max(usados) + 1) if usados else 0
    if m.corrida.get('uniformes') is None:
        m.corrida['uniformes'] = necesarios
    elif m.corrida['uniformes'] < necesarios:
        reg.error('[corrida]', f'uniformes = {m.corrida["uniformes"]}, pero la red necesita {necesarios}')


def _leer_restricciones(reg, m, lista):
    for i, t in enumerate(lista):
        donde = f'restricciones[{i}]'
        if not reg.claves(donde, t, 'restriccion'):
            continue
        a = _expr(reg, donde, t.get('expr'))
        if a is None:
            continue
        for n in a.nombres - set(m.var):
            reg.error(donde, f'usa «{n}», que no es una variable')
        m.restricciones.append({'expr': a, 'texto': t.get('texto', a.texto),
                                'evidencia': _evidencias(reg, donde, t.get('evidencia'))})


def _leer_reglas(reg, m, lista):
    vistos = set()
    for i, t in enumerate(lista):
        donde = f'reglas[{i}]'
        if not reg.claves(donde, t, 'regla'):
            continue
        rid = _id(reg, donde, t, vistos)
        if rid is None:
            continue
        donde = f'regla {rid}'
        r = Regla()
        r.id = rid
        r.texto = t.get('texto', '')
        if not r.texto:
            reg.error(donde, 'falta el texto')
        r.friccion = bool(t.get('friccion', False))
        r.patron = t.get('patron')
        r.evidencia = _evidencias(reg, donde, t.get('evidencia'), obligatoria=True)
        r.cw = list(t.get('cw', ['sí', 'sí', 'sí', 'sí']))
        if len(r.cw) != 4 or any(c not in CW_VALIDAS for c in r.cw):
            reg.error(donde, 'cw son las 4 respuestas del recorrido cognitivo: «sí», «no» o «en parte»')
        r.nota_cw = t.get('nota_cw')
        if r.friccion and 'cw' not in t:
            reg.aviso(donde, 'es fricción y no trae su recorrido cognitivo (cw)')
        if any(c != 'sí' for c in r.cw) and not r.nota_cw:
            reg.aviso(donde, 'el recorrido cognitivo tiene un «no» o «en parte» sin nota_cw')
        m.reglas[rid] = r
        if r.friccion:
            m.fricciones.add(rid)


def _leer_cadena(reg, m, cad, estados):
    reg.claves('[cadena]', cad, 'cadena')
    m.cadena = {
        'inicio': cad.get('inicio', 'inicio'),
        'profundidad_maxima': int(cad.get('profundidad_maxima', 30)),
        'atribuibles': list(cad.get('atribuibles', [])),
        'perdida': list(cad.get('perdida', [])),
        'con_friccion': dict(cad.get('con_friccion', {})),
        'desenlaces': dict(cad.get('desenlaces', {})),
    }
    des = m.cadena['desenlaces']
    if not des:
        reg.error('[cadena]', 'falta [cadena.desenlaces]: id = "texto" de cada desenlace absorbente')
    for k in m.cadena['atribuibles'] + m.cadena['perdida'] + list(m.cadena['con_friccion']) + \
            list(m.cadena['con_friccion'].values()):
        if k not in des:
            reg.error('[cadena]', f'«{k}» no está en [cadena.desenlaces]')
    vistos = set()
    for i, t in enumerate(estados):
        donde = f'estados[{i}]'
        if not reg.claves(donde, t, 'estado'):
            continue
        sid = _id(reg, donde, t, vistos)
        if sid is None:
            continue
        donde = f'estado {sid}'
        e = Estado()
        e.id = sid
        e.texto = t.get('texto', '')
        e.args = list(t.get('args', []))
        for a in e.args:
            if not isinstance(a, str) or not ex._ID.match(a) or a in ex.RESERVADOS:
                reg.error(donde, f'argumento «{a}» no válido')
        e.por_defecto = dict(t.get('por_defecto', {}))
        for a in e.por_defecto:
            if a not in e.args:
                reg.error(donde, f'por_defecto de «{a}», que no está en args')
        e.nombre = _plantilla(reg, donde + ' (nombre)', t.get('nombre', sid))
        e.superficies = [(s, _plantilla(reg, f'{donde} (superficie)', s)) for s in t.get('superficies', [])]
        e.locales = _locales(reg, donde, t.get('locales', {}))
        e.casos = []
        if 'ramas' in t and 'casos' in t:
            reg.error(donde, 'usa ramas o casos, no los dos')
        if 'ramas' in t:
            e.casos.append(_caso_estado(reg, donde, {'ramas': t['ramas']}))
        for j, c in enumerate(t.get('casos', [])):
            if reg.claves(f'{donde}, caso {j + 1}', c, 'caso_estado'):
                e.casos.append(_caso_estado(reg, f'{donde}, caso {j + 1}', c))
        if not e.casos:
            reg.error(donde, 'no tiene ramas')
        m.estados[sid] = e
    if m.cadena['inicio'] not in m.estados:
        reg.error('[cadena]', f'el estado de inicio «{m.cadena["inicio"]}» no existe')


def _locales(reg, donde, tabla):
    if not isinstance(tabla, dict):
        reg.error(donde, 'locales es una tabla { nombre = "expresión" }')
        return []
    salida = []
    for k, e in tabla.items():
        if not ex._ID.match(k) or k in ex.RESERVADOS:
            reg.error(donde, f'local «{k}» no válido')
        salida.append((k, _expr(reg, f'{donde} (local {k})', e)))
    return salida


def _caso_estado(reg, donde, t):
    c = CasoEstado()
    c.si = _expr(reg, donde + ' (si)', t.get('si', 'True'))
    c.locales = _locales(reg, donde, t.get('locales', {}))
    c.ramas = []
    for k, r in enumerate(t.get('ramas', [])):
        dr = f'{donde}, rama {k + 1}'
        if not reg.claves(dr, r, 'rama'):
            continue
        x = Rama()
        x.donde = dr
        x.si = _expr(reg, dr + ' (si)', r['si']) if 'si' in r else None
        x.prob = _expr(reg, dr + ' (prob)', r.get('prob'))
        x.va = r.get('va')
        if not isinstance(x.va, str) or not x.va:
            reg.error(dr, 'falta va: otro estado, $argumento o FIN:<desenlace>')
        x.con = [(k2, _expr(reg, f'{dr} (con.{k2})', e)) for k2, e in dict(r.get('con', {})).items()]
        if 'accion' not in r:
            reg.error(dr, 'falta accion (lo que hace el usuario)')
        x.accion = _plantilla(reg, dr + ' (accion)', r.get('accion', ''))
        x.arco = _plantilla(reg, dr + ' (arco)', r['arco']) if 'arco' in r else None
        x.regla = _plantilla(reg, dr + ' (regla)', r['regla']) if 'regla' in r else None
        x.superficies = [(s, _plantilla(reg, f'{dr} (superficie)', s)) for s in r.get('superficies', [])]
        c.ramas.append(x)
    if not c.ramas:
        reg.error(donde, 'un caso sin ramas')
    return c


def _leer_metricas(reg, m, lista):
    vistos = set()
    for i, t in enumerate(lista):
        donde = f'metricas[{i}]'
        if not reg.claves(donde, t, 'metrica'):
            continue
        mid = _id(reg, donde, t, vistos)
        a = _expr(reg, f'métrica {mid}', t.get('expr'))
        if a is None or mid is None:
            continue
        for n in a.nombres - set(m.cadena['desenlaces']):
            reg.error(f'métrica {mid}', f'usa «{n}», que no es un desenlace')
        m.metricas.append({'id': mid, 'expr': a, 'texto': t.get('texto', mid)})
    if not m.metricas:
        reg.error('[[metricas]]', 'declara al menos una métrica (suma de desenlaces)')


def _leer_perfiles(reg, m, lista):
    vistos = set()
    for i, t in enumerate(lista):
        donde = f'perfiles[{i}]'
        if not reg.claves(donde, t, 'perfil'):
            continue
        pid = _id(reg, donde, t, vistos)
        a = _expr(reg, f'perfil {pid}', t.get('si', 'True'))
        if a is None or pid is None:
            continue
        for n in a.nombres - set(m.var):
            reg.error(f'perfil {pid}', f'usa «{n}», que no es una variable')
        m.perfiles.append({'id': pid, 'nombre': t.get('nombre', pid), 'si': a, 'texto': t.get('texto', '')})
    if not m.perfiles:
        reg.error('[[perfiles]]', 'declara al menos un perfil')


def _leer_factores(reg, m, lista):
    vistos = set()
    for i, t in enumerate(lista):
        donde = f'factores[{i}]'
        if not reg.claves(donde, t, 'factor'):
            continue
        fid = _id(reg, donde, t, vistos)
        a = _expr(reg, f'factor {fid}', t.get('expr'))
        if a is None or fid is None:
            continue
        for n in a.nombres - set(m.var):
            reg.error(f'factor {fid}', f'usa «{n}», que no es una variable')
        m.factores.append({'id': fid, 'expr': a, 'texto': t.get('texto', fid)})


def _leer_superficies(reg, m, lista):
    vistos = set()
    for i, t in enumerate(lista):
        donde = f'superficies[{i}]'
        if not reg.claves(donde, t, 'superficie'):
            continue
        sid = _id(reg, donde, t, vistos)
        if sid is None:
            continue
        u = _expr(reg, f'superficie {sid} (usuario)', t['usuario']) if 'usuario' in t else None
        m.superficies.append({'id': sid, 'clase': t.get('clase', sid), 'usuario': u,
                              'texto': t.get('texto', ''),
                              'evidencia': _evidencias(reg, f'superficie {sid}', t.get('evidencia'))})


def _leer_hipotesis(reg, m, lista):
    vistos = set()
    for i, t in enumerate(lista):
        donde = f'hipotesis[{i}]'
        if not reg.claves(donde, t, 'hipotesis'):
            continue
        hid = _id(reg, donde, t, vistos)
        if hid is None:
            continue
        if hid == 'base':
            reg.error(f'hipótesis {hid}', '«base» está reservado para el modelo sin cambios')
        cambios = t.get('cambios', {})
        if not isinstance(cambios, dict) or not cambios:
            reg.error(f'hipótesis {hid}', 'cambios es una tabla { parametro = valor } no vacía')
            cambios = {}
        m.hipotesis.append({'id': hid, 'texto': t.get('texto', hid), 'cambios': dict(cambios)})


def _leer_fidelidad(reg, m, lista):
    for i, t in enumerate(lista):
        donde = f'fidelidad[{i}]'
        if not reg.claves(donde, t, 'fidelidad'):
            continue
        e = _expr(reg, donde + ' (expr)', t.get('expr'))
        dado = _expr(reg, donde + ' (dado)', t['dado']) if 'dado' in t else None
        dec = _expr(reg, donde + ' (declarada)', t.get('declarada'))
        if e is None or dec is None:
            continue
        if dec.nombres:
            reg.error(donde, 'declarada solo usa p.<parámetro>, d.<distribución>.<valor> y números')
        m.fidelidad.append({'texto': t.get('texto', e.texto), 'expr': e, 'dado': dado, 'declarada': dec})


def _leer_cobertura(reg, m, t):
    if not reg.claves('[cobertura]', t, 'cobertura'):
        return
    for k in COBERTURA_POR_DEFECTO:
        if k in t:
            m.cobertura[k] = int(t[k])
    apl = t.get('aplanada', {})
    reg.claves('[cobertura.aplanada]', apl, 'aplanada')
    m.aplanada = {'parametros': dict(apl.get('parametros', {})),
                  'distribuciones': dict(apl.get('distribuciones', {}))}


def _leer_sensibilidad(reg, m, t):
    if not reg.claves('[sensibilidad]', t, 'sensibilidad'):
        return
    m.sensibilidad.update({k: t[k] for k in ('trayectorias', 'niveles', 'usuarios') if k in t})
    m.sensibilidad['parametros'] = list(t.get('parametros', []))
    m.sensibilidad['metricas'] = list(t.get('metricas', []))
    m.sensibilidad['ordenar_por'] = t.get('ordenar_por')


def _leer_nombres(reg, m, t):
    if t is None:
        return
    if not reg.claves('[nombres]', t, 'nombres'):
        return
    listas = t.get('listas', {})
    casos = []
    for i, c in enumerate(t.get('casos', [])):
        donde = f'nombres.casos[{i}]'
        if not reg.claves(donde, c, 'caso_nombre'):
            continue
        si = _expr(reg, donde, c.get('si', 'True'))
        sorteos = []
        for s in c.get('sorteos', []):
            hueco, _, lista = s.partition(':')
            if lista not in listas:
                reg.error(donde, f'la lista «{lista}» no está en [nombres.listas]')
            sorteos.append((hueco, lista))
        casos.append({'si': si, 'sorteos': sorteos, 'plantilla': c.get('plantilla', '')})
    m.nombres = {'listas': listas, 'casos': casos}


def _revisar_referencias(reg, m):
    """Que cada p.x, d.x.v, estado, regla y desenlace citado exista."""
    def revisar(a, donde):
        if a is None:
            return
        for pid in a.parametros:
            if pid not in m.param:
                reg.error(donde, f'p.{pid} no está en [[parametros]]')
        for did, val in a.distribuciones:
            if did not in m.dist:
                reg.error(donde, f'd.{did} no está en [[distribuciones]]')
            elif val not in dict(m.dist[did].valores):
                reg.error(donde, f'd.{did}.{val}: la distribución no tiene ese valor')

    for v in m.variables:
        for k in v.casos:
            for a in [k.si, k.valor, k.prob, k.transformar] + [e for _, e in (k.dist_inline or [])] + \
                     [e for _, e in (k.inclinacion or [])]:
                revisar(a, f'variable {v.id}')
            if k.dist is not None and k.dist not in m.dist:
                reg.error(f'variable {v.id}', f'dist «{k.dist}» no está en [[distribuciones]]')
            if k.dist is not None and k.dist in m.dist and k.transformar is None:
                for val, _ in m.dist[k.dist].valores:
                    if val not in v.valores:
                        reg.error(f'variable {v.id}', f'la distribución {k.dist} da «{val}», que no está en valores')
            if k.dist_inline:
                for val, _ in k.dist_inline:
                    if val not in v.valores:
                        reg.error(f'variable {v.id}', f'«{val}» no está en valores')
    atributos = set(m.var)
    desenlaces = set(m.cadena['desenlaces'])
    for e in m.estados.values():
        locales_estado = set(e.args) | {k for k, _ in e.locales}
        for k, a in e.locales:
            revisar(a, f'estado {e.id}')
        for _, pl in e.superficies:
            if pl:
                _revisar_nombres_plantilla(reg, f'estado {e.id}', pl, atributos | set(e.args) | {k for k, _ in e.locales})
        if e.nombre:
            _revisar_nombres_plantilla(reg, f'estado {e.id} (nombre)', e.nombre, atributos | set(e.args))
        for c in e.casos:
            locs = locales_estado | {k for k, _ in c.locales}
            for a in [c.si] + [x for _, x in c.locales]:
                revisar(a, f'estado {e.id}')
                if a is not None:
                    for n in a.nombres - atributos - locs:
                        reg.error(f'estado {e.id}', f'usa «{n}», que no es variable, argumento ni local')
            for r in c.ramas:
                for a in [r.si, r.prob] + [x for _, x in r.con]:
                    revisar(a, r.donde)
                    if a is not None:
                        for n in a.nombres - atributos - locs:
                            reg.error(r.donde, f'usa «{n}», que no es variable, argumento ni local')
                for pl in [r.accion, r.arco, r.regla] + [p for _, p in r.superficies]:
                    if pl:
                        _revisar_nombres_plantilla(reg, r.donde, pl, atributos | locs)
                if not isinstance(r.va, str):
                    continue
                if r.va.startswith('FIN:'):
                    if r.va[4:] not in desenlaces:
                        reg.error(r.donde, f'desenlace «{r.va[4:]}» no está en [cadena.desenlaces]')
                    if r.con:
                        reg.error(r.donde, 'una rama a FIN no lleva con')
                elif r.va.startswith('$'):
                    if r.va[1:] not in locs:
                        reg.error(r.donde, f'«{r.va}»: {r.va[1:]} no es argumento ni local del estado')
                elif r.va not in m.estados:
                    reg.error(r.donde, f'va a «{r.va}», que no es un estado')
                else:
                    dest = m.estados[r.va]
                    for k, _ in r.con:
                        if k not in dest.args:
                            reg.error(r.donde, f'con.{k}: el estado {dest.id} no tiene ese argumento')
                    for a in dest.args:
                        if a not in dict(r.con) and a not in dest.por_defecto:
                            reg.error(r.donde, f'falta con.{a} para el estado {dest.id}')
                rid = _texto_plantilla(r.regla) if r.regla else None
                if rid and rid not in m.reglas:
                    reg.error(r.donde, f'la regla «{rid}» no está en [[reglas]]')
    for f in m.fidelidad:
        revisar(f['declarada'], 'fidelidad')
    for s in m.superficies:
        if s['usuario'] is not None:
            for n in s['usuario'].nombres - atributos:
                reg.error(f'superficie {s["id"]}', f'usa «{n}», que no es una variable')
    for h in m.hipotesis:
        for k in h['cambios']:
            if k not in m.param:
                reg.error(f'hipótesis {h["id"]}', f'cambia «{k}», que no es un parámetro')
    for k in m.aplanada['parametros']:
        if k not in m.param:
            reg.error('[cobertura.aplanada]', f'«{k}» no es un parámetro')
    for k, v in m.aplanada['distribuciones'].items():
        if k not in m.dist:
            reg.error('[cobertura.aplanada]', f'«{k}» no es una distribución')
        elif v != 'uniforme':
            if not isinstance(v, dict):
                reg.error('[cobertura.aplanada]', f'{k}: se espera "uniforme" o una tabla de probabilidades')
            else:
                if set(v) != set(dict(m.dist[k].valores)):
                    reg.error('[cobertura.aplanada]', f'{k}: los valores no calzan con la distribución')
                if abs(sum(v.values()) - 1) > 1e-9:
                    reg.error('[cobertura.aplanada]', f'{k}: las probabilidades no suman 1')
    sens = m.sensibilidad
    for k in sens.get('parametros', []):
        if k not in m.param:
            reg.error('[sensibilidad]', f'«{k}» no es un parámetro')
        elif m.param[k].interruptor or m.param[k].p10 == m.param[k].p90:
            reg.error('[sensibilidad]', f'«{k}» no tiene rango (p10 = p90 o es interruptor)')
    ids_metricas = [x['id'] for x in m.metricas]
    for k in sens.get('metricas', []):
        if k not in ids_metricas:
            reg.error('[sensibilidad]', f'«{k}» no es una métrica')
    if sens.get('ordenar_por') and sens['ordenar_por'] not in ids_metricas:
        reg.error('[sensibilidad]', f'ordenar_por «{sens["ordenar_por"]}» no es una métrica')
    for r in m.reglas.values():
        if r.patron is not None and not isinstance(r.patron, str):
            reg.error(f'regla {r.id}', 'patron es el id de un patrón del catálogo')
    # Variables de relato: el flujo no puede depender de ellas.
    relato = {v.id for v in m.variables if v.relato}
    for e in m.estados.values():
        for c in e.casos:
            for r in c.ramas:
                for a in [c.si, r.si, r.prob] + [x for _, x in c.locales + r.con]:
                    if a is not None and a.nombres & relato:
                        reg.error(r.donde, f'usa variables de relato ({", ".join(sorted(a.nombres & relato))}): no pueden cambiar el flujo')
    for p in m.perfiles:
        if p['si'].nombres & relato:
            reg.aviso(f'perfil {p["id"]}', 'usa variables de relato')


def _texto_plantilla(pl):
    partes = pl[0]
    return ''.join(s for t, s in partes if t == 'lit') if all(t == 'lit' for t, _ in partes) else None


def _revisar_nombres_plantilla(reg, donde, pl, validos):
    _, nombres, _, _ = pl
    for n in nombres - validos:
        reg.error(donde, f'la plantilla usa «{n}», que no es variable, argumento ni local')


# --------------------------------------------------------------------------------------------
# Parámetros: theta en p50, aplanada (q) y sorteada
# --------------------------------------------------------------------------------------------
class Theta:
    """Valores de los parámetros y de las distribuciones para una evaluación."""

    __slots__ = ('P', 'D', 'DL')

    def __init__(self, P, DL):
        self.P = P
        self.DL = DL
        self.D = {k: dict(v) for k, v in DL.items()}

    def con(self, cambios_p=None, cambios_d=None):
        P = dict(self.P)
        P.update(cambios_p or {})
        DL = dict(self.DL)
        DL.update(cambios_d or {})
        return Theta(P, DL)


def theta_p50(m):
    P = {x.id: x.p50 for x in m.parametros}
    DL = {x.id: list(x.valores) for x in m.distribuciones}
    return Theta(P, DL)


def theta_aplanado(m):
    t = theta_p50(m)
    DL = {}
    for k, v in m.aplanada['distribuciones'].items():
        vals = [val for val, _ in m.dist[k].valores]
        if v == 'uniforme':
            DL[k] = [(val, 1 / len(vals)) for val in vals]
        else:
            DL[k] = [(val, float(v[val])) for val in vals]
    return t.con({k: v for k, v in m.aplanada['parametros'].items()}, DL)


def theta_sorteado(m, rng):
    """Un sorteo de todos los parámetros: Beta (F1) para los escalares y Dirichlet (F2) para las categóricas."""
    from .incertidumbre import beta_desde
    P = {}
    for x in m.parametros:
        if x.interruptor:
            P[x.id] = x.p50
            continue
        ab = beta_desde(x.p50, x.p10, x.p90)
        P[x.id] = x.p50 if ab is None else rng.betavariate(*ab)
    DL = {}
    for x in m.distribuciones:
        g = [rng.gammavariate(max(x.kappa * p, 1e-3), 1.0) for _, p in x.valores]
        s = sum(g)
        DL[x.id] = [(v, gi / s) for (v, _), gi in zip(x.valores, g)]
    return Theta(P, DL)


def aplicar_calibracion(m, cal):
    """Reemplaza los parámetros calibrados (calibracion.toml) antes de compilar."""
    for pid, vals in cal.get('parametros', {}).items():
        if pid in m.param:
            x = m.param[pid]
            x.p50, x.p10, x.p90 = float(vals['p50']), float(vals['p10']), float(vals['p90'])
    for did, vals in cal.get('distribuciones', {}).items():
        if did in m.dist:
            x = m.dist[did]
            x.valores = [(k, float(vals['valores'][k])) for k, _ in x.valores]
            x.kappa = float(vals['kappa'])


# --------------------------------------------------------------------------------------------
# Carpeta de corrida
# --------------------------------------------------------------------------------------------
ENTRADAS = ('contexto.toml', 'recorrido.toml', 'modelo.toml', 'hallazgos.toml', 'lectura.md',
            'relatos.toml', 'calibracion.toml', 'conteos.toml')


class Corrida:
    """Rutas de una carpeta de corrida y lectura de sus archivos."""

    def __init__(self, raiz):
        self.raiz = os.path.abspath(raiz)

    def ruta(self, *partes):
        return os.path.join(self.raiz, *partes)

    def existe(self, nombre):
        return os.path.exists(self.ruta(nombre))

    def toml(self, nombre):
        ruta = self.ruta(nombre)
        if not os.path.exists(ruta):
            return None
        with open(ruta, 'rb') as f:
            try:
                return tomllib.load(f)
            except tomllib.TOMLDecodeError as e:
                raise ErrorModelo([f'{nombre}: TOML no válido: {e}'])

    def modelo(self):
        cal = self.toml('calibracion.toml')
        return cargar_modelo(self.ruta('modelo.toml'), calibracion=cal)

    def contexto(self):
        return self.toml('contexto.toml') or {}

    def anclas(self):
        """Las anclas copiadas en la corrida: id → (datos del ancla, archivo)."""
        return leer_anclas(self.ruta('anclas'))

    def archivos_entrada(self):
        """Todas las entradas de la corrida, para el manifiesto (rutas relativas, en orden)."""
        salida = [n for n in ENTRADAS if self.existe(n)]
        for sub in ('anclas', 'elicitacion'):
            base = self.ruta(sub)
            for dirpath, _, archivos in sorted(os.walk(base)):
                for a in sorted(archivos):
                    if a.startswith('.'):
                        continue
                    salida.append(os.path.relpath(os.path.join(dirpath, a), self.raiz))
        return salida


def leer_anclas(base):
    """Lee todas las anclas bajo `base` (archivos .toml con [[anclas]])."""
    salida = {}
    if not os.path.isdir(base):
        return salida
    for dirpath, _, archivos in sorted(os.walk(base)):
        for a in sorted(archivos):
            if not a.endswith('.toml'):
                continue
            ruta = os.path.join(dirpath, a)
            with open(ruta, 'rb') as f:
                datos = tomllib.load(f)
            comun = {k: v for k, v in datos.items() if k != 'anclas'}
            for x in datos.get('anclas', []):
                y = dict(comun)
                y.update(x)
                salida[y['id']] = (y, os.path.relpath(ruta, base))
    return salida


def json_estable(obj):
    """JSON con orden fijo y sin escapar acentos: dos corridas iguales dan los mismos bytes."""
    return json.dumps(obj, ensure_ascii=False, indent=1, allow_nan=False) + '\n'


def finito(x):
    return x if isinstance(x, (int, float)) and math.isfinite(x) else None


def leer_json(ruta):
    with open(ruta, encoding='utf-8') as f:
        return json.load(f)


def leer_texto(ruta):
    with open(ruta, encoding='utf-8') as f:
        return f.read()
