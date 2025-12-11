from .supabase_config import get_supabase
import streamlit as st
from datetime import datetime

class DatabaseOperations:
    def __init__(self):
        self.supabase = get_supabase()
    
    # Operaciones de Administradores
    def verificar_admin(self, usuario, password):
        try:
            response = self.supabase.table('administradores').select('*').eq('usuario', usuario).eq('password', password).execute()
            return len(response.data) > 0
        except:
            return False
    
    # Operaciones de Torneos
    def crear_torneo(self, nombre, fecha):
        try:
            response = self.supabase.table('torneos').insert({
                'nombre': nombre,
                'fecha': fecha.strftime('%Y-%m-%d'),
                'estado': 'en_curso'
            }).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            st.error(f"Error creando torneo: {e}")
            return None
    
    def obtener_torneos(self):
        try:
            response = self.supabase.table('torneos').select('*').order('created_at', desc=True).execute()
            return response.data
        except:
            return []
    
    def actualizar_estado_torneo(self, torneo_id, estado):
        try:
            self.supabase.table('torneos').update({'estado': estado}).eq('id', torneo_id).execute()
            return True
        except:
            return False
    
    # Operaciones de Categorías
    def crear_categoria(self, torneo_id, nombre, cantidad_cuadros, personas_por_cuadro):
        try:
            response = self.supabase.table('categorias').insert({
                'torneo_id': torneo_id,
                'nombre': nombre,
                'cantidad_cuadros': cantidad_cuadros,
                'personas_por_cuadro': personas_por_cuadro
            }).execute()
            return response.data[0]['id'] if response.data else None
        except Exception as e:
            st.error(f"Error creando categoría: {e}")
            return None
    
    def obtener_categorias(self, torneo_id):
        try:
            response = self.supabase.table('categorias').select('*').eq('torneo_id', torneo_id).execute()
            return response.data
        except:
            return []
    
    def actualizar_categoria(self, categoria_id, nombre, cantidad_cuadros, personas_por_cuadro):
        try:
            self.supabase.table('categorias').update({
                'nombre': nombre,
                'cantidad_cuadros': cantidad_cuadros,
                'personas_por_cuadro': personas_por_cuadro
            }).eq('id', categoria_id).execute()
            return True
        except:
            return False
    
    # Operaciones de Participantes
    def agregar_participante(self, categoria_id, nombre, cuadro_numero=None, posicion_en_cuadro=None):
        try:
            self.supabase.table('participantes').insert({
                'categoria_id': categoria_id,
                'nombre': nombre,
                'cuadro_numero': cuadro_numero,
                'posicion_en_cuadro': posicion_en_cuadro
            }).execute()
            return True
        except:
            return False
    
    def obtener_participantes(self, categoria_id):
        try:
            response = self.supabase.table('participantes').select('*').eq('categoria_id', categoria_id).execute()
            return response.data
        except:
            return []
    
    def actualizar_participante_cuadro(self, participante_id, cuadro_numero, posicion_en_cuadro):
        try:
            self.supabase.table('participantes').update({
                'cuadro_numero': cuadro_numero,
                'posicion_en_cuadro': posicion_en_cuadro
            }).eq('id', participante_id).execute()
            return True
        except:
            return False
    
    # Operaciones de Partidos
    def guardar_resultado_partido(self, categoria_id, cuadro_numero, jugador1, jugador2, resultado, ganador):
        try:
            # Verificar si ya existe el partido
            existing = self.supabase.table('partidos').select('*').eq('categoria_id', categoria_id).eq('cuadro_numero', cuadro_numero).eq('jugador1', jugador1).eq('jugador2', jugador2).execute()
            
            if existing.data:
                # Actualizar
                self.supabase.table('partidos').update({
                    'resultado': resultado,
                    'ganador': ganador,
                    'updated_at': datetime.now().isoformat()
                }).eq('id', existing.data[0]['id']).execute()
            else:
                # Crear nuevo
                self.supabase.table('partidos').insert({
                    'categoria_id': categoria_id,
                    'cuadro_numero': cuadro_numero,
                    'jugador1': jugador1,
                    'jugador2': jugador2,
                    'resultado': resultado,
                    'ganador': ganador
                }).execute()
            return True
        except:
            return False
    
    def obtener_partidos(self, categoria_id):
        try:
            response = self.supabase.table('partidos').select('*').eq('categoria_id', categoria_id).execute()
            return response.data
        except:
            return []