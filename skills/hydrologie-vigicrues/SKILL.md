---
name: hydrologie-vigicrues
description: Trigger when user asks about inondations, crues, cours d'eau, hydrologie, risques inondation, Vigicrues.
allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/main.py *)
---

# Skill hydrologie-vigicrues

Utiliser ce skill pour vérifier l'état de vigilance des cours d'eau à proximité via l'API Vigicrues.

Commande :

```bash
python3 ${CLAUDE_SKILL_DIR}/main.py --lat "LATITUDE" --lon "LONGITUDE"
```

La sortie est en JSON. Reformater pour informer l'utilisateur des risques d'inondation potentiels.
