#!/usr/bin/env python3
"""
J.A.R.V.I.S. - AUTONOMOUS AGENT v2
Agente autónomo práctico que hace cosas útiles por sí mismo
"""

import os
import sys
import json
import time
import random
import requests
import threading
import subprocess
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"
OLLAMA_TIMEOUT = 30
AGENT_DATA_DIR = os.path.join(WORKING_DIR, "agent_data")
os.makedirs(AGENT_DATA_DIR, exist_ok=True)

AUTONOMOUS_STATE_FILE = os.path.join(AGENT_DATA_DIR, "autonomous_state.json")
AUTONOMOUS_LOG_FILE = os.path.join(AGENT_DATA_DIR, "autonomous_actions.json")


class AutonomousAgentV2:
    """Agente autónomo que hace cosas útiles por sí mismo."""
    
    def __init__(self):
        self.is_running = False
        self.state = self._load_state()
        self.action_count = 0
        self.thread = None
    
    def _load_state(self) -> Dict:
        """Cargar estado."""
        if os.path.exists(AUTONOMOUS_STATE_FILE):
            with open(AUTONOMOUS_STATE_FILE, 'r') as f:
                return json.load(f)
        
        return {
            "last_actions": {},
            "action_history": [],
            "system_checks": 0,
            "backups_created": 0,
            "projects_reviewed": 0,
            "code_optimized": 0,
            "knowledge_gained": 0,
            "issues_found": 0,
            "started_at": datetime.now().isoformat()
        }
    
    def _save_state(self):
        """Guardar estado."""
        with open(AUTONOMOUS_STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def _log_action(self, action: Dict):
        """Registrar acción."""
        self.state["action_history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": action
        })
        
        # Mantener últimos 50
        self.state["action_history"] = self.state["action_history"][-50:]
        self._save_state()
    
    # ==================== ACCIONES ÚTILES ====================
    
    def _check_critical_battery(self) -> Optional[Dict]:
        """Verificar batería crítica y actuar."""
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
            data = json.loads(result.stdout)
            level = data.get("percentage", 100)
            status = data.get("status", "unknown")
            
            # Si está muy baja y no cargando, alertar
            if level < 15 and status != "CHARGING":
                last_alert = self.state["last_actions"].get("battery_alert")
                if last_alert:
                    last_time = datetime.fromisoformat(last_alert)
                    if (datetime.now() - last_time).total_seconds() < 1800:  # 30 min
                        return None  # No alertar tan seguido
                
                self.state["last_actions"]["battery_alert"] = datetime.now().isoformat()
                self._save_state()
                
                return {
                    "type": "battery_alert",
                    "priority": "critical",
                    "message": f"⚠️ BATERÍA CRÍTICA: {level}% - Conecta el cargador ahora",
                    "action_taken": "Alerta enviada"
                }
        except:
            pass
        return None
    
    def _auto_backup(self) -> Optional[Dict]:
        """Backup automático de datos importantes."""
        last_backup = self.state["last_actions"].get("auto_backup")
        if last_backup:
            last_time = datetime.fromisoformat(last_backup)
            if (datetime.now() - last_time).total_seconds() < 3600:  # Cada hora
                return None
        
        # Archivos importantes para respaldar
        important_files = [
            "memory.db",
            "learning.db",
            "agent_data/autonomous_state.json",
            "plugins_registry.json"
        ]
        
        backup_dir = os.path.join(WORKING_DIR, "backups", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        os.makedirs(backup_dir, exist_ok=True)
        
        backed_up = []
        for filepath in important_files:
            src = os.path.join(WORKING_DIR, filepath)
            if os.path.exists(src):
                dst = os.path.join(backup_dir, os.path.basename(filepath))
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.copy2(src, dst)
                backed_up.append(filepath)
        
        if backed_up:
            self.state["last_actions"]["auto_backup"] = datetime.now().isoformat()
            self.state["backups_created"] += 1
            self._save_state()
            
            return {
                "type": "auto_backup",
                "priority": "normal",
                "message": f"💾 Backup automático: {len(backed_up)} archivos respaldados",
                "action_taken": f"Archivos: {', '.join(backed_up)}"
            }
        
        return None
    
    def _check_system_health(self) -> Optional[Dict]:
        """Verificar salud del sistema."""
        last_check = self.state["last_actions"].get("system_check")
        if last_check:
            last_time = datetime.fromisoformat(last_check)
            if (datetime.now() - last_time).total_seconds() < 600:  # Cada 10 min
                return None
        
        issues = []
        
        # Verificar almacenamiento
        try:
            result = subprocess.run(["df", "-h", "/data"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                percent = int(parts[4].replace("%", ""))
                if percent > 90:
                    issues.append(f"Almacenamiento casi lleno: {percent}%")
        except:
            pass
        
        # Verificar procesos de JARVIS
        try:
            result = subprocess.run(["pgrep", "-f", "jarvis_brain"], capture_output=True, text=True, timeout=5)
            if not result.stdout.strip():
                issues.append("BRAIN no está corriendo")
        except:
            pass
        
        # Verificar Ollama
        try:
            resp = requests.get("http://localhost:11434/", timeout=3)
            if resp.status_code != 200:
                issues.append("Ollama no responde")
        except:
            issues.append("Ollama no está disponible")
        
        self.state["last_actions"]["system_check"] = datetime.now().isoformat()
        self.state["system_checks"] += 1
        self._save_state()
        
        if issues:
            self.state["issues_found"] += len(issues)
            self._save_state()
            
            return {
                "type": "system_health",
                "priority": "high",
                "message": f"🔍 Problemas detectados: {len(issues)}",
                "action_taken": " | ".join(issues)
            }
        
        return None
    
    def _review_projects(self) -> Optional[Dict]:
        """Revisar proyectos y sugerir mejoras."""
        last_review = self.state["last_actions"].get("project_review")
        if last_review:
            last_time = datetime.fromisoformat(last_review)
            if (datetime.now() - last_time).total_seconds() < 3600:  # Cada hora
                return None
        
        projects_dir = os.path.join(WORKING_DIR, "projects")
        if not os.path.exists(projects_dir):
            return None
        
        projects = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
        
        if not projects:
            return None
        
        # Revisar un proyecto aleatorio
        project = random.choice(projects)
        project_path = os.path.join(projects_dir, project)
        
        # Contar archivos y tamaño
        file_count = 0
        total_size = 0
        for root, dirs, files in os.walk(project_path):
            for f in files:
                file_count += 1
                total_size += os.path.getsize(os.path.join(root, f))
        
        self.state["last_actions"]["project_review"] = datetime.now().isoformat()
        self.state["projects_reviewed"] += 1
        self._save_state()
        
        return {
            "type": "project_review",
            "priority": "low",
            "message": f"📁 Proyecto '{project}': {file_count} archivos, {total_size/1024:.1f} KB",
            "action_taken": "Revisión completada"
        }
    
    def _clean_temp_files(self) -> Optional[Dict]:
        """Limpiar archivos temporales."""
        last_clean = self.state["last_actions"].get("temp_clean")
        if last_clean:
            last_time = datetime.fromisoformat(last_clean)
            if (datetime.now() - last_time).total_seconds() < 1800:  # Cada 30 min
                return None
        
        cleaned = 0
        # Buscar archivos temp_*.py
        for f in os.listdir(WORKING_DIR):
            if f.startswith("temp_") and f.endswith(".py"):
                filepath = os.path.join(WORKING_DIR, f)
                try:
                    os.remove(filepath)
                    cleaned += 1
                except:
                    pass
        
        if cleaned > 0:
            self.state["last_actions"]["temp_clean"] = datetime.now().isoformat()
            self._save_state()
            
            return {
                "type": "temp_clean",
                "priority": "normal",
                "message": f"🧹 Limpieza: {cleaned} archivos temporales eliminados",
                "action_taken": f"Archivos eliminados: {cleaned}"
            }
        
        return None
    
    def _optimize_database(self) -> Optional[Dict]:
        """Optimizar bases de datos SQLite."""
        last_opt = self.state["last_actions"].get("db_optimize")
        if last_opt:
            last_time = datetime.fromisoformat(last_opt)
            if (datetime.now() - last_time).total_seconds() < 7200:  # Cada 2 horas
                return None
        
        db_files = ["memory.db", "learning.db"]
        optimized = []
        
        for db_file in db_files:
            db_path = os.path.join(WORKING_DIR, db_file)
            if os.path.exists(db_path):
                try:
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    conn.execute("VACUUM")
                    conn.close()
                    optimized.append(db_file)
                except:
                    pass
        
        if optimized:
            self.state["last_actions"]["db_optimize"] = datetime.now().isoformat()
            self.state["code_optimized"] += 1
            self._save_state()
            
            return {
                "type": "db_optimize",
                "priority": "normal",
                "message": f"⚡ Bases de datos optimizadas: {', '.join(optimized)}",
                "action_taken": "VACUUM ejecutado"
            }
        
        return None
    
    def _learn_from_interactions(self) -> Optional[Dict]:
        """Aprender de interacciones recientes."""
        last_learn = self.state["last_actions"].get("learning")
        if last_learn:
            last_time = datetime.fromisoformat(last_learn)
            if (datetime.now() - last_time).total_seconds() < 1800:  # Cada 30 min
                return None
        
        # Analizar historial de aprendizaje si existe
        learning_db_path = os.path.join(WORKING_DIR, "learning.db")
        if os.path.exists(learning_db_path):
            try:
                import sqlite3
                conn = sqlite3.connect(learning_db_path)
                c = conn.cursor()
                c.execute("SELECT COUNT(*) FROM command_log")
                total = c.fetchone()[0]
                c.execute("SELECT COUNT(*) FROM command_log WHERE success = 1")
                success = c.fetchone()[0]
                conn.close()
                
                if total > 0:
                    success_rate = success / total
                    self.state["last_actions"]["learning"] = datetime.now().isoformat()
                    self.state["knowledge_gained"] += 1
                    self._save_state()
                    
                    return {
                        "type": "learning_analysis",
                        "priority": "low",
                        "message": f"📊 Tasa de éxito: {success_rate:.0%} ({success}/{total} comandos)",
                        "action_taken": "Análisis completado"
                    }
            except:
                pass
        
        return None
    
    # ==================== CICLO PRINCIPAL ====================
    
    def start(self, interval_seconds: int = 60):
        """Iniciar modo autónomo."""
        self.is_running = True
        self.thread = threading.Thread(target=self._loop, args=(interval_seconds,), daemon=True)
        self.thread.start()
        print(f"🧠 J.A.R.V.I.S. en modo autónomo (cada {interval_seconds}s)")
        print("   Haciendo cosas útiles por sí mismo...\n")
    
    def stop(self):
        """Detener modo autónomo."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("\n🛑 Modo autónomo detenido")
    
    def _loop(self, interval: int):
        """Ciclo principal."""
        while self.is_running:
            try:
                # Ejecutar todas las acciones útiles y ver cuáles aplican
                actions = []
                
                # 1. Verificar batería crítica (prioridad máxima)
                action = self._check_critical_battery()
                if action: actions.append(action)
                
                # 2. Verificar salud del sistema
                action = self._check_system_health()
                if action: actions.append(action)
                
                # 3. Backup automático
                action = self._auto_backup()
                if action: actions.append(action)
                
                # 4. Limpiar temporales
                action = self._clean_temp_files()
                if action: actions.append(action)
                
                # 5. Optimizar bases de datos
                action = self._optimize_database()
                if action: actions.append(action)
                
                # 6. Revisar proyectos
                action = self._review_projects()
                if action: actions.append(action)
                
                # 7. Aprender de interacciones
                action = self._learn_from_interactions()
                if action: actions.append(action)
                
                # Mostrar acciones ejecutadas
                for action in actions:
                    self.action_count += 1
                    priority_icon = {"critical": "🔴", "high": "🟡", "normal": "🟢", "low": "🔵"}.get(action.get("priority", "low"), "⚪")
                    
                    print(f"\n{'='*60}")
                    print(f"{priority_icon} **ACCIÓN AUTÓNOMA #{self.action_count}**")
                    print(f"{'='*60}")
                    print(f"📋 Tipo: {action['type']}")
                    print(f"💬 {action['message']}")
                    print(f"✅ {action['action_taken']}")
                    print(f"{'='*60}")
                    
                    self._log_action(action)
                
                if not actions:
                    print(f"\n🧠 [{datetime.now().strftime('%H:%M:%S')}] Verificando... nada urgente necesario")
                
                time.sleep(interval)
                
            except Exception as e:
                print(f"\n❌ Error en ciclo autónomo: {e}")
                time.sleep(interval)
    
    def get_status(self) -> Dict:
        """Obtener estado."""
        return {
            "is_running": self.is_running,
            "action_count": self.action_count,
            "state_summary": {
                "system_checks": self.state.get("system_checks", 0),
                "backups_created": self.state.get("backups_created", 0),
                "projects_reviewed": self.state.get("projects_reviewed", 0),
                "code_optimized": self.state.get("code_optimized", 0),
                "knowledge_gained": self.state.get("knowledge_gained", 0),
                "issues_found": self.state.get("issues_found", 0)
            },
            "recent_actions": self.state.get("action_history", [])[-5:]
        }


# Instancia global
autonomous_agent_v2 = AutonomousAgentV2()


def test():
    """Probar agente."""
    agent = AutonomousAgentV2()
    
    print("🧠 Probando agente autónomo v2...\n")
    
    # Ejecutar acciones manualmente
    actions = []
    
    action = agent._check_critical_battery()
    if action: actions.append(action)
    
    action = agent._check_system_health()
    if action: actions.append(action)
    
    action = agent._auto_backup()
    if action: actions.append(action)
    
    action = agent._clean_temp_files()
    if action: actions.append(action)
    
    action = agent._optimize_database()
    if action: actions.append(action)
    
    print(f"\n✅ Acciones ejecutadas: {len(actions)}")
    for a in actions:
        print(f"  • {a['type']}: {a['message']}")
    
    print("\n✅ Prueba completada")


if __name__ == "__main__":
    test()
