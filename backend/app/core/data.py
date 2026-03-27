"""Visa demand data for 21 country blocs x 5 EB categories.

Sources:
    USCIS FY2025 Q2 Approved Petitions
    Visa Bulletin April 2026 (Final Action Dates)
"""

from app.core.config import COUNTRIES, CATEGORIES, T_ACTUAL, K_BASE, P_C, V

VISA_DATA: dict[str, dict[str, dict[str, int]]] = {
    "India": {
        "EB-1": {"n": 18_462, "d": 2023},
        "EB-2": {"n": 331_561, "d": 2014},
        "EB-3": {"n": 102_683, "d": 2013},
        "EB-4": {"n": 4_866, "d": 2022},
        "EB-5": {"n": 116, "d": 2022},
    },
    "China": {
        "EB-1": {"n": 11_858, "d": 2023},
        "EB-2": {"n": 36_172, "d": 2021},
        "EB-3": {"n": 13_334, "d": 2021},
        "EB-4": {"n": 853, "d": 2022},
        "EB-5": {"n": 12_117, "d": 2016},
    },
    "Filipinas": {
        "EB-1": {"n": 300, "d": 2026},
        "EB-2": {"n": 187, "d": 2026},
        "EB-3": {"n": 22_040, "d": 2023},
        "EB-4": {"n": 314, "d": 2022},
        "EB-5": {"n": 50, "d": 2026},
    },
    "Mexico": {
        "EB-1": {"n": 200, "d": 2026},
        "EB-2": {"n": 727, "d": 2026},
        "EB-3": {"n": 5_432, "d": 2024},
        "EB-4": {"n": 12_963, "d": 2022},
        "EB-5": {"n": 50, "d": 2026},
    },
    "Afganistan": {
        "EB-1": {"n": 30, "d": 2026},
        "EB-2": {"n": 100, "d": 2025},
        "EB-3": {"n": 500, "d": 2023},
        "EB-4": {"n": 100_000, "d": 2022},
        "EB-5": {"n": 20, "d": 2026},
    },
    "Irak": {
        "EB-1": {"n": 30, "d": 2026},
        "EB-2": {"n": 100, "d": 2025},
        "EB-3": {"n": 400, "d": 2023},
        "EB-4": {"n": 80_000, "d": 2022},
        "EB-5": {"n": 20, "d": 2026},
    },
    "Corea del Sur": {
        "EB-1": {"n": 1_200, "d": 2026},
        "EB-2": {"n": 3_000, "d": 2025},
        "EB-3": {"n": 3_500, "d": 2023},
        "EB-4": {"n": 200, "d": 2022},
        "EB-5": {"n": 150, "d": 2026},
    },
    "Pakistan": {
        "EB-1": {"n": 800, "d": 2026},
        "EB-2": {"n": 2_500, "d": 2025},
        "EB-3": {"n": 3_000, "d": 2023},
        "EB-4": {"n": 500, "d": 2022},
        "EB-5": {"n": 30, "d": 2026},
    },
    "Iran": {
        "EB-1": {"n": 700, "d": 2026},
        "EB-2": {"n": 2_000, "d": 2025},
        "EB-3": {"n": 1_500, "d": 2023},
        "EB-4": {"n": 300, "d": 2022},
        "EB-5": {"n": 30, "d": 2026},
    },
    "Taiwan": {
        "EB-1": {"n": 800, "d": 2026},
        "EB-2": {"n": 1_500, "d": 2025},
        "EB-3": {"n": 2_000, "d": 2023},
        "EB-4": {"n": 50, "d": 2022},
        "EB-5": {"n": 100, "d": 2026},
    },
    "Brasil": {
        "EB-1": {"n": 500, "d": 2026},
        "EB-2": {"n": 1_200, "d": 2025},
        "EB-3": {"n": 1_800, "d": 2023},
        "EB-4": {"n": 100, "d": 2022},
        "EB-5": {"n": 50, "d": 2026},
    },
    "Canada": {
        "EB-1": {"n": 600, "d": 2026},
        "EB-2": {"n": 1_000, "d": 2025},
        "EB-3": {"n": 1_200, "d": 2023},
        "EB-4": {"n": 50, "d": 2022},
        "EB-5": {"n": 50, "d": 2026},
    },
    "Reino Unido": {
        "EB-1": {"n": 500, "d": 2026},
        "EB-2": {"n": 900, "d": 2025},
        "EB-3": {"n": 1_000, "d": 2023},
        "EB-4": {"n": 50, "d": 2022},
        "EB-5": {"n": 50, "d": 2026},
    },
    "Nigeria": {
        "EB-1": {"n": 300, "d": 2026},
        "EB-2": {"n": 800, "d": 2025},
        "EB-3": {"n": 1_200, "d": 2023},
        "EB-4": {"n": 500, "d": 2022},
        "EB-5": {"n": 20, "d": 2026},
    },
    "Japon": {
        "EB-1": {"n": 600, "d": 2026},
        "EB-2": {"n": 700, "d": 2025},
        "EB-3": {"n": 800, "d": 2023},
        "EB-4": {"n": 50, "d": 2022},
        "EB-5": {"n": 50, "d": 2026},
    },
    "Bangladesh": {
        "EB-1": {"n": 200, "d": 2026},
        "EB-2": {"n": 600, "d": 2025},
        "EB-3": {"n": 1_500, "d": 2023},
        "EB-4": {"n": 300, "d": 2022},
        "EB-5": {"n": 20, "d": 2026},
    },
    "Colombia": {
        "EB-1": {"n": 200, "d": 2026},
        "EB-2": {"n": 400, "d": 2025},
        "EB-3": {"n": 800, "d": 2023},
        "EB-4": {"n": 200, "d": 2022},
        "EB-5": {"n": 20, "d": 2026},
    },
    "Alemania": {
        "EB-1": {"n": 400, "d": 2026},
        "EB-2": {"n": 500, "d": 2025},
        "EB-3": {"n": 800, "d": 2023},
        "EB-4": {"n": 50, "d": 2022},
        "EB-5": {"n": 30, "d": 2026},
    },
    "Vietnam": {
        "EB-1": {"n": 200, "d": 2026},
        "EB-2": {"n": 400, "d": 2025},
        "EB-3": {"n": 1_200, "d": 2023},
        "EB-4": {"n": 200, "d": 2022},
        "EB-5": {"n": 100, "d": 2026},
    },
    "Etiopia": {
        "EB-1": {"n": 50, "d": 2026},
        "EB-2": {"n": 200, "d": 2025},
        "EB-3": {"n": 500, "d": 2023},
        "EB-4": {"n": 1_000, "d": 2022},
        "EB-5": {"n": 20, "d": 2026},
    },
    "Resto del Mundo": {
        "EB-1": {"n": 14_890, "d": 2026},
        "EB-2": {"n": 12_556, "d": 2025},
        "EB-3": {"n": 22_155, "d": 2023},
        "EB-4": {"n": 14_892, "d": 2022},
        "EB-5": {"n": 300, "d": 2026},
    },
}

# Data provenance metadata
REAL_DEMAND: dict[str, set[str]] = {
    "India": {"EB-1", "EB-2", "EB-3", "EB-4", "EB-5"},
    "China": {"EB-1", "EB-2", "EB-3", "EB-4", "EB-5"},
    "Filipinas": {"EB-2", "EB-3", "EB-4"},
    "Mexico": {"EB-2", "EB-3", "EB-4"},
}

EST_DEM_CATS: set[str] = {"EB-1", "EB-5"}

DHS_COUNTRIES: set[str] = {
    "Afganistan", "Irak", "Corea del Sur", "Pakistan", "Iran", "Taiwan",
    "Brasil", "Canada", "Reino Unido", "Nigeria", "Japon", "Bangladesh",
    "Colombia", "Alemania", "Vietnam", "Etiopia",
}


def demand_source(country: str, category: str) -> str:
    if country in REAL_DEMAND and category in REAL_DEMAND[country]:
        return "REAL"
    if country in DHS_COUNTRIES and category in EST_DEM_CATS:
        return "EST-DEM"
    if country in DHS_COUNTRIES:
        return "EST"
    if country == "Resto del Mundo" and category in EST_DEM_CATS:
        return "EST-DEM"
    if country == "Resto del Mundo":
        return "EST"
    return "EST-DEM"


def build_groups() -> list[dict]:
    groups: list[dict] = []
    idx = 0
    for country in COUNTRIES:
        for cat in CATEGORIES:
            entry = VISA_DATA[country][cat]
            w = T_ACTUAL - entry["d"]
            groups.append({
                "index": idx,
                "country": country,
                "category": cat,
                "n": entry["n"],
                "d": entry["d"],
                "w": w,
            })
            idx += 1
    return groups


def compute_spillover(groups: list[dict]) -> dict[str, int]:
    demand_by_cat: dict[str, int] = {cat: 0 for cat in CATEGORIES}
    for g in groups:
        demand_by_cat[g["category"]] += g["n"]

    d4 = demand_by_cat["EB-4"]
    d5 = demand_by_cat["EB-5"]
    d1 = demand_by_cat["EB-1"]
    d2 = demand_by_cat["EB-2"]

    k4_eff = K_BASE["EB-4"]
    k5_eff = K_BASE["EB-5"]
    s4 = max(0, k4_eff - d4)
    s5 = max(0, k5_eff - d5)

    k1_eff = K_BASE["EB-1"] + s4 + s5
    s1 = max(0, k1_eff - d1)

    k2_eff = K_BASE["EB-2"] + s1
    s2 = max(0, k2_eff - d2)

    k3_eff = K_BASE["EB-3"] + s2

    return {
        "EB-1": k1_eff, "EB-2": k2_eff, "EB-3": k3_eff,
        "EB-4": k4_eff, "EB-5": k5_eff,
    }


def compute_country_caps(groups: list[dict]) -> dict[str, int]:
    country_demand: dict[str, int] = {}
    for g in groups:
        country_demand[g["country"]] = country_demand.get(g["country"], 0) + g["n"]

    caps: dict[str, int] = {}
    sum_others = 0
    for country in COUNTRIES:
        if country != "Resto del Mundo":
            caps[country] = P_C
            sum_others += min(country_demand[country], P_C)

    caps["Resto del Mundo"] = max(P_C, V - sum_others)
    return caps
