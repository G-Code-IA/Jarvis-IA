# 🧠 J.A.R.V.I.S.

**Just A Rather Very Intelligent System**

Asistente de IA personal con cerebro central unificado, inspirado en el J.A.R.V.I.S. de Iron Man.

---

## ✨ Características

| Capacidad | Descripción |
|-----------|-------------|
| 🗣️ **Conversación natural** | Habla como Siri/Gemini, entiende contexto y seguimientos |
| 🧠 **Memoria persistente** | Recuerda conversaciones, preferencias y conocimientos |
| 📈 **Aprendizaje automático** | Aprende patrones, se auto-optimiza |
| 🔌 **Sistema de plugins** | 4 plugins built-in, extensible |
| 📊 **Análisis de GitHub** | Analiza cualquier repositorio |
| 📷 **Cámara con IA** | Toma fotos, analiza con visión artificial |
| ⏰ **Automatización** | Tareas programadas, triggers, workflows |
| 🎤 **Control por voz** | TTS/STT, modo Siri |
| 🌐 **Multi-interfaz** | Telegram, Web Dashboard, App Android |

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────┐
│     J.A.R.V.I.S. BRAIN (FastAPI)        │
│     Puerto: 8000                        │
│                                         │
│  ┌───────────────────────────────────┐  │
│  │  Memoria Persistente (SQLite)     │  │
│  │  Aprendizaje Automático           │  │
│  │  Plugins (4 built-in)             │  │
│  │  Motor Conversacional             │  │
│  │  Motor de Razonamiento            │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
           │         │         │
    ┌──────┘         │         └──────┐
    ▼                ▼                ▼
┌─────────┐  ┌────────────┐  ┌──────────────┐
│Telegram │  │Web         │  │Android App   │
│Bot      │  │Dashboard   │  │(Flutter)     │
└─────────┘  └────────────┘  └──────────────┘
```

---

## 🚀 Instalación

### Requisitos
- Python 3.10+
- Ollama (con modelo qwen2.5-coder:1.5b)
- Termux (en Android)

### Setup

```bash
# Clonar repo
git clone https://github.com/G-Code-IA/Jarvis-IA.git
cd Jarvis-IA

# Instalar dependencias
pip install -r requirements.txt

# Iniciar Ollama
ollama pull qwen2.5-coder:1.5b
ollama serve &

# Iniciar J.A.R.V.I.S.
python jarvis_brain.py &
python telegram_brain.py &
```

---

## 📁 Estructura

```
Jarvis-IA/
├── 🧠 jarvis_brain.py          # Cerebro central (FastAPI)
├── 📱 telegram_brain.py        # Bot de Telegram
│
├── 📦 memory_system.py         # Memoria persistente
├── 📦 plugin_system.py         # Sistema de plugins
├── 📦 voice_automation.py      # Voz y automatización
├── 📦 camera_module.py         # Cámara
├── 📦 ai_developer.py          # Desarrollo con IA
├── 📦 reasoning_engine.py      # Motor de razonamiento
├── 📦 conversational_engine.py # Motor conversacional
├── 📦 jarvis_personality.py    # Personalidad
│
├── 🌐 web_dashboard/           # Dashboard web unificado
│   └── index.html
│
├── 📱 flutter_app/             # App Android
│   └── lib/
│       ├── main.dart
│       └── siri_mode.dart
│
└── 📋 requirements.txt         # Dependencias Python
```

---

## 🌐 Interfaces

### 1. Web Dashboard
```
http://localhost:8000/dashboard/
```
- Chat tipo ChatGPT
- Estado del sistema
- Gestión de plugins
- Control de cámara

### 2. Telegram Bot
```
@Redmi_claw_bot
```
- Comandos conversacionales
- Mismas capacidades que el web
- Memoria compartida

### 3. API Directa
```bash
curl -X POST http://localhost:8000/brain/command \
  -H "Content-Type: application/json" \
  -d '{"command": "batería", "interface": "api"}'
```

---

## 💬 Ejemplos de Uso

### Conversación natural
```
Tú: Hola!
JARVIS: ¡Hey! 😊 ¿Qué necesitas?

Tú: ¿Cuánta batería tengo?
JARVIS: 🔋 Tu batería está así: 73%...

Tú: Analiza github.com/luanti-org/luanti
JARVIS: 📊 Analicé ese repo por ti:
      Luanti (formerly Minetest)...
      ⭐ Stars: 12492

Tú: ¿Qué te pareció?
JARVIS: Me pareció interesante! Es un proyecto activo...
```

### Comandos disponibles
```
🔋 "¿Cuánta batería tengo?"
📊 "Analiza https://github.com/..."
🔍 "Busca noticias de IA"
📸 "Toma una foto"
📁 "Crea un archivo llamado..."
🔌 "¿Qué plugins tienes?"
🧠 "¿Qué recuerdas?"
```

---

## 🔌 Plugins

| Plugin | Comandos |
|--------|----------|
| **System Extended** | `cpu`, `memory`, `network`, `processes` |
| **Network Tools** | `ping`, `scan`, `dns` |
| **Integrations** | `github`, `weather`, `crypto` |
| **Dev Tools** | `git_clone`, `pip_install`, `file_tree`, `code_stats` |

---

## 🧠 Memoria

J.A.R.V.I.S. recuerda:
- ✅ Conversaciones anteriores
- ✅ Preferencias del usuario
- ✅ Conocimiento aprendido
- ✅ Patrones de uso

La memoria es **compartida** entre todas las interfaces.

---

## 📊 API Endpoints

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/brain/status` | Estado del cerebro |
| `POST` | `/brain/command` | Ejecutar comando |
| `GET` | `/brain/memory/stats` | Estadísticas de memoria |
| `GET` | `/brain/plugins` | Lista de plugins |
| `GET` | `/brain/reasoning` | Estadísticas de razonamiento |
| `POST` | `/brain/camera/take` | Tomar foto |
| `GET` | `/brain/camera/photos` | Listar fotos |
| `WS` | `/ws/{client_id}` | WebSocket tiempo real |

---

## 🛣️ Roadmap

- [ ] Activación por voz "Hey JARVIS" en background
- [ ] Modo proactivo (sugerencias automáticas)
- [ ] Control de smart home
- [ ] Ejecución de código en sandbox
- [ ] Lectura de documentos PDF
- [ ] Navegación web autónoma
- [ ] Calendario y agenda
- [ ] Auto-mejora continua

---

## 📄 Licencia

Apache License 2.0 - Ver [LICENSE](LICENSE) para detalles.

---

## 🙏 Créditos

- **Ollama** - Motor de IA local
- **FastAPI** - Backend API
- **python-telegram-bot** - Bot de Telegram
- **Flutter** - App Android

---

**"A veces necesitas correr antes de caminar"** - Tony Stark
