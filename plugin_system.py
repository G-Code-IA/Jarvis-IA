#!/usr/bin/env python3
"""
J.A.R.V.I.S. - SISTEMA DE PLUGINS
Arquitectura extensible para agregar capacidades ilimitadas
"""

import os
import sys
import json
import importlib
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
PLUGINS_DIR = os.path.join(WORKING_DIR, "plugins")
PLUGINS_REGISTRY = os.path.join(WORKING_DIR, "plugins_registry.json")

os.makedirs(PLUGINS_DIR, exist_ok=True)


# ==================== REGISTRO DE PLUGINS ====================

class PluginRegistry:
    """Registro y gestor de plugins."""
    
    def __init__(self):
        self.plugins = {}
        self.load_registry()
    
    def load_registry(self):
        """Cargar registro de plugins."""
        if os.path.exists(PLUGINS_REGISTRY):
            with open(PLUGINS_REGISTRY, 'r', encoding='utf-8') as f:
                self.plugins = json.load(f)
    
    def save_registry(self):
        """Guardar registro de plugins."""
        with open(PLUGINS_REGISTRY, 'w', encoding='utf-8') as f:
            json.dump(self.plugins, f, indent=2, ensure_ascii=False)
    
    def register_plugin(self, plugin_info: Dict) -> str:
        """Registrar plugin."""
        plugin_id = plugin_info.get("id", f"plugin_{len(self.plugins)}")
        
        self.plugins[plugin_id] = {
            "id": plugin_id,
            "name": plugin_info.get("name", "Unknown"),
            "version": plugin_info.get("version", "1.0.0"),
            "description": plugin_info.get("description", ""),
            "author": plugin_info.get("author", "Anonymous"),
            "file": plugin_info.get("file", ""),
            "enabled": plugin_info.get("enabled", True),
            "commands": plugin_info.get("commands", []),
            "dependencies": plugin_info.get("dependencies", []),
            "installed": datetime.now().isoformat(),
            "updated": datetime.now().isoformat()
        }
        
        self.save_registry()
        return plugin_id
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """Eliminar plugin del registro."""
        if plugin_id in self.plugins:
            del self.plugins[plugin_id]
            self.save_registry()
            return True
        return False
    
    def get_plugin(self, plugin_id: str) -> Optional[Dict]:
        """Obtener información de plugin."""
        return self.plugins.get(plugin_id)
    
    def get_all_plugins(self) -> List[Dict]:
        """Obtener todos los plugins."""
        return list(self.plugins.values())
    
    def get_enabled_plugins(self) -> List[Dict]:
        """Obtener plugins habilitados."""
        return [p for p in self.plugins.values() if p.get("enabled", True)]
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Habilitar plugin."""
        if plugin_id in self.plugins:
            self.plugins[plugin_id]["enabled"] = True
            self.plugins[plugin_id]["updated"] = datetime.now().isoformat()
            self.save_registry()
            return True
        return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Deshabilitar plugin."""
        if plugin_id in self.plugins:
            self.plugins[plugin_id]["enabled"] = False
            self.plugins[plugin_id]["updated"] = datetime.now().isoformat()
            self.save_registry()
            return True
        return False
    
    def search_plugins(self, query: str) -> List[Dict]:
        """Buscar plugins."""
        query_lower = query.lower()
        return [
            p for p in self.plugins.values()
            if query_lower in p.get("name", "").lower() or
               query_lower in p.get("description", "").lower()
        ]


# ==================== BASE CLASS PARA PLUGINS ====================

class PluginBase:
    """Clase base para todos los plugins."""
    
    name = "Base Plugin"
    version = "1.0.0"
    description = "Plugin base"
    author = "Unknown"
    
    def __init__(self, jarvis_core=None):
        self.jarvis = jarvis_core
        self.enabled = True
        self.commands = {}
    
    def initialize(self) -> bool:
        """Inicializar plugin."""
        return True
    
    def shutdown(self) -> bool:
        """Cerrar plugin."""
        return True
    
    def register_command(self, name: str, handler: Callable, description: str = ""):
        """Registrar comando del plugin."""
        self.commands[name] = {
            "handler": handler,
            "description": description
        }
    
    def execute_command(self, command: str, args: List[str] = None) -> Any:
        """Ejecutar comando del plugin."""
        if command in self.commands:
            return self.commands[command]["handler"](args or [])
        return None
    
    def get_commands(self) -> Dict:
        """Obtener comandos registrados."""
        return {
            name: {"description": info["description"]}
            for name, info in self.commands.items()
        }
    
    def log(self, message: str, level: str = "info"):
        """Registrar log del plugin."""
        print(f"[{self.name}] [{level.upper()}] {message}")


# ==================== PLUGINS BUILT-IN ====================

class SystemPlugin(PluginBase):
    """Plugin de sistema extendido."""
    
    name = "System Extended"
    version = "2.0.0"
    description = "Funciones extendidas de sistema"
    author = "J.A.R.V.I.S."
    
    def initialize(self):
        self.register_command("cpu", self.get_cpu_usage, "Uso de CPU")
        self.register_command("memory", self.get_memory_usage, "Uso de memoria")
        self.register_command("network", self.get_network_stats, "Estadísticas de red")
        self.register_command("processes", self.list_top_processes, "Top procesos")
        return True
    
    def get_cpu_usage(self, args):
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
            parts = line.split()
            idle = float(parts[4])
            total = sum(float(p) for p in parts[1:8])
            usage = ((total - idle) / total) * 100
            return f"📊 CPU: {usage:.1f}%"
        except:
            return "❌ No se pudo obtener uso de CPU"
    
    def get_memory_usage(self, args):
        try:
            with open('/proc/meminfo', 'r') as f:
                lines = f.readlines()
            
            mem_info = {}
            for line in lines[:5]:
                parts = line.split()
                mem_info[parts[0].rstrip(':')] = int(parts[1])
            
            total = mem_info.get('MemTotal', 0)
            available = mem_info.get('MemAvailable', 0)
            used = total - available
            percent = (used / total) * 100 if total > 0 else 0
            
            return f"💾 RAM: {used/1024/1024:.1f}GB / {total/1024/1024:.1f}GB ({percent:.1f}%)"
        except:
            return "❌ No se pudo obtener uso de memoria"
    
    def get_network_stats(self, args):
        try:
            result = subprocess.run(
                ["ip", "addr", "show", "wlan0"],
                capture_output=True, text=True, timeout=5
            )
            output = result.stdout
            
            # Extraer IP
            import re
            ip_match = re.search(r'inet\s+([\d.]+)', output)
            ip = ip_match.group(1) if ip_match else "N/A"
            
            return f"🌐 Red:\n  IP: {ip}\n  Interface: wlan0"
        except:
            return "❌ No se pudo obtener info de red"
    
    def list_top_processes(self, args):
        try:
            result = subprocess.run(
                ["ps", "-o", "pid,pcpu,mem,comm", "--sort=-pcpu"],
                capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split('\n')[:6]
            
            return f"📊 Top 5 Procesos:\n```\n" + "\n".join(lines) + "\n```"
        except:
            return "❌ Error al listar procesos"


class NetworkPlugin(PluginBase):
    """Plugin de red y conectividad."""
    
    name = "Network Tools"
    version = "1.5.0"
    description = "Herramientas de red avanzadas"
    author = "J.A.R.V.I.S."
    
    def initialize(self):
        self.register_command("ping", self.ping_host, "Hacer ping a un host")
        self.register_command("scan", self.scan_ports, "Escanear puertos")
        self.register_command("speedtest", self.speedtest, "Test de velocidad")
        self.register_command("dns", self.get_dns_info, "Info DNS")
        return True
    
    def ping_host(self, args):
        host = args[0] if args else "8.8.8.8"
        try:
            result = subprocess.run(
                ["ping", "-c", "3", host],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                # Extraer tiempo promedio
                import re
                match = re.search(r'min/avg/max = [\d.]+/([\d.]+)', result.stdout)
                avg = match.group(1) if match else "N/A"
                return f"🏓 Ping a {host}:\n  Promedio: {avg}ms"
            return f"❌ No se pudo hacer ping a {host}"
        except:
            return "❌ Error en ping"
    
    def scan_ports(self, args):
        host = args[0] if args else "localhost"
        common_ports = [21, 22, 80, 443, 8080, 3306, 5432]
        
        open_ports = []
        for port in common_ports:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass
        
        if open_ports:
            return f"🔍 Puertos abiertos en {host}:\n  " + ", ".join(map(str, open_ports))
        return f"🔍 No se encontraron puertos abiertos en {host}"
    
    def speedtest(self, args):
        return "⏱️ Test de velocidad (requiere speedtest-cli):\n  Instala: pip install speedtest-cli"
    
    def get_dns_info(self, args):
        try:
            with open('/etc/resolv.conf', 'r') as f:
                content = f.read()
            
            dns_servers = []
            for line in content.split('\n'):
                if line.strip().startswith('nameserver'):
                    dns_servers.append(line.split()[1])
            
            return f"🌐 DNS Servers:\n  " + "\n  ".join(dns_servers)
        except:
            return "❌ No se pudo obtener info DNS"


class IntegrationPlugin(PluginBase):
    """Plugin de integraciones externas."""
    
    name = "Integrations"
    version = "1.0.0"
    description = "Integraciones con servicios externos"
    author = "J.A.R.V.I.S."
    
    def initialize(self):
        self.register_command("github", self.github_info, "Info de repo GitHub")
        self.register_command("weather", self.get_weather, "Clima de ciudad")
        self.register_command("crypto", self.get_crypto_price, "Precio de cripto")
        self.register_command("translate", self.translate_text, "Traducir texto")
        return True
    
    def github_info(self, args):
        repo = args[0] if args else "torvalds/linux"
        try:
            import requests
            resp = requests.get(f"https://api.github.com/repos/{repo}", timeout=10)
            data = resp.json()
            
            return (f"📦 **{data.get('full_name', repo)}**\n"
                    f"⭐ Stars: {data.get('stargazers_count', 0)}\n"
                    f"🍴 Forks: {data.get('forks_count', 0)}\n"
                    f"📝 {data.get('description', 'Sin descripción')}")
        except:
            return "❌ Error al obtener info de GitHub"
    
    def get_weather(self, args):
        city = args[0] if args else "Mexico City"
        try:
            import requests
            resp = requests.get(
                f"https://wttr.in/{city}?format=%c+%t+%h+%w",
                headers={"User-Agent": "curl/7.68.0"},
                timeout=10
            )
            return f"🌤️ **{city}:** {resp.text.strip()}"
        except:
            return "❌ Error al obtener clima"
    
    def get_crypto_price(self, args):
        coin = args[0] if args else "bitcoin"
        try:
            import requests
            resp = requests.get(
                f"https://api.coingecko.com/api/v3/simple/price?ids={coin}&vs_currencies=usd&include_24hr_change=true",
                timeout=10
            )
            data = resp.json()
            
            if coin in data:
                price = data[coin].get("usd", 0)
                change = data[coin].get("usd_24h_change", 0)
                emoji = "📈" if change > 0 else "📉"
                return f"{emoji} **{coin.title()}:** ${price:,} ({change:.2f}%)"
            return f"❌ Criptomoneda no encontrada"
        except:
            return "❌ Error al obtener precio"
    
    def translate_text(self, args):
        return "🔄 Traducción (requiere API externa)\n  Próximamente..."


class DevToolsPlugin(PluginBase):
    """Plugin de herramientas para desarrolladores."""
    
    name = "Dev Tools"
    version = "1.0.0"
    description = "Herramientas para desarrolladores"
    author = "J.A.R.V.I.S."
    
    def initialize(self):
        self.register_command("git_clone", self.git_clone, "Clonar repo Git")
        self.register_command("pip_install", self.pip_install, "Instalar paquete Python")
        self.register_command("file_tree", self.show_file_tree, "Árbol de archivos")
        self.register_command("code_stats", self.get_code_stats, "Estadísticas de código")
        return True
    
    def git_clone(self, args):
        url = args[0] if args else ""
        if not url:
            return "❌ URL requerida"
        
        try:
            result = subprocess.run(
                ["git", "clone", url],
                capture_output=True, text=True, timeout=60,
                cwd=WORKING_DIR
            )
            
            if result.returncode == 0:
                return f"✅ Repositorio clonado:\n{result.stdout}"
            return f"❌ Error: {result.stderr}"
        except:
            return "❌ Error al clonar (asegúrate de tener git: pkg install git)"
    
    def pip_install(self, args):
        package = args[0] if args else ""
        if not package:
            return "❌ Paquete requerido"
        
        try:
            result = subprocess.run(
                ["pip", "install", package],
                capture_output=True, text=True, timeout=120
            )
            
            return f"📦 Instalando {package}:\n{result.stdout[-1000:]}"
        except:
            return "❌ Error al instalar paquete"
    
    def show_file_tree(self, args):
        path = args[0] if args else WORKING_DIR
        
        try:
            result = subprocess.run(
                ["tree", "-L", "2", path],
                capture_output=True, text=True, timeout=10
            )
            
            if result.returncode == 0:
                return f"📁 Estructura:\n```\n{result.stdout}\n```"
            else:
                # Fallback si no hay tree
                return self._simple_tree(path)
        except:
            return self._simple_tree(path)
    
    def _simple_tree(self, path: str, indent: str = "") -> str:
        """Árbol simple sin comando tree."""
        result = []
        try:
            items = sorted(os.listdir(path))
            for i, item in enumerate(items[:20]):
                is_last = i == len(items) - 1
                prefix = "└── " if is_last else "├── "
                result.append(f"{indent}{prefix}{item}")
                
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path) and not item.startswith('.'):
                    child_indent = indent + ("    " if is_last else "│   ")
                    result.extend(self._simple_tree(item_path, child_indent).split('\n')[:5])
        except:
            pass
        
        return f"📁 {path}:\n" + "\n".join(result)
    
    def get_code_stats(self, args):
        path = args[0] if args else WORKING_DIR
        
        stats = {"files": 0, "lines": 0, "code": 0, "comments": 0, "blank": 0}
        extensions = ['.py', '.js', '.ts', '.cpp', '.c', '.rs', '.java', '.go']
        
        try:
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if any(file.endswith(ext) for ext in extensions):
                        filepath = os.path.join(root, file)
                        stats["files"] += 1
                        
                        try:
                            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                                for line in f:
                                    stats["lines"] += 1
                                    stripped = line.strip()
                                    if not stripped:
                                        stats["blank"] += 1
                                    elif stripped.startswith(('#', '//', '/*', '*')):
                                        stats["comments"] += 1
                                    else:
                                        stats["code"] += 1
                        except:
                            pass
        except:
            pass
        
        return (f"📊 **Estadísticas de Código:**\n"
                f"  Archivos: {stats['files']}\n"
                f"  Líneas totales: {stats['lines']}\n"
                f"  Código: {stats['code']}\n"
                f"  Comentarios: {stats['comments']}\n"
                f"  Líneas en blanco: {stats['blank']}")


# ==================== GESTOR DE PLUGINS ====================

class PluginManager:
    """Gestor principal de plugins."""
    
    def __init__(self, jarvis_core=None):
        self.registry = PluginRegistry()
        self.loaded_plugins = {}
        self.jarvis = jarvis_core
        
        # Plugins built-in
        self.built_in_plugins = [
            SystemPlugin,
            NetworkPlugin,
            IntegrationPlugin,
            DevToolsPlugin
        ]
    
    def load_built_in_plugins(self):
        """Cargar plugins built-in."""
        for plugin_class in self.built_in_plugins:
            try:
                plugin = plugin_class(self.jarvis)
                if plugin.initialize():
                    plugin_id = plugin.name.lower().replace(' ', '_')
                    self.loaded_plugins[plugin_id] = plugin
                    
                    # Registrar en registry
                    self.registry.register_plugin({
                        "id": plugin_id,
                        "name": plugin.name,
                        "version": plugin.version,
                        "description": plugin.description,
                        "author": plugin.author,
                        "enabled": True,
                        "commands": list(plugin.get_commands().keys())
                    })
            except Exception as e:
                print(f"Error cargando plugin {plugin_class.__name__}: {e}")
    
    def load_plugin_from_file(self, filepath: str) -> bool:
        """Cargar plugin desde archivo .py"""
        try:
            spec = importlib.util.spec_from_file_location("plugin_module", filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Buscar clase que herede de PluginBase
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, PluginBase) and attr != PluginBase:
                    plugin = attr(self.jarvis)
                    if plugin.initialize():
                        plugin_id = attr_name.lower()
                        self.loaded_plugins[plugin_id] = plugin
                        return True
            
            return False
        except Exception as e:
            print(f"Error cargando plugin {filepath}: {e}")
            return False
    
    def install_plugin(self, plugin_info: Dict) -> str:
        """Instalar plugin."""
        plugin_id = self.registry.register_plugin(plugin_info)
        
        # Si tiene archivo, cargarlo
        if plugin_info.get("file"):
            filepath = os.path.join(PLUGINS_DIR, plugin_info["file"])
            if os.path.exists(filepath):
                self.load_plugin_from_file(filepath)
        
        return plugin_id
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """Desinstalar plugin."""
        # Cerrar plugin
        if plugin_id in self.loaded_plugins:
            self.loaded_plugins[plugin_id].shutdown()
            del self.loaded_plugins[plugin_id]
        
        # Eliminar del registro
        return self.registry.unregister_plugin(plugin_id)
    
    def execute_plugin_command(self, plugin_id: str, command: str, args: List[str] = None) -> Any:
        """Ejecutar comando de plugin."""
        if plugin_id in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_id]
            if plugin.enabled:
                return plugin.execute_command(command, args)
            return f"❌ Plugin {plugin_id} está deshabilitado"
        return f"❌ Plugin {plugin_id} no encontrado"
    
    def get_all_commands(self) -> Dict[str, Dict]:
        """Obtener todos los comandos de todos los plugins."""
        all_commands = {}
        
        for plugin_id, plugin in self.loaded_plugins.items():
            if plugin.enabled:
                commands = plugin.get_commands()
                for cmd_name, cmd_info in commands.items():
                    all_commands[f"{plugin_id}:{cmd_name}"] = cmd_info
        
        return all_commands
    
    def get_plugin_stats(self) -> Dict:
        """Obtener estadísticas de plugins."""
        return {
            "total_plugins": len(self.registry.plugins),
            "loaded_plugins": len(self.loaded_plugins),
            "enabled_plugins": len([p for p in self.loaded_plugins.values() if p.enabled]),
            "total_commands": len(self.get_all_commands())
        }


# ==================== INSTANCIA GLOBAL ====================

plugin_manager = PluginManager()


def test_plugins():
    """Probar sistema de plugins."""
    print("🔌 Probando Sistema de Plugins...")
    
    # Cargar built-in plugins
    plugin_manager.load_built_in_plugins()
    
    # Mostrar estadísticas
    print("\n📊 Estadísticas:")
    stats = plugin_manager.get_plugin_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Listar plugins
    print("\n📦 Plugins cargados:")
    for plugin_id, plugin in plugin_manager.loaded_plugins.items():
        print(f"  • {plugin.name} v{plugin.version}")
        commands = plugin.get_commands()
        for cmd, info in commands.items():
            print(f"    - {cmd}: {info['description']}")
    
    # Ejecutar comando de ejemplo
    print("\n🧪 Ejecutando comandos de prueba:")
    
    # System plugin
    result = plugin_manager.execute_plugin_command("system_extended", "cpu", [])
    print(f"  CPU: {result}")
    
    result = plugin_manager.execute_plugin_command("system_extended", "memory", [])
    print(f"  Memoria: {result}")
    
    # Network plugin
    result = plugin_manager.execute_plugin_command("network_tools", "ping", ["8.8.8.8"])
    print(f"  Ping: {result}")
    
    # Integration plugin
    result = plugin_manager.execute_plugin_command("integrations", "crypto", ["bitcoin"])
    print(f"  Crypto: {result}")
    
    print("\n✅ Sistema de plugins probado")


if __name__ == "__main__":
    test_plugins()
