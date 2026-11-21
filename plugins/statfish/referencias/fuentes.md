# Fuentes: anclas y literatura

## Registro de anclas

Viven en `datos/anclas/<fuente>/<país>/<periodo>.toml`. Cada archivo agrupa las anclas de una fuente, un
país y un período:

```toml
fuente = "statcounter"
titulo_fuente = "StatCounter Global Stats"
pais = "CL"
pais_nombre = "chile"            # para la plantilla de URL
periodo = "2026-10"
consultado = 2026-11-20          # cuándo se leyó
vigencia_meses = 6               # cuánto dura antes de volver a consultarla
unidad = "%"

[[anclas]]
id = "statcounter-CL-plataforma-2026-10"
titulo = "Plataforma (escritorio, celular, tablet), Chile, oct-2026"
url = "https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet/chile"
plantilla_url = "https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet/{pais_nombre}"
valores = { escritorio = 50.05, movil = 49.12, tablet = 0.84 }   # tal como se publican
```

**Orden de resolución** de cada peso:

1. Un ancla vigente del registro para el país y el período: `statfish anclas --pais CL`.
2. Si falta o venció, el agente la consulta con su `plantilla_url`, guarda la copia en `anclas/` de la
   corrida con este mismo formato y propone sumarla al registro del plugin.
3. Si no hay fuente pública, un prior de K elicitaciones independientes, marcado como prior en el informe.

La corrida guarda una copia de cada ancla que usa (`statfish anclas --corrida <corrida> --copiar`), así que
se puede reproducir aunque el registro cambie. El motor nunca accede a la red: las consultas las hace el
agente y quedan guardadas.

### Anclas iniciales

Todas se consultaron para el caso Volutus el 2026-11-20:

| Id | Qué | Vigencia |
|---|---|---|
| `statcounter-CL-plataforma-2026-10` | Escritorio, celular y tablet en Chile | 6 meses |
| `statcounter-CL-sistema-movil-2026-10` | Android e iOS en Chile | 6 meses |
| `statcounter-CL-sistema-escritorio-2026-10` | Windows, macOS y Linux en Chile | 6 meses |
| `statcounter-CL-navegador-2026-10` | Navegadores en Chile, todas las plataformas | 6 meses |
| `sii-CL-empresas-tamano-2024` | Empresas con ventas por tamaño (SII) | 12 meses |
| `ine-CL-empresas-activas-2025` | Empresas activas (INE) | 12 meses |
| `webmcp-estado-2026-11` | Estado de WebMCP: origin trials y soporte | 2 meses |

## Literatura por técnica

- **Perfil operacional y cadena de uso.**
  - Musa, «Operational profiles in software-reliability engineering», IEEE Software, 1993.
  - [Whittaker y Thomason, 1994](https://www.site.uottawa.ca/~gvj/papers/Software%20Engineering%20IEEE%20Transactions%20on%201994%20Whittaker.pdf).
  - [Perfil operacional, ACM Computing Surveys](https://dl.acm.org/doi/abs/10.1145/2518106).
- **Distribuciones verbalizadas y mezcla de priors.**
  - [Meister et al., NAACL 2025](https://arxiv.org/abs/2411.05403).
  - [Evi-DA](https://arxiv.org/pdf/2603.13305).
  - [AutoElicit, ICML 2025](https://arxiv.org/abs/2411.17284).
  - [Wisdom of the silicon crowd](https://www.science.org/doi/10.1126/sciadv.adp1528).
  - Para respuestas tipo escala: [SSR, Maier et al. 2025](https://arxiv.org/abs/2510.08338).
- **Personas sintéticas, estructura antes que relato.**
  - [LLM Generated Persona is a Promise with a Catch, NeurIPS 2025](https://arxiv.org/abs/2503.16527).
  - [Revisión de 81 artículos](https://arxiv.org/abs/2504.04927).
  - [Verbalized Sampling](https://arxiv.org/abs/2510.01171).
- **Pruebas combinatorias.** Kuhn y Wallace (2004); [Kuhn, NIST](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=910001).
- **Sensibilidad.** Morris (1991); Saltelli; [JASSS 17(3):11](https://jasss.soc.surrey.ac.uk/17/3/11.html).
- **LLM como usuarios** (por qué no deciden acciones).
  - [ShopCART, Lu et al. 2025](https://arxiv.org/abs/2503.20749).
  - [UXAgent](https://arxiv.org/abs/2502.12561).
  - [Generative Agent Simulations of 1,000 People](https://arxiv.org/abs/2411.10109).
- **Recorrido cognitivo con LLM.**
  - [Synthetic Cognitive Walkthrough](https://arxiv.org/pdf/2512.03568).
  - [GenderMag con agentes](https://dl.acm.org/doi/full/10.1145/3801978).
- **Código y agentes.**
  - [LocAgent](https://arxiv.org/abs/2503.09089).
  - [RepoGraph](https://github.com/ozyyshr/RepoGraph).
  - [AutoE2E](https://arxiv.org/abs/2408.01894).
- **Comparación con enjambres.**
  - [MiroFish](https://github.com/666ghj/MiroFish).
  - [Prueba de WPP](https://cms.research.wpp.com/?research_feed=mirofish-is-swarm-intelligence-worth-the-cloud-bill).

La lista completa, con el contexto de cada una, está en `docs/viabilidad.md#fuentes` del repo.
