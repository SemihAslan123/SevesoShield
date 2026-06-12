"""
SevesoShield — Agent Manager (Orchestrateur Central)

Rôle : Point d'entrée du pipeline multi-agents. Orchestre l'exécution des agents
       dans un ordre déterministe et logique :

  [1] GeocoderAgent     → Coordonnées GPS (séquentiel, bloquant)
  [2] MeteoAgent        ┐
      SitesAgent        ├─ Parallèle (ThreadPoolExecutor) — indépendants
      EtablissementsAgent│
      PopulationAgent   ┘
  [3] SyntheseAgent     → Synthèse finale Markdown

Le Manager assure la résilience (mode dégradé) : si un agent échoue,
le pipeline continue avec les données disponibles.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents.geocoder_agent import GeocoderAgent
from agents.meteo_agent import MeteoAgent
from agents.sites_agent import SitesAgent
from agents.etablissements_agent import EtablissementsAgent
from agents.population_agent import PopulationAgent
from agents.synthese_agent import SyntheseAgent
from core.schemas import AgentInput, AgentOutput, PipelineResult
from core import logger


class ManagerAgent:
    """
    Orchestrateur central du pipeline SevesoShield.
    
    Usage :
        manager = ManagerAgent()
        result = manager.run("Analyse un incident industriel à Tavaux")
        print(result.synthese.data["markdown"])
    """

    def __init__(self):
        self._geocoder = GeocoderAgent()
        self._meteo = MeteoAgent()
        self._sites = SitesAgent()
        self._etablissements = EtablissementsAgent()
        self._population = PopulationAgent()
        self._synthese = SyntheseAgent()

    def run(self, query: str, lat: float = None, lon: float = None,
            city: str = None, radius: int = 5000) -> PipelineResult:
        """
        Exécute le pipeline complet de manière déterministe.
        
        Args:
            query:  Question ou description de l'incident (texte libre).
            lat:    Latitude GPS (optionnel — si fourni, passe le géocodage).
            lon:    Longitude GPS (optionnel — si fourni, passe le géocodage).
            city:   Nom de commune (optionnel — extrait de query si absent).
            radius: Rayon de recherche en mètres (défaut : 5000).
            
        Returns:
            PipelineResult avec tous les outputs et la synthèse finale.
        """
        t_pipeline_start = time.time()

        logger.log_pipeline_start(query)

        result = PipelineResult(query=query, city=city, lat=lat, lon=lon)

        # ── ÉTAPE 1 : GÉOCODAGE ─────────────────────────────────────────
        # Séquentiel — toutes les étapes suivantes dépendent de lat/lon

        if lat is not None and lon is not None:
            # Coordonnées fournies directement → on crée un output synthétique
            logger.log_info("Coordonnées GPS fournies directement — étape de géocodage ignorée.")
            result.geocoder = AgentOutput(
                agent_name="GeocoderAgent",
                success=True,
                data={"results": [{"latitude": lat, "longitude": lon, "city": city or "", "postcode": "", "score": 1.0}]},
                duration_ms=0
            )
            result.lat = lat
            result.lon = lon
        else:
            inp_geo = AgentInput(query=query, city=city, radius=radius)
            result.geocoder = self._geocoder.run(inp_geo)

            if not result.geocoder.success:
                # Sans coordonnées, le pipeline est bloqué
                logger.log_pipeline_end(int((time.time() - t_pipeline_start) * 1000), success=False)
                result.success = False
                result.total_duration_ms = int((time.time() - t_pipeline_start) * 1000)
                return result

            result.lat, result.lon = self._geocoder.extract_coordinates(result.geocoder.data)
            result.city = self._geocoder.extract_city(result.geocoder.data) or city

        # ── ÉTAPE 2 : AGENTS PARALLÈLES ────────────────────────────────
        # Météo, Sites, Établissements et Population sont indépendants
        # → Exécutés simultanément pour réduire le temps total

        inp_parallel = AgentInput(
            query=query,
            city=result.city,
            lat=result.lat,
            lon=result.lon,
            radius=radius
        )

        parallel_agents = {
            "meteo":         (self._meteo, inp_parallel),
            "sites":         (self._sites, inp_parallel),
            "etablissements": (self._etablissements, inp_parallel),
            "population":    (self._population, inp_parallel),
        }

        logger.log_parallel_start(["MeteoAgent", "SitesAgent", "EtablissementsAgent", "PopulationAgent"])

        parallel_results = {}
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {
                executor.submit(agent.run, inp): key
                for key, (agent, inp) in parallel_agents.items()
            }
            for future in as_completed(futures):
                key = futures[future]
                try:
                    parallel_results[key] = future.result()
                except Exception as exc:
                    # Cas extrême — BaseAgent.run() capture déjà les exceptions
                    parallel_results[key] = AgentOutput(
                        agent_name=key,
                        success=False,
                        error=str(exc)
                    )

        result.meteo = parallel_results.get("meteo")
        result.sites = parallel_results.get("sites")
        result.etablissements = parallel_results.get("etablissements")
        result.population = parallel_results.get("population")

        # ── ÉTAPE 3 : SYNTHÈSE ──────────────────────────────────────────
        result.synthese = self._synthese.synthesize(
            query=query,
            geocoder_out=result.geocoder,
            meteo_out=result.meteo,
            sites_out=result.sites,
            etab_out=result.etablissements,
            pop_out=result.population,
        )

        # ── FIN DU PIPELINE ─────────────────────────────────────────────
        result.total_duration_ms = int((time.time() - t_pipeline_start) * 1000)
        result.success = result.synthese.success

        logger.log_pipeline_end(result.total_duration_ms, result.success)

        return result
