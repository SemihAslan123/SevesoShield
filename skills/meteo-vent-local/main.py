import argparse
import json
import sys
import requests

def get_wind_label(degrees: float) -> str:
    """Convertit une direction en degrés en libellé cardinal (simplifié)."""
    val = int((degrees / 22.5) + .5)
    arr = ["Nord", "Nord-Nord-Est", "Nord-Est", "Est-Nord-Est", "Est", "Est-Sud-Est",
           "Sud-Est", "Sud-Sud-Est", "Sud", "Sud-Sud-Ouest", "Sud-Ouest", "Ouest-Sud-Ouest",
           "Ouest", "Ouest-Nord-Ouest", "Nord-Ouest", "Nord-Nord-Ouest"]
    return arr[(val % 16)]

def get_weather(lat: float, lon: float):
    """
    Récupère la météo locale et la direction du vent via Open-Meteo.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m"],
        "timezone": "auto"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        print(json.dumps({
            "error": "Erreur réseau lors de l'appel à Open-Meteo",
            "details": str(e)
        }), file=sys.stderr)
        sys.exit(1)

    current = data.get("current", {})
    if not current:
        return {
            "error": "Données météo non disponibles pour ces coordonnées."
        }
        
    wind_dir = current.get("wind_direction_10m", 0)
    # Règle de calcul pour la vigilance indicative : direction du vent + 180 modulo 360
    watch_dir = (wind_dir + 180) % 360
    
    wind_label = get_wind_label(wind_dir)
    watch_label = get_wind_label(watch_dir)

    return {
        "location": {
            "latitude": lat,
            "longitude": lon
        },
        "current": {
            "temperature_2m": current.get("temperature_2m"),
            "wind_speed_10m": current.get("wind_speed_10m"),
            "wind_direction_10m": wind_dir,
            "wind_gusts_10m": current.get("wind_gusts_10m")
        },
        "wind_interpretation": {
            "wind_from_degrees": wind_dir,
            "wind_from_label": wind_label,
            "indicative_watch_towards_degrees": watch_dir,
            "indicative_watch_towards_label": watch_label,
            "explanation": f"Le vent venant du/de {wind_label}, une vigilance indicative peut être portée vers {watch_label}."
        },
        "warning": "Cette interprétation est simplifiée et ne constitue pas une modélisation de dispersion. Ne remplace pas les outils officiels."
    }

def main():
    parser = argparse.ArgumentParser(description="Récupérer la météo locale et l'interprétation du vent.")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    
    args = parser.parse_args()
    
    result = get_weather(args.lat, args.lon)
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
