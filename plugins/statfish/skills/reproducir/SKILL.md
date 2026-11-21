---
name: reproducir
description: Recalcula una corrida de Statfish y comprueba que da los mismos bytes; verifica cada cita contra el commit actual del repo y marca los hallazgos con evidencia vencida como posible arreglo.
argument-hint: "<carpeta de la corrida>"
disable-model-invocation: true
---

# Reproducir una corrida

El motor es `statfish`, que está en el PATH con el plugin activo. Si no responde, usa
`python3 "${CLAUDE_SKILL_DIR}/../../bin/statfish"`.

1. Ubica la corrida: `$ARGUMENTS`, o la carpeta más reciente bajo `statfish/` del repo actual. Debe tener
   `manifiesto.json`. Sin manifiesto no hay qué reproducir: córrela con `statfish correr`.
2. Corre `statfish reproducir <corrida>`. El comando:
   - compara el hash de cada entrada con el del manifiesto y lista las que cambiaron;
   - recalcula en una copia temporal, con la misma semilla y la evidencia guardada, y compara byte a byte
     las salidas;
   - verifica cada cita contra el commit actual: `vigente`, `desplazada` (con la cita nueva) o `vencida`;
   - escribe `salida/reproduccion.json`.
3. Informa en este orden:
   - **Reproducible o no.** Si una salida difiere y las entradas no cambiaron, compara las versiones del motor
     y de Python del manifiesto. Una diferencia sin explicación es un error del motor: repórtalo.
   - **Entradas que cambiaron.** Si cambió `modelo.toml` u otra entrada, las salidas viejas ya no
     corresponden: ofrece `statfish correr`.
   - **Evidencia.** Las desplazadas se corrigen con la cita nueva que sugiere el comando. Las vencidas indican
     que el código cambió.
   - **Hallazgos con evidencia vencida:** «posible arreglo, verificar». Lee el código actual en esa zona y di
     si la fricción sigue, cambió o se resolvió. Si se resolvió, propón cambiar su `estado` a `resuelto` en
     `hallazgos.toml` y volver a correr. No cambies el estado sin confirmación.
4. No edites código del repo ni cierres issues.
