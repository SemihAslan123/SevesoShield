# Interprétation du vent

## Règle de vigilance
La direction du vent donnée par l'API représente la provenance du vent.
Par exemple, 270° signifie que le vent *vient* de l'Ouest.

En cas d'incident avec dégagement d'un panache ou de fumée, celui-ci sera poussé dans la direction opposée (sous le vent).
Le calcul est simple : `(direction_vent_degres + 180) % 360`

Exemple : 
- Vent : 270° (Ouest)
- Vigilance indicative : 90° (Est)

## Avertissement
Ceci est une règle purement géométrique. Elle ne tient pas compte du relief, de la stabilité atmosphérique (classes de Pasquill), ni de la vitesse du vent pour la dispersion (qui détermine la largeur du cône et la dilution). 
**Cette donnée est une simple aide au premier coup d'œil et ne remplace pas un modèle de dispersion.**
