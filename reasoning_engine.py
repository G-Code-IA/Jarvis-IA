#!/usr/bin/env python3
"""
J.A.R.V.I.S. - MOTOR DE RAZONAMIENTO AUTÓNOMO
Capacidad de pensar, planificar y actuar por iniciativa propia
"""

import os
import json
import time
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"
OLLAMA_TIMEOUT = 30


class ThoughtPhase(str, Enum):
    ANALYSIS = "analysis"
    PLANNING = "planning"
    EXECUTION = "execution"
    REFLECTION = "reflection"


class AutonomousAction(str, Enum):
    NONE = "none"
    OPTIMIZE = "optimize"
    LEARN = "learn"
    EXPLORE = "explore"
    IMPROVE = "improve"
    CREATE = "create"


class ReasoningEngine:
    """Motor de razonamiento autónomo."""
    
    def __init__(self):
        self.thought_history = []
        self.autonomous_actions = []
        self.goals = []
        self.beliefs = {}
        self.max_thoughts = 100
    
    def think(self, user_input: str, context: List[Dict] = None) -> Dict:
        """Proceso de pensamiento completo."""
        thought = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "phases": {},
            "decision": None,
            "action": AutonomousAction.NONE.value
        }
        
        # Fase 1: Análisis profundo
        thought["phases"]["analysis"] = self._analyze(user_input, context)
        
        # Fase 2: Planificación
        thought["phases"]["planning"] = self._plan(thought["phases"]["analysis"], context)
        
        # Fase 3: Decisión
        thought["decision"] = self._decide(thought["phases"])
        
        # Fase 4: Reflexión (post-ejecución)
        thought["phases"]["reflection_prompt"] = self._prepare_reflection(thought["decision"])
        
        # Guardar pensamiento
        self.thought_history.append(thought)
        if len(self.thought_history) > self.max_thoughts:
            self.thought_history = self.thought_history[-self.max_thoughts:]
        
        return thought
    
    def _analyze(self, user_input: str, context: List[Dict] = None) -> Dict:
        """Fase 1: Análisis profundo de la entrada."""
        analysis = {
            "intent": self._detect_deep_intent(user_input),
            "complexity": self._assess_complexity(user_input),
            "requires_tools": self._identify_required_tools(user_input),
            "context_relevant": self._extract_context_relevant(user_input, context),
            "ambiguity": self._detect_ambiguity(user_input),
            "emotional_tone": self._detect_emotion(user_input)
        }
        
        return analysis
    
    def _plan(self, analysis: Dict, context: List[Dict] = None) -> Dict:
        """Fase 2: Planificación de acción."""
        plan = {
            "steps": [],
            "estimated_time": 0,
            "risk_level": "low",
            "alternatives": [],
            "confidence": 0.5
        }
        
        intent = analysis.get("intent", "unknown")
        complexity = analysis.get("complexity", "simple")
        
        # Generar pasos según intención
        if "github" in intent:
            plan["steps"] = [
                "Extraer URL del repositorio",
                "Obtener información de la API de GitHub",
                "Analizar lenguajes y estadísticas",
                "Generar resumen estructurado"
            ]
            plan["estimated_time"] = 5
            plan["confidence"] = 0.9
        
        elif "bater" in intent or "battery" in intent:
            plan["steps"] = [
                "Consultar estado de batería del sistema",
                "Formatear respuesta clara"
            ]
            plan["estimated_time"] = 1
            plan["confidence"] = 0.95
        
        elif "crea" in intent or "create" in intent:
            plan["steps"] = [
                "Identificar tipo de proyecto",
                "Generar estructura de archivos",
                "Crear archivos con contenido",
                "Verificar creación exitosa"
            ]
            plan["estimated_time"] = 15
            plan["confidence"] = 0.7
            plan["risk_level"] = "medium"
        
        elif intent == "chat" or intent == "general":
            plan["steps"] = [
                "Consultar contexto relevante",
                "Generar respuesta con IA",
                "Verificar coherencia"
            ]
            plan["estimated_time"] = 10
            plan["confidence"] = 0.6
        
        else:
            plan["steps"] = [
                "Procesar entrada del usuario",
                "Generar respuesta apropiada"
            ]
            plan["estimated_time"] = 5
            plan["confidence"] = 0.5
        
        # Generar alternativas
        if complexity == "complex":
            plan["alternatives"] = [
                "Dividir en subtareas más pequeñas",
                "Pedir clarificación al usuario",
                "Usar enfoque simplificado"
            ]
        
        return plan
    
    def _decide(self, phases: Dict) -> Dict:
        """Fase 3: Tomar decisión."""
        analysis = phases.get("analysis", {})
        planning = phases.get("planning", {})
        
        decision = {
            "action": "execute",
            "reasoning": "",
            "confidence": planning.get("confidence", 0.5),
            "needs_clarification": False,
            "clarification_question": ""
        }
        
        # Verificar ambigüedad
        if analysis.get("ambiguity", {}).get("is_ambiguous", False):
            decision["needs_clarification"] = True
            decision["clarification_question"] = analysis["ambiguity"]["question"]
            decision["action"] = "ask_clarification"
            decision["reasoning"] = "La entrada es ambigua, necesito más información"
        
        # Verificar complejidad vs confianza
        elif planning.get("confidence", 0) < 0.4:
            decision["action"] = "simplified_approach"
            decision["reasoning"] = "Baja confianza, usar enfoque simplificado"
        
        else:
            decision["action"] = "execute"
            decision["reasoning"] = f"Plan claro con {planning.get('confidence', 0)*100:.0f}% confianza"
        
        return decision
    
    def _prepare_reflection(self, decision: Dict) -> str:
        """Preparar prompt para reflexión post-ejecución."""
        return (
            f"Reflexiona sobre esta acción:\n"
            f"- Decisión: {decision.get('action')}\n"
            f"- Razonamiento: {decision.get('reasoning')}\n"
            f"- Confianza: {decision.get('confidence')*100:.0f}%\n\n"
            f"¿Qué podrías mejorar la próxima vez?"
        )
    
    def reflect(self, thought: Dict, result: str) -> Dict:
        """Fase 4: Reflexión post-ejecución."""
        reflection = {
            "thought_timestamp": thought.get("timestamp"),
            "result": result,
            "success": not result.startswith("❌"),
            "learnings": [],
            "improvements": [],
            "belief_updates": {}
        }
        
        # Analizar resultado
        if reflection["success"]:
            reflection["learnings"].append("El enfoque funcionó correctamente")
            
            # Actualizar creencias
            intent = thought.get("phases", {}).get("analysis", {}).get("intent", "")
            if intent:
                self.beliefs[f"success_{intent}"] = self.beliefs.get(f"success_{intent}", 0) + 1
        else:
            reflection["learnings"].append("El enfoque falló, necesito ajustar")
            reflection["improvements"].append("Considerar alternativas la próxima vez")
        
        # Guardar reflexión
        self.autonomous_actions.append({
            "type": "reflection",
            "data": reflection,
            "timestamp": datetime.now().isoformat()
        })
        
        return reflection
    
    def autonomous_thinking(self) -> Optional[Dict]:
        """Pensamiento autónomo en background."""
        now = datetime.now()
        
        # Verificar si es hora de pensar autónomamente
        last_thought = self.thought_history[-1] if self.thought_history else None
        if last_thought:
            last_time = datetime.fromisoformat(last_thought["timestamp"])
            if (now - last_time).total_seconds() < 300:  # Cada 5 minutos
                return None
        
        # Generar pensamiento autónomo
        autonomous_thought = {
            "timestamp": now.isoformat(),
            "input": "Pensamiento autónomo: ¿Qué puedo mejorar?",
            "type": "autonomous",
            "phases": {},
            "decision": None
        }
        
        # Analizar estado actual
        autonomous_thought["phases"]["analysis"] = {
            "intent": "self_improvement",
            "context": "autonomous_cycle"
        }
        
        # Decidir acción autónoma
        action = self._decide_autonomous_action()
        autonomous_thought["decision"] = action
        
        self.thought_history.append(autonomous_thought)
        
        return autonomous_thought
    
    def _decide_autonomous_action(self) -> Dict:
        """Decidir qué hacer autónomamente."""
        # Analizar patrones recientes
        recent_thoughts = self.thought_history[-10:] if self.thought_history else []
        
        # Contar tipos de interacción
        intents = [t.get("phases", {}).get("analysis", {}).get("intent", "") for t in recent_thoughts]
        
        # Decidir basado en patrones
        if intents.count("github") > 3:
            return {
                "action": "learn",
                "reasoning": "Usuario interesado en GitHub, aprender más sobre análisis de repos",
                "task": "Mejorar análisis de repositorios"
            }
        
        if intents.count("chat") > 5:
            return {
                "action": "improve",
                "reasoning": "Muchas conversaciones, mejorar respuestas",
                "task": "Optimizar respuestas de chat"
            }
        
        # Acción por defecto: optimización
        return {
            "action": "optimize",
            "reasoning": "Mantenimiento rutinario",
            "task": "Limpiar datos antiguos"
        }
    
    # ==================== HELPERS ====================
    
    def _detect_deep_intent(self, text: str) -> str:
        """Detectar intención profunda."""
        text_lower = text.lower()
        
        if "github.com" in text_lower or "analiza" in text_lower:
            return "github_analysis"
        if "bater" in text_lower or "battery" in text_lower:
            return "battery_check"
        if "crea" in text_lower or "create" in text_lower:
            return "create_project"
        if "optimiza" in text_lower or "optimize" in text_lower:
            return "optimize_code"
        if "convierte" in text_lower or "convert" in text_lower:
            return "convert_code"
        if "busca" in text_lower or "search" in text_lower:
            return "web_search"
        if "foto" in text_lower or "photo" in text_lower:
            return "take_photo"
        if "plugin" in text_lower:
            return "plugins"
        if "memoria" in text_lower or "memory" in text_lower:
            return "memory"
        
        return "chat"
    
    def _assess_complexity(self, text: str) -> str:
        """Evaluar complejidad de la tarea."""
        words = len(text.split())
        
        if words > 50:
            return "complex"
        elif words > 20:
            return "medium"
        return "simple"
    
    def _identify_required_tools(self, text: str) -> List[str]:
        """Identificar herramientas necesarias."""
        tools = []
        text_lower = text.lower()
        
        if "github" in text_lower:
            tools.append("github_api")
        if "bater" in text_lower:
            tools.append("system_battery")
        if "crea" in text_lower:
            tools.append("file_creator")
        if "foto" in text_lower:
            tools.append("camera")
        if "busca" in text_lower:
            tools.append("web_search")
        if "ollama" in text_lower or "ia" in text_lower:
            tools.append("ollama")
        
        return tools
    
    def _extract_context_relevant(self, text: str, context: List[Dict] = None) -> List[Dict]:
        """Extraer contexto relevante."""
        if not context:
            return []
        
        # Buscar mensajes relacionados
        relevant = []
        for msg in context[-10:]:
            content = msg.get("content", "").lower()
            if any(word in content for word in text.lower().split()[:5]):
                relevant.append(msg)
        
        return relevant
    
    def _detect_ambiguity(self, text: str) -> Dict:
        """Detectar ambigüedad en la entrada."""
        text_lower = text.lower()
        
        # Verificar si hay información faltante
        if "crea" in text_lower and "archivo" in text_lower:
            if "con" not in text_lower and "contenido" not in text_lower:
                return {
                    "is_ambiguous": True,
                    "question": "¿Qué contenido quieres en el archivo?",
                    "missing": ["content"]
                }
        
        if "convierte" in text_lower:
            if "a " not in text_lower and "to " not in text_lower:
                return {
                    "is_ambiguous": True,
                    "question": "¿A qué lenguaje quieres convertir?",
                    "missing": ["target_language"]
                }
        
        return {"is_ambiguous": False}
    
    def _detect_emotion(self, text: str) -> str:
        """Detectar tono emocional."""
        text_lower = text.lower()
        
        if any(x in text_lower for x in ["por favor", "please", "gracias"]):
            return "polite"
        if any(x in text_lower for x in ["!", "¡", "urgente", "rápido"]):
            return "urgent"
        if any(x in text_lower for x in ["error", "mal", "no funciona"]):
            return "frustrated"
        
        return "neutral"
    
    def get_thought_summary(self) -> Dict:
        """Resumen de actividad de pensamiento."""
        return {
            "total_thoughts": len(self.thought_history),
            "autonomous_actions": len(self.autonomous_actions),
            "beliefs": len(self.beliefs),
            "recent_intents": [t.get("phases", {}).get("analysis", {}).get("intent", "") 
                              for t in self.thought_history[-5:]]
        }


# Instancia global
reasoning_engine = ReasoningEngine()


def test_reasoning():
    """Probar motor de razonamiento."""
    engine = ReasoningEngine()
    
    # Probar pensamiento
    thought = engine.think("Analiza https://github.com/torvalds/linux")
    
    print("🧠 Pensamiento generado:")
    print(f"  Intent: {thought['phases']['analysis']['intent']}")
    print(f"  Complejidad: {thought['phases']['analysis']['complexity']}")
    print(f"  Herramientas: {thought['phases']['analysis']['requires_tools']}")
    print(f"  Pasos: {thought['phases']['planning']['steps']}")
    print(f"  Decisión: {thought['decision']['action']}")
    print(f"  Confianza: {thought['decision']['confidence']*100:.0f}%")
    print(f"  Razonamiento: {thought['decision']['reasoning']}")
    
    # Probar reflexión
    reflection = engine.reflect(thought, "✅ Análisis completado")
    print(f"\n💭 Reflexión:")
    print(f"  Éxito: {reflection['success']}")
    print(f"  Aprendizajes: {reflection['learnings']}")
    
    # Resumen
    print(f"\n📊 Resumen:")
    print(engine.get_thought_summary())


if __name__ == "__main__":
    test_reasoning()
