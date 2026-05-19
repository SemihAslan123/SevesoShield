import argparse
import json
import sys
import requests
import math

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calcule la distance en mètres entre deux points GPS."""
    R = 6371000  # Rayon de la Terre en mètres
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def get_insee_code(city: str):
    """Récupère le code INSEE et les coordonnées d'une commune via l'API geo.api.gouv.fr"""
    url = "https://geo.api.gouv.fr/communes"
    try:
        params = {"nom": city, "fields": "centre", "boost": "population", "limit": 1}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data:
            coords = data[0].get("centre", {}).get("coordinates", [0, 0])
            return data[0].get("code"), coords[1], coords[0]
    except Exception:
        pass
    return None, None, None

def get_icpe_sites(lat: float, lon: float, radius: int):
    """
    Recherche les sites ICPE / SEVESO autour d'un point via l'API Géorisques.
    """
    url = "https://georisques.gouv.fr/api/v1/installations_classees"
    
    # L'API Géorisques accepte un paramètre latlon au format "longitude,latitude"
    # Le rayon est en mètres
    params = {
        "latlon": f"{lon},{lat}",
        "rayon": radius,
        "page": 1,
        "page_size": 50
    }
    
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "error": "Erreur réseau lors de l'appel à Géorisques",
            "details": str(e)
        }), file=sys.stderr)
        sys.exit(1)

    records = data.get("data", [])
    sites = []
    
    for record in records:
        site_lon = record.get("longitude")
        site_lat = record.get("latitude")
        
        distance = None
        if site_lat is not None and site_lon is not None:
            distance = int(haversine_distance(lat, lon, site_lat, site_lon))
            
        sites.append({
            "name": record.get("raisonSociale") or record.get("nomUsuel", "Inconnu"),
            "city": record.get("commune", "Inconnue"),
            "address": record.get("adresse1", ""),
            "seveso_status": record.get("statutSeveso", "Non renseigné"),
            "icpe_regime": record.get("regime", "Inconnu"),
            "activity_status": record.get("etatActivite", "Inconnu"),
            "latitude": site_lat,
            "longitude": site_lon,
            "distance_m": distance,
            "source": "Géorisques"
        })

    if sites:
        # Trier par distance si possible
        sites.sort(key=lambda x: x["distance_m"] if x["distance_m"] is not None else float('inf'))

    return {
        "center": {
            "latitude": lat,
            "longitude": lon
        },
        "radius_m": radius,
        "count": len(sites),
        "sites": sites,
        "warning": "Les données doivent être vérifiées auprès des sources officielles (DREAL, Préfecture)."
    }

def main():
    parser = argparse.ArgumentParser(description="Rechercher des sites industriels à risque (ICPE/SEVESO).")
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    parser.add_argument("--city", type=str, help="Nom de la commune")
    parser.add_argument("--radius", type=int, default=10000, help="Rayon en mètres (défaut: 10000)")
    
    args = parser.parse_args()
    
    lat, lon = args.lat, args.lon
    
    if args.city and (lat is None or lon is None):
        _, city_lat, city_lon = get_insee_code(args.city)
        if city_lat is None:
            print(json.dumps({"error": f"Commune '{args.city}' introuvable."}), file=sys.stderr)
            sys.exit(1)
        lat, lon = city_lat, city_lon
        
    if lat is None or lon is None:
        print(json.dumps({"error": "Veuillez fournir --lat et --lon, OU --city"}), file=sys.stderr)
        sys.exit(1)
        
    result = get_icpe_sites(lat, lon, args.radius)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
