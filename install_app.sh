#!/bin/bash
# J.A.R.V.I.S. - Instalador de App Android con Modo Siri

echo "🚀 J.A.R.V.I.S. - Instalador de App Android"
echo "==========================================="

FLUTTER_DIR="/data/data/com.termux/files/home/Jarvis/flutter_app"

# Verificar Flutter
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter no instalado"
    echo ""
    echo "Para instalar Flutter en Termux:"
    echo "  pkg install flutter -y"
    echo ""
    echo "O en tu PC:"
    echo "  https://flutter.dev/docs/get-started/install"
    exit 1
fi

echo "✅ Flutter detectado"
flutter --version

cd "$FLUTTER_DIR" || exit 1

# Limpiar
echo ""
echo "🧹 Limpiando proyecto..."
flutter clean

# Obtener dependencias
echo ""
echo "📦 Obteniendo dependencias..."
flutter pub get

# Verificar permisos de Android
echo ""
echo "📋 Configurando permisos de Android..."

# Crear/actualizar AndroidManifest.xml
MANIFEST_PATH="android/app/src/main/AndroidManifest.xml"
if [ -f "$MANIFEST_PATH" ]; then
    # Agregar permisos si no existen
    if ! grep -q "RECORD_AUDIO" "$MANIFEST_PATH"; then
        sed -i '/<uses-permission android:name="android.permission.INTERNET"\/>/a\    <uses-permission android:name="android.permission.RECORD_AUDIO"/>\n    <uses-permission android:name="android.permission.CAMERA"/>' "$MANIFEST_PATH"
        echo "✅ Permisos de micrófono y cámara agregados"
    fi
fi

# Compilar APK
echo ""
echo "🔨 Compilando APK..."
flutter build apk --release

# Verificar resultado
APK_PATH="$FLUTTER_DIR/build/app/outputs/flutter-apk/app-release.apk"
if [ -f "$APK_PATH" ]; then
    echo ""
    echo "✅ ¡APK compilada exitosamente!"
    echo ""
    echo "📁 Ubicación: $APK_PATH"
    echo "📊 Tamaño: $(du -h "$APK_PATH" | cut -f1)"
    echo ""
    echo "📲 Para instalar:"
    echo "  adb install $APK_PATH"
    echo ""
    echo "O copia el APK a tu dispositivo e instálalo manualmente"
else
    echo ""
    echo "❌ Error al compilar APK"
    echo "Revisa los errores arriba"
    exit 1
fi

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "📖 Instrucciones:"
echo "1. Abre la app en tu Android"
echo "2. Concede permisos de micrófono"
echo "3. Configura la IP de tu API en la app"
echo "4. Di 'Hey JARVIS' o toca el micrófono"
echo ""
