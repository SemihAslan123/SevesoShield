# Exemples : meteo-vent-local

## Exemple de commande
```bash
python3 main.py --lat 47.04 --lon 5.40
```

## Sortie JSON typique
```json
{
  "location": {
    "latitude": 47.04,
    "longitude": 5.4
  },
  "current": {
    "temperature_2m": 18.5,
    "wind_speed_10m": 12.3,
    "wind_direction_10m": 265,
    "wind_gusts_10m": 22.1
  },
  "wind_interpretation": {
    "wind_from_degrees": 265,
    "wind_from_label": "Ouest",
    "indicative_watch_towards_degrees": 85,
    "indicative_watch_towards_label": "Est",
    "explanation": "Le vent venant du/de Ouest, une vigilance indicative peut être portée vers Est."
  },
  "warning": "Cette interprétation est simplifiée et ne constitue pas une modélisation de dispersion. Ne remplace pas les outils officiels."
}
```
