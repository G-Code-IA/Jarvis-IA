# 🧠 J.A.R.V.I.S. v3.0 - ARQUITECTURA DE CEREBRO CENTRAL

## Arquitectura Unificada

```
┌─────────────────────────────────────────────────────────┐
│           J.A.R.V.I.S. BRAIN v3.0                       │
│           (Cerebro Central en FastAPI)                  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Memoria Persistente (SQLite)                    │  │
│  │  - Conversaciones compartidas                    │  │
│  │  - Preferencias de usuario                       │  │
│  │  - Conocimiento aprendido                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Sistema de Aprendizaje                          │  │
│  │  - Patrones de comandos                          │  │
│  │  - Auto-optimización                             │  │
│  │  - Estadísticas de rendimiento                   │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Plugins (4 built-in)                            │  │
│  │  - System Extended                               │  │
│  │  - Network Tools                                 │  │
│  │  - Integrations                                  │  │
│  │  - Dev Tools                                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Módulos                                         │  │
│  │  - Cámara                                        │  │
│  │  - Automatización                                │  │
│  │  - Workflows                                     │  │
│  │  - Voz (TTS/STT)                                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
           │              │              │
    ┌──────┴──────┐ ┌────┴────┐ ┌──────┴──────┐
    │             │ │         │ │             │
┌───▼────┐  ┌─────▼─────┐ ┌──▼──────────┐
│Telegram│  │Dashboard  │ │Android App  │
│Bot     │  │Web        │ │(Flutter)    │
└────────┘  └───────────┘ └─────────────┘
```

---

## 📋 ÍNDICE

1. [Arquitectura](#arquitectura)
2. [Instalación](#instalación)
3. [Uso por Interfaz](#uso-por-interfaz)
4. [API del BRAIN](#api-del-brain)
5. [Memoria Compartida](#memoria-compartida)
6. [Plugins](#plugins)

---

## 🏗️ ARQUITECTURA

### BRAIN Central (`jarvis_brain.py`)

El cerebro es una API FastAPI que:
- ✅ Procesa comandos de TODAS las interfaces
- ✅ Mantiene memoria compartida
- ✅ Aprende de todas las interacciones
- ✅ Broadcast de eventos en tiempo real
- ✅ Gestiona sesiones de clientes

### Interfaces

| Interfaz | Archivo | Puerto | Protocolo |
|----------|---------|--------|-----------|
| **Telegram** | `telegram_brain.py` | - | Polling |
| **Web Dashboard** | `web_dashboard/brain.html` | 8000 | WebSocket |
| **Android App** | `flutter_app/` | - | HTTP/WebSocket |
| **API Directa** | - | 8000 | REST |

---

## 🚀 INSTALACIÓN

### Paso 1: Dependencias

```bash
cd ~/Jarvis
pip install -r requirements.txt
```

### Paso 2: Iniciar el BRAIN

```bash
python jarvis_brain.py &
```

### Paso 3: Iniciar Interfaces

**Telegram:**
```bash
python telegram_brain.py
```

**Web Dashboard:**
```
Abre: http://localhost:8000/dashboard
O: http://localhost:8000/brain.html
```

**Android App:**
```bash
cd flutter_app
flutter build apk --release
```

---

## 💬 USO POR INTERFAZ

### 1. Telegram

```
@Redmi_claw_bot

Comandos:
/start - Iniciar
/help - Ayuda
/status - Estado del BRAIN
/memory - Mi memoria
/plugins - Plugins activos

Mensajes:
"Crea un motor de Minecraft"
"¿Qué batería tengo?"
"Analiza https://github.com/..."
```

### 2. Web Dashboard

```
http://localhost:8000/brain.html

Características:
- Chat en tiempo real (WebSocket)
- Visualización del BRAIN
- Estadísticas en vivo
- Eventos broadcast
```

### 3. Android App

```
Dos modos:
1. 🎤 Modo Siri - Control por voz
2. 📊 Dashboard - Interfaz gráfica

Comandos de voz:
"Hey JARVIS, ¿cuánta batería tengo?"
"Hey JARVIS, toma una foto"
```

---

## 🔌 API DEL BRAIN

### Endpoints Principales

```bash
# Estado del BRAIN
GET /brain/status

# Ejecutar comando
POST /brain/command
{
    "command": "batería",
    "interface": "telegram",
    "user_id": 8406954800
}

# WebSocket (tiempo real)
WS /ws/{client_id}

# Memoria
GET /brain/memory/stats
GET /brain/memory/long-term

# Aprendizaje
GET /brain/learning/stats
GET /brain/learning/patterns

# Plugins
GET /brain/plugins
GET /brain/plugins/commands

# Automatización
GET /brain/automation/tasks
POST /brain/automation/task

# Cámara
POST /brain/camera/take
GET /brain/camera/photos
POST /brain/camera/analyze
```

### Ejemplo de Uso

```python
import requests

# Comando al BRAIN
r = requests.post('http://localhost:8000/brain/command',
    json={
        'command': 'batería',
        'interface': 'api',
        'user_id': 8406954800
    }
)
print(r.json()['response'])

# WebSocket
from websocket import create_connection
ws = create_connection('ws://localhost:8000/ws/mi_cliente')
ws.send('{"type": "command", "command": "hola"}')
print(ws.recv())
```

---

## 🧠 MEMORIA COMPARTIDA

### Lo que recuerda el BRAIN

| Tipo | Descripción | Persistencia |
|------|-------------|--------------|
| **Largo Plazo** | Información importante | Permanente |
| **Conversaciones** | Historial de chats | Permanente |
| **Preferencias** | Gustos del usuario | Permanente |
| **Conocimiento** | Datos aprendidos | Permanente |
| **Contexto** | Estado actual | Temporal |

### Ejemplos

```
# En Telegram:
"Guarda que prefiero Python"

# En Web Dashboard:
"¿Qué recuerdas de mí?"
→ Muestra: "Prefieres Python"

# En Android App:
"¿Cuál es mi lenguaje favorito?"
→ Responde: "Python"
```

**¡La memoria es COMPARTIDA entre todas las interfaces!**

---

## 🔌 PLUGINS

### Built-in Plugins

#### 1. System Extended
```
Comandos:
- system_extended:cpu
- system_extended:memory
- system_extended:network
- system_extended:processes
```

#### 2. Network Tools
```
Comandos:
- network_tools:ping 8.8.8.8
- network_tools:scan localhost
- network_tools:dns
```

#### 3. Integrations
```
Comandos:
- integrations:github torvalds/linux
- integrations:weather Madrid
- integrations:crypto bitcoin
```

#### 4. Dev Tools
```
Comandos:
- dev_tools:git_clone https://...
- dev_tools:pip_install requests
- dev_tools:file_tree
- dev_tools:code_stats
```

### Usar Plugins

**Desde cualquier interfaz:**

Telegram:
```
system_extended:cpu
```

Web:
```javascript
ws.send(JSON.stringify({
    type: 'plugin_command',
    plugin: 'system_extended',
    command: 'cpu'
}));
```

Android:
```
Di: "Usa el plugin de sistema para ver la CPU"
```

---

## 📊 ESTADÍSTICAS EN TIEMPO REAL

El BRAIN muestra:

```
🧠 Memorias: 150
📈 Patrones: 25
🔌 Plugins: 4
⏰ Tareas: 10
📊 Éxito: 95%
⚡ Tiempo Prom: 1.2s
```

---

## 🎯 FLUJO DE COMANDO

```
1. Usuario dice "batería" en Telegram
       ↓
2. Telegram envía al BRAIN
       ↓
3. BRAIN procesa (plugins, memoria, etc.)
       ↓
4. BRAIN guarda en memoria
       ↓
5. BRAIN responde a Telegram
       ↓
6. BRAIN broadcast a Web y App
       ↓
7. Todas las interfaces ven el comando
```

---

## 📁 ARCHIVOS PRINCIPALES

```
Jarvis/
├── jarvis_brain.py         # 🧠 CEREBRO CENTRAL
├── telegram_brain.py       # 📱 Telegram Bot
├── jarvis_ai_dev.py        # 🤖 IA Core (legacy)
│
├── memory_system.py        # 🧠 Memoria
├── learning_system.py      # 📈 Aprendizaje
├── plugin_system.py        # 🔌 Plugins
├── voice_automation.py     # 🎤 Voz
├── camera_module.py        # 📷 Cámara
│
├── web_dashboard/
│   ├── brain.html          # 🌐 Dashboard BRAIN
│   └── index.html          # Dashboard legacy
│
├── flutter_app/
│   ├── lib/main.dart       # 📲 App Android
│   └── lib/siri_mode.dart  # 🎤 Modo Siri
│
└── requirements.txt        # 📦 Dependencias
```

---

## 🚀 COMANDOS PARA PROBAR

### Desde cualquier interfaz:

```
# Sistema
"batería"
"sistema"
"procesos"

# Memoria
"¿Qué recuerdas de mí?"
"Guarda que me gusta Python"
"memoria"

# Plugins
"plugins"
"system_extended:cpu"
"network_tools:ping 8.8.8.8"
"integrations:crypto bitcoin"

# Creación
"Crea un motor de Minecraft"
"Analiza https://github.com/torvalds/linux"

# Cámara
"toma una foto"
"analiza la última foto"

# Automatización
"programar tarea batería daily 08:00"
"ver tareas"
```

---

## 💡 VENTAJAS DE ESTA ARQUITECTURA

1. **Memoria Única**: Lo que aprendes en Telegram, lo sabe la App
2. **Procesamiento Central**: Todo pasa por el BRAIN
3. **Tiempo Real**: WebSocket broadcast a todas las interfaces
4. **Escalable**: Puedes agregar más interfaces sin cambiar el core
5. **Plugins Compartidos**: Un plugin funciona en TODAS las interfaces
6. **Aprendizaje Continuo**: Mejora con cada interacción

---

## 🎉 ¡J.A.R.V.I.S. v3.0 ESTÁ COMPLETO!

**Un cerebro, múltiples interfaces, infinitas posibilidades.** 🧠
