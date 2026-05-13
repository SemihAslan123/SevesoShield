import argparse
import json
import sys
import requests

def get_commune_info(lat: float = None, lon: float = None, city: str = None):
    """
    Récupère les informations d'une commune via l'API geo.api.gouv.fr
    """
    base_url = "https://geo.api.gouv.fr/communes"
    params = {
        "fields": "nom,code,codesPostaux,population,departement,region,centre",
        "format": "json",
        "geometry": "centre"
    }
    
    if lat is not None and lon is not None:
        params["lat"] = lat
        params["lon"] = lon
    elif city:
        params["nom"] = city
        params["boost"] = "population"
        params["limit"] = 1
    else:
        return {"error": "Vous devez fournir (lat, lon) ou city."}
        
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "error": "Erreur réseau lors de l'appel à geo.api.gouv.fr",
            "details": str(e)
        }), file=sys.stderr)
        sys.exit(1)

    if not data:
        return {
            "error": "Aucune commune trouvée pour cette recherche."
        }
        
    # L'API retourne une liste
    commune = data[0]
    
    # Extraire les coordonnées centrales de la commune si lat/lon n'étaient pas fournis
    center_coords = commune.get("centre", {}).get("coordinates", [lon, lat])
    # geojson: [longitude, latitude]
    
    return {
        "city": commune.get("nom", ""),
        "insee_code": commune.get("code", ""),
        "postcode": commune.get("codesPostaux", [""])[0] if commune.get("codesPostaux") else "",
        "population": commune.get("population", "Non renseignée"),
        "department": commune.get("departement", {}).get("nom", ""),
        "region": commune.get("region", {}).get("nom", ""),
        "center": {
            "latitude": lat if lat is not None else center_coords[1],
            "longitude": lon if lon is not None else center_coords[0]
        },
        "source": "geo.api.gouv.fr"
    }

def main():
    parser = argparse.ArgumentParser(description="Récupérer le contexte démographique d'une commune.")
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    parser.add_argument("--city", type=str, help="Nom de la commune")
    
    args = parser.parse_args()
    
    if (args.lat is None or args.lon is None) and not args.city:
        print(json.dumps({"error": "Veuillez fournir --lat et --lon, OU --city"}), file=sys.stderr)
        sys.exit(1)
        
    result = get_commune_info(args.lat, args.lon, args.city)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
