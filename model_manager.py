#!/usr/bin/env python3
"""
J.A.R.V.I.S. - MODEL MANAGER
Gestiona múltiples modelos de Ollama y rutea tareas al modelo correcto
"""

import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime

OLLAMA_API = "http://localhost:11434"
OLLAMA_GENERATE = f"{OLLAMA_API}/api/generate"
OLLAMA_CHAT = f"{OLLAMA_API}/api/chat"
OLLAMA_TAGS = f"{OLLAMA_API}/api/tags"
OLLAMA_PULL = f"{OLLAMA_API}/api/pull"

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
MODELS_CONFIG = os.path.join(WORKING_DIR, "models_config.json")


class ModelInfo:
    """Información de un modelo."""
    def __init__(self, name: str, size: str, capabilities: List[str], 
                 best_for: List[str], description: str, ram_gb: float):
        self.name = name
        self.size = size
        self.capabilities = capabilities
        self.best_for = best_for
        self.description = description
        self.ram_gb = ram_gb
    
    def to_dict(self):
        return {
            "name": self.name,
            "size": self.size,
            "capabilities": self.capabilities,
            "best_for": self.best_for,
            "description": self.description,
            "ram_gb": self.ram_gb
        }


class ModelManager:
    """Gestor de múltiples modelos de Ollama."""
    
    # Modelos recomendados para diferentes tareas
    RECOMMENDED_MODELS = {
        # Código y desarrollo
        "code": ModelInfo(
            name="qwen2.5-coder:1.5b",
            size="1.5B",
            capabilities=["code", "reasoning", "instruction_following"],
            best_for=["generar código", "analizar código", "debuggear", "explicar código"],
            description="Modelo especializado en código, rápido y eficiente",
            ram_gb=1.2
        ),
        
        # Chat general
        "chat": ModelInfo(
            name="llama3.2:1b",
            size="1B",
            capabilities=["chat", "general", "fast_response"],
            best_for=["conversación", "preguntas generales", "respuestas rápidas"],
            description="Modelo ligero para conversación rápida",
            ram_gb=0.8
        ),
        
        # Razonamiento complejo
        "reasoning": ModelInfo(
            name="qwen2.5:3b",
            size="3B",
            capabilities=["reasoning", "analysis", "complex_tasks"],
            best_for=["análisis complejo", "planificación", "razonamiento"],
            description="Modelo balanceado para tareas complejas",
            ram_gb=2.0
        ),
        
        # Visión (imágenes)
        "vision": ModelInfo(
            name="llava:7b",
            size="7B",
            capabilities=["vision", "image_analysis", "multimodal"],
            best_for=["analizar imágenes", "describir fotos", "OCR visual"],
            description="Modelo de visión para analizar imágenes",
            ram_gb=4.5
        ),
        
        # Escritura creativa
        "creative": ModelInfo(
            name="mistral:7b",
            size="7B",
            capabilities=["creative", "writing", "storytelling"],
            best_for=["escritura creativa", "historias", "contenido creativo"],
            description="Modelo creativo para contenido elaborado",
            ram_gb=4.5
        ),
        
        # Traducción
        "translation": ModelInfo(
            name="qwen2.5:1.5b",
            size="1.5B",
            capabilities=["translation", "language", "multilingual"],
            best_for=["traducir texto", "cambiar idioma"],
            description="Modelo multilingüe para traducciones",
            ram_gb=1.2
        ),
        
        # Resumen
        "summarization": ModelInfo(
            name="qwen2.5:1.5b",
            size="1.5B",
            capabilities=["summarization", "extraction", "compression"],
            best_for=["resumir texto", "extraer información", "sintetizar"],
            description="Modelo eficiente para resumir contenido",
            ram_gb=1.2
        )
    }
    
    def __init__(self):
        self.config = self._load_config()
        self.available_models = []
        self._refresh_available_models()
    
    def _load_config(self) -> Dict:
        """Cargar configuración de modelos."""
        if os.path.exists(MODELS_CONFIG):
            with open(MODELS_CONFIG, 'r') as f:
                return json.load(f)
        
        return {
            "default_model": "qwen2.5-coder:1.5b",
            "task_models": {
                "code": "qwen2.5-coder:1.5b",
                "chat": "qwen2.5-coder:1.5b",
                "reasoning": "qwen2.5-coder:1.5b",
                "vision": "llava:7b",
                "creative": "qwen2.5-coder:1.5b",
                "translation": "qwen2.5-coder:1.5b",
                "summarization": "qwen2.5-coder:1.5b"
            },
            "installed_models": [],
            "last_updated": datetime.now().isoformat()
        }
    
    def _save_config(self):
        """Guardar configuración."""
        self.config["last_updated"] = datetime.now().isoformat()
        with open(MODELS_CONFIG, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _refresh_available_models(self):
        """Actualizar lista de modelos disponibles."""
        try:
            resp = requests.get(OLLAMA_TAGS, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                self.available_models = [m.get("name", "") for m in data.get("models", [])]
                self.config["installed_models"] = self.available_models
                self._save_config()
        except:
            pass
    
    def get_best_model_for_task(self, task: str) -> str:
        """Obtener el mejor modelo para una tarea."""
        task_lower = task.lower()
        
        # Determinar categoría de tarea
        if any(x in task_lower for x in ["código", "code", "programa", "función", "clase"]):
            category = "code"
        elif any(x in task_lower for x in ["imagen", "foto", "foto", "visual", "ver"]):
            category = "vision"
        elif any(x in task_lower for x in ["analiza", "analizar", "complejo", "difícil"]):
            category = "reasoning"
        elif any(x in task_lower for x in ["traduce", "translate", "idioma", "inglés", "español"]):
            category = "translation"
        elif any(x in task_lower for x in ["resume", "resumir", "summary", "sintetiza"]):
            category = "summarization"
        elif any(x in task_lower for x in ["crea", "escribe", "historia", "cuento", "poema"]):
            category = "creative"
        else:
            category = "chat"
        
        # Obtener modelo configurado para esta categoría
        model = self.config.get("task_models", {}).get(category)
        
        # Si el modelo no está instalado, usar default
        if model not in self.available_models:
            model = self.config.get("default_model", "qwen2.5-coder:1.5b")
        
        return model
    
    def generate(self, prompt: str, task_type: str = "chat", 
                 system_prompt: str = None, max_tokens: int = 300) -> str:
        """Generar respuesta con el modelo apropiado."""
        model = self.get_best_model_for_task(task_type)
        
        full_prompt = ""
        if system_prompt:
            full_prompt += f"{system_prompt}\n\n"
        full_prompt += prompt
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
                "num_predict": max_tokens
            }
        }
        
        try:
            resp = requests.post(OLLAMA_GENERATE, json=payload, timeout=60)
            resp.raise_for_status()
            return resp.json().get("response", "")
        except Exception as e:
            return f"Error con modelo {model}: {str(e)}"
    
    def list_available_models(self) -> List[Dict]:
        """Listar modelos disponibles."""
        self._refresh_available_models()
        
        models = []
        for category, info in self.RECOMMENDED_MODELS.items():
            is_installed = info.name in self.available_models
            models.append({
                "category": category,
                **info.to_dict(),
                "installed": is_installed,
                "status": "✅ Instalado" if is_installed else "❌ No instalado"
            })
        
        return models
    
    def install_model(self, model_name: str) -> Dict:
        """Instalar un modelo."""
        try:
            print(f"📥 Descargando {model_name}...")
            
            resp = requests.post(
                OLLAMA_PULL,
                json={"name": model_name, "stream": False},
                timeout=300
            )
            
            if resp.status_code == 200:
                self._refresh_available_models()
                return {
                    "success": True,
                    "message": f"✅ {model_name} instalado correctamente",
                    "model": model_name
                }
            else:
                return {
                    "success": False,
                    "message": f"❌ Error al instalar {model_name}",
                    "error": resp.text
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"❌ Error: {str(e)}",
                "error": str(e)
            }
    
    def set_default_model(self, model_name: str) -> Dict:
        """Cambiar modelo por defecto."""
        if model_name in self.available_models:
            self.config["default_model"] = model_name
            self._save_config()
            return {"success": True, "message": f"Modelo por defecto: {model_name}"}
        return {"success": False, "message": f"Modelo no instalado: {model_name}"}
    
    def set_task_model(self, task: str, model_name: str) -> Dict:
        """Cambiar modelo para una tarea específica."""
        valid_tasks = list(self.RECOMMENDED_MODELS.keys())
        if task not in valid_tasks:
            return {"success": False, "message": f"Tarea inválida. Opciones: {', '.join(valid_tasks)}"}
        
        if model_name not in self.available_models:
            return {"success": False, "message": f"Modelo no instalado: {model_name}"}
        
        self.config["task_models"][task] = model_name
        self._save_config()
        return {"success": True, "message": f"Modelo para {task}: {model_name}"}
    
    def get_model_recommendations(self) -> str:
        """Obtener recomendaciones de modelos."""
        models = self.list_available_models()
        
        result = "🧠 **Modelos de IA disponibles:**\n\n"
        
        for m in models:
            status_icon = "✅" if m["installed"] else "⬜"
            result += f"{status_icon} **{m['category']}** - {m['name']}\n"
            result += f"   {m['description']}\n"
            result += f"   RAM: {m['ram_gb']}GB | Mejor para: {', '.join(m['best_for'][:3])}\n\n"
        
        result += "\n💡 **Para instalar un modelo:**\n"
        result += "  `jarvis 'instala modelo llama3.2:1b'`\n\n"
        result += "💡 **Para cambiar modelo por defecto:**\n"
        result += "  `jarvis 'cambia modelo a llama3.2:1b'`\n"
        
        return result
    
    def get_status(self) -> Dict:
        """Obtener estado del gestor de modelos."""
        self._refresh_available_models()
        
        return {
            "default_model": self.config.get("default_model"),
            "installed_count": len(self.available_models),
            "available_models": self.available_models,
            "task_assignments": self.config.get("task_models", {}),
            "recommendations": {
                category: info.to_dict()
                for category, info in self.RECOMMENDED_MODELS.items()
            }
        }


# Instancia global
model_manager = ModelManager()


def test():
    """Probar gestor de modelos."""
    manager = ModelManager()
    
    print("🧠 Probando gestor de modelos...\n")
    
    # Listar modelos
    print("=== MODELOS DISPONIBLES ===")
    models = manager.list_available_models()
    for m in models:
        status = "✅" if m["installed"] else "❌"
        print(f"  {status} {m['category']}: {m['name']}")
    
    # Estado
    print("\n=== ESTADO ===")
    status = manager.get_status()
    print(f"  Default: {status['default_model']}")
    print(f"  Instalados: {status['installed_count']}")
    print(f"  Modelos: {status['available_models']}")
    
    print("\n✅ Prueba completada")


if __name__ == "__main__":
    test()
