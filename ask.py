"""
SevesoShield v2.0 — Interface LLM en langage naturel

Llama 3 (via Groq) joue le rôle de "cerveau" :
  1. Comprend la question en français (n'importe quelle formulation)
  2. Extrait le lieu et les paramètres pertinents
  3. Lance le pipeline multi-agents (déterministe)
  4. Formule une réponse conversationnelle adaptée à la vraie question

Usage :
    python ask.py "C'est dangereux à Besançon ?"
    python ask.py "Y a-t-il des sites SEVESO près de Dunkerque ?"
    python ask.py "Est-ce que les enfants sont en sécurité à Tavaux ?"
    python ask.py "Qu'est-ce qui peut exploser autour de Feyzin ?"

Prérequis :
    $env:GROQ_API_KEY = "votre_cle_ici"
    (clé gratuite sur https://console.groq.com/keys)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.manager_agent import ManagerAgent
from core import llm, logger


def build_pipeline_summary(result) -> dict:
    """
    Construit un dictionnaire résumé des données collectées
    pour l'envoyer à Gemini afin qu'il formule la réponse.
    """
    summary = {
        "localisation": {},
        "risques_industriels": {},
        "meteo_vent": {},
        "etablissements_sensibles": {},
    }

    # Localisation / Population
    if result.population and result.population.success:
        d = result.population.data
        summary["localisation"] = {
            "commune": d.get("city", "?"),
            "departement": d.get("department", "?"),
            "region": d.get("region", "?"),
            "population": d.get("population", "?"),
            "code_insee": d.get("insee_code", "?"),
        }

    # Risques industriels
    if result.sites and result.sites.success:
        d = result.sites.data
        sites = d.get("sites", [])
        seveso_high = [s for s in sites if "haut" in (s.get("seveso_status") or "").lower()]
        seveso_low  = [s for s in sites if "bas"  in (s.get("seveso_status") or "").lower()]
        summary["risques_industriels"] = {
            "total_icpe": d.get("count", 0),
            "rayon_m": d.get("radius_m", 5000),
            "seveso_seuil_haut": [
                {"nom": s.get("name"), "distance_m": s.get("distance_m"), "ville": s.get("city")}
                for s in seveso_high[:5]
            ],
            "seveso_seuil_bas": [
                {"nom": s.get("name"), "distance_m": s.get("distance_m")}
                for s in seveso_low[:3]
            ],
        }
    else:
        summary["risques_industriels"] = {"erreur": "données indisponibles (API Géorisques)"}

    # Météo et vent
    if result.meteo and result.meteo.success:
        d = result.meteo.data
        current = d.get("current", {})
        wind = d.get("wind_interpretation", {})
        summary["meteo_vent"] = {
            "temperature_c": current.get("temperature_2m"),
            "vent_kmh": current.get("wind_speed_10m"),
            "rafales_kmh": current.get("wind_gusts_10m"),
            "vent_depuis": wind.get("wind_from_label"),
            "vigilance_vers": wind.get("indicative_watch_towards_label"),
            "note": "direction de vigilance indicative uniquement (règle géométrique simple)",
        }
    else:
        summary["meteo_vent"] = {"erreur": "données indisponibles (API Open-Meteo)"}

    # Établissements sensibles
    if result.etablissements and result.etablissements.success:
        d = result.etablissements.data
        cats = d.get("categories", {})
        items = d.get("items", [])
        priority = [i for i in items if i.get("category") in ("school", "kindergarten", "hospital", "clinic", "nursing_home")]
        summary["etablissements_sensibles"] = {
            "total": d.get("count", 0),
            "rayon_m": d.get("radius_m", 3000),
            "ecoles": cats.get("school", 0) + cats.get("kindergarten", 0),
            "hopitaux_cliniques": cats.get("hospital", 0) + cats.get("clinic", 0),
            "ehpad": cats.get("nursing_home", 0),
            "etablissements_prioritaires_proches": [
                {"nom": i.get("name"), "type": i.get("category"), "distance_m": i.get("distance_m")}
                for i in priority[:5]
            ],
        }
    else:
        summary["etablissements_sensibles"] = {"erreur": "données indisponibles (API Overpass/OSM)"}

    return summary


def main():
    if len(sys.argv) < 2:
        print()
        print("  Usage : python ask.py \"votre question en français\"")
        print()
        print("  Exemples :")
        print("    python ask.py \"C'est dangereux a Besancon ?\"")
        print("    python ask.py \"Y a-t-il des sites SEVESO pres de Dunkerque ?\"")
        print("    python ask.py \"Est-ce que les enfants sont en securite a Tavaux ?\"")
        print("    python ask.py \"Qu est-ce qui peut exploser autour de Feyzin ?\"")
        print()
        sys.exit(0)

    question = " ".join(sys.argv[1:])

    print()
    print(f"  Question : \"{question}\"")
    print()

    # ── ÉTAPE 1 : Le LLM comprend la question ──────────────────────────────────
    print("  [LLM] Llama 3 analyse votre question...")
    try:
        parsed = llm.extract_location_from_question(question)
    except EnvironmentError as e:
        print(e)
        sys.exit(1)

    city   = parsed.get("city")
    lat    = parsed.get("lat")
    lon    = parsed.get("lon")
    radius = parsed.get("radius", 5000)
    intent = parsed.get("intent", "analyse générale")

    if not city and not (lat and lon):
        print()
        print("  ❌ Le LLM n'a pas identifié de lieu dans votre question.")
        print("  Essayez d'inclure un nom de commune (ex: 'autour de Rouen', 'à Lyon').")
        sys.exit(1)

    print(f"  [LLM] Lieu détecté : {city or f'GPS ({lat}, {lon})'} — Intention : {intent}")
    print()

    # ── ÉTAPE 2 : Pipeline multi-agents (déterministe) ─────────────────────────
    manager = ManagerAgent()
    result = manager.run(
        query=question,
        city=city,
        lat=lat,
        lon=lon,
        radius=radius
    )

    if not result.success:
        print("  ❌ Le pipeline n'a pas pu collecter les données nécessaires.")
        sys.exit(1)

    # ── ÉTAPE 3 : Le LLM formule la réponse ───────────────────────────────────
    logger.log_section("RÉPONSE DE SEVESOSCHIELD")
    print()
    print("  [LLM] Llama 3 formule la réponse...")
    print()

    pipeline_data = build_pipeline_summary(result)
    response = llm.generate_conversational_response(question, pipeline_data)

    print(response)
    print()


if __name__ == "__main__":
    main()
