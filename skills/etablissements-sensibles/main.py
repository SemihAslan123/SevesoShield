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

def get_sensitive_facilities(lat: float, lon: float, radius: int):
    """
    Recherche les établissements sensibles via l'API Overpass (OpenStreetMap).
    """
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Requête Overpass QL
    # On cherche les nœuds (node), chemins (way) et relations (relation) avec des tags spécifiques
    tags = [
        "amenity=school", "amenity=kindergarten", "amenity=childcare",
        "amenity=hospital", "amenity=clinic", "amenity=doctors",
        "amenity=pharmacy", "amenity=nursing_home", "amenity=social_facility",
        "amenity=townhall", "amenity=fire_station", "amenity=police"
    ]
    
    query_parts = []
    for tag in tags:
        key, value = tag.split("=")
        query_parts.append(f'node["{key}"="{value}"](around:{radius},{lat},{lon});')
        query_parts.append(f'way["{key}"="{value}"](around:{radius},{lat},{lon});')
        query_parts.append(f'relation["{key}"="{value}"](around:{radius},{lat},{lon});')
        
    overpass_query = f"""
    [out:json][timeout:25];
    (
      {''.join(query_parts)}
    );
    out center;
    """
    
    try:
        response = requests.post(overpass_url, data={'data': overpass_query}, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "error": "Erreur réseau lors de l'appel à Overpass API",
            "details": str(e)
        }), file=sys.stderr)
        sys.exit(1)

    elements = data.get("elements", [])
    
    items = []
    categories_count = {}
    
    for el in elements:
        # Les noeuds ont lat/lon directement, les ways/relations ont center.lat/center.lon avec `out center`
        item_lat = el.get("lat") or el.get("center", {}).get("lat")
        item_lon = el.get("lon") or el.get("center", {}).get("lon")
        
        if not item_lat or not item_lon:
            continue
            
        tags_dict = el.get("tags", {})
        name = tags_dict.get("name", "Inconnu")
        category = tags_dict.get("amenity", "unknown")
        
        distance = int(haversine_distance(lat, lon, item_lat, item_lon))
        
        items.append({
            "name": name,
            "category": category,
            "latitude": item_lat,
            "longitude": item_lon,
            "distance_m": distance,
            "source": "OpenStreetMap"
        })
        
        categories_count[category] = categories_count.get(category, 0) + 1

    # Trier par distance
    items.sort(key=lambda x: x["distance_m"])

    return {
        "center": {
            "latitude": lat,
            "longitude": lon
        },
        "radius_m": radius,
        "count": len(items),
        "categories": categories_count,
        "items": items,
        "warning": "Les données OpenStreetMap peuvent être incomplètes et doivent être vérifiées."
    }

def main():
    parser = argparse.ArgumentParser(description="Identifier les établissements sensibles autour d'un point.")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--radius", type=int, default=3000, help="Rayon de recherche en mètres (défaut: 3000)")
    
    args = parser.parse_args()
    
    result = get_sensitive_facilities(args.lat, args.lon, args.radius)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
