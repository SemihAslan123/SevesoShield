# Exemples : contexte-population

## Exemple de commande (par coordonnées)
```bash
python3 main.py --lat 47.04 --lon 5.40
```

## Exemple de commande (par nom)
```bash
python3 main.py --city "Tavaux"
```

## Sortie JSON typique
```json
{
  "city": "Tavaux",
  "insee_code": "39526",
  "postcode": "39500",
  "population": 3923,
  "department": "Jura",
  "region": "Bourgogne-Franche-Comté",
  "center": {
    "latitude": 47.04,
    "longitude": 5.4
  },
  "source": "geo.api.gouv.fr"
}
```
