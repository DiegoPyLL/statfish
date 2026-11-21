"""Apoyo de los tests: ruta del motor y modelos de juguete escritos en TOML."""
import os
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOTOR = os.path.join(RAIZ, 'plugins', 'statfish', 'motor')
EJEMPLO = os.path.join(RAIZ, 'ejemplos', 'volutus')
if MOTOR not in sys.path:
    sys.path.insert(0, MOTOR)

# Un modelo mínimo pero completo: dos variables, una regla de fricción, tres estados.
JUGUETE = '''
[modelo]
nombre = "juguete"

[corrida]
semilla = 7
poblacion = 2000
representativos = 4
sorteos_parametros = 20
usuarios_incertidumbre = 300
usuarios_hipotesis = 500

[[parametros]]
id = "movil"
p50 = 0.5
p10 = 0.3
p90 = 0.7
fuente = "prior:elicitacion"

[[parametros]]
id = "escribe"
p50 = 0.4
p10 = 0.2
p90 = 0.6
fuente = "prior:elicitacion"

[[parametros]]
id = "falla_movil"
p50 = 0.2
p10 = 0.1
p90 = 0.4
fuente = "prior:elicitacion"

[[parametros]]
id = "arreglo"
interruptor = true

[[distribuciones]]
id = "canal"
valores = { google = 0.6, redes = 0.4 }
kappa = 20
fuente = "prior:elicitacion"

[[variables]]
id = "canal"
valores = ["google", "redes"]
soporte = [{ cita = "a.js:1", extracto = "uno" }]
  [[variables.casos]]
  dist = "canal"

[[variables]]
id = "movil"
valores = [true, false]
soporte = [{ cita = "a.js:1", extracto = "uno" }]
  [[variables.casos]]
  prob = "p.movil"

[[reglas]]
id = "R1"
texto = "En celular el envío falla"
friccion = true
cw = ["sí", "sí", "sí", "no"]
nota_cw = "No ve por qué falla."
evidencia = [{ cita = "a.js:2", extracto = "dos" }]

[cadena]
inicio = "inicio"
atribuibles = ["abandono_por_friccion", "contacto_con_friccion"]
perdida = ["abandono_por_friccion"]
con_friccion = { contacto = "contacto_con_friccion" }

[cadena.desenlaces]
contacto = "Contacto"
contacto_con_friccion = "Contacto con fricción"
abandono = "Se va"
abandono_por_friccion = "Se va por fricción"

[[estados]]
id = "inicio"
nombre = "Llegada"
superficies = ["portada"]
  [[estados.ramas]]
  prob = "p.escribe"
  va = "envio"
  accion = "escribe por {canal}"
  arco = "escribe"
  [[estados.ramas]]
  prob = "1 - p.escribe"
  va = "FIN:abandono"
  accion = "se va"

[[estados]]
id = "envio"
nombre = "Envío"
superficies = ["formulario"]
locales = { f = "p.falla_movil if movil and not p.arreglo else 0.0" }
  [[estados.ramas]]
  prob = "1 - f"
  va = "FIN:contacto"
  accion = "envía"
  [[estados.ramas]]
  prob = "f * 0.5"
  va = "reintento"
  accion = "falla y reintenta"
  regla = "R1"
  [[estados.ramas]]
  prob = "f * 0.5"
  va = "FIN:abandono_por_friccion"
  accion = "falla y se va"
  regla = "R1"

[[estados]]
id = "reintento"
nombre = "Reintento"
  [[estados.ramas]]
  prob = "1.0"
  va = "FIN:contacto"
  accion = "reintenta y llega"

[[metricas]]
id = "contacto_total"
expr = "contacto + contacto_con_friccion"

[[metricas]]
id = "perdida"
expr = "abandono_por_friccion"

[[perfiles]]
id = "P1"
nombre = "Celular"
si = "movil"

[[perfiles]]
id = "P2"
nombre = "Escritorio"
si = "True"

[[factores]]
id = "canal"
expr = "canal"

[[factores]]
id = "movil"
expr = "movil"

[[superficies]]
id = "portada"

[[superficies]]
id = "formulario"

[cobertura]
candidatos_universo = 200
candidatos_por_vuelta = 50
universo_arcos = 100

[cobertura.aplanada.parametros]
movil = 0.5

[sensibilidad]
parametros = ["movil", "escribe", "falla_movil"]
metricas = ["contacto_total", "perdida"]
ordenar_por = "perdida"
trayectorias = 3
usuarios = 200

[[hipotesis]]
id = "arreglo"
texto = "Arreglar el envío en celular"
cambios = { arreglo = true }
'''


def escribir_corrida(toml=JUGUETE, extra=None):
    """Una carpeta de corrida temporal con modelo.toml (y otros archivos opcionales)."""
    d = tempfile.mkdtemp(prefix='statfish-test-')
    with open(os.path.join(d, 'modelo.toml'), 'w', encoding='utf-8') as f:
        f.write(toml)
    for nombre, texto in (extra or {}).items():
        ruta = os.path.join(d, nombre)
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, 'w', encoding='utf-8') as f:
            f.write(texto)
    return d
