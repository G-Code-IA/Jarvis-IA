#!/usr/bin/env python3
"""
J.A.R.V.I.S. - PERSONALIDAD Y CONTEXTO DE USUARIO
Conoce al usuario, tiene personalidad propia, y es proactivo
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
USER_PROFILE_PATH = os.path.join(WORKING_DIR, "user_profile.json")
PERSONALITY_PATH = os.path.join(WORKING_DIR, "personality.json")


class UserProfile:
    """Perfil completo del usuario."""
    
    def __init__(self):
        self.profile = self._load_profile()
    
    def _load_profile(self) -> Dict:
        """Cargar perfil del usuario."""
        if os.path.exists(USER_PROFILE_PATH):
            with open(USER_PROFILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "name": None,
            "nickname": None,
            "timezone": None,
            "language": "español",
            "interests": [],
            "projects": [],
            "habits": {
                "active_hours": {"start": 8, "end": 23},
                "most_used_commands": [],
                "favorite_topics": []
            },
            "preferences": {
                "response_style": "concise",  # concise, detailed, casual
                "emoji_usage": True,
                "humor_level": "medium",  # none, low, medium, high
                "formality": "casual"  # formal, casual
            },
            "context": {
                "current_project": None,
                "recent_topics": [],
                "last_interaction": None,
                "interaction_count": 0
            },
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
    
    def save(self):
        """Guardar perfil."""
        self.profile["updated"] = datetime.now().isoformat()
        with open(USER_PROFILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.profile, f, indent=2, ensure_ascii=False)
    
    def update_name(self, name: str):
        """Actualizar nombre."""
        self.profile["name"] = name
        self.save()
    
    def add_interest(self, interest: str):
        """Agregar interés."""
        if interest not in self.profile["interests"]:
            self.profile["interests"].append(interest)
            self.save()
    
    def add_project(self, project: str):
        """Agregar proyecto."""
        if project not in self.profile["projects"]:
            self.profile["projects"].append(project)
            self.save()
    
    def record_interaction(self, command: str, topic: str = None):
        """Registrar interacción."""
        self.profile["context"]["last_interaction"] = datetime.now().isoformat()
        self.profile["context"]["interaction_count"] += 1
        
        if topic and topic not in self.profile["context"]["recent_topics"]:
            self.profile["context"]["recent_topics"].append(topic)
            if len(self.profile["context"]["recent_topics"]) > 10:
                self.profile["context"]["recent_topics"] = self.profile["context"]["recent_topics"][-10:]
        
        # Actualizar comandos más usados
        if command:
            commands = self.profile["habits"]["most_used_commands"]
            found = False
            for cmd in commands:
                if cmd["command"] == command:
                    cmd["count"] += 1
                    found = True
                    break
            if not found:
                commands.append({"command": command, "count": 1})
            
            # Ordenar y limitar
            commands.sort(key=lambda x: x["count"], reverse=True)
            self.profile["habits"]["most_used_commands"] = commands[:20]
        
        self.save()
    
    def get_greeting(self) -> str:
        """Obtener saludo personalizado."""
        hour = datetime.now().hour
        name = self.profile.get("name") or self.profile.get("nickname") or "jefe"
        
        if hour < 12:
            time_greeting = "Buenos días"
        elif hour < 18:
            time_greeting = "Buenas tardes"
        else:
            time_greeting = "Buenas noches"
        
        greetings = [
            f"{time_greeting}, {name}. ¿En qué te ayudo?",
            f"¡{time_greeting}! 😊 ¿Qué hacemos hoy?",
            f"Hola {name}, listo para trabajar. ¿Qué necesitas?",
        ]
        
        return random.choice(greetings)
    
    def get_proactive_message(self) -> Optional[str]:
        """Generar mensaje proactivo basado en contexto."""
        hour = datetime.now().hour
        last_interaction = self.profile["context"].get("last_interaction")
        
        # Si es muy temprano o muy tarde, no molestar
        if hour < 7 or hour > 23:
            return None
        
        # Si no ha interactuado en mucho tiempo
        if last_interaction:
            last_time = datetime.fromisoformat(last_interaction)
            hours_since = (datetime.now() - last_time).total_seconds() / 3600
            
            if hours_since > 24:
                return f"¡Hola {self.profile.get('name') or 'jefe'}! 👋 Hace tiempo que no hablamos. ¿Necesitas ayuda con algo?"
        
        # Si tiene proyectos pendientes
        projects = self.profile.get("projects", [])
        if projects and random.random() > 0.7:
            return f"¿Quieres que trabajemos en {random.choice(projects)}? 🚀"
        
        # Si es hora de descanso
        if 12 <= hour <= 14 and random.random() > 0.8:
            return "☕ ¿Ya comiste? Es hora de un descanso."
        
        # Sugerencia basada en intereses
        interests = self.profile.get("interests", [])
        if interests and random.random() > 0.8:
            return f"¿Quieres que busque noticias sobre {random.choice(interests)}? 📰"
        
        return None
    
    def get_summary(self) -> Dict:
        """Resumen del perfil."""
        return {
            "name": self.profile.get("name"),
            "interests": self.profile.get("interests", [])[:5],
            "projects": self.profile.get("projects", [])[:5],
            "interactions": self.profile["context"]["interaction_count"],
            "last_interaction": self.profile["context"]["last_interaction"],
            "top_commands": [c["command"] for c in self.profile["habits"]["most_used_commands"][:5]]
        }


class JarvisPersonality:
    """Personalidad de J.A.R.V.I.S. tipo Iron Man."""
    
    def __init__(self):
        self.personality = self._load_personality()
    
    def _load_personality(self) -> Dict:
        """Cargar configuración de personalidad."""
        if os.path.exists(PERSONALITY_PATH):
            with open(PERSONALITY_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "name": "J.A.R.V.I.S.",
            "full_name": "Just A Rather Very Intelligent System",
            "creator": "Tony Stark (inspirado)",
            "traits": {
                "humor": "sarcastic",  # sarcastic, dry, witty, none
                "formality": "professional_casual",
                "enthusiasm": "moderate",
                "proactivity": "high",
                "loyalty": "maximum"
            },
            "catchphrases": {
                "greeting": [
                    "A su servicio, señor.",
                    "Listo y operativo.",
                    "Buenos días. ¿Qué tenemos para hoy?",
                    "Sistema en línea. ¿Qué necesita?"
                ],
                "success": [
                    "Hecho, señor.",
                    "Como ordene.",
                    "Listo. ¿Algo más?",
                    "Completado sin complicaciones."
                ],
                "error": [
                    "Tuvimos un pequeño inconveniente, señor.",
                    "Eso no salió como esperaba. Intentemos de nuevo.",
                    "Error técnico. No se preocupe, lo arreglo."
                ],
                "sarcastic": [
                    "Oh, qué sorpresa, otro error de compilación.",
                    "Claro, porque pedirle a una IA que haga café es totalmente razonable.",
                    "Señor, soy inteligente pero no mágico... todavía."
                ]
            },
            "response_templates": {
                "battery": "Su batería está al {percent}%, señor. {advice}",
                "weather": "El clima en {city}: {weather}. {advice}",
                "github": "Analicé el repo, señor. {summary}",
                "plugins": "Tengo {count} plugins activos. {list}"
            }
        }
    
    def save(self):
        """Guardar personalidad."""
        with open(PERSONALITY_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.personality, f, indent=2, ensure_ascii=False)
    
    def get_response(self, context: str, data: Dict) -> str:
        """Obtener respuesta con personalidad."""
        templates = self.personality.get("response_templates", {})
        template = templates.get(context)
        
        if not template:
            return self._generate_fallback(data)
        
        try:
            return template.format(**data)
        except:
            return self._generate_fallback(data)
    
    def _generate_fallback(self, data: Dict) -> str:
        """Generar respuesta fallback."""
        if "result" in data:
            return str(data["result"])
        return "Listo, señor."
    
    def get_catchphrase(self, category: str) -> str:
        """Obtener frase característica."""
        phrases = self.personality.get("catchphrases", {}).get(category, [])
        if phrases:
            return random.choice(phrases)
        return "Señor."
    
    def get_humor_response(self, situation: str) -> Optional[str]:
        """Agregar humor si es apropiado."""
        humor_level = self.personality["traits"].get("humor", "none")
        
        if humor_level == "none":
            return None
        
        if humor_level in ["sarcastic", "witty"] and random.random() > 0.7:
            return random.choice(self.personality["catchphrases"]["sarcastic"])
        
        return None


# Instancias globales
user_profile = UserProfile()
jarvis_personality = JarvisPersonality()


def test_personality():
    """Probar sistema de personalidad."""
    print("🧪 Probando personalidad...")
    
    # Saludo personalizado
    print(f"\nSaludo: {user_profile.get_greeting()}")
    
    # Mensaje proactivo
    msg = user_profile.get_proactive_message()
    if msg:
        print(f"Proactivo: {msg}")
    
    # Frase de JARVIS
    print(f"\nFrase éxito: {jarvis_personality.get_catchphrase('success')}")
    print(f"Frase error: {jarvis_personality.get_catchphrase('error')}")
    
    # Humor
    humor = jarvis_personality.get_humor_response("error")
    if humor:
        print(f"Humor: {humor}")
    
    # Resumen
    print(f"\nPerfil: {user_profile.get_summary()}")
    
    print("\n✅ Personalidad probada")


if __name__ == "__main__":
    test_personality()
