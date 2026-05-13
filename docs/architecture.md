# Architecture de SevesoShield

## Pourquoi utiliser des skills plutôt que des MCP (Model Context Protocol) ?
Le projet SevesoShield a été pensé pour être léger et activable "à la demande". Contrairement à un serveur MCP qui tourne en tâche de fond et expose un ensemble complexe d'outils, les "skills" de Claude Code permettent :
- D'éviter l'installation de serveurs supplémentaires ou l'ouverture de ports locaux.
- De réduire l'empreinte token : un serveur MCP envoie souvent l'intégralité de son schéma à chaque appel, alors qu'un skill n'est chargé en contexte que si le modèle décide qu'il est pertinent.
- D'assurer une exécution ponctuelle, transparente et facile à auditer (scripts Python appelés par le shell).

## Découpage des skills
L'architecture est construite autour de 6 skills spécialisés et d'un couplage faible :
1. **geocoder-lieu** : point d'entrée, il standardise l'entrée utilisateur en coordonnées géographiques.
2. **meteo-vent-local** : fournit le contexte atmosphérique.
3. **sites-industriels-risques** : vérifie la nature industrielle du point.
4. **etablissements-sensibles** : analyse l'impact humain de proximité.
5. **contexte-population** : apporte l'aspect démographique et administratif.
6. **synthese-incident-industriel** : skill d'orchestration purement prompt-based (pas de script Python) qui agglomère les résultats précédents selon une trame stricte.

## Flux de données
Le LLM agit comme l'orchestrateur. Il lit la requête utilisateur, déclenche `geocoder-lieu` pour obtenir des coordonnées, puis passe ces coordonnées (latitude/longitude) de manière transparente aux autres skills. Les résultats JSON des scripts sont ingérés par Claude, qui produit ensuite une réponse naturelle.
