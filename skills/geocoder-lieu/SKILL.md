---
name: geocoder-lieu
description: Trigger when user asks to locate an address, a city, an industrial site, or get GPS coordinates (latitude, longitude) of a place.
allowed-tools: Bash(python3 *)
---

# Skill geocoder-lieu

Utiliser ce skill pour transformer une adresse, une commune, un lieu ou un site industriel en coordonnées GPS (latitude, longitude).
C'est le point d'entrée pour la plupart des autres skills.

Commande :

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py --query "VOTRE RECHERCHE" --limit 3
```

La sortie est en JSON.
Si aucun résultat n'est trouvé, essayez de simplifier la requête.

Voir `references/api.md` et `references/exemples.md` pour les détails de l'API utilisée.
