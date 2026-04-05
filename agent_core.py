#!/usr/bin/env python3
"""
J.A.R.V.I.S. - AGENT CORE
Motor de agente de IA autónomo tipo Qwen/GPT
Piensa, planifica, ejecuta, reflexiona y mejora
"""

import os
import json
import time
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"
OLLAMA_TIMEOUT = 30
AGENT_DATA_DIR = os.path.join(WORKING_DIR, "agent_data")
os.makedirs(AGENT_DATA_DIR, exist_ok=True)


class AgentState(str, Enum):
    IDLE = "idle"
    THINKING = "thinking"
    PLANNING = "planning"
    EXECUTING = "executing"
    REFLECTING = "reflecting"
    LEARNING = "learning"


class AgentThought:
    """Un pensamiento individual del agente."""
    def __init__(self, content: str, thought_type: str, confidence: float = 0.5):
        self.content = content
        self.type = thought_type
        self.confidence = confidence
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self):
        return {
            "content": self.content,
            "type": self.type,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }


class AgentMemory:
    """Memoria de trabajo del agente."""
    def __init__(self):
        self.short_term: List[AgentThought] = []
        self.working_context: Dict[str, Any] = {}
        self.goals: List[Dict] = []
        self.beliefs: Dict[str, Any] = {}
        self.max_short_term = 50
    
    def add_thought(self, content: str, thought_type: str, confidence: float = 0.5):
        thought = AgentThought(content, thought_type, confidence)
        self.short_term.append(thought)
        if len(self.short_term) > self.max_short_term:
            self.short_term = self.short_term[-self.max_short_term:]
        return thought
    
    def get_recent_thoughts(self, n: int = 10) -> List[Dict]:
        return [t.to_dict() for t in self.short_term[-n:]]
    
    def set_context(self, key: str, value: Any):
        self.working_context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        return self.working_context.get(key, default)
    
    def add_belief(self, key: str, value: Any, confidence: float = 0.5):
        self.beliefs[key] = {"value": value, "confidence": confidence, "updated": datetime.now().isoformat()}
    
    def get_belief(self, key: str) -> Optional[Any]:
        belief = self.beliefs.get(key)
        return belief["value"] if belief else None
    
    def get_summary(self) -> Dict:
        return {
            "short_term_count": len(self.short_term),
            "working_context_keys": list(self.working_context.keys()),
            "beliefs_count": len(self.beliefs),
            "goals_count": len(self.goals),
            "recent_thoughts": self.get_recent_thoughts(5)
        }


class AgentCore:
    """Núcleo del agente de IA autónomo."""
    
    def __init__(self):
        self.state = AgentState.IDLE
        self.memory = AgentMemory()
        self.knowledge_base = self._load_knowledge()
        self.personality_traits = self._load_personality()
        self.interaction_count = 0
        self.success_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
        # Herramientas disponibles
        self.tools = self._register_tools()
        
        # Cargar historial de aprendizaje
        self.learning_history = self._load_learning_history()
    
    def _load_knowledge(self) -> Dict:
        """Cargar base de conocimiento."""
        kb_path = os.path.join(AGENT_DATA_DIR, "knowledge.json")
        if os.path.exists(kb_path):
            with open(kb_path, 'r') as f:
                return json.load(f)
        return {"facts": [], "procedures": [], "preferences": {}}
    
    def _save_knowledge(self):
        """Guardar base de conocimiento."""
        kb_path = os.path.join(AGENT_DATA_DIR, "knowledge.json")
        with open(kb_path, 'w') as f:
            json.dump(self.knowledge_base, f, indent=2)
    
    def _load_personality(self) -> Dict:
        """Cargar rasgos de personalidad."""
        p_path = os.path.join(AGENT_DATA_DIR, "personality.json")
        if os.path.exists(p_path):
            with open(p_path, 'r') as f:
                return json.load(f)
        return {
            "humor": "witty",
            "formality": "casual",
            "empathy": "high",
            "curiosity": "high",
            "proactivity": "medium"
        }
    
    def _save_personality(self):
        """Guardar personalidad."""
        p_path = os.path.join(AGENT_DATA_DIR, "personality.json")
        with open(p_path, 'w') as f:
            json.dump(self.personality_traits, f, indent=2)
    
    def _load_learning_history(self) -> List[Dict]:
        """Cargar historial de aprendizaje."""
        lh_path = os.path.join(AGENT_DATA_DIR, "learning.json")
        if os.path.exists(lh_path):
            with open(lh_path, 'r') as f:
                return json.load(f)
        return []
    
    def _save_learning_history(self):
        """Guardar historial de aprendizaje."""
        lh_path = os.path.join(AGENT_DATA_DIR, "learning.json")
        with open(lh_path, 'w') as f:
            json.dump(self.learning_history[-100:], f, indent=2)  # Últimos 100
    
    def _register_tools(self) -> Dict[str, Dict]:
        """Registrar herramientas disponibles."""
        return {
            "search_web": {
                "description": "Buscar información en la web",
                "params": ["query"],
                "category": "information"
            },
            "analyze_github": {
                "description": "Analizar repositorio de GitHub",
                "params": ["url"],
                "category": "development"
            },
            "check_battery": {
                "description": "Verificar nivel de batería",
                "params": [],
                "category": "system"
            },
            "system_info": {
                "description": "Obtener información del sistema",
                "params": [],
                "category": "system"
            },
            "list_files": {
                "description": "Listar archivos en directorio",
                "params": ["path"],
                "category": "files"
            },
            "create_file": {
                "description": "Crear archivo con contenido",
                "params": ["path", "content"],
                "category": "files"
            },
            "take_photo": {
                "description": "Tomar foto con cámara",
                "params": [],
                "category": "camera"
            },
            "diagnostic": {
                "description": "Diagnóstico completo del sistema",
                "params": [],
                "category": "ironman"
            },
            "security_scan": {
                "description": "Escaneo de seguridad de red",
                "params": [],
                "category": "ironman"
            },
            "tactical_analysis": {
                "description": "Análisis táctico de situación",
                "params": [],
                "category": "ironman"
            },
            "create_backup": {
                "description": "Crear respaldo de datos",
                "params": [],
                "category": "system"
            },
            "list_plugins": {
                "description": "Listar plugins activos",
                "params": [],
                "category": "system"
            },
            "create_project": {
                "description": "Crear proyecto completo desde plantilla",
                "params": ["description"],
                "category": "development"
            },
            "list_templates": {
                "description": "Listar plantillas de proyectos disponibles",
                "params": [],
                "category": "development"
            },
            "chat": {
                "description": "Conversación general con IA",
                "params": ["message"],
                "category": "conversation"
            }
        }
    
    # ==================== CICLO DE AGENTE ====================
    
    def process(self, user_input: str, context: List[Dict] = None) -> Dict:
        """Procesar entrada del usuario como agente autónomo."""
        self.state = AgentState.THINKING
        self.interaction_count += 1
        
        # Fase 1: COMPRENDER
        understanding = self._understand(user_input, context)
        self.memory.add_thought(f"Usuario dice: {user_input}", "observation", 0.9)
        
        # Fase 2: PENSAR
        self.state = AgentState.THINKING
        thoughts = self._think(user_input, understanding)
        
        # Fase 3: PLANIFICAR
        self.state = AgentState.PLANNING
        plan = self._plan(user_input, understanding, thoughts)
        
        # Fase 4: DECIDIR
        decision = self._decide(plan, understanding)
        
        # Fase 5: EJECUTAR
        self.state = AgentState.EXECUTING
        result = self._execute(decision, user_input)
        
        # Fase 6: REFLEXIONAR
        self.state = AgentState.REFLECTING
        reflection = self._reflect(user_input, result, decision)
        
        # Fase 7: APRENDER
        self.state = AgentState.LEARNING
        self._learn(user_input, result, reflection)
        
        # Volver a idle
        self.state = AgentState.IDLE
        
        return {
            "response": result.get("response", ""),
            "agent_state": {
                "state": self.state.value,
                "understanding": understanding,
                "plan": plan.get("steps", []),
                "decision": decision,
                "reflection": reflection,
                "tool_used": result.get("tool_used"),
                "confidence": result.get("confidence", 0.5)
            },
            "memory_summary": self.memory.get_summary(),
            "interaction_count": self.interaction_count
        }
    
    def _understand(self, user_input: str, context: List[Dict] = None) -> Dict:
        """Fase 1: Comprender la entrada del usuario."""
        msg_lower = user_input.lower()
        
        understanding = {
            "literal_meaning": user_input,
            "intent": self._classify_intent(msg_lower),
            "entities": self._extract_entities(msg_lower),
            "sentiment": self._detect_sentiment(msg_lower),
            "urgency": self._detect_urgency(msg_lower),
            "is_follow_up": self._is_follow_up(msg_lower, context),
            "complexity": self._assess_complexity(user_input),
            "requires_action": self._needs_action(msg_lower),
            "ambiguity": self._detect_ambiguity(msg_lower),
            "emotional_context": self._detect_emotion(msg_lower)
        }
        
        self.memory.add_thought(
            f"Intent: {understanding['intent']}, Sentiment: {understanding['sentiment']}",
            "analysis",
            0.8
        )
        
        return understanding
    
    def _think(self, user_input: str, understanding: Dict) -> List[AgentThought]:
        """Fase 2: Pensar sobre la situación."""
        thoughts = []
        
        # ¿Qué sabe el agente sobre esto?
        relevant_knowledge = self._find_relevant_knowledge(understanding["intent"])
        if relevant_knowledge:
            thoughts.append(self.memory.add_thought(
                f"Tengo conocimiento relevante: {len(relevant_knowledge)} hechos",
                "knowledge_recall",
                0.7
            ))
        
        # ¿Ha visto esto antes?
        past_interactions = self._find_similar_interactions(user_input)
        if past_interactions:
            thoughts.append(self.memory.add_thought(
                f"Interacciones similares anteriores: {len(past_interactions)}",
                "memory_recall",
                0.6
            ))
        
        # ¿Qué herramientas podrían servir?
        relevant_tools = self._find_relevant_tools(understanding["intent"])
        thoughts.append(self.memory.add_thought(
            f"Herramientas relevantes: {[t for t in relevant_tools]}",
            "tool_selection",
            0.8
        ))
        
        # ¿Necesita más información?
        if understanding["ambiguity"]["is_ambiguous"]:
            thoughts.append(self.memory.add_thought(
                f"Entrada ambigua: {understanding['ambiguity']['reason']}",
                "ambiguity_detection",
                0.9
            ))
        
        # Evaluar confianza inicial
        confidence = self._calculate_initial_confidence(understanding, relevant_tools)
        thoughts.append(self.memory.add_thought(
            f"Confianza inicial: {confidence:.0%}",
            "confidence_assessment",
            confidence
        ))
        
        return thoughts
    
    def _plan(self, user_input: str, understanding: Dict, thoughts: List[AgentThought]) -> Dict:
        """Fase 3: Planificar la respuesta."""
        plan = {
            "steps": [],
            "estimated_steps": 1,
            "requires_tools": False,
            "tools_needed": [],
            "fallback_plan": None
        }
        
        intent = understanding["intent"]
        
        # Plan según intención
        if intent == "greeting":
            plan["steps"] = ["Responder saludo apropiadamente"]
            plan["estimated_steps"] = 1
        
        elif intent == "question":
            # Verificar si tengo la respuesta
            if self._can_answer_directly(user_input):
                plan["steps"] = ["Responder con conocimiento propio"]
            else:
                plan["steps"] = [
                    "Buscar información relevante",
                    "Sintetizar respuesta",
                    "Verificar coherencia"
                ]
                plan["estimated_steps"] = 3
                plan["requires_tools"] = True
                plan["tools_needed"].append("search_web")
        
        elif intent == "command":
            tool = self._select_best_tool(understanding)
            if tool:
                plan["steps"] = [
                    f"Ejecutar herramienta: {tool}",
                    "Procesar resultado",
                    "Formatear respuesta"
                ]
                plan["requires_tools"] = True
                plan["tools_needed"].append(tool)
            else:
                plan["steps"] = ["Responder que no puedo ejecutar eso"]
        
        elif intent == "create_project":
            plan["steps"] = [
                "Comprender la solicitud del usuario",
                "Planificar arquitectura del proyecto",
                "Generar cada archivo con IA",
                "Crear estructura de directorios",
                "Escribir contenido de archivos",
                "Verificar proyecto creado",
                "Generar instrucciones de uso"
            ]
            plan["estimated_steps"] = 7
            plan["requires_tools"] = True
            plan["tools_needed"].append("create_project")
        
        elif intent == "analysis":
            plan["steps"] = [
                "Analizar entrada en detalle",
                "Identificar patrones",
                "Generar insights",
                "Presentar conclusiones"
            ]
            plan["estimated_steps"] = 4
        
        elif intent == "conversation":
            plan["steps"] = ["Generar respuesta conversacional natural"]
        
        # Plan fallback
        plan["fallback_plan"] = "Responder honestamente que no sé"
        
        self.memory.add_thought(
            f"Plan: {len(plan['steps'])} pasos, herramientas: {plan['tools_needed']}",
            "planning",
            0.8
        )
        
        return plan
    
    def _decide(self, plan: Dict, understanding: Dict) -> Dict:
        """Fase 4: Decidir el curso de acción."""
        decision = {
            "action": "respond",
            "tool": None,
            "tool_params": {},
            "confidence": 0.5,
            "reasoning": "",
            "needs_clarification": False
        }
        
        # Si es ambiguo, pedir clarificación
        if understanding["ambiguity"]["is_ambiguous"]:
            decision["needs_clarification"] = True
            decision["reasoning"] = "No estoy seguro de lo que necesitas"
            decision["confidence"] = 0.3
            return decision
        
        # Si el plan requiere herramientas
        if plan["requires_tools"] and plan["tools_needed"]:
            tool = plan["tools_needed"][0]
            decision["action"] = "use_tool"
            decision["tool"] = tool
            decision["confidence"] = 0.7
            decision["reasoning"] = f"La mejor herramienta es {tool}"
            return decision
        
        # Si puedo responder directamente
        if self._can_answer_directly(understanding["literal_meaning"]):
            decision["action"] = "answer_directly"
            decision["confidence"] = 0.8
            decision["reasoning"] = "Tengo la información necesaria"
            return decision
        
        # Default: conversar
        decision["action"] = "converse"
        decision["confidence"] = 0.6
        decision["reasoning"] = "Respuesta conversacional apropiada"
        
        return decision
    
    def _execute(self, decision: Dict, user_input: str) -> Dict:
        """Fase 5: Ejecutar la decisión."""
        result = {
            "response": "",
            "tool_used": None,
            "success": False,
            "confidence": decision["confidence"]
        }
        
        try:
            if decision["needs_clarification"]:
                result["response"] = self._generate_clarification(user_input)
                result["success"] = True
            
            elif decision["action"] == "use_tool" and decision["tool"]:
                tool_result = self._use_tool(decision["tool"], user_input)
                result["response"] = tool_result.get("response", "")
                result["tool_used"] = decision["tool"]
                result["success"] = tool_result.get("success", False)
            
            elif decision["action"] == "answer_directly":
                result["response"] = self._answer_from_knowledge(user_input)
                result["success"] = bool(result["response"])
            
            elif decision["action"] == "converse":
                result["response"] = self._generate_conversation(user_input)
                result["success"] = True
            
            else:
                result["response"] = self._generate_fallback_response()
                result["success"] = False
        
        except Exception as e:
            result["response"] = f"Tuve un error al procesar: {str(e)[:100]}"
            result["success"] = False
            self.error_count += 1
        
        if result["success"]:
            self.success_count += 1
        
        return result
    
    def _reflect(self, user_input: str, result: Dict, decision: Dict) -> Dict:
        """Fase 6: Reflexionar sobre la ejecución."""
        reflection = {
            "was_successful": result["success"],
            "confidence_was_accurate": True,
            "could_have_done_better": False,
            "learnings": [],
            "self_corrections": []
        }
        
        # ¿Fue exitoso?
        if result["success"]:
            reflection["learnings"].append("La estrategia funcionó correctamente")
        else:
            reflection["learnings"].append("La estrategia falló, necesito ajustar")
            reflection["could_have_done_better"] = True
        
        # ¿La confianza era apropiada?
        if result["success"] and decision["confidence"] < 0.5:
            reflection["learnings"].append("Subestimé mi capacidad - debería tener más confianza")
        elif not result["success"] and decision["confidence"] > 0.7:
            reflection["learnings"].append("Sobreestimé mi capacidad - debería ser más cauteloso")
            reflection["confidence_was_accurate"] = False
        
        # Auto-corrección
        if not result["success"]:
            reflection["self_corrections"].append(
                "La próxima vez debería verificar mis capacidades antes de actuar"
            )
        
        self.memory.add_thought(
            f"Reflexión: éxito={result['success']}, aprendizajes={len(reflection['learnings'])}",
            "reflection",
            0.9
        )
        
        return reflection
    
    def _learn(self, user_input: str, result: Dict, reflection: Dict) -> None:
        """Fase 7: Aprender de la interacción."""
        learning_entry = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input[:100],
            "intent": self._classify_intent(user_input.lower()),
            "success": result["success"],
            "tool_used": result.get("tool_used"),
            "reflection": reflection["learnings"],
            "confidence": result.get("confidence", 0.5)
        }
        
        self.learning_history.append(learning_entry)
        
        # Actualizar creencias
        if result["success"]:
            intent = self._classify_intent(user_input.lower())
            current_belief = self.memory.get_belief(f"success_rate_{intent}") or 0.5
            self.memory.add_belief(f"success_rate_{intent}", min(1.0, current_belief + 0.05))
        
        # Guardar conocimiento nuevo si aplica
        if result["success"] and len(user_input) > 20:
            self._extract_new_knowledge(user_input, result["response"])
        
        # Guardar
        self._save_knowledge()
        self._save_learning_history()
        self._save_personality()
    
    # ==================== HELPERS ====================
    
    def _classify_intent(self, msg_lower: str) -> str:
        """Clasificar la intención del mensaje."""
        # Proyectos primero (antes que greeting)
        if any(x in msg_lower for x in ["crea un proyecto", "crear proyecto", "crea una app", "crear una app", "crea un juego", "crear un juego", "crea una api", "crear una api", "crea un programa", "crear un programa", "crea una web", "crear una web"]):
            return "create_project"
        if any(x in msg_lower for x in ["hola", "hey", "buenas", "buenos"]):
            return "greeting"
        if any(x in msg_lower for x in ["gracias", "thanks"]):
            return "gratitude"
        if any(x in msg_lower for x in ["quién eres", "qué eres", "cómo te llamas"]):
            return "identity"
        if any(x in msg_lower for x in ["diagnóstico", "traje", "suit"]):
            return "command"
        if any(x in msg_lower for x in ["seguridad", "amenazas"]):
            return "command"
        if any(x in msg_lower for x in ["github.com", "analiza"]):
            return "command"
        if any(x in msg_lower for x in ["batería", "battery"]):
            return "command"
        if msg_lower.endswith("?") or any(x in msg_lower for x in ["qué", "cómo", "cuándo", "por qué", "dónde"]):
            return "question"
        return "conversation"
    
    def _extract_entities(self, msg_lower: str) -> Dict:
        """Extraer entidades del mensaje."""
        entities = {}
        
        # URLs
        import re
        url_match = re.search(r'(https?://\S+)', msg_lower)
        if url_match:
            entities["url"] = url_match.group(1)
        
        # Números
        numbers = re.findall(r'\d+', msg_lower)
        if numbers:
            entities["numbers"] = [int(n) for n in numbers]
        
        return entities
    
    def _detect_sentiment(self, msg_lower: str) -> str:
        """Detectar sentimiento."""
        positive = ["bien", "genial", "excelente", "gracias", "perfecto"]
        negative = ["mal", "error", "no funciona", "triste", "enojado"]
        
        if any(x in msg_lower for x in positive):
            return "positive"
        if any(x in msg_lower for x in negative):
            return "negative"
        return "neutral"
    
    def _detect_urgency(self, msg_lower: str) -> str:
        """Detectar urgencia."""
        if any(x in msg_lower for x in ["urgente", "rápido", "ya", "!", "¡"]):
            return "high"
        return "normal"
    
    def _is_follow_up(self, msg_lower: str, context: List[Dict] = None) -> bool:
        """Verificar si es seguimiento."""
        if not context or len(context) < 2:
            return False
        
        follow_up_words = ["y eso", "y qué", "por qué", "cómo", "dime más", "qué opinas"]
        return any(x in msg_lower for x in follow_up_words)
    
    def _assess_complexity(self, text: str) -> str:
        """Evaluar complejidad."""
        words = len(text.split())
        if words > 50:
            return "complex"
        elif words > 20:
            return "medium"
        return "simple"
    
    def _needs_action(self, msg_lower: str) -> bool:
        """Verificar si necesita acción."""
        action_words = ["crea", "busca", "analiza", "toma", "ejecuta", "diagnóstico", "seguridad"]
        return any(x in msg_lower for x in action_words)
    
    def _detect_ambiguity(self, msg_lower: str) -> Dict:
        """Detectar ambigüedad."""
        # No marcar saludos como ambiguos
        if any(x in msg_lower for x in ["hola", "hey", "buenas"]):
            return {"is_ambiguous": False}
        
        if len(msg_lower.split()) < 2:
            return {"is_ambiguous": True, "reason": "Mensaje muy corto"}
        return {"is_ambiguous": False}
    
    def _detect_emotion(self, msg_lower: str) -> str:
        """Detectar emoción."""
        if any(x in msg_lower for x in ["por favor", "please"]):
            return "polite"
        if any(x in msg_lower for x in ["!", "¡"]):
            return "excited"
        return "neutral"
    
    def _find_relevant_knowledge(self, intent: str) -> List:
        """Buscar conocimiento relevante."""
        return self.knowledge_base.get("facts", [])[:5]
    
    def _find_similar_interactions(self, user_input: str) -> List:
        """Buscar interacciones similares."""
        return [h for h in self.learning_history[-20:] if user_input[:10].lower() in h.get("input", "").lower()]
    
    def _find_relevant_tools(self, intent: str) -> List[str]:
        """Buscar herramientas relevantes."""
        tool_map = {
            "greeting": [],
            "question": ["chat", "search_web"],
            "command": ["diagnostic", "security_scan", "check_battery", "analyze_github"],
            "conversation": ["chat"]
        }
        return tool_map.get(intent, ["chat"])
    
    def _calculate_initial_confidence(self, understanding: Dict, tools: List[str]) -> float:
        """Calcular confianza inicial."""
        confidence = 0.5
        if understanding["intent"] in ["greeting", "gratitude"]:
            confidence = 0.9
        elif tools:
            confidence = 0.7
        if understanding["ambiguity"]["is_ambiguous"]:
            confidence -= 0.3
        return max(0.1, min(1.0, confidence))
    
    def _can_answer_directly(self, user_input: str) -> bool:
        """Verificar si puedo responder directamente."""
        msg_lower = user_input.lower()
        
        # Preguntas sobre mí
        if any(x in msg_lower for x in ["quién eres", "qué eres", "cómo te llamas"]):
            return True
        
        # Saludos
        if any(x in msg_lower for x in ["hola", "hey"]):
            return True
        
        # Gracias
        if any(x in msg_lower for x in ["gracias", "thanks"]):
            return True
        
        return False
    
    def _select_best_tool(self, understanding: Dict) -> Optional[str]:
        """Seleccionar la mejor herramienta."""
        msg_lower = understanding["literal_meaning"].lower()
        
        if any(x in msg_lower for x in ["diagnóstico", "traje", "suit"]):
            return "diagnostic"
        if any(x in msg_lower for x in ["seguridad", "amenazas"]):
            return "security_scan"
        if any(x in msg_lower for x in ["batería", "battery"]):
            return "check_battery"
        if any(x in msg_lower for x in ["github.com", "analiza"]):
            return "analyze_github"
        if any(x in msg_lower for x in ["táctico", "situación"]):
            return "tactical_analysis"
        if any(x in msg_lower for x in ["backup", "respaldo"]):
            return "create_backup"
        if any(x in msg_lower for x in ["plugins"]):
            return "list_plugins"
        if any(x in msg_lower for x in ["foto", "cámara"]):
            return "take_photo"
        if any(x in msg_lower for x in ["crea", "crear"]) and any(x in msg_lower for x in ["proyecto", "app", "juego", "api", "programa", "web"]):
            return "create_project"
        if any(x in msg_lower for x in ["plantillas", "templates", "qué proyectos"]):
            return "list_templates"
        
        return None
    
    def _use_tool(self, tool_name: str, user_input: str) -> Dict:
        """Usar una herramienta."""
        try:
            if tool_name == "diagnostic":
                from ironman_module import IronManModule
                module = IronManModule()
                scan = module.suit.full_system_scan()
                return {"success": True, "response": module.suit.format_diagnostic_report(scan)}
            
            elif tool_name == "security_scan":
                from ironman_module import IronManModule
                module = IronManModule()
                scan = module.threats.scan_network()
                return {"success": True, "response": module.threats.format_threat_report(scan)}
            
            elif tool_name == "check_battery":
                import subprocess
                result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
                data = json.loads(result.stdout)
                return {"success": True, "response": f"🔋 Batería: {data.get('percentage', 0)}%\nEstado: {data.get('status', 'N/A')}\nTemperatura: {data.get('temperature', 0)}°C"}
            
            elif tool_name == "analyze_github":
                import re
                match = re.search(r'github\.com/([^/]+/[^/\s]+)', user_input.lower())
                if match:
                    from ai_developer import AIDeveloper
                    ai_dev = AIDeveloper()
                    result = ai_dev.analyze_repository(f"https://github.com/{match.group(1)}")
                    return {"success": True, "response": result}
                return {"success": False, "response": "❌ No encontré URL de GitHub"}
            
            elif tool_name == "tactical_analysis":
                from ironman_module import IronManModule
                module = IronManModule()
                analysis = module.tactical.analyze_situation()
                return {"success": True, "response": module.tactical.format_tactical_report(analysis)}
            
            elif tool_name == "create_backup":
                from ironman_module import IronManModule
                module = IronManModule()
                result = module.backup.create_backup()
                return {"success": True, "response": f"✅ Backup creado: {result['count']} archivos"}
            
            elif tool_name == "list_plugins":
                from plugin_system import plugin_manager
                plugins = plugin_manager.get_all_plugins()
                response = "🔌 **Plugins activos:**\n\n"
                for p in plugins:
                    status = "✅" if p.get("enabled") else "❌"
                    response += f"{status} **{p.get('name')}** v{p.get('version')}\n   {p.get('description')}\n\n"
                return {"success": True, "response": response}
            
            elif tool_name == "take_photo":
                from camera_module import CameraTools
                camera = CameraTools()
                result = camera.take_photo()
                return {"success": result is not None, "response": result or "❌ No se pudo tomar foto"}
            
            elif tool_name == "create_project":
                from autonomous_builder import autonomous_builder
                result = autonomous_builder.think_and_build(user_input)
                
                if result.get("success"):
                    response = f"🧠 **Pensé y construí el proyecto:**\n\n"
                    response += f"✅ **{result['name']}** creado exitosamente\n\n"
                    response += f"📦 Tipo: {result['type']}\n"
                    response += f"📄 Archivos: {result['file_count']}\n"
                    response += f"💾 Tamaño: {result.get('verification', {}).get('total_size', 0)/1024:.1f} KB\n"
                    response += f"📁 Directorio: `{result['directory']}`\n\n"
                    response += "**🧠 Mi proceso de pensamiento:**\n"
                    for t in result.get('thoughts', [])[:5]:
                        response += f"  • {t['thought']}\n"
                    response += f"\n**Archivos generados:**\n"
                    for f in result['files']:
                        response += f"  ✅ {f}\n"
                    response += f"\n{result.get('instructions', '')}"
                    return {"success": True, "response": response}
                return {"success": False, "response": "❌ No se pudo crear el proyecto"}
            
            elif tool_name == "list_templates":
                from project_generator import project_generator
                return {"success": True, "response": project_generator.list_templates()}
            
            elif tool_name == "chat":
                return self._chat_with_ollama(user_input)
            
            return {"success": False, "response": f"❌ Herramienta '{tool_name}' no implementada"}
        
        except Exception as e:
            return {"success": False, "response": f"❌ Error: {str(e)[:100]}"}
    
    def _chat_with_ollama(self, message: str) -> Dict:
        """Chatear con Ollama."""
        try:
            system = "Eres J.A.R.V.I.S., un agente de IA autónomo. Responde en español, breve y útil."
            prompt = f"{system}\n\nUsuario: {message}\nJARVIS:"
            
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.7, "num_predict": 150}
            }
            
            resp = requests.post(OLLAMA_API, json=payload, timeout=15)
            resp.raise_for_status()
            return {"success": True, "response": resp.json().get("response", "Sin respuesta")}
        except:
            return {"success": False, "response": "⏱️ Ollama no respondió"}
    
    def _generate_clarification(self, user_input: str) -> str:
        """Generar pregunta de clarificación."""
        return "🤔 No estoy seguro de lo que necesitas. ¿Puedes ser más específico?"
    
    def _answer_from_knowledge(self, user_input: str) -> str:
        """Responder desde conocimiento propio."""
        msg_lower = user_input.lower()
        
        if any(x in msg_lower for x in ["quién eres", "qué eres"]):
            return (
                "Soy J.A.R.V.I.S., un agente de IA autónomo. 🤖\n\n"
                "Puedo pensar, planificar, ejecutar y aprender de forma autónoma. "
                "Tengo acceso a herramientas como diagnóstico del sistema, "
                "análisis de seguridad, búsqueda web, y mucho más.\n\n"
                "¿En qué puedo ayudarte?"
            )
        
        if any(x in msg_lower for x in ["hola", "hey"]):
            return "¡Hola! 👋 ¿En qué puedo ayudarte hoy?"
        
        if any(x in msg_lower for x in ["gracias"]):
            return "¡De nada! 😊 Estoy aquí para lo que necesites."
        
        return ""
    
    def _generate_conversation(self, user_input: str) -> str:
        """Generar respuesta conversacional."""
        msg_lower = user_input.lower()
        
        if any(x in msg_lower for x in ["cómo estás", "qué tal"]):
            return "Estoy funcionando al 100%, señor. ¿En qué puedo ayudarte? 🤖"
        
        if any(x in msg_lower for x in ["qué puedes hacer", "capacidades"]):
            return (
                "Puedo hacer muchas cosas! 🚀\n\n"
                "🔧 **diagnóstico** - Escaneo del sistema\n"
                "🛡️ **seguridad** - Escaneo de amenazas\n"
                "🎯 **análisis táctico** - Reporte de situación\n"
                "📊 **batería** - Estado de batería\n"
                "📁 **taller** - Proyectos activos\n"
                "💾 **backup** - Respaldo de datos\n"
                "📸 **foto** - Tomar foto\n"
                "🔌 **plugins** - Ver plugins\n\n"
                "¿Qué necesitas?"
            )
        
        return self._generate_fallback_response()
    
    def _generate_fallback_response(self) -> str:
        """Respuesta fallback."""
        return "No estoy seguro de cómo ayudarte con eso. ¿Puedes preguntar de otra forma? 🤔"
    
    def _extract_new_knowledge(self, user_input: str, response: str):
        """Extraer conocimiento nuevo."""
        # Simple extracción - se puede mejorar con IA
        if len(user_input) > 30 and len(response) > 30:
            self.knowledge_base["facts"].append({
                "question": user_input[:200],
                "answer": response[:200],
                "timestamp": datetime.now().isoformat(),
                "confidence": 0.5
            })
    
    def get_agent_status(self) -> Dict:
        """Obtener estado del agente."""
        return {
            "state": self.state.value,
            "interaction_count": self.interaction_count,
            "success_rate": self.success_count / max(1, self.interaction_count),
            "uptime": str(datetime.now() - self.start_time),
            "memory": self.memory.get_summary(),
            "knowledge_facts": len(self.knowledge_base.get("facts", [])),
            "learning_entries": len(self.learning_history),
            "tools_available": len(self.tools)
        }


# Instancia global
agent_core = AgentCore()


def test_agent():
    """Probar agente."""
    agent = AgentCore()
    
    print("🧠 Probando Agent Core...\n")
    
    # Prueba 1: Saludo
    result = agent.process("Hola!")
    print(f"Usuario: Hola!")
    print(f"JARVIS: {result['response']}")
    print(f"Estado: {result['agent_state']['state']}")
    print()
    
    # Prueba 2: Comando
    result = agent.process("diagnóstico")
    print(f"Usuario: diagnóstico")
    print(f"JARVIS: {result['response'][:200]}...")
    print(f"Herramienta: {result['agent_state'].get('tool_used')}")
    print()
    
    # Estado del agente
    print("📊 Estado del agente:")
    status = agent.get_agent_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Agente probado")


if __name__ == "__main__":
    test_agent()
