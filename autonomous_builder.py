#!/usr/bin/env python3
"""
J.A.R.V.I.S. - AUTONOMOUS PROJECT BUILDER
Crea proyectos completos pensando y actuando autónomamente
Sin plantillas - genera TODO con IA
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Any

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
PROJECTS_DIR = os.path.join(WORKING_DIR, "projects")
os.makedirs(PROJECTS_DIR, exist_ok=True)

OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:1.5b"
OLLAMA_TIMEOUT = 60


class AutonomousProjectBuilder:
    """Constructor de proyectos autónomo - piensa y actúa solo."""
    
    def __init__(self):
        self.current_project = None
        self.thoughts = []
        self.created_files = []
    
    def think_and_build(self, user_request: str) -> Dict:
        """Pensar y construir proyecto autónomamente."""
        self.thoughts = []
        self.created_files = []
        
        # Fase 1: COMPRENDER qué quiere el usuario
        self._think(f"Usuario quiere: {user_request}")
        project_plan = self._understand_request(user_request)
        
        # Fase 2: PLANIFICAR la arquitectura
        self._think("Planificando arquitectura...")
        architecture = self._plan_architecture(user_request, project_plan)
        
        # Fase 3: GENERAR cada archivo con IA
        self._think("Generando archivos con IA...")
        project_dir = self._create_project_structure(user_request, architecture)
        
        # Fase 4: VERIFICAR que todo está bien
        self._think("Verificando proyecto...")
        verification = self._verify_project(project_dir, architecture)
        
        # Fase 5: GENERAR instrucciones
        instructions = self._generate_instructions(user_request, project_dir, architecture)
        
        return {
            "success": True,
            "name": project_plan.get("name", "mi_proyecto"),
            "type": project_plan.get("type", "desconocido"),
            "directory": project_dir,
            "files": self.created_files,
            "file_count": len(self.created_files),
            "thoughts": self.thoughts,
            "architecture": architecture,
            "verification": verification,
            "instructions": instructions
        }
    
    def _think(self, thought: str):
        """Registrar pensamiento."""
        self.thoughts.append({
            "thought": thought,
            "timestamp": datetime.now().isoformat()
        })
    
    def _ask_ollama(self, prompt: str, max_tokens: int = 500) -> str:
        """Preguntar a Ollama."""
        try:
            payload = {
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": max_tokens
                }
            }
            
            resp = requests.post(OLLAMA_API, json=payload, timeout=OLLAMA_TIMEOUT)
            resp.raise_for_status()
            return resp.json().get("response", "").strip()
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _understand_request(self, user_request: str) -> Dict:
        """Fase 1: Comprender qué quiere el usuario."""
        prompt = f"""Analiza esta solicitud de proyecto y responde SOLO con JSON:

Solicitud: "{user_request}"

Responde con este formato JSON exacto:
{{"name": "nombre_del_proyecto", "type": "tipo (web_api, cli, game, web_app, library)", "language": "lenguaje principal", "description": "descripción breve", "key_features": ["feature1", "feature2"]}}

Solo el JSON, nada más."""

        response = self._ask_ollama(prompt, 300)
        
        # Parsear JSON de la respuesta
        try:
            # Buscar JSON en la respuesta
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback inteligente
        req_lower = user_request.lower()
        
        if any(x in req_lower for x in ["api", "backend", "servidor", "fastapi", "express"]):
            return {
                "name": self._extract_name(user_request) or "mi_api",
                "type": "web_api",
                "language": "python" if "python" in req_lower or "fastapi" in req_lower else "javascript",
                "description": "API REST generada por J.A.R.V.I.S.",
                "key_features": ["CRUD endpoints", "Health check", "Documentation"]
            }
        
        if any(x in req_lower for x in ["juego", "game", "minecraft", "minecraft"]):
            return {
                "name": self._extract_name(user_request) or "mi_juego",
                "type": "game",
                "language": "cpp",
                "description": "Juego generado por J.A.R.V.I.S.",
                "key_features": ["Game loop", "Rendering", "Input handling"]
            }
        
        if any(x in req_lower for x in ["cli", "comandos", "terminal"]):
            return {
                "name": self._extract_name(user_request) or "mi_cli",
                "type": "cli",
                "language": "python",
                "description": "CLI generada por J.A.R.V.I.S.",
                "key_features": ["Command parsing", "Help system", "Output formatting"]
            }
        
        return {
            "name": self._extract_name(user_request) or "mi_proyecto",
            "type": "web_app",
            "language": "python",
            "description": "Proyecto generado por J.A.R.V.I.S.",
            "key_features": ["Basic structure", "Configuration", "Documentation"]
        }
    
    def _extract_name(self, request: str) -> Optional[str]:
        """Extraer nombre del proyecto."""
        import re
        match = re.search(r'(?:llamado|nombre)\s+(\w[\w-]+)', request, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _plan_architecture(self, user_request: str, project_plan: Dict) -> Dict:
        """Fase 2: Planificar arquitectura del proyecto."""
        name = project_plan["name"]
        ptype = project_plan["type"]
        lang = project_plan["language"]
        
        self._think(f"Proyecto: {name}, Tipo: {ptype}, Lenguaje: {lang}")
        
        # Generar lista de archivos necesarios
        prompt = f"""Para un proyecto {ptype} en {lang} llamado "{name}",
¿qué archivos necesito? Responde SOLO con una lista de archivos JSON:

{{"files": [
  {{"path": "ruta/archivo.ext", "description": "qué hace este archivo", "content_type": "code|config|doc"}},
  ...
]}}

Solo el JSON, nada más."""

        response = self._ask_ollama(prompt, 500)
        
        try:
            import re
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                arch = json.loads(json_match.group())
                return arch
        except:
            pass
        
        # Fallback: arquitectura inteligente por tipo
        if ptype == "web_api" and lang == "python":
            return {
                "files": [
                    {"path": "README.md", "description": "Documentación del proyecto", "content_type": "doc"},
                    {"path": "requirements.txt", "description": "Dependencias Python", "content_type": "config"},
                    {"path": "main.py", "description": "Punto de entrada de la API", "content_type": "code"},
                    {"path": "models.py", "description": "Modelos de datos", "content_type": "code"},
                    {"path": "routes.py", "description": "Rutas de la API", "content_type": "code"},
                    {"path": "config.py", "description": "Configuración", "content_type": "code"},
                    {"path": ".gitignore", "description": "Archivos ignorados por git", "content_type": "config"}
                ]
            }
        
        if ptype == "game":
            return {
                "files": [
                    {"path": "README.md", "description": "Documentación", "content_type": "doc"},
                    {"path": "CMakeLists.txt", "description": "Configuración de compilación", "content_type": "config"},
                    {"path": "src/main.cpp", "description": "Punto de entrada", "content_type": "code"},
                    {"path": "src/game.hpp", "description": "Clase principal del juego", "content_type": "code"},
                    {"path": "src/game.cpp", "description": "Implementación del juego", "content_type": "code"},
                    {"path": "src/renderer.hpp", "description": "Sistema de renderizado", "content_type": "code"},
                    {"path": "src/renderer.cpp", "description": "Implementación del renderer", "content_type": "code"}
                ]
            }
        
        return {
            "files": [
                {"path": "README.md", "description": "Documentación", "content_type": "doc"},
                {"path": "main.py", "description": "Código principal", "content_type": "code"},
                {"path": "requirements.txt", "description": "Dependencias", "content_type": "config"}
            ]
        }
    
    def _create_project_structure(self, user_request: str, architecture: Dict) -> str:
        """Fase 3: Crear cada archivo con IA."""
        project_plan = self._understand_request(user_request)
        name = project_plan["name"]
        project_dir = os.path.join(PROJECTS_DIR, name)
        os.makedirs(project_dir, exist_ok=True)
        
        files = architecture.get("files", [])
        
        for i, file_info in enumerate(files):
            filepath = file_info["path"]
            description = file_info["description"]
            content_type = file_info.get("content_type", "code")
            
            self._think(f"Generando {filepath}...")
            
            # Generar contenido con IA
            content = self._generate_file_content(
                name, project_plan, filepath, description, content_type, files
            )
            
            # Crear archivo
            full_path = os.path.join(project_dir, filepath)
            os.makedirs(os.path.dirname(full_path) or project_dir, exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.created_files.append(filepath)
            self._think(f"✅ {filepath} creado")
        
        return project_dir
    
    def _generate_file_content(self, project_name: str, project_plan: Dict, 
                                filepath: str, description: str, content_type: str,
                                all_files: List[Dict]) -> str:
        """Generar contenido de un archivo con IA."""
        
        lang = project_plan.get("language", "python")
        ptype = project_plan.get("type", "web_app")
        
        # Construir prompt para generar código
        if content_type == "code":
            ext = os.path.splitext(filepath)[1]
            
            prompt = f"""Genera el código COMPLETO para este archivo de un proyecto {ptype}:

Proyecto: {project_name}
Tipo: {ptype}
Lenguaje: {lang}
Archivo: {filepath}
Descripción: {description}

Estructura del proyecto:
{json.dumps([f['path'] for f in all_files], indent=2)}

Genera SOLO el código del archivo {filepath}.
Debe ser código funcional y completo.
No incluyas explicaciones, solo el código."""

        elif content_type == "config":
            prompt = f"""Genera el contenido de configuración para:

Proyecto: {project_name}
Archivo: {filepath}
Descripción: {description}
Lenguaje: {lang}

Solo el contenido del archivo, sin explicaciones."""

        else:  # doc
            prompt = f"""Genera la documentación para:

Proyecto: {project_name}
Tipo: {ptype}
Descripción: {project_plan.get('description', '')}
Features: {', '.join(project_plan.get('key_features', []))}
Archivo: {filepath}

Solo el contenido del archivo README, sin explicaciones."""

        content = self._ask_ollama(prompt, 800)
        
        # Limpiar código de markdown si es necesario
        if content_type == "code":
            import re
            # Remover bloques de markdown
            content = re.sub(r'```(?:\w+)?\n', '', content)
            content = re.sub(r'```\n?', '', content)
        
        return content
    
    def _verify_project(self, project_dir: str, architecture: Dict) -> Dict:
        """Fase 4: Verificar que el proyecto está bien."""
        verification = {
            "files_created": 0,
            "files_expected": len(architecture.get("files", [])),
            "total_size": 0,
            "issues": []
        }
        
        # Verificar archivos
        for file_info in architecture.get("files", []):
            filepath = os.path.join(project_dir, file_info["path"])
            if os.path.exists(filepath):
                verification["files_created"] += 1
                verification["total_size"] += os.path.getsize(filepath)
            else:
                verification["issues"].append(f"❌ {file_info['path']} no existe")
        
        verification["success"] = verification["files_created"] == verification["files_expected"]
        
        return verification
    
    def _generate_instructions(self, user_request: str, project_dir: str, architecture: Dict) -> str:
        """Fase 5: Generar instrucciones de uso."""
        project_plan = self._understand_request(user_request)
        name = project_plan["name"]
        lang = project_plan["language"]
        
        instructions = f"📦 **Para ejecutar {name}:**\n\n"
        
        if lang == "python":
            instructions += "1. Instalar dependencias:\n"
            instructions += "   ```bash\n   pip install -r requirements.txt\n   ```\n\n"
            instructions += "2. Ejecutar:\n"
            instructions += "   ```bash\n   python main.py\n   ```\n"
        
        elif lang == "javascript":
            instructions += "1. Instalar dependencias:\n"
            instructions += "   ```bash\n   npm install\n   ```\n\n"
            instructions += "2. Ejecutar:\n"
            instructions += "   ```bash\n   npm start\n   ```\n"
        
        elif lang == "cpp":
            instructions += "1. Compilar:\n"
            instructions += "   ```bash\n   mkdir build && cd build\n   cmake ..\n   make\n   ```\n\n"
            instructions += "2. Ejecutar:\n"
            instructions += "   ```bash\n   ./main\n   ```\n"
        
        instructions += f"\n📁 Directorio: `{project_dir}`"
        
        return instructions


# Instancia global
autonomous_builder = AutonomousProjectBuilder()


def test_builder():
    """Probar constructor autónomo."""
    builder = AutonomousProjectBuilder()
    
    print("🏗️ Probando constructor autónomo...\n")
    
    result = builder.think_and_build("crea una API web en Python")
    
    print(f"✅ Proyecto: {result['name']}")
    print(f"📄 Archivos: {result['file_count']}")
    print(f"📁 Directorio: {result['directory']}")
    print(f"\n🧠 Pensamientos:")
    for t in result['thoughts'][:5]:
        print(f"  • {t['thought']}")
    
    print(f"\n{result['instructions']}")
    
    print("\n✅ Constructor autónomo probado")


if __name__ == "__main__":
    test_builder()
