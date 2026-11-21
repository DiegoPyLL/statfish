"""F1 a F15 con valores conocidos (referencias/formulas.md)."""
import math
import random
import unittest

import apoyo  # noqa: F401
from statfish import cadena as C
from statfish import calibracion as CAL
from statfish import cobertura as CO
from statfish import incertidumbre as I
from statfish import modelo as M
from statfish import muestreo as MU
from statfish import red as R
from statfish import sensibilidad as S


def _modelo(toml=apoyo.JUGUETE):
    d = apoyo.escribir_corrida(toml)
    return M.Corrida(d).modelo()


class F1Beta(unittest.TestCase):
    def test_simetrica(self):
        # σ = 0,4/2,563; κ = 0,25/σ² − 1 = 9,264; α = β = 4,632
        a, b = I.beta_desde(0.5, 0.3, 0.7)
        self.assertAlmostEqual(a, 4.632, places=3)
        self.assertAlmostEqual(b, 4.632, places=3)

    def test_media_es_p50(self):
        a, b = I.beta_desde(0.05, 0.02, 0.10)
        self.assertAlmostEqual(a / (a + b), 0.05, places=12)

    def test_tope_y_minimo(self):
        # var se topa en 0,95·m(1−m) y α no baja de 0,05.
        a, b = I.beta_desde(0.05, 0.0, 1.0)
        self.assertEqual(a, 0.05)
        self.assertAlmostEqual(b, 0.95 * (0.0475 / 0.045125 - 1), places=9)

    def test_sin_rango(self):
        self.assertIsNone(I.beta_desde(0.5, 0.5, 0.5))


class F2Dirichlet(unittest.TestCase):
    def test_kappa_por_fuente(self):
        self.assertEqual(I.kappa_por_fuente('ancla'), 200)
        self.assertEqual(I.kappa_por_fuente('prior'), 12)
        self.assertEqual(I.kappa_por_fuente('definicion'), 1000)

    def test_sorteo_concentrado(self):
        m = _modelo(apoyo.JUGUETE.replace('kappa = 20', 'kappa = 1000000'))
        th = M.theta_sorteado(m, random.Random(1))
        self.assertAlmostEqual(th.D['canal']['google'], 0.6, places=2)
        self.assertAlmostEqual(sum(th.D['canal'].values()), 1.0, places=12)


class F3Mezcla(unittest.TestCase):
    def test_iguales(self):
        r = I.combinar_binarias([(0.1, 0.2, 0.3)] * 3)
        self.assertAlmostEqual(r['p50'], 0.2, places=12)
        self.assertAlmostEqual(r['jsd'], 0.0, places=12)

    def test_dos_distintas(self):
        # var = media(v_k + m_k²) − m² = 0,0060892 + 0,1 − 0,09; κ = 0,21/var − 1 ≈ 12,05
        r = I.combinar_binarias([(0.1, 0.2, 0.3), (0.3, 0.4, 0.5)])
        self.assertAlmostEqual(r['p50'], 0.3, places=12)
        self.assertAlmostEqual(r['kappa'], 0.21 / (0.0060892 + 0.01) - 1, places=2)
        self.assertAlmostEqual(r['jsd'], 0.034852, places=5)
        self.assertLess(r['p10'], 0.3)
        self.assertGreater(r['p90'], 0.3)

    def test_categoricas(self):
        r = I.combinar_categoricas([({'a': 0.5, 'b': 0.5}, 20), ({'a': 0.7, 'b': 0.3}, 20)])
        self.assertAlmostEqual(r['valores']['a'], 0.6, places=12)
        self.assertGreater(r['jsd'], 0)


class F4Muestreo(unittest.TestCase):
    def test_numeros_comunes(self):
        m = _modelo()
        red = R.Red(m)
        t = M.theta_p50(m)
        U = [0.9, 0.7]
        u1, _ = red.muestrear(U, t)
        u2, _ = red.muestrear(U, t.con({'movil': 0.95}))
        self.assertEqual(u1['canal'], u2['canal'])     # cambiar un peso no reordena a los demás
        self.assertNotEqual(u1['movil'], u2['movil'])  # x = 0,7: no es < 0,5, pero sí < 0,95

    def test_logp(self):
        m = _modelo()
        red = R.Red(m)
        t = M.theta_p50(m)
        u, lp = red.muestrear([0.1, 0.9], t)  # google (0,6), movil = False (1 − 0,5)
        self.assertEqual((u['canal'], u['movil']), ('google', False))
        self.assertAlmostEqual(lp, math.log(0.6) + math.log(0.5), places=12)
        self.assertAlmostEqual(red.logp(u, t), lp, places=12)


class F5Peso(unittest.TestCase):
    def test_peso_p_sobre_q(self):
        m = _modelo()
        red = R.Red(m)
        p, q = M.theta_p50(m), M.theta_p50(m).con({'movil': 0.9})
        u, lq = red.muestrear([0.1, 0.5], q)  # movil = True con q
        w = math.exp(red.logp(u, p) - lq)
        self.assertAlmostEqual(w, (0.6 * 0.5) / (0.6 * 0.9), places=12)


class F6Pares(unittest.TestCase):
    def test_cubre_todos(self):
        m = _modelo()
        red = R.Red(m)
        t = M.theta_p50(m)
        universo, cubiertos, _, nuevos = CO.cubrir_pares(red, t, M.theta_aplanado(m), random.Random(3), [], 200, 50)
        self.assertEqual(len(universo), 4)  # canal × movil: 2 × 2 pares
        self.assertTrue(universo <= cubiertos)
        self.assertTrue(all(x['peso'] > 0 for x in nuevos))


CICLO = apoyo.JUGUETE.replace('''[[estados]]
id = "reintento"
nombre = "Reintento"
  [[estados.ramas]]
  prob = "1.0"
  va = "FIN:contacto"
  accion = "reintenta y llega"''', '''[[estados]]
id = "reintento"
nombre = "Reintento"
  [[estados.ramas]]
  prob = "0.5"
  va = "envio"
  accion = "vuelve a enviar"
  [[estados.ramas]]
  prob = "0.5"
  va = "FIN:abandono"
  accion = "lo deja"''')


class F7Absorcion(unittest.TestCase):
    def test_ciclo_exacto(self):
        # envio → reintento → envio … : P(contacto | escribe) = (1 − f) / (1 − f/4), con f = 0,2.
        m = _modelo(CICLO)
        cad = C.Cadena(m)
        u = {'canal': 'google', 'movil': True}
        acum, _ = cad.evaluar(u, M.theta_p50(m))
        f = 0.2
        p_contacto = 0.4 * (1 - f) / (1 - f / 4)
        self.assertAlmostEqual(acum['contacto_con_friccion'] + acum.get('contacto', 0), p_contacto, places=12)
        self.assertAlmostEqual(sum(acum.values()), 1.0, places=12)

    def test_caminos_igual_lineal(self):
        m = M.Corrida(apoyo.EJEMPLO).modelo()
        red, cad, t = R.Red(m), C.Cadena(m), M.theta_p50(m)
        for U in red.uniformes(random.Random(5), 200):
            u, _ = red.muestrear(U, t)
            a1, r1 = cad._suma_por_caminos(u, t)
            a2, r2 = cad._absorcion_lineal(u, t)
            for d in set(a1) | set(a2):
                self.assertAlmostEqual(a1.get(d, 0), a2.get(d, 0), places=12)
            for k in set(r1) | set(r2):
                self.assertAlmostEqual(r1.get(k, 0), r2.get(k, 0), places=12)


class F8Atribucion(unittest.TestCase):
    def test_ultima_friccion(self):
        m = _modelo()
        cad = C.Cadena(m)
        acum, pr = cad.evaluar({'canal': 'google', 'movil': True}, M.theta_p50(m))
        # Contacto tras reintentar: 0,4 · 0,2 · 0,5 = 0,04, con fricción y atribuido a R1.
        self.assertAlmostEqual(acum['contacto_con_friccion'], 0.04, places=12)
        self.assertAlmostEqual(pr[('R1', 'contacto_con_friccion')], 0.04, places=12)
        self.assertAlmostEqual(pr[('R1', 'abandono_por_friccion')], 0.04, places=12)


class F9Cuantiles(unittest.TestCase):
    def test_indices(self):
        xs = list(range(200))
        self.assertEqual(I.intervalo(xs), {'p5': 10, 'p50': 100, 'p95': 189})
        self.assertEqual(I.intervalo(list(range(20))), {'p5': 1, 'p50': 10, 'p95': 18})


class F10Morris(unittest.TestCase):
    def test_lineal(self):
        m = _modelo()
        for k in ('movil', 'escribe'):
            m.param[k].p10, m.param[k].p90 = 0.0, 1.0
        evaluar = lambda th: {'y': 2 * th.P['movil'] + 3 * th.P['escribe']}
        filas = S.morris(evaluar, m, ['movil', 'escribe'], ['y'], 5, 4, random.Random(2), M.theta_p50(m))
        mu = {f['parametro']: f['y']['mu_estrella'] for f in filas}
        self.assertAlmostEqual(mu['movil'], 2.0, places=9)
        self.assertAlmostEqual(mu['escribe'], 3.0, places=9)
        self.assertAlmostEqual(filas[0]['y']['sigma'], 0.0, places=9)


class F11Robustez(unittest.TestCase):
    def test_frecuencias(self):
        r = I.robustez([{'A': 3, 'B': 2, 'C': 1, 'D': 0}, {'B': 3, 'A': 2, 'C': 1, 'D': 0},
                        {'A': 3, 'D': 2, 'B': 1, 'C': 0}, {'A': 3, 'B': 2, 'C': 1, 'D': 0}])
        self.assertEqual(r['top1'], {'A': 0.75, 'B': 0.25})
        self.assertEqual(r['top3'], {'A': 1.0, 'B': 1.0, 'C': 0.75, 'D': 0.25})


class F12Fidelidad(unittest.TestCase):
    def test_tres_sigma(self):
        self.assertTrue(MU.fiel(0.5, 0.51, 10_000))   # 3σ = 0,015
        self.assertFalse(MU.fiel(0.5, 0.52, 10_000))


class F13JensenShannon(unittest.TestCase):
    def test_extremos(self):
        self.assertAlmostEqual(I.jsd([[1, 0], [0, 1]]), 1.0, places=12)
        self.assertAlmostEqual(I.jsd([[0.5, 0.5], [0.5, 0.5]]), 0.0, places=12)


class F14Calibracion(unittest.TestCase):
    def test_beta(self):
        r = CAL.calibrar_binario(0.5, 0.3, 0.7, 10, 0)
        a, b = r['posterior']['alfa'], r['posterior']['beta']
        self.assertAlmostEqual(a, 4.632 + 10, places=3)
        self.assertAlmostEqual(r['posterior']['p50'], a / (a + b), places=12)

    def test_dirichlet(self):
        r = CAL.calibrar_categorica([('a', 0.5), ('b', 0.5)], 10, {'a': 10})
        self.assertAlmostEqual(r['posterior']['valores']['a'], 0.75, places=12)
        self.assertEqual(r['posterior']['kappa'], 20)


class F15ArcoForzado(unittest.TestCase):
    def test_camino_mas_probable(self):
        m = _modelo()
        cad = C.Cadena(m)
        u = {'canal': 'google', 'movil': True}
        idx, p = cad.mejor_camino(u, M.theta_p50(m), ('reintento', 'reintenta y llega'))
        self.assertAlmostEqual(p, 0.4 * 0.2 * 0.5, places=12)
        pasos, d, _ = cad.trazar(u, M.theta_p50(m), None, forzar=idx)
        self.assertEqual(d, 'contacto_con_friccion')
        self.assertEqual([x['arco'][0] for x in pasos], ['inicio', 'envio', 'reintento'])


class BetaCuantil(unittest.TestCase):
    def test_uniforme_y_simetrica(self):
        self.assertAlmostEqual(I.beta_cdf(0.3, 1, 1), 0.3, places=12)
        self.assertAlmostEqual(I.beta_cuantil(0.9, 1, 1), 0.9, places=9)
        self.assertAlmostEqual(I.beta_cuantil(0.5, 2, 2), 0.5, places=9)
        # Beta(2, 1): F(x) = x² → cuantil 0,25 = 0,5
        self.assertAlmostEqual(I.beta_cuantil(0.25, 2, 1), 0.5, places=9)


if __name__ == '__main__':
    unittest.main()
