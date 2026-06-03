# Memoria de cierre MICAI 2026

Fecha de cierre: 2026-06-02

## Objetivo

Auditar y reforzar el paper MICAI para reducir riesgos de rechazo por sobreventa, baja reproducibilidad, flancos legales/politicos y narrativa algorítmica confusa.

## Estado editorial final

Titulo aplicado en las 4 versiones `.tex`:

`When Blind Sampling Beats Tuned NSGA-II: A Two-Condition Diagnostic with a Calibrated Visa Allocation Case Study`

Running title:

`Two-Condition Diagnostic for Decoder-Based Search`

Decision editorial clave:

- La contribucion principal queda como diagnostico metodologico de dos condiciones para busqueda multiobjetivo con decoder.
- El caso de visas queda como calibrated case study, no como estudio politico/legal completo.
- Discrete-MOHHO queda presentado como mecanismo de validacion swarm, no como campeon global.
- permutation-NSGA-II queda reconocido como marginalmente el metodo mas fuerte/estable overall.

## Cambios principales realizados

- Se corrigio el tono de claims politicos: decision-support artifact, not a policy prescription.
- Se matizo el caso de visas como parcialmente sintetico/calibrado.
- Se explico el uso de `P_c=25,620` como cap cross-preference usado exogenamente en el modelo EB de un periodo.
- Se agrego auditoria de equidad alternativa:
  - wait std: FIFO `3.14` -> front `0.75`
  - Gini: FIFO `0.79` -> front `0.17`
  - Jain inverse waits: FIFO `0.80` -> front `0.94`
- Se implemento/verifico baseline suplementario `perm-SPEA2`.
- Se agrego verificador rapido reproducible `backend/repro/reproduce_fast.py`.
- Se actualizaron README, logs, resultados JSON y ZIPs de entrega.
- Se dividio la conclusion para mejorar legibilidad.
- Se suavizo el titulo para evitar lectura clickbait.

## Archivos importantes

- Paper anonimo largo: `MICAI/main_submission.tex`
- Paper anonimo reducido recomendado: `MICAI/main_reducida_submission.tex`
- Version Overleaf/camera-ready larga: `MICAI/main.tex`
- Version Overleaf/camera-ready reducida: `MICAI/main_reducida.tex`
- Log completo de mejoras: `MICAI/LOG_MEJORAS_MICAI_2026.md`
- Verificador rapido: `backend/repro/reproduce_fast.py`
- Resultado del verificador: `backend/app/data/results/reproduce_fast.json`
- Auditoria de equidad: `backend/repro/equity_audit.py`
- Resultado auditoria: `backend/app/data/results/equity_audit.json`
- SPEA2 suplementario: `backend/perm_spea2.py`
- Resultado SPEA2: `backend/app/data/results/perm_spea2.json`

## Entregables actualizados

- `MICAI/VisaPredictAI_MICAI_anonymous.zip`
- `MICAI/VisaPredictAI_MICAI_reducida_anonymous.zip`
- `MICAI/VisaPredictAI_MICAI_Overleaf.zip`
- `MICAI/VisaPredictAI_MICAI_reducida.zip`
- `MICAI/main_submission.pdf`
- `MICAI/main_reducida_submission.pdf`
- `MICAI/main.pdf`
- `MICAI/main_reducida.pdf`
- `MICAI/Feasibility-Preserving_MOHHO_MICAI*.pdf`

## Validacion final conocida

Ultimo `backend/repro/reproduce_fast.py`:

```json
{
  "overall_ok": true,
  "pytest": 0,
  "firewall": 0,
  "pages": {
    "main_submission.pdf": 28,
    "main_reducida_submission.pdf": 18
  },
  "anonymous_zip_hits": 0
}
```

PDFs:

- `main_submission.pdf`: 28 paginas, A4
- `main.pdf`: 28 paginas, A4
- `main_reducida_submission.pdf`: 18 paginas, A4
- `main_reducida.pdf`: 18 paginas, A4

Barrido de logs:

- Sin `Undefined`
- Sin citas indefinidas
- Sin referencias indefinidas
- Sin `Overfull`
- Sin residuos textuales accidentales tipo `SCALAR` o `ARGVOUT`

## Recomendacion de envio

Usar `MICAI/main_reducida_submission.pdf` y `MICAI/VisaPredictAI_MICAI_reducida_anonymous.zip` si MICAI mantiene limite practico cercano a 20 paginas. La version larga sirve como respaldo/suplemento o para un venue con mas holgura.

## Riesgos residuales

- La version larga sigue demasiado extensa para una conferencia si el limite es estricto.
- La reproducibilidad es fuerte localmente, pero idealmente conviene alojar un ZIP anonimo en OSF/Zenodo/GitHub anonimo si el proceso de MICAI lo permite.
- El caso de visas sigue siendo el flanco mas sensible; sostener siempre que es calibrated case study y no policy prescription.

## Comando de sanity check para retomar

Desde `/Users/haowei/Documents/MIAAD/SMART/Harris2`:

```bash
backend/.venv/bin/python backend/repro/reproduce_fast.py
```


## Actualizacion final (HEAD d537f85, 2026-06-02)

Esta seccion supersede los conteos de pagina y el titulo de arriba.

Titulo final: `When Blind Sampling Beats Tuned NSGA-II: A Two-Condition Diagnostic with a Calibrated Visa Allocation Case Study` (gancho + tesis + caso). Saltos con `\texorpdfstring{\\}{ }` para no disparar el warning de hyperref.

Invariante de paginas actualizado: **28 / 27 / 18 / 18** (main / main_submission / main_reducida / main_reducida_submission), A4. El envio sigue siendo `main_reducida_submission.pdf` (18 pp).

Trabajo posterior al cierre original:
- Autores camera-ready con ORCID en `main`/`main_reducida` (Rebull 0009-0008-2089-5274, Flores Martinez 0009-0002-6848-1608 SIN acentos, Porras Alaniz 0000-0002-6772-5351). Las versiones de envio mantienen "Anonymous Author(s)".
- Repo de reproducibilidad privado `jrebull/decoder-moo-reproducibility`, anonimizado en `https://anonymous.4open.science/r/decoder-moo-reproducibility/`; ese enlace va en "Data and Code Availability" de las versiones de envio.
- Conclusion partida en dos parrafos; frase de recap de robustez quitada de la conclusion de las reducidas para volver a 18 pp (el analisis sigue en el cuerpo).
- Auditorias: gramatica (caption capitalizado + frase duplicada removida), figuras/tablas (orden de tablas ascendente en la full), y bibliografia verificada entrada por entrada contra Crossref/fuente.
- Bibliografia: 4 referencias corregidas -> cato (URL homepage->deep-link, titulo "1.8 million in employment-based green card backlog", 2023), cerci (mal atribuida a Çerçi -> en realidad Wang, M. et al. 2022, Adv. Eng. Software 172:103218), kusoglu (inicial M., paginas 31--41), uscis (deep-link a las FAQ FY2023).
- Figura 1 (Taguchi main-effects): se corrigio "L\'evy" -> "Lévy" en el titulo del panel D (era acento estilo-LaTeX en un titulo de matplotlib); figura regenerada desde taguchi.json sin re-correr el DOE.

Gotcha de entregables: al regenerar una figura hay que actualizar `figures/<fig>.pdf` DENTRO de los 4 ZIP (no solo recompilar). Los 4 ZIP se reconstruyeron desde su manifiesto para quedar 100% al dia (.tex + figuras).

Validacion final: firewall 0/72, reproduce_fast overall_ok=true, anonymous_zip_hits=0, A4, 0 undefined/overfull.

Pendiente del usuario: re-subir/sincronizar los .tex y la figura a Overleaf (Overleaf no se entera de los cambios locales solo).
