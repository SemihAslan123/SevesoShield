# Requête Overpass API

L'API Overpass permet d'interroger la base de données OpenStreetMap (OSM) en temps réel.
Le script construit dynamiquement une requête en langage Overpass QL.

## Structure de la requête générée
```overpassql
[out:json][timeout:25];
(
  node["amenity"="school"](around:3000,47.04,5.4);
  way["amenity"="school"](around:3000,47.04,5.4);
  relation["amenity"="school"](around:3000,47.04,5.4);
  // ... autres tags ...
);
out center;
```

L'instruction `out center;` est très importante : elle permet de récupérer un point central (latitude/longitude) même pour des bâtiments modélisés sous forme de polygones (chemins/ways) ou de relations (plusieurs polygones).

## Limites
Les données OSM sont collaboratives. Un établissement récent ou non cartographié peut être manquant.
La disponibilité du service Overpass public gratuit peut parfois être limitée ou lente en cas de forte charge.
