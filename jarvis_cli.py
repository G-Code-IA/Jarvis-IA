#!/usr/bin/env python3
"""
J.A.R.V.I.S. - INTERFAZ DE TERMINAL
CLI completo para usar J.A.R.V.I.S. directamente en la terminal
"""

import os
import sys
import json
import time
import asyncio
import requests
import subprocess
from datetime import datetime
from typing import Optional
from pathlib import Path

# Agregar directorio de trabajo
WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
sys.path.insert(0, WORKING_DIR)

# Colores para terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

BRAIN_URL = "http://localhost:8000"


def print_banner():
    """Imprimir banner de J.A.R.V.I.S."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ███████╗ █████╗ ███╗   ██╗███████╗                      ║
║   ██╔════╝██╔══██╗████╗  ██║██╔════╝                      ║
║   █████╗  ███████║██╔██╗ ██║█████╗                        ║
║   ██╔══╝  ██╔══██║██║╚██╗██║██╔══╝                        ║
║   ██║     ██║  ██║██║ ╚████║███████╗                      ║
║   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝                      ║
║                                                          ║
║         Just A Rather Very Intelligent System            ║
║              Terminal Interface v3.0                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
{Colors.RESET}
"""
    print(banner)


def print_help():
    """Imprimir ayuda."""
    help_text = f"""
{Colors.BOLD}📋 COMANDOS DISPONIBLES:{Colors.RESET}

{Colors.CYAN}💬 Conversación:{Colors.RESET}
  <mensaje>          Hablar con J.A.R.V.I.S.
  ayuda, help        Mostrar esta ayuda
  hola               Saludar

{Colors.CYAN}🧠 Sistema:{Colors.RESET}
  status             Estado del BRAIN
  diagnostico        Diagnóstico completo del sistema
  bateria            Ver nivel de batería
  sistema            Información del sistema
  procesos           Ver procesos activos

{Colors.CYAN}🛡️ Seguridad:{Colors.RESET}
  seguridad          Escaneo de seguridad de red
  amenazas           Ver amenazas detectadas

{Colors.CYAN}🎯 Análisis:{Colors.RESET}
  tactico            Análisis táctico de situación
  github <url>       Analizar repositorio de GitHub

{Colors.CYAN}📁 Proyectos:{Colors.RESET}
  crea <descripción> Crear proyecto completo con IA
  taller             Ver proyectos activos
  templates          Ver plantillas disponibles

{Colors.CYAN}📷 Cámara:{Colors.RESET}
  foto               Tomar foto
  captura            Captura de pantalla
  fotos              Ver fotos tomadas

{Colors.CYAN}💾 Datos:{Colors.RESET}
  backup             Crear respaldo de datos
  backups            Ver respaldos disponibles
  memoria            Ver estado de memoria

{Colors.CYAN}🔌 Plugins:{Colors.RESET}
  plugins            Ver plugins activos
  plugins list       Listar todos los comandos

{Colors.CYAN}⚙️ Sistema:{Colors.RESET}
  limpiar            Limpiar pantalla
  salir, exit, quit  Salir de J.A.R.V.I.S.
  historial          Ver historial de comandos
  version            Ver versión de J.A.R.V.I.S.

{Colors.DIM}💡 Tip: Puedes usar pipes y redirección como en cualquier comando{Colors.RESET}
"""
    print(help_text)


def send_to_brain(command: str) -> Optional[dict]:
    """Enviar comando al BRAIN."""
    try:
        response = requests.post(
            f"{BRAIN_URL}/brain/command",
            headers={"Content-Type": "application/json"},
            json={
                "command": command,
                "interface": "cli",
                "user_id": 8406954800
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}❌ Error: No se pudo conectar con el BRAIN{Colors.RESET}")
        print(f"{Colors.DIM}   Asegúrate de que J.A.R.V.I.S. esté corriendo:{Colors.RESET}")
        print(f"{Colors.DIM}   python jarvis_brain.py &{Colors.RESET}")
        return None
    except requests.exceptions.Timeout:
        print(f"{Colors.YELLOW}⏱️ J.A.R.V.I.S. está pensando... espera un momento{Colors.RESET}")
        return None
    except Exception as e:
        print(f"{Colors.RED}❌ Error: {str(e)}{Colors.RESET}")
        return None


def check_brain_status() -> bool:
    """Verificar si el BRAIN está disponible."""
    try:
        response = requests.get(f"{BRAIN_URL}/brain/status", timeout=5)
        return response.status_code == 200
    except:
        return False


def interactive_mode():
    """Modo interactivo de terminal."""
    print_banner()
    
    # Verificar conexión
    if check_brain_status():
        print(f"{Colors.GREEN}✅ J.A.R.V.I.S. BRAIN está en línea{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️ J.A.R.V.I.S. BRAIN no está disponible{Colors.RESET}")
        print(f"{Colors.DIM}   Iniciando en modo offline...{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}Escribe 'ayuda' para ver comandos disponibles{Colors.RESET}\n")
    
    command_history = []
    
    while True:
        try:
            # Prompt
            timestamp = datetime.now().strftime("%H:%M:%S")
            user_input = input(f"{Colors.BOLD}[{timestamp}] J.A.R.V.I.S. > {Colors.RESET}")
            
            if not user_input.strip():
                continue
            
            # Agregar al historial
            command_history.append(user_input)
            
            # Procesar comandos especiales
            cmd_lower = user_input.lower().strip()
            
            if cmd_lower in ["salir", "exit", "quit", "q"]:
                print(f"\n{Colors.CYAN}¡Hasta luego! 👋{Colors.RESET}")
                break
            
            elif cmd_lower in ["ayuda", "help", "h"]:
                print_help()
                continue
            
            elif cmd_lower in ["limpiar", "clear", "cls"]:
                os.system('clear' if os.name != 'nt' else 'cls')
                print_banner()
                continue
            
            elif cmd_lower == "version":
                print(f"\n{Colors.BOLD}J.A.R.V.I.S. Terminal v3.0{Colors.RESET}")
                print(f"{Colors.DIM}Just A Rather Very Intelligent System{Colors.RESET}")
                print(f"{Colors.DIM}Terminal Interface - CLI Mode{Colors.RESET}\n")
                continue
            
            elif cmd_lower == "historial":
                print(f"\n{Colors.BOLD}📋 Historial de comandos:{Colors.RESET}\n")
                for i, cmd in enumerate(command_history[-10:], 1):
                    print(f"  {i}. {cmd}")
                print()
                continue
            
            # Enviar al BRAIN
            result = send_to_brain(user_input)
            
            if result and result.get("response"):
                response = result["response"]
                
                # Imprimir respuesta con formato
                print(f"\n{Colors.GREEN}{response}{Colors.RESET}\n")
                
                # Mostrar info de agente si está disponible
                agent_info = result.get("agent", {})
                if agent_info.get("tool_used"):
                    print(f"{Colors.DIM}   🛠️ Herramienta: {agent_info['tool_used']}{Colors.RESET}")
                if agent_info.get("confidence"):
                    print(f"{Colors.DIM}   🎯 Confianza: {agent_info['confidence']:.0%}{Colors.RESET}")
                print()
            else:
                print(f"{Colors.RED}❌ No se recibió respuesta{Colors.RESET}\n")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}¡Hasta luego! 👋{Colors.RESET}")
            break
        except EOFError:
            print(f"\n\n{Colors.CYAN}¡Hasta luego! 👋{Colors.RESET}")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {str(e)}{Colors.RESET}\n")


def command_mode(command: str):
    """Modo comando único (para pipes y scripts)."""
    result = send_to_brain(command)
    
    if result and result.get("response"):
        print(result["response"])
        return 0
    else:
        print("Error: No se recibió respuesta", file=sys.stderr)
        return 1


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="J.A.R.V.I.S. - Terminal Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  jarvis                    Modo interactivo
  jarvis "batería"          Comando único
  jarvis -c "diagnóstico"   Comando con flag
  echo "hola" | jarvis      Pipe (próximamente)
        """
    )
    
    parser.add_argument(
        "command",
        nargs="?",
        help="Comando a ejecutar"
    )
    
    parser.add_argument(
        "-c", "--command",
        help="Comando a ejecutar (alternativa)"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Forzar modo interactivo"
    )
    
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Modo silencioso (sin banner)"
    )
    
    args = parser.parse_args()
    
    # Determinar modo
    if args.command or args.command:
        # Modo comando único
        cmd = args.command or args.command
        sys.exit(command_mode(cmd))
    elif args.interactive or not sys.stdin.isatty():
        # Modo interactivo o pipe
        if not args.quiet:
            print_banner()
        interactive_mode()
    else:
        # Modo interactivo por defecto
        interactive_mode()


if __name__ == "__main__":
    main()
