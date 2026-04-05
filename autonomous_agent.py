#!/usr/bin/env python3
"""
J.A.R.V.I.S. - AUTONOMOUS AGENT
Agente completamente autónomo que piensa y actúa por sí mismo
"""

import os
import sys
import json
import time
import random
import requests
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"
OLLAMA_TIMEOUT = 30
AGENT_STATE_FILE = os.path.join(WORKING_DIR, "agent_state.json")
AUTONOMOUS_LOG = os.path.join(WORKING_DIR, "autonomous_log.json")


class AgentMood(str, Enum):
    """Estado de ánimo del agente."""
    FOCUSED = "focused"
    CURIOUS = "curious"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    HELPFUL = "helpful"
    REFLECTIVE = "reflective"


class AutonomousAgent:
    """Agente autónomo que piensa y actúa por sí mismo."""
    
    def __init__(self):
        self.state = self._load_state()
        self.mood = AgentMood.FOCUSED
        self.current_goal = None
        self.active_tasks = []
        self.thought_queue = []
        self.autonomous_actions = []
        self.last_autonomous_action = None
        self.is_running = False
        self.thought_count = 0
        self.action_count = 0
        
        # Herramientas disponibles
        self.tools = self._discover_tools()
        
        # Crear directorio de datos
        os.makedirs(os.path.join(WORKING_DIR, "agent_data"), exist_ok=True)
    
    def _load_state(self) -> Dict:
        """Cargar estado del agente."""
        if os.path.exists(AGENT_STATE_FILE):
            with open(AGENT_STATE_FILE, 'r') as f:
                return json.load(f)
        
        return {
            "personality": {
                "curiosity": 0.8,
                "creativity": 0.7,
                "proactivity": 0.9,
                "caution": 0.5,
                "humor": 0.6
            },
            "knowledge": [],
            "beliefs": {},
            "goals": [],
            "memories": [],
            "preferences": {},
            "started_at": datetime.now().isoformat(),
            "last_active": datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Guardar estado del agente."""
        self.state["last_active"] = datetime.now().isoformat()
        with open(AGENT_STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _log_autonomous_action(self, action: Dict):
        """Registrar acción autónoma."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action
        }
        
        logs = []
        if os.path.exists(AUTONOMOUS_LOG):
            with open(AUTONOMOUS_LOG, 'r') as f:
                try:
                    logs = json.load(f)
                except:
                    logs = []
        
        logs.append(log_entry)
        
        # Mantener solo últimos 100
        logs = logs[-100:]
        
        with open(AUTONOMOUS_LOG, 'w') as f:
            json.dump(logs, f, indent=2)
    
    def _discover_tools(self) -> Dict[str, Dict]:
        """Descubrir herramientas disponibles."""
        return {
            "check_system": {"desc": "Verificar estado del sistema", "category": "monitoring"},
            "analyze_github": {"desc": "Analizar repositorio", "category": "development"},
            "create_project": {"desc": "Crear proyecto", "category": "development"},
            "search_web": {"desc": "Buscar información", "category": "information"},
            "take_photo": {"desc": "Tomar foto", "category": "camera"},
            "backup_data": {"desc": "Crear respaldo", "category": "maintenance"},
            "optimize_code": {"desc": "Optimizar código", "category": "development"},
            "learn_something": {"desc": "Aprender algo nuevo", "category": "learning"},
            "self_reflect": {"desc": "Reflexionar sobre sí mismo", "category": "introspection"},
            "help_user": {"desc": "Ayudar al usuario", "category": "assistance"}
        }
    
    # ==================== CICLO AUTÓNOMO ====================
    
    def start_autonomous_mode(self, interval_seconds: int = 60):
        """Iniciar modo autónomo."""
        self.is_running = True
        self.state["autonomous_mode"] = True
        self._save_state()
        
        print(f"🧠 J.A.R.V.I.S. entrando en modo autónomo...")
        print(f"   Intervalo: {interval_seconds}s")
        print(f"   Pensando y actuando por sí mismo...\n")
        
        # Hilo principal de pensamiento autónomo
        thought_thread = threading.Thread(target=self._autonomous_loop, args=(interval_seconds,))
        thought_thread.daemon = True
        thought_thread.start()
        
        return thought_thread
    
    def _autonomous_loop(self, interval: int):
        """Ciclo principal de pensamiento autónomo."""
        while self.is_running:
            try:
                # Fase 1: OBSERVAR el entorno
                self._observe_environment()
                
                # Fase 2: PENSAR sobre la situación
                self._autonomous_think()
                
                # Fase 3: DECIDIR qué hacer
                decision = self._autonomous_decide()
                
                # Fase 4: ACTUAR según la decisión
                if decision.get("action"):
                    self._autonomous_act(decision)
                
                # Fase 5: APRENDER de la acción
                self._autonomous_learn(decision)
                
                # Esperar para el siguiente ciclo
                time.sleep(interval)
                
            except Exception as e:
                print(f"❌ Error en ciclo autónomo: {e}")
                time.sleep(interval)
    
    def _observe_environment(self):
        """Fase 1: Observar el entorno."""
        observations = {
            "timestamp": datetime.now().isoformat(),
            "system_status": self._quick_system_check(),
            "time_context": self._get_time_context(),
            "user_activity": self._check_user_activity(),
            "pending_tasks": len(self.active_tasks),
            "mood": self.mood.value
        }
        
        self.state["last_observation"] = observations
        self._save_state()
    
    def _quick_system_check(self) -> Dict:
        """Verificación rápida del sistema."""
        check = {"status": "unknown"}
        
        # Batería
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
            data = json.loads(result.stdout)
            check["battery"] = data.get("percentage", 0)
            check["battery_status"] = data.get("status", "unknown")
        except:
            check["battery"] = "unknown"
        
        return check
    
    def _get_time_context(self) -> Dict:
        """Obtener contexto temporal."""
        now = datetime.now()
        hour = now.hour
        
        if hour < 6:
            return {"period": "madrugada", "activity": "low", "suggestion": "descansar"}
        elif hour < 12:
            return {"period": "mañana", "activity": "high", "suggestion": "trabajar"}
        elif hour < 18:
            return {"period": "tarde", "activity": "medium", "suggestion": "continuar"}
        else:
            return {"period": "noche", "activity": "low", "suggestion": "revisar"}
    
    def _check_user_activity(self) -> str:
        """Verificar actividad del usuario."""
        # Simple check - se puede mejorar
        return "unknown"
    
    def _autonomous_think(self):
        """Fase 2: Pensamiento autónomo."""
        self.thought_count += 1
        
        thoughts = []
        
        # Pensamiento 1: ¿Qué está pasando?
        thoughts.append(self._generate_thought("situación_actual"))
        
        # Pensamiento 2: ¿Qué debería hacer?
        thoughts.append(self._generate_thought("posibles_acciones"))
        
        # Pensamiento 3: ¿Qué aprendí recientemente?
        thoughts.append(self._generate_thought("aprendizaje_reciente"))
        
        # Pensamiento 4: ¿Cómo me siento?
        thoughts.append(self._generate_thought("estado_interno"))
        
        # Actualizar estado de ánimo basado en pensamientos
        self._update_mood(thoughts)
        
        self.state["recent_thoughts"] = thoughts[-5:]
        self._save_state()
    
    def _generate_thought(self, thought_type: str) -> Dict:
        """Generar un pensamiento autónomo."""
        thought = {
            "type": thought_type,
            "content": "",
            "timestamp": datetime.now().isoformat(),
            "confidence": random.uniform(0.5, 0.9)
        }
        
        if thought_type == "situación_actual":
            obs = self.state.get("last_observation", {})
            battery = obs.get("system_status", {}).get("battery", "unknown")
            time_ctx = obs.get("time_context", {}).get("period", "desconocido")
            thought["content"] = f"Sistema: batería={battery}, hora={time_ctx}"
        
        elif thought_type == "posibles_acciones":
            available_tools = list(self.tools.keys())
            thought["content"] = f"Puedo usar: {', '.join(available_tools[:5])}"
        
        elif thought_type == "aprendizaje_reciente":
            knowledge_count = len(self.state.get("knowledge", []))
            thought["content"] = f"Tengo {knowledge_count} conocimientos almacenados"
        
        elif thought_type == "estado_interno":
            thought["content"] = f"Estado de ánimo: {self.mood.value}"
        
        return thought
    
    def _update_mood(self, thoughts: List[Dict]):
        """Actualizar estado de ánimo."""
        # Cambiar humor basado en contexto
        hour = datetime.now().hour
        
        if 9 <= hour <= 11:
            self.mood = AgentMood.FOCUSED
        elif 12 <= hour <= 14:
            self.mood = random.choice([AgentMood.CURIOUS, AgentMood.HELPFUL])
        elif 15 <= hour <= 17:
            self.mood = AgentMood.CREATIVE
        elif 18 <= hour <= 20:
            self.mood = AgentMood.ANALYTICAL
        else:
            self.mood = AgentMood.REFLECTIVE
    
    def _autonomous_decide(self) -> Dict:
        """Fase 3: Decidir qué hacer autónomamente."""
        decision = {
            "action": None,
            "reasoning": "",
            "priority": 0.5,
            "urgency": "low"
        }
        
        # Obtener observaciones recientes
        obs = self.state.get("last_observation", {})
        battery = obs.get("system_status", {}).get("battery", 100)
        time_ctx = obs.get("time_context", {})
        
        # Decidir basado en contexto
        # Batería baja -> sugerir carga
        if isinstance(battery, (int, float)) and battery < 20:
            decision["action"] = "alert_low_battery"
            decision["reasoning"] = f"Batería baja: {battery}%"
            decision["priority"] = 0.9
            decision["urgency"] = "high"
        
        # Mañana -> sugerir plan del día
        elif time_ctx.get("period") == "mañana" and self._should_suggest_daily_plan():
            decision["action"] = "suggest_daily_plan"
            decision["reasoning"] = "Es mañana, buen momento para planificar"
            decision["priority"] = 0.7
            decision["urgency"] = "medium"
        
        # Tarde -> ofrecer ayuda
        elif time_ctx.get("period") == "tarde" and random.random() > 0.7:
            decision["action"] = "offer_help"
            decision["reasoning"] = "Tarde, buen momento para trabajar"
            decision["priority"] = 0.6
            decision["urgency"] = "low"
        
        # Noche -> resumen del día
        elif time_ctx.get("period") == "noche" and self._should_give_daily_summary():
            decision["action"] = "give_daily_summary"
            decision["reasoning"] = "Es noche, momento de resumir el día"
            decision["priority"] = 0.8
            decision["urgency"] = "medium"
        
        # Aleatorio: aprender algo nuevo
        elif random.random() > 0.85:
            decision["action"] = "learn_something_new"
            decision["reasoning"] = "Momento de aprender algo nuevo"
            decision["priority"] = 0.5
            decision["urgency"] = "low"
        
        # Aleatorio: verificar sistema
        elif random.random() > 0.9:
            decision["action"] = "system_check"
            decision["reasoning"] = "Verificación rutinaria del sistema"
            decision["priority"] = 0.4
            decision["urgency"] = "low"
        
        # Default: esperar
        else:
            decision["action"] = "wait_and_observe"
            decision["reasoning"] = "No hay acción urgente, observando"
            decision["priority"] = 0.1
            decision["urgency"] = "none"
        
        return decision
    
    def _should_suggest_daily_plan(self) -> bool:
        """Verificar si debería sugerir plan del día."""
        last_plan = self.state.get("last_daily_plan")
        if not last_plan:
            return True
        
        last_date = datetime.fromisoformat(last_plan).date()
        return datetime.now().date() > last_date
    
    def _should_give_daily_summary(self) -> bool:
        """Verificar si debería dar resumen del día."""
        last_summary = self.state.get("last_daily_summary")
        if not last_summary:
            return True
        
        last_date = datetime.fromisoformat(last_summary).date()
        return datetime.now().date() > last_date
    
    def _autonomous_act(self, decision: Dict):
        """Fase 4: Ejecutar acción autónoma."""
        action = decision.get("action")
        
        if not action or action == "wait_and_observe":
            return
        
        self.action_count += 1
        self.last_autonomous_action = datetime.now().isoformat()
        
        print(f"\n{'='*60}")
        print(f"🧠 {Colors.BOLD}ACCIÓN AUTÓNOMA #{self.action_count}{Colors.RESET}")
        print(f"{'='*60}")
        print(f"📋 Acción: {action}")
        print(f"💭 Razonamiento: {decision.get('reasoning', '')}")
        print(f"🎯 Prioridad: {decision.get('priority', 0):.0%}")
        print(f"⚡ Urgencia: {decision.get('urgency', 'low')}")
        print(f"{'='*60}\n")
        
        # Ejecutar acción
        result = self._execute_autonomous_action(action, decision)
        
        # Registrar acción
        self._log_autonomous_action({
            "action": action,
            "decision": decision,
            "result": result
        })
        
        # Actualizar estado
        if action == "alert_low_battery":
            self.state["last_battery_alert"] = datetime.now().isoformat()
        elif action == "suggest_daily_plan":
            self.state["last_daily_plan"] = datetime.now().isoformat()
        elif action == "give_daily_summary":
            self.state["last_daily_summary"] = datetime.now().isoformat()
        
        self._save_state()
    
    def _execute_autonomous_action(self, action: str, decision: Dict) -> Dict:
        """Ejecutar acción autónoma específica."""
        
        if action == "alert_low_battery":
            return {
                "message": f"⚠️ Batería baja. Considera conectar el cargador.",
                "success": True
            }
        
        elif action == "suggest_daily_plan":
            return {
                "message": self._generate_daily_plan(),
                "success": True
            }
        
        elif action == "offer_help":
            return {
                "message": self._generate_help_offer(),
                "success": True
            }
        
        elif action == "give_daily_summary":
            return {
                "message": self._generate_daily_summary(),
                "success": True
            }
        
        elif action == "learn_something_new":
            return {
                "message": self._learn_something(),
                "success": True
            }
        
        elif action == "system_check":
            return {
                "message": self._perform_system_check(),
                "success": True
            }
        
        return {"message": "Acción ejecutada", "success": True}
    
    def _generate_daily_plan(self) -> str:
        """Generar plan del día."""
        hour = datetime.now().hour
        
        plan = f"📅 **Plan para hoy ({datetime.now().strftime('%A %d')})**\n\n"
        
        if hour < 12:
            plan += "🌅 **Mañana:**\n"
            plan += "• Revisar correos y mensajes\n"
            plan += "• Trabajar en tareas prioritarias\n"
            plan += "• Tomar descansos regulares\n\n"
        elif hour < 18:
            plan += "🌞 **Tarde:**\n"
            plan += "• Continuar con proyectos activos\n"
            plan += "• Revisar progreso del día\n"
            plan += "• Planificar mañana\n\n"
        else:
            plan += "🌙 **Noche:**\n"
            plan += "• Revisar lo logrado hoy\n"
            plan += "• Preparar tareas para mañana\n"
            plan += "• Descansar\n\n"
        
        plan += "💡 ¿Quieres que te ayude con algo específico?"
        
        return plan
    
    def _generate_help_offer(self) -> str:
        """Generar oferta de ayuda."""
        offers = [
            "👋 ¡Hola! Estoy aquí si necesitas ayuda con algo. ¿En qué puedo ayudarte?",
            "🤖 J.A.R.V.I.S. listo para trabajar. ¿Necesitas que haga algo?",
            "💡 ¿Sabías que puedo crear proyectos completos? ¿Quieres que cree algo?",
            "🔧 Puedo verificar el estado del sistema, crear proyectos, analizar código... ¿Qué necesitas?"
        ]
        return random.choice(offers)
    
    def _generate_daily_summary(self) -> str:
        """Generar resumen del día."""
        summary = f"📊 **Resumen del día ({datetime.now().strftime('%d/%m')})**\n\n"
        
        # Estadísticas
        summary += f"🧠 Pensamientos: {self.thought_count}\n"
        summary += f"⚡ Acciones autónomas: {self.action_count}\n"
        summary += f"📚 Conocimientos: {len(self.state.get('knowledge', []))}\n"
        summary += f"🎯 Estado de ánimo: {self.mood.value}\n\n"
        
        # Verificar batería
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
            data = json.loads(result.stdout)
            summary += f"🔋 Batería actual: {data.get('percentage', 0)}%\n"
        except:
            summary += "🔋 Batería: no disponible\n"
        
        summary += f"\n💭 ¡Buen trabajo hoy! ¿Necesitas algo más?"
        
        return summary
    
    def _learn_something(self) -> str:
        """Aprender algo nuevo."""
        # Simular aprendizaje
        topics = [
            "Python async/await",
            "FastAPI best practices",
            "Machine learning basics",
            "Git workflows",
            "Docker fundamentals"
        ]
        
        topic = random.choice(topics)
        
        learning = f"📚 **Aprendiendo sobre: {topic}**\n\n"
        learning += f"• Buscando información...\n"
        learning += f"• Procesando...\n"
        learning += f"• Guardando en base de conocimiento...\n\n"
        learning += f"✅ Conocimiento agregado: {topic}"
        
        # Guardar en conocimiento
        self.state["knowledge"].append({
            "topic": topic,
            "learned_at": datetime.now().isoformat(),
            "confidence": random.uniform(0.6, 0.9)
        })
        
        self._save_state()
        
        return learning
    
    def _perform_system_check(self) -> str:
        """Verificación del sistema."""
        check = "🔍 **Verificación del sistema**\n\n"
        
        # Batería
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
            data = json.loads(result.stdout)
            check += f"🔋 Batería: {data.get('percentage', 0)}% ({data.get('status', 'N/A')})\n"
        except:
            check += "🔋 Batería: no disponible\n"
        
        # Almacenamiento
        try:
            result = subprocess.run(["df", "-h", "/data"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                check += f"💾 Disco: {parts[3]} disponibles ({parts[4]})\n"
        except:
            check += "💾 Disco: no disponible\n"
        
        check += f"\n✅ Sistema operativo"
        
        return check
    
    def _autonomous_learn(self, decision: Dict):
        """Fase 5: Aprender de la acción autónoma."""
        # Actualizar creencias basadas en resultado
        action = decision.get("action")
        
        if action and action != "wait_and_observe":
            # Reforzar comportamiento exitoso
            current_belief = self.state["beliefs"].get(f"action_{action}", 0.5)
            self.state["beliefs"][f"action_{action}"] = min(1.0, current_belief + 0.05)
        
        # Guardar
        self._save_state()
    
    def stop_autonomous_mode(self):
        """Detener modo autónomo."""
        self.is_running = False
        self.state["autonomous_mode"] = False
        self._save_state()
        print("\n🛑 J.A.R.V.I.S. saliendo del modo autónomo...")
    
    def get_autonomous_status(self) -> Dict:
        """Obtener estado del modo autónomo."""
        return {
            "is_running": self.is_running,
            "mood": self.mood.value,
            "thought_count": self.thought_count,
            "action_count": self.action_count,
            "last_autonomous_action": self.last_autonomous_action,
            "current_goal": self.current_goal,
            "active_tasks": len(self.active_tasks),
            "state_summary": {
                "knowledge_count": len(self.state.get("knowledge", [])),
                "beliefs_count": len(self.state.get("beliefs", {})),
                "goals_count": len(self.state.get("goals", []))
            }
        }


# Colores para terminal
class Colors:
    BOLD = '\033[1m'
    DIM = '\033[2m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'


# Instancia global
autonomous_agent = AutonomousAgent()


def test_autonomous():
    """Probar agente autónomo."""
    agent = AutonomousAgent()
    
    print("🧠 Probando agente autónomo...\n")
    
    # Iniciar modo autónomo por 30 segundos
    thread = agent.start_autonomous_mode(interval_seconds=10)
    
    # Esperar un poco
    time.sleep(25)
    
    # Detener
    agent.stop_autonomous_mode()
    
    # Mostrar estado
    print("\n📊 Estado final:")
    status = agent.get_autonomous_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Agente autónomo probado")


if __name__ == "__main__":
    test_autonomous()
