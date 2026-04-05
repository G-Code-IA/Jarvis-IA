#!/usr/bin/env python3
"""
J.A.R.V.I.S. - MOTOR CONVERSACIONAL
Conversación natural tipo Siri/Gemini con capacidad de acción
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"
OLLAMA_TIMEOUT = 30


class ConversationalEngine:
    """Motor conversacional tipo Siri/Gemini."""
    
    def __init__(self):
        self.conversation_history = []
        self.current_topic = None
        self.pending_actions = []
        self.user_context = {
            "name": None,
            "preferences": {},
            "recent_topics": [],
            "last_interaction": None
        }
        self.max_history = 20
    
    def chat(self, user_message: str, context_messages: List[Dict] = None) -> Dict:
        """Procesar mensaje de forma conversacional."""
        
        # 1. Entender el mensaje
        understanding = self._understand(user_message)
        
        # 2. Verificar si es seguimiento de algo anterior
        follow_up = self._is_follow_up(user_message, understanding)
        
        # 3. Construir contexto conversacional
        conversation_context = self._build_context(user_message, follow_up)
        
        # 4. Decidir si necesita hacer algo o solo conversar
        needs_action = self._needs_action(user_message, understanding)
        
        if needs_action:
            # Ejecutar acción y luego responder conversacionalmente
            action_result = self._execute_action(user_message, understanding)
            response = self._generate_conversational_response(
                user_message, understanding, action_result, conversation_context
            )
        else:
            # Solo conversar
            response = self._generate_conversational_response(
                user_message, understanding, None, conversation_context
            )
        
        # 5. Guardar en historial
        self.conversation_history.append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        self.conversation_history.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limitar historial
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        return {
            "response": response,
            "understanding": understanding,
            "follow_up": follow_up,
            "action_taken": needs_action,
            "history": self.conversation_history[-6:]
        }
    
    def _understand(self, message: str) -> Dict:
        """Entender qué quiere el usuario."""
        msg_lower = message.lower()
        
        understanding = {
            "type": "unknown",
            "intent": "unknown",
            "entities": {},
            "is_question": message.endswith("?") or message.endswith("？"),
            "is_command": False,
            "emotion": "neutral",
            "urgency": "normal"
        }
        
        # Detectar tipo
        if any(x in msg_lower for x in ["hola", "hey", "buenas", "buenos"]):
            understanding["type"] = "greeting"
            understanding["intent"] = "greet"
        
        elif any(x in msg_lower for x in ["gracias", "thanks"]):
            understanding["type"] = "gratitude"
            understanding["intent"] = "thank"
        
        elif any(x in msg_lower for x in ["adiós", "chao", "bye", "hasta luego"]):
            understanding["type"] = "farewell"
            understanding["intent"] = "goodbye"
        
        elif any(x in msg_lower for x in ["quién eres", "qué eres", "cómo te llamas"]):
            understanding["type"] = "identity"
            understanding["intent"] = "ask_identity"
        
        elif any(x in msg_lower for x in ["puedes hacer", "qué haces", "capacidades"]):
            understanding["type"] = "capabilities"
            understanding["intent"] = "ask_capabilities"
        
        elif "github.com" in msg_lower or "analiza" in msg_lower:
            understanding["type"] = "action"
            understanding["intent"] = "analyze_github"
            # Extraer URL
            import re
            match = re.search(r'(https?://github\.com/\S+)', msg_lower)
            if match:
                understanding["entities"]["url"] = match.group(1)
        
        elif any(x in msg_lower for x in ["batería", "bateria", "battery"]):
            understanding["type"] = "action"
            understanding["intent"] = "check_battery"
        
        elif any(x in msg_lower for x in ["crea", "crear", "hazme", "genera"]):
            understanding["type"] = "action"
            understanding["intent"] = "create_something"
        
        elif any(x in msg_lower for x in ["busca", "buscar", "investiga"]):
            understanding["type"] = "action"
            understanding["intent"] = "search_web"
        
        elif any(x in msg_lower for x in ["clima", "tiempo", "temperatura"]):
            understanding["type"] = "action"
            understanding["intent"] = "check_weather"
        
        elif any(x in msg_lower for x in ["foto", "cámara", "selfie"]):
            understanding["type"] = "action"
            understanding["intent"] = "take_photo"
        
        elif any(x in msg_lower for x in ["diagnóstico", "diagnostico", "traje", "suit"]):
            understanding["type"] = "action"
            understanding["intent"] = "ironman_diagnostic"
        
        elif any(x in msg_lower for x in ["seguridad", "security", "amenazas"]):
            understanding["type"] = "action"
            understanding["intent"] = "ironman_security"
        
        elif any(x in msg_lower for x in ["análisis táctico", "analisis tactico", "situación"]):
            understanding["type"] = "action"
            understanding["intent"] = "ironman_tactical"
        
        elif any(x in msg_lower for x in ["taller", "workshop", "mis proyectos"]):
            understanding["type"] = "action"
            understanding["intent"] = "ironman_workshop"
        
        elif any(x in msg_lower for x in ["crear backup", "hacer backup", "respaldo"]):
            understanding["type"] = "action"
            understanding["intent"] = "ironman_backup"
        
        elif any(x in msg_lower for x in ["iron man", "modo iron", "protocolos"]):
            understanding["type"] = "action"
            understanding["intent"] = "ironman_menu"
        
        elif any(x in msg_lower for x in ["plugins", "extensiones"]):
            understanding["type"] = "action"
            understanding["intent"] = "list_plugins"
        
        elif any(x in msg_lower for x in ["memoria", "recuerdas", "recordar"]):
            understanding["type"] = "action"
            understanding["intent"] = "check_memory"
        
        elif any(x in msg_lower for x in ["sistema", "info del sistema"]):
            understanding["type"] = "action"
            understanding["intent"] = "system_info"
        
        elif understanding["is_question"]:
            understanding["type"] = "question"
            understanding["intent"] = "general_question"
        
        else:
            understanding["type"] = "conversation"
            understanding["intent"] = "chat"
        
        # Detectar emoción
        if any(x in msg_lower for x in ["por favor", "please"]):
            understanding["emotion"] = "polite"
        if any(x in msg_lower for x in ["!", "¡", "urgente", "rápido", "ya"]):
            understanding["emotion"] = "urgent"
            understanding["urgency"] = "high"
        if any(x in msg_lower for x in ["triste", "mal", "enojado"]):
            understanding["emotion"] = "negative"
        
        return understanding
    
    def _is_follow_up(self, message: str, understanding: Dict) -> Optional[Dict]:
        """Verificar si es seguimiento de conversación anterior."""
        if len(self.conversation_history) < 2:
            return None
        
        msg_lower = message.lower()
        
        # Pronombres que indican seguimiento
        follow_up_indicators = [
            "y eso", "y qué", "por qué", "cómo funciona",
            "dime más", "cuéntame más", "explícame",
            "y el", "y la", "y los",
            "qué opinas", "qué piensas",
            "puedes", "sabes",
            "eso es", "eso fue"
        ]
        
        is_follow_up = any(x in msg_lower for x in follow_up_indicators)
        
        if is_follow_up:
            # Obtener último tema
            last_user_msg = None
            for msg in reversed(self.conversation_history):
                if msg["role"] == "user":
                    last_user_msg = msg["content"]
                    break
            
            return {
                "is_follow_up": True,
                "previous_topic": last_user_msg,
                "connection": "continuing_conversation"
            }
        
        return None
    
    def _build_context(self, message: str, follow_up: Optional[Dict]) -> str:
        """Construir contexto para la conversación."""
        context_parts = []
        
        # Agregar historial reciente
        recent = self.conversation_history[-6:]
        if recent:
            context_parts.append("Historial reciente de la conversación:")
            for msg in recent:
                role = "Usuario" if msg["role"] == "user" else "J.A.R.V.I.S."
                context_parts.append(f"{role}: {msg['content']}")
        
        # Si es seguimiento, agregar contexto adicional
        if follow_up:
            context_parts.append(f"\nEl usuario está continuando la conversación sobre: {follow_up['previous_topic']}")
        
        return "\n".join(context_parts)
    
    def _needs_action(self, message: str, understanding: Dict) -> bool:
        """Decidir si necesita ejecutar una acción."""
        return understanding["type"] == "action"
    
    def _execute_action(self, message: str, understanding: Dict) -> Optional[Dict]:
        """Ejecutar la acción necesaria."""
        intent = understanding["intent"]
        
        try:
            if intent == "analyze_github":
                url = understanding.get("entities", {}).get("url", "")
                if not url:
                    import re
                    match = re.search(r'(https?://github\.com/\S+)', message.lower())
                    if match:
                        url = match.group(1)
                
                if url:
                    from ai_developer import AIDeveloper
                    ai_dev = AIDeveloper()
                    result = ai_dev.analyze_repository(url)
                    return {"success": True, "result": result}
                return {"success": False, "error": "URL no encontrada"}
            
            elif intent == "check_battery":
                import subprocess
                result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
                data = json.loads(result.stdout)
                return {
                    "success": True,
                    "result": f"Batería: {data.get('percentage', 0)}%, Estado: {data.get('status', 'N/A')}, Temp: {data.get('temperature', 0)}°C"
                }
            
            elif intent == "check_weather":
                import re
                match = re.search(r'(?:en|ciudad|de)\s+(\w+)', message, re.IGNORECASE)
                city = match.group(1) if match else "Mexico City"
                resp = requests.get(
                    f"https://wttr.in/{city}?format=%c+%t+%h+%w",
                    headers={"User-Agent": "curl/7.68.0"},
                    timeout=10
                )
                return {"success": True, "result": f"Clima en {city}: {resp.text.strip()}"}
            
            elif intent == "list_plugins":
                from plugin_system import plugin_manager
                plugins = plugin_manager.get_all_plugins()
                result = "Plugins activos:\n"
                for p in plugins:
                    status = "✅" if p.get("enabled") else "❌"
                    result += f"{status} {p.get('name')} v{p.get('version')}\n"
                return {"success": True, "result": result}
            
            elif intent == "check_memory":
                from memory_system import memory_system
                stats = memory_system.get_memory_stats()
                result = f"Memoria: {stats.get('long_term_count', 0)} memorias, {stats.get('conversation_count', 0)} conversaciones, {stats.get('preferences_count', 0)} preferencias"
                return {"success": True, "result": result}
            
            elif intent == "system_info":
                import platform
                result = f"Python {platform.python_version()}, {platform.system()} {platform.release()}, {platform.machine()}"
                return {"success": True, "result": result}
            
            elif intent == "take_photo":
                from camera_module import CameraTools
                camera = CameraTools()
                result = camera.take_photo()
                return {"success": result is not None, "result": result or "No se pudo tomar foto"}
            
            elif intent == "ironman_diagnostic":
                from ironman_module import IronManModule
                module = IronManModule()
                scan = module.suit.full_system_scan()
                return {"success": True, "result": module.suit.format_diagnostic_report(scan)}
            
            elif intent == "ironman_security":
                from ironman_module import IronManModule
                module = IronManModule()
                scan = module.threats.scan_network()
                return {"success": True, "result": module.threats.format_threat_report(scan)}
            
            elif intent == "ironman_tactical":
                from ironman_module import IronManModule
                module = IronManModule()
                analysis = module.tactical.analyze_situation()
                return {"success": True, "result": module.tactical.format_tactical_report(analysis)}
            
            elif intent == "ironman_workshop":
                from ironman_module import IronManModule
                module = IronManModule()
                projects = module.workshop.list_projects()
                return {"success": True, "result": module.workshop.format_workshop_report(projects)}
            
            elif intent == "ironman_backup":
                from ironman_module import IronManModule
                module = IronManModule()
                result = module.backup.create_backup()
                return {"success": True, "result": f"✅ Backup creado: {result['count']} archivos en {result['path']}"}
            
            elif intent == "ironman_menu":
                return {
                    "success": True,
                    "result": (
                        "🦾 **PROTOCOLOS IRON MAN**\n\n"
                        "🔧 **diagnóstico** - Escaneo del sistema\n"
                        "🛡️ **seguridad** - Escaneo de amenazas\n"
                        "🎯 **análisis táctico** - Reporte de situación\n"
                        "📁 **taller** - Proyectos activos\n"
                        "💾 **crear backup** - Respaldo de datos\n\n"
                        "¿Qué necesitas, señor?"
                    )
                }
            
            elif intent == "search_web":
                import re
                query = re.sub(r'(busca|buscar|investiga)', '', message, flags=re.IGNORECASE).strip()
                from urllib.parse import quote
                url = f"https://lite.duckduckgo.com/lite/?q={quote(query)}"
                headers = {"User-Agent": "Mozilla/5.0"}
                resp = requests.get(url, headers=headers, timeout=10)
                links = re.findall(r'<a href="(https?://[^"]+)"[^>]*>([^<]{30,100})</a>', resp.text)
                results = []
                for link, title in links[:5]:
                    title = re.sub(r'<[^>]+>', '', title).strip()
                    if 'duckduckgo' not in link.lower() and len(title) > 10:
                        results.append(f"• {title}\n  {link}")
                return {"success": True, "result": "\n\n".join(results) if results else "Sin resultados"}
            
            elif intent == "create_something":
                return {"success": True, "result": "¿Qué quieres que cree? Dime más detalles y lo hago."}
            
            return {"success": False, "error": "Acción no reconocida"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_conversational_response(self, message: str, understanding: Dict, 
                                          action_result: Optional[Dict], context: str) -> str:
        """Generar respuesta conversacional natural."""
        
        # Respuestas directas para tipos específicos
        if understanding["type"] == "greeting":
            return self._respond_to_greeting()
        
        if understanding["type"] == "gratitude":
            return "¡De nada! 😊 ¿En qué más puedo ayudarte?"
        
        if understanding["type"] == "farewell":
            return "¡Hasta luego! 👋 Estaré aquí cuando me necesites."
        
        if understanding["type"] == "identity":
            return (
                "Soy J.A.R.V.I.S., tu asistente personal de IA. 🤖\n\n"
                "Puedo ayudarte con muchas cosas:\n"
                "• Analizar repositorios de GitHub\n"
                "• Buscar información en la web\n"
                "• Ver el clima y la batería\n"
                "• Crear archivos y proyectos\n"
                "• Y mucho más!\n\n"
                "¿Qué necesitas?"
            )
        
        if understanding["type"] == "capabilities":
            return (
                "Puedo hacer muchas cosas! 🚀\n\n"
                "🔍 **Buscar:** 'Busca noticias de IA'\n"
                "📊 **Analizar:** 'Analiza github.com/...'\n"
                "🔋 **Sistema:** '¿Cuánta batería tengo?'\n"
                "🌤️ **Clima:** 'Clima en Madrid'\n"
                "📸 **Cámara:** 'Toma una foto'\n"
                "📁 **Archivos:** 'Crea un archivo...'\n"
                "🔌 **Plugins:** '¿Qué plugins tienes?'\n\n"
                "¡Solo dime qué necesitas!"
            )
        
        # Si hay acción, responder con el resultado de forma natural
        if action_result:
            if action_result.get("success"):
                return self._format_action_response(action_result["result"], understanding)
            else:
                return f"Ups, tuve un problema: {action_result.get('error', 'Error desconocido')}. ¿Intentamos de otra forma?"
        
        # Para conversación general, usar Ollama
        return self._chat_with_ollama(message, understanding, context)
    
    def _respond_to_greeting(self) -> str:
        """Responder a saludos de forma natural."""
        import random
        greetings = [
            "¡Hola! 👋 ¿En qué puedo ayudarte hoy?",
            "¡Hey! 😊 ¿Qué necesitas?",
            "¡Hola! Estoy listo para ayudarte. ¿Qué hacemos?",
            "¡Buenas! 🤖 ¿En qué te ayudo?"
        ]
        return random.choice(greetings)
    
    def _format_action_response(self, result: str, understanding: Dict) -> str:
        """Formatear resultado de acción de forma conversacional."""
        intent = understanding["intent"]
        
        if intent == "check_battery":
            return f"🔋 Tu batería está así:\n\n{result}"
        
        if intent == "analyze_github":
            return f"📊 Analicé ese repo por ti:\n\n{result}"
        
        if intent == "check_weather":
            return f"🌤️ El clima:\n\n{result}"
        
        if intent == "list_plugins":
            return f"🔌 Estos son mis plugins:\n\n{result}"
        
        if intent == "search_web":
            return f"🔍 Encontré esto:\n\n{result}"
        
        return f"✅ Listo:\n\n{result}"
    
    def _chat_with_ollama(self, message: str, understanding: Dict, context: str) -> str:
        """Usar Ollama para conversación general - con fallback inteligente."""
        
        # Primero intentar responder sin Ollama (más rápido)
        msg_lower = message.lower()
        
        # Respuestas directas para preguntas comunes
        if any(x in msg_lower for x in ["qué te pareció", "qué opinas", "qué piensas"]):
            if "repo" in msg_lower or "github" in msg_lower:
                return "Me pareció interesante! 📊 Es un proyecto activo con buena comunidad. ¿Quieres que analice algo específico de ese repo?"
            return "Buena pregunta! 🤔 Dame más contexto y te doy mi opinión."
        
        if any(x in msg_lower for x in ["y eso", "y qué", "qué es"]):
            if "repo" in msg_lower:
                return "Un repositorio de GitHub es donde los desarrolladores guardan su código. El que analizamos tiene miles de estrellas! ⭐"
            return "¿Puedes ser más específico? Así te puedo ayudar mejor. 😊"
        
        if any(x in msg_lower for x in ["cómo funciona", "cómo se usa"]):
            return "Depende del proyecto, pero generalmente puedes clonarlo con `git clone` y seguir las instrucciones del README. ¿Quieres que te ayude con algo específico?"
        
        if any(x in msg_lower for x in ["vale", "ok", "entendido", "genial", "perfecto"]):
            return "¡Genial! 😊 ¿Necesitas algo más?"
        
        if any(x in msg_lower for x in ["no entiendo", "no comprendo", "explícame"]):
            return "Claro, te explico mejor. ¿Qué parte no entendiste? Así te ayudo paso a paso. 👍"
        
        if any(x in msg_lower for x in ["quién creó", "quién hizo", "autor"]):
            return "Ese repo fue creado por la comunidad de desarrolladores. Tiene miles de contribuidores! 🌟"
        
        if any(x in msg_lower for x in ["gracias", "thanks"]):
            return "¡De nada! 😊 Estoy aquí para lo que necesites."
        
        if any(x in msg_lower for x in ["adiós", "chao", "bye"]):
            return "¡Hasta luego! 👋 Cuando me necesites, aquí estaré."
        
        if any(x in msg_lower for x in ["quién eres", "qué eres"]):
            return "Soy J.A.R.V.I.S., tu asistente de IA personal. 🤖 Puedo ayudarte con código, búsquedas, análisis y mucho más. ¿Qué necesitas?"
        
        # Si no puedo responder directamente, intentar Ollama con timeout corto
        try:
            system = (
                "Eres J.A.R.V.I.S., un asistente de IA amigable. "
                "Responde en español, BREVE (máximo 2 oraciones). "
                "Sé natural y útil."
            )
            
            prompt = f"{system}\n\nUsuario: {message}\nJ.A.R.V.I.S.:"
            
            payload = {
                "model": "qwen2.5-coder:1.5b",
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 80}
            }
            
            resp = requests.post(OLLAMA_API, json=payload, timeout=10)
            resp.raise_for_status()
            result = resp.json().get("response", "")
            
            if result:
                return result
            return "No estoy seguro de eso, pero puedo ayudarte con otra cosa. 😊"
        
        except requests.exceptions.Timeout:
            return "Esa pregunta me tiene pensando. ¿Puedes reformularla? 🤔"
        except Exception as e:
            return "Tengo un pequeño problema técnico. ¿Intentamos otra cosa? 🔧"
    
    def get_conversation_summary(self) -> Dict:
        """Resumen de la conversación actual."""
        return {
            "messages_exchanged": len(self.conversation_history),
            "current_topic": self.current_topic,
            "recent_topics": self.user_context.get("recent_topics", [])[-5:],
            "last_interaction": self.user_context.get("last_interaction")
        }


# Instancia global
conversational_engine = ConversationalEngine()


def test_conversation():
    """Probar motor conversacional."""
    engine = ConversationalEngine()
    
    # Prueba 1: Saludo
    result = engine.chat("Hola!")
    print(f"Usuario: Hola!")
    print(f"JARVIS: {result['response']}\n")
    
    # Prueba 2: Pregunta de capacidad
    result = engine.chat("¿Qué puedes hacer?")
    print(f"Usuario: ¿Qué puedes hacer?")
    print(f"JARVIS: {result['response']}\n")
    
    # Prueba 3: Acción
    result = engine.chat("¿Cuánta batería tengo?")
    print(f"Usuario: ¿Cuánta batería tengo?")
    print(f"JARVIS: {result['response']}\n")
    
    # Prueba 4: Seguimiento
    result = engine.chat("¿Y qué plugins tienes?")
    print(f"Usuario: ¿Y qué plugins tienes?")
    print(f"JARVIS: {result['response']}\n")
    
    print("✅ Prueba completada")


if __name__ == "__main__":
    test_conversation()
