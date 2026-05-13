# Référence API : geocoder-lieu

## Source de données
Ce skill utilise l'API Adresse fournie par data.gouv.fr / la Géoplateforme.
URL de base : `https://api-adresse.data.gouv.fr/search/`

## Fonctionnement
- L'API accepte un paramètre `q` pour la requête textuelle.
- Le paramètre `limit` permet de restreindre le nombre de résultats.
- Les coordonnées retournées sont au format `[longitude, latitude]`, le script Python les convertit en `latitude` et `longitude` pour plus de clarté.

## Limites
L'API Adresse est très performante pour les adresses postales et les communes. Elle peut parfois avoir plus de difficulté avec des noms commerciaux ou des usines si l'adresse exacte n'est pas connue.
Dans ce cas, une recherche sur la commune est souvent la meilleure solution de repli.
