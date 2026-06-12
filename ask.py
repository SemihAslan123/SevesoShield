"""
SevesoShield v2.0 — Interface en langage naturel

Pose une question en français et reçois une réponse directe et conversationnelle.

Usage :
    python ask.py "Je veux savoir ce qu'il y a autour de Rouen comme risques industriels"
    python ask.py "Y a-t-il des sites SEVESO près de Dunkerque ?"
    python ask.py "Quels sont les établissements sensibles autour de Feyzin ?"
    python ask.py "Analyse l'incident industriel à Tavaux"
"""

import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.manager_agent import ManagerAgent
from core import logger


# ──────────────────────────────────────────────────────────────────
#  Extraction du lieu depuis une question en langage naturel
# ──────────────────────────────────────────────────────────────────

def extract_city_from_question(question: str) -> str | None:
    """
    Extrait le nom de commune depuis une question en français.
    
    Exemples :
        "Qu'y a-t-il autour de Rouen ?"                    → "Rouen"
        "Y a-t-il des sites SEVESO près de Lyon ?"         → "Lyon"
        "Analyse un incident à Tavaux"                      → "Tavaux"
        "Risques industriels à Fos-sur-Mer"                 → "Fos-sur-Mer"
        "Ce qu'il y a autour de Rouen comme risques..."     → "Rouen"
    """
    # Pattern pour un nom de commune : 1 à 3 mots capitalisés, séparés par tiret ou espace
    # S'arrête aux mots communs (comme, avec, pour, et, ou...)
    CITY_PATTERN = r'([A-ZÀ-Ý][a-zà-ÿ\-]+(?:[\s\-][A-ZÀ-Ý][a-zà-ÿ\-]+){0,2})'

    # Prépositions spatiales → le lieu suit immédiatement
    spatial_preps = [
        r'autour\s+de\s+',
        r'pr[eè]s\s+de\s+',
        r'alentours?\s+de\s+',
        r'à\s+côté\s+de\s+',
        r'aux\s+abords?\s+de\s+',
        r'dans\s+la\s+commune\s+de\s+',
        r'sur\s+la\s+commune\s+de\s+',
        r'de\s+la\s+commune\s+de\s+',
        r'(?:autour|incident|alerte|situation|analyse)\s+(?:à|de|sur)\s+',
        r'\bà\s+',
        r'\bde\s+',
        r'\bsur\s+',
    ]

    for prep in spatial_preps:
        # On cherche la préposition (insensible à la casse) suivie d'un ou plusieurs mots
        pattern = r'(?i)' + prep + r'(\S+(?:\s+\S+){0,2})'
        match = re.search(pattern, question)
        if match:
            raw = match.group(1).strip()
            # Extraire uniquement les mots qui commencent par une majuscule (nom propre)
            # et s'arrêter dès qu'on rencontre un mot en minuscule
            words = raw.split()
            city_words = []
            for w in words:
                # Nettoyer la ponctuation en fin de mot
                w_clean = re.sub(r'[\?\!\.\,\;\:]+$', '', w)
                if w_clean and (w_clean[0].isupper() or '-' in w_clean):
                    city_words.append(w_clean)
                else:
                    break  # Premier mot non-capitalisé → on s'arrête
            candidate = " ".join(city_words).strip()
            if candidate and candidate.lower() not in _STOPWORDS_LOWER and len(candidate) > 2:
                return candidate

    # Dernier recours : chercher un nom propre isolé (majuscule, pas en début de phrase)
    for match in re.finditer(r'(?<!\A)(?<!\. )\b([A-ZÀ-Ý][a-zà-ÿ\-]+(?:[\-][A-ZÀ-Ý][a-zà-ÿ\-]+)*)\b', question):
        candidate = match.group(1).strip()
        if candidate.lower() not in _STOPWORDS_LOWER and len(candidate) > 2:
            return candidate

    return None


# Mots à ne pas considérer comme des communes
_STOPWORDS_LOWER = {
    "je", "il", "elle", "les", "des", "un", "une", "que", "qui", "quoi",
    "quels", "quelles", "comment", "combien", "est", "sont", "avoir",
    "seveso", "icpe", "analyse", "risques", "risque", "sites", "site",
    "ecoles", "écoles", "école", "hôpital", "hopital", "industrie",
    "industriel", "industriels", "établissements", "etablissements",
    "france", "français", "zone", "zones", "région", "commune", "ville",
    "département", "comme", "avec", "pour", "dans", "sur", "autour",
    "alerte", "incident", "situation", "veux", "savoir", "veut",
    "donner", "donne", "exposées", "exposees", "sensibles", "proches",
    "rayon", "kilomètres", "kilometres", "km", "mètres", "metres",
}


# ──────────────────────────────────────────────────────────────────
#  Formateur de réponse conversationnelle
# ──────────────────────────────────────────────────────────────────

def format_conversational_answer(question: str, result) -> str:
    """
    Produit une réponse directe et conversationnelle
    adaptée à la question posée.
    """
    lines = []

    # Vérification que le pipeline a réussi
    if not result.success or not result.synthese or not result.synthese.success:
        return "❌ Je n'ai pas pu analyser cette demande. Vérifiez le nom du lieu et réessayez."

    # Données collectées
    city = result.city or "ce lieu"
    pop_data = result.population.data if result.population and result.population.success else {}
    sites_data = result.sites.data if result.sites and result.sites.success else {}
    etab_data = result.etablissements.data if result.etablissements and result.etablissements.success else {}
    meteo_data = result.meteo.data if result.meteo and result.meteo.success else {}

    population = pop_data.get("population", "?")
    dept = pop_data.get("department", "")
    region = pop_data.get("region", "")

    sites_count = sites_data.get("count", 0)
    sites = sites_data.get("sites", [])
    seveso_high = [s for s in sites if "haut" in (s.get("seveso_status") or "").lower()]
    seveso_low  = [s for s in sites if "bas"  in (s.get("seveso_status") or "").lower()]

    etab_count = etab_data.get("count", 0)
    cats = etab_data.get("categories", {})
    schools = cats.get("school", 0) + cats.get("kindergarten", 0) + cats.get("childcare", 0)
    hospitals = cats.get("hospital", 0) + cats.get("clinic", 0)
    nursing = cats.get("nursing_home", 0)
    items = etab_data.get("items", [])

    wind = meteo_data.get("wind_interpretation", {})
    wind_from = wind.get("wind_from_label", "?")
    watch_label = wind.get("indicative_watch_towards_label", "?")
    temp = meteo_data.get("current", {}).get("temperature_2m", "?")
    wind_speed = meteo_data.get("current", {}).get("wind_speed_10m", "?")

    # ── Intro ──────────────────────────────────────────────────────
    pop_str = f"{population:,}".replace(",", " ") if isinstance(population, int) else str(population)
    dept_str = f" ({dept})" if dept else ""
    lines.append(f"📍 **{city}{dept_str}** — {pop_str} habitants")
    if region:
        lines.append(f"   Région : {region}")
    lines.append("")

    # ── Risques industriels ────────────────────────────────────────
    lines.append(f"🏭 **Risques industriels dans un rayon de {sites_data.get('radius_m', 5000)//1000} km :**")
    lines.append("")
    if sites_count == 0:
        lines.append("   Aucun site ICPE ou SEVESO identifié dans ce rayon.")
    else:
        lines.append(f"   → **{sites_count} installations ICPE** identifiées au total.")
        if seveso_high:
            lines.append(f"   → ⛔ **{len(seveso_high)} site(s) SEVESO Seuil Haut** (danger majeur) :")
            for s in seveso_high[:5]:
                dist = s.get("distance_m", "?")
                lines.append(f"      • **{s.get('name', '?')}** — à {dist} m")
        else:
            lines.append("   → ✅ Aucun site SEVESO Seuil Haut dans ce rayon.")
        if seveso_low:
            lines.append(f"   → ⚠️ **{len(seveso_low)} site(s) SEVESO Seuil Bas** :")
            for s in seveso_low[:3]:
                dist = s.get("distance_m", "?")
                lines.append(f"      • {s.get('name', '?')} — à {dist} m")
    lines.append("")

    # ── Établissements sensibles ───────────────────────────────────
    lines.append(f"🏫 **Établissements sensibles (rayon 3 km) :**")
    lines.append("")
    if etab_count == 0:
        lines.append("   Aucun établissement sensible identifié dans ce rayon (données OSM).")
    else:
        lines.append(f"   → **{etab_count} établissements** au total.")
        if schools:
            # Trouver les écoles les plus proches
            school_items = [i for i in items if i.get("category") in ("school", "kindergarten", "childcare")]
            lines.append(f"   → 🏫 **{schools} établissement(s) scolaire(s)** exposé(s).")
            if school_items:
                closest = school_items[0]
                lines.append(f"      Le plus proche : **{closest.get('name', 'Inconnu')}** à {closest.get('distance_m')} m du centre.")
        if hospitals:
            lines.append(f"   → 🏥 **{hospitals} hôpital(ux)/clinique(s)** à proximité.")
        if nursing:
            lines.append(f"   → 🏠 **{nursing} EHPAD/maison(s) de retraite** — populations vulnérables.")
    lines.append("")

    # ── Météo et vent ──────────────────────────────────────────────
    if meteo_data:
        lines.append(f"🌬️ **Conditions météo actuelles :**")
        lines.append(f"   → {temp}°C, vent à {wind_speed} km/h depuis le **{wind_from}**.")
        lines.append(f"   → Direction de vigilance indicative : **vers le {watch_label}**.")
        lines.append(f"   *(règle géométrique simple — non modélisé)*")
        lines.append("")

    # ── Conclusion directe ─────────────────────────────────────────
    lines.append("─" * 50)
    lines.append("")
    lines.append("💬 **En résumé :**")

    if seveso_high:
        names = " et ".join(s.get("name", "?") for s in seveso_high[:2])
        lines.append(f"   Il y a **{len(seveso_high)} site(s) SEVESO Seuil Haut** autour de {city} ({names}). C'est une zone à risque industriel élevé.")
    elif seveso_low:
        lines.append(f"   Pas de SEVESO Seuil Haut, mais **{len(seveso_low)} site(s) Seuil Bas** sont présents.")
    else:
        lines.append(f"   Pas de site SEVESO identifié dans ce rayon autour de {city}.")

    if schools:
        lines.append(f"   **{schools} école(s)** sont dans le périmètre exposé.")
    if hospitals:
        lines.append(f"   **{hospitals} structure(s) hospitalière(s)** sont à prendre en compte.")
    if meteo_data:
        lines.append(f"   En cas d'incident, la zone **vers le {watch_label}** est prioritaire pour la vigilance.")

    lines.append("")
    lines.append("⚠️ *Ces données sont indicatives — valider avec la DREAL, la Préfecture et les services de secours compétents.*")

    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────
#  Point d'entrée
# ──────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage : python ask.py \"Votre question en français\"")
        print()
        print("Exemples :")
        print('  python ask.py "Je veux savoir ce qu\'il y a autour de Rouen comme risques industriels"')
        print('  python ask.py "Y a-t-il des sites SEVESO près de Dunkerque ?"')
        print('  python ask.py "Combien d\'écoles sont exposées autour de Feyzin ?"')
        print('  python ask.py "Analyse la situation industrielle à Fos-sur-Mer"')
        sys.exit(0)

    question = " ".join(sys.argv[1:])

    print()
    print(f"  Question : \"{question}\"")
    print()

    # Extraire le lieu
    city = extract_city_from_question(question)
    if not city:
        print("❌ Je n'ai pas réussi à identifier un lieu dans votre question.")
        print("   Essayez d'inclure un nom de commune (ex: 'autour de Rouen', 'à Lyon').")
        sys.exit(1)

    print(f"  Lieu détecté : {city}")
    print()

    # Lancer le pipeline
    manager = ManagerAgent()
    result = manager.run(
        query=question,
        city=city,
        radius=5000
    )

    # Réponse conversationnelle
    logger.log_section("RÉPONSE")
    print(format_conversational_answer(question, result))
    print()


if __name__ == "__main__":
    main()
