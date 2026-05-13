# Choix des Sources de Données

Toutes les sources utilisées sont libres d'accès, gratuites et ne nécessitent pas de clé d'authentification (Open Data).

1. **Géoplateforme / BAN (Base Adresse Nationale)** : 
   - *Utilisation* : `geocoder-lieu`
   - *Pourquoi* : Source officielle française, extrêmement rapide et fiable pour les communes et les adresses postales.
   - *Limites* : Moins performante pour rechercher le nom commercial d'une usine isolée sans adresse.

2. **Open-Meteo** :
   - *Utilisation* : `meteo-vent-local`
   - *Pourquoi* : API sans clé, agrégation de plusieurs modèles globaux (DWD, NOAA, Météo-France AROME si dispo), adaptée pour un projet étudiant.
   - *Limites* : Pas de mesure in-situ.

3. **Géorisques (installations classées)** :
   - *Utilisation* : `sites-industriels-risques`
   - *Pourquoi* : La base ICPE officielle du gouvernement français. Permet d'isoler le statut SEVESO et le régime de l'usine.
   - *Limites* : API parfois instable, géolocalisation qui pointe souvent vers les bureaux plutôt que vers l'installation à risque en elle-même.

4. **OpenStreetMap (via Overpass API)** :
   - *Utilisation* : `etablissements-sensibles`
   - *Pourquoi* : La base de données cartographique la plus riche pour recenser de petits établissements (crèches, pharmacies) introuvables facilement dans des bases centralisées d'État sans retraitement lourd.
   - *Limites* : Données collaboratives, exhaustivité non garantie.

5. **geo.api.gouv.fr (Code Officiel Géographique)** :
   - *Utilisation* : `contexte-population`
   - *Pourquoi* : Fournit instantanément la démographie et les limites administratives (région, département) très proprement.
