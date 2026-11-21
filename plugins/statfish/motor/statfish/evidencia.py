"""Evidencia con extracto: cada `archivo:línea` se verifica contra el commit actual del repo.

Estados:
- vigente: el extracto está en las líneas citadas;
- desplazada: el extracto está en el archivo, pero en otras líneas (se informa la cita nueva);
- vencida: el archivo no existe, el rango no es válido o el extracto ya no está;
- sin_extracto: la cita no trae el texto que cita (no se puede verificar).
"""
import os
import re
import subprocess

from .modelo import parsear_cita

_ESPACIOS = re.compile(r'\s+')


def normalizar(texto):
    return _ESPACIOS.sub(' ', texto).strip()


def recoger_citas(corrida):
    """Todas las citas de la corrida: (origen, cita, extracto)."""
    citas = []

    def rec(obj, donde):
        if isinstance(obj, dict):
            if 'cita' in obj and isinstance(obj.get('cita'), str):
                citas.append((donde, obj['cita'], obj.get('extracto', '')))
                return
            for k, v in obj.items():
                rec(v, f'{donde}.{k}' if donde else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                ident = v.get('id') if isinstance(v, dict) and isinstance(v.get('id'), str) else None
                rec(v, f'{donde}[{ident or i}]')

    for nombre in ('recorrido.toml', 'modelo.toml', 'hallazgos.toml'):
        datos = corrida.toml(nombre)
        if datos:
            rec(datos, nombre)
    return citas


def commit_actual(repo):
    try:
        r = subprocess.run(['git', '-C', repo, 'rev-parse', 'HEAD'], capture_output=True, text=True, timeout=10)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def verificar_cita(repo, cita, extracto, cache):
    try:
        ruta, a, b = parsear_cita(cita)
    except ValueError as e:
        return {'estado': 'vencida', 'motivo': str(e)}
    completa = os.path.join(repo, ruta)
    if ruta not in cache:
        try:
            with open(completa, encoding='utf-8') as f:
                cache[ruta] = f.read().split('\n')
        except (OSError, UnicodeDecodeError):
            cache[ruta] = None
    lineas = cache[ruta]
    if lineas is None:
        return {'estado': 'vencida', 'motivo': 'el archivo no existe o no se puede leer'}
    if not extracto:
        sugerido = next((x.strip() for x in lineas[a - 1:b] if len(x.strip()) > 3), '')
        return {'estado': 'sin_extracto', 'motivo': 'falta el extracto', 'sugerido': sugerido[:120]}
    objetivo = normalizar(extracto)
    if b <= len(lineas) and objetivo in normalizar('\n'.join(lineas[a - 1:b])):
        return {'estado': 'vigente'}
    # ¿Está en otras líneas? Se busca una ventana del mismo alto que el extracto.
    alto = max(1, extracto.count('\n') + 1)
    for i in range(len(lineas)):
        ventana = normalizar('\n'.join(lineas[i:i + alto]))
        if objetivo in ventana:
            nueva = f'{ruta}:{i + 1}' if alto == 1 else f'{ruta}:{i + 1}-{i + alto}'
            motivo = 'el rango citado pasa el final del archivo' if b > len(lineas) else 'el texto se movió'
            return {'estado': 'desplazada', 'motivo': motivo, 'nueva_cita': nueva}
    if b > len(lineas):
        return {'estado': 'vencida', 'motivo': f'el archivo tiene {len(lineas)} líneas y el extracto ya no está'}
    return {'estado': 'vencida', 'motivo': 'el extracto ya no está en el archivo'}


def verificar(corrida, repo=None):
    """Verifica todas las citas de la corrida y devuelve el informe de evidencia."""
    ctx = corrida.contexto()
    if repo is None:
        rel = ctx.get('repo', {}).get('ruta')
        repo = os.path.normpath(os.path.join(corrida.raiz, rel)) if rel else None
    citas = recoger_citas(corrida)
    salida = {'repo': ctx.get('repo', {}).get('nombre', ''), 'commit_corrida': ctx.get('repo', {}).get('commit', ''),
              'commit_actual': None, 'citas': [], 'resumen': {}}
    if not repo or not os.path.isdir(repo):
        for donde, cita, extracto in citas:
            salida['citas'].append({'origen': donde, 'cita': cita, 'extracto': extracto, 'estado': 'no_verificable',
                                    'motivo': 'no se encontró el repo (usa --repo)'})
    else:
        salida['commit_actual'] = commit_actual(repo)
        cache = {}
        vistos = {}
        for donde, cita, extracto in citas:
            clave = (cita, extracto)
            if clave not in vistos:
                vistos[clave] = verificar_cita(repo, cita, extracto, cache)
            salida['citas'].append({'origen': donde, 'cita': cita, 'extracto': extracto, **vistos[clave]})
    resumen = {}
    for c in salida['citas']:
        resumen[c['estado']] = resumen.get(c['estado'], 0) + 1
    unicas = {(c['cita'], c['extracto']): c['estado'] for c in salida['citas']}
    salida['resumen'] = {'citas': len(salida['citas']), 'unicas': len(unicas), **resumen,
                         'vigentes_unicas': sum(1 for e in unicas.values() if e == 'vigente')}
    salida['precision'] = (salida['resumen']['vigentes_unicas'] / len(unicas)) if unicas else None
    return salida


def hallazgos_afectados(corrida, evidencia):
    """Hallazgos con alguna cita vencida: «posible arreglo, verificar»."""
    malas = {c['cita'] for c in evidencia['citas'] if c['estado'] == 'vencida'}
    datos = corrida.toml('hallazgos.toml') or {}
    salida = []
    for h in datos.get('hallazgos', []):
        citas = [e.get('cita') for e in h.get('evidencia', [])]
        if any(c in malas for c in citas):
            salida.append({'id': h.get('id'), 'estado': h.get('estado'), 'aviso': 'posible arreglo, verificar',
                           'citas_vencidas': [c for c in citas if c in malas]})
    return salida
