"""
SevesoShield — Agent de Synthèse Opérationnelle

Rôle : Agréger les données de tous les agents et produire une synthèse Markdown
       structurée selon la trame définie dans skills/synthese-incident-industriel/SKILL.md

Pas d'appel API — cet agent travaille uniquement sur les données déjà collectées.
"""

from datetime import datetime
from agents.base_agent import BaseAgent
from core.schemas import AgentInput, AgentOutput


class SyntheseAgent(BaseAgent):
    """
    Agent de synthèse finale.
    
    Entrée spéciale : cet agent reçoit les AgentOutput des autres agents
                      via la méthode synthesize() plutôt que run().
    """

    name = "SyntheseAgent"

    def _execute(self, inp: AgentInput) -> dict:
        # Non utilisé directement — voir synthesize()
        return {}

    def synthesize(
        self,
        query: str,
        geocoder_out: AgentOutput,
        meteo_out: AgentOutput,
        sites_out: AgentOutput,
        etab_out: AgentOutput,
        pop_out: AgentOutput,
    ) -> AgentOutput:
        """
        Produit la synthèse finale à partir des résultats de tous les agents.
        Retourne un AgentOutput dont data["markdown"] contient la note complète.
        """
        import time
        from core import logger

        logger.log_agent_start(self.name, "génération de la synthèse")
        t_start = time.time()

        try:
            markdown = self._build_markdown(query, geocoder_out, meteo_out, sites_out, etab_out, pop_out)
            duration_ms = int((time.time() - t_start) * 1000)
            output = AgentOutput(
                agent_name=self.name,
                success=True,
                data={"markdown": markdown},
                duration_ms=duration_ms
            )
            logger.log_agent_success(self.name, duration_ms, "synthèse générée")
            return output

        except Exception as exc:
            duration_ms = int((time.time() - t_start) * 1000)
            error_msg = f"{type(exc).__name__}: {exc}"
            output = AgentOutput(
                agent_name=self.name,
                success=False,
                data={},
                error=error_msg,
                duration_ms=duration_ms
            )
            from core import logger as _log
            _log.log_agent_failure(self.name, duration_ms, error_msg)
            return output

    # ──────────────────────────────────────────────
    #  Construction du Markdown
    # ──────────────────────────────────────────────

    def _build_markdown(self, query, geocoder_out, meteo_out, sites_out, etab_out, pop_out) -> str:
        lines = []
        now = datetime.now().strftime("%d/%m/%Y à %H:%M")

        lines.append(f"# 🛡️ Synthèse Opérationnelle SevesoShield")
        lines.append(f"")
        lines.append(f"> **Requête :** {query}")
        lines.append(f"> **Générée le :** {now}")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"")

        # ── 1. LOCALISATION ──────────────────────────────────────────
        lines.append(f"## 1. 📍 Localisation")
        lines.append(f"")
        if pop_out.success and pop_out.data:
            d = pop_out.data
            city = d.get("city", "?")
            dept = d.get("department", "?")
            region = d.get("region", "?")
            pop = d.get("population", "Non renseignée")
            postcode = d.get("postcode", "")
            insee = d.get("insee_code", "")
            lines.append(f"| Champ | Valeur |")
            lines.append(f"|---|---|")
            lines.append(f"| **Commune** | {city} ({postcode}) |")
            lines.append(f"| **Département** | {dept} |")
            lines.append(f"| **Région** | {region} |")
            lines.append(f"| **Population** | {pop:,} habitants |".replace(",", " ") if isinstance(pop, int) else f"| **Population** | {pop} |")
            lines.append(f"| **Code INSEE** | {insee} |")
        elif geocoder_out.success and geocoder_out.data.get("results"):
            r = geocoder_out.data["results"][0]
            lines.append(f"| Champ | Valeur |")
            lines.append(f"|---|---|")
            lines.append(f"| **Commune** | {r.get('city', '?')} ({r.get('postcode', '?')}) |")
            lines.append(f"| **Coordonnées** | lat={r.get('latitude'):.5f}, lon={r.get('longitude'):.5f} |")
        else:
            lines.append(f"⚠️ *Données de localisation non disponibles.*")
        lines.append(f"")

        # ── 2. RISQUES INDUSTRIELS ────────────────────────────────────
        lines.append(f"## 2. 🏭 Risques Industriels (ICPE / SEVESO)")
        lines.append(f"")
        if sites_out.success and sites_out.data:
            d = sites_out.data
            sites = d.get("sites", [])
            radius = d.get("radius_m", 5000)
            count = d.get("count", 0)
            lines.append(f"**{count} installation(s) identifiée(s)** dans un rayon de {radius // 1000} km.")
            lines.append(f"")
            if sites:
                seveso_high = [s for s in sites if "haut" in (s.get("seveso_status") or "").lower()]
                seveso_low = [s for s in sites if "bas" in (s.get("seveso_status") or "").lower()]
                other = [s for s in sites if s not in seveso_high and s not in seveso_low]

                if seveso_high:
                    lines.append(f"### ⛔ Sites SEVESO Seuil Haut ({len(seveso_high)})")
                    for s in seveso_high[:5]:
                        dist = f"{s.get('distance_m', '?')} m" if s.get('distance_m') else "?"
                        lines.append(f"- **{s.get('name', '?')}** — {s.get('city', '?')} — {dist}")
                    lines.append(f"")

                if seveso_low:
                    lines.append(f"### ⚠️ Sites SEVESO Seuil Bas ({len(seveso_low)})")
                    for s in seveso_low[:5]:
                        dist = f"{s.get('distance_m', '?')} m" if s.get('distance_m') else "?"
                        lines.append(f"- **{s.get('name', '?')}** — {s.get('city', '?')} — {dist}")
                    lines.append(f"")

                if other and len(other) <= 5:
                    lines.append(f"### ℹ️ Autres ICPE ({len(other)})")
                    for s in other[:5]:
                        dist = f"{s.get('distance_m', '?')} m" if s.get('distance_m') else "?"
                        lines.append(f"- {s.get('name', '?')} — {s.get('city', '?')} — {dist}")
                    lines.append(f"")
                elif other:
                    lines.append(f"*(+{len(other)} autres installations ICPE non-SEVESO)*")
                    lines.append(f"")
            else:
                lines.append(f"✅ Aucun site ICPE/SEVESO identifié dans ce rayon.")
                lines.append(f"")
        else:
            lines.append(f"⚠️ *Données indisponibles — API Géorisques inaccessible.*")
            if sites_out.error:
                lines.append(f"  - Erreur : `{sites_out.error}`")
            lines.append(f"")

        # ── 3. MÉTÉO ET VENT ──────────────────────────────────────────
        lines.append(f"## 3. 🌬️ Météo et Vent")
        lines.append(f"")
        if meteo_out.success and meteo_out.data:
            d = meteo_out.data
            current = d.get("current", {})
            wind = d.get("wind_interpretation", {})
            temp = current.get("temperature_2m", "?")
            speed = current.get("wind_speed_10m", "?")
            gusts = current.get("wind_gusts_10m", "?")
            wind_from = wind.get("wind_from_label", "?")
            watch_label = wind.get("indicative_watch_towards_label", "?")
            lines.append(f"| Paramètre | Valeur |")
            lines.append(f"|---|---|")
            lines.append(f"| **Température** | {temp} °C |")
            lines.append(f"| **Vitesse du vent** | {speed} km/h |")
            lines.append(f"| **Rafales** | {gusts} km/h |")
            lines.append(f"| **Direction du vent** | Depuis le {wind_from} |")
            lines.append(f"")
            lines.append(f"### 🧭 Direction de Vigilance Indicative")
            lines.append(f"")
            lines.append(f"> Le vent souffle **depuis le {wind_from}** → vigilance indicative **vers le {watch_label}**.")
            lines.append(f">")
            lines.append(f"> ⚠️ *Règle géométrique simple — ne constitue pas une modélisation de dispersion atmosphérique.*")
            lines.append(f"")
        else:
            lines.append(f"⚠️ *Données météo indisponibles — API Open-Meteo inaccessible.*")
            if meteo_out.error:
                lines.append(f"  - Erreur : `{meteo_out.error}`")
            lines.append(f"")

        # ── 4. ÉTABLISSEMENTS SENSIBLES ───────────────────────────────
        lines.append(f"## 4. 🏫 Établissements Sensibles")
        lines.append(f"")
        if etab_out.success and etab_out.data:
            d = etab_out.data
            count = d.get("count", 0)
            radius = d.get("radius_m", 3000)
            categories = d.get("categories", {})
            items = d.get("items", [])

            lines.append(f"**{count} établissement(s)** dans un rayon de {radius} m.")
            lines.append(f"")

            LABELS = {
                "school": "🏫 Écoles",
                "kindergarten": "👶 Crèches/Maternelles",
                "childcare": "👶 Garde d'enfants",
                "hospital": "🏥 Hôpitaux",
                "clinic": "🏥 Cliniques",
                "doctors": "👨‍⚕️ Médecins",
                "pharmacy": "💊 Pharmacies",
                "nursing_home": "🏠 EHPAD/Maisons de retraite",
                "social_facility": "🤝 Structures sociales",
                "townhall": "🏛️ Mairies",
                "fire_station": "🚒 Casernes pompiers",
                "police": "👮 Police/Gendarmerie",
            }

            for cat, label in LABELS.items():
                n = categories.get(cat, 0)
                if n:
                    lines.append(f"- {label} : **{n}**")

            lines.append(f"")

            # Les 5 plus proches établissements prioritaires (écoles/hôpitaux)
            priority = [i for i in items if i.get("category") in ("school", "kindergarten", "hospital", "clinic", "nursing_home")]
            if priority:
                lines.append(f"**5 établissements prioritaires les plus proches :**")
                lines.append(f"")
                for i in priority[:5]:
                    dist = i.get("distance_m", "?")
                    name = i.get("name", "Inconnu")
                    cat = LABELS.get(i.get("category", ""), i.get("category", "?"))
                    lines.append(f"- {cat} — **{name}** — à {dist} m")
                lines.append(f"")
        else:
            lines.append(f"⚠️ *Données indisponibles — API Overpass inaccessible.*")
            if etab_out.error:
                lines.append(f"  - Erreur : `{etab_out.error}`")
            lines.append(f"")

        # ── 5. POINTS DE VIGILANCE ────────────────────────────────────
        lines.append(f"## 5. ⚡ Points de Vigilance")
        lines.append(f"")
        vigilance = self._generate_vigilance_points(meteo_out, sites_out, etab_out, pop_out)
        for point in vigilance:
            lines.append(f"- {point}")
        lines.append(f"")

        # ── 6. DONNÉES MANQUANTES ─────────────────────────────────────
        missing = []
        if not geocoder_out.success: missing.append("Géocodage")
        if not meteo_out.success: missing.append("Météo (Open-Meteo)")
        if not sites_out.success: missing.append("Sites ICPE/SEVESO (Géorisques)")
        if not etab_out.success: missing.append("Établissements sensibles (OSM)")
        if not pop_out.success: missing.append("Contexte population (geo.api.gouv.fr)")

        if missing:
            lines.append(f"## ⚠️ Données Non Disponibles")
            lines.append(f"")
            lines.append(f"Les sources suivantes étaient inaccessibles lors de cette analyse :")
            for m in missing:
                lines.append(f"- {m}")
            lines.append(f"")

        # ── 7. AVERTISSEMENT OBLIGATOIRE ──────────────────────────────
        lines.append(f"---")
        lines.append(f"")
        lines.append(f"## ⚠️ Avertissement Réglementaire")
        lines.append(f"")
        lines.append(f"> **Cette synthèse est strictement indicative.** Elle est générée automatiquement à partir de données ouvertes (Open Data) et ne remplace en aucun cas :")
        lines.append(f">")
        lines.append(f"> - Les **Plans Particuliers d'Intervention (PPI)** et **Plans ORSEC**")
        lines.append(f"> - Les **outils officiels de la DREAL** et des **services préfectoraux**")
        lines.append(f"> - Les **modèles scientifiques de dispersion atmosphérique** (Gaussian, PHAST...)")
        lines.append(f"> - Les **décisions des services de secours** (SDIS, SAMU, gendarmerie)")
        lines.append(f">")
        lines.append(f"> *SevesoShield est un outil d'aide à la première analyse — toujours valider auprès des autorités compétentes.*")
        lines.append(f"")
        lines.append(f"---")
        lines.append(f"*Généré par SevesoShield v2.0 — Pipeline Multi-Agents — {now}*")

        return "\n".join(lines)

    def _generate_vigilance_points(self, meteo_out, sites_out, etab_out, pop_out) -> list:
        """Génère 3 à 5 recommandations contextuelles selon les données disponibles."""
        points = []

        # Vent et direction
        if meteo_out.success:
            wind = meteo_out.data.get("wind_interpretation", {})
            watch = wind.get("indicative_watch_towards_label", "")
            speed = meteo_out.data.get("current", {}).get("wind_speed_10m", 0)
            if watch:
                points.append(f"**Vigilance vent :** surveiller prioritairement la zone **vers le {watch}** (direction de dispersion indicative).")
            if speed and speed > 30:
                points.append(f"**Vent fort ({speed} km/h) :** dispersion rapide des polluants — élargir le périmètre de précaution.")

        # Sites SEVESO
        if sites_out.success:
            seveso_high = [s for s in sites_out.data.get("sites", []) if "haut" in (s.get("seveso_status") or "").lower()]
            if seveso_high:
                names = ", ".join(s.get("name", "?") for s in seveso_high[:2])
                points.append(f"**Site(s) SEVESO Seuil Haut identifié(s) :** contacter immédiatement la DREAL et la Préfecture ({names}).")
            elif sites_out.data.get("count", 0) > 0:
                points.append(f"**Sites ICPE présents :** vérifier auprès de la DREAL si des substances dangereuses sont impliquées.")
            else:
                points.append(f"**Aucun site SEVESO dans le rayon analysé** — vérifier auprès de la Préfecture si le périmètre est suffisant.")

        # Établissements sensibles
        if etab_out.success:
            cats = etab_out.data.get("categories", {})
            schools = cats.get("school", 0) + cats.get("kindergarten", 0)
            hospitals = cats.get("hospital", 0) + cats.get("clinic", 0)
            nursing = cats.get("nursing_home", 0)
            if schools:
                points.append(f"**{schools} établissement(s) scolaire(s) à proximité :** envisager le confinement ou l'évacuation selon l'avis des autorités.")
            if hospitals or nursing:
                n = hospitals + nursing
                points.append(f"**{n} structure(s) médicale(s)/EHPAD proche(s) :** populations vulnérables — prioriser l'alerte et la mise à l'abri.")

        # Population
        if pop_out.success:
            pop = pop_out.data.get("population")
            if isinstance(pop, int) and pop > 10000:
                points.append(f"**Commune densément peuplée ({pop:,} hab.)** — prévoir des canaux d'alerte publique (FR-Alert, sirènes PPI).".replace(",", " "))

        if not points:
            points.append("Vérifier auprès des autorités compétentes (DREAL, Préfecture, SDIS) pour toute prise de décision opérationnelle.")

        return points
