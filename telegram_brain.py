#!/usr/bin/env python3
"""
J.A.R.V.I.S. - Bot de Telegram conectado al BRAIN
"""

import asyncio
import logging
import requests
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Configuración
BOT_TOKEN = "8449452826:AAGmq-FeDS987KD7T12dUss4ZhppoiKYzy0"
ALLOWED_USER_ID = 8406954800
BRAIN_URL = "http://localhost:8000"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("JARVIS-TELEGRAM")


class TelegramBrainClient:
    """Cliente de Telegram conectado al BRAIN."""
    
    def __init__(self):
        self.client_id = f"telegram_{ALLOWED_USER_ID}"
        self.context = []
        self.ws = None
    
    def connect_to_brain(self):
        """Conectar al BRAIN (WebSocket cuando esté disponible)."""
        try:
            # Verificar que el BRAIN esté online
            resp = requests.get(f"{BRAIN_URL}/brain/status", timeout=5)
            if resp.status_code == 200:
                logger.info("✅ Conectado al J.A.R.V.I.S. BRAIN")
                return True
        except:
            logger.warning("⚠️ BRAIN no disponible, usando modo offline")
        return False
    
    def send_command(self, command: str) -> str:
        """Enviar comando al BRAIN."""
        try:
            resp = requests.post(
                f"{BRAIN_URL}/brain/command",
                json={
                    "command": command,
                    "interface": "telegram",
                    "user_id": ALLOWED_USER_ID,
                    "context": {"messages": self.context[-10:]}
                },
                timeout=60
            )
            
            if resp.status_code == 200:
                data = resp.json()
                
                # Actualizar contexto
                self.context.append({"role": "user", "content": command})
                self.context.append({"role": "assistant", "content": data.get("response", "")})
                
                return data.get("response", "Sin respuesta")
            else:
                return f"❌ Error del BRAIN: {resp.status_code}"
        
        except requests.exceptions.Timeout:
            return "⏱️ El BRAIN está pensando... intenta de nuevo"
        except Exception as e:
            return f"❌ Error: {str(e)}"


# Cliente global
brain_client = TelegramBrainClient()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id != ALLOWED_USER_ID:
        logger.warning(f"Acceso no autorizado: {user.id}")
        return
    
    # Verificar conexión al BRAIN
    brain_status = "🟢" if brain_client.connect_to_brain() else "🔴"
    
    await update.message.reply_text(
        f"🤖 **J.A.R.V.I.S. v3.0**\n\n"
        f"Estado del BRAIN: {brain_status}\n\n"
        f"Hola {user.first_name}, soy tu asistente de IA.\n\n"
        f"**Conectado a:**\n"
        f"• 🧠 J.A.R.V.I.S. BRAIN Central\n"
        f"• 📊 Dashboard Web\n"
        f"• 📱 App Android\n\n"
        f"**Comandos:**\n"
        f"• `/start` - Iniciar\n"
        f"• `/help` - Ayuda\n"
        f"• `/status` - Estado del BRAIN\n"
        f"• `/memory` - Mi memoria\n"
        f"• `/plugins` - Plugins activos\n\n"
        f"**Ejemplos:**\n"
        f"• 'Crea un motor de Minecraft'\n"
        f"• 'Analiza https://github.com/...'\n"
        f"• '¿Qué batería tengo?'\n"
        f"• 'Toma una foto'"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    
    await update.message.reply_text(
        "📚 **AYUDA J.A.R.V.I.S. v3.0**\n\n"
        
        "🧠 **SISTEMA CENTRAL:**\n"
        "Todos los comandos se procesan en el BRAIN central,\n"
        "compartiendo memoria entre Telegram, Web y App.\n\n"
        
        "🎮 **CREACIÓN:**\n"
        "• 'Crea un motor de Minecraft'\n"
        "• 'Crea proyecto web en Python'\n\n"
        
        "📊 **ANÁLISIS:**\n"
        "• 'Analiza https://github.com/user/repo'\n"
        "• 'Explica este código: [código]'\n\n"
        
        "⚡ **OPTIMIZACIÓN:**\n"
        "• 'Optimiza este código: [código]'\n"
        "• 'Convierte de Python a Rust'\n\n"
        
        "📱 **CÁMARA:**\n"
        "• 'Toma una foto'\n"
        "• 'Analiza la última foto'\n\n"
        
        "🧠 **MEMORIA:**\n"
        "• '¿Qué recuerdas de mí?'\n"
        "• 'Guarda que prefiero Python'\n\n"
        
        "🔌 **PLUGINS:**\n"
        "• 'plugins'\n"
        "• 'system_extended:cpu'\n"
        "• 'network_tools:ping 8.8.8.8'"
    )


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    
    try:
        resp = requests.get(f"{BRAIN_URL}/brain/status", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            
            status_text = (
                f"🧠 **J.A.R.V.I.S. BRAIN Status**\n\n"
                f"📊 **General:**\n"
                f"• Versión: {data.get('version', 'N/A')}\n"
                f"• Uptime: {data.get('uptime', 'N/A')}\n"
                f"• Clientes: {data.get('connected_clients', 0)}\n"
                f"• Interfaces: {', '.join(data.get('active_interfaces', []))}\n"
                f"• Comandos: {data.get('total_commands', 0)}\n\n"
                f"🧠 **Memoria:**\n"
                f"• Largo plazo: {data.get('memory', {}).get('long_term_count', 0)}\n"
                f"• Conversaciones: {data.get('memory', {}).get('conversation_count', 0)}\n\n"
                f"📈 **Aprendizaje:**\n"
                f"• Tasa de éxito: {data.get('learning', {}).get('success_rate', 0)*100:.1f}%\n"
                f"• Patrones: {data.get('learning', {}).get('learned_patterns', 0)}\n\n"
                f"🔌 **Plugins:**\n"
                f"• Cargados: {data.get('plugins', {}).get('loaded_plugins', 0)}\n"
                f"• Comandos: {data.get('plugins', {}).get('total_commands', 0)}"
            )
            
            await update.message.reply_text(status_text)
        else:
            await update.message.reply_text("❌ No se pudo obtener el estado del BRAIN")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    
    try:
        resp = requests.get(f"{BRAIN_URL}/brain/memory/stats", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            
            memory_text = (
                f"🧠 **Memoria de J.A.R.V.I.S.**\n\n"
                f"📊 **Estadísticas:**\n"
                f"• Largo plazo: {data.get('long_term_count', 0)} memorias\n"
                f"• Conversaciones: {data.get('conversation_count', 0)}\n"
                f"• Preferencias: {data.get('preferences_count', 0)}\n"
                f"• Conocimiento: {data.get('knowledge_count', 0)}\n\n"
                f"💡 *La memoria es compartida entre todas las interfaces*"
            )
            
            await update.message.reply_text(memory_text)
        else:
            await update.message.reply_text("❌ No se pudo obtener la memoria")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def plugins_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id != ALLOWED_USER_ID:
        return
    
    try:
        resp = requests.get(f"{BRAIN_URL}/brain/plugins", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            
            plugins_text = "🔌 **Plugins Activos:**\n\n"
            for plugin in data.get("plugins", []):
                status = "✅" if plugin.get("enabled") else "❌"
                plugins_text += f"{status} **{plugin.get('name')}** v{plugin.get('version')}\n"
                plugins_text += f"   {plugin.get('description')}\n\n"
            
            await update.message.reply_text(plugins_text)
        else:
            await update.message.reply_text("❌ No se pudo obtener la lista de plugins")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if user.id != ALLOWED_USER_ID:
        return
    
    # Mostrar "escribiendo..."
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    user_message = update.message.text
    logger.info(f"Telegram: {user_message[:50]}...")
    
    # Enviar al BRAIN
    loop = asyncio.get_event_loop()
    response = await loop.run_in_executor(
        None, brain_client.send_command, user_message
    )
    
    # Enviar respuesta (dividir si es larga)
    if len(response) > 4096:
        for i in range(0, len(response), 4096):
            await update.message.reply_text(response[i:i+4096])
    else:
        await update.message.reply_text(response)


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Error: {context.error}")


def main() -> None:
    logger.info("🔌 Iniciando J.A.R.V.I.S. Telegram Bot...")
    
    # Conectar al BRAIN
    brain_client.connect_to_brain()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("memory", memory_command))
    app.add_handler(CommandHandler("plugins", plugins_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    logger.info("✅ Telegram Bot conectado al BRAIN")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
