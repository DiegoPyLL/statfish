#!/usr/bin/env python3
"""Statfish, caso Volutus: red de perfiles, usuarios, flujos y agregados.

Script DESECHABLE del caso de prueba (no es parte de ningún repo). Solo usa la
biblioteca estándar. Todo sorteo sale de la semilla declarada: correrlo de nuevo
da exactamente lo mismo.

    python3 -I modelo.py            # escribe salida/*.json y salida/*.md

Separación que exige el diseño:
  - soporte y restricciones: del código (ver REGLAS, con archivo:línea);
  - pesos: anclas públicas (StatCounter, SII/INE) o priors del LLM con rango;
  - acción de cada paso: sorteada con P(transición | usuario);
  - consecuencia: la regla del código que corresponde;
  - percepción: las 4 preguntas del recorrido cognitivo (CW).
"""
import json
import math
import os
import random
import statistics
from collections import Counter, defaultdict

SEMILLA = 20261120
AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, 'salida')
os.makedirs(SALIDA, exist_ok=True)

# --------------------------------------------------------------------------
# Parámetros escalares: (p50, p10, p90, fuente)
# --------------------------------------------------------------------------
P = {
    # población y entorno
    'relacion_cliente_brief': (0.05, 0.02, 0.10, 'prior LLM'),
    'movil_si_redes': (0.80, 0.65, 0.90, 'prior LLM'),
    'movil_si_recomendacion': (0.70, 0.55, 0.85, 'prior LLM'),
    'inapp_si_redes_movil': (0.60, 0.40, 0.80, 'prior LLM'),
    'movimiento_reducido': (0.05, 0.02, 0.10, 'prior LLM'),
    'js_off': (0.005, 0.002, 0.015, 'prior LLM'),
    'brief_js_falla': (0.005, 0.001, 0.02, 'prior LLM'),
    'almacen_bloqueado': (0.03, 0.01, 0.06, 'prior LLM'),
    'estricta_base': (0.03, 0.01, 0.06, 'prior LLM'),
    'agente_en_chrome_escritorio': (0.002, 0.0005, 0.01, 'prior LLM + estado de WebMCP'),
    'smart_punct_on': (0.95, 0.85, 0.99, 'prior LLM + comportamiento documentado de iOS'),
    'nombre_apostrofo': (0.004, 0.001, 0.010, 'prior LLM'),
    'nombre_guion_punto': (0.021, 0.010, 0.040, 'prior LLM'),
    'nombre_empresa_signos': (0.025, 0.010, 0.050, 'prior LLM'),
    'whatsapp_si_movil': (0.45, 0.30, 0.60, 'prior LLM'),
    'whatsapp_si_escritorio': (0.20, 0.10, 0.35, 'prior LLM'),
    'pega_rapido_comparando': (0.10, 0.05, 0.20, 'prior LLM'),
    # flujo
    'sale_explorando': (0.55, 0.40, 0.70, 'prior LLM'),
    'sale_comparando': (0.35, 0.20, 0.50, 'prior LLM'),
    'sale_listo': (0.10, 0.05, 0.20, 'prior LLM'),
    'home_a_servicio': (0.60, 0.45, 0.75, 'prior LLM'),
    'articulo_a_servicio': (0.30, 0.15, 0.45, 'prior LLM'),
    'usa_estimado': (0.45, 0.30, 0.60, 'prior LLM'),
    'usa_estimado_ley': (0.40, 0.25, 0.55, 'prior LLM'),
    'pide_cotizacion': (0.35, 0.20, 0.50, 'prior LLM'),
    'contacta_explorando': (0.10, 0.05, 0.20, 'prior LLM'),
    'contacta_comparando': (0.30, 0.20, 0.45, 'prior LLM'),
    'contacta_listo': (0.70, 0.55, 0.85, 'prior LLM'),
    'abandona_seleccion_perdida': (0.25, 0.10, 0.45, 'prior LLM'),
    'usa_cta_brief_web': (0.40, 0.25, 0.55, 'prior LLM'),
    'envia_brief_prospecto': (0.45, 0.25, 0.65, 'prior LLM'),
    'vuelve_al_formulario': (0.35, 0.20, 0.50, 'prior LLM'),
    'resuelve_nombre_opaco': (0.55, 0.30, 0.80, 'prior LLM'),
    'resuelve_nombre_claro': (0.85, 0.70, 0.95, 'prior LLM'),
    'token_no_listo_rapido_movil': (0.35, 0.15, 0.55, 'prior LLM'),
    'token_no_listo_rapido_escritorio': (0.15, 0.05, 0.30, 'prior LLM'),
    'token_no_listo_normal': (0.01, 0.002, 0.03, 'prior LLM'),
    'token_no_listo_agente': (0.60, 0.30, 0.85, 'prior LLM'),
    'turnstile_falla_estricta': (0.30, 0.10, 0.50, 'prior LLM'),
    'turnstile_falla_normal': (0.005, 0.001, 0.02, 'prior LLM'),
    'reintenta_tras_403': (0.25, 0.10, 0.40, 'prior LLM'),
    'correo_directo_tras_error': (0.35, 0.20, 0.50, 'prior LLM'),
    'resend_falla': (0.002, 0.0005, 0.01, 'prior LLM'),
    'whatsapp_envia': (0.85, 0.70, 0.95, 'prior LLM'),
    'inapp_falla_whatsapp': (0.10, 0.02, 0.25, 'prior LLM'),
    'cambia_a_correo': (0.50, 0.30, 0.70, 'prior LLM'),
    'nojs_correo_directo': (0.40, 0.20, 0.60, 'prior LLM'),
    'cliente_completa_brief': (0.80, 0.60, 0.90, 'prior LLM'),
    'brief_rapido_si_agente': (0.50, 0.20, 0.80, 'prior LLM'),
    'carrera_turnstile_brief': (0.05, 0.01, 0.15, 'prior LLM'),
    'reintenta_brief': (0.85, 0.70, 0.95, 'prior LLM'),
    'brief_en_varias_sesiones': (0.40, 0.25, 0.60, 'prior LLM'),
}

# --------------------------------------------------------------------------
# Categóricas: (lista ordenada de (valor, p50), kappa de la Dirichlet, fuente)
# --------------------------------------------------------------------------
C = {
    'canal': ([('google', 0.32), ('articulo', 0.14), ('recomendacion', 0.20), ('redes', 0.14),
               ('directo', 0.08), ('ia', 0.12)], 15, 'prior LLM'),
    'disp_base': ([('escritorio', 0.5005), ('movil', 0.4912), ('tablet', 0.0083)], 200,
                  'ancla: StatCounter Chile, oct-2026'),
    'disp_cliente': ([('escritorio', 0.60), ('movil', 0.30), ('tablet', 0.10)], 10, 'prior LLM'),
    'sistema_movil': ([('android', 0.7928), ('ios', 0.2072)], 200, 'ancla: StatCounter Chile, oct-2026'),
    'sistema_escritorio': ([('windows', 0.8502), ('macos', 0.0880), ('linux', 0.0618)], 200,
                           'ancla: StatCounter Chile, oct-2026'),
    'sistema_tablet': ([('ipados', 0.60), ('android', 0.40)], 10, 'prior LLM'),
    'nav_android': ([('chrome', 0.85), ('samsung', 0.08), ('opera', 0.04), ('firefox', 0.03)], 50,
                    'ancla StatCounter + prior LLM'),
    'nav_ios': ([('safari', 0.82), ('chrome', 0.15), ('otro', 0.03)], 30, 'prior LLM'),
    'nav_ipados': ([('safari', 0.90), ('chrome', 0.10)], 20, 'prior LLM'),
    'nav_windows': ([('chrome', 0.80), ('edge', 0.13), ('firefox', 0.04), ('opera', 0.03)], 50,
                    'ancla StatCounter + prior LLM'),
    'nav_macos': ([('safari', 0.45), ('chrome', 0.48), ('firefox', 0.07)], 30, 'prior LLM'),
    'nav_linux': ([('chrome', 0.70), ('firefox', 0.30)], 10, 'prior LLM'),
    'gpu_escritorio': ([('ok', 0.86), ('lenta', 0.12), ('sin_webgl', 0.02)], 20, 'prior LLM'),
    'gpu_movil': ([('ok', 0.92), ('lenta', 0.07), ('sin_webgl', 0.01)], 20, 'prior LLM'),
    'tamano': ([('independiente', 0.25), ('micro', 0.40), ('pequena', 0.25), ('mediana', 0.08),
                ('grande', 0.02)], 15, 'ancla SII 2024 (empresas con ventas) + prior LLM'),
    'servicio_base': ([('web', 0.25), ('tienda', 0.13), ('gestion', 0.12), ('automatizacion', 0.10),
                       ('agente', 0.10), ('app', 0.08), ('prospeccion', 0.06), ('datos', 0.10),
                       ('no_sabe', 0.06)], 12, 'prior LLM'),
    'etapa_google': ([('explorando', 0.55), ('comparando', 0.30), ('listo', 0.15)], 12, 'prior LLM'),
    'etapa_articulo': ([('explorando', 0.70), ('comparando', 0.22), ('listo', 0.08)], 12, 'prior LLM'),
    'etapa_recomendacion': ([('explorando', 0.35), ('comparando', 0.35), ('listo', 0.30)], 12, 'prior LLM'),
    'etapa_redes': ([('explorando', 0.65), ('comparando', 0.25), ('listo', 0.10)], 12, 'prior LLM'),
    'etapa_directo': ([('explorando', 0.40), ('comparando', 0.35), ('listo', 0.25)], 12, 'prior LLM'),
    'etapa_ia': ([('explorando', 0.45), ('comparando', 0.35), ('listo', 0.20)], 12, 'prior LLM'),
    'destino_google': ([('servicio', 0.50), ('home', 0.35), ('articulo', 0.15)], 10, 'prior LLM'),
    'destino_articulo': ([('articulo', 1.0)], 1000, 'definición'),
    'destino_recomendacion': ([('home', 0.75), ('servicio', 0.25)], 10, 'prior LLM'),
    'destino_redes': ([('home', 0.70), ('servicio', 0.20), ('articulo', 0.10)], 10, 'prior LLM'),
    'destino_directo': ([('home', 1.0)], 1000, 'definición'),
    'destino_ia': ([('servicio', 0.50), ('articulo', 0.30), ('home', 0.20)], 10, 'prior LLM'),
    'rubro': ([('comercio', 0.30), ('servicios profesionales', 0.18), ('gastronomía', 0.10),
               ('salud y bienestar', 0.10), ('construcción', 0.06), ('manufactura', 0.06),
               ('transporte', 0.05), ('educación', 0.05), ('agro', 0.05), ('turismo', 0.05)], 10,
              'prior LLM (solo relato)'),
    'region': ([('Metropolitana', 0.45), ('Valparaíso', 0.095), ('Biobío', 0.09), ('Maule', 0.05),
                ('Araucanía', 0.05), ("O'Higgins", 0.05), ('Coquimbo', 0.04), ('Antofagasta', 0.04),
                ('Los Lagos', 0.04), ('Ñuble', 0.02), ('Los Ríos', 0.02), ('Atacama', 0.015),
                ('Tarapacá', 0.015), ('Arica y Parinacota', 0.01), ('Magallanes', 0.01), ('Aysén', 0.005)],
               30, 'ancla SII/INE para RM (~41-43 %) + prior LLM (solo relato)'),
    'edad': ([('18-29', 0.15), ('30-44', 0.40), ('45-59', 0.33), ('60+', 0.12)], 10, 'prior LLM (solo relato)'),
}

# Inclinación del servicio según el tamaño (prior LLM): multiplica y normaliza.
INCLINACION = {
    'independiente': {'web': 1.3, 'tienda': 1.2, 'gestion': 0.5, 'automatizacion': 0.7, 'datos': 0.6},
    'micro': {},
    'pequena': {'gestion': 1.5, 'automatizacion': 1.4, 'datos': 1.4, 'web': 0.8},
    'mediana': {'gestion': 1.7, 'automatizacion': 1.6, 'datos': 1.6, 'web': 0.6, 'tienda': 0.8, 'app': 1.3},
    'grande': {'gestion': 1.5, 'automatizacion': 1.8, 'datos': 1.8, 'web': 0.5, 'tienda': 0.7, 'app': 1.5,
               'agente': 1.3},
}

# --------------------------------------------------------------------------
# Reglas del código: lo que pasa, con su evidencia. La que es fricción, lo dice.
# --------------------------------------------------------------------------
REGLAS = {
    'R1': ('El nombre solo admite letras, marcas, espacio y apóstrofo recto: rechaza guion, punto, dígitos y &',
           ['src/lib/contacto.js:89-91', 'src/client.js:82-85', 'worker/index.js:99-101',
            'src/comportamiento/brief/brief.js:350', 'worker/brief.js:292-294'], True),
    'R1+R2': ('En iPhone y iPad el apóstrofo se escribe ’ (Smart Punctuation) y la regla del nombre lo rechaza',
              ['src/lib/contacto.js:89-91', 'src/components/Contacto.jsx:121-130', 'src/client.js:82-85'], True),
    'R4': ('Turnstile se descarga al primer foco del formulario y el envío no espera su token: sin token, 403',
           ['src/lib/turnstile.js:53', 'src/lib/turnstile.js:27-51', 'src/client.js:191-245',
            'worker/index.js:103-105', 'worker/comun.js:137'], True),
    'R4b': ('Turnstile no se resuelve con privacidad estricta: 403', ['worker/comun.js:130-152'], True),
    'R5': ('Resend no responde: 502 con el correo directo', ['worker/index.js:121-123', 'worker/comun.js:163-192'], True),
    'R6': ('WhatsApp se abre con window.open; en el navegador de una app puede no abrir',
           ['src/client.js:202-214'], True),
    'R7': ('Sin JavaScript el envío llega sin token y se rechaza; la respuesta es una página aparte sin enlace al correo',
           ['src/components/Contacto.jsx:23-25', 'worker/index.js:34-40', 'worker/comun.js:32-46'], True),
    'R8': ('En /ley21719, «Pedir esta cotización» y «Cuéntanos tu proyecto» llevan a /#contacto: sin lo marcado ni el servicio',
           ['src/paginas/Ley21719.jsx:429', 'src/paginas/Ley21719.jsx:264', 'src/components/Estimado.jsx:48',
            'src/components/Estimado.jsx:204-207', 'src/paginas/Inicio.jsx:33'], True),
    'R9': ('En desarrollo web, «Cuéntanos tu proyecto» de la cabecera abre el brief de 35 a 45 min; el de la barra, el formulario',
           ['src/data/paginas-de-servicio.js:66', 'src/paginas/Servicio.jsx:89', 'src/components/Barra.jsx:158',
            'src/lib/brief/preguntas.js:89-93'], True),
    'R8b': ('Desde /ley21719 el formulario de la portada llega sin el servicio marcado (el campo es opcional)',
            ['src/paginas/Ley21719.jsx:264', 'src/paginas/Inicio.jsx:33', 'src/components/Contacto.jsx:159-178'], False),
    'R9a': ('En desarrollo web, la cabecera ofrece el brief como «Cuéntanos tu proyecto»',
            ['src/data/paginas-de-servicio.js:66', 'src/paginas/Servicio.jsx:89'], False),
    'R10': ('El brief enviado antes de 8 s se descarta en silencio con 200 y el navegador borra lo guardado',
            ['src/lib/brief/reglas.js:38-40', 'worker/brief.js:280-285', 'src/comportamiento/brief/brief.js:669-680'], True),
    'R11': ('En el brief, Turnstile se monta al llegar a la revisión; si falla, las respuestas siguen guardadas',
            ['src/comportamiento/brief/brief.js:408', 'src/comportamiento/brief/brief.js:52-53',
             'src/comportamiento/brief/brief.js:681-684'], True),
    'R12': ('Sin almacenamiento, el brief no se guarda y lo avisa', ['src/lib/almacen.js:1-3',
                                                                    'src/comportamiento/brief/brief.js:163-166'], True),
    'R13': ('Sin GPU, sin WebGL o con movimiento reducido la escena queda quieta o en video y la página sigue entera',
            ['src/comportamiento/nubes.js:44-49', 'src/comportamiento/nubes.js:57-59'], False),
    'R14': ('El estimado escribe lo marcado en el mensaje del formulario de la misma página',
            ['src/comportamiento/estimado.js:61-72'], False),
    'R15': ('Un agente WebMCP rellena el formulario y deja el foco en «Enviar mensaje»: la persona lo envía',
            ['src/components/Contacto.jsx:40-43', 'src/components/Contacto.jsx:81-82'], False),
    'R16': ('Un agente WebMCP recibe el estimado con respondWith', ['src/comportamiento/estimado.js:78-86'], False),
    'R17': ('El brief guarda la hora de inicio con las respuestas: quien vuelve no cae en los 8 s',
            ['src/comportamiento/brief/brief.js:134-139', 'src/comportamiento/brief/brief.js:163'], False),
    'R21': ('Sin JavaScript (o si brief.js no carga) el brief llega con «transcurrido» vacío: se descarta en silencio y la página dice «Recibimos tu brief.»',
            ['src/paginas/Brief.jsx:326', 'src/comportamiento/brief/brief.js:640', 'src/client.js:299-302',
             'worker/brief.js:282-285', 'worker/brief.js:85'], True),
}
FRICCIONES = {k for k, (_, _, es) in REGLAS.items() if es}

# Recorrido cognitivo: (¿intenta el efecto correcto?, ¿nota la acción?, ¿la asocia al efecto?, ¿ve el progreso?)
CW = {
    'R1+R2': (('sí', 'sí', 'sí', 'no'), 'El aviso «Usa solo letras.» contradice lo que ve: su nombre solo tiene letras y un apóstrofo, que la regla quiere aceptar (O\'Higgins), y el cambio a ’ no se nota.'),
    'R1': (('sí', 'sí', 'sí', 'en parte'), 'El aviso dice qué hacer, pero le pide escribir su nombre (o el de su negocio) de otra forma.'),
    'R4': (('sí', 'sí', 'sí', 'no'), 'El aviso no dice que basta reintentar: manda a escribir al correo. La causa, un token que no llegó, no se ve.'),
    'R4b': (('sí', 'sí', 'sí', 'no'), 'Mismo aviso que R4; reintentar no sirve si su navegador bloquea la comprobación.'),
    'R6': (('sí', 'sí', 'sí', 'no'), 'El botón no abre WhatsApp desde el navegador de la app y nada lo avisa.'),
    'R7': (('sí', 'sí', 'sí', 'no'), 'La página de respuesta trae el correo como texto, sin enlace, y lo escrito se pierde al salir.'),
    'R8': (('sí', 'sí', 'no', 'no'), '«Pedir esta cotización» no lleva lo marcado: llega a un formulario vacío y sin el servicio, cuando en los otros servicios sí llega escrito.'),
    'R9': (('sí', 'sí', 'no', 'sí'), 'El mismo «Cuéntanos tu proyecto» lleva al formulario en la barra y a un brief de 35 a 45 min en la cabecera; el brief avisa su largo.'),
    'R10': (('sí', 'sí', 'sí', 'no'), 'La respuesta parece un éxito, sin número de referencia; no llegó nada y lo guardado se borró.'),
    'R11': (('sí', 'sí', 'sí', 'sí'), 'Falla, pero el aviso dice que las respuestas siguen guardadas y ofrece reintentar o copiarlas.'),
    'R12': (('sí', 'sí', 'sí', 'sí'), 'Avisó que no puede guardar («No cierres la página hasta enviar»).'),
    'R21': (('sí', 'sí', 'sí', 'no'), 'La página dice «Recibimos tu brief.» y no llegó nada.'),
}

RUTA = {
    'home': '/', 'articulo': 'un artículo', 'ley': '/ley21719', 'brief': '/brief-web',
}
RUTA_SERVICIO = {
    'web': '/servicios/desarrollo-web', 'tienda': '/servicios/tiendas-online', 'gestion': '/servicios/sistemas-de-gestion',
    'automatizacion': '/servicios/automatizacion-procesos', 'agente': '/servicios/agentes-ia',
    'app': '/servicios/desarrollo-software-a-medida', 'prospeccion': '/servicios/prospeccion-de-clientes',
    'datos': '/ley21719', 'no_sabe': '/servicios',
}


def ruta_de(u, donde):
    if donde == 'servicio':
        return RUTA_SERVICIO[u['servicio']]
    return RUTA[donde]


# --------------------------------------------------------------------------
# Parámetros: p50, sorteo con incertidumbre, ajuste Beta desde (p10, p90)
# --------------------------------------------------------------------------
def theta_p50():
    t = {k: v[0] for k, v in P.items()}
    t['cat'] = {k: list(v[0]) for k, v in C.items()}
    return t


def beta_desde(p50, p10, p90):
    sd = (p90 - p10) / 2.563
    var = sd * sd
    tope = p50 * (1 - p50) * 0.95
    var = min(var, tope)
    k = p50 * (1 - p50) / var - 1
    return max(p50 * k, 0.05), max((1 - p50) * k, 0.05)


def theta_sorteado(rng):
    t = {}
    for k, (p50, p10, p90, _) in P.items():
        a, b = beta_desde(p50, p10, p90)
        t[k] = rng.betavariate(a, b)
    t['cat'] = {}
    for k, (lista, kappa, _) in C.items():
        g = [rng.gammavariate(max(kappa * p, 1e-3), 1.0) for _, p in lista]
        s = sum(g)
        t['cat'][k] = [(v, x / s) for (v, _), x in zip(lista, g)]
    return t


def elegir(dist, x):
    acc = 0.0
    for v, p in dist:
        acc += p
        if x < acc:
            return v, p
    return dist[-1][0], dist[-1][1]


# --------------------------------------------------------------------------
# Red de perfiles: muestreo ancestral con uniformes fijos (números aleatorios comunes)
# --------------------------------------------------------------------------
N_UNIFORMES = 26


def muestrear(U, t):
    """Un usuario a partir de N_UNIFORMES uniformes y los parámetros t.
    Devuelve (atributos, log p). Las restricciones del código salen de la estructura."""
    cat = t['cat']
    lp = 0.0
    u = {}

    def bern(x, p):
        nonlocal lp
        r = x < p
        lp += math.log(p if r else 1 - p)
        return r

    def cat_(nombre, x, dist=None):
        nonlocal lp
        v, p = elegir(dist if dist is not None else cat[nombre], x)
        lp += math.log(max(p, 1e-300))
        return v

    u['relacion'] = 'cliente_brief' if bern(U[0], t['relacion_cliente_brief']) else 'prospecto'
    cliente = u['relacion'] == 'cliente_brief'
    u['canal'] = 'link_del_brief' if cliente else cat_('canal', U[1])

    if cliente:
        u['dispositivo'] = cat_('disp_cliente', U[2])
    elif u['canal'] == 'redes':
        m = t['movil_si_redes']
        u['dispositivo'] = cat_(None, U[2], [('movil', m), ('tablet', 0.01), ('escritorio', 1 - m - 0.01)])
    elif u['canal'] == 'recomendacion':
        m = t['movil_si_recomendacion']
        u['dispositivo'] = cat_(None, U[2], [('movil', m), ('tablet', 0.01), ('escritorio', 1 - m - 0.01)])
    else:
        u['dispositivo'] = cat_('disp_base', U[2])

    u['sistema'] = cat_({'movil': 'sistema_movil', 'escritorio': 'sistema_escritorio',
                         'tablet': 'sistema_tablet'}[u['dispositivo']], U[3])
    # El navegador de una app (Instagram, Facebook) es su propio webview: no se sortea otro.
    u['inapp'] = (not cliente and u['canal'] == 'redes' and u['dispositivo'] == 'movil'
                  and bern(U[5], t['inapp_si_redes_movil']))
    u['navegador'] = 'webview de la app' if u['inapp'] else cat_('nav_' + u['sistema'], U[4])
    if u['sistema'] in ('ios', 'ipados'):
        u['motor'] = 'webkit'
    elif u['navegador'] == 'firefox':
        u['motor'] = 'gecko'
    elif u['navegador'] == 'safari':
        u['motor'] = 'webkit'
    else:
        u['motor'] = 'blink'

    u['movimiento_reducido'] = bern(U[6], t['movimiento_reducido'])
    u['gpu'] = cat_('gpu_escritorio' if u['dispositivo'] == 'escritorio' else 'gpu_movil', U[7])
    u['js_off'] = bern(U[8], t['js_off'])  # el agente (más abajo) exige JS: se descarta si no lo hay
    u['almacen_bloqueado'] = bern(U[9], t['almacen_bloqueado'])
    p_estricta = min(t['estricta_base'] * (5 if u['navegador'] == 'firefox' else 1), 0.9)
    u['estricta'] = bern(U[10], p_estricta)
    puede_agente = (u['dispositivo'] == 'escritorio' and u['navegador'] in ('chrome', 'edge') and not u['inapp']
                    and not u['js_off'])
    u['agente'] = puede_agente and bern(U[11], t['agente_en_chrome_escritorio'])
    u['smart_punct'] = u['sistema'] in ('ios', 'ipados') and bern(U[12], t['smart_punct_on'])

    pa, pg, pe = t['nombre_apostrofo'], t['nombre_guion_punto'], t['nombre_empresa_signos']
    u['nombre_tipo'] = cat_(None, U[13], [('apostrofo', pa), ('guion_punto', pg), ('empresa_signos', pe),
                                          ('simple', 1 - pa - pg - pe)])

    u['tamano'] = cat_('tamano', U[14])
    if cliente:
        u['servicio'] = 'web'
    else:
        base = cat['servicio_base']
        incl = INCLINACION[u['tamano']]
        pesos = [(v, p * incl.get(v, 1.0)) for v, p in base]
        s = sum(p for _, p in pesos)
        u['servicio'] = cat_(None, U[15], [(v, p / s) for v, p in pesos])

    u['etapa'] = 'listo' if cliente else cat_('etapa_' + u['canal'], U[16])
    mult = {'explorando': 0.5, 'comparando': 1.0, 'listo': 2.0}[u['etapa']]
    u['pega_rapido'] = bern(U[17], min(t['pega_rapido_comparando'] * mult, 0.95))
    pw = t['whatsapp_si_escritorio'] if u['dispositivo'] == 'escritorio' else t['whatsapp_si_movil']
    u['canal_envio'] = 'whatsapp' if bern(U[18], pw) else 'correo'

    if cliente:
        u['destino'] = 'brief'
    else:
        dist = cat['destino_' + u['canal']]

        def final(crudo):
            if crudo == 'servicio' and u['servicio'] == 'datos':
                return 'ley'
            if crudo == 'servicio' and u['servicio'] == 'no_sabe':
                return 'home'
            return crudo

        crudo, _ = elegir(dist, U[19])
        d = final(crudo)
        # La probabilidad del destino suma los valores crudos que llevan a él.
        lp += math.log(max(sum(p for v, p in dist if final(v) == d), 1e-300))
        u['destino'] = d

    u['js_brief_falla'] = u['js_off'] or bern(U[23], t['brief_js_falla'])
    # Solo relato: no cambian nada en el flujo (el código no depende de ellas).
    u['rubro'] = cat_('rubro', U[20])
    u['region'] = cat_('region', U[21])
    u['edad'] = cat_('edad', U[22])
    return u, lp


def segmento(u):
    """Partición en perfiles (la primera que calza)."""
    if u['relacion'] == 'cliente_brief':
        return 'S6'
    if u['agente']:
        return 'S8'
    if u['js_off'] or u['estricta'] or u['almacen_bloqueado']:
        return 'S7'
    if u['servicio'] == 'datos':
        return 'S5'
    if u['sistema'] in ('ios', 'ipados'):
        return 'S4'
    if u['sistema'] == 'android':
        return 'S1'
    if u['servicio'] == 'web':
        return 'S2'
    return 'S3'


SEGMENTOS = {
    'S1': 'Celular o tablet Android',
    'S2': 'Escritorio, busca una página web',
    'S3': 'Escritorio, otros servicios',
    'S4': 'iPhone o iPad (WebKit, Smart Punctuation)',
    'S5': 'Negocio ante la Ley 21.719',
    'S6': 'Cliente con el link del brief',
    'S7': 'Entorno restrictivo (sin JS, privacidad estricta o sin almacenamiento)',
    'S8': 'Agente de IA por WebMCP',
}

# --------------------------------------------------------------------------
# Cadena de uso: ramas (prob, siguiente, etiqueta, regla)
# --------------------------------------------------------------------------
FIN = 'FIN'


def fin(x):
    return (FIN, x)


def ramas(u, t, s):
    k = s[0]
    if k == 'inicio':
        if u['relacion'] == 'cliente_brief':
            return [(1.0, ('brief_cliente',), 'abre el link del brief que le mandó Volutus', 'R17')]
        return [(1.0, ('pagina', u['destino'], 'llegada'), f"llega a {ruta_de(u, u['destino'])}", None)]

    if k == 'pagina':
        _, donde, momento = s
        out = []
        q_sale = t['sale_' + u['etapa']] if momento == 'llegada' else 0.0
        if q_sale:
            out.append((q_sale, fin('abandono_sin_intento'), 'se va sin buscar más', None))
        resto = 1 - q_sale
        if donde in ('home', 'articulo'):
            q = t['home_a_servicio' if donde == 'home' else 'articulo_a_servicio']
            if u['servicio'] == 'no_sabe':
                q = 0.0
            destino = 'ley' if u['servicio'] == 'datos' else 'servicio'
            if q:
                out.append((resto * q, ('pagina', destino, 'navegando'), f'va a {ruta_de(u, destino)}', None))
            out.append((resto * (1 - q), ('decide', donde), 'sigue en la portada' if donde == 'home'
                        else 'termina el artículo', None))
        elif donde == 'servicio':
            q = t['usa_estimado']
            if u['agente']:
                out.append((resto * q, ('estimado', 'servicio'), 'el agente usa «estimar_precio» y recibe el estimado', 'R16'))
            else:
                out.append((resto * q, ('estimado', 'servicio'), 'calcula un estimado', None))
            out.append((resto * (1 - q), ('decide', 'servicio'), 'lee la página sin calcular', None))
        elif donde == 'ley':
            q = t['usa_estimado_ley']
            out.append((resto * q, ('estimado', 'ley'), 'calcula un estimado de la ley de datos', None))
            out.append((resto * (1 - q), ('decide', 'ley'), 'lee la guía sin calcular', None))
        return out

    if k == 'estimado':
        q = t['pide_cotizacion']
        if s[1] == 'servicio':
            return [(q, ('form', 'servicio'), 'pulsa «Pedir esta cotización»: el mensaje llega escrito', 'R14'),
                    (1 - q, ('decide', 'servicio'), 'mira el precio y sigue leyendo', None)]
        return [(q, ('ley_a_portada',), 'pulsa «Pedir esta cotización»: va a la portada', 'R8'),
                (1 - q, ('decide', 'ley'), 'mira el precio y sigue leyendo', None)]

    if k == 'ley_a_portada':
        q = t['abandona_seleccion_perdida']
        return [(q, fin('abandono_por_friccion'), 'llega a un formulario vacío, sin lo que marcó, y se va', 'R8'),
                (1 - q, ('form', 'home'), 'escribe de nuevo lo que necesita', 'R8')]

    if k == 'decide':
        donde = s[1]
        q = t['contacta_' + u['etapa']]
        out = [(1 - q, fin('abandono_sin_intento'), 'decide no escribir por ahora', None)]
        if donde == 'servicio' and u['servicio'] == 'web':
            b = t['usa_cta_brief_web']
            out.append((q * b, ('brief_prospecto',), 'pulsa «Cuéntanos tu proyecto» de la cabecera: abre el brief', 'R9a'))
            out.append((q * (1 - b), ('form', 'servicio'), 'baja al formulario', None))
        elif donde == 'ley':
            out.append((q, ('form', 'home'), 'pulsa «Cuéntanos tu proyecto»: va al formulario de la portada', 'R8b'))
        else:
            out.append((q, ('form', donde), 'va al formulario', None))
        return out

    if k == 'brief_prospecto':
        q, v = t['envia_brief_prospecto'], t['vuelve_al_formulario']
        return [(q, ('validar_nombre', ('brief_envio',), 'brief'), 'llena lo obligatorio y llega a la revisión', None),
                ((1 - q) * v, ('form', 'servicio'), 've «35 a 45 min», vuelve y usa el formulario', 'R9'),
                ((1 - q) * (1 - v), fin('abandono_por_friccion'), 've «35 a 45 min» y lo deja para después', 'R9')]

    if k == 'brief_cliente':
        out = []
        resto = 1.0
        if u['almacen_bloqueado']:
            m = t['brief_en_varias_sesiones']
            out.append((m, fin('abandono_por_friccion'), 'lo llena en dos sesiones y al volver no hay nada guardado', 'R12'))
            resto = 1 - m
        q = t['cliente_completa_brief']
        out.append((resto * q, ('validar_nombre', ('brief_envio',), 'brief'), 'completa el brief y llega a la revisión', None))
        out.append((resto * (1 - q), fin('abandono_sin_intento'), 'no lo termina', None))
        return out

    if k == 'form':
        if u['js_off']:
            return [(1.0, ('nojs',), 'envía sin JavaScript: POST nativo', 'R7')]
        if u['canal_envio'] == 'whatsapp':
            return [(1.0, ('validar_nombre', ('whatsapp',), 'form'), 'elige WhatsApp y escribe', None)]
        regla = 'R15' if u['agente'] else None
        etiqueta = 'el agente rellena el formulario y la persona lo revisa' if u['agente'] else 'elige correo y escribe'
        return [(1.0, ('validar_nombre', ('envio_correo', 1), 'form'), etiqueta, regla)]

    if k == 'validar_nombre':
        _, siguiente, origen = s
        if origen == 'brief' and u['js_brief_falla']:
            return [(1.0, siguiente, 'sin brief.js no hay validación en el navegador', None)]
        n = u['nombre_tipo']
        if n == 'apostrofo' and u['smart_punct']:
            q = t['resuelve_nombre_opaco']
            return [(q, siguiente, '«Usa solo letras.»: quita el apóstrofo y sigue', 'R1+R2'),
                    (1 - q, fin('abandono_por_friccion'), '«Usa solo letras.» sobre su nombre bien escrito: se rinde', 'R1+R2')]
        if n in ('guion_punto', 'empresa_signos'):
            q = t['resuelve_nombre_claro']
            return [(q, siguiente, '«Usa solo letras.»: reescribe el nombre', 'R1'),
                    (1 - q, fin('abandono_por_friccion'), '«Usa solo letras.»: no sabe cómo escribirlo y se va', 'R1')]
        return [(1.0, siguiente, 'el nombre pasa', None)]

    if k == 'whatsapp':
        out = []
        resto = 1.0
        if u['inapp']:
            f, c = t['inapp_falla_whatsapp'], t['cambia_a_correo']
            out.append((f * c, ('envio_correo', 1), 'WhatsApp no abre desde la app: cambia a correo', 'R6'))
            out.append((f * (1 - c), fin('abandono_por_friccion'), 'WhatsApp no abre desde la app: se va', 'R6'))
            resto = 1 - f
        w = t['whatsapp_envia']
        out.append((resto * w, fin('contacto'), 'se abre WhatsApp con el mensaje escrito y lo envía', None))
        out.append((resto * (1 - w), fin('no_envia_whatsapp'), 'se abre WhatsApp pero no lo envía', None))
        return out

    if k == 'envio_correo':
        intento = s[1]
        if u['agente']:
            tn = t['token_no_listo_agente'] if intento == 1 else 0.02
        elif u['pega_rapido']:
            tn = (t['token_no_listo_rapido_movil'] if u['dispositivo'] != 'escritorio'
                  else t['token_no_listo_rapido_escritorio']) if intento == 1 else 0.02
        else:
            tn = t['token_no_listo_normal'] if intento == 1 else 0.002
        tf = t['turnstile_falla_estricta'] if u['estricta'] else t['turnstile_falla_normal']
        rf = t['resend_falla']
        return [((1 - tn) * (1 - tf) * (1 - rf), fin('contacto'), 'envía: «¡Gracias por escribirnos!»', None),
                (tn, ('tras_error', intento, 'R4'), 'envía antes de que llegue el token: 403 «No pudimos enviar tu mensaje…»', 'R4'),
                ((1 - tn) * tf, ('tras_error', intento, 'R4b'), 'Turnstile no pasa: 403 «No pudimos enviar tu mensaje…»', 'R4b'),
                ((1 - tn) * (1 - tf) * rf, ('tras_error', 2, 'R5'), 'Resend no responde: 502', 'R5')]

    if k == 'tras_error':
        _, intento, causa = s
        r = t['reintenta_tras_403'] if intento == 1 else 0.0
        c = t['correo_directo_tras_error']
        out = []
        if r:
            out.append((r, ('envio_correo', 2), 'cierra el aviso y vuelve a enviar', causa))
        out.append(((1 - r) * c, fin('correo_directo'), 'copia el correo del aviso y escribe desde su correo', causa))
        out.append(((1 - r) * (1 - c), fin('abandono_por_friccion'), 'cree que el sitio falla y se va', causa))
        return out

    if k == 'nojs':
        valido = u['nombre_tipo'] == 'simple' or (u['nombre_tipo'] == 'apostrofo' and not u['smart_punct'])
        aviso = ('página «No pudimos enviar tu mensaje. Escríbenos directamente a…»' if valido
                 else 'página «Faltan datos o el correo no es válido…»')
        c = t['nojs_correo_directo']
        return [(c, fin('correo_directo'), f'{aviso}: escribe desde su correo', 'R7'),
                (1 - c, fin('abandono_por_friccion'), f'{aviso}: se va', 'R7')]

    if k == 'brief_envio':
        if u['js_brief_falla']:
            return [(1.0, fin('perdida_silenciosa'), 'POST nativo con «transcurrido» vacío: «Recibimos tu brief.» y no llega nada', 'R21')]
        out = []
        resto = 1.0
        if u['agente']:
            a = t['brief_rapido_si_agente']
            out.append((a, fin('perdida_silenciosa'), 'el agente lo llena y la persona envía antes de 8 s: «Recibimos tu brief.» y no llega nada', 'R10'))
            resto = 1 - a
        cr = t['carrera_turnstile_brief']
        tf = t['turnstile_falla_estricta'] if u['estricta'] else t['turnstile_falla_normal']
        e = cr + (1 - cr) * tf
        rb = t['reintenta_brief']
        out.append((resto * (1 - e), fin('contacto'), 'envía: «Tu número de referencia es B-…»', None))
        out.append((resto * e * rb, fin('contacto'), 'falla el envío; sus respuestas siguen guardadas y reintenta', 'R11'))
        out.append((resto * e * (1 - rb), fin('correo_directo'), 'falla el envío; copia sus respuestas y las manda por correo', 'R11'))
        return out

    raise ValueError(s)


DESENLACES = ['contacto', 'contacto_con_friccion', 'correo_directo', 'no_envia_whatsapp',
              'abandono_sin_intento', 'abandono_por_friccion', 'perdida_silenciosa']


def evaluar(u, t):
    """Probabilidad exacta de cada desenlace (absorción de la cadena) y atribución por regla."""
    acum = defaultdict(float)
    por_regla = defaultdict(float)

    def rec(s, prob, causa, prof):
        if prof > 30:
            raise RuntimeError('ciclo')
        for p, s2, _, regla in ramas(u, t, s):
            if p <= 0:
                continue
            c2 = regla if regla in FRICCIONES else causa
            if s2[0] == FIN:
                d = s2[1]
                if d == 'contacto' and c2:
                    d = 'contacto_con_friccion'
                acum[d] += prob * p
                if d in ('abandono_por_friccion', 'perdida_silenciosa', 'correo_directo', 'contacto_con_friccion'):
                    por_regla[(c2, d)] += prob * p
            else:
                rec(s2, prob * p, c2, prof + 1)

    rec(('inicio',), 1.0, None, 0)
    return acum, por_regla


def trazar(u, t, rng, forzar=None):
    """Una traza sorteada (o forzada por una lista de índices de rama)."""
    s = ('inicio',)
    pasos = []
    causa = None
    prob_camino = 1.0
    i = 0
    while True:
        opciones = [o for o in ramas(u, t, s) if o[0] > 0]
        if forzar is not None:
            j = forzar[i]
            x = None
        else:
            x = rng.random()
            acc = 0.0
            j = len(opciones) - 1
            for idx, o in enumerate(opciones):
                acc += o[0]
                if x < acc:
                    j = idx
                    break
        p, s2, etiqueta, regla = opciones[j]
        prob_camino *= p
        if regla in FRICCIONES:
            causa = regla
        cw = CW.get(regla) if regla in FRICCIONES else None
        pasos.append({'estado': estado_legible(u, s), 'sorteo': None if x is None else round(x, 3),
                      'prob': round(p, 4), 'accion': etiqueta, 'regla': regla,
                      'evidencia': REGLAS[regla][1] if regla else None,
                      'cw': cw[0] if cw else ('sí', 'sí', 'sí', 'sí'), 'nota_cw': cw[1] if cw else None,
                      'arco': arco_de(s, etiqueta)})
        i += 1
        if s2[0] == FIN:
            d = s2[1]
            if d == 'contacto' and causa:
                d = 'contacto_con_friccion'
            return pasos, d, prob_camino
        s = s2


TIPO_DE_RUTA = {**{v: 'la página de su servicio' for k, v in RUTA_SERVICIO.items() if k not in ('datos', 'no_sabe')},
                '/ley21719': '/ley21719', '/': 'la portada', 'un artículo': 'un artículo', '/brief-web': '/brief-web'}


def arco_de(s, etiqueta):
    """El arco del grafo, sin la ruta concreta: la ruta es una superficie, no un arco."""
    for prefijo in ('llega a ', 'va a '):
        if etiqueta.startswith(prefijo):
            return (s[0], prefijo + TIPO_DE_RUTA.get(etiqueta[len(prefijo):], etiqueta[len(prefijo):]))
    return (s[0], etiqueta)


SUPERFICIES = (['/'] + [v for k, v in RUTA_SERVICIO.items() if k not in ('no_sabe',)] + ['un artículo', '/brief-web']
               + ['formulario de contacto', 'estimado', 'brief', 'WhatsApp', 'POST /api/contacto', 'POST /api/brief']
               + [k for k in REGLAS])


def superficies_de(u, pasos):
    vistas = set()
    for p in pasos:
        a = p['accion']
        for prefijo in ('llega a ', 'va a '):
            if a.startswith(prefijo):
                vistas.add(a[len(prefijo):])
        if p['estado'].startswith('Formulario'):
            vistas.add('formulario de contacto')
        if p['estado'].startswith('Estimado'):
            vistas.add('estimado')
        if p['estado'].startswith('Brief'):
            vistas.add('brief')
        if p['estado'] == 'WhatsApp':
            vistas.add('WhatsApp')
        if p['estado'].startswith('Envío por correo') or p['estado'] == 'Respuesta sin JavaScript':
            vistas.add('POST /api/contacto')
        if p['estado'] == 'Envío del brief':
            vistas.add('POST /api/brief')
        if p['regla']:
            vistas.add(p['regla'])
        if 'brief' in a and 'abre el link' in a:
            vistas.add('/brief-web')
    if u['gpu'] != 'ok' or u['movimiento_reducido']:
        vistas.add('R13')
    if u['agente']:
        vistas.add('R15')
    return vistas


def estado_legible(u, s):
    k = s[0]
    if k == 'inicio':
        return 'Llegada'
    if k == 'pagina':
        return f"En {ruta_de(u, s[1])}"
    if k == 'estimado':
        return 'Estimado' + (' de la ley de datos' if s[1] == 'ley' else '')
    if k == 'ley_a_portada':
        return 'Portada, tras «Pedir esta cotización»'
    if k == 'decide':
        return '¿Escribe?'
    if k == 'brief_prospecto':
        return 'Brief (prospecto)'
    if k == 'brief_cliente':
        return 'Brief (cliente)'
    if k == 'form':
        return 'Formulario' + (' de la portada' if s[1] == 'home' else '')
    if k == 'validar_nombre':
        return 'Validación del nombre'
    if k == 'whatsapp':
        return 'WhatsApp'
    if k == 'envio_correo':
        return 'Envío por correo' + (' (2.º intento)' if s[1] == 2 else '')
    if k == 'tras_error':
        return 'Tras el error'
    if k == 'nojs':
        return 'Respuesta sin JavaScript'
    if k == 'brief_envio':
        return 'Envío del brief'
    return k


# --------------------------------------------------------------------------
# Población: métricas por perfil
# --------------------------------------------------------------------------
def uniformes(rng, n):
    return [[rng.random() for _ in range(N_UNIFORMES)] for _ in range(n)]


def poblacion(t, US):
    tot = defaultdict(float)
    seg_masa = Counter()
    seg_des = defaultdict(lambda: defaultdict(float))
    regla = defaultdict(float)
    for U in US:
        u, _ = muestrear(U, t)
        s = segmento(u)
        seg_masa[s] += 1
        acum, pr = evaluar(u, t)
        for d, p in acum.items():
            tot[d] += p
            seg_des[s][d] += p
        for k, p in pr.items():
            regla[k] += p
    n = len(US)
    return ({d: tot[d] / n for d in DESENLACES},
            {s: seg_masa[s] / n for s in SEGMENTOS},
            {s: {d: seg_des[s][d] / max(seg_masa[s], 1e-9) for d in DESENLACES} for s in SEGMENTOS},
            {k: v / n for k, v in regla.items()})


def metricas(tot):
    contacto = tot['contacto'] + tot['contacto_con_friccion'] + tot['correo_directo']
    perdida = tot['abandono_por_friccion'] + tot['perdida_silenciosa']
    friccion = perdida + tot['correo_directo'] + tot['contacto_con_friccion']
    return {'contacto_total': contacto, 'perdida_por_codigo': perdida, 'con_friccion': friccion}


# --------------------------------------------------------------------------
# Cobertura por pares
# --------------------------------------------------------------------------
def factores(u):
    plat = {'android': 'android', 'ios': 'ios_ipados', 'ipados': 'ios_ipados', 'windows': 'windows_linux',
            'linux': 'windows_linux', 'macos': 'macos'}[u['sistema']]
    nombre = {'simple': 'simple', 'apostrofo': 'apostrofo', 'guion_punto': 'otros_signos',
              'empresa_signos': 'otros_signos'}[u['nombre_tipo']]
    return {
        'plataforma': plat, 'motor': u['motor'], 'navegador_de_app': u['inapp'], 'canal_envio': u['canal_envio'],
        'js': 'inactivo' if u['js_off'] else 'activo',
        'almacenamiento': 'bloqueado' if u['almacen_bloqueado'] else 'ok',
        'movimiento': 'reducido' if u['movimiento_reducido'] else 'normal', 'gpu': u['gpu'],
        'usuario': 'agente' if u['agente'] else 'persona', 'nombre': nombre,
        'ritmo': 'pega_rapido' if u['pega_rapido'] else 'normal',
        'privacidad': 'estricta' if u['estricta'] else 'normal', 'destino': u['destino'],
    }


def pares(f):
    ks = sorted(f)
    return {(a, str(f[a]), b, str(f[b])) for i, a in enumerate(ks) for b in ks[i + 1:]}


def theta_aplanado():
    """q: la misma red con lo raro inflado, para generar candidatos de cobertura."""
    t = theta_p50()
    t.update({'relacion_cliente_brief': 0.25, 'inapp_si_redes_movil': 0.6, 'movimiento_reducido': 0.3,
              'js_off': 0.15, 'brief_js_falla': 0.1, 'almacen_bloqueado': 0.2, 'estricta_base': 0.2,
              'agente_en_chrome_escritorio': 0.5, 'nombre_apostrofo': 0.2, 'nombre_guion_punto': 0.15,
              'nombre_empresa_signos': 0.15, 'pega_rapido_comparando': 0.3, 'whatsapp_si_escritorio': 0.4})
    c = t['cat']
    c['disp_base'] = [('escritorio', 0.45), ('movil', 0.45), ('tablet', 0.10)]
    c['sistema_movil'] = [('android', 0.5), ('ios', 0.5)]
    c['sistema_escritorio'] = [('windows', 0.5), ('macos', 0.35), ('linux', 0.15)]
    c['nav_android'] = [('chrome', 0.6), ('samsung', 0.15), ('opera', 0.1), ('firefox', 0.15)]
    c['nav_windows'] = [('chrome', 0.5), ('edge', 0.25), ('firefox', 0.15), ('opera', 0.1)]
    c['nav_macos'] = [('safari', 0.4), ('chrome', 0.4), ('firefox', 0.2)]
    c['gpu_escritorio'] = [('ok', 0.4), ('lenta', 0.3), ('sin_webgl', 0.3)]
    c['gpu_movil'] = [('ok', 0.4), ('lenta', 0.3), ('sin_webgl', 0.3)]
    c['canal'] = [('google', 0.2), ('articulo', 0.2), ('recomendacion', 0.15), ('redes', 0.2),
                  ('directo', 0.1), ('ia', 0.15)]
    c['servicio_base'] = [(v, 1 / 9) for v, _ in c['servicio_base']]
    for k in list(c):
        if k.startswith('destino_') and len(c[k]) > 1:
            c[k] = [(v, 1 / len(c[k])) for v, _ in c[k]]
    return t


# --------------------------------------------------------------------------
# Programa
# --------------------------------------------------------------------------
def main():
    rng = random.Random(SEMILLA)
    t50 = theta_p50()

    # 1. Población grande (p50): masa de cada perfil y desenlaces exactos por usuario.
    US_grande = uniformes(random.Random(SEMILLA + 1), 120_000)
    tot, masa, por_seg, por_regla = poblacion(t50, US_grande)

    # 2. Fidelidad del generador: marginales declaradas contra las de la muestra.
    muestras = [muestrear(U, t50)[0] for U in US_grande]
    n = len(muestras)
    fid = []

    def frac(f):
        return sum(1 for u in muestras if f(u)) / n

    def frac_cond(f, g):
        sub = [u for u in muestras if g(u)]
        return sum(1 for u in sub if f(u)) / max(len(sub), 1), len(sub)

    for nombre, decl, obs in [
        ('relación: cliente con link', P['relacion_cliente_brief'][0], frac(lambda u: u['relacion'] == 'cliente_brief')),
        ('sin JavaScript', P['js_off'][0], frac(lambda u: u['js_off'])),
        ('sin almacenamiento', P['almacen_bloqueado'][0], frac(lambda u: u['almacen_bloqueado'])),
        ('movimiento reducido', P['movimiento_reducido'][0], frac(lambda u: u['movimiento_reducido'])),
        ('nombre con apóstrofo', P['nombre_apostrofo'][0], frac(lambda u: u['nombre_tipo'] == 'apostrofo')),
        ('nombre con guion o punto', P['nombre_guion_punto'][0], frac(lambda u: u['nombre_tipo'] == 'guion_punto')),
    ]:
        fid.append({'variable': nombre, 'declarada': decl, 'muestra': obs, 'n': n})
    for nombre, decl, (obs, m) in [
        ('iOS, dado celular (ancla 20,72 %)', 0.2072,
         frac_cond(lambda u: u['sistema'] == 'ios', lambda u: u['dispositivo'] == 'movil')),
        ('Windows, dado escritorio (ancla 85,02 %)', 0.8502,
         frac_cond(lambda u: u['sistema'] == 'windows', lambda u: u['dispositivo'] == 'escritorio')),
        ('celular, dado que llega por Google (ancla 49,12 %)', 0.4912,
         frac_cond(lambda u: u['dispositivo'] == 'movil', lambda u: u['canal'] == 'google')),
        ('Smart Punctuation, dado iOS o iPadOS', P['smart_punct_on'][0],
         frac_cond(lambda u: u['smart_punct'], lambda u: u['sistema'] in ('ios', 'ipados'))),
    ]:
        fid.append({'variable': nombre, 'declarada': decl, 'muestra': obs, 'n': m})

    marginal = {
        'dispositivo': Counter(u['dispositivo'] for u in muestras),
        'sistema': Counter(u['sistema'] for u in muestras),
        'motor': Counter(u['motor'] for u in muestras),
        'servicio': Counter(u['servicio'] for u in muestras),
        'destino': Counter(u['destino'] for u in muestras),
        'canal_envio': Counter(u['canal_envio'] for u in muestras),
        'agente': Counter(u['agente'] for u in muestras),
    }
    marginal = {k: {str(v): c / n for v, c in sorted(cnt.items(), key=lambda kv: -kv[1])} for k, cnt in marginal.items()}

    # 3. Usuarios representativos: 12 sorteados de la red tal cual.
    usuarios = []
    for i in range(12):
        U = [rng.random() for _ in range(N_UNIFORMES)]
        u, lp = muestrear(U, t50)
        usuarios.append({'u': u, 'U': U, 'tipo': 'representativo', 'peso': None, 'logp': lp})

    # 4. Cobertura por pares (AETG voraz con candidatos de la red aplanada; las
    #    restricciones del código se cumplen porque los candidatos salen de la red).
    tq = theta_aplanado()
    rng_c = random.Random(SEMILLA + 2)
    universo = set()
    candidatos_universo = []
    for _ in range(60_000):
        U = [rng_c.random() for _ in range(N_UNIFORMES)]
        u, _ = muestrear(U, tq)
        universo |= pares(factores(u))
        candidatos_universo.append(U)
    cubiertos = set()
    for x in usuarios:
        cubiertos |= pares(factores(x['u']))
    while cubiertos < universo:
        mejor, mejor_n, mejor_U = None, -1, None
        for _ in range(3000):
            U = [rng_c.random() for _ in range(N_UNIFORMES)]
            u, _ = muestrear(U, tq)
            nuevos = len(pares(factores(u)) - cubiertos)
            if nuevos > mejor_n:
                mejor, mejor_n, mejor_U = u, nuevos, U
        if mejor_n <= 0:
            break
        lq = muestrear(mejor_U, tq)[1]
        # El peso es p(x)/q(x) del usuario elegido: su log p se reconstruye bajo p50.
        lp_mismo = logp_de(mejor, t50)
        usuarios.append({'u': mejor, 'U': mejor_U, 'tipo': 'cobertura', 'peso': math.exp(lp_mismo - lq),
                         'logp': lp_mismo, 'nuevos_pares': mejor_n})
        cubiertos |= pares(factores(mejor))
    cobertura_pares = {'universo': len(universo), 'cubiertos': len(cubiertos & universo),
                       'faltan': sorted([list(p) for p in universo - cubiertos])}

    # 5. Nombres sintéticos y trazas sorteadas.
    nombrar(usuarios, random.Random(SEMILLA + 3))
    trazas = []
    arcos_cubiertos = set()
    superficies_vistas = set()
    for i, x in enumerate(usuarios, 1):
        x['id'] = f'U{i:02d}'
        x['segmento'] = segmento(x['u'])
        acum, _ = evaluar(x['u'], t50)
        x['esperado'] = {d: round(acum.get(d, 0), 4) for d in DESENLACES}
        pasos, d, pc = trazar(x['u'], t50, random.Random(SEMILLA * 100 + i))
        trazas.append({'id': x['id'], 'forzada': False, 'pasos': pasos, 'desenlace': d, 'prob_camino': pc})
        arcos_cubiertos |= {tuple(p['arco']) for p in pasos}
        superficies_vistas |= superficies_de(x['u'], pasos)

    # 6. Universo de arcos: todo lo alcanzable desde los usuarios de la muestra y la red aplanada.
    universo_arcos = set()
    for U in candidatos_universo[:20_000]:
        u, _ = muestrear(U, tq)
        universo_arcos |= arcos_alcanzables(u, t50)
    faltan_arcos = universo_arcos - arcos_cubiertos
    superficies_total = set(superficies_vistas)
    forzadas = []
    for arco in sorted(faltan_arcos):
        mejor = None
        for x in usuarios:
            camino = mejor_camino(x['u'], t50, arco)
            if camino and (mejor is None or camino[1] > mejor[2]):
                mejor = (x, camino[0], camino[1])
        if mejor:
            x, idx, pc = mejor
            pasos, d, _ = trazar(x['u'], t50, None, forzar=idx)
            forzadas.append({'id': x['id'], 'forzada': True, 'arco': list(arco), 'pasos': pasos,
                             'desenlace': d, 'prob_camino': pc})
            arcos_cubiertos |= {tuple(p['arco']) for p in pasos}
            superficies_total |= superficies_de(x['u'], pasos)
    cobertura_arcos = {'universo': len(universo_arcos), 'cubiertos_sorteo': len(universo_arcos - faltan_arcos),
                       'cubiertos_total': len(universo_arcos & arcos_cubiertos),
                       'faltan': sorted([list(a) for a in universo_arcos - arcos_cubiertos])}

    # 7. Incertidumbre: 200 sorteos de parámetros, misma población (números comunes).
    US = uniformes(random.Random(SEMILLA + 4), 3000)
    rng_t = random.Random(SEMILLA + 5)
    corridas = []
    for _ in range(200):
        tt = theta_sorteado(rng_t)
        tt_tot, tt_masa, _, _ = poblacion(tt, US)
        m = metricas(tt_tot)
        m.update({'masa_' + s: v for s, v in tt_masa.items()})
        corridas.append(m)
    intervalos = {}
    for k in corridas[0]:
        xs = sorted(c[k] for c in corridas)
        intervalos[k] = {'p5': xs[int(0.05 * len(xs))], 'p50': xs[len(xs) // 2], 'p95': xs[int(0.95 * len(xs)) - 1]}

    # 8. Morris: qué supuesto mueve más el resultado.
    claves = ['movil_si_recomendacion', 'relacion_cliente_brief', 'nombre_apostrofo', 'smart_punct_on',
              'resuelve_nombre_opaco', 'nombre_guion_punto', 'nombre_empresa_signos', 'resuelve_nombre_claro',
              'pega_rapido_comparando', 'token_no_listo_rapido_movil', 'token_no_listo_rapido_escritorio',
              'reintenta_tras_403', 'correo_directo_tras_error', 'usa_estimado_ley', 'pide_cotizacion',
              'abandona_seleccion_perdida', 'usa_cta_brief_web', 'envia_brief_prospecto', 'vuelve_al_formulario',
              'estricta_base', 'turnstile_falla_estricta', 'js_off', 'contacta_comparando', 'sale_explorando']
    morris = correr_morris(claves, US[:2000], r=10, rng=random.Random(SEMILLA + 6))

    # 9. Hipótesis: qué cambia si se corrige cada fricción.
    US_h = uniformes(random.Random(SEMILLA + 7), 20_000)
    base = metricas(poblacion(t50, US_h)[0])
    hipotesis = {'base': base}
    for nombre, cambios in arreglos().items():
        tt = theta_p50()
        tt.update(cambios.get('theta', {}))
        hipotesis[nombre] = metricas(poblacion_con_arreglo(tt, US_h, cambios.get('reglas', set()))[0])

    json.dump({'semilla': SEMILLA, 'desenlaces_p50': tot, 'metricas_p50': metricas(tot), 'masa': masa,
               'por_segmento': por_seg, 'por_regla': {f'{k[0]}|{k[1]}': v for k, v in por_regla.items()},
               'fidelidad': fid, 'marginales': marginal, 'cobertura_pares': cobertura_pares,
               'cobertura_arcos': cobertura_arcos,
               'cobertura_superficies': {'universo': SUPERFICIES, 'vistas_en_sorteo': sorted(superficies_vistas & set(SUPERFICIES)),
                                         'vistas_total': sorted(superficies_total & set(SUPERFICIES)),
                                         'faltan_sorteo': [x for x in SUPERFICIES if x not in superficies_vistas],
                                         'faltan_total': [x for x in SUPERFICIES if x not in superficies_total]},
               'intervalos': intervalos, 'morris': morris,
               'hipotesis': hipotesis},
              open(os.path.join(SALIDA, 'agregados.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump([{'id': x['id'], 'tipo': x['tipo'], 'peso': x['peso'], 'segmento': x['segmento'],
                'nombre': x['nombre'], 'nuevos_pares': x.get('nuevos_pares'), 'atributos': x['u'],
                'factores': factores(x['u']), 'esperado': x['esperado']} for x in usuarios],
              open(os.path.join(SALIDA, 'usuarios.json'), 'w'), ensure_ascii=False, indent=1)
    json.dump(trazas + forzadas, open(os.path.join(SALIDA, 'trazas.json'), 'w'), ensure_ascii=False, indent=1)
    print('usuarios', len(usuarios), 'trazas', len(trazas), 'forzadas', len(forzadas))
    print('pares', cobertura_pares['cubiertos'], '/', cobertura_pares['universo'])
    print('arcos', cobertura_arcos['cubiertos_total'], '/', cobertura_arcos['universo'])
    print('metricas p50', metricas(tot))


def logp_de(u, t):
    """log p de un usuario ya fijado: se recorre la red con uniformes que caen en su valor."""
    U = buscar_uniformes(u, t)
    v, lp = muestrear(U, t)
    clave = ('relacion', 'canal', 'dispositivo', 'sistema', 'navegador', 'inapp', 'movimiento_reducido', 'gpu',
             'js_off', 'almacen_bloqueado', 'estricta', 'agente', 'smart_punct', 'nombre_tipo', 'tamano',
             'servicio', 'etapa', 'pega_rapido', 'canal_envio', 'destino', 'js_brief_falla')
    assert all(v[k] == u[k] for k in clave), 'logp_de: no se pudo reconstruir el usuario'
    return lp


def buscar_uniformes(u, t):
    """Uniformes que reproducen las decisiones de u bajo t (centro del tramo de cada valor)."""
    cat = t['cat']
    U = [0.5] * N_UNIFORMES

    def centro(dist, valor):
        acc = 0.0
        for v, p in dist:
            if v == valor:
                return acc + p / 2
            acc += p
        raise KeyError(valor)

    def b(i, verdadero, p):
        U[i] = p / 2 if verdadero else p + (1 - p) / 2

    cliente = u['relacion'] == 'cliente_brief'
    b(0, cliente, t['relacion_cliente_brief'])
    if not cliente:
        U[1] = centro(cat['canal'], u['canal'])
    if cliente:
        U[2] = centro(cat['disp_cliente'], u['dispositivo'])
    elif u['canal'] in ('redes', 'recomendacion'):
        m = t['movil_si_redes' if u['canal'] == 'redes' else 'movil_si_recomendacion']
        U[2] = centro([('movil', m), ('tablet', 0.01), ('escritorio', 1 - m - 0.01)], u['dispositivo'])
    else:
        U[2] = centro(cat['disp_base'], u['dispositivo'])
    U[3] = centro(cat[{'movil': 'sistema_movil', 'escritorio': 'sistema_escritorio',
                       'tablet': 'sistema_tablet'}[u['dispositivo']]], u['sistema'])
    if not u['inapp']:
        U[4] = centro(cat['nav_' + u['sistema']], u['navegador'])
    b(5, u['inapp'], t['inapp_si_redes_movil'])
    b(6, u['movimiento_reducido'], t['movimiento_reducido'])
    U[7] = centro(cat['gpu_escritorio' if u['dispositivo'] == 'escritorio' else 'gpu_movil'], u['gpu'])
    b(8, u['js_off'], t['js_off'])
    b(9, u['almacen_bloqueado'], t['almacen_bloqueado'])
    b(10, u['estricta'], min(t['estricta_base'] * (5 if u['navegador'] == 'firefox' else 1), 0.9))
    b(11, u['agente'], t['agente_en_chrome_escritorio'])
    b(12, u['smart_punct'], t['smart_punct_on'])
    pa, pg, pe = t['nombre_apostrofo'], t['nombre_guion_punto'], t['nombre_empresa_signos']
    U[13] = centro([('apostrofo', pa), ('guion_punto', pg), ('empresa_signos', pe), ('simple', 1 - pa - pg - pe)],
                   u['nombre_tipo'])
    U[14] = centro(cat['tamano'], u['tamano'])
    if not cliente:
        incl = INCLINACION[u['tamano']]
        pesos = [(v, p * incl.get(v, 1.0)) for v, p in cat['servicio_base']]
        s = sum(p for _, p in pesos)
        U[15] = centro([(v, p / s) for v, p in pesos], u['servicio'])
        U[16] = centro(cat['etapa_' + u['canal']], u['etapa'])
    mult = {'explorando': 0.5, 'comparando': 1.0, 'listo': 2.0}[u['etapa']]
    b(17, u['pega_rapido'], min(t['pega_rapido_comparando'] * mult, 0.95))
    pw = t['whatsapp_si_escritorio'] if u['dispositivo'] == 'escritorio' else t['whatsapp_si_movil']
    b(18, u['canal_envio'] == 'whatsapp', pw)
    if not cliente:
        d = u['destino']
        crudo = 'servicio' if d in ('ley',) or (d == 'servicio') else d
        if d == 'home' and u['servicio'] == 'no_sabe' and 'servicio' in dict(cat['destino_' + u['canal']]):
            crudo = 'home'
        U[19] = centro(cat['destino_' + u['canal']], crudo)
    U[20] = centro(cat['rubro'], u['rubro'])
    U[21] = centro(cat['region'], u['region'])
    U[22] = centro(cat['edad'], u['edad'])
    if not u['js_off']:
        b(23, u['js_brief_falla'], t['brief_js_falla'])
    return U


def arcos_alcanzables(u, t):
    arcos = set()

    def rec(s, prof):
        if prof > 30:
            return
        for p, s2, etiqueta, _ in ramas(u, t, s):
            if p <= 0:
                continue
            arcos.add(arco_de(s, etiqueta))
            if s2[0] != FIN:
                rec(s2, prof + 1)

    rec(('inicio',), 0)
    return arcos


def mejor_camino(u, t, arco):
    """Índices de rama del camino más probable que pasa por `arco`, y su probabilidad."""
    mejor = [None, 0.0]

    def rec(s, idx, prob, visto, prof):
        if prof > 30:
            return
        opciones = [o for o in ramas(u, t, s) if o[0] > 0]
        for j, (p, s2, etiqueta, _) in enumerate(opciones):
            v2 = visto or arco_de(s, etiqueta) == tuple(arco)
            if s2[0] == FIN:
                if v2 and prob * p > mejor[1]:
                    mejor[0], mejor[1] = idx + [j], prob * p
            else:
                rec(s2, idx + [j], prob * p, v2, prof + 1)

    rec(('inicio',), [], 1.0, False, 0)
    return (mejor[0], mejor[1]) if mejor[0] else None


def correr_morris(claves, US, r, rng):
    niveles = 4
    delta = niveles / (2 * (niveles - 1))
    efectos = {k: {'contacto_total': [], 'perdida_por_codigo': []} for k in claves}

    def evaluar_x(x):
        t = theta_p50()
        for k, v in zip(claves, x):
            _, p10, p90, _ = P[k]
            t[k] = p10 + v * (p90 - p10)
        return metricas(poblacion(t, US)[0])

    for _ in range(r):
        x = [rng.choice([0, 1 / 3]) for _ in claves]
        y = evaluar_x(x)
        orden = list(range(len(claves)))
        rng.shuffle(orden)
        for i in orden:
            x2 = list(x)
            x2[i] = x[i] + delta if x[i] + delta <= 1 + 1e-9 else x[i] - delta
            y2 = evaluar_x(x2)
            signo = 1 if x2[i] > x[i] else -1
            for m in ('contacto_total', 'perdida_por_codigo'):
                efectos[claves[i]][m].append(signo * (y2[m] - y[m]) / delta)
            x, y = x2, y2
    salida = []
    for k in claves:
        fila = {'parametro': k, 'rango': [P[k][1], P[k][2]]}
        for m in ('contacto_total', 'perdida_por_codigo'):
            ee = efectos[k][m]
            fila[m] = {'mu_estrella': statistics.fmean(abs(e) for e in ee), 'sigma': statistics.pstdev(ee)}
        salida.append(fila)
    salida.sort(key=lambda f: -f['perdida_por_codigo']['mu_estrella'])
    return salida


def arreglos():
    return {
        'R1+R2: aceptar ’, guion y punto en el nombre': {'reglas': {'nombre'}},
        'R4: esperar el token antes de enviar': {'theta': {'token_no_listo_rapido_movil': 0.002,
                                                          'token_no_listo_rapido_escritorio': 0.002,
                                                          'token_no_listo_normal': 0.002,
                                                          'token_no_listo_agente': 0.002}},
        'R8: llevar lo marcado y el servicio desde /ley21719': {'reglas': {'ley'}},
        'R9: «Cuéntanos tu proyecto» de la cabecera al formulario': {'theta': {'usa_cta_brief_web': 0.0}},
        'R21+R10: el brief sin JS (o apurado) responde como el contacto': {'reglas': {'brief_silencio'}},
        'Todos': {'reglas': {'nombre', 'ley', 'brief_silencio'},
                  'theta': {'token_no_listo_rapido_movil': 0.002, 'token_no_listo_rapido_escritorio': 0.002,
                            'token_no_listo_normal': 0.002, 'token_no_listo_agente': 0.002,
                            'usa_cta_brief_web': 0.0}},
    }


def poblacion_con_arreglo(t, US, reglas):
    """Como `poblacion`, pero con las ramas que cambia cada arreglo."""
    global ramas
    original = ramas

    def ramas_arregladas(u, tt, s):
        k = s[0]
        if 'nombre' in reglas and k == 'validar_nombre' and u['nombre_tipo'] in ('apostrofo', 'guion_punto'):
            return [(1.0, s[1], 'el nombre pasa', None)]
        if 'ley' in reglas and k == 'estimado' and s[1] == 'ley':
            q = tt['pide_cotizacion']
            return [(q, ('form', 'servicio'), 'pulsa «Pedir esta cotización»: el mensaje llega escrito', 'R14'),
                    (1 - q, ('decide', 'ley'), 'mira el precio y sigue leyendo', None)]
        if 'ley' in reglas and k == 'ley_a_portada':
            return [(1.0, ('form', 'servicio'), 'llega al formulario con lo marcado', 'R14')]
        if 'ley' in reglas and k == 'decide' and s[1] == 'ley':
            q = tt['contacta_' + u['etapa']]
            return [(1 - q, fin('abandono_sin_intento'), 'decide no escribir por ahora', None),
                    (q, ('form', 'servicio'), 'va al formulario de la guía', None)]
        if 'brief_silencio' in reglas and k == 'brief_envio' and u['js_brief_falla']:
            c = tt['nojs_correo_directo']
            return [(c, fin('correo_directo'), 'página con el correo: escribe desde su correo', 'R21'),
                    (1 - c, fin('abandono_por_friccion'), 'página con el correo: se va', 'R21')]
        if 'brief_silencio' in reglas and k == 'brief_envio' and u['agente']:
            # El apuro deja de ser silencioso: un aviso visible y el reintento llega.
            return [(p, fin('contacto'), 'aviso visible: espera y reintenta', 'R10') if d == (FIN, 'perdida_silenciosa')
                    else (p, d, e, r) for p, d, e, r in original(u, tt, s)]
        return original(u, tt, s)

    ramas = ramas_arregladas
    try:
        return poblacion(t, US)
    finally:
        ramas = original


# --------------------------------------------------------------------------
# Nombres sintéticos (no son personas reales)
# --------------------------------------------------------------------------
F = ['Camila', 'Javiera', 'Francisca', 'Constanza', 'Valentina', 'Daniela', 'Carolina', 'Paula', 'Marcela',
     'Lorena', 'Patricia', 'Claudia', 'Fernanda', 'Catalina', 'Rocío', 'Ximena', 'Gloria', 'Andrea', 'Pamela',
     'Macarena']
M = ['Matías', 'Sebastián', 'Diego', 'Felipe', 'Cristóbal', 'Nicolás', 'Rodrigo', 'Gonzalo', 'Patricio',
     'Mauricio', 'Jorge', 'Luis', 'Claudio', 'Andrés', 'Tomás', 'Ignacio', 'Marcelo', 'Héctor', 'Raúl', 'Esteban']
A = ['González', 'Muñoz', 'Rojas', 'Díaz', 'Pérez', 'Soto', 'Contreras', 'Silva', 'Martínez', 'Sepúlveda',
     'Morales', 'Rodríguez', 'López', 'Fuentes', 'Hernández', 'Torres', 'Araya', 'Flores', 'Espinoza',
     'Valenzuela', 'Castillo', 'Tapia', 'Reyes', 'Gutiérrez', 'Castro', 'Pizarro', 'Álvarez', 'Vásquez',
     'Sánchez', 'Fernández']
APOSTROFO = ["O'Ryan", "D'Alessandro", "O'Kuinghttons", "D'Amico", "O'Brien", "D'Angelo", "D'Etigny", "O'Neill"]
GUION_PUNTO = ['Jean-Baptiste', 'Marie-Claire', 'Ma. José', 'M. Ignacia', 'Ana-María', 'Jean-Pierre', 'Ma. Paz',
               'Marie-Ange', 'Ma. Fernanda']
EMPRESA = ['Ferretería Hnos. Soto', 'Pinturas & Más', 'Taller 2 Ruedas', 'Dulces Doña Rosa Ltda.',
           'Clínica Dental Sonrisa+']


def nombrar(usuarios, rng):
    usados = set()
    for x in usuarios:
        u = x['u']
        while True:
            nombre = rng.choice(F + M)
            apellido = rng.choice(A)
            if u['nombre_tipo'] == 'apostrofo':
                apellido = rng.choice(APOSTROFO)
            elif u['nombre_tipo'] == 'guion_punto':
                nombre = rng.choice(GUION_PUNTO)
            texto = rng.choice(EMPRESA) if u['nombre_tipo'] == 'empresa_signos' else f'{nombre} {apellido}'
            if texto not in usados:
                usados.add(texto)
                x['nombre'] = texto
                break


if __name__ == '__main__':
    main()
