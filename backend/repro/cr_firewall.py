"""Gate del camera-ready. Va MAS ALLA de comprobar valores contra JSON:

  * EXIGE que los claims esperados EXISTAN en el PDF (no basta con validar los
    que se encuentren: una cifra borrada pasaria un gate solo-de-valores).
  * PROHIBE terminologia retirada.
  * Comprueba INVARIANTES de instrumentacion en los JSON publicos.
  * Verifica el texto DENTRO de las figuras, en el PDF de figura y en el ensamblado.

Uso:  python cr_firewall.py --pdf <ruta> --figdir <dir>
"""
import sys, json, re, subprocess, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import _bootstrap; _bootstrap.bootstrap_engine()
R = Path(_bootstrap.results_dir())

def pdftext(p):
    raw = subprocess.run(["pdftotext", str(p), "-"], capture_output=True, text=True).stdout
    return " ".join(raw.split())

# (1) claims que DEBEN aparecer, con CONTEO EXACTO. La presencia sola no basta:
#     "316,345" sale dos veces, asi que sustituir una y dejar la otra pasaria un
#     gate de solo-presencia. Los p-valores se exigen con su frase completa,
#     porque un fragmento como "5.9" casa en varios sitios del documento.
REQUIRED = {
    "316,345": 2, "321,799": 1, "\\textbf{204}".replace("\\textbf{","").replace("}",""): None,
    "it dominates 15,270 of the 15,273 points": 1,  "20,200": 1,
    "Mann\u2013Whitney p = 5.9 \u00d7 10\u22125": 1,
    "seed-label Wilcoxon p = 5.7 \u00d7 10\u22124": 1,
    "H = 149.8": 1, "\u03c72 = 133.8": 1, "0.885": 1,
    "0.027": 1, "0.254": 1, "0.474": 1, "0.790": 1, "0.860": 1,
    "0.972": 1, "0.961": 1, "0.999": 1,
    "NDS-selected": 10, "Kruskal\u2013Wallis": 5, "Rebull-Saucedo": 11,
    "Disclosure of Interests": 1,
    # los dos controles, con su p bilateral y la frase entera que lo enmarca
    "same budget) lands 3.8 % below uniform constructions (298,531, Mann\u2013Whitney p = 6.1 \u00d7 10\u221211": 1,
    "lands 2.0 % below blind sampling (Mann\u2013Whitney p = 1.9 \u00d7 10\u22124": 1,
    # la salvedad de procedencia que el Reviewer #1 pregunto explicitamente
    "a calibrated synthetic case study": 2,
    # Jain: sobre que cantidad se calcula
    "Jain\u2019s index on inverse waits 0.80 \u2192 0.94": 1,
    # la Fig. 4 era la unica figura con label y sin referencia en el texto
    "Of the four packages (Figure 4)": 1,
    "(tag micai-cameraready-r1)": 1,
    # la frase de equidad, con la Gini corregida (la version enviada imprimia 0.17)
    "wait standard deviation falls 3.14 \u2192 0.75": 1,
    "Gini 0.79 \u2192 0.23": 1,
    # credits acordados por los tres autores: la declaracion de financiamiento es
    # una afirmacion de hecho y debe sobrevivir a cualquier recompactacion
    "Gilberto Rivera-Z\u00e1rate, coordinator of the": 1,
    "have no competing interests": 1,
    "without external funding": 1,
    "provided non-financial": 1,
    # el tag citado en Data Availability: una afirmacion sobre donde vive el codigo
    # N1: la refutacion de C2 fuera del visa
    "gated acceptance did so only on the visa": 1,
    "p = 9.0 \u00d7 10\u221211": 1, "9.2 %": 3,
    "whose first fully dominating value is 20,201 and which runs to 25,000": 1,
    "one-sided Mann\u2013Whitney p < 10\u22124": 1,
    "genetic algorithm (BRKGA) crossover": 1,
    "five simultaneous constraints": 1, "wait disparity": 4,
    # lote semantico-numerico
    "316,345 \u00b1 6,682": 1, "Z9 (185)": 1, "per-run fronts against Z9,hist": 1, "Z9,hist (187)": 1, "Z2 (126 points": 1,
    "20,201": 1,
    "p = 3.0 \u00d7 10\u221211": 1, "seed-label Wilcoxon sensitivity p = 1.9 × 10−9": 1,
    "\u03b7c \u2208 {2, 5, 10, 20, 50, 100}": 1,
    "five hard constraints": 3, "FIFO ordering convention": 4,
    # 2x2 reescrito como paquetes
    "variation package (C1)": 2, "selection rule (C2)": 2,
    "p = 7.979 \u00d7 10\u22124": 1, "p = 6.0 × 10−4": 1,
    "25,050": 2, "0.87 % and 1.75 %": 1,
    "HHO moves": 2, "poly. mutation": 2,
}
# (2) terminologia retirada que NO debe reaparecer
FORBIDDEN = [
    # valores obsoletos: solo pueden vivir en evidencia_archivo200/ y en la nota
    "Z9 (187) , the 9", "15,377", "15,374",
    # promesas y formulaciones retiradas en este lote
    "regenerate every reported number", "6,682 \u00b1", "\u00b1 6,683",
    "fixes the parameters shared", "fixes shared parameters", "fixing the parameters shared",
    # microbloque semantico
    "shared Taguchi-fixed operating point", "Taguchi-tuned N and T",
    "not a tuning artifact", "exactly N \u00d7 T evaluations",
    "diversity-preserving mechanism control",
    "ranks them as the two-condition account predicts",
    "micai-submission-v1", "micai-submission-v2",
    "uniform constructions (298,531, Mann\u2013Whitney p = 3.0",   # unilateral de GRASP
    "blind sampling (Mann\u2013Whitney p = 9.5",       # unilateral de la busqueda local
    "Jain 0.80 \u2192 0.94",                       # sin decir sobre que cantidad
    "(tag micai-cameraready)",                     # el tag anterior, ya historico
    "Gini 0.79 \u2192 0.17",   # valor erroneo de la version enviada
    "no competing interests to declare",
    "nominal exception", "lies within the critical difference",
    "the sweep reaching 22,081", "nearest-neighbour",
    "six simultaneous constraints", "waste and equity",
    "diversity-preserving swarm", "trading off against equity",
    "biased random-key (BRKGA-style)",
    "six hard constraints", "\u03b7c \u2208 {2, . . . , 100}",
    "isolation experiment",
    # afirmaciones fuertes retiradas: la tesis es una pantalla de riesgo contextual
    # ANOVA y permutacion sin bloques, retirados del 2x2
    "F = 16.7", "\u03b7 2 = 0.098", "p = 8.0 \u00d7 10\u22125", "p = 2.0 \u00d7 10\u22124",
    "varying only the operator", "synergistic", "operator\u00d7selection",
    "50 \u00d7 500 evaluation budget",
    "only if", "necessary but not sufficient", "confirms the two-condition core",
    "predicts a win", "under every configuration", "preserves population diversity",
    "preserves diversity", "preserve diversity",
    "Competent MO-HHO", "competent MO-HHO", "paired seeds", "paired Friedman",
    "variance-reduction", "an upper bound on each objective",
    "the top tier is theirs", "genuine three-way conflict",
    "five problem families", "Rebull Saucedo",
    "realized population movement", "whole population is replaced",
]
# (3) invariantes de instrumentacion en los JSON publicos
def json_invariants():
    out = []
    d = json.load(open(R / "factorial_2x2_conditions.json"))
    for name, c in d["cells"].items():
        nds = c.get("selection") == "nds"
        if nds:
            out.append((f"{name}: moved_fraction_mean es null", c.get("moved_fraction_mean") is None))
            out.append((f"{name}: movement_measured es False", c.get("movement_measured") is False))
        else:
            out.append((f"{name}: movement_measured es True", c.get("movement_measured") is True))
            out.append((f"{name}: moved_fraction_mean es numerico",
                        isinstance(c.get("moved_fraction_mean"), (int, float))))
    e = json.load(open(R / "expC_decoder_ladder.json"))["tier_separation"]
    for k, v in e.items():
        out.append((f"decoder {k}: MWU primaria presente", isinstance(v.get("mwu_p_perm_gt_rk"), float)))
        out.append((f"decoder {k}: campo paired_* retirado", "paired_wilcoxon_p_perm_gt_rk" not in v))
    # omnibus y contrastes de la escalera: una sola fuente gobernada, el deriver puro
    st = json.load(open(R / "cr_derived.json"))
    out.append(("omnibus primario es Kruskal-Wallis",
                "Kruskal" in st["omnibus"]["ladder9"]["primary"]["test"]))
    out.append(("MWU primaria < Wilcoxon sensibilidad (NDS vs random)",
                st["holm"]["unpaired_primary"]["results"]["nds_vs_random"]["p"]
                < st["holm"]["seed_label_sensitivity"]["results"]["nds_vs_random"]["p"]))
    # mo-SCP es el unico bloqueo preregistrado y su Wilcoxon pareado no lo re-deriva
    # cr_derive.py; se lee de su snapshot gobernado, no del deriver.
    sc = json.load(open(R / "cr_stats_v2.json"))
    out.append(("mo-SCP conserva Wilcoxon pareado como primaria",
                "Wilcoxon" in sc["mo_scp"]["competent_vs_random"]["primary_test"]))
    c = json.load(open(R / "competent_arch100.json"))
    out.append(("invariancia de trayectoria 30/30",
                c["trajectory_invariance"]["seeds_identical"] == 30))
    return out

# (4) texto dentro de las figuras
FIG_REQUIRED = {"ladder.pdf": ["NDS-selected"],
                "mechanism_2x2_annot.pdf": ["variation package (C1)", "selection rule (C2)",
                                            "HHO moves", "replace their parent"]}
FIG_FORBIDDEN = {"ladder.pdf": ["Competent"],
                 "mechanism_2x2_annot.pdf": ["Realized population", "movement per iteration",
                                             "\u03c4", "order-changing", "near-identity"]}

EXPECTED_META = {
    "Title": "A Two-Condition Diagnostic for Decoder-Based Multi-Objective Search: "
             "When Blind Sampling Beats a Mismatched NSGA-II",
    "Author": "Javier Augusto Rebull-Saucedo; Yazmin Ivonne Flores-Martinez; "
              "Ra\u00fal Gibran Porras-Alaniz",
    "Subject": "MICAI 2026 Posters Track (Springer CCIS)",
}

def check_metadata(pdf):
    out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
    got = {}
    for line in out.splitlines():
        if ":" in line:
            k, v = line.split(":", 1); got[k.strip()] = v.strip()
    bad = []
    for k, want in EXPECTED_META.items():
        if got.get(k, "") != want:
            bad.append(f"metadata {k}: esperado {want[:42]!r}... encontrado {got.get(k,'(vacio)')[:42]!r}")
    if not got.get("Keywords"): bad.append("metadata Keywords vacio")
    if "2026" not in got.get("CreationDate", ""): bad.append(f"CreationDate no es de 2026: {got.get('CreationDate')}")
    return bad


# (5) lettering de artwork: minimo 6 pt NOMINALES en toda pagina con figura.
# La escala de matriz del PDF es 0.99626 (10 pt miden 9.96), asi que 6 pt nominales
# se miden como 5.98: comparar contra 6.00 crudo reprueba fuentes que si cumplen.
K_MATRIZ = 0.99626
MIN_ARTWORK_PT = 6.0

def artwork_lettering(pdf_path):
    try:
        import pdfplumber
    except ImportError:
        return [("lettering de artwork: pdfplumber ausente, control NO ejecutado", False)]
    umbral = MIN_ARTWORK_PT * K_MATRIZ - 0.005
    out = []
    doc = pdfplumber.open(pdf_path)
    for i, pg in enumerate(doc.pages):
        if not any(l.startswith("Fig.") for l in (pg.extract_text() or "").split("\n")):
            continue
        # el cuerpo va a 8.97/9.96; por debajo de 8.5 solo queda lettering de figura
        up = [c for c in pg.chars if c["upright"] and c["size"] < 8.5]
        # en texto girado 90 grados el ancho del bbox es la altura real del glifo
        rot = [c for c in pg.chars if not c["upright"]]
        lo_u = min((c["size"] for c in up), default=99.0)
        lo_r = min((c["x1"] - c["x0"] for c in rot), default=99.0)
        out.append((f"p{i+1}: lettering de figura >= {MIN_ARTWORK_PT} pt "
                    f"(recto {lo_u:.2f}, girado {lo_r:.2f})",
                    lo_u >= umbral and lo_r >= umbral))
    if not out:
        out.append(("lettering de artwork: no se hallo ninguna pagina con figura", False))
    return out


# (6) frases que el salto de linea rompe en el PDF: se verifican en la FUENTE.
# "random-key" se parte en su propio guion y pdftotext lo devuelve como "randomkey";
# eso es tipografia correcta, no un defecto, asi que el ancla va en el .tex.
SOURCE_REQUIRED = {
    "biased random-key genetic algorithm (BRKGA)": 1,
    "first-in, first-out (FIFO) ordering convention": 1,
}

def source_phrases(pdf_path):
    tex = Path(str(pdf_path)[:-4] + ".tex")
    if not tex.exists():
        return [(f"fuente {tex.name} no hallada junto al PDF", False)]
    t = tex.read_text()
    return [(f"fuente: {k!r} x{n}", t.count(k) == n) for k, n in SOURCE_REQUIRED.items()]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf", required=True); ap.add_argument("--figdir", required=True)
    a = ap.parse_args()
    T = pdftext(a.pdf); fails = []
    for k, n in REQUIRED.items():
        c = T.count(k)
        if c == 0: fails.append(f"FALTA en el PDF: {k!r}")
        elif n is not None and c != n:
            fails.append(f"CONTEO cambiado para {k!r}: esperado {n}, encontrado {c}")
    for k in FORBIDDEN:
        if k in T: fails.append(f"PROHIBIDO y presente en el PDF: {k!r}")
    fails += check_metadata(a.pdf)
    for desc, ok in source_phrases(a.pdf):
        if not ok: fails.append(f"FUENTE incumplida: {desc}")
    art = artwork_lettering(a.pdf)
    for desc, ok in art:
        if not ok: fails.append(f"LETTERING bajo el minimo: {desc}")
    for desc, ok in json_invariants():
        if not ok: fails.append(f"INVARIANTE roto: {desc}")
    for fig, keys in FIG_REQUIRED.items():
        t = pdftext(Path(a.figdir) / fig)
        for k in keys:
            if k not in t: fails.append(f"FALTA en {fig}: {k!r}")
            if k not in T: fails.append(f"FALTA en el PDF ensamblado (via {fig}): {k!r}")
    # Estas prohibiciones son de la FIGURA. El mismo termino puede ser legitimo en
    # el cuerpo (la tau de Kendall del ladder, "order-changing" en la prosa), asi
    # que NO se evaluan contra el PDF ensamblado.
    for fig, keys in FIG_FORBIDDEN.items():
        t = pdftext(Path(a.figdir) / fig)
        for k in keys:
            if k in t: fails.append(f"PROHIBIDO en la figura {fig}: {k!r}")
    print(f"  requeridos(con conteo): {len(REQUIRED)}  prohibidos: {len(FORBIDDEN)}  "
          f"invariantes: {len(json_invariants())}  figuras: {len(FIG_REQUIRED)}  "
          f"paginas con artwork: {len(art)}")
    for f in fails: print("  " + f)
    print(f"\n  n_fallos = {len(fails)}")
    return 1 if fails else 0

sys.exit(main())
