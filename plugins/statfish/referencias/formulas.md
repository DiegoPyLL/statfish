# Fórmulas fijas

Cada fórmula está implementada una sola vez en el motor y tiene un test con valores conocidos en
`tests/test_formulas.py`. Si cambia una fórmula, cambian los bytes de las corridas: sube la versión del
motor.

| Id | Fórmula | Dónde |
|---|---|---|
| F1 | **Beta desde (p10, p50, p90).** σ = (p90 − p10)/2,563 y var = min(σ², 0,95·m(1−m)), con m = p50. Luego κ = m(1−m)/var − 1, α = máx(mκ; 0,05) y β = máx((1−m)κ; 0,05). Si var = 0, el parámetro queda fijo. | `incertidumbre.beta_desde` |
| F2 | **Dirichlet(κ·p).** κ según la fuente: ancla 200, prior 12 (de 10 a 15), definición o código 1.000. Un `kappa` declarado manda. | `modelo.theta_sorteado` |
| F3 | **Mezcla de K elicitaciones.** Cada una da una Beta por F1. p̄ es la media de las K. La varianza de la mezcla es media(var_k + m_k²) − p̄²: suma la de cada elicitación y la dispersión entre ellas. κ sale por momentos, con el tope de F1. p10 y p90 son los cuantiles de esa Beta. En las categóricas, κ = Σ p̄(1−p̄)/Σ var − 1. | `incertidumbre.combinar_*` |
| F4 | **Muestreo ancestral con números aleatorios comunes.** Hay un uniforme por variable aleatoria. Una booleana es `true` si u < p. Una categórica toma el primer valor cuya acumulada supera u. log p suma el log de cada valor elegido, o la suma de los crudos si hay `transformar`. | `red.generar_red` |
| F5 | **Peso de importancia.** w = exp(log p − log q): cuánta población representa un usuario de cobertura frente a lo que se infló para encontrarlo. | `cobertura.cubrir_pares` |
| F6 | **Cobertura por pares (AETG voraz).** El universo de pares se estima con N usuarios de la red aplanada q. En cada vuelta se sortean M candidatos de q y se elige el primero que cubre más pares nuevos. Termina cuando no quedan pares o ningún candidato suma. | `cobertura.cubrir_pares` |
| F7 | **Absorción exacta.** Suma por caminos con profundidad acotada. Si se pasa, por ciclos o caminos largos, se resuelve B = (I − Q)⁻¹R sobre estados aumentados con la última fricción. | `cadena.Cadena.evaluar` |
| F8 | **Atribución.** Cada desenlace atribuible se asigna a la última regla de fricción del camino. Si hubo fricción, el desenlace de `con_friccion` cambia: contacto pasa a contacto con fricción. | `cadena.Cadena._suma_por_caminos` |
| F9 | **Cuantiles de S sorteos.** Para q ≤ 0,5, el elemento ⌊q·S⌋ de los valores ordenados; para q > 0,5, el elemento S − 1 − ⌊(1−q)·S⌋. Es simétrico: con S = 200, p5, p50 y p95 son los elementos 10, 100 y 189. | `incertidumbre.cuantil` |
| F10 | **Morris.** r trayectorias y p niveles, con Δ = p/(2(p−1)). Cada parámetro vale p10 + x·(p90 − p10), con x ∈ [0, 1]. EE = ΔY/Δ, con su signo. μ* es la media de \|EE\| y σ la desviación estándar de EE. | `sensibilidad.morris` |
| F11 | **Robustez del orden.** La frecuencia con que cada regla queda 1.ª y entre las 3 primeras, por pérdida y por fricción total, a través de los S sorteos. | `incertidumbre.robustez` |
| F12 | **Fidelidad.** \|declarada − muestra\| ≤ 3·√(p(1−p)/n). Se revisa para cada valor de cada caso de la red, más las marginales declaradas. | `muestreo.fiel` |
| F13 | **Divergencia de Jensen-Shannon en base 2.** H(mezcla) − media de H, con pesos iguales, de 0 a log2(K). Se usa para la estabilidad entre elicitaciones y entre corridas, con umbral 0,05. | `incertidumbre.jsd` |
| F14 | **Calibración conjugada.** Beta(α + s, β + f) y Dirichlet(κ·p + n). El posterior de p50 es la media; p10 y p90 son los cuantiles de la Beta posterior. | `calibracion` |
| F15 | **Arco forzado.** Entre los usuarios con traza, el camino de máxima probabilidad que contiene el arco. Ante un empate gana el primero. | `cadena.Cadena.mejor_camino` |

## Semillas por etapa

Cada etapa tiene su propio generador, así que cambiar el tamaño de una no cambia los sorteos de las demás.

| Etapa | Semilla |
|---|---|
| Representativos | s |
| Población grande | s + 1 |
| Cobertura (universo y vueltas) | s + 2 |
| Nombres sintéticos | s + 3 |
| Usuarios de la incertidumbre y de Morris | s + 4 |
| Sorteos de parámetros | s + 5 |
| Morris (trayectorias) | s + 6 |
| Usuarios de las hipótesis | s + 7 |
| Traza del usuario i (1, 2, …) | 100·s + i |

## Beta: cuantiles

`beta_cdf` calcula la beta incompleta regularizada con la fracción continua de Lentz, y `beta_cuantil` la
invierte por bisección en 80 pasos. Ambas son deterministas y solo usan la biblioteca estándar.
