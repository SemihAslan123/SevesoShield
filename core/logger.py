"""
SevesoShield — Logger structuré pour le pipeline multi-agents

Affiche les étapes du pipeline en console avec horodatage et codes couleurs ANSI.
Chaque agent rapporte son démarrage, sa durée et son statut (succès/échec).
"""

import sys
from datetime import datetime


# ──────────────────────────────────────────────
#  Codes ANSI (Windows 10+ avec VT100 activé)
# ──────────────────────────────────────────────
class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    # Agents
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    MAGENTA = "\033[95m"
    BLUE    = "\033[94m"
    WHITE   = "\033[97m"
    # Fond
    BG_RED  = "\033[41m"


def _enable_ansi_windows():
    """Active les séquences ANSI sur Windows et force UTF-8 sur stdout."""
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            pass
        # Forcer l'encodage UTF-8 sur stdout/stderr pour les emojis et caractères spéciaux
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


_enable_ansi_windows()


def _timestamp() -> str:
    return datetime.now().strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm


def _agent_color(agent_name: str) -> str:
    """Associe une couleur distincte à chaque agent."""
    colors = {
        "GeocoderAgent":        Color.CYAN,
        "MeteoAgent":           Color.BLUE,
        "SitesAgent":           Color.YELLOW,
        "EtablissementsAgent":  Color.MAGENTA,
        "PopulationAgent":      Color.WHITE,
        "SyntheseAgent":        Color.GREEN,
        "ManagerAgent":         Color.BOLD,
    }
    return colors.get(agent_name, Color.WHITE)


# ──────────────────────────────────────────────
#  API publique
# ──────────────────────────────────────────────

def log_pipeline_start(query: str):
    """Annonce le démarrage du pipeline."""
    print()
    print(f"{Color.BOLD}{'=' * 60}{Color.RESET}")
    print(f"{Color.BOLD}  SevesoShield -- Pipeline Multi-Agents{Color.RESET}")
    print(f"{Color.BOLD}{'=' * 60}{Color.RESET}")
    print(f"  {Color.DIM}[{_timestamp()}]{Color.RESET} Requete : {Color.WHITE}{query}{Color.RESET}")
    print(f"{Color.DIM}{'-' * 60}{Color.RESET}")


def log_agent_start(agent_name: str, detail: str = ""):
    """Indique qu'un agent démarre."""
    color = _agent_color(agent_name)
    detail_str = f" {Color.DIM}({detail}){Color.RESET}" if detail else ""
    print(f"  {Color.DIM}[{_timestamp()}]{Color.RESET} {color}>> {agent_name}{Color.RESET}{detail_str}")


def log_agent_success(agent_name: str, duration_ms: int, detail: str = ""):
    """Indique qu'un agent s'est terminé avec succès."""
    color = _agent_color(agent_name)
    detail_str = f" -- {Color.DIM}{detail}{Color.RESET}" if detail else ""
    print(f"  {Color.DIM}[{_timestamp()}]{Color.RESET} {Color.GREEN}OK {agent_name}{Color.RESET} "
          f"{Color.DIM}({duration_ms} ms){Color.RESET}{detail_str}")


def log_agent_failure(agent_name: str, duration_ms: int, error: str):
    """Indique qu'un agent a échoué (mode dégradé — le pipeline continue)."""
    print(f"  {Color.DIM}[{_timestamp()}]{Color.RESET} {Color.RED}ERR {agent_name}{Color.RESET} "
          f"{Color.DIM}({duration_ms} ms){Color.RESET} -- {Color.YELLOW}Mode degrade : {error}{Color.RESET}")


def log_parallel_start(agents: list):
    """Annonce le lancement des agents en parallèle."""
    names = ", ".join(agents)
    print(f"  {Color.DIM}[{_timestamp()}]{Color.RESET} {Color.CYAN}[//] Parallele :{Color.RESET} {Color.DIM}{names}{Color.RESET}")


def log_pipeline_end(total_ms: int, success: bool):
    """Annonce la fin du pipeline."""
    print(f"{Color.DIM}{'-' * 60}{Color.RESET}")
    status = f"{Color.GREEN}OK Succes{Color.RESET}" if success else f"{Color.RED}ERR Echec partiel{Color.RESET}"
    print(f"  {Color.DIM}[{_timestamp()}]{Color.RESET} Pipeline termine -- {status} {Color.DIM}({total_ms} ms){Color.RESET}")
    print(f"{Color.BOLD}{'=' * 60}{Color.RESET}")
    print()


def log_info(message: str):
    """Message d'information générique."""
    print(f"  {Color.DIM}[{_timestamp()}] {message}{Color.RESET}")


def log_section(title: str):
    """Séparateur de section."""
    print(f"\n{Color.DIM}{'-' * 60}{Color.RESET}")
    print(f"  {Color.BOLD}{title}{Color.RESET}")
    print(f"{Color.DIM}{'-' * 60}{Color.RESET}")
