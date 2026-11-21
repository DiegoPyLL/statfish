"""Expresiones, validación del modelo, evidencia, determinismo y el ejemplo Volutus."""
import json
import os
import random
import shutil
import subprocess
import tempfile
import unittest

import apoyo
from statfish import cadena as C
from statfish import cli
from statfish import corrida as CR
from statfish import evidencia as EV
from statfish import expresiones as ex
from statfish import modelo as M
from statfish import muestreo as MU
from statfish import red as R

LENTO = os.environ.get('STATFISH_LENTO') == '1'


class Expresiones(unittest.TestCase):
    def test_permitidas(self):
        f = ex.compilar("min(p.a * (5 if nav == 'firefox' else 1), 0.9)")
        self.assertEqual(f({'nav': 'firefox'}, {'a': 0.03}, {}, {}), 0.15)
        f = ex.compilar("x in ('a', 'b') and not y or d.dist.v > 0.5", locales=['x'])
        self.assertTrue(f({'y': True}, {}, {'dist': {'v': 0.7}}, {'x': 'a'}))

    def test_rechazadas(self):
        for malo in ('__import__("os")', 'u.__class__', 'open("x")', 'x[0]', 'lambda: 1', 'p',
                     '[x for x in y]', 'a ** 2', 'd.x', '_privado', 'f"{x}"', 'a if b', 'min(x)'):
            with self.assertRaises(ex.ErrorExpresion, msg=malo):
                ex.analizar(malo)

    def test_plantilla(self):
        codigo = ex.plantilla_a_python("llega a {ruta} {{literal}}")
        f = eval(f'lambda u: {codigo}', {'__builtins__': {}, '_s': str})
        self.assertEqual(f({'ruta': '/'}), 'llega a / {literal}')


class Validacion(unittest.TestCase):
    def _errores(self, toml):
        d = apoyo.escribir_corrida(toml)
        try:
            M.Corrida(d).modelo()
        except M.ErrorModelo as e:
            return e.errores
        return []

    def test_juguete_valido(self):
        self.assertEqual(self._errores(apoyo.JUGUETE), [])

    def test_suma_distinta_de_uno(self):
        e = self._errores(apoyo.JUGUETE.replace('google = 0.6, redes = 0.4', 'google = 0.6, redes = 0.3'))
        self.assertTrue(any('suman' in x for x in e), e)

    def test_regla_sin_evidencia(self):
        e = self._errores(apoyo.JUGUETE.replace('evidencia = [{ cita = "a.js:2", extracto = "dos" }]', ''))
        self.assertTrue(any('sin cita no entra al modelo' in x for x in e), e)

    def test_nombre_desconocido(self):
        e = self._errores(apoyo.JUGUETE.replace('prob = "p.escribe"', 'prob = "p.escribe * pais"'))
        self.assertTrue(any('«pais»' in x for x in e), e)

    def test_estado_desconocido(self):
        e = self._errores(apoyo.JUGUETE.replace('va = "envio"', 'va = "envoi"'))
        self.assertTrue(any('envoi' in x for x in e), e)

    def test_relato_no_cambia_el_flujo(self):
        toml = apoyo.JUGUETE.replace('''[[variables]]
id = "movil"''', '''[[variables]]
id = "edad"
relato = true
valores = ["joven", "mayor"]
  [[variables.casos]]
  dist = { joven = "0.5", mayor = "0.5" }

[[variables]]
id = "movil"''').replace('prob = "p.escribe"', 'prob = "p.escribe if edad == \'joven\' else 0.1"')
        e = self._errores(toml)
        self.assertTrue(any('relato' in x for x in e), e)

    def test_dinamica(self):
        d = apoyo.escribir_corrida(apoyo.JUGUETE.replace('prob = "f * 0.5"\n  va = "reintento"', 'prob = "f * 0.6"\n  va = "reintento"'))
        corrida = M.Corrida(d)
        errores, _ = cli.validar(corrida, corrida.modelo(), n=200, sorteos=1)
        self.assertTrue(any('suman' in x for x in errores), errores)


class Evidencia(unittest.TestCase):
    def test_estados(self):
        repo = tempfile.mkdtemp(prefix='statfish-repo-')
        with open(os.path.join(repo, 'a.js'), 'w') as f:
            f.write('const nueva = 0\nconst uno = 1\nconst dos = 2\n')
        recorrido = '''
[[citas]]
id = "vigente"
evidencia = [{ cita = "a.js:2", extracto = "const uno = 1" }]
[[citas]]
id = "desplazada"
evidencia = [{ cita = "a.js:1", extracto = "const dos = 2" }]
[[citas]]
id = "vencida"
evidencia = [{ cita = "a.js:3", extracto = "const tres = 3" }]
[[citas]]
id = "sin_extracto"
evidencia = [{ cita = "a.js:3", extracto = "" }]
[[citas]]
id = "sin_archivo"
evidencia = [{ cita = "b.js:1", extracto = "x" }]
'''
        d = apoyo.escribir_corrida(extra={'recorrido.toml': recorrido})
        ev = EV.verificar(M.Corrida(d), repo=repo)
        estados = {c['origen'].split('[')[1].split(']')[0]: c for c in ev['citas'] if c['origen'].startswith('recorrido')}
        self.assertEqual(estados['vigente']['estado'], 'vigente')
        self.assertEqual(estados['desplazada']['estado'], 'desplazada')
        self.assertEqual(estados['desplazada']['nueva_cita'], 'a.js:3')
        self.assertEqual(estados['vencida']['estado'], 'vencida')
        self.assertEqual(estados['sin_extracto']['estado'], 'sin_extracto')
        self.assertEqual(estados['sin_extracto']['sugerido'], 'const dos = 2')
        self.assertEqual(estados['sin_archivo']['estado'], 'vencida')


class Determinismo(unittest.TestCase):
    def test_mismos_bytes(self):
        m = M.Corrida(apoyo.escribir_corrida()).modelo()
        a = CR.calcular(m)
        b = CR.calcular(m)
        for k in ('usuarios', 'trazas', 'resultados'):
            self.assertEqual(M.json_estable(a[k]), M.json_estable(b[k]))
        c = CR.calcular(m, semilla=8)
        self.assertNotEqual(M.json_estable(a['usuarios']), M.json_estable(c['usuarios']))

    def test_reproducir_cli(self):
        d = apoyo.escribir_corrida()
        self.assertEqual(cli.main(['correr', d]), 0)
        self.assertEqual(cli.main(['reproducir', d]), 0)
        rep = M.leer_json(os.path.join(d, 'salida', 'reproduccion.json'))
        self.assertTrue(all(v == 'idéntico' for v in rep['salidas'].values()))
        # Si el modelo cambia, reproducir lo dice y las salidas ya no son las mismas.
        with open(os.path.join(d, 'modelo.toml'), 'a', encoding='utf-8') as f:
            f.write('\n')
        self.assertEqual(cli.main(['reproducir', d]), 0)
        rep = M.leer_json(os.path.join(d, 'salida', 'reproduccion.json'))
        self.assertIn('modelo.toml', rep['entradas_cambiadas'])


class Marcadores(unittest.TestCase):
    def test_resolver(self):
        from statfish import informe as INF
        esp = {'metricas': {'p': 0.0127}, 'reglas': {'R1+R2': {'perdida': 0.00004}}, 'n': 200, 'lista': [{'x': 'a'}]}
        texto, err = INF.resolver('{{metricas.p|pct}} · {{reglas.R1+R2.perdida|mil}} · {{n}} · '
                                  '{{ metricas.p * 2 |pp}} · {{lista.0.x|texto}} · {{nada.x}}', esp)
        self.assertEqual(texto, '1,3 % · 0,04 · 200 · 2,54 · a · {{nada.x}}')
        self.assertEqual(len(err), 1)

    def test_cifras_a_mano(self):
        from statfish import informe as INF
        avisos = INF.cifras_a_mano('El 23,6 % contacta.\nLey 21.719 y R1.\n{{metricas.p|pct}} bien.\n')
        self.assertEqual(len(avisos), 1)
        self.assertIn('23,6 %', avisos[0])


class Volutus(unittest.TestCase):
    """El ejemplo reproduce exacto el script del caso (fase 2 del plan)."""

    @classmethod
    def setUpClass(cls):
        cls.m = M.Corrida(apoyo.EJEMPLO).modelo()
        cls.ref = os.path.join(apoyo.EJEMPLO, 'referencia', 'salida')

    def test_poblacion_exacta(self):
        m = self.m
        red, cad, t50 = R.Red(m), C.Cadena(m), M.theta_p50(m)
        US = red.uniformes(random.Random(m.corrida['semilla'] + CR.SEMILLA_POBLACION), m.corrida['poblacion'])
        pob = MU.poblacion(red, cad, m, t50, US)
        met = MU.metricas(MU.compilar_metricas(m), pob['desenlaces'])
        self.assertEqual(met['contacto_total'], 0.2355817451354591)
        self.assertEqual(met['perdida_por_codigo'], 0.01271781635688427)
        ref = M.leer_json(os.path.join(self.ref, 'agregados.json'))
        self.assertEqual(pob['desenlaces'], ref['desenlaces_p50'])
        self.assertEqual(pob['masa'], ref['masa'])

    def test_salidas_guardadas(self):
        res = M.leer_json(os.path.join(apoyo.EJEMPLO, 'salida', 'resultados.json'))
        cob = res['cobertura']
        self.assertEqual((cob['pares']['cubiertos'], cob['pares']['universo']), (514, 514))
        self.assertEqual((cob['arcos']['cubiertos_total'], cob['arcos']['universo']), (61, 61))
        self.assertEqual(res['metricas']['contacto_total'], 0.2355817451354591)
        ref_u = M.leer_json(os.path.join(self.ref, 'usuarios.json'))
        us = M.leer_json(os.path.join(apoyo.EJEMPLO, 'salida', 'usuarios.json'))
        self.assertEqual([x['nombre'] for x in us], [x['nombre'] for x in ref_u])
        self.assertEqual([x['peso'] for x in us], [x['peso'] for x in ref_u])

    @unittest.skipUnless(LENTO, 'corrida completa (unos 45 s): STATFISH_LENTO=1')
    def test_corrida_completa_igual_al_script(self):
        out = CR.calcular(self.m)
        r = out['resultados']
        ref = M.leer_json(os.path.join(self.ref, 'agregados.json'))
        self.assertEqual(r['intervalos'], ref['intervalos'])
        self.assertEqual({f['parametro']: f['perdida_por_codigo'] for f in r['morris']},
                         {f['parametro']: f['perdida_por_codigo'] for f in ref['morris']})
        tr = M.leer_json(os.path.join(self.ref, 'trazas.json'))
        for x, y in zip(out['trazas'], tr):
            self.assertEqual([p['accion'] for p in x['pasos']], [p['accion'] for p in y['pasos']])
            self.assertEqual(x['prob_camino'], y['prob_camino'])


class Patrones(unittest.TestCase):
    def test_siete_en_volutus(self):
        from statfish import contexto as CTX
        ctx = M.Corrida(apoyo.EJEMPLO).contexto()
        aplican, _ = CTX.patrones_aplicables(ctx, CTX.leer_patrones())
        self.assertEqual(sorted(p['id'] for p in aplican if p.get('tipo') != 'descartada'), [
            'P-ANTIBOT-SILENCIO-SIN-JS', 'P-ESTADO-PERDIDO-ENTRE-PAGINAS', 'P-MISMO-TEXTO-DOS-DESTINOS',
            'P-NOMBRE-SOLO-LETRAS', 'P-RESPUESTA-SIN-JS-SIN-ENLACE', 'P-TURNSTILE-SIN-ESPERA',
            'P-WEBMCP-SIN-ORIGIN-TRIAL'])


if __name__ == '__main__':
    unittest.main()
