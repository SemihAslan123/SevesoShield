# Exemples : sites-industriels-risques

## Exemple de commande (par coordonnées)
```bash
python3 main.py --lat 47.04 --lon 5.40 --radius 5000
```

## Sortie JSON typique
```json
{
  "center": {
    "latitude": 47.04,
    "longitude": 5.4
  },
  "radius_m": 5000,
  "count": 1,
  "sites": [
    {
      "name": "ARKEMA FRANCE",
      "city": "PIERRE-BENITE",
      "address": "RUE HENRI MOISSAN",
      "seveso_status": "Seuil Haut",
      "icpe_regime": "A",
      "activity_status": "En fonctionnement",
      "latitude": 45.698,
      "longitude": 4.825,
      "distance_m": 2500,
      "source": "Géorisques"
    }
  ],
  "warning": "Les données doivent être vérifiées auprès des sources officielles (DREAL, Préfecture)."
}
```
