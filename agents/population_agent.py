"""
SevesoShield — Agent Contexte Population

Rôle : Fournir le contexte administratif et démographique d'une commune.
Source : geo.api.gouv.fr (COG / INSEE)
Skill d'origine : skills/contexte-population/main.py
"""

import os
import importlib.util

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_PATH = os.path.join(_ROOT, "skills", "contexte-population", "main.py")

_spec = importlib.util.spec_from_file_location("contexte_population", _SKILL_PATH)
_pop_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pop_module)

from agents.base_agent import BaseAgent
from core.schemas import AgentInput


class PopulationAgent(BaseAgent):
    """
    Agent contexte population / administratif.
    
    Entrée  : AgentInput.lat + AgentInput.lon OU AgentInput.city
    Sortie  : { city, insee_code, postcode, population, department, region, center }
    """

    name = "PopulationAgent"

    def _execute(self, inp: AgentInput) -> dict:
        result = _pop_module.get_commune_info(
            lat=inp.lat,
            lon=inp.lon,
            city=inp.city
        )

        if "error" in result:
            raise ValueError(result["error"])

        return result

    def _start_detail(self, inp: AgentInput) -> str:
        if inp.city:
            return f"city='{inp.city}'"
        return f"lat={inp.lat:.4f}, lon={inp.lon:.4f}" if inp.lat else ""

    def _success_detail(self, data: dict) -> str:
        city = data.get("city", "?")
        dept = data.get("department", "?")
        pop = data.get("population", "?")
        return f"{city} ({dept}) — {pop} hab."
