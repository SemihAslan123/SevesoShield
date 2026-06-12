# SevesoShield

> **Plugin Claude Code + Système Multi-Agents d'aide à l'analyse rapide d'un incident industriel**

SevesoShield est un outil d'assistance à la première analyse d'un incident industriel. Il permet de localiser un site, d'identifier son contexte ICPE/SEVESO, de récupérer les conditions météo locales, d'interpréter la direction du vent, de repérer les établissements sensibles à proximité et de produire une synthèse opérationnelle structurée.

> ⚠️ **Avertissement important** : SevesoShield ne remplace pas les outils officiels de gestion de crise, les plans particuliers d'intervention (PPI), les procédures préfectorales, les services de secours, ni les modèles scientifiques de dispersion atmosphérique. Les résultats sont **indicatifs** et doivent être validés par des acteurs compétents.

---

## Contexte

En cas d'incident industriel, les premières minutes sont essentielles. Une cellule de crise ou un opérateur peut avoir besoin de répondre rapidement à plusieurs questions :

- Où se situe exactement le site industriel ?
- Le site est-il classé ICPE ou SEVESO ?
- Quels sont les établissements sensibles autour (écoles, hôpitaux, EHPAD...) ?
- Quelle est la météo locale et dans quelle direction souffle le vent ?
- Quelle est la commune concernée et sa population ?

SevesoShield apporte des réponses indicatives à ces questions en s'appuyant exclusivement sur des **données ouvertes (Open Data) françaises**.

---

## Deux modes d'utilisation

### Mode 1 — Plugin Claude Code (v1.0)
Intégration dans Claude Code : Claude orchestre lui-même les skills via des commandes Bash.

### Mode 2 — Système Multi-Agents autonome (v2.0)
Un système Python entièrement autonome avec un **agent manager** qui orchestre **5 agents spécialisés** en parallèle. Aucune intervention humaine requise — on pose une question en français, le système répond.

### Mode 3 — Orchestration avancée avec LangGraph (v3.0) ✨ Nouveau
Même logique que le v2.0, mais l'orchestration est gérée par un **StateGraph LangChain (LangGraph)**. Ce mode répond aux exigences d'ingénierie logicielle pour des workflows traçables et résilients, permettant de facilement forcer ou rejouer des étapes ("fake step 1").

---

## Architecture Multi-Agents (v2.0)

```
┌─────────────────────────────────────────────────────────┐
│                    AGENT MANAGER                         │
│           (agents/manager_agent.py)                      │
│  1. Reçoit la question / le lieu                         │
│  2. Lance GeocoderAgent (séquentiel)                     │
│  3. Lance 4 agents en parallèle                          │
│  4. Agrège les résultats → SyntheseAgent                 │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼ [ÉTAPE 1 — Séquentiel]
┌─────────────────┐
│  GeocoderAgent  │  → Coordonnées GPS depuis nom de commune
│ geocoder-lieu   │    (api-adresse.data.gouv.fr)
└────────┬────────┘
         │ lat, lon
         ▼ [ÉTAPE 2 — Parallèle simultané]
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  MeteoAgent  │ │  SitesAgent  │ │  Etab.Agent  │ │  Pop.Agent   │
│ meteo-vent   │ │ sites-indust │ │ etabliss.    │ │ contexte-pop │
│ Open-Meteo   │ │ Géorisques   │ │ OSM/Overpass │ │ geo.api.gouv │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
         │               │               │               │
         └───────────────┴───────────────┴───────────────┘
                                 │
                                 ▼ [ÉTAPE 3]
                      ┌──────────────────────┐
                      │    SyntheseAgent     │
                      │  Rapport Markdown    │
                      │  en 7 sections       │
                      └──────────────────────┘
```

### Fonctionnalités clés de l'architecture
- **Parallélisme** : les 4 agents indépendants tournent simultanément → ~5 secondes de bout en bout
- **Mode dégradé** : si une API est indisponible, le pipeline continue avec les données disponibles
- **Contrats normalisés** : chaque agent reçoit un `AgentInput` et retourne un `AgentOutput` standardisé
- **Journal horodaté** : chaque étape est loggée avec sa durée en millisecondes

---

## Liste des Skills (v1.0 — compatible Claude Code)

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
- Python 3.10 ou supérieur
- `pip` disponible
- (Optionnel) Claude Code CLI pour le mode plugin

### Étapes

**1. Cloner le dépôt :**
```bash
git clone https://github.com/SemihAslan123/SevesoShield.git
cd SevesoShield
```

**2. Installer les dépendances Python :**
```bash
pip install -r requirements.txt
```

**3. (Optionnel) Installer le plugin dans Claude Code :**
```bash
claude plugin install .
```

---

## Utilisation — Mode Multi-Agents (v2.0)

### Interface en langage naturel avec LLM — `ask.py` ⭐ Recommandé

La version 2.0 utilise **Llama 3 (via Groq)** comme cerveau pour analyser votre question, extraire les paramètres, orchestrer le pipeline et formuler la réponse.

**Prérequis pour `ask.py` :**
Vous devez définir une clé API Groq (100% gratuite, ultra-rapide, aucune CB requise) :
1. Obtenez une clé sur [Console Groq](https://console.groq.com/keys)
2. Définissez-la dans votre terminal :
   - Windows PowerShell : `$env:GROQ_API_KEY = 'votre_cle'`
   - Windows CMD : `set GROQ_API_KEY=votre_cle`
   - Linux/Mac : `export GROQ_API_KEY='votre_cle'`

Posez ensuite une question directement en français :

```bash
python ask.py "Je veux savoir ce qu'il y a autour de Rouen comme risques industriels"
python ask.py "Y a-t-il des sites SEVESO près de Dunkerque ?"
python ask.py "Combien d'écoles sont exposées autour de Feyzin ?"
python ask.py "Analyse la situation industrielle à Fos-sur-Mer"
python ask.py "Quels sont les risques autour de Tavaux ?"
```

**Ce que le système fait automatiquement :**
1. **Llama 3** analyse la question, extrait le lieu ("autour de Rouen" → "Rouen") et l'intention.
2. Le **Pipeline multi-agents** est lancé et collecte les données en parallèle (~5 secondes).
3. **Llama 3** rédige une réponse fluide et directement adaptée à votre question initiale.

---

### Alternative d'Excellence — Workflow LangGraph (`ask_langgraph.py`)

Si vous avez besoin d'une architecture orientée "Workflow" (idéale pour prouver la robustesse de l'orchestration) :

```bash
python ask_langgraph.py "Analyse un incident à Tavaux"

# Option spéciale : Court-circuiter l'étape 1 (simuler les données)
python ask_langgraph.py --fake-step-1 --lat 47.04 --lon 5.41
```
Ce script utilise `langgraph` pour définir un graphe d'états (StateGraph) strict, incluant des routes conditionnelles et du parallélisme géré dynamiquement.

---

### Interface CLI avancée — `main.py`

Pour plus de contrôle sur les paramètres :

```bash
# Par nom de commune
python main.py --city "Tavaux"
python main.py --city "Feyzin" --radius 10000

# Par coordonnées GPS directes (passe le géocodage)
python main.py --lat 47.04 --lon 5.41

# Sauvegarder le rapport complet en Markdown
python main.py --city "Rouen" --output rapport_rouen.md

# Sans couleurs (pour redirection dans un fichier)
python main.py --city "Lyon" --no-color > rapport.txt

# Aide complète
python main.py --help
```

---

### Exemple de sortie — `ask.py`

```
  Question : "Y a-t-il des sites SEVESO près de Dunkerque ?"

  Lieu détecté : Dunkerque

  [Pipeline Multi-Agents — 5.6 secondes]

📍 Dunkerque (Nord) — 86 263 habitants
   Région : Hauts-de-France

🏭 Risques industriels dans un rayon de 5 km :
   → 50 installations ICPE identifiées au total.
   → ⛔ 6 site(s) SEVESO Seuil Haut (danger majeur) :
      • DEPOTS DE PETROLE COTIERS — à 1051 m
      • TEPSA ST Dunkerque — à 1354 m
      • Société de la Raffinerie de Dunkerque — à 2021 m
      ...

🏫 Établissements sensibles (rayon 3 km) :
   → 170 établissements au total.
   → 🏫 85 établissement(s) scolaire(s) exposé(s).
   → 🏥 1 hôpital(ux)/clinique(s) à proximité.

🌬️ Conditions météo actuelles :
   → 15.8°C, vent à 23.4 km/h depuis le Ouest-Sud-Ouest.
   → Direction de vigilance indicative : vers le Est-Nord-Est.

💬 En résumé :
   Il y a 6 site(s) SEVESO Seuil Haut autour de Dunkerque.
   85 école(s) sont dans le périmètre exposé.
```

---

## Utilisation — Mode Claude Code (v1.0)

```bash
# Installer le plugin
claude plugin install .

# Puis dans Claude Code, poser une question :
> "Analyse rapidement un incident industriel autour de la commune de Tavaux (Jura)."
> "Y a-t-il des sites SEVESO dans un rayon de 5 km autour de Pierre-Bénite (69) ?"
> "Quel est le contexte autour du point GPS 47.04, 5.41 ?"
```

---

## Tester les Scripts en Ligne de Commande (Skills isolés)

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

## Structure du Dépôt

```
SevesoShield/
│
├── ask.py                          ← Interface langage naturel (v2.0) ⭐
├── main.py                         ← CLI avancée multi-agents (v2.0)
├── requirements.txt
├── plugin.json                     ← Déclaration plugin Claude Code
├── CLAUDE.md                       ← Instructions pour Claude Code
├── README.md
│
├── agents/                         ← Agents spécialisés (v2.0)
│   ├── __init__.py
│   ├── base_agent.py               ← Classe abstraite commune
│   ├── manager_agent.py            ← Orchestrateur central
│   ├── geocoder_agent.py           ← Agent géocodage
│   ├── meteo_agent.py              ← Agent météo et vent
│   ├── sites_agent.py              ← Agent sites ICPE/SEVESO
│   ├── etablissements_agent.py     ← Agent établissements sensibles
│   ├── population_agent.py         ← Agent contexte population
│   ├── synthese_agent.py           ← Agent synthèse finale
│   └── workflow_langgraph.py       ← Orchestrateur LangGraph (v3.0)
│
├── core/                           ← Infrastructure partagée (v2.0)
│   ├── __init__.py
│   ├── schemas.py                  ← Contrats inter-agents (dataclasses)
│   └── logger.py                   ← Journal horodaté coloré
│
├── skills/                         ← Skills Claude Code (v1.0 — inchangés)
│   ├── geocoder-lieu/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   ├── sites-industriels-risques/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   ├── meteo-vent-local/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   ├── etablissements-sensibles/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   ├── contexte-population/
│   │   ├── SKILL.md
│   │   ├── main.py
│   │   └── references/
│   ├── hydrologie-vigicrues/       ← Skill inondations
│   │   ├── SKILL.md
│   │   └── main.py
│   ├── visualisation-risques/      ← Skill Mermaid
│   │   └── SKILL.md
│   └── synthese-incident-industriel/
│       ├── SKILL.md
│       └── references/
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
Le parallélisme utilise `concurrent.futures.ThreadPoolExecutor` de la bibliothèque standard Python.

---

## Résultats de tests réels

| Commune | Durée | Sites ICPE | SEVESO Seuil Haut | Établissements | Écoles |
|---|---|---|---|---|---|
| Tavaux (39) | 5.6 s | 37 | 2 (Syensqo, INOVYN) | 22 | 14 |
| Feyzin (69) | 4.3 s | 50 | 6 | 58 | 34 |
| Dunkerque (59) | 5.6 s | 50 | 6 | 170 | 85 |
| Rouen (76) | 6.3 s | 50 | 0 | 388 | 149 |
| Pierre-Bénite (69) | 9.3 s | 50 | 6 (ARKEMA, KEM ONE...) | 125 | 59 |

---

## Limites du Projet

- Les données sont issues de sources ouvertes et peuvent ne pas être exhaustives ou à jour en temps réel.
- L'interprétation de la direction du vent est une règle géométrique simple (`(direction + 180) % 360`). Elle ne tient compte ni du relief, ni de la stabilité atmosphérique, ni d'une dispersion en cône.
- OpenStreetMap est une base collaborative : certains établissements peuvent être manquants selon le niveau de cartographie local.
- L'API Overpass peut être temporairement indisponible (timeout) sur les zones très denses — le système bascule alors en mode dégradé.
- Ce plugin est conçu pour un usage indicatif en phase de première analyse. Il ne remplace en aucun cas les outils réglementaires ou les plans d'urgence officiels (PPI, ORSEC).