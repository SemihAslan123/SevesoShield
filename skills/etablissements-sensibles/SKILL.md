---
name: etablissements-sensibles
description: Trigger when user asks about établissements sensibles, écoles, hôpitaux, crèches, EHPAD, pharmacies, lieux vulnérables, population à risque, proches d'un site.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/main.py *)
---

# Skill etablissements-sensibles

Utiliser ce skill pour identifier les établissements sensibles (écoles, hôpitaux, crèches, EHPAD, etc.) autour d’un point GPS. Utile pour évaluer rapidement les populations vulnérables potentiellement exposées.

Commande :

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py --lat "LATITUDE" --lon "LONGITUDE" --radius "RAYON_EN_METRES"
```

Le rayon par défaut est de 3000 mètres si non précisé.
La sortie est en JSON. Reformater les résultats en synthétisant par catégorie (ex: "Il y a X écoles, Y hôpitaux").

Voir `references/tags-osm.md` et `references/requetes-overpass.md` pour les détails des tags OpenStreetMap utilisés.
