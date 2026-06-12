"""
SevesoShield — Agent Établissements Sensibles

Rôle : Identifier les établissements sensibles (écoles, hôpitaux, EHPAD...) autour d'un point.
Source : OpenStreetMap / Overpass API (overpass-api.de)
Skill d'origine : skills/etablissements-sensibles/main.py
"""

import os
import importlib.util

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_PATH = os.path.join(_ROOT, "skills", "etablissements-sensibles", "main.py")

_spec = importlib.util.spec_from_file_location("etablissements_sensibles", _SKILL_PATH)
_etab_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_etab_module)

from agents.base_agent import BaseAgent
from core.schemas import AgentInput

# Rayon spécifique pour les établissements (3 km par défaut — plus pertinent)
_DEFAULT_ETAB_RADIUS = 3000


class EtablissementsAgent(BaseAgent):
    """
    Agent établissements sensibles.
    
    Entrée  : AgentInput.lat, AgentInput.lon (radius optionnel — défaut 3000 m)
    Sortie  : { center, radius_m, count, categories: {school: N, hospital: N, ...},
                items: [{name, category, distance_m, ...}] }
    """

    name = "EtablissementsAgent"

    def _execute(self, inp: AgentInput) -> dict:
        if inp.lat is None or inp.lon is None:
            raise ValueError("Coordonnées GPS manquantes pour EtablissementsAgent")

        # On utilise un rayon dédié pour les établissements (3 km)
        radius = min(inp.radius, _DEFAULT_ETAB_RADIUS)
        result = _etab_module.get_sensitive_facilities(inp.lat, inp.lon, radius)

        if "error" in result:
            raise ValueError(result["error"])

        return result

    def _start_detail(self, inp: AgentInput) -> str:
        return f"rayon={min(inp.radius, _DEFAULT_ETAB_RADIUS)} m"

    def _success_detail(self, data: dict) -> str:
        count = data.get("count", 0)
        cats = data.get("categories", {})
        schools = cats.get("school", 0) + cats.get("kindergarten", 0)
        hospitals = cats.get("hospital", 0) + cats.get("clinic", 0)
        summary_parts = []
        if schools:
            summary_parts.append(f"{schools} école(s)")
        if hospitals:
            summary_parts.append(f"{hospitals} hôpital/clinique")
        return f"{count} établissement(s) — {', '.join(summary_parts) or 'voir détail'}"
