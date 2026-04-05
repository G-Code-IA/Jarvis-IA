# 🎤 J.A.R.V.I.S. - MODO SIRI

## 📱 App Android con Control por Voz Completo

---

## 🚀 INSTALACIÓN

### Paso 1: Instalar Flutter

**En Termux:**
```bash
pkg install flutter -y
flutter doctor
```

**En tu PC:**
```bash
# Descarga desde https://flutter.dev
```

### Paso 2: Compilar la APK

```bash
cd ~/Jarvis
./install_app.sh
```

### Paso 3: Instalar en tu Android

```bash
adb install flutter_app/build/app/outputs/flutter-apk/app-release.apk
```

O copia el APK a tu celular e instálalo manualmente.

---

## 🎯 CARACTERÍSTICAS DEL MODO SIRI

### 1. **Activación por Voz** 🎤
- Di **"Hey JARVIS"** para activar
- Di **"OK JARVIS"** para activar
- Escucha continua en segundo plano

### 2. **Respuestas Habladas** 🔊
- J.A.R.V.I.S. te habla con voz natural
- Texto a voz (TTS) en español
- Velocidad y tono ajustables

### 3. **Animaciones Tipo Siri** ⭕
- Orbe azul cuando escucha
- Orbe dorado cuando procesa
- Orbe verde cuando habla

### 4. **Comandos Rápidos** ⚡
- Toca botones para comandos frecuentes
- Batería, Clima, Sistema, etc.

---

## 🗣️ COMANDOS DE VOZ

### Activación
```
"Hey JARVIS"
"OK JARVIS"
"JARVIS"
```

### Comandos
```
"¿Cuánta batería tengo?"
"¿Qué hora es?"
"Muéstrame el sistema"
"Toma una foto"
"Busca noticias de IA"
"Crea un motor de Minecraft"
"¿Qué recuerdas?"
"¿Qué plugins tienes?"
```

---

## 🎨 INTERFAZ

### Pantalla Principal
```
┌─────────────────────────────────┐
│  🤖 J.A.R.V.I.S.     🎤 ⚙️ 🔊  │
├─────────────────────────────────┤
│                                 │
│         [ ORBE ANIMADO ]        │
│      (Azul/Dorado/Verde)        │
│                                 │
├─────────────────────────────────┤
│  "Escuchando..."                │
│                                 │
│  [Respuesta de J.A.R.V.I.S.]    │
│                                 │
├─────────────────────────────────┤
│      [ 🎤 Micrófono ]           │
│                                 │
│  🔋 Bat  🌤️ Clima  📊 Sis       │
│  🧠 Mem  🔌 Plug  📷 Foto       │
└─────────────────────────────────┘
```

### Estados del Orbe

| Color | Estado | Significado |
|-------|--------|-------------|
| 🔵 Azul | Escuchando | Te está escuchando |
| 🟡 Dorado | Procesando | Pensando respuesta |
| 🟢 Verde | Hablando | Te está respondiendo |

---

## ⚙️ CONFIGURACIÓN

### Configurar IP de la API

En `flutter_app/lib/siri_mode.dart`, línea ~35:

```dart
String apiUrl = 'http://192.168.1.100:8000'; // CAMBIA ESTO
```

**Opciones:**
- `http://127.0.0.1:8000` - Si la API está en el mismo celular
- `http://192.168.1.XXX:8000` - Si la API está en tu PC (misma red)
- `http://TU_IP_PUBLICA:8000` - Si la API está en internet

### Permisos de Android

La app necesita:
- ✅ Micrófono (para voz)
- ✅ Internet (para API)

Se conceden automáticamente al instalar.

---

## 🔧 SOLUCIÓN DE PROBLEMAS

### "No escucha mi voz"
1. Verifica permisos de micrófono
2. Sube el volumen del micrófono
3. Habla claro y cerca del celular

### "No responde la API"
1. Verifica que la API esté corriendo
2. Verifica la IP configurada
3. Verifica conexión a internet

### "No habla las respuestas"
1. Sube el volumen del celular
2. Verifica que el TTS esté instalado
3. Reinicia la app

### "La app se cierra"
1. Limpia caché de la app
2. Reinstala la APK
3. Verifica logs con `adb logcat`

---

## 🎯 FLUJO DE USO

```
1. Abres la app
2. Ves el selector de modo
3. Eliges "🎤 Modo Siri"
4. El orbe aparece
5. Dices "Hey JARVIS"
6. El orbe se pone azul (escucha)
7. Dices tu comando
8. El orbe se pone dorado (procesa)
9. El orbe se pone verde (habla)
10. J.A.R.V.I.S. te responde
```

---

## 💡 CONSEJOS

1. **Habla claro**: Pronuncia bien "Hey JARVIS"
2. **Espera el tono**: La app hace un sonido cuando activa
3. **Usa comandos cortos**: Funciona mejor con frases concisas
4. **Configura bien la IP**: Crucial para que funcione
5. **Mantén la app abierta**: Funciona en primer plano

---

## 🚀 COMPILAR PARA PRODUCCIÓN

```bash
cd ~/Jarvis/flutter_app

# APK Release
flutter build apk --release

# APK dividida por arquitectura (más pequeña)
flutter build apk --split-per-abi

# App Bundle (para Play Store)
flutter build appbundle
```

---

## 📊 TAMAÑO DE LA APK

- **APK Universal**: ~50-70 MB
- **APK por ABI**: ~25-35 MB (recomendado)
- **App Bundle**: ~20-30 MB

---

## 🎉 LISTO

¡Ahora tienes un asistente tipo Siri en tu Android!

**Prueba decir:**
- "Hey JARVIS, ¿cuánta batería tengo?"
- "Hey JARVIS, toma una foto"
- "Hey JARVIS, ¿qué plugins tienes?"

---

**"A veces necesitas correr antes de caminar"** - Tony Stark
