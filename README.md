# SevesoShield

**Plugin Claude Code d’aide à l’analyse rapide d’un incident industriel**

## Pitch
SevesoShield est un plugin Claude Code destiné à assister une première analyse autour d’un incident industriel. Il permet de localiser un site, d’identifier son contexte ICPE/SEVESO, de récupérer les conditions météo locales, d’interpréter la direction du vent de manière indicative, de repérer les établissements sensibles à proximité et de produire une synthèse opérationnelle.

**Avertissement important** :
SevesoShield ne remplace pas les outils officiels de gestion de crise, les plans particuliers d’intervention, les procédures préfectorales, les services de secours, ni les modèles scientifiques de dispersion atmosphérique. Les résultats sont indicatifs et doivent être validés par des acteurs compétents.

## Objectifs
Fournir une aide rapide sous forme de plugin Claude Code pour répondre aux questions essentielles lors des premières minutes d'un incident industriel, en se basant uniquement sur des données ouvertes (Open Data).

## Limites
Les données sont issues de sources ouvertes (Géoplateforme, Géorisques, OpenStreetMap, Open-Meteo, etc.) et ne sont pas garanties en temps réel ni exhaustives. L'interprétation du vent est une simplification mathématique basique et non une modélisation.

## Liste des skills
1. **geocoder-lieu** : Transformer une adresse ou une commune en coordonnées GPS.
2. *(À venir) sites-industriels-risques* : Rechercher les sites industriels à risque autour d'un point.
3. *(À venir) meteo-vent-local* : Récupérer la météo locale et la direction du vent.
4. *(À venir) etablissements-sensibles* : Identifier les établissements sensibles autour d'un point GPS.
5. *(À venir) contexte-population* : Fournir le contexte administratif et démographique de la commune.
6. *(À venir) synthese-incident-industriel* : Produire une synthèse opérationnelle.

## Installation
Ce projet est un plugin Claude Code.
1. Cloner le dépôt.
2. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
3. Utiliser le plugin dans Claude Code :
   ```bash
   claude plugin install .
   ```

## Exemples d’utilisation
```bash
> claude
# Puis demander par exemple :
> "Où se trouve l'usine Arkema Pierre-Bénite ?"
> "Donne les coordonnées GPS de Tavaux."
```

## Structure du dépôt
- `plugin.json` : Déclaration du plugin pour Claude Code.
- `skills/` : Dossier contenant les différents skills (un dossier par skill avec `SKILL.md` et `main.py`).
- `docs/` : Documentation technique du projet.
- `references/` (dans chaque skill) : Détails techniques et API pour ne pas surcharger le contexte de Claude.