#!/usr/bin/env python3
"""
J.A.R.V.I.S. - COMPLETE AI ASSISTANT
Asistente de IA completo que piensa, razona y actúa con múltiples modelos
"""

import os
import sys
import json
import time
import random
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Optional, Any

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
sys.path.insert(0, WORKING_DIR)

from model_manager import model_manager, ModelManager
from agent_core import agent_core, AgentCore
from autonomous_agent import autonomous_agent_v2 as autonomous_agent, AutonomousAgentV2 as AutonomousAgent
from conversational_engine import conversational_engine, ConversationalEngine
from web_and_self_improve import web_search, self_improvement, WebSearchEngine, SelfImprovementEngine


class CompleteAIAssistant:
    """Asistente de IA completo con múltiples modelos y razonamiento."""
    
    def __init__(self):
        self.model_manager = model_manager
        self.agent_core = agent_core
        self.autonomous = autonomous_agent
        self.conversational = conversational_engine
        self.thought_history = []
        self.action_history = []
        self.learning_rate = 0.0
    
    def think_and_respond(self, user_input: str, context: List[Dict] = None) -> Dict:
        """Pensar profundamente y responder con el mejor modelo."""
        start_time = time.time()
        
        # Fase 1: ANALIZAR qué necesita el usuario
        analysis = self._deep_analyze(user_input)
        
        # Fase 2: SELECCIONAR el mejor modelo
        best_model = self.model_manager.get_best_model_for_task(user_input)
        
        # Fase 3: RAZONAR con el modelo apropiado
        reasoning = self._reason_with_model(user_input, best_model, analysis)
        
        # Fase 4: VERIFICAR coherencia
        verified = self._verify_response(reasoning, user_input)
        
        # Fase 5: RESPONDER
        execution_time = time.time() - start_time
        
        result = {
            "response": verified,
            "model_used": best_model,
            "analysis": analysis,
            "execution_time": execution_time,
            "thought_process": self.thought_history[-3:]
        }
        
        # Guardar en historial
        self.thought_history.append({
            "input": user_input[:100],
            "model": best_model,
            "time": execution_time,
            "timestamp": datetime.now().isoformat()
        })
        
        return result
    
    def _deep_analyze(self, user_input: str) -> Dict:
        """Análisis profundo de la entrada."""
        msg_lower = user_input.lower()
        
        analysis = {
            "intent": self._classify_intent(msg_lower),
            "complexity": self._assess_complexity(user_input),
            "requires_code": any(x in msg_lower for x in ["código", "code", "programa", "función"]),
            "requires_vision": any(x in msg_lower for x in ["imagen", "foto", "visual"]),
            "requires_creativity": any(x in msg_lower for x in ["crea", "escribe", "historia", "cuento"]),
            "requires_translation": any(x in msg_lower for x in ["traduce", "translate", "idioma"]),
            "requires_summarization": any(x in msg_lower for x in ["resume", "resumir", "summary"]),
            "emotional_tone": self._detect_emotion(msg_lower),
            "urgency": self._detect_urgency(msg_lower)
        }
        
        return analysis
    
    def _classify_intent(self, msg_lower: str) -> str:
        """Clasificar intención profunda."""
        if any(x in msg_lower for x in ["hola", "hey", "buenas"]):
            return "greeting"
        if any(x in msg_lower for x in ["gracias", "thanks"]):
            return "gratitude"
        if any(x in msg_lower for x in ["quién eres", "qué eres"]):
            return "identity"
        if any(x in msg_lower for x in ["crea un proyecto", "crear proyecto", "crea una api"]):
            return "create_project"
        if any(x in msg_lower for x in ["diagnóstico", "traje"]):
            return "diagnostic"
        if any(x in msg_lower for x in ["batería", "battery"]):
            return "battery"
        if any(x in msg_lower for x in ["github", "analiza"]):
            return "github_analysis"
        if any(x in msg_lower for x in ["modelos", "models"]):
            return "models"
        if any(x in msg_lower for x in ["instala modelo"]):
            return "install_model"
        if any(x in msg_lower for x in ["cambia modelo"]):
            return "change_model"
        
        # Web search
        if any(x in msg_lower for x in ["busca", "buscar", "search", "investiga", "noticias de"]):
            return "web_search"
        if any(x in msg_lower for x in ["obtén", "obtener", "fetch", "descarga página"]):
            return "fetch_url"
        
        # Self-improvement
        if any(x in msg_lower for x in ["actualiza", "update", "actualizar"]):
            return "self_update"
        if any(x in msg_lower for x in ["modifica", "modify", "cambia código"]):
            return "self_modify"
        if any(x in msg_lower for x in ["historial de cambios", "modificaciones", "version"]):
            return "mod_history"
        if any(x in msg_lower for x in ["agrega funcionalidad", "nueva feature"]):
            return "add_feature"
        
        if msg_lower.endswith("?"):
            return "question"
        return "conversation"
    
    def _assess_complexity(self, text: str) -> str:
        """Evaluar complejidad."""
        words = len(text.split())
        if words > 50:
            return "complex"
        elif words > 20:
            return "medium"
        return "simple"
    
    def _detect_emotion(self, msg_lower: str) -> str:
        """Detectar emoción."""
        if any(x in msg_lower for x in ["por favor", "please"]):
            return "polite"
        if any(x in msg_lower for x in ["!", "¡", "urgente"]):
            return "excited"
        if any(x in msg_lower for x in ["error", "mal", "no funciona"]):
            return "frustrated"
        return "neutral"
    
    def _detect_urgency(self, msg_lower: str) -> str:
        """Detectar urgencia."""
        if any(x in msg_lower for x in ["urgente", "rápido", "ya"]):
            return "high"
        return "normal"
    
    def _reason_with_model(self, user_input: str, model: str, analysis: Dict) -> str:
        """Razonar con el modelo seleccionado."""
        intent = analysis.get("intent", "conversation")
        
        # Respuestas directas para comandos simples
        if intent == "greeting":
            return random.choice([
                "¡Hola! 👋 ¿En qué puedo ayudarte hoy?",
                "¡Hey! 😊 ¿Qué necesitas?",
                "¡Hola! Estoy listo para ayudarte. ¿Qué hacemos?"
            ])
        
        if intent == "gratitude":
            return "¡De nada! 😊 Estoy aquí para lo que necesites."
        
        if intent == "identity":
            return (
                "Soy J.A.R.V.I.S., tu asistente de IA completo. 🤖\n\n"
                "Puedo ayudarte con:\n"
                "• 💻 Crear proyectos completos\n"
                "• 🔍 Analizar código y repositorios\n"
                "• 📊 Diagnóstico del sistema\n"
                "• 🧠 Razonamiento complejo\n"
                "• 📷 Analizar imágenes\n"
                "• 🌐 Traducciones\n"
                "• 📝 Resúmenes\n"
                "• Y mucho más!\n\n"
                "¿Qué necesitas?"
            )
        
        if intent == "models":
            return self.model_manager.get_model_recommendations()
        
        if intent == "install_model":
            import re
            match = re.search(r'instala modelo (\S+)', user_input, re.IGNORECASE)
            if match:
                model_name = match.group(1)
                result = self.model_manager.install_model(model_name)
                return result.get("message", "Procesando...")
            return "¿Qué modelo quieres instalar?"
        
        if intent == "change_model":
            import re
            match = re.search(r'cambia modelo a (\S+)', user_input, re.IGNORECASE)
            if match:
                model_name = match.group(1)
                result = self.model_manager.set_default_model(model_name)
                return result.get("message", "Procesando...")
            return "¿A qué modelo quieres cambiar?"
        
        # Web search
        if intent == "web_search":
            import re
            query = re.sub(r'(busca|buscar|search|investiga|noticias de)', '', user_input, flags=re.IGNORECASE).strip()
            if not query:
                return "¿Qué quieres que busque?"
            
            results = web_search.search(query)
            return web_search.format_search_results(results)
        
        if intent == "fetch_url":
            import re
            match = re.search(r'(https?://\S+)', user_input)
            if match:
                url = match.group(1)
                result = web_search.fetch_url(url)
                if result.get("success"):
                    return f"🌐 **{result.get('title', 'Sin título')}**\n\n{result.get('content', '')[:1000]}"
                return f"❌ Error: {result.get('error', 'No se pudo obtener')}"
            return "No encontré URL en tu mensaje"
        
        # Self-improvement
        if intent == "self_update":
            result = self_improvement.self_update()
            return result.get("message", "Actualizando...")
        
        if intent == "mod_history":
            return self_improvement.get_modification_history()
        
        if intent == "self_modify":
            return "🤔 Para modificar código necesito saber:\n1. Qué archivo cambiar\n2. Qué contenido poner\n3. Por qué hacerlo\n\n¿Qué quieres modificar?"
        
        if intent == "add_feature":
            return "✨ Para agregar una funcionalidad necesito:\n1. Nombre de la feature\n2. Código a agregar\n3. Archivo destino\n\n¿Qué quieres agregar?"
        
        # Para comandos que requieren herramientas
        if intent in ["create_project", "diagnostic", "battery", "github_analysis"]:
            # Usar agent core para ejecutar la herramienta
            result = self.agent_core.process(user_input)
            return result.get("response", "Procesando...")
        
        # Para conversación general, usar el modelo seleccionado
        return self._chat_with_selected_model(user_input, model, analysis)
    
    def _chat_with_selected_model(self, user_input: str, model: str, analysis: Dict) -> str:
        """Chatear con el modelo seleccionado."""
        try:
            # Construir prompt según tipo de tarea
            if analysis.get("requires_creativity"):
                system = "Eres J.A.R.V.I.S., un asistente creativo. Sé imaginativo y detallado."
                max_tokens = 500
            elif analysis.get("requires_summarization"):
                system = "Eres J.A.R.V.I.S., experto en resumir. Sé conciso pero completo."
                max_tokens = 300
            elif analysis.get("requires_translation"):
                system = "Eres J.A.R.V.I.S., traductor profesional. Traduce manteniendo el significado."
                max_tokens = 400
            elif analysis.get("complexity") == "complex":
                system = "Eres J.A.R.V.I.S., un asistente de IA que razona profundamente. Piensa paso a paso."
                max_tokens = 500
            else:
                system = "Eres J.A.R.V.I.S., un asistente útil. Responde en español, breve y claro."
                max_tokens = 300
            
            prompt = f"{system}\n\nUsuario: {user_input}\nJARVIS:"
            
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": max_tokens
                }
            }
            
            resp = requests.post("http://localhost:11434/api/generate", json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json().get("response", "No pude generar una respuesta")
        
        except requests.exceptions.Timeout:
            return f"⏱️ El modelo {model} tardó mucho. Intenta con algo más simple."
        except Exception as e:
            return f"❌ Error: {str(e)[:100]}"
    
    def _verify_response(self, response: str, user_input: str) -> str:
        """Verificar coherencia de la respuesta."""
        if not response:
            return "No pude generar una respuesta. ¿Puedes reformular?"
        
        if response.startswith("Error") or response.startswith("❌"):
            return response
        
        return response
    
    def get_assistant_status(self) -> Dict:
        """Obtener estado completo del asistente."""
        return {
            "models": self.model_manager.get_status(),
            "agent": self.agent_core.get_agent_status(),
            "autonomous": self.autonomous.get_status() if hasattr(self.autonomous, 'get_status') else {},
            "thought_history": self.thought_history[-5:],
            "action_history": self.action_history[-5:]
        }


# Instancia global
complete_assistant = CompleteAIAssistant()


def test():
    """Probar asistente completo."""
    assistant = CompleteAIAssistant()
    
    print("🧠 Probando asistente completo...\n")
    
    # Prueba 1: Saludo
    result = assistant.think_and_respond("Hola!")
    print(f"Usuario: Hola!")
    print(f"JARVIS: {result['response']}")
    print(f"Modelo: {result['model_used']}")
    print(f"Tiempo: {result['execution_time']:.2f}s\n")
    
    # Prueba 2: Identidad
    result = assistant.think_and_respond("¿Quién eres?")
    print(f"Usuario: ¿Quién eres?")
    print(f"JARVIS: {result['response'][:200]}...")
    print(f"Modelo: {result['model_used']}\n")
    
    # Estado
    print("📊 Estado:")
    status = assistant.get_assistant_status()
    print(f"  Modelo default: {status['models']['default_model']}")
    print(f"  Modelos instalados: {status['models']['installed_count']}")
    
    print("\n✅ Prueba completada")


if __name__ == "__main__":
    test()
