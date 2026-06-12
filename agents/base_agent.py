"""
SevesoShield — Classe de base abstraite pour tous les agents

Chaque agent hérite de BaseAgent et implémente la méthode `_execute()`.
BaseAgent gère automatiquement :
  - Le timing (durée d'exécution en ms)
  - La capture des exceptions (mode dégradé)
  - Le logging structuré (via core.logger)
"""

import time
from abc import ABC, abstractmethod

from core.schemas import AgentInput, AgentOutput
from core import logger


class BaseAgent(ABC):
    """
    Classe abstraite commune à tous les agents SevesoShield.
    
    Usage :
        class MonAgent(BaseAgent):
            name = "MonAgent"
            
            def _execute(self, inp: AgentInput) -> dict:
                # Logique métier ici
                return {"result": "..."}
    """

    # À surcharger dans chaque sous-classe
    name: str = "BaseAgent"

    def run(self, inp: AgentInput) -> AgentOutput:
        """
        Exécute l'agent de manière sécurisée.
        
        - Démarre le timer
        - Appelle _execute()
        - Capture toute exception → mode dégradé (success=False)
        - Retourne un AgentOutput normalisé
        """
        logger.log_agent_start(self.name, self._start_detail(inp))
        t_start = time.time()

        try:
            data = self._execute(inp)
            duration_ms = int((time.time() - t_start) * 1000)
            output = AgentOutput(
                agent_name=self.name,
                success=True,
                data=data,
                duration_ms=duration_ms
            )
            logger.log_agent_success(self.name, duration_ms, self._success_detail(data))
            return output

        except (Exception, SystemExit) as exc:
            duration_ms = int((time.time() - t_start) * 1000)
            error_msg = f"{type(exc).__name__}: {exc}"
            output = AgentOutput(
                agent_name=self.name,
                success=False,
                data={},
                error=error_msg,
                duration_ms=duration_ms
            )
            logger.log_agent_failure(self.name, duration_ms, error_msg)
            return output

    @abstractmethod
    def _execute(self, inp: AgentInput) -> dict:
        """
        Logique métier de l'agent.
        Doit retourner un dictionnaire JSON-sérialisable.
        En cas d'erreur, lever une exception — BaseAgent.run() la capture.
        """
        ...

    def _start_detail(self, inp: AgentInput) -> str:
        """Message affiché au démarrage de l'agent (optionnel)."""
        return ""

    def _success_detail(self, data: dict) -> str:
        """Message affiché en cas de succès (optionnel, résumé du résultat)."""
        return ""
