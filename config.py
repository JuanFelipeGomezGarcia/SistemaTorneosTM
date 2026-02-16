"""Configuración centralizada de la aplicación"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Supabase
    SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qxhjsmcfucqnsvlsbhef.supabase.co")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4aGpzbWNmdWNxbnN2bHNiaGVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU0MTgzOTMsImV4cCI6MjA4MDk5NDM5M30.BZXdEUdVlOJ2v-ktu0QJkMZKQtcwxT0x662DeiaCHnA")
    
    # App
    PAGE_TITLE = "Sistema de Torneos - Tenis de Mesa"
    PAGE_ICON = "🏓"
    LAYOUT = "wide"
    
    # Estados
    ESTADO_EN_CURSO = 'en_curso'
    ESTADO_FINALIZADO = 'finalizado'
