"""
Componente de Bracket Dinámico para Torneos
Usa declare_component para comunicación bidireccional confiable entre JS y Python.
"""

import streamlit as st
import streamlit.components.v1 as components
import math
import os
from database.db_operations import DatabaseOperations

# Declarar componente custom con path al directorio que contiene index.html
_COMPONENT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "components", "bracket")
_bracket_component = components.declare_component("bracket_component", path=_COMPONENT_DIR)


def render_bracket(players, categoria_id, puede_editar=True, torneo_id=None, seed_map=None):
    """
    Renderiza el bracket en Streamlit usando un componente custom bidireccional.
    
    Args:
        players: Lista de jugadores ya en POSICIÓN FINAL del bracket (incluye BYEs).
                 El orden refleja el seeding y cross-group matching.
        categoria_id: ID de la categoría.
        puede_editar: Si el usuario puede seleccionar ganadores.
        torneo_id: ID del torneo (para auto-finalización).
        seed_map: Dict {nombre_jugador: número_de_seed} para mostrar seeds correctos.
    """
    # Contar jugadores reales (sin BYEs)
    real_players = [p for p in players if p != "BYE"]
    num_real_players = len(real_players)
    num_total = len(players)
    num_rounds = math.ceil(math.log2(num_total)) if num_total > 1 else 1
    next_power = 2 ** num_rounds
    
    # Asegurar que la lista tenga tamaño next_power
    bracket_players = list(players)
    while len(bracket_players) < next_power:
        bracket_players.append("BYE")
    
    # Si no se proporcionó seed_map, generar uno básico
    if seed_map is None:
        seed_map = {}
        counter = 1
        for p in bracket_players:
            if p != "BYE" and p not in seed_map:
                seed_map[p] = counter
                counter += 1
    
    # Keys para session_state
    bracket_key = f'bracket_state_{categoria_id}'
    campeon_key = f'campeon_{categoria_id}'
    
    # Instanciar DB
    db = DatabaseOperations()
    
    # Cargar desde DB SOLO si no hay estado local
    if bracket_key not in st.session_state:
        st.session_state[bracket_key] = {}
        db_state_data = db.obtener_estado_llaves(categoria_id)
        if db_state_data:
            raw_state = db_state_data.get('bracket_state', {})
            converted_state = {}
            for k, v in raw_state.items():
                if k.isdigit():
                    converted_state[int(k)] = v
                else:
                    converted_state[k] = v
            st.session_state[bracket_key] = converted_state
            if db_state_data.get('campeon'):
                st.session_state[campeon_key] = db_state_data['campeon']
    
    bracket_state = st.session_state[bracket_key]
    
    # Inicializar bracket si está vacío
    if not bracket_state or 1 not in bracket_state:
        bracket_state[1] = bracket_players[:]
        for r in range(2, num_rounds + 1):
            prev = bracket_state[r - 1]
            bracket_state[r] = [None] * (len(prev) // 2)
        
        # Procesar BYEs automáticamente
        for r in range(1, num_rounds):
            rplayers = bracket_state[r]
            for i in range(0, len(rplayers), 2):
                p1 = rplayers[i]
                p2 = rplayers[i + 1] if i + 1 < len(rplayers) else None
                if p1 == "BYE" and p2 and p2 != "BYE":
                    bracket_state[r + 1][i // 2] = p2
                elif p2 == "BYE" and p1 and p1 != "BYE":
                    bracket_state[r + 1][i // 2] = p1
        
        st.session_state[bracket_key] = bracket_state
    
    # Convertir keys a string para serialización JSON
    state_for_js = {}
    for k, v in bracket_state.items():
        state_for_js[str(k)] = v
    
    # Calcular altura dinámica
    base_height = max(next_power * 55, 400)
    dynamic_height = min(base_height + 120, 1200)
    
    # Renderizar componente custom bidireccional
    component_value = _bracket_component(
        players=bracket_players,
        bracket_state=state_for_js,
        categoria_id=str(categoria_id),
        can_edit=puede_editar,
        num_rounds=num_rounds,
        num_original_players=num_real_players,
        seed_map=seed_map,
        key=f"bracket_{categoria_id}",
        height=dynamic_height,
    )
    
    # Procesar valor de retorno: el usuario pulsó "Guardar" dentro del bracket
    if component_value is not None:
        new_state_raw = component_value.get('bracket_state', {})
        new_champion = component_value.get('champion')
        
        # Convertir keys de vuelta a int
        new_state = {}
        for k, v in new_state_raw.items():
            if k.isdigit():
                new_state[int(k)] = v
            else:
                new_state[k] = v
        
        # Actualizar session_state
        st.session_state[bracket_key] = new_state
        if new_champion:
            st.session_state[campeon_key] = new_champion
        
        # Guardar automáticamente en DB
        if db.guardar_estado_llaves(categoria_id, new_state, new_champion):
            st.success("¡Cambios guardados en base de datos!")
            
            # Verificar si TODAS las categorías tienen campeón -> finalizar torneo
            if new_champion and torneo_id:
                torneo_finalizado = db.verificar_torneo_completado(torneo_id)
                if torneo_finalizado:
                    st.balloons()
                    st.success("🏆 ¡TORNEO FINALIZADO! Todas las categorías tienen campeón.")
        else:
            st.error("Error al guardar en base de datos.")
