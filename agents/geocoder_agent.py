"""
SevesoShield — Agent Geocoder

Rôle : Transformer une adresse ou un nom de commune en coordonnées GPS (lat, lon).
Source : API Adresse / Base Adresse Nationale (api-adresse.data.gouv.fr)
Skill d'origine : skills/geocoder-lieu/main.py

Cet agent est TOUJOURS le premier du pipeline.
Son résultat (lat, lon) est injecté dans l'AgentInput de tous les agents suivants.
"""

import os
import importlib.util

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SKILL_PATH = os.path.join(_ROOT, "skills", "geocoder-lieu", "main.py")

_spec = importlib.util.spec_from_file_location("geocoder_lieu", _SKILL_PATH)
_geocoder_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_geocoder_module)

from agents.base_agent import BaseAgent
from core.schemas import AgentInput


class GeocoderAgent(BaseAgent):
    """
    Agent de géocodage.
    
    Entrée  : AgentInput.city ou AgentInput.query (nom de commune/adresse)
    Sortie  : { query, results: [{label, latitude, longitude, city, postcode, score}] }
    """

    name = "GeocoderAgent"

    def _execute(self, inp: AgentInput) -> dict:
        # Priorité : city > extraction depuis query naturelle
        if inp.city:
            search_query = inp.city
        else:
            # Essayer d'extraire un lieu depuis la query en langage naturel
            # en cherchant les mots après des prépositions communes
            search_query = self._extract_location_from_query(inp.query)

        result = _geocoder_module.geocode(search_query, limit=3)

        if not result.get("results"):
            # Tentative de repli : essayer la query brute tronquée
            if search_query != inp.query:
                result = _geocoder_module.geocode(inp.query, limit=3)
            if not result.get("results"):
                raise ValueError(f"Aucun résultat de géocodage pour : '{search_query}'")

        return result

    @staticmethod
    def _extract_location_from_query(query: str) -> str:
        """
        Tente d'extraire le nom de lieu depuis une question en langage naturel.
        
        Exemples :
          "Analyse un incident à Tavaux" → "Tavaux"
          "Incident industriel autour de Pierre-Bénite" → "Pierre-Bénite"
          "Tavaux" → "Tavaux" (déjà un lieu simple)
        """
        import re

        # Prépositions spatiales françaises courantes
        prepositions = [
            r'\bde\s+la\s+commune\s+de\b',
            r'\bautour\s+de\b',
            r'\b\u00e0\s+la\s+commune\s+de\b',
            r'\bdans\s+la\s+commune\s+de\b',
            r'\bpour\s+la\s+commune\s+de\b',
            r'\bpr\u00e8s\s+de\b',
            r'\bau\s+niveau\s+de\b',
            r'\bincident\s+\u00e0\b',
            r'\bsur\s+la\s+commune\s+de\b',
            r'\b\u00e0\b',
            r'\bde\b',
        ]

        for pattern in prepositions:
            match = re.search(pattern + r'\s+(.+?)(?:\s*[\(\.,]|$)', query, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                # Nettoyer les parenthèses et numéros de département
                location = re.sub(r'\s*\(\d+\)\s*$', '', location)
                if location and len(location) > 1:
                    return location

        # Si aucune préposition trouvée, retourner la query telle quelle (peut être un lieu simple)
        return query

    def _start_detail(self, inp: AgentInput) -> str:
        return f"query='{inp.city or inp.query}'"

    def _success_detail(self, data: dict) -> str:
        if data.get("results"):
            r = data["results"][0]
            return f"→ {r.get('city', '?')} [{r.get('latitude'):.4f}, {r.get('longitude'):.4f}]"
        return ""

    def extract_coordinates(self, data: dict) -> tuple:
        """
        Extrait (lat, lon) du premier résultat de géocodage.
        Retourne (None, None) si aucun résultat.
        """
        results = data.get("results", [])
        if results:
            return results[0]["latitude"], results[0]["longitude"]
        return None, None

    def extract_city(self, data: dict) -> str:
        """Extrait le nom de commune du premier résultat."""
        results = data.get("results", [])
        if results:
            return results[0].get("city", "")
        return ""
