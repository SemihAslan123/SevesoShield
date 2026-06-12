"""
SevesoShield — Client LLM (Groq / Llama 3)

Rôle : Fournir le "cerveau" du pipeline.
       Llama 3 interprète la question en langage naturel
       et formule une réponse conversationnelle finale.

Modèle : llama-3.3-70b-versatile via Groq API (très rapide)
API Key : https://console.groq.com/keys (gratuit, pas de carte bancaire requise)
"""

import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


# ──────────────────────────────────────────────
#  Configuration
# ──────────────────────────────────────────────

def _get_api_key() -> str:
    """
    Lit la clé API Groq depuis la variable d'environnement GROQ_API_KEY.
    Lève une erreur claire si elle est absente.
    """
    key = os.environ.get("GROQ_API_KEY", "").strip()
    if not key:
        raise EnvironmentError(
            "\n\n❌ Variable d'environnement GROQ_API_KEY manquante.\n"
            "\n"
            "   1. Obtenez une clé gratuite sur : https://console.groq.com/keys\n"
            "   2. Définissez-la dans votre terminal :\n"
            "\n"
            "      Windows PowerShell :\n"
            "        $env:GROQ_API_KEY = 'votre_cle_ici'\n"
            "\n"
            "      Windows CMD :\n"
            "        set GROQ_API_KEY=votre_cle_ici\n"
            "\n"
            "      Linux / macOS :\n"
            "        export GROQ_API_KEY='votre_cle_ici'\n"
        )
    return key


def _build_client():
    """Initialise et retourne le client Groq."""
    api_key = _get_api_key()
    return Groq(api_key=api_key)


# Singleton — initialisé une seule fois à l'import
_model = None


def get_model():
    """Retourne le modèle Gemini (initialisé à la demande)."""
    global _model
    if _model is None:
        _model = _build_client()
    return _model


# ──────────────────────────────────────────────
#  Fonctions publiques
# ──────────────────────────────────────────────

def extract_location_from_question(question: str) -> dict:
    """
    Demande à Gemini d'extraire le lieu et l'intention depuis une question en français.

    Retourne un dict :
    {
        "city": "Besançon",          # Nom de commune (ou None)
        "lat": None,                  # Latitude si coordonnées détectées
        "lon": None,                  # Longitude si coordonnées détectées
        "radius": 5000,               # Rayon en mètres (5000 par défaut)
        "intent": "danger général"    # Ce que l'utilisateur veut savoir
    }
    """
    model = get_model()

    prompt = f"""Tu es un assistant spécialisé en risques industriels français.
    
Analyse cette question : "{question}"

Extrais les informations suivantes au format JSON strict (pas de commentaires, pas de markdown) :
{{
  "city": "nom de la commune française mentionnée, ou null si aucune",
  "lat": null,
  "lon": null,
  "radius": 5000,
  "intent": "résumé en 5 mots max de ce que l'utilisateur veut savoir"
}}

Règles :
- Si une commune est mentionnée (ex: "Rouen", "Tavaux", "Feyzin"), mets son nom dans "city"
- Si des coordonnées GPS sont mentionnées (ex: "45.7, 4.8"), mets-les dans "lat" et "lon"
- Si un rayon est mentionné (ex: "dans un rayon de 10 km"), convertis en mètres dans "radius"
- Sinon, radius = 5000 (défaut)
- Ne retourne QUE le JSON, rien d'autre"""

    try:
        response = model.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es un assistant JSON strict. Ne renvoie QUE du JSON valide."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        raw = response.choices[0].message.content.strip()
        # Nettoyer si le LLM ajoute des balises markdown
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"  [Erreur LLM] {e}")
        # Fallback si l'API échoue
        return {
            "city": None,
            "lat": None,
            "lon": None,
            "radius": 5000,
            "intent": "analyse générale"
        }


def generate_conversational_response(question: str, pipeline_data: dict) -> str:
    """
    Demande à Gemini de formuler une réponse conversationnelle
    adaptée à la question posée, à partir des données collectées.

    Args:
        question:      Question originale de l'utilisateur.
        pipeline_data: Dictionnaire avec toutes les données collectées par les agents.

    Returns:
        Réponse en langage naturel, directe et adaptée à la question.
    """
    model = get_model()

    prompt = f"""Tu es SevesoShield, un assistant d'aide à l'analyse d'incidents industriels.
Tu dois répondre à une question en utilisant UNIQUEMENT les données fournies.
Ne jamais inventer de données. Si une information manque, le dire.

QUESTION DE L'UTILISATEUR :
"{question}"

DONNÉES COLLECTÉES (sources officielles françaises) :
{json.dumps(pipeline_data, ensure_ascii=False, indent=2)}

CONSIGNES DE RÉPONSE :
- Réponds directement à la question posée, de manière conversationnelle
- Commence par répondre à ce qui est demandé (oui/non si c'est une question fermée)
- Cite les chiffres clés : nombre de SEVESO, d'écoles, direction du vent
- Mentionne les sites SEVESO Seuil Haut par leur nom si présents
- Si aucun SEVESO : le dire clairement
- Termine par un avertissement court sur le caractère indicatif des données
- Réponse en français, ton professionnel mais accessible
- Maximum 200 mots
"""

    try:
        response = model.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "Tu es SevesoShield, un assistant expert en risques industriels français."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Erreur LLM lors de la génération de la réponse : {e}"
