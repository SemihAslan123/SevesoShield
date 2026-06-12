"""
SevesoShield — Agent Météo et Vent

Rôle : Récupérer les conditions météo locales et interpréter la direction du vent.
Source : Open-Meteo (open-meteo.com)
Skill d'origine : skills/meteo-vent-local/main.py
"""

import sys
import os
import importlib.util

# ──────────────────────────────────────────────
#  Import dynamique du skill (dossier avec tiret = non importable directement)
# ──────────────────────────────────────────────
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_PATH = os.path.join(_ROOT, "skills", "meteo-vent-local", "main.py")

_spec = importlib.util.spec_from_file_location("meteo_vent_local", _SKILL_PATH)
_meteo_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_meteo_module)

from agents.base_agent import BaseAgent
from core.schemas import AgentInput


class MeteoAgent(BaseAgent):
    """
    Agent météo et vent.
    
    Entrée  : AgentInput.lat, AgentInput.lon (coordonnées GPS)
    Sortie  : { location, current: {temperature, wind_speed, wind_direction, wind_gusts},
                wind_interpretation: {wind_from_label, indicative_watch_towards_label, ...} }
    """

    name = "MeteoAgent"

    def _execute(self, inp: AgentInput) -> dict:
        if inp.lat is None or inp.lon is None:
            raise ValueError("Coordonnées GPS manquantes pour MeteoAgent")

        result = _meteo_module.get_weather(inp.lat, inp.lon)

        if "error" in result:
            raise ValueError(result["error"])

        return result

    def _start_detail(self, inp: AgentInput) -> str:
        if inp.lat and inp.lon:
            return f"lat={inp.lat:.4f}, lon={inp.lon:.4f}"
        return ""

    def _success_detail(self, data: dict) -> str:
        current = data.get("current", {})
        wind = data.get("wind_interpretation", {})
        temp = current.get("temperature_2m", "?")
        speed = current.get("wind_speed_10m", "?")
        direction = wind.get("wind_from_label", "?")
        return f"{temp}°C, vent {speed} km/h depuis {direction}"
