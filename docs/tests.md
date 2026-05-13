# Tests du projet SevesoShield

## Commandes CLI de test

### geocoder-lieu
```bash
python3 skills/geocoder-lieu/main.py --query "Tavaux" --limit 3
python3 skills/geocoder-lieu/main.py --query "usine Arkema Pierre-Bénite" --limit 1
```

## Exemples de questions naturelles (pour Claude)
- Localise cette adresse.
- Donne les coordonnées GPS de Tavaux.
- Géocode ce site industriel.
- Où se trouve cette usine ?
- Trouve la latitude et longitude de cette commune.

## Résultats attendus
Les scripts Python renvoient toujours du JSON sur la sortie standard (stdout).
Les erreurs sont renvoyées sur la sortie d'erreur (stderr) ou dans un champ `message`/`error` du JSON.

## Cas d'erreur à tester
- Panne réseau : simuler en désactivant le réseau ou tester avec une URL erronée.
- Lieu introuvable : rechercher "ZzZzZzZzZz".
