#!/usr/bin/env python3
"""
J.A.R.V.I.S. - CONTROL POR VOZ Y AUTOMATIZACIÓN
Speech-to-text, text-to-speech, y automatización avanzada
"""

import os
import json
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import threading
import sqlite3

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
VOICE_DB = os.path.join(WORKING_DIR, "automation.db")


# ==================== CONTROL POR VOZ ====================

class VoiceControl:
    """Control por voz para Termux/Android."""
    
    def __init__(self):
        self.tts_engine = "termux-tts-speech"
        self.stt_engine = "termux-speech-recognition"
    
    def text_to_speech(self, text: str, lang: str = "es-ES") -> str:
        """Convertir texto a voz."""
        try:
            # Usar termux-tts-speech
            subprocess.run(
                ["termux-tts-speech", text],
                timeout=30
            )
            return f"🔊 Reproduciendo: {text[:50]}..."
        except FileNotFoundError:
            # Fallback: guardar a archivo
            return self._save_tts_file(text)
        except Exception as e:
            return f"❌ Error TTS: {str(e)}"
    
    def _save_tts_file(self, text: str) -> str:
        """Guardar texto para TTS externo."""
        filepath = os.path.join(WORKING_DIR, f"tts_{int(time.time())}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        return f"📝 Texto guardado para TTS: {filepath}"
    
    def speech_to_text(self, timeout: int = 10) -> Optional[str]:
        """Convertir voz a texto."""
        try:
            result = subprocess.run(
                ["termux-speech-recognition"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
            return None
        except FileNotFoundError:
            return "❌ termux-speech-recognition no disponible"
        except subprocess.TimeoutExpired:
            return "⏱️ Timeout de reconocimiento de voz"
        except Exception as e:
            return f"❌ Error STT: {str(e)}"
    
    def voice_command(self, timeout: int = 10) -> Dict:
        """Escuchar comando de voz y ejecutar."""
        # Escuchar
        command = self.speech_to_text(timeout)
        
        if not command or command.startswith("❌") or command.startswith("⏱️"):
            return {"success": False, "command": None, "response": command}
        
        # Aquí se integraría con J.A.R.V.I.S. core
        return {
            "success": True,
            "command": command,
            "response": f"🎤 Escuché: '{command}'"
        }
    
    def set_tts_engine(self, engine: str):
        """Configurar motor TTS."""
        self.tts_engine = engine
    
    def list_tts_engines(self) -> List[str]:
        """Listar motores TTS disponibles."""
        engines = []
        
        # Verificar termux-tts-speech
        try:
            subprocess.run(["termux-tts-speech", "--help"], capture_output=True, timeout=3)
            engines.append("termux-tts-speech")
        except:
            pass
        
        # Verificar otros
        for cmd in ["espeak", "festival", "gtts"]:
            try:
                subprocess.run([cmd, "--version"], capture_output=True, timeout=3)
                engines.append(cmd)
            except:
                pass
        
        return engines
    
    def speak_notification(self, title: str, message: str):
        """Anunciar notificación por voz."""
        text = f"{title}. {message}"
        return self.text_to_speech(text)


# ==================== AUTOMATIZACIÓN ====================

class AutomationManager:
    """Gestor de automatizaciones y tareas programadas."""
    
    def __init__(self):
        self.init_db()
        self.scheduled_tasks = []
        self.triggers = []
    
    def init_db(self):
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS scheduled_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            command TEXT NOT NULL,
            schedule_type TEXT,
            schedule_time TIMESTAMP,
            enabled BOOLEAN DEFAULT 1,
            last_run TIMESTAMP,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS automation_triggers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            trigger_type TEXT,
            trigger_condition TEXT,
            action TEXT,
            enabled BOOLEAN DEFAULT 1,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')

        c.execute('''CREATE TABLE IF NOT EXISTS task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER,
            executed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN,
            result TEXT,
            FOREIGN KEY (task_id) REFERENCES scheduled_tasks(id)
        )''')
        
        conn.commit()
        conn.close()
    
    def schedule_task(self, name: str, command: str, schedule_type: str, 
                      schedule_time: str, enabled: bool = True) -> int:
        """Programar tarea."""
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        c.execute(
            """INSERT INTO scheduled_tasks (name, command, schedule_type, schedule_time, enabled) 
               VALUES (?, ?, ?, ?, ?)""",
            (name, command, schedule_type, schedule_time, enabled)
        )
        task_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_scheduled_tasks(self, enabled_only: bool = True) -> List[Dict]:
        """Obtener tareas programadas."""
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        
        if enabled_only:
            c.execute("SELECT * FROM scheduled_tasks WHERE enabled = 1 ORDER BY schedule_time")
        else:
            c.execute("SELECT * FROM scheduled_tasks ORDER BY created DESC")
        
        results = c.fetchall()
        conn.close()
        
        return [dict(zip(["id", "name", "command", "schedule_type", "schedule_time", 
                          "enabled", "last_run", "created"], r)) for r in results]
    
    def enable_task(self, task_id: int):
        """Activar tarea."""
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        c.execute("UPDATE scheduled_tasks SET enabled = 1 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
    
    def disable_task(self, task_id: int):
        """Desactivar tarea."""
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        c.execute("UPDATE scheduled_tasks SET enabled = 0 WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
    
    def delete_task(self, task_id: int):
        """Eliminar tarea."""
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        c.execute("DELETE FROM scheduled_tasks WHERE id = ?", (task_id,))
        conn.commit()
        conn.close()
    
    def add_trigger(self, name: str, trigger_type: str, trigger_condition: str, 
                    action: str) -> int:
        """Agregar trigger de automatización."""
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        c.execute(
            """INSERT INTO automation_triggers (name, trigger_type, trigger_condition, action) 
               VALUES (?, ?, ?, ?)""",
            (name, trigger_type, trigger_condition, action)
        )
        trigger_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return trigger_id
    
    def get_triggers(self, enabled_only: bool = True) -> List[Dict]:
        """Obtener triggers."""
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        
        if enabled_only:
            c.execute("SELECT * FROM automation_triggers WHERE enabled = 1")
        else:
            c.execute("SELECT * FROM automation_triggers")
        
        results = c.fetchall()
        conn.close()
        
        return [dict(zip(["id", "name", "trigger_type", "trigger_condition", "action", 
                          "enabled", "created"], r)) for r in results]
    
    def log_task_execution(self, task_id: int, success: bool, result: str):
        """Registrar ejecución de tarea."""
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        c.execute(
            """INSERT INTO task_history (task_id, success, result) 
               VALUES (?, ?, ?)""",
            (task_id, success, result)
        )
        c.execute(
            "UPDATE scheduled_tasks SET last_run = ? WHERE id = ?",
            (datetime.now().isoformat(), task_id)
        )
        conn.commit()
        conn.close()
    
    def get_task_history(self, task_id: int = None, limit: int = 50) -> List[Dict]:
        """Obtener historial de tareas."""
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        
        if task_id:
            c.execute(
                """SELECT * FROM task_history WHERE task_id = ? 
                   ORDER BY executed DESC LIMIT ?""",
                (task_id, limit)
            )
        else:
            c.execute(
                "SELECT * FROM task_history ORDER BY executed DESC LIMIT ?",
                (limit,)
            )
        
        results = c.fetchall()
        conn.close()
        
        return [dict(zip(["id", "task_id", "executed", "success", "result"], r)) 
                for r in results]
    
    def check_scheduled_tasks(self) -> List[Dict]:
        """Verificar tareas que deben ejecutarse."""
        now = datetime.now()
        tasks_to_run = []
        
        tasks = self.get_scheduled_tasks()
        
        for task in tasks:
            schedule_time = datetime.fromisoformat(task["schedule_time"])
            
            # Verificar si es hora de ejecutar
            should_run = False
            
            if task["schedule_type"] == "once":
                if schedule_time <= now and not task["last_run"]:
                    should_run = True
            
            elif task["schedule_type"] == "daily":
                if now.hour == schedule_time.hour and now.minute == schedule_time.minute:
                    if not task["last_run"] or \
                       datetime.fromisoformat(task["last_run"]).date() < now.date():
                        should_run = True
            
            elif task["schedule_type"] == "weekly":
                if (now.hour == schedule_time.hour and 
                    now.minute == schedule_time.minute and
                    now.weekday() == schedule_time.weekday()):
                    should_run = True
            
            if should_run:
                tasks_to_run.append(task)
        
        return tasks_to_run
    
    def get_automation_stats(self) -> Dict:
        """Obtener estadísticas de automatización."""
        stats = {}
        
        conn = sqlite3.connect(VOICE_DB)
        c = conn.cursor()
        
        # Tareas totales
        c.execute("SELECT COUNT(*) FROM scheduled_tasks")
        stats["total_tasks"] = c.fetchone()[0]
        
        # Tareas activas
        c.execute("SELECT COUNT(*) FROM scheduled_tasks WHERE enabled = 1")
        stats["active_tasks"] = c.fetchone()[0]
        
        # Triggers
        c.execute("SELECT COUNT(*) FROM automation_triggers WHERE enabled = 1")
        stats["active_triggers"] = c.fetchone()[0]
        
        # Ejecuciones totales
        c.execute("SELECT COUNT(*) FROM task_history")
        stats["total_executions"] = c.fetchone()[0]
        
        # Tasa de éxito
        c.execute("SELECT COUNT(*) FROM task_history WHERE success = 1")
        successful = c.fetchone()[0]
        stats["success_rate"] = successful / stats["total_executions"] if stats["total_executions"] > 0 else 0
        
        conn.close()
        
        return stats


# ==================== WORKFLOWS ====================

class WorkflowEngine:
    """Motor de workflows/automatizaciones complejas."""
    
    def __init__(self):
        self.workflows = {}
        self.automation = AutomationManager()
    
    def create_workflow(self, name: str, steps: List[Dict]) -> str:
        """Crear workflow."""
        workflow_id = f"wf_{name.lower().replace(' ', '_')}_{int(time.time())}"
        
        self.workflows[workflow_id] = {
            "name": name,
            "steps": steps,
            "created": datetime.now().isoformat()
        }
        
        return workflow_id
    
    def execute_workflow(self, workflow_id: str, context: Dict = None) -> Dict:
        """Ejecutar workflow."""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow no encontrado"}
        
        workflow = self.workflows[workflow_id]
        results = []
        
        if context is None:
            context = {}
        
        for i, step in enumerate(workflow["steps"]):
            step_type = step.get("type")
            step_action = step.get("action")
            
            # Ejecutar paso
            result = self._execute_step(step_type, step_action, context)
            results.append({"step": i + 1, "result": result})
            
            # Si falla y es crítico, detener
            if step.get("critical", False) and not result.get("success"):
                return {
                    "success": False,
                    "error": f"Paso {i + 1} falló",
                    "results": results
                }
        
        return {"success": True, "results": results}
    
    def _execute_step(self, step_type: str, action: str, context: Dict) -> Dict:
        """Ejecutar paso individual."""
        if step_type == "command":
            # Ejecutar comando de J.A.R.V.I.S.
            return {"success": True, "output": f"Comando: {action}"}
        
        elif step_type == "delay":
            # Esperar
            delay = int(action)
            time.sleep(delay)
            return {"success": True, "output": f"Esperado {delay}s"}
        
        elif step_type == "condition":
            # Evaluar condición
            return {"success": True, "output": f"Condición: {action}"}
        
        elif step_type == "notification":
            # Enviar notificación
            return {"success": True, "output": f"Notificación: {action}"}
        
        else:
            return {"success": False, "error": f"Tipo de paso desconocido: {step_type}"}
    
    def list_workflows(self) -> List[Dict]:
        """Listar workflows."""
        return [
            {"id": wf_id, "name": wf["name"], "steps": len(wf["steps"])}
            for wf_id, wf in self.workflows.items()
        ]


# ==================== INSTANCIAS GLOBALES ====================

voice_control = VoiceControl()
automation_manager = AutomationManager()
workflow_engine = WorkflowEngine()


def test_voice_automation():
    """Probar módulo de voz y automatización."""
    print("🎤 Probando Control por Voz y Automatización...")
    
    # Voz
    print("\n🔊 Control por Voz:")
    engines = voice_control.list_tts_engines()
    print(f"  Motores TTS disponibles: {engines}")
    
    # Automatización
    print("\n⏰ Automatización:")
    
    # Programar tarea de ejemplo
    task_id = automation_manager.schedule_task(
        name="Saludo matutino",
        command="buenos días",
        schedule_type="daily",
        schedule_time=datetime.now().replace(hour=8, minute=0).isoformat()
    )
    print(f"  Tarea programada ID: {task_id}")
    
    # Agregar trigger
    trigger_id = automation_manager.add_trigger(
        name="Batería baja",
        trigger_type="event",
        trigger_condition="battery < 20",
        action="notificar 'Batería baja'"
    )
    print(f"  Trigger agregado ID: {trigger_id}")
    
    # Workflow
    print("\n🔄 Workflows:")
    wf_id = workflow_engine.create_workflow(
        name="Buenos días",
        steps=[
            {"type": "command", "action": "batería", "critical": True},
            {"type": "delay", "action": "2", "critical": False},
            {"type": "command", "action": "clima", "critical": False},
            {"type": "notification", "action": "Reporte completado", "critical": False}
        ]
    )
    print(f"  Workflow creado: {wf_id}")
    
    # Estadísticas
    print("\n📊 Estadísticas:")
    stats = automation_manager.get_automation_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n✅ Módulo probado")


if __name__ == "__main__":
    test_voice_automation()
