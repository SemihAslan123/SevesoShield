---
name: contexte-population
description: Trigger when user asks about population, commune concernée, contexte administratif, code INSEE, démographie.
allowed-tools: Bash(python3 *)
---

# Skill contexte-population

Utiliser ce skill pour fournir un contexte administratif et démographique simple sur la commune concernée par l'incident (code INSEE, population, département, région).

Commande :

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py --lat "LATITUDE" --lon "LONGITUDE"
```

ou par nom de commune :

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py --city "NOM_COMMUNE"
```

La sortie est en JSON. Reformater pour donner un résumé clair (ex: "La commune de X compte Y habitants et se situe dans le département Z").

Voir `references/sources.md` pour les détails de l'API geo.api.gouv.fr.
