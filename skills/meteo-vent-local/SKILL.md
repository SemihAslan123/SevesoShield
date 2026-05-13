---
name: meteo-vent-local
description: Trigger when user asks about météo locale, vent, direction du vent, rafales, panache, fumée, incident industriel, SEVESO, ICPE, vigilance sous le vent.
allowed-tools: Bash(python3 *)
---

# Skill meteo-vent-local

Utiliser ce skill pour récupérer les conditions météo locales actuelles autour d’un point GPS, avec un focus sur la direction et la vitesse du vent.

Commande :

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py --lat "LATITUDE" --lon "LONGITUDE"
```

La sortie est en JSON. Reformater les résultats en langage naturel et rappeler que l’interprétation du vent est indicative.

Voir `references/api.md` et `references/interpretation-vent.md` pour les détails.
