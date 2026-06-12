---
name: visualisation-risques
description: Trigger when user asks for a mindmap, diagramme, carte, graphe mermaid, ou visualisation visuelle des risques.
allowed-tools: Read
---

# Skill visualisation-risques

Utiliser ce skill pour générer un diagramme Mermaid résumant la situation.
Il n'y a pas de script Python associé. Vous devez :
1. Obtenir les données via les autres skills (sites industriels, établissements sensibles).
2. Générer un bloc de code `mermaid` au format `mindmap` ou `graph TD`.

Le centre du graphe doit être la commune, reliée aux sites SEVESO et aux établissements proches.
Ne générez que du code Mermaid valide.
