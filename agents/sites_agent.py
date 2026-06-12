"""
SevesoShield — Agent Sites Industriels à Risque

Rôle : Rechercher les sites ICPE/SEVESO autour d'un point GPS.
Source : API Géorisques (georisques.gouv.fr)
Skill d'origine : skills/sites-industriels-risques/main.py
"""

import os
import importlib.util

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_PATH = os.path.join(_ROOT, "skills", "sites-industriels-risques", "main.py")

_spec = importlib.util.spec_from_file_location("sites_industriels_risques", _SKILL_PATH)
_sites_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sites_module)

from agents.base_agent import BaseAgent
from core.schemas import AgentInput


class SitesAgent(BaseAgent):
    """
    Agent sites industriels ICPE/SEVESO.
    
    Entrée  : AgentInput.lat, AgentInput.lon, AgentInput.radius
    Sortie  : { center, radius_m, count, sites: [{name, city, seveso_status, distance_m, ...}] }
    """

    name = "SitesAgent"

    def _execute(self, inp: AgentInput) -> dict:
        if inp.lat is None or inp.lon is None:
            raise ValueError("Coordonnées GPS manquantes pour SitesAgent")

        result = _sites_module.get_icpe_sites(inp.lat, inp.lon, inp.radius)

        if "error" in result:
            raise ValueError(result["error"])

        return result

    def _start_detail(self, inp: AgentInput) -> str:
        return f"rayon={inp.radius} m"

    def _success_detail(self, data: dict) -> str:
        count = data.get("count", 0)
        seveso = [s for s in data.get("sites", [])
                  if (s.get("seveso_status") or "").lower() not in ("non seveso", "non renseigné", "")]
        return f"{count} site(s) dont {len(seveso)} SEVESO"
