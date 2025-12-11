#!/usr/bin/env python3
"""
Script de configuración para el Sistema de Torneos
"""

import os
import sys
import subprocess

def install_requirements():
    """Instala las dependencias del proyecto"""
    print("📦 Instalando dependencias...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError:
        print("❌ Error instalando dependencias")
        return False

def create_env_file():
    """Crea el archivo .env basado en el ejemplo"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("📝 Creando archivo .env...")
            with open(".env.example", "r") as example:
                content = example.read()
            
            with open(".env", "w") as env_file:
                env_file.write(content)
            
            print("✅ Archivo .env creado")
            print("⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales de Supabase")
        else:
            print("❌ No se encontró .env.example")
    else:
        print("ℹ️  El archivo .env ya existe")

def check_python_version():
    """Verifica la versión de Python"""
    if sys.version_info < (3, 8):
        print("❌ Se requiere Python 3.8 o superior")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True

def main():
    """Función principal de configuración"""
    print("🏓 Configurando Sistema de Torneos - Tenis de Mesa")
    print("=" * 50)
    
    # Verificar versión de Python
    if not check_python_version():
        sys.exit(1)
    
    # Instalar dependencias
    if not install_requirements():
        sys.exit(1)
    
    # Crear archivo .env
    create_env_file()
    
    print("\n🎉 Configuración completada!")
    print("\n📋 Próximos pasos:")
    print("1. Configura tu cuenta de Supabase (gratuita)")
    print("2. Edita el archivo .env con tus credenciales")
    print("3. Ejecuta el esquema SQL en Supabase")
    print("4. Ejecuta: streamlit run main.py")
    print("\n📖 Lee el README.md para instrucciones detalladas")

if __name__ == "__main__":
    main()