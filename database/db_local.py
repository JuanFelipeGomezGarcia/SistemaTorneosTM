import streamlit as st
from datetime import datetime

class LocalDatabaseOperations:
    def __init__(self):
        # Inicializar datos en session_state
        if 'torneos_data' not in st.session_state:
            st.session_state.torneos_data = []
        if 'categorias_data' not in st.session_state:
            st.session_state.categorias_data = []
        if 'participantes_data' not in st.session_state:
            st.session_state.participantes_data = []
        if 'partidos_data' not in st.session_state:
            st.session_state.partidos_data = []
        if 'next_id' not in st.session_state:
            st.session_state.next_id = {'torneos': 1, 'categorias': 1, 'participantes': 1, 'partidos': 1}
    
    def verificar_admin(self, usuario, password):
        # Siempre retorna True para acceso local
        return True
    
    def crear_torneo(self, nombre, fecha):
        try:
            torneo_id = st.session_state.next_id['torneos']
            st.session_state.next_id['torneos'] += 1
            
            torneo = {
                'id': torneo_id,
                'nombre': nombre,
                'fecha': fecha.strftime('%Y-%m-%d'),
                'estado': 'en_curso',
                'created_at': datetime.now().isoformat()
            }
            st.session_state.torneos_data.append(torneo)
            return torneo_id
        except Exception as e:
            st.error(f"Error creando torneo: {e}")
            return None
    
    def obtener_torneos(self):
        return sorted(st.session_state.torneos_data, key=lambda x: x['created_at'], reverse=True)
    
    def actualizar_estado_torneo(self, torneo_id, estado):
        try:
            for torneo in st.session_state.torneos_data:
                if torneo['id'] == torneo_id:
                    torneo['estado'] = estado
                    return True
            return False
        except:
            return False
    
    def crear_categoria(self, torneo_id, nombre, cantidad_cuadros, personas_por_cuadro):
        try:
            categoria_id = st.session_state.next_id['categorias']
            st.session_state.next_id['categorias'] += 1
            
            categoria = {
                'id': categoria_id,
                'torneo_id': torneo_id,
                'nombre': nombre,
                'cantidad_cuadros': cantidad_cuadros,
                'personas_por_cuadro': personas_por_cuadro,
                'ganador': None,
                'created_at': datetime.now().isoformat()
            }
            st.session_state.categorias_data.append(categoria)
            return categoria_id
        except Exception as e:
            st.error(f"Error creando categoría: {e}")
            return None
    
    def obtener_categorias(self, torneo_id):
        return [cat for cat in st.session_state.categorias_data if cat['torneo_id'] == torneo_id]
    
    def actualizar_categoria(self, categoria_id, nombre, cantidad_cuadros, personas_por_cuadro):
        try:
            for categoria in st.session_state.categorias_data:
                if categoria['id'] == categoria_id:
                    categoria['nombre'] = nombre
                    categoria['cantidad_cuadros'] = cantidad_cuadros
                    categoria['personas_por_cuadro'] = personas_por_cuadro
                    return True
            return False
        except:
            return False
    
    def agregar_participante(self, categoria_id, nombre, cuadro_numero=None, posicion_en_cuadro=None):
        try:
            participante_id = st.session_state.next_id['participantes']
            st.session_state.next_id['participantes'] += 1
            
            participante = {
                'id': participante_id,
                'categoria_id': categoria_id,
                'nombre': nombre,
                'cuadro_numero': cuadro_numero,
                'posicion_en_cuadro': posicion_en_cuadro,
                'created_at': datetime.now().isoformat()
            }
            st.session_state.participantes_data.append(participante)
            return True
        except:
            return False
    
    def obtener_participantes(self, categoria_id):
        return [p for p in st.session_state.participantes_data if p['categoria_id'] == categoria_id]
    
    def actualizar_participante_cuadro(self, participante_id, cuadro_numero, posicion_en_cuadro):
        try:
            for participante in st.session_state.participantes_data:
                if participante['id'] == participante_id:
                    participante['cuadro_numero'] = cuadro_numero
                    participante['posicion_en_cuadro'] = posicion_en_cuadro
                    return True
            return False
        except:
            return False
    
    def guardar_resultado_partido(self, categoria_id, cuadro_numero, jugador1, jugador2, resultado, ganador):
        try:
            # Buscar partido existente
            for partido in st.session_state.partidos_data:
                if (partido['categoria_id'] == categoria_id and 
                    partido['cuadro_numero'] == cuadro_numero and
                    partido['jugador1'] == jugador1 and 
                    partido['jugador2'] == jugador2):
                    # Actualizar
                    partido['resultado'] = resultado
                    partido['ganador'] = ganador
                    partido['updated_at'] = datetime.now().isoformat()
                    return True
            
            # Crear nuevo
            partido_id = st.session_state.next_id['partidos']
            st.session_state.next_id['partidos'] += 1
            
            partido = {
                'id': partido_id,
                'categoria_id': categoria_id,
                'cuadro_numero': cuadro_numero,
                'jugador1': jugador1,
                'jugador2': jugador2,
                'resultado': resultado,
                'ganador': ganador,
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            st.session_state.partidos_data.append(partido)
            return True
        except:
            return False
    
    def obtener_partidos(self, categoria_id):
        return [p for p in st.session_state.partidos_data if p['categoria_id'] == categoria_id]