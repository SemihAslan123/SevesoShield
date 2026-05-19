# SevesoShield

> **Plugin Claude Code d'aide à l'analyse rapide d'un incident industriel**

SevesoShield est un plugin Claude Code destiné à assister une première analyse autour d'un incident industriel. Il permet de localiser un site, d'identifier son contexte ICPE/SEVESO, de récupérer les conditions météo locales, d'interpréter la direction du vent de manière indicative, de repérer les établissements sensibles à proximité et de produire une synthèse opérationnelle.

> ⚠️ **Avertissement important** : SevesoShield ne remplace pas les outils officiels de gestion de crise, les plans particuliers d'intervention (PPI), les procédures préfectorales, les services de secours, ni les modèles scientifiques de dispersion atmosphérique. Les résultats sont **indicatifs** et doivent être validés par des acteurs compétents.

---

## Contexte

En cas d'incident industriel, les premières minutes sont essentielles pour comprendre rapidement le territoire concerné. Une cellule de crise ou un opérateur peut avoir besoin de répondre rapidement à plusieurs questions :

- Où se situe exactement le site industriel ?
- Le site est-il classé ICPE ou SEVESO ?
- Quels sont les établissements sensibles autour (écoles, hôpitaux, EHPAD...) ?
- Quelle est la météo locale et dans quelle direction souffle le vent ?
- Quelle est la commune concernée et sa population ?

SevesoShield apporte des réponses indicatives à ces questions en s'appuyant exclusivement sur des données ouvertes (Open Data) françaises.

---

## Liste des Skills

Le plugin est composé de **6 skills Claude Code** indépendants et activables à la demande :

| Skill | Rôle | Source de données |
|---|---|---|
| `geocoder-lieu` | Transformer une adresse ou commune en coordonnées GPS | Géoplateforme / BAN |
| `sites-industriels-risques` | Rechercher les sites ICPE/SEVESO autour d'un point | Géorisques (API officielle) |
| `meteo-vent-local` | Récupérer la météo locale et la direction du vent | Open-Meteo |
| `etablissements-sensibles` | Identifier les établissements sensibles (écoles, hôpitaux...) | OpenStreetMap / Overpass API |
| `contexte-population` | Fournir le contexte administratif et démographique | geo.api.gouv.fr (COG INSEE) |
| `synthese-incident-industriel` | Produire une synthèse opérationnelle structurée | (orchestration via prompt) |

---

## Sources de Données

Toutes les sources sont gratuites, ouvertes, et ne nécessitent **aucune clé d'API** :

- **[Géoplateforme / Base Adresse Nationale](https://api-adresse.data.gouv.fr)** : Géocodage d'adresses et communes françaises.
- **[Géorisques](https://georisques.gouv.fr)** : Base officielle des Installations Classées (ICPE) et sites SEVESO.
- **[Open-Meteo](https://open-meteo.com)** : API météo gratuite basée sur des modèles mondiaux.
- **[OpenStreetMap / Overpass API](https://overpass-api.de)** : Cartographie collaborative pour les établissements sensibles.
- **[geo.api.gouv.fr](https://geo.api.gouv.fr)** : Code Officiel Géographique (COG), données INSEE sur les communes.

---

## Installation

### Prérequis
- Python 3.x
- Claude Code (CLI)

### Étapes

1. Cloner le dépôt :
   ```bash
   git clone https://github.com/SemihAslan123/SevesoShield.git
   cd SevesoShield
   ```

2. Installer les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```

3. Installer le plugin dans Claude Code :
   ```bash
   claude plugin install .
   ```

---

## Tester les Scripts en Ligne de Commande

Chaque skill est testable indépendamment, sans Claude :

```bash
# 1. Géocodage d'une commune
python skills/geocoder-lieu/main.py --query "Tavaux"

# 2. Météo et direction du vent
python skills/meteo-vent-local/main.py --lat 47.04 --lon 5.41

# 3. Contexte administratif et population
python skills/contexte-population/main.py --city "Tavaux"

# 4. Établissements sensibles dans un rayon de 3 km
python skills/etablissements-sensibles/main.py --lat 47.04 --lon 5.41 --radius 3000

# 5. Sites ICPE/SEVESO dans un rayon de 5 km
python skills/sites-industriels-risques/main.py --city "Tavaux" --radius 5000
```

Tous les scripts renvoient du **JSON structuré** sur la sortie standard.

---

## Démonstration avec Claude Code

Une fois le plugin installé, lancez une session Claude Code et utilisez un de ces prompts :

```
> "Analyse rapidement un incident industriel autour de la commune de Tavaux (Jura). Fais-moi une synthèse complète pour une cellule de crise."
```

```
> "Y a-t-il des sites SEVESO dans un rayon de 5 km autour de Pierre-Bénite (69) ?"
```

```
> "Quel est le contexte autour du point GPS 47.04, 5.41 ? Donne-moi la météo, les établissements sensibles et les sites industriels à risque."
```

Claude va automatiquement chaîner les skills pertinents et produire une synthèse opérationnelle structurée.

---

## Structure du Dépôt

```
SevesoShield/
│
├── README.md
├── requirements.txt
├── plugin.json
├── .gitignore
│
├── skills/
│   ├── geocoder-lieu/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   │       ├── api.md
│   │       └── exemples.md
│   │
│   ├── sites-industriels-risques/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   │       ├── sources.md
│   │       ├── limites.md
│   │       └── exemples.md
│   │
│   ├── meteo-vent-local/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   │       ├── api.md
│   │       ├── interpretation-vent.md
│   │       └── exemples.md
│   │
│   ├── etablissements-sensibles/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   │       ├── tags-osm.md
│   │       ├── requetes-overpass.md
│   │       └── exemples.md
│   │
│   ├── contexte-population/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   │       ├── sources.md
│   │       └── exemples.md
│   │
│   └── synthese-incident-industriel/
│       ├── SKILL.md
│       └── references/
│           ├── methode.md
│           ├── limites.md
│           └── exemple-synthese.md
│
└── docs/
    ├── architecture.md
    ├── choix-des-sources.md
    ├── tests.md
    ├── empreinte-tokens.md
    └── demonstration.md
```

---

## Dépendances

```
requests
```

Voir `requirements.txt`. Aucune dépendance lourde ni framework requis.

---

## Limites du Projet

- Les données sont issues de sources ouvertes et peuvent ne pas être exhaustives ou à jour en temps réel.
- L'interprétation de la direction du vent est une règle géométrique simple (`(direction + 180) % 360`). Elle ne tient compte ni du relief, ni de la stabilité atmosphérique, ni d'une dispersion en cône.
- OpenStreetMap est une base collaborative : certains établissements peuvent être manquants selon le niveau de cartographie local.
- Ce plugin est conçu pour un usage indicatif en phase de première analyse. Il ne remplace en aucun cas les outils réglementaires ou les plans d'urgence officiels (PPI, ORSEC).