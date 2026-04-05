#!/bin/bash
# J.A.R.V.I.S. - Compilador de APKs Android

echo "🔨 J.A.R.V.I.S. - Compilador de APK"
echo "===================================="

WORKING_DIR="/data/data/com.termux/files/home/Jarvis"
FLUTTER_DIR="$WORKING_DIR/flutter_app"

# Verificar Flutter
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter no instalado"
    echo "Instala con: pkg install flutter"
    exit 1
fi

echo "✅ Flutter detectado"
flutter --version

# Navegar al proyecto
cd "$FLUTTER_DIR" || exit 1

# Limpiar
echo "🧹 Limpiando proyecto..."
flutter clean

# Obtener dependencias
echo "📦 Obteniendo dependencias..."
flutter pub get

# Compilar APK
echo "🔨 Compilando APK..."
flutter build apk --release

# Verificar resultado
APK_PATH="$FLUTTER_DIR/build/app/outputs/flutter-apk/app-release.apk"
if [ -f "$APK_PATH" ]; then
    echo ""
    echo "✅ ¡APK compilada exitosamente!"
    echo "📁 Ubicación: $APK_PATH"
    echo "📊 Tamaño: $(du -h "$APK_PATH" | cut -f1)"
    echo ""
    echo "Para instalar en tu dispositivo:"
    echo "  adb install $APK_PATH"
else
    echo "❌ Error al compilar APK"
    exit 1
fi
