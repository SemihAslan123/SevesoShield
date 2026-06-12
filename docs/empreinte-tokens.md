# Stratégie d'empreinte Tokens

Un des enjeux des assistants IA autonomes est de ne pas "polluer" la fenêtre de contexte avec des instructions inutiles, sous peine d'augmenter les coûts et de dégrader la qualité des réponses.

## Choix de conception dans SevesoShield
1. **Fichiers `SKILL.md` très courts** :
   Le fichier racine de chaque skill se limite à une description stricte (Trigger when user asks...) et une liste de mots-clés.
   
2. **Déportation de la complexité dans `references/`** :
   Plutôt que d'expliquer comment fonctionne l'API Géorisques dans le `SKILL.md`, ces détails sont placés dans des fichiers annexes (`references/`). Claude ne les charge qu'à la demande.

3. **Scripts Python au lieu de logique LLM** :
   Les requêtes APIs et les calculs sont réalisés via des scripts CLI.

4. **Restriction de sécurité des outils** :
   Pour chaque skill, nous avons implémenté le format restrictif `allowed-tools: Bash(python3 ${CLAUDE_SKILL_DIR}/main.py *)` pour limiter l'exécution au périmètre du plugin.

## MCP vs Skills : Comparaison chiffrée de l'empreinte

| Skill / Capacité | Empreinte Inactive (idle) | Empreinte Active (chargé) | Mode de chargement |
|---|---|---|---|
| geocoder-lieu | ~50 tokens | ~300 tokens | À la demande (progressive) |
| sites-industriels | ~50 tokens | ~350 tokens | À la demande (progressive) |
| meteo-vent | ~50 tokens | ~280 tokens | À la demande (progressive) |
| contexte-pop | ~50 tokens | ~250 tokens | À la demande (progressive) |
| etablissements | ~50 tokens | ~320 tokens | À la demande (progressive) |
| hydrologie-vigicrues | ~50 tokens | ~250 tokens | À la demande (progressive) |
| visualisation-mermaid | ~50 tokens | ~200 tokens | À la demande (progressive) |
| **Total Cumulé** | **~350 tokens** | **~1950 tokens** (si tous actifs) | - |

> Si nous avions utilisé une architecture MCP classique, les 1950+ tokens seraient injectés de manière permanente (Idle), que l'utilisateur en ait besoin ou non. L'architecture en Skills permet de diviser par plus de 5 l'empreinte par défaut.
