---
name: sites-industriels-risques
description: Trigger when user asks about sites industriels, risques, SEVESO, ICPE, usines proches, installations classées.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/main.py *)
---

# Skill sites-industriels-risques

Utiliser ce skill pour rechercher les sites industriels à risque (ICPE, SEVESO) autour d’un point GPS ou d'une commune.

Commande (par coordonnées) :

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py --lat "LATITUDE" --lon "LONGITUDE" --radius "RAYON_EN_METRES"
```

Commande (par commune) :

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py --city "NOM_COMMUNE" --radius "RAYON_EN_METRES"
```

Le rayon par défaut est 10000 mètres.
La sortie est en JSON. Reformater pour informer l'utilisateur des sites potentiellement dangereux.

Voir `references/sources.md` et `references/limites.md` pour les détails de l'API.
