"""Contexto de la corrida: detección determinista del stack, catálogo de patrones y registro de anclas."""
import datetime
import json
import os
import re
import subprocess
import tomllib

from . import expresiones as ex
from . import modelo as M

DATOS = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'datos')
# Carpetas que no son el producto: dependencias, salidas de build y herramientas del equipo
# (skills de Claude Code, CI, editores), que traen HTML y texto ajenos al sitio.
IGNORAR = {'.git', 'node_modules', 'dist', 'build', '.next', '.astro', '.wrangler', 'coverage', 'vendor',
           '.venv', 'venv', '__pycache__', '.cache', 'statfish', 'out', '.claude', '.github', '.vscode',
           '.idea', '.husky', '.agents', '.cursor'}
INDICES = ('index.html', 'public/index.html', 'src/index.html', 'app/layout.tsx', 'app/layout.jsx',
           'src/app/layout.tsx', 'src/app.html', 'src/layouts/Base.astro')
CODIGO = ('.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.vue', '.svelte', '.astro', '.html', '.py', '.rb',
          '.php', '.go', '.java', '.kt', '.swift', '.cs', '.jsonc', '.toml', '.json', '.css', '.scss')
TOPE_ARCHIVO = 400_000

# Rasgos que se detectan buscando texto en el código (sin ejecutar nada).
PISTAS = {
    'turnstile': r'turnstile',
    'recaptcha': r'recaptcha|grecaptcha',
    'hcaptcha': r'hcaptcha',
    'webmcp': r'\btoolname\s*=|navigator\.modelContext',
    'resend': r'\bresend\b|api\.resend\.com',
    'whatsapp': r'wa\.me/|api\.whatsapp\.com',
    'trampa-honeypot': r'honeypot|hp_campo|\bhp_\w+',
    'almacenamiento-local': r'localStorage|sessionStorage|indexedDB',
    'webgl': r'WebGLRenderingContext|getContext\(\s*[\'"]webgl|three\b',
    'movimiento-reducido': r'prefers-reduced-motion',
    'post-nativo': r'method=["\']post["\']',
    'service-worker': r'serviceWorker\.register',
    'stripe': r'js\.stripe\.com|@stripe/|\bStripe\(',
    'analitica': r'gtag\(|googletagmanager|plausible|posthog|umami|segment\.com|mixpanel|hotjar',
}
DEPENDENCIAS = {
    'react': 'react', 'preact': 'preact', 'vue': 'vue', 'svelte': 'svelte', 'astro': 'astro', 'next': 'next',
    'nuxt': 'nuxt', 'vite': 'vite', 'express': 'express', 'hono': 'hono', 'three': 'webgl',
    '@cloudflare/workers-types': 'cloudflare-workers', 'wrangler': 'cloudflare-workers', 'tailwindcss': 'tailwind',
    'playwright': 'playwright', '@playwright/test': 'playwright',
}


def _leer(ruta):
    with open(ruta, encoding='utf-8', errors='ignore') as f:
        return f.read()


def _git(repo, *args):
    try:
        r = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def nombre_repo(repo):
    url = _git(repo, 'remote', 'get-url', 'origin') or ''
    m = re.search(r'github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?$', url)
    return m.group(1) if m else os.path.basename(os.path.abspath(repo))


def archivos_de(repo):
    """Archivos de código versionados (git ls-files) o, sin git, los del árbol menos los ignorados."""
    lista = _git(repo, 'ls-files')
    if lista is not None:
        return sorted(x for x in lista.split('\n') if x and not any(p in IGNORAR for p in x.split('/')[:-1]))
    salida = []
    for dirpath, dirs, archivos in os.walk(repo):
        dirs[:] = sorted(d for d in dirs if d not in IGNORAR)
        for a in sorted(archivos):
            salida.append(os.path.relpath(os.path.join(dirpath, a), repo))
    return salida


def detectar(repo):
    """El stack del repo, de forma determinista: dependencias, archivos y pistas en el código."""
    rasgos = set()
    archivos = archivos_de(repo)
    lenguajes = {}
    for a in archivos:
        ext = os.path.splitext(a)[1].lower()
        if ext in CODIGO:
            lenguajes[ext.lstrip('.')] = lenguajes.get(ext.lstrip('.'), 0) + 1
    pkg = os.path.join(repo, 'package.json')
    if os.path.exists(pkg):
        try:
            datos = M.leer_json(pkg)
            deps = {**datos.get('dependencies', {}), **datos.get('devDependencies', {})}
            for d, r in DEPENDENCIAS.items():
                if d in deps:
                    rasgos.add(r)
            rasgos.add('node')
        except (OSError, ValueError):
            pass
    for nombre, rasgo in (('wrangler.jsonc', 'cloudflare-workers'), ('wrangler.toml', 'cloudflare-workers'),
                          ('wrangler.json', 'cloudflare-workers'), ('vercel.json', 'vercel'),
                          ('netlify.toml', 'netlify'), ('Dockerfile', 'docker'), ('requirements.txt', 'python'),
                          ('pyproject.toml', 'python'), ('Gemfile', 'ruby'), ('go.mod', 'go')):
        if os.path.exists(os.path.join(repo, nombre)):
            rasgos.add(rasgo)
    patrones = {k: re.compile(v, re.I) for k, v in PISTAS.items()}
    formularios = 0
    origin_trial = False
    idioma = None
    for indice in INDICES:
        ruta = os.path.join(repo, indice)
        if os.path.exists(ruta):
            mi = re.search(r'<html[^>]*\slang=["\']([\w-]+)["\']', _leer(ruta))
            if mi:
                idioma = mi.group(1)
                break
    idiomas = {}
    rutas = set()
    for a in archivos:
        ext = os.path.splitext(a)[1].lower()
        if ext not in CODIGO or ext in ('.json', '.css', '.scss'):
            continue
        ruta = os.path.join(repo, a)
        try:
            if os.path.getsize(ruta) > TOPE_ARCHIVO:
                continue
            texto = _leer(ruta)
        except OSError:
            continue
        for k, p in patrones.items():
            if k not in rasgos and p.search(texto):
                rasgos.add(k)
        formularios += len(re.findall(r'<form[\s>]', texto))
        if re.search(r'origin-trial', texto, re.I):
            origin_trial = True
        mi = re.search(r'<html[^>]*\slang=["\']([\w-]+)["\']', texto)
        if mi:
            idiomas[mi.group(1)] = idiomas.get(mi.group(1), 0) + 1
        partes = a.split('/')
        if len(partes) > 1 and partes[-2] in ('pages', 'paginas', 'routes', 'app') and ext in (
                '.jsx', '.tsx', '.js', '.ts', '.vue', '.svelte', '.astro', '.html'):
            rutas.add(a)
    if idioma is None and idiomas:
        idioma = sorted(idiomas.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
    if 'analitica' not in rasgos:
        rasgos.add('sin-analitica')
    return {
        'rasgos': sorted(rasgos),
        'formularios': formularios,
        'paginas': len(rutas),
        'origin_trial': origin_trial,
        'idioma': idioma or '',
        'lenguajes': dict(sorted(lenguajes.items(), key=lambda kv: (-kv[1], kv[0]))),
        'archivos': len(archivos),
    }


def armar_contexto(repo, corrida_dir, pregunta, pais, publico, fecha):
    commit = _git(repo, 'rev-parse', 'HEAD') or ''
    sucio = bool(_git(repo, 'status', '--porcelain'))
    return {
        'corrida': {'pregunta': pregunta, 'pais': pais, 'publico': publico, 'fecha': fecha},
        'repo': {'nombre': nombre_repo(repo),
                 'ruta': os.path.relpath(os.path.abspath(repo), os.path.abspath(corrida_dir)),
                 'commit': commit, 'commit_corto': commit[:7], 'cambios_locales': sucio},
        'stack': detectar(repo),
    }


# --------------------------------------------------------------------------------------------
# Catálogo de patrones (datos/patrones/*.toml)
# --------------------------------------------------------------------------------------------
def leer_patrones(base=None):
    base = base or os.path.join(DATOS, 'patrones')
    salida = []
    if not os.path.isdir(base):
        return salida
    for a in sorted(os.listdir(base)):
        if a.endswith('.toml'):
            with open(os.path.join(base, a), 'rb') as f:
                p = tomllib.load(f)
            p['_archivo'] = a
            salida.append(p)
    return salida


def espacio_contexto(ctx):
    """Los nombres que puede usar `aplica_si`: rasgos, formularios, paginas, origin_trial, idioma, pais."""
    st = ctx.get('stack', {})
    return {'rasgos': tuple(st.get('rasgos', [])), 'formularios': st.get('formularios', 0),
            'paginas': st.get('paginas', 0), 'origin_trial': st.get('origin_trial', False),
            'idioma': st.get('idioma', ''), 'pais': ctx.get('corrida', {}).get('pais', '')}


def patrones_aplicables(ctx, patrones):
    espacio = espacio_contexto(ctx)
    aplican, no = [], []
    for p in patrones:
        try:
            f = ex.compilar(p.get('aplica_si', 'True'))
            si = bool(f(espacio, None, None, None))
        except (ex.ErrorExpresion, KeyError) as e:
            raise ValueError(f'{p["_archivo"]}: aplica_si no válido: {e}') from None
        (aplican if si else no).append(p)
    return aplican, no


def buscar_pistas(repo, patron, tope=8):
    """Lugares del repo donde aparecen las regex del patrón (archivo:línea y el texto)."""
    regex = [re.compile(r, re.I) for r in patron.get('deteccion', {}).get('regex', [])]
    if not regex:
        return []
    hallados = []
    for a in archivos_de(repo):
        if os.path.splitext(a)[1].lower() not in CODIGO:
            continue
        ruta = os.path.join(repo, a)
        try:
            if os.path.getsize(ruta) > TOPE_ARCHIVO:
                continue
            for i, linea in enumerate(_leer(ruta).split('\n'), 1):
                if any(r.search(linea) for r in regex):
                    hallados.append({'cita': f'{a}:{i}', 'texto': linea.strip()[:140]})
                    if len(hallados) >= tope:
                        return hallados
        except OSError:
            continue
    return hallados


# --------------------------------------------------------------------------------------------
# Registro de anclas (datos/anclas/<fuente>/<país>/<periodo>.toml)
# --------------------------------------------------------------------------------------------
def leer_registro(base=None):
    return M.leer_anclas(base or os.path.join(DATOS, 'anclas'))


def vence(ancla):
    consultado = ancla.get('consultado')
    meses = int(ancla.get('vigencia_meses', 0))
    if not isinstance(consultado, datetime.date):
        return None
    y, m = consultado.year, consultado.month + meses
    y += (m - 1) // 12
    m = (m - 1) % 12 + 1
    dia = min(consultado.day, [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28, 31, 30, 31, 30, 31,
                               31, 30, 31, 30, 31][m - 1])
    return datetime.date(y, m, dia)


def estado_ancla(ancla, hoy):
    v = vence(ancla)
    if v is None:
        return 'sin_fecha', None
    return ('vencida' if hoy > v else 'vigente'), v
