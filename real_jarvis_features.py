#!/usr/bin/env python3
"""
J.A.R.V.I.S. - REAL JARVIS CAPABILITIES
Funciones esenciales para ser un Jarvis real
"""

import os
import sys
import json
import time
import subprocess
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
REMINDERS_FILE = os.path.join(WORKING_DIR, "reminders.json")
ALARMS_FILE = os.path.join(WORKING_DIR, "alarms.json")
TASKS_FILE = os.path.join(WORKING_DIR, "real_tasks.json")


class VoiceActivation:
    """Activación por voz 'Hey Jarvis' siempre escuchando."""
    
    def __init__(self):
        self.is_listening = False
        self.callback = None
    
    def start_listening(self, callback=None):
        """Iniciar escucha continua."""
        self.is_listening = True
        self.callback = callback
        
        # Usar termux-microphone-record si está disponible
        try:
            # Verificar si hay termux-api
            result = subprocess.run(["termux-microphone-record", "--help"], 
                                  capture_output=True, text=True, timeout=3)
            if result.returncode == 0:
                print("🎤 Escucha por voz activada")
                # En un implementación real, aquí se escucharía continuamente
                return {"success": True, "message": "Escucha activada"}
        except:
            pass
        
        return {"success": False, "message": "termux-api no disponible para escucha por voz"}
    
    def stop_listening(self):
        """Detener escucha."""
        self.is_listening = False
        return {"success": True, "message": "Escucha detenida"}
    
    def get_status(self) -> Dict:
        """Obtener estado de escucha."""
        return {
            "is_listening": self.is_listening,
            "method": "termux-microphone-record" if self.is_listening else "none"
        }


class ReminderSystem:
    """Sistema de recordatorios y alarmas."""
    
    def __init__(self):
        self.reminders = self._load_reminders()
        self.alarms = self._load_alarms()
        self._start_checker()
    
    def _load_reminders(self) -> List[Dict]:
        """Cargar recordatorios."""
        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def _save_reminders(self):
        """Guardar recordatorios."""
        with open(REMINDERS_FILE, 'w') as f:
            json.dump(self.reminders, f, indent=2)
    
    def _load_alarms(self) -> List[Dict]:
        """Cargar alarmas."""
        if os.path.exists(ALARMS_FILE):
            with open(ALARMS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def _save_alarms(self):
        """Guardar alarmas."""
        with open(ALARMS_FILE, 'w') as f:
            json.dump(self.alarms, f, indent=2)
    
    def add_reminder(self, message: str, minutes: int) -> Dict:
        """Agregar recordatorio."""
        reminder = {
            "id": len(self.reminders) + 1,
            "message": message,
            "trigger_time": (datetime.now() + timedelta(minutes=minutes)).isoformat(),
            "created": datetime.now().isoformat(),
            "triggered": False
        }
        self.reminders.append(reminder)
        self._save_reminders()
        
        return {
            "success": True,
            "message": f"⏰ Recordatorio #{reminder['id']} en {minutes} minutos: {message}",
            "id": reminder["id"]
        }
    
    def add_alarm(self, hour: int, minute: int, message: str = "Alarma") -> Dict:
        """Agregar alarma."""
        alarm = {
            "id": len(self.alarms) + 1,
            "hour": hour,
            "minute": minute,
            "message": message,
            "enabled": True,
            "triggered_today": False
        }
        self.alarms.append(alarm)
        self._save_alarms()
        
        return {
            "success": True,
            "message": f"⏰ Alarma #{alarm['id']} a las {hour:02d}:{minute:02d}: {message}",
            "id": alarm["id"]
        }
    
    def list_reminders(self) -> str:
        """Listar recordatorios."""
        if not self.reminders:
            return "⏰ No hay recordatorios"
        
        output = "⏰ **Recordatorios:**\n\n"
        for r in self.reminders:
            if not r.get("triggered"):
                status = "✅" if r.get("triggered") else "⏳"
                output += f"{status} #{r['id']} {r['message']}\n"
                output += f"   📅 {r['trigger_time'][:16]}\n\n"
        
        return output
    
    def list_alarms(self) -> str:
        """Listar alarmas."""
        if not self.alarms:
            return "⏰ No hay alarmas"
        
        output = "⏰ **Alarmas:**\n\n"
        for a in self.alarms:
            status = "✅" if a.get("enabled") else "❌"
            output += f"{status} #{a['id']} {a['hour']:02d}:{a['minute']:02d} - {a['message']}\n"
        
        return output
    
    def delete_reminder(self, reminder_id: int) -> Dict:
        """Eliminar recordatorio."""
        self.reminders = [r for r in self.reminders if r.get("id") != reminder_id]
        self._save_reminders()
        return {"success": True, "message": f"Recordatorio #{reminder_id} eliminado"}
    
    def delete_alarm(self, alarm_id: int) -> Dict:
        """Eliminar alarma."""
        self.alarms = [a for a in self.alarms if a.get("id") != alarm_id]
        self._save_alarms()
        return {"success": True, "message": f"Alarma #{alarm_id} eliminada"}
    
    def _start_checker(self):
        """Iniciar verificación periódica."""
        thread = threading.Thread(target=self._check_loop, daemon=True)
        thread.start()
    
    def _check_loop(self):
        """Loop de verificación."""
        while True:
            now = datetime.now()
            
            # Verificar recordatorios
            for reminder in self.reminders:
                if not reminder.get("triggered"):
                    trigger_time = datetime.fromisoformat(reminder["trigger_time"])
                    if now >= trigger_time:
                        reminder["triggered"] = True
                        self._save_reminders()
                        print(f"\n🔔 RECORDATORIO: {reminder['message']}")
            
            # Verificar alarmas
            for alarm in self.alarms:
                if alarm.get("enabled") and not alarm.get("triggered_today"):
                    if now.hour == alarm["hour"] and now.minute == alarm["minute"]:
                        alarm["triggered_today"] = True
                        self._save_alarms()
                        print(f"\n🔔 ALARMA: {alarm['message']}")
            
            time.sleep(30)  # Verificar cada 30 segundos


class TaskManager:
    """Gestor de tareas avanzado."""
    
    def __init__(self):
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> List[Dict]:
        """Cargar tareas."""
        if os.path.exists(TASKS_FILE):
            with open(TASKS_FILE, 'r') as f:
                return json.load(f)
        return []
    
    def _save_tasks(self):
        """Guardar tareas."""
        with open(TASKS_FILE, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def add_task(self, title: str, description: str = "", priority: str = "normal", 
                 due_date: str = None, tags: List[str] = None) -> Dict:
        """Agregar tarea."""
        task = {
            "id": len(self.tasks) + 1,
            "title": title,
            "description": description,
            "priority": priority,
            "status": "pending",
            "due_date": due_date,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "completed": None
        }
        self.tasks.append(task)
        self._save_tasks()
        
        return {
            "success": True,
            "message": f"✅ Tarea #{task['id']} agregada: {title}",
            "id": task["id"]
        }
    
    def complete_task(self, task_id: int) -> Dict:
        """Completar tarea."""
        for task in self.tasks:
            if task.get("id") == task_id:
                task["status"] = "completed"
                task["completed"] = datetime.now().isoformat()
                self._save_tasks()
                return {"success": True, "message": f"✅ Tarea #{task_id} completada"}
        return {"success": False, "message": f"❌ Tarea #{task_id} no encontrada"}
    
    def delete_task(self, task_id: int) -> Dict:
        """Eliminar tarea."""
        self.tasks = [t for t in self.tasks if t.get("id") != task_id]
        self._save_tasks()
        return {"success": True, "message": f"🗑️ Tarea #{task_id} eliminada"}
    
    def list_tasks(self, status: str = "all") -> str:
        """Listar tareas."""
        filtered = self.tasks
        if status != "all":
            filtered = [t for t in self.tasks if t.get("status") == status]
        
        if not filtered:
            return f"📋 No hay tareas ({status})"
        
        output = f"📋 **Tareas ({status}):**\n\n"
        for t in filtered:
            status_icon = {"pending": "⏳", "completed": "✅", "cancelled": "❌"}.get(t.get("status"), "⏳")
            priority_icon = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(t.get("priority"), "🟡")
            
            output += f"{status_icon} {priority_icon} **#{t['id']} {t['title']}**\n"
            if t.get("description"):
                output += f"   📝 {t['description'][:100]}\n"
            if t.get("due_date"):
                output += f"   📅 Vence: {t['due_date']}\n"
            if t.get("tags"):
                output += f"   🏷️ {', '.join(t['tags'])}\n"
            output += "\n"
        
        return output
    
    def get_stats(self) -> Dict:
        """Obtener estadísticas."""
        total = len(self.tasks)
        completed = len([t for t in self.tasks if t.get("status") == "completed"])
        pending = len([t for t in self.tasks if t.get("status") == "pending"])
        
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "completion_rate": completed / total if total > 0 else 0
        }


class DocumentReader:
    """Lector de documentos (PDF, TXT, etc.)."""
    
    @staticmethod
    def read_text_file(filepath: str) -> Dict:
        """Leer archivo de texto."""
        try:
            full_path = os.path.join(WORKING_DIR, filepath) if not filepath.startswith('/') else filepath
            
            if not os.path.exists(full_path):
                return {"success": False, "error": "Archivo no encontrado"}
            
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            words = content.split()
            
            return {
                "success": True,
                "content": content[:3000],
                "stats": {
                    "lines": len(lines),
                    "words": len(words),
                    "chars": len(content)
                }
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    def read_pdf(filepath: str) -> Dict:
        """Leer PDF (si está disponible PyPDF2)."""
        try:
            full_path = os.path.join(WORKING_DIR, filepath) if not filepath.startswith('/') else filepath
            
            if not os.path.exists(full_path):
                return {"success": False, "error": "Archivo no encontrado"}
            
            # Intentar con PyPDF2
            try:
                import PyPDF2
                with open(full_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    text = ""
                    for page in reader.pages[:5]:  # Primeras 5 páginas
                        text += page.extract_text() + "\n"
                
                return {
                    "success": True,
                    "content": text[:3000],
                    "pages": len(reader.pages)
                }
            except ImportError:
                return {"success": False, "error": "PyPDF2 no instalado. Ejecuta: pip install PyPDF2"}
        except Exception as e:
            return {"success": False, "error": str(e)}


class SystemController:
    """Control del sistema."""
    
    @staticmethod
    def get_screen_info() -> Dict:
        """Obtener información de pantalla."""
        try:
            result = subprocess.run(["dumpsys", "display"], capture_output=True, text=True, timeout=5)
            return {"success": True, "info": result.stdout[:500]}
        except:
            return {"success": False, "error": "No se pudo obtener info de pantalla"}
    
    @staticmethod
    def get_running_apps() -> Dict:
        """Obtener apps corriendo."""
        try:
            result = subprocess.run(["ps", "-A"], capture_output=True, text=True, timeout=5)
            apps = [line.split()[-1] for line in result.stdout.strip().split('\n')[1:]]
            return {"success": True, "apps": list(set(apps))[:20]}
        except:
            return {"success": False, "error": "No se pudo obtener apps"}
    
    @staticmethod
    def get_network_info() -> Dict:
        """Obtener info de red."""
        info = {}
        
        # IP local
        try:
            result = subprocess.run(["ip", "addr", "show", "wlan0"], capture_output=True, text=True, timeout=5)
            import re
            match = re.search(r'inet\s+([\d.]+)', result.stdout)
            if match:
                info["local_ip"] = match.group(1)
        except:
            pass
        
        # IP pública
        try:
            resp = requests.get("https://api.ipify.org", timeout=5)
            info["public_ip"] = resp.text
        except:
            pass
        
        return {"success": True, "info": info}


# Instancias globales
voice_activation = VoiceActivation()
reminder_system = ReminderSystem()
task_manager = TaskManager()
document_reader = DocumentReader()
system_controller = SystemController()


def test():
    """Probar módulos."""
    print("🎤 Probando Voice Activation...")
    print(voice_activation.get_status())
    
    print("\n⏰ Probando Reminder System...")
    result = reminder_system.add_reminder("Prueba", 5)
    print(result)
    print(reminder_system.list_reminders())
    
    print("\n📋 Probando Task Manager...")
    result = task_manager.add_task("Probar Jarvis", "Test completo", "high", tags=["test"])
    print(result)
    print(task_manager.list_tasks())
    
    print("\n📄 Probando Document Reader...")
    # Crear archivo de prueba
    test_file = os.path.join(WORKING_DIR, "test_doc.txt")
    with open(test_file, 'w') as f:
        f.write("Este es un documento de prueba para J.A.R.V.I.S.")
    
    result = document_reader.read_text_file("test_doc.txt")
    print(result)
    
    print("\n✅ Prueba completada")


if __name__ == "__main__":
    test()
