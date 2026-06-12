import time
from typing import TypedDict, Optional, Dict, Any

from langgraph.graph import StateGraph, START, END

from core.schemas import AgentInput, AgentOutput, PipelineResult
from core import logger

# Importation de nos agents existants
from agents.geocoder_agent import GeocoderAgent
from agents.meteo_agent import MeteoAgent
from agents.sites_agent import SitesAgent
from agents.etablissements_agent import EtablissementsAgent
from agents.population_agent import PopulationAgent
from agents.synthese_agent import SyntheseAgent

class WorkflowState(TypedDict):
    """L'état partagé entre tous les noeuds du graphe."""
    query: str
    city: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    radius: int
    
    geocoder: Optional[AgentOutput]
    meteo: Optional[AgentOutput]
    sites: Optional[AgentOutput]
    etablissements: Optional[AgentOutput]
    population: Optional[AgentOutput]
    synthese: Optional[AgentOutput]
    
    success: bool
    total_duration_ms: int
    start_time: float


class LangGraphManager:
    """Orchestrateur basé sur LangGraph."""
    
    def __init__(self):
        self._geocoder = GeocoderAgent()
        self._meteo = MeteoAgent()
        self._sites = SitesAgent()
        self._etablissements = EtablissementsAgent()
        self._population = PopulationAgent()
        self._synthese = SyntheseAgent()
        
        self.app = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(WorkflowState)
        
        # Ajout des noeuds
        workflow.add_node("geocoder", self.node_geocoder)
        workflow.add_node("meteo", self.node_meteo)
        workflow.add_node("sites", self.node_sites)
        workflow.add_node("etablissements", self.node_etablissements)
        workflow.add_node("population", self.node_population)
        workflow.add_node("synthese", self.node_synthese)
        
        # Définition du routage (Edges)
        workflow.add_edge(START, "geocoder")
        
        # Routage conditionnel après geocoder
        workflow.add_conditional_edges(
            "geocoder",
            self.route_after_geocoder
        )
        
        # Les 4 agents parallèles convergent vers la synthèse
        workflow.add_edge("meteo", "synthese")
        workflow.add_edge("sites", "synthese")
        workflow.add_edge("etablissements", "synthese")
        workflow.add_edge("population", "synthese")
        
        workflow.add_edge("synthese", END)
        
        # Compilation du graphe
        return workflow.compile()

    def node_geocoder(self, state: WorkflowState) -> dict:
        if state.get("lat") is not None and state.get("lon") is not None:
            logger.log_info("Coordonnées GPS fournies directement — étape de géocodage ignorée (Fake étape 1).")
            out = AgentOutput(
                agent_name="GeocoderAgent",
                success=True,
                data={"results": [{"latitude": state["lat"], "longitude": state["lon"], "city": state.get("city", ""), "postcode": "", "score": 1.0}]},
                duration_ms=0
            )
            return {"geocoder": out}

        inp = AgentInput(query=state["query"], city=state.get("city"), radius=state.get("radius", 5000))
        out = self._geocoder.run(inp)
        
        updates = {"geocoder": out}
        if out.success:
            updates["lat"], updates["lon"] = self._geocoder.extract_coordinates(out.data)
            updates["city"] = self._geocoder.extract_city(out.data) or state.get("city")
            
        return updates

    def route_after_geocoder(self, state: WorkflowState) -> list[str]:
        if state.get("geocoder") and state["geocoder"].success:
            logger.log_parallel_start(["MeteoAgent", "SitesAgent", "EtablissementsAgent", "PopulationAgent"])
            return ["meteo", "sites", "etablissements", "population"]
        return [END]

    def _build_agent_input(self, state: WorkflowState) -> AgentInput:
        return AgentInput(
            query=state["query"],
            city=state.get("city"),
            lat=state.get("lat"),
            lon=state.get("lon"),
            radius=state.get("radius", 5000)
        )

    def node_meteo(self, state: WorkflowState) -> dict:
        inp = self._build_agent_input(state)
        return {"meteo": self._meteo.run(inp)}

    def node_sites(self, state: WorkflowState) -> dict:
        inp = self._build_agent_input(state)
        return {"sites": self._sites.run(inp)}

    def node_etablissements(self, state: WorkflowState) -> dict:
        inp = self._build_agent_input(state)
        return {"etablissements": self._etablissements.run(inp)}

    def node_population(self, state: WorkflowState) -> dict:
        inp = self._build_agent_input(state)
        return {"population": self._population.run(inp)}

    def node_synthese(self, state: WorkflowState) -> dict:
        out = self._synthese.synthesize(
            query=state["query"],
            geocoder_out=state.get("geocoder"),
            meteo_out=state.get("meteo"),
            sites_out=state.get("sites"),
            etab_out=state.get("etablissements"),
            pop_out=state.get("population")
        )
        duration = int((time.time() - state["start_time"]) * 1000)
        success = out.success
        logger.log_pipeline_end(duration, success)
        return {"synthese": out, "total_duration_ms": duration, "success": success}

    def run(self, query: str, lat: float = None, lon: float = None, city: str = None, radius: int = 5000) -> PipelineResult:
        logger.log_pipeline_start(query)
        
        initial_state = {
            "query": query,
            "city": city,
            "lat": lat,
            "lon": lon,
            "radius": radius,
            "start_time": time.time(),
            "success": False,
            "total_duration_ms": 0
        }
        
        final_state = self.app.invoke(initial_state)
        
        result = PipelineResult(
            query=final_state.get("query"),
            city=final_state.get("city"),
            lat=final_state.get("lat"),
            lon=final_state.get("lon"),
            geocoder=final_state.get("geocoder"),
            meteo=final_state.get("meteo"),
            sites=final_state.get("sites"),
            etablissements=final_state.get("etablissements"),
            population=final_state.get("population"),
            synthese=final_state.get("synthese"),
            total_duration_ms=final_state.get("total_duration_ms", 0),
            success=final_state.get("success", False)
        )
        return result
