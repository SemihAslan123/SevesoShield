"""
SevesoShield — Schémas de communication inter-agents

Ce module définit les contrats de données (dataclasses) utilisés par tous les agents.
Chaque agent reçoit un AgentInput et retourne un AgentOutput.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AgentInput:
    """
    Entrée standardisée pour tous les agents SevesoShield.
    
    Attributes:
        query:   Question ou description originale de l'utilisateur.
        city:    Nom de la commune cible (optionnel si lat/lon fournis).
        lat:     Latitude GPS (renseignée après l'étape de géocodage).
        lon:     Longitude GPS (renseignée après l'étape de géocodage).
        radius:  Rayon de recherche en mètres (défaut : 5 km).
    """
    query: str
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    radius: int = 5000


@dataclass
class AgentOutput:
    """
    Sortie standardisée retournée par tous les agents SevesoShield.
    
    Attributes:
        agent_name:  Identifiant de l'agent qui a produit ce résultat.
        success:     True si l'exécution s'est déroulée sans erreur critique.
        data:        Dictionnaire JSON structuré — résultat de l'agent.
        error:       Message d'erreur en cas d'échec (None si succès).
        duration_ms: Temps d'exécution en millisecondes.
    """
    agent_name: str
    success: bool
    data: dict = field(default_factory=dict)
    error: Optional[str] = None
    duration_ms: int = 0


@dataclass
class PipelineResult:
    """
    Résultat agrégé du pipeline complet, retourné par le ManagerAgent.
    
    Attributes:
        query:         Question originale de l'utilisateur.
        city:          Commune identifiée.
        lat:           Latitude GPS.
        lon:           Longitude GPS.
        geocoder:      Résultat de l'agent geocoder.
        meteo:         Résultat de l'agent météo.
        sites:         Résultat de l'agent sites industriels.
        etablissements: Résultat de l'agent établissements sensibles.
        population:    Résultat de l'agent contexte population.
        synthese:      Texte de la synthèse finale (Markdown).
        total_duration_ms: Durée totale du pipeline.
        success:       True si au moins les données minimales sont disponibles.
    """
    query: str
    city: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None
    geocoder: Optional[AgentOutput] = None
    meteo: Optional[AgentOutput] = None
    sites: Optional[AgentOutput] = None
    etablissements: Optional[AgentOutput] = None
    population: Optional[AgentOutput] = None
    synthese: Optional[AgentOutput] = None
    total_duration_ms: int = 0
    success: bool = False
