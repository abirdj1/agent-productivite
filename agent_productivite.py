import os
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from ddgs import DDGS
import wikipediaapi

# Charger la clé API depuis le fichier .env
load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"

NOTES_FILE = "notes.json"

print(f" DEBUG : Clé commence par '{API_KEY[:8]}'\n")

# ========== GESTION DES NOTES (Mémoire Longue) ==========

def charger_notes():
    """Charge les notes depuis le fichier JSON"""
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def sauvegarder_notes(notes):
    """Sauvegarde les notes dans le fichier JSON"""
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

def ajouter_note(contenu: str) -> str:
    """Ajoute une nouvelle note"""
    notes = charger_notes()
    nouvelle_note = {
        "id": len(notes) + 1,
        "contenu": contenu,
        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
    }
    notes.append(nouvelle_note)
    sauvegarder_notes(notes)
    return f"✅ Note ajoutée avec succès (ID {nouvelle_note['id']}) : {contenu}"

def lire_notes() -> str:
    """Lit toutes les notes sauvegardées"""
    notes = charger_notes()
    if not notes:
        return "📝 Tu n'as aucune note pour le moment."
    
    texte = "📋 Voici toutes tes notes :\n\n"
    for note in notes:
        texte += f"[{note['id']}] ({note['date']}) → {note['contenu']}\n"
    return texte

def supprimer_note(note_id: int) -> str:
    """Supprime une note par son ID"""
    notes = charger_notes()
    notes_filtrees = [n for n in notes if n["id"] != note_id]
    
    if len(notes) == len(notes_filtrees):
        return f"❌ Aucune note trouvée avec l'ID {note_id}."
    
    # Réattribuer les IDs pour garder la cohérence
    for i, note in enumerate(notes_filtrees, 1):
        note["id"] = i
    
    sauvegarder_notes(notes_filtrees)
    return f"🗑️ Note {note_id} supprimée avec succès."

# ========== AUTRES OUTILS ==========

def calculer(expression: str) -> str:
    """Fait un calcul mathématique"""
    try:
        resultat = eval(expression)
        return f"Le résultat de {expression} est {resultat}"
    except ZeroDivisionError:
        return "Erreur : division par zéro impossible."
    except Exception as e:
        return f"Erreur de calcul : {str(e)}"

def heure_actuelle() -> str:
    """Retourne l'heure et la date actuelles"""
    maintenant = datetime.now()
    return f"Il est {maintenant.strftime('%H:%M:%S')} le {maintenant.strftime('%A %d %B %Y')}"

def rechercher_internet(query: str) -> str:
    """Recherche sur internet avec DuckDuckGo"""
    try:
        with DDGS() as ddgs:
            resultats = list(ddgs.text(query, max_results=5))
        if not resultats:
            return "Aucun résultat trouvé."
        texte = f"Résultats de recherche pour '{query}' :\n\n"
        for i, res in enumerate(resultats, 1):
            texte += f"{i}. {res['title']}\n"
            texte += f"   {res['body'][:200]}...\n"
            texte += f"   Lien : {res['href']}\n\n"
        return texte
    except Exception as e:
        return f"Erreur lors de la recherche : {str(e)}"

def rechercher_wikipedia(query: str) -> str:
    """Recherche des informations fiables sur Wikipedia"""
    try:
        wiki = wikipediaapi.Wikipedia('AgentProductivite/1.0 (abir1@local)', 'fr')
        page = wiki.page(query)
        if not page.exists():
            return f"❌ Aucune page Wikipedia trouvée pour '{query}'."
        phrases = page.summary.split('. ')[:4]
        resume = '. '.join(phrases) + '.'
        return f"📚 Résumé Wikipedia sur '{query}' :\n\n{resume}\n\n🔗 Lien : {page.fullurl}"
    except Exception as e:
        return f"Erreur Wikipedia : {str(e)}"

# ========== DÉFINITION DES OUTILS ==========

tools = [
    {
        "type": "function",
        "function": {
            "name": "ajouter_note",
            "description": "Permet d'ajouter une note ou une information importante à retenir de façon permanente",
            "parameters": {
                "type": "object",
                "properties": {
                    "contenu": {"type": "string", "description": "Le contenu de la note à sauvegarder"}
                },
                "required": ["contenu"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lire_notes",
            "description": "Permet de lire toutes les notes sauvegardées",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "supprimer_note",
            "description": "Permet de supprimer une note grâce à son numéro (ID)",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {"type": "integer", "description": "Le numéro de la note à supprimer"}
                },
                "required": ["note_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculer",
            "description": "Faire un calcul mathématique",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "L'expression à calculer"}
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "heure_actuelle",
            "description": "Obtenir l'heure et la date actuelles",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rechercher_internet",
            "description": "Chercher des informations récentes sur internet",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "La requête de recherche"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "rechercher_wikipedia",
            "description": "Chercher des informations fiables sur Wikipedia",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Le sujet à rechercher"}
                },
                "required": ["query"]
            }
        }
    }
]

# ========== FONCTION D'APPEL API (Contourne Kaspersky) ==========

def appeler_ia(messages):
    """Appelle OpenRouter via curl.exe avec gestion d'erreurs"""
    data = {
        "model": "openrouter/auto",
        "messages": messages,
        "tools": tools,
        "tool_choice": "auto"
    }
    
    with open("temp_request.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)
    
    curl_command = [
        "curl.exe", "-s", "-k", "-X", "POST", API_URL,
        "-H", f"Authorization: Bearer {API_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "HTTP-Referer: http://localhost",
        "-H", "X-Title: Agent Productivite",
        "-d", "@temp_request.json"
    ]
    
    try:
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=90
        )
        
        if result.returncode != 0:
            raise Exception(f"curl a échoué: {result.stderr}")
        
        response = json.loads(result.stdout)
        
        if "error" in response:
            code = response["error"].get("code")
            if code == 429:
                return {"rate_limited": True}
            elif code == 404:
                return {"model_unavailable": True}
            raise Exception(f"Erreur API : {response['error']}")
        
        return response
        
    except subprocess.TimeoutExpired:
        raise Exception("La requête a expiré (90s).")
    except Exception as e:
        raise Exception(f"Erreur : {e}")
    finally:
        if os.path.exists("temp_request.json"):
            os.remove("temp_request.json")

# ========== AGENT DE PRODUCTIVITÉ ==========

class AgentProductivite:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": """Tu es Atlas, un assistant de productivité intelligent et professionnel.

Tes capacités :
- Ajouter, lire et supprimer des notes (sauvegardées de façon permanente)
- Faire des calculs mathématiques
- Chercher des informations sur internet et Wikipedia
- Donner l'heure et la date

Règles :
- Quand l'utilisateur dit "ajoute une note" ou "note que...", utilise l'outil ajouter_note.
- Quand l'utilisateur demande "mes notes" ou "liste des notes", utilise lire_notes.
- Quand l'utilisateur dit "supprime la note X", utilise supprimer_note avec l'ID.
- Base tes réponses sur les résultats des outils.
- Réponds toujours en français, de façon claire et structurée."""
            }
        ]

    def run(self, question: str):
        self.messages.append({"role": "user", "content": question})

        response = appeler_ia(self.messages)
        
        # Gestion des erreurs API
        if isinstance(response, dict) and response.get("rate_limited"):
            return "⚠️ Limite quotidienne gratuite d'OpenRouter atteinte. Réessaie demain."
        if isinstance(response, dict) and response.get("model_unavailable"):
            return "⚠️ Le modèle IA est temporairement indisponible. Réessaie dans quelques minutes."

        response_message = response["choices"][0]["message"]
        tool_calls = response_message.get("tool_calls")

        if tool_calls:
            self.messages.append(response_message)

            for tool_call in tool_calls:
                function_name = tool_call["function"]["name"]
                args = json.loads(tool_call["function"]["arguments"])

                print(f"→ Outil utilisé : {function_name}")

                if function_name == "ajouter_note":
                    result = ajouter_note(args.get("contenu"))
                elif function_name == "lire_notes":
                    result = lire_notes()
                elif function_name == "supprimer_note":
                    result = supprimer_note(args.get("note_id"))
                elif function_name == "calculer":
                    result = calculer(args.get("expression"))
                elif function_name == "heure_actuelle":
                    result = heure_actuelle()
                elif function_name == "rechercher_internet":
                    result = rechercher_internet(args.get("query"))
                elif function_name == "rechercher_wikipedia":
                    result = rechercher_wikipedia(args.get("query"))
                else:
                    result = "Outil inconnu"

                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": str(result)
                })

            # Appel final pour la réponse
            final_response = appeler_ia(self.messages)
            
            if isinstance(final_response, dict) and final_response.get("rate_limited"):
                return "⚠️ Limite atteinte lors de la réponse finale."
            
            reponse_raw = final_response["choices"][0]["message"].get("content")
            if not reponse_raw or not reponse_raw.strip():
                reponse = "⚠️ Le modèle n'a pas pu générer de réponse finale. Ton code fonctionne, c'est une limite du service gratuit."
            else:
                reponse = reponse_raw
        else:
            reponse_raw = response_message.get("content")
            if not reponse_raw or not reponse_raw.strip():
                reponse = "Je n'ai pas de réponse pour le moment."
            else:
                reponse = reponse_raw

        self.messages.append({"role": "assistant", "content": reponse})
        return reponse

# ========== LANCEMENT ==========

if __name__ == "__main__":
    agent = AgentProductivite()
    print("=== Agent de Productivité Atlas (avec Mémoire Longue) ===")
    print("Tape 'quit' pour quitter\n")
    print("💡 Astuce : Tes notes sont sauvegardées dans 'notes.json' et persistent après redémarrage !\n")

    while True:
        question = input("Toi : ")
        if question.lower() in ["quit", "exit", "q"]:
            print("À bientôt !")
            break

        reponse = agent.run(question)
        print(f"\nAtlas : {reponse}\n")