# Référence API : meteo-vent-local

## Source de données
Ce skill utilise l'API gratuite d'Open-Meteo.
URL : `https://api.open-meteo.com/v1/forecast`

## Paramètres utilisés
- `latitude`, `longitude` : Coordonnées du point d'intérêt.
- `current` : Demande les données actuelles (`temperature_2m`, `wind_speed_10m`, `wind_direction_10m`, `wind_gusts_10m`).
- `timezone=auto` : Pour s'adapter au fuseau horaire du point.

## Limites
Open-Meteo est basé sur des modèles météorologiques mondiaux ou régionaux. Ce n'est pas une mesure sur place (station météo locale), la donnée peut donc différer de la réalité exacte au sol.
