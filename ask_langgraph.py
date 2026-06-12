"""
SevesoShield v2.0 — Point d'entrée via LangGraph (Workflow)

Usage :
    python ask_langgraph.py "Analyse un incident industriel à Tavaux"
    python ask_langgraph.py --fake-step-1 --lat 47.04 --lon 5.41
"""

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.workflow_langgraph import LangGraphManager
from core import logger

def parse_args():
    parser = argparse.ArgumentParser(description="🛡️ SevesoShield (Version LangGraph)")
    parser.add_argument("query", nargs="?", default="Analyse d'incident", help="Question")
    parser.add_argument("--city", "-c", type=str, help="Nom de la commune")
    parser.add_argument("--lat", type=float, help="Latitude GPS")
    parser.add_argument("--lon", type=float, help="Longitude GPS")
    parser.add_argument("--fake-step-1", action="store_true", help="Force le bypass de l'étape de géocodage")
    return parser.parse_args()

def main():
    args = parse_args()

    # Si on veut faker l'étape 1 sans donner les coords, on en met par défaut
    lat = args.lat
    lon = args.lon
    if args.fake_step_1 and not lat and not lon:
        print("💡 Mode --fake-step-1 activé : injection des coordonnées de Tavaux par défaut.")
        lat = 47.0435
        lon = 5.4150

    manager = LangGraphManager()
    
    print("\n🚀 [Lancement du Workflow LangGraph]")
    result = manager.run(
        query=args.query,
        lat=lat,
        lon=lon,
        city=args.city
    )

    if result.synthese and result.synthese.success:
        markdown = result.synthese.data.get("markdown", "")
        logger.log_section("SYNTHÈSE OPÉRATIONNELLE (LANGGRAPH)")
        print(markdown)
    else:
        print("\n❌ Le workflow LangGraph a échoué.")
        sys.exit(1)

if __name__ == "__main__":
    main()
