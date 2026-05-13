# Exemples : geocoder-lieu

## Recherche d'une commune
```bash
python3 main.py --query "Tavaux" --limit 1
```

Sortie JSON typique :
```json
{
  "query": "Tavaux",
  "results": [
    {
      "label": "Tavaux",
      "latitude": 47.043598,
      "longitude": 5.412497,
      "city": "Tavaux",
      "postcode": "39500",
      "score": 0.98
    }
  ]
}
```

## Recherche d'une adresse précise
```bash
python3 main.py --query "10 rue de la République, Lyon" --limit 2
```

## Gestion des erreurs
Si le lieu n'existe pas :
```bash
python3 main.py --query "VilleQuiNExistePas"
```
```json
{
  "query": "VilleQuiNExistePas",
  "results": [],
  "message": "Aucun résultat trouvé pour cette recherche."
}
```
