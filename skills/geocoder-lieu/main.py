import argparse
import json
import sys
import requests

def geocode(query: str, limit: int = 3):
    """
    Appelle l'API de géocodage de la Géoplateforme (API Adresse) pour chercher une adresse ou un lieu.
    """
    url = "https://api-adresse.data.gouv.fr/search/"
    params = {
        "q": query,
        "limit": limit
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "error": "Erreur réseau lors de l'appel à l'API de géocodage",
            "details": str(e)
        }), file=sys.stderr)
        sys.exit(1)

    features = data.get("features", [])
    
    if not features:
        return {
            "query": query,
            "results": [],
            "message": "Aucun résultat trouvé pour cette recherche."
        }

    results = []
    for feature in features:
        props = feature.get("properties", {})
        coords = feature.get("geometry", {}).get("coordinates", [0, 0])
        
        results.append({
            "label": props.get("label", ""),
            "latitude": coords[1],
            "longitude": coords[0],
            "city": props.get("city", ""),
            "postcode": props.get("postcode", ""),
            "score": props.get("score", 0.0)
        })

    return {
        "query": query,
        "results": results
    }

def main():
    parser = argparse.ArgumentParser(description="Géocoder une adresse, un lieu ou une commune.")
    parser.add_argument("--query", "-q", type=str, required=True, help="Lieu à rechercher (ex: Tavaux)")
    parser.add_argument("--limit", "-l", type=int, default=3, help="Nombre max de résultats (défaut: 3)")
    
    args = parser.parse_args()
    
    result = geocode(args.query, args.limit)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
