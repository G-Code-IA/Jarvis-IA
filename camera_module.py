#!/usr/bin/env python3
"""
J.A.R.V.I.S. - Módulo de Cámara
Captura, análisis y procesamiento de imágenes
"""

import os
import time
import base64
import subprocess
import requests
from datetime import datetime
from typing import Optional, Tuple

WORKING_DIR = "/data/data/com.termux/files/home/Jarvis"
CAMERA_DIR = os.path.join(WORKING_DIR, "camera")
os.makedirs(CAMERA_DIR, exist_ok=True)

OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_VISION_MODEL = "llava:7b"  # Modelo de visión para analizar imágenes


class CameraTools:
    """Herramientas de cámara para Termux/Android."""
    
    @staticmethod
    def take_photo(filename: str = None) -> Optional[str]:
        """Tomar foto con cámara de Termux."""
        try:
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"photo_{timestamp}.jpg"
            
            filepath = os.path.join(CAMERA_DIR, filename)
            
            # Usar termux-camera (requiere termux-api)
            result = subprocess.run(
                ["termux-camera-photo", filepath],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and os.path.exists(filepath):
                return filepath
            else:
                return None
                
        except Exception as e:
            print(f"Error tomando foto: {e}")
            return None
    
    @staticmethod
    def list_photos() -> list:
        """Listar fotos tomadas."""
        try:
            photos = []
            for f in os.listdir(CAMERA_DIR):
                if f.endswith(('.jpg', '.jpeg', '.png')):
                    filepath = os.path.join(CAMERA_DIR, f)
                    photos.append({
                        "name": f,
                        "path": filepath,
                        "size": os.path.getsize(filepath),
                        "created": datetime.fromtimestamp(os.path.getctime(filepath)).isoformat()
                    })
            return sorted(photos, key=lambda x: x["created"], reverse=True)
        except:
            return []
    
    @staticmethod
    def get_photo_base64(filepath: str) -> Optional[str]:
        """Convertir foto a base64."""
        try:
            with open(filepath, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except:
            return None
    
    @staticmethod
    def analyze_image(filepath: str, prompt: str = "Describe esta imagen en detalle") -> str:
        """Analizar imagen con IA (LLaVA)."""
        try:
            # Verificar si existe LLaVA
            models = requests.get("http://localhost:11434/api/tags", timeout=5).json()
            model_names = [m.get("name", "") for m in models.get("models", [])]
            
            if not any("llava" in m for m in model_names):
                return "❌ Modelo LLaVA no instalado. Ejecuta: ollama pull llava:7b"
            
            # Codificar imagen
            with open(filepath, 'rb') as f:
                image_base64 = base64.b64encode(f.read()).decode()
            
            payload = {
                "model": "llava:7b",
                "prompt": prompt,
                "images": [image_base64],
                "stream": False
            }
            
            resp = requests.post(OLLAMA_API, json=payload, timeout=120)
            resp.raise_for_status()
            return resp.json().get("response", "No se pudo analizar la imagen")
        
        except requests.exceptions.Timeout:
            return "⏱️ El análisis tardó mucho. Intenta de nuevo."
        except FileNotFoundError:
            return "❌ Imagen no encontrada"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @staticmethod
    def scan_qr(filepath: str) -> str:
        """Escanear código QR desde imagen."""
        try:
            # Usar zbarimg si está disponible
            result = subprocess.run(
                ["zbarimg", "-q", "--raw", filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return f"📱 **Código QR detectado:**\n\n```\n{result.stdout.strip()}\n```"
            return "❌ No se detectó código QR"
        except FileNotFoundError:
            return "❌ zbarimg no instalado. Ejecuta: pkg install zbar"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @staticmethod
    def ocr_image(filepath: str) -> str:
        """Extraer texto de imagen (OCR)."""
        try:
            # Usar tesseract si está disponible
            result = subprocess.run(
                ["tesseract", filepath, "stdout"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.stdout.strip():
                return f"📝 **Texto detectado:**\n\n```\n{result.stdout.strip()}\n```"
            return "❌ No se detectó texto"
        except FileNotFoundError:
            return "❌ Tesseract no instalado. Ejecuta: pkg install tesseract"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @staticmethod
    def resize_image(filepath: str, width: int = 800, height: int = 600) -> Optional[str]:
        """Redimensionar imagen."""
        try:
            # Usar ImageMagick convert si está disponible
            output_path = filepath.replace('.jpg', '_resized.jpg')
            result = subprocess.run(
                ["convert", filepath, "-resize", f"{width}x{height}!", output_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                return output_path
            return None
        except:
            return None
    
    @staticmethod
    def get_camera_info() -> str:
        """Obtener información de cámaras disponibles."""
        try:
            # En Android/Termux
            result = subprocess.run(
                ["termux-camera-info"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return f"📷 **Cámaras disponibles:**\n\n```\n{result.stdout}\n```"
            
            return "📷 Cámara de Termux disponible (termux-camera-photo)"
        except:
            return "📷 Cámara no disponible o termux-api no instalado"


class ScreenCapture:
    """Capturas de pantalla."""
    
    @staticmethod
    def take_screenshot() -> Optional[str]:
        """Tomar captura de pantalla."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(CAMERA_DIR, f"screenshot_{timestamp}.png")
            
            result = subprocess.run(
                ["screencap", "-p", filepath],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and os.path.exists(filepath):
                return filepath
            return None
        except:
            return None
    
    @staticmethod
    def analyze_screenshot(prompt: str = "¿Qué se muestra en esta captura?") -> str:
        """Tomar y analizar captura de pantalla."""
        filepath = ScreenCapture.take_screenshot()
        if filepath:
            return CameraTools.analyze_image(filepath, prompt)
        return "❌ No se pudo tomar la captura"


# Instancia global
camera = CameraTools()
screen = ScreenCapture()


def test_camera():
    """Probar funcionalidades de cámara."""
    print("📷 Probando cámara...")
    
    # Info
    print(camera.get_camera_info())
    
    # Tomar foto
    print("\n📸 Tomando foto...")
    filepath = camera.take_photo()
    if filepath:
        print(f"✅ Foto tomada: {filepath}")
        
        # Listar fotos
        photos = camera.list_photos()
        print(f"📁 Fotos en directorio: {len(photos)}")
    else:
        print("❌ No se pudo tomar la foto")
        print("   Asegúrate de tener termux-api instalado:")
        print("   pkg install termux-api")


if __name__ == "__main__":
    test_camera()
