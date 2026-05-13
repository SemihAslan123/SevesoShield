# Limites de la synthèse

La synthèse générée combine les données des autres skills. Elle hérite donc de toutes leurs limites :
- Imprécisions potentielles d'OpenStreetMap (lieux sensibles manquants).
- Modélisation météo globale et non locale (Open-Meteo).
- Direction du vent interprétée de façon strictement géométrique sans prise en compte de la topographie.
- Délais de mise à jour de la base Géorisques.

La phrase d'avertissement en fin de synthèse est donc **obligatoire** dans chaque réponse générée par Claude pour ce plugin.
