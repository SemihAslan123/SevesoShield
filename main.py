"""
SevesoShield v2.0 — Point d'entrée CLI du pipeline multi-agents

Usage :
    python main.py "Analyse un incident industriel à Tavaux"
    python main.py --city "Tavaux" --radius 5000
    python main.py --lat 47.04 --lon 5.41
    python main.py --city "Pierre-Bénite" --output rapport.md

Options :
    --city      Nom de la commune cible
    --lat       Latitude GPS (optionnel si --city fourni)
    --lon       Longitude GPS (optionnel si --city fourni)
    --radius    Rayon de recherche en mètres (défaut : 5000)
    --output    Chemin du fichier Markdown de sortie (optionnel)
    --no-color  Désactive les couleurs ANSI (utile pour les pipes)
"""

import argparse
import sys
import os

# S'assurer que la racine du projet est dans le path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.manager_agent import ManagerAgent
from core import logger


def parse_args():
    parser = argparse.ArgumentParser(
        prog="SevesoShield",
        description="🛡️ SevesoShield v2.0 — Analyse autonome d'incident industriel (pipeline multi-agents)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python main.py "Analyse un incident industriel à Tavaux"
  python main.py --city "Tavaux" --radius 10000
  python main.py --lat 47.04 --lon 5.41 --output rapport.md
  python main.py --city "Pierre-Bénite" --no-color > rapport.txt
        """
    )

    # Argument positionnel optionnel (question en langage naturel)
    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Question en langage naturel (ex: 'Analyse un incident à Tavaux')"
    )

    # Options nommées
    parser.add_argument("--city", "-c", type=str, help="Nom de la commune cible")
    parser.add_argument("--lat", type=float, help="Latitude GPS")
    parser.add_argument("--lon", type=float, help="Longitude GPS")
    parser.add_argument("--radius", "-r", type=int, default=5000,
                        help="Rayon de recherche en mètres (défaut : 5000)")
    parser.add_argument("--output", "-o", type=str,
                        help="Fichier de sortie Markdown (ex: rapport.md)")
    parser.add_argument("--no-color", action="store_true",
                        help="Désactiver les couleurs ANSI")

    return parser.parse_args()


def build_query(args) -> str:
    """Construit la requête finale à partir des arguments CLI."""
    if args.query:
        return args.query
    if args.city:
        return f"Analyse d'incident industriel autour de la commune de {args.city}"
    if args.lat and args.lon:
        return f"Analyse d'incident industriel au point GPS ({args.lat}, {args.lon})"
    return "Analyse d'incident industriel"


def disable_colors():
    """Désactive toutes les séquences ANSI dans le logger."""
    from core import logger as _log
    _log.Color.RESET = _log.Color.BOLD = _log.Color.DIM = ""
    _log.Color.CYAN = _log.Color.GREEN = _log.Color.YELLOW = ""
    _log.Color.RED = _log.Color.MAGENTA = _log.Color.BLUE = ""
    _log.Color.WHITE = _log.Color.BG_RED = ""


def save_output(markdown: str, output_path: str):
    """Sauvegarde le rapport Markdown dans un fichier."""
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)
        print(f"\n  ✅ Rapport sauvegardé : {output_path}\n")
    except IOError as e:
        print(f"\n  ⚠️ Impossible de sauvegarder le rapport : {e}\n", file=sys.stderr)


def main():
    args = parse_args()

    # Validation des arguments
    if not args.query and not args.city and not (args.lat and args.lon):
        print("❌ Erreur : fournissez une question, --city, ou --lat/--lon")
        print("   Exemple : python main.py \"Incident à Tavaux\"")
        sys.exit(1)

    if (args.lat is None) != (args.lon is None):
        print("❌ Erreur : --lat et --lon doivent être fournis ensemble")
        sys.exit(1)

    # Désactiver les couleurs si demandé
    if args.no_color:
        disable_colors()

    # Construire la requête
    query = build_query(args)

    # Lancer le pipeline
    manager = ManagerAgent()
    result = manager.run(
        query=query,
        lat=args.lat,
        lon=args.lon,
        city=args.city,
        radius=args.radius
    )

    # Afficher la synthèse
    if result.synthese and result.synthese.success:
        markdown = result.synthese.data.get("markdown", "")
        logger.log_section("SYNTHÈSE OPÉRATIONNELLE")
        print(markdown)

        # Sauvegarder si demandé
        if args.output:
            save_output(markdown, args.output)
    else:
        print("\n❌ Le pipeline a échoué — impossible de générer la synthèse.")
        if result.geocoder and not result.geocoder.success:
            print(f"   Cause : {result.geocoder.error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
