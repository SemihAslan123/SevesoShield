# Scénarios de démonstration SevesoShield

Voici plusieurs scénarios pour tester le plugin Claude Code.
Avant de commencer, assurez-vous que le plugin est bien chargé dans votre session Claude (`claude plugin install .`).

## Scénario 1 : Le flux complet (Cellule de Crise)

**Question à poser à Claude :**
> "Analyse rapidement un incident industriel autour de la commune de Tavaux (Jura). Fais-moi une synthèse complète pour une cellule de crise."

**Ce que Claude devrait faire :**
1. Appeler `geocoder-lieu` avec "Tavaux" pour obtenir `[47.04, 5.41]`.
2. Appeler `contexte-population` pour voir qu'il y a environ 3900 habitants.
3. Appeler `sites-industriels-risques` avec les coordonnées et un rayon de 10 km (va trouver l'usine Solvay/Inovyn par exemple).
4. Appeler `meteo-vent-local` pour avoir la météo en temps réel et la direction du vent.
5. Appeler `etablissements-sensibles` avec un rayon de 3 km.
6. Utiliser la trame de `synthese-incident-industriel` pour structurer sa réponse finale en Markdown.

---

## Scénario 2 : Point d'intérêt direct

**Question à poser à Claude :**
> "Voici un point GPS : 45.698, 4.825 (Pierre-Bénite). Donne-moi les établissements sensibles dans un rayon de 2 km et la direction de vigilance selon le vent actuel."

**Ce que Claude devrait faire :**
- Passer l'étape de géocodage.
- Appeler directement `etablissements-sensibles` (rayon 2000) et `meteo-vent-local`.
- Formuler une réponse claire liant la direction de vigilance et la position des écoles/hôpitaux.

---

## Scénario 3 : Vérification d'un site

**Question à poser à Claude :**
> "Y a-t-il des sites classés SEVESO près de l'adresse : 10 rue de la République à Lyon ?"

**Ce que Claude devrait faire :**
- Appeler `geocoder-lieu` sur "10 rue de la République, Lyon".
- Appeler `sites-industriels-risques` autour de ces coordonnées.
- Renvoyer la liste des sites trouvés (ou indiquer qu'il n'y en a pas dans le rayon par défaut).
