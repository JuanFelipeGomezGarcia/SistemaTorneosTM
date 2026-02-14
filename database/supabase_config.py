from supabase import create_client, Client
import streamlit as st
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase desde variables de entorno
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://qxhjsmcfucqnsvlsbhef.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF4aGpzbWNmdWNxbnN2bHNiaGVmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjU0MTgzOTMsImV4cCI6MjA4MDk5NDM5M30.BZXdEUdVlOJ2v-ktu0QJkMZKQtcwxT0x662DeiaCHnA")

@st.cache_resource
def init_supabase():
    """Inicializa la conexión con Supabase"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return supabase
    except Exception as e:
        st.error(f"Error conectando a Supabase: {e}")
        return None

def get_supabase():
    """Obtiene la instancia de Supabase"""
    return init_supabase()