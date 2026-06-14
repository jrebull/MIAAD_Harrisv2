# Anexo visual explorado y DECLINADO — bitácora

**Fecha:** 2026-06-13
**Decisión:** NO se integra al envío. La submission oficial queda en
`main_compacta_submission.pdf` / `submission_anonymous_compacta.zip`,
**17pp, sin anexos**, tag `micai-submission-v2 @ 9b9527d`, intacta.

## Qué se construyó (queda como material de defensa/charla/póster)

- `fig_anexo_main.pdf` — figura "hero": (a) frente 3D con FIFO flotando dominado
  (restaura el `pareto3d` que se perdió al compactar de 34→20→17pp);
  (b) antes→después por objetivo (desperdicio −100%, disparidad −85%, f₁ ≈tied).
  **Vive en espacio de objetivos → robusta y verificada.**
- `fig_anexo_footprint.pdf` / `fig_anexo_dominance.pdf` — figura por país. **INVÁLIDA**
  (ver hallazgo abajo). NO usar.
- `preview_anexo.tex/.pdf` — cómo se vería el Appendix A en LNCS (3pp).
- Scripts: `repro_country_1to30.py` (reproduce per-país desde seeds 1-30),
  `audit_blind.py` (re-derivación con valores esperados — sesgada),
  `audit_independent.py` (re-derivación ciega + prueba de unicidad).
- `country_impact_1to30.csv`, `country_impact_equity_1to30.csv` — datos reproducidos.

## Por qué se declinó

1. **HALLAZGO DEL BLIND AUDIT (lo decisivo):** la asignación **por país** de la
   política min-f₁ **NO es única**. 20 posiciones del archivo alcanzan el objetivo
   exacto (8.7884, 13.0, 680) y decodifican a **16 patrones por-país distintos**.
   El patrón que mostraba la figura `(Afganistán −1,200; Corea +2,460)` era 1 de 20;
   el más común (4/20) movía un solo país; otros mueven 6 países con saltos de
   ±10,000 (p. ej. México −10,000, Pakistán +7,000). La narrativa "huella mínima,
   solo 2 de 21 países cambian" era un **artefacto de `argmin`**, no una propiedad.
   El espacio de asignación es masivamente degenerado (f₂ = máximo ⇒ muchas
   asignaciones dan el mismo (f₁,f₂,f₃)). → **Cualquier figura por país es "una de
   muchas", no defendible.**
2. **Posicionamiento:** la contribución del paper es **metodológica** (diagnóstico
   de dos condiciones). El riesgo #1 de rechazo es "esto es ingeniería/aplicación".
   Un anexo que celebra el resultado de visas empuja la percepción hacia ese riesgo.
3. **Costo/riesgo:** +1–2 páginas sobre presupuesto exacto; reabrir una submission
   con dos blind audits limpios (reabrir introdujo 3 errores que el audit cazó:
   overclaim "higher-priority demand" —pesos de espera idénticos SK/Afg—, óptica de
   nombrar Afganistán −92%, y "dominates in all three" con f₂ empatado).

## Verificación que SÍ quedó sólida (por si se retoma la Fig.1 sola algún día)

Espacio de objetivos, todo re-derivado independientemente y determinista:
FIFO (8.7891, 13.0, 1940), frente 104 sol, min-f₁ (8.7884,13,680),
min-f₂ (8.9994,2,0), 94/104 cero-desperdicio, equidad 13→2 cuesta +2.4% en f₁.
El **paper principal NO depende del per-país** (ya lo había soltado; solo afirma en
espacio de objetivos), así que este hallazgo NO afecta la submission v2.
