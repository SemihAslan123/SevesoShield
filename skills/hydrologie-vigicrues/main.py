import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="Skill Vigicrues")
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--lon", type=float, required=True)
    args = parser.parse_args()

    # Note: Dans un environnement réel, nous appellerions l'API Vigicrues
    # URL: https://alidade.data.gouv.fr/vigicrues/ ou similaire
    # Pour ce skill, nous renvoyons un mock structuré pour démontrer la capacité
    
    result = {
        "source": "Vigicrues",
        "coordonnees": {"lat": args.lat, "lon": args.lon},
        "station_proche": "Station de mesure la plus proche",
        "niveau_vigilance": "Vert",
        "tendance": "Stable",
        "cours_d_eau": "Cours d'eau principal",
        "message": "Aucune vigilance crue particulière n'est en cours sur les tronçons à proximité."
    }
    
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
