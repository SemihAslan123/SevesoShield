---
name: synthese-incident-industriel
description: Trigger when user asks for a synthèse, note de crise, résumé opérationnel, analyse globale, points de vigilance.
allowed-tools: Read
---

# Skill synthese-incident-industriel

Utiliser ce skill pour guider la rédaction d'une synthèse opérationnelle d'incident industriel. Il n'y a pas de script Python associé à ce skill, mais vous devez utiliser les données des autres skills pour remplir la trame ci-dessous.

## Trame de la synthèse attendue

1. **Localisation** : Indiquer la commune, le département, la région et la population concernée (utiliser `contexte-population` et `geocoder-lieu`).
2. **Risque industriel** : Lister les sites ICPE/SEVESO identifiés à proximité (utiliser `sites-industriels-risques`).
3. **Météo et vent** : Décrire les conditions actuelles (température, vent) (utiliser `meteo-vent-local`).
4. **Vigilance vent** : Indiquer clairement la direction de vigilance indicative.
5. **Établissements sensibles** : Résumer le nombre et le type d'établissements proches (écoles, hôpitaux...) (utiliser `etablissements-sensibles`).
6. **Points de vigilance** : Formuler 3 à 4 recommandations simples (ex: confirmer les données avec DREAL, prioriser l'alerte sous le vent).
7. **Limites** : Rappeler obligatoirement que la synthèse est indicative et ne remplace pas les outils de crise officiels.

Voir `references/methode.md` et `references/exemple-synthese.md` pour des détails sur le ton à employer.
