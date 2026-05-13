# Stratégie d'empreinte Tokens

Un des enjeux des assistants IA autonomes est de ne pas "polluer" la fenêtre de contexte avec des instructions inutiles, sous peine d'augmenter les coûts et de dégrader la qualité des réponses.

## Choix de conception dans SevesoShield
1. **Fichiers `SKILL.md` très courts** :
   Le fichier racine de chaque skill, qui est lu par Claude pour comprendre l'outil, se limite à une ou deux phrases de description et à la commande Bash exacte à exécuter.
   
2. **Déportation de la complexité dans `references/`** :
   Plutôt que d'expliquer comment fonctionne l'API Géorisques dans le `SKILL.md`, ces détails sont placés dans des fichiers markdown annexes dans un dossier `references/`. Si Claude a besoin de débugger le script Python, il ira lire ces fichiers de lui-même grâce à l'outil `view_file` ou `glob`, mais il ne sera pas forcé de les charger au moment de l'initialisation du skill.

3. **Scripts Python au lieu de logique LLM** :
   Les calculs mathématiques (comme le Haversine pour la distance, ou la conversion d'angle pour la direction du vent) sont réalisés en Python. Cela économise des "tokens de raisonnement" et garantit un résultat exact.

## MCP vs Skills
Une approche MCP (Model Context Protocol) aurait obligé le LLM à charger le schéma JSON complet de toutes les API (météo, géocodage, OSM) à chaque démarrage, ce qui consomme énormément de contexte inactif. L'approche "Skills" ne déclenche la lecture du prompt d'un outil que lorsque l'utilisateur pose une question pertinente.
