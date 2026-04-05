#!/usr/bin/env python3
"""
J.A.R.V.I.S. - MÓDULO IRON MAN
Funciones avanzadas tipo J.A.R.V.I.S. real de Tony Stark
"""

import os
import json
import time
import socket
import hashlib
import subprocess
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
IRONMAN_DIR = os.path.join(WORKING_DIR, "ironman_data")
os.makedirs(IRONMAN_DIR, exist_ok=True)


class SuitDiagnostics:
    """Diagnóstico del 'traje' - estado completo del dispositivo."""
    
    @staticmethod
    def full_system_scan() -> Dict:
        """Escaneo completo del sistema como diagnóstico de traje."""
        scan = {
            "timestamp": datetime.now().isoformat(),
            "status": "operational",
            "systems": {}
        }
        
        # Batería = Reactor Arc
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
            data = json.loads(result.stdout)
            scan["systems"]["arc_reactor"] = {
                "charge": data.get("percentage", 0),
                "status": data.get("status", "unknown"),
                "temperature": data.get("temperature", 0),
                "health": data.get("health", "unknown"),
                "status_icon": "🟢" if data.get("percentage", 0) > 50 else "🟡" if data.get("percentage", 0) > 20 else "🔴"
            }
        except:
            scan["systems"]["arc_reactor"] = {"status": "offline", "status_icon": "⚫"}
        
        # Almacenamiento = Sistemas de datos
        try:
            result = subprocess.run(["df", "-h", "/data"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                scan["systems"]["data_systems"] = {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "percent": parts[4],
                    "status_icon": "🟢" if int(parts[4].replace("%", "")) < 70 else "🟡" if int(parts[4].replace("%", "")) < 90 else "🔴"
                }
        except:
            scan["systems"]["data_systems"] = {"status": "offline", "status_icon": "⚫"}
        
        # RAM = Sistemas de procesamiento
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            mem = {}
            for line in lines[:5]:
                parts = line.split()
                mem[parts[0].rstrip(":")] = int(parts[1])
            
            total = mem.get("MemTotal", 0)
            available = mem.get("MemAvailable", 0)
            used = total - available
            percent = (used / total * 100) if total > 0 else 0
            
            scan["systems"]["processing"] = {
                "total_mb": total / 1024,
                "used_mb": used / 1024,
                "available_mb": available / 1024,
                "percent": round(percent, 1),
                "status_icon": "🟢" if percent < 70 else "🟡" if percent < 90 else "🔴"
            }
        except:
            scan["systems"]["processing"] = {"status": "offline", "status_icon": "⚫"}
        
        # Red = Sistemas de comunicación
        try:
            # Verificar conectividad
            socket.setdefaulttimeout(3)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect(("8.8.8.8", 53))
            scan["systems"]["comms"] = {
                "status": "online",
                "latency_ms": "low",
                "status_icon": "🟢"
            }
        except:
            scan["systems"]["comms"] = {
                "status": "offline",
                "status_icon": "🔴"
            }
        
        # CPU = Núcleo de energía
        try:
            with open("/proc/stat", "r") as f:
                line = f.readline()
            parts = line.split()
            idle = float(parts[4])
            total = sum(float(p) for p in parts[1:8])
            cpu_usage = ((total - idle) / total) * 100
            
            scan["systems"]["power_core"] = {
                "usage": round(cpu_usage, 1),
                "status_icon": "🟢" if cpu_usage < 70 else "🟡" if cpu_usage < 90 else "🔴"
            }
        except:
            scan["systems"]["power_core"] = {"status": "unknown", "status_icon": "⚫"}
        
        # Temperatura = Sistemas térmicos
        try:
            battery_temp = scan["systems"].get("arc_reactor", {}).get("temperature", 0)
            scan["systems"]["thermal"] = {
                "battery_temp_c": battery_temp,
                "status": "normal" if battery_temp < 40 else "warning" if battery_temp < 45 else "critical",
                "status_icon": "🟢" if battery_temp < 40 else "🟡" if battery_temp < 45 else "🔴"
            }
        except:
            scan["systems"]["thermal"] = {"status": "unknown", "status_icon": "⚫"}
        
        # Determinar estado general
        all_icons = [s.get("status_icon", "⚫") for s in scan["systems"].values()]
        if "🔴" in all_icons:
            scan["status"] = "critical"
        elif "🟡" in all_icons:
            scan["status"] = "warning"
        else:
            scan["status"] = "optimal"
        
        return scan
    
    @staticmethod
    def format_diagnostic_report(scan: Dict) -> str:
        """Formatear diagnóstico como reporte de traje."""
        systems = scan.get("systems", {})
        
        report = f"🦾 **DIAGNÓSTICO DEL TRAJE**\n\n"
        report += f"Estado general: {scan.get('status', 'unknown').upper()}\n\n"
        
        system_names = {
            "arc_reactor": "⚡ Reactor Arc (Batería)",
            "power_core": "🔥 Núcleo de Energía (CPU)",
            "processing": "🧠 Procesamiento (RAM)",
            "data_systems": "💾 Sistemas de Datos",
            "comms": "📡 Comunicaciones",
            "thermal": "🌡️ Sistemas Térmicos"
        }
        
        for key, name in system_names.items():
            if key in systems:
                sys_data = systems[key]
                icon = sys_data.get("status_icon", "⚫")
                
                if key == "arc_reactor":
                    detail = f"{sys_data.get('charge', 0)}% - {sys_data.get('status', 'N/A')}"
                elif key == "power_core":
                    detail = f"{sys_data.get('usage', 0)}% uso"
                elif key == "processing":
                    detail = f"{sys_data.get('used_mb', 0):.0f}MB / {sys_data.get('total_mb', 0):.0f}MB"
                elif key == "data_systems":
                    detail = f"{sys_data.get('used', '0')} / {sys_data.get('total', '0')}"
                elif key == "comms":
                    detail = sys_data.get("status", "N/A")
                elif key == "thermal":
                    detail = f"{sys_data.get('battery_temp_c', 0)}°C"
                else:
                    detail = "N/A"
                
                report += f"{icon} {name}: {detail}\n"
        
        return report


class ThreatDetector:
    """Detector de amenazas de seguridad."""
    
    @staticmethod
    def scan_network() -> Dict:
        """Escanear red en busca de amenazas."""
        result = {
            "timestamp": datetime.now().isoformat(),
            "threats": [],
            "open_ports": [],
            "connected_devices": [],
            "status": "secure"
        }
        
        # Escanear puertos comunes
        common_ports = [21, 22, 80, 443, 3306, 5432, 8080, 8443]
        localhost = "127.0.0.1"
        
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                if sock.connect_ex((localhost, port)) == 0:
                    result["open_ports"].append({
                        "port": port,
                        "service": ThreatDetector._get_service_name(port),
                        "risk": "low" if port in [80, 443, 22] else "medium"
                    })
                sock.close()
            except:
                pass
        
        # Verificar conexiones activas
        try:
            result_output = subprocess.run(
                ["netstat", "-tuln"],
                capture_output=True, text=True, timeout=5
            )
            connections = result_output.stdout.strip().split("\n")[2:]
            result["connected_devices"] = len([c for c in connections if "ESTABLISHED" in c])
        except:
            pass
        
        # Evaluar amenazas
        high_risk_ports = [p for p in result["open_ports"] if p.get("risk") == "high"]
        if high_risk_ports:
            result["threats"].append(f"Puertos de alto riesgo abiertos: {[p['port'] for p in high_risk_ports]}")
            result["status"] = "warning"
        
        return result
    
    @staticmethod
    def _get_service_name(port: int) -> str:
        services = {
            21: "FTP", 22: "SSH", 80: "HTTP", 443: "HTTPS",
            3306: "MySQL", 5432: "PostgreSQL", 8080: "HTTP-Alt",
            8443: "HTTPS-Alt"
        }
        return services.get(port, f"Unknown-{port}")
    
    @staticmethod
    def format_threat_report(scan: Dict) -> str:
        """Formatear reporte de amenazas."""
        report = f"🛡️ **REPORTE DE SEGURIDAD**\n\n"
        report += f"Estado: {scan.get('status', 'unknown').upper()}\n\n"
        
        if scan.get("open_ports"):
            report += f"📡 **Puertos abiertos:**\n"
            for p in scan["open_ports"]:
                risk_icon = "🟢" if p["risk"] == "low" else "🟡" if p["risk"] == "medium" else "🔴"
                report += f"  {risk_icon} Puerto {p['port']} ({p['service']}) - Riesgo: {p['risk']}\n"
            report += "\n"
        
        if scan.get("threats"):
            report += f"⚠️ **Amenazas detectadas:**\n"
            for t in scan["threats"]:
                report += f"  • {t}\n"
            report += "\n"
        
        report += f"📊 Dispositivos conectados: {scan.get('connected_devices', 0)}\n"
        
        return report


class TacticalAnalyzer:
    """Análisis táctico tipo J.A.R.V.I.S."""
    
    @staticmethod
    def analyze_situation() -> Dict:
        """Analizar la situación actual del usuario."""
        now = datetime.now()
        hour = now.hour
        
        analysis = {
            "timestamp": now.isoformat(),
            "time_context": "",
            "suggestions": [],
            "alerts": []
        }
        
        # Contexto temporal
        if hour < 6:
            analysis["time_context"] = "Madrugada"
            analysis["suggestions"].append("Es tarde, deberías descansar")
        elif hour < 12:
            analysis["time_context"] = "Mañana"
            analysis["suggestions"].append("Buen momento para tareas productivas")
        elif hour < 18:
            analysis["time_context"] = "Tarde"
            analysis["suggestions"].append("¿Cómo va tu día?")
        else:
            analysis["time_context"] = "Noche"
            analysis["suggestions"].append("Momento de revisar lo logrado hoy")
        
        # Verificar batería
        try:
            result = subprocess.run(["termux-battery-status"], capture_output=True, text=True, timeout=5)
            data = json.loads(result.stdout)
            battery = data.get("percentage", 0)
            
            if battery < 20:
                analysis["alerts"].append(f"⚠️ Batería crítica: {battery}%")
                analysis["suggestions"].append("Conecta el cargador pronto")
            elif battery < 50:
                analysis["alerts"].append(f"Batería media: {battery}%")
        except:
            pass
        
        # Verificar almacenamiento
        try:
            result = subprocess.run(["df", "-h", "/data"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                percent = int(parts[4].replace("%", ""))
                if percent > 90:
                    analysis["alerts"].append(f"⚠️ Almacenamiento casi lleno: {percent}%")
                    analysis["suggestions"].append("Libera espacio eliminando archivos innecesarios")
        except:
            pass
        
        return analysis
    
    @staticmethod
    def format_tactical_report(analysis: Dict) -> str:
        """Formatear reporte táctico."""
        report = f"🎯 **ANÁLISIS TÁCTICO**\n\n"
        report += f"📅 {analysis.get('time_context', 'N/A')} - {datetime.now().strftime('%H:%M')}\n\n"
        
        if analysis.get("alerts"):
            report += f"🚨 **Alertas:**\n"
            for alert in analysis["alerts"]:
                report += f"  {alert}\n"
            report += "\n"
        
        if analysis.get("suggestions"):
            report += f"💡 **Sugerencias:**\n"
            for sug in analysis["suggestions"]:
                report += f"  • {sug}\n"
        
        return report


class ProjectWorkshop:
    """Taller de proyectos tipo taller de Tony Stark."""
    
    @staticmethod
    def list_projects() -> List[Dict]:
        """Listar todos los proyectos activos."""
        projects_dir = os.path.join(WORKING_DIR, "projects")
        if not os.path.exists(projects_dir):
            return []
        
        projects = []
        for item in os.listdir(projects_dir):
            item_path = os.path.join(projects_dir, item)
            if os.path.isdir(item_path):
                # Contar archivos
                file_count = 0
                total_size = 0
                for root, dirs, files in os.walk(item_path):
                    for f in files:
                        file_count += 1
                        total_size += os.path.getsize(os.path.join(root, f))
                
                projects.append({
                    "name": item,
                    "path": item_path,
                    "files": file_count,
                    "size_mb": round(total_size / 1024 / 1024, 2),
                    "created": datetime.fromtimestamp(os.path.getctime(item_path)).strftime("%Y-%m-%d")
                })
        
        return projects
    
    @staticmethod
    def format_workshop_report(projects: List[Dict]) -> str:
        """Formatear reporte del taller."""
        report = f"🔧 **TALLER DE PROYECTOS**\n\n"
        
        if not projects:
            report += "No hay proyectos activos.\n"
            report += "Usa 'Crea un proyecto...' para empezar uno nuevo."
            return report
        
        report += f"Proyectos activos: {len(projects)}\n\n"
        
        for p in projects:
            report += f"📁 **{p['name']}**\n"
            report += f"   📄 {p['files']} archivos | 💾 {p['size_mb']} MB\n"
            report += f"   📅 Creado: {p['created']}\n\n"
        
        return report


class AutoBackup:
    """Sistema de backup automático."""
    
    @staticmethod
    def create_backup() -> Dict:
        """Crear backup de archivos importantes."""
        backup_dir = os.path.join(IRONMAN_DIR, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"jarvis_backup_{timestamp}"
        backup_path = os.path.join(backup_dir, backup_name)
        os.makedirs(backup_path, exist_ok=True)
        
        # Archivos a respaldar
        files_to_backup = [
            "memory.db",
            "learning.db",
            "plugins_registry.json",
            "user_profile.json",
            "personality.json"
        ]
        
        backed_up = []
        for filename in files_to_backup:
            src = os.path.join(WORKING_DIR, filename)
            if os.path.exists(src):
                dst = os.path.join(backup_path, filename)
                import shutil
                shutil.copy2(src, dst)
                backed_up.append(filename)
        
        # Crear metadata
        metadata = {
            "timestamp": timestamp,
            "files": backed_up,
            "count": len(backed_up)
        }
        
        with open(os.path.join(backup_path, "metadata.json"), "w") as f:
            json.dump(metadata, f, indent=2)
        
        return {
            "success": True,
            "path": backup_path,
            "files": backed_up,
            "count": len(backed_up)
        }
    
    @staticmethod
    def list_backups() -> List[Dict]:
        """Listar backups disponibles."""
        backup_dir = os.path.join(IRONMAN_DIR, "backups")
        if not os.path.exists(backup_dir):
            return []
        
        backups = []
        for item in os.listdir(backup_dir):
            item_path = os.path.join(backup_dir, item)
            if os.path.isdir(item_path):
                metadata_path = os.path.join(item_path, "metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, "r") as f:
                        metadata = json.load(f)
                    backups.append(metadata)
        
        return sorted(backups, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    @staticmethod
    def format_backup_report(backups: List[Dict]) -> str:
        """Formatear reporte de backups."""
        report = f"💾 **SISTEMA DE BACKUP**\n\n"
        
        if not backups:
            report += "No hay backups disponibles.\n"
            report += "Usa 'crear backup' para hacer uno."
            return report
        
        report += f"Backups disponibles: {len(backups)}\n\n"
        
        for b in backups[:5]:
            report += f"📦 **{b.get('timestamp', 'unknown')}**\n"
            report += f"   📄 {b.get('count', 0)} archivos\n\n"
        
        return report


class IronManModule:
    """Módulo principal Iron Man."""
    
    def __init__(self):
        self.suit = SuitDiagnostics()
        self.threats = ThreatDetector()
        self.tactical = TacticalAnalyzer()
        self.workshop = ProjectWorkshop()
        self.backup = AutoBackup()
    
    def process_command(self, command: str) -> str:
        """Procesar comando Iron Man."""
        cmd_lower = command.lower()
        
        # Diagnóstico del traje
        if any(x in cmd_lower for x in ["diagnóstico", "diagnostico", "traje", "suit", "estado completo"]):
            scan = self.suit.full_system_scan()
            return self.suit.format_diagnostic_report(scan)
        
        # Escaneo de seguridad
        if any(x in cmd_lower for x in ["seguridad", "security", "amenazas", "escanear red"]):
            scan = self.threats.scan_network()
            return self.threats.format_threat_report(scan)
        
        # Análisis táctico
        if any(x in cmd_lower for x in ["análisis táctico", "analisis tactico", "situación", "situacion", "reporte"]):
            analysis = self.tactical.analyze_situation()
            return self.tactical.format_tactical_report(analysis)
        
        # Taller de proyectos
        if any(x in cmd_lower for x in ["taller", "workshop", "mis proyectos", "proyectos activos"]):
            projects = self.workshop.list_projects()
            return self.workshop.format_workshop_report(projects)
        
        # Backup
        if any(x in cmd_lower for x in ["crear backup", "hacer backup", "respaldo"]):
            result = self.backup.create_backup()
            return f"✅ Backup creado:\n\n📦 {result['count']} archivos respaldados\n📁 {result['path']}"
        
        if any(x in cmd_lower for x in ["ver backups", "lista backups", "backups disponibles"]):
            backups = self.backup.list_backups()
            return self.backup.format_backup_report(backups)
        
        # Comando general Iron Man
        if any(x in cmd_lower for x in ["iron man", "modo iron", "activar protocolos"]):
            return (
                "🦾 **PROTOCOLOS IRON MAN ACTIVADOS**\n\n"
                "Comandos disponibles:\n\n"
                "🔧 **diagnóstico** - Escaneo completo del sistema\n"
                "🛡️ **seguridad** - Escaneo de amenazas\n"
                "🎯 **análisis táctico** - Reporte de situación\n"
                "📁 **taller** - Proyectos activos\n"
                "💾 **crear backup** - Respaldo de datos\n"
                "💾 **ver backups** - Backups disponibles\n\n"
                "¿Qué protocolo necesitas, señor?"
            )
        
        return None  # No es comando Iron Man


# Instancia global
ironman_module = IronManModule()


def test_ironman():
    """Probar módulo Iron Man."""
    module = IronManModule()
    
    print("🦾 Probando módulo Iron Man...\n")
    
    # Diagnóstico
    print("=== DIAGNÓSTICO ===")
    scan = module.suit.full_system_scan()
    print(module.suit.format_diagnostic_report(scan))
    
    # Táctico
    print("\n=== ANÁLISIS TÁCTICO ===")
    analysis = module.tactical.analyze_situation()
    print(module.tactical.format_tactical_report(analysis))
    
    # Taller
    print("\n=== TALLER ===")
    projects = module.workshop.list_projects()
    print(module.workshop.format_workshop_report(projects))
    
    print("\n✅ Módulo Iron Man probado")


if __name__ == "__main__":
    test_ironman()
