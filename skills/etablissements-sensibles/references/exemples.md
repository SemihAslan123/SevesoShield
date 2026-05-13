# Exemples : etablissements-sensibles

## Exemple de commande
```bash
python3 main.py --lat 47.04 --lon 5.40 --radius 3000
```

## Sortie JSON typique
```json
{
  "center": {
    "latitude": 47.04,
    "longitude": 5.4
  },
  "radius_m": 3000,
  "count": 12,
  "categories": {
    "school": 4,
    "pharmacy": 3,
    "townhall": 1,
    "doctors": 4
  },
  "items": [
    {
      "name": "École Primaire Jules Ferry",
      "category": "school",
      "latitude": 47.0415,
      "longitude": 5.4022,
      "distance_m": 850,
      "source": "OpenStreetMap"
    }
  ],
  "warning": "Les données OpenStreetMap peuvent être incomplètes et doivent être vérifiées."
}
```
