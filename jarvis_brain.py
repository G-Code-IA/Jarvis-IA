#!/usr/bin/env python3
"""
J.A.R.V.I.S. BRAIN - Cerebro Central Unificado
Conecta Telegram, Dashboard, App, y todos los módulos
"""

import os
import sys
import json
import logging
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from contextlib import asynccontextmanager
from dataclasses import dataclass, asdict
from enum import Enum

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import requests
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JARVIS-BRAIN")

# Directorios
WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
WEB_DIR = os.path.join(WORKING_DIR, "web_dashboard")

# Importar módulos
sys.path.insert(0, WORKING_DIR)
from memory_system import memory_system, learning_system, MemorySystem, LearningSystem
from plugin_system import plugin_manager, PluginManager
from voice_automation import voice_control, automation_manager, workflow_engine
from camera_module import CameraTools
from ai_developer import AIDeveloper, CodeAnalyzer, CodeOptimizer
from reasoning_engine import reasoning_engine, ReasoningEngine
from conversational_engine import conversational_engine, ConversationalEngine
from ironman_module import ironman_module, IronManModule
from agent_core import agent_core, AgentCore
from autonomous_agent import autonomous_agent, AutonomousAgent
from model_manager import model_manager, ModelManager

# ==================== CONFIGURACIÓN ====================

class InterfaceType(str, Enum):
    TELEGRAM = "telegram"
    WEB = "web"
    APP = "app"
    API = "api"

@dataclass
class ClientSession:
    """Sesión de cliente conectado."""
    client_id: str
    interface: InterfaceType
    user_id: Optional[int] = None
    websocket: Optional[WebSocket] = None
    connected_at: datetime = None
    last_activity: datetime = None
    context: Dict = None
    
    def __post_init__(self):
        if self.connected_at is None:
            self.connected_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
        if self.context is None:
            self.context = {}

@dataclass
class BrainEvent:
    """Evento del cerebro para broadcast."""
    event_type: str
    source: str
    data: Dict
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

# ==================== MODELOS ====================

class CommandRequest(BaseModel):
    command: str
    interface: str = "api"
    user_id: Optional[int] = None
    context: Optional[Dict] = {}

class BroadcastRequest(BaseModel):
    message: str
    interfaces: Optional[List[str]] = ["all"]

class VoiceRequest(BaseModel):
    audio_base64: Optional[str] = None
    text: Optional[str] = None
    user_id: Optional[int] = None

# ==================== CEREBRO CENTRAL ====================

class JARVISBrain:
    """Cerebro central de J.A.R.V.I.S."""
    
    def __init__(self):
        self.sessions: Dict[str, ClientSession] = {}
        self.event_history: List[BrainEvent] = []
        self.max_history = 1000
        
        # Sistemas
        self.memory: MemorySystem = memory_system
        self.learning: LearningSystem = learning_system
        self.plugins: PluginManager = plugin_manager
        self.voice = voice_control
        self.automation = automation_manager
        self.workflows = workflow_engine
        self.camera = CameraTools()
        self.ai_dev = AIDeveloper()
        
        # Estado global
        self.global_context = {
            "active_users": set(),
            "total_commands": 0,
            "start_time": datetime.now(),
        }
        
        # Cargar plugins
        self.plugins.load_built_in_plugins()
        logger.info(f"✅ {len(self.plugins.loaded_plugins)} plugins cargados")
    
    def register_client(self, client_id: str, interface: InterfaceType, 
                       user_id: Optional[int] = None, websocket: WebSocket = None) -> ClientSession:
        """Registrar cliente conectado."""
        session = ClientSession(
            client_id=client_id,
            interface=interface,
            user_id=user_id,
            websocket=websocket
        )
        self.sessions[client_id] = session
        self.global_context["active_users"].add(client_id)
        
        logger.info(f"🔌 Cliente registrado: {client_id} ({interface.value})")
        return session
    
    def unregister_client(self, client_id: str):
        """Eliminar cliente."""
        if client_id in self.sessions:
            del self.sessions[client_id]
            self.global_context["active_users"].discard(client_id)
            logger.info(f"🔌 Cliente desconectado: {client_id}")
    
    def update_activity(self, client_id: str):
        """Actualizar actividad de cliente."""
        if client_id in self.sessions:
            self.sessions[client_id].last_activity = datetime.now()
    
    async def broadcast_event(self, event: BrainEvent, exclude: List[str] = None):
        """Broadcast de evento a todos los clientes."""
        if exclude is None:
            exclude = []
        
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history = self.event_history[-self.max_history:]
        
        event_data = {
            "type": "event",
            "event": asdict(event)
        }
        
        for client_id, session in list(self.sessions.items()):
            if client_id in exclude:
                continue
            
            if session.websocket:
                try:
                    await session.websocket.send_json(event_data)
                except:
                    pass
        
        logger.info(f"📢 Broadcast: {event.event_type} a {len(self.sessions) - len(exclude)} clientes")
    
    async def send_to_interface(self, interface: InterfaceType, data: Dict, exclude: List[str] = None):
        """Enviar a interfaz específica."""
        if exclude is None:
            exclude = []
        
        for client_id, session in list(self.sessions.items()):
            if client_id in exclude:
                continue
            if session.interface == interface and session.websocket:
                try:
                    await session.websocket.send_json(data)
                except:
                    pass
    
    def process_command(self, command: str, interface: str = "api", 
                       user_id: Optional[int] = None, context: List = None) -> Dict:
        """Procesar comando con agente de IA autónomo."""
        start_time = time.time()
        
        # 🧠 Usar Agent Core para procesamiento autónomo
        agent_result = agent_core.process(command, context)
        
        response = agent_result["response"]
        execution_time = time.time() - start_time
        
        # Guardar en memoria compartida
        if agent_result.get("agent_state", {}).get("tool_used"):
            self.memory.add_short_term(command, f"command_{interface}")
            self.memory.add_conversation(user_id or 0, command, response)
            self.learning.log_command(command, True, execution_time, "positive")
        
        self.global_context["total_commands"] += 1
        
        # Broadcast
        event = BrainEvent(
            event_type="command_executed",
            source=interface,
            data={"command": command, "response": response, "user_id": user_id, "execution_time": execution_time}
        )
        asyncio.create_task(self.broadcast_event(event, exclude=[]))
        
        return {
            "response": response,
            "execution_time": execution_time,
            "interface": interface,
            "timestamp": datetime.now().isoformat(),
            "agent": agent_result.get("agent_state", {}),
            "conversation": {
                "is_follow_up": agent_result.get("agent_state", {}).get("understanding", {}).get("is_follow_up", False),
                "history": agent_result.get("memory_summary", {}).get("recent_thoughts", [])
            },
            "context": {"messages": self.memory.get_conversation_history(user_id or 0, 10)}
        }
    
    def get_brain_status(self) -> Dict:
        """Estado completo del cerebro."""
        uptime = datetime.now() - self.global_context["start_time"]
        
        return {
            "status": "online",
            "version": "3.0.0",
            "uptime": str(uptime),
            "connected_clients": len(self.sessions),
            "active_interfaces": list(set(s.interface.value for s in self.sessions.values())),
            "total_commands": self.global_context["total_commands"],
            "memory": self.memory.get_memory_stats(),
            "learning": self.learning.get_performance_stats(),
            "plugins": self.plugins.get_plugin_stats(),
            "automation": self.automation.get_automation_stats(),
        }
    
    def get_session_info(self, client_id: str) -> Optional[Dict]:
        """Información de sesión."""
        if client_id in self.sessions:
            session = self.sessions[client_id]
            return {
                "client_id": session.client_id,
                "interface": session.interface.value,
                "user_id": session.user_id,
                "connected_at": session.connected_at.isoformat(),
                "last_activity": session.last_activity.isoformat(),
                "context": session.context
            }
        return None
    
    def cleanup_inactive_sessions(self, timeout_minutes: int = 60):
        """Limpiar sesiones inactivas."""
        now = datetime.now()
        to_remove = []
        
        for client_id, session in self.sessions.items():
            if (now - session.last_activity).total_seconds() > timeout_minutes * 60:
                to_remove.append(client_id)
        
        for client_id in to_remove:
            self.unregister_client(client_id)
        
        if to_remove:
            logger.info(f"🧹 {len(to_remove)} sesiones inactivas eliminadas")


# ==================== INSTANCIA GLOBAL ====================

brain = JARVISBrain()

# ==================== FASTAPI APP ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🧠 Iniciando J.A.R.V.I.S. BRAIN v3.0...")
    
    # Iniciar limpieza periódica
    async def cleanup_task():
        while True:
            await asyncio.sleep(300)  # Cada 5 minutos
            brain.cleanup_inactive_sessions()
    
    asyncio.create_task(cleanup_task())
    
    logger.info("✅ J.A.R.V.I.S. BRAIN v3.0 listo")
    yield
    
    # Shutdown
    logger.info("Apagando J.A.R.V.I.S. BRAIN...")

app = FastAPI(
    title="J.A.R.V.I.S. BRAIN",
    description="Cerebro Central Unificado - Telegram, Web, App",
    version="3.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== WEBSOCKET ====================

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket para conexión en tiempo real."""
    await websocket.accept()
    
    # Registrar cliente
    interface = InterfaceType.API
    brain.register_client(client_id, interface, websocket=websocket)
    
    # Enviar estado inicial
    await websocket.send_json({
        "type": "connected",
        "client_id": client_id,
        "brain_status": brain.get_brain_status()
    })
    
    try:
        while True:
            data = await websocket.receive_json()
            brain.update_activity(client_id)
            
            # Manejar diferentes tipos de mensajes
            msg_type = data.get("type", "command")
            
            if msg_type == "command":
                result = brain.process_command(
                    command=data.get("command", ""),
                    interface="websocket",
                    user_id=data.get("user_id"),
                    context=data.get("context", [])
                )
                await websocket.send_json({
                    "type": "response",
                    "data": result
                })
            
            elif msg_type == "subscribe":
                # Suscribirse a eventos
                await websocket.send_json({
                    "type": "subscribed",
                    "events": ["command_executed", "system_event"]
                })
            
            elif msg_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
    
    except WebSocketDisconnect:
        brain.unregister_client(client_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        brain.unregister_client(client_id)

# ==================== ENDPOINTS ====================

@app.get("/")
async def root():
    return {
        "name": "J.A.R.V.I.S. BRAIN",
        "version": "3.0.0",
        "status": "online",
        "description": "Cerebro Central Unificado",
        "interfaces": ["Telegram", "Web Dashboard", "Android App", "API Directa"],
        "websocket": "/ws/{client_id}",
        "docs": "/docs"
    }

@app.get("/brain/status")
async def get_brain_status():
    """Estado completo del cerebro"""
    return brain.get_brain_status()

@app.get("/brain/sessions")
async def get_sessions():
    """Sesiones activas"""
    return {
        "sessions": [
            {
                "client_id": s.client_id,
                "interface": s.interface.value,
                "last_activity": s.last_activity.isoformat()
            }
            for s in brain.sessions.values()
        ]
    }

@app.get("/brain/memory/stats")
async def get_memory_stats():
    return brain.memory.get_memory_stats()

@app.get("/brain/learning/stats")
async def get_learning_stats():
    return brain.learning.get_performance_stats()

@app.get("/brain/plugins")
async def get_plugins():
    return {"plugins": brain.plugins.get_all_plugins()}

@app.get("/brain/plugins/commands")
async def get_plugin_commands():
    return {"commands": brain.plugins.get_all_commands()}

@app.post("/brain/command")
async def execute_command(request: CommandRequest):
    """Ejecutar comando desde cualquier interfaz"""
    result = brain.process_command(
        command=request.command,
        interface=request.interface,
        user_id=request.user_id,
        context=request.context.get("messages", [])
    )
    return result

@app.post("/brain/broadcast")
async def broadcast_message(request: BroadcastRequest):
    """Broadcast a interfaces"""
    event = BrainEvent(
        event_type="broadcast",
        source="api",
        data={"message": request.message}
    )
    
    interfaces = [InterfaceType(i) for i in request.interfaces] if request.interfaces != ["all"] else list(InterfaceType)
    
    for interface in interfaces:
        await brain.send_to_interface(interface, {"type": "broadcast", "message": request.message})
    
    return {"success": True, "interfaces": [i.value for i in interfaces]}

# ==================== CÁMARA ====================

@app.post("/brain/camera/take")
async def take_photo():
    result = brain.camera.take_photo()
    return {"success": result is not None, "filepath": result}

@app.get("/brain/camera/photos")
async def list_photos():
    return {"photos": brain.camera.list_photos()}

@app.post("/brain/camera/analyze")
async def analyze_image(filepath: str, prompt: str = "Describe esta imagen"):
    result = brain.camera.analyze_image(filepath, prompt)
    return {"analysis": result}

# ==================== AUTOMATIZACIÓN ====================

@app.get("/brain/automation/tasks")
async def get_tasks():
    return {"tasks": brain.automation.get_scheduled_tasks()}

@app.post("/brain/automation/task")
async def schedule_task(name: str, command: str, schedule_type: str, schedule_time: str):
    task_id = brain.automation.schedule_task(name, command, schedule_type, schedule_time)
    return {"success": True, "task_id": task_id}

@app.get("/brain/automation/stats")
async def get_automation_stats():
    return brain.automation.get_automation_stats()

@app.get("/brain/reasoning")
async def get_reasoning_stats():
    """Estadísticas de razonamiento"""
    return {
        "reasoning": reasoning_engine.get_thought_summary(),
        "recent_thoughts": reasoning_engine.thought_history[-5:]
    }

@app.post("/brain/autonomous/start")
async def start_autonomous_mode(interval: int = 60):
    """Iniciar modo autónomo"""
    autonomous_agent.start_autonomous_mode(interval)
    return {"success": True, "message": f"Modo autónomo iniciado (intervalo: {interval}s)"}

@app.post("/brain/autonomous/stop")
async def stop_autonomous_mode():
    """Detener modo autónomo"""
    autonomous_agent.stop_autonomous_mode()
    return {"success": True, "message": "Modo autónomo detenido"}

@app.get("/brain/autonomous/status")
async def get_autonomous_status():
    """Estado del modo autónomo"""
    return autonomous_agent.get_autonomous_status()

@app.get("/brain/models")
async def list_models():
    """Listar modelos disponibles"""
    return model_manager.list_available_models()

@app.get("/brain/models/status")
async def get_models_status():
    """Estado de modelos"""
    return model_manager.get_status()

@app.get("/brain/models/recommendations")
async def get_model_recommendations():
    """Recomendaciones de modelos"""
    return {"recommendations": model_manager.get_model_recommendations()}

@app.post("/brain/models/install")
async def install_model(model_name: str):
    """Instalar modelo"""
    return model_manager.install_model(model_name)

@app.post("/brain/models/set-default")
async def set_default_model(model_name: str):
    """Cambiar modelo por defecto"""
    return model_manager.set_default_model(model_name)

@app.post("/brain/models/set-task")
async def set_task_model(task: str, model_name: str):
    """Cambiar modelo para tarea"""
    return model_manager.set_task_model(task, model_name)

# ==================== STATIC FILES ====================

if os.path.exists(WEB_DIR):
    app.mount("/dashboard", StaticFiles(directory=WEB_DIR, html=True), name="dashboard")

# Servir brain.html directamente en /
@app.get("/brain-dashboard")
async def serve_brain_dashboard():
    """Servir brain.html directamente"""
    brain_path = os.path.join(WEB_DIR, "brain.html")
    if os.path.exists(brain_path):
        with open(brain_path, 'r', encoding='utf-8') as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse("<h1>brain.html no encontrado</h1>")

# ==================== MAIN ====================

if __name__ == "__main__":
    logger.info("🧠 Iniciando J.A.R.V.I.S. BRAIN en puerto 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
