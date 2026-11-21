#!/usr/bin/env bash
# Una corrida con un error a propósito: la distribución «canal» suma 0,9.
set -euo pipefail
mkdir -p corrida
cat > corrida/modelo.toml <<'TOML'
[modelo]
nombre = "prueba rota"

[[parametros]]
id = "escribe"
p50 = 0.4
p10 = 0.2
p90 = 0.6
fuente = "prior:elicitacion"

[[distribuciones]]
id = "canal"
valores = { google = 0.6, redes = 0.3 }
fuente = "prior:elicitacion"

[[variables]]
id = "canal"
valores = ["google", "redes"]
  [[variables.casos]]
  dist = "canal"

[[reglas]]
id = "R1"
texto = "El envío falla"
friccion = true
evidencia = [{ cita = "a.js:1", extracto = "uno" }]

[cadena]
inicio = "inicio"
[cadena.desenlaces]
contacto = "Contacto"
abandono = "Se va"

[[estados]]
id = "inicio"
  [[estados.ramas]]
  prob = "p.escribe"
  va = "FIN:contacto"
  accion = "escribe"
  [[estados.ramas]]
  prob = "1 - p.escribe"
  va = "FIN:abandono"
  accion = "se va"

[[metricas]]
id = "contacto_total"
expr = "contacto"

[[perfiles]]
id = "P1"
si = "True"
TOML
