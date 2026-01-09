import streamlit as st
from database.db_operations import DatabaseOperations
import math

def vista_llaves_page():
    """Vista de llaves eliminatorias con diseño profesional"""
    
    # CSS simplificado para bracket funcional
    st.markdown("""
    <style>
    .bracket-container {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
    .round-section {
        margin: 20px 0;
        padding: 15px;
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .round-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .match-item {
        background: #f8f9fa;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        position: relative;
    }
    .final-match {
        border-color: #ffd700;
        background: linear-gradient(135deg, #fff9c4 0%, #ffecb3 100%);
    }
    .player-name {
        font-weight: bold;
        margin: 5px 0;
        padding: 8px 12px;
        background: white;
        border-radius: 5px;
        border: 1px solid #ddd;
    }
    .winner-highlight {
        background: #d4edda;
        border-color: #28a745;
        color: #155724;
    }
    .champion-highlight {
        background: #fff3cd;
        border-color: #ffc107;
        color: #856404;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Validaciones
    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("❌ No hay categoría seleccionada")
        return
    
    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()
    
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    st.title(f"🏆 Llaves - {categoria['nombre']}")
    st.write(f"Torneo: {torneo['nombre']}")
    
    if st.button("← Volver a Cuadros"):
        st.session_state.current_page = 'vista_cuadros'
        st.rerun()
    
    st.markdown("---")
    
    # Obtener clasificados
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    from utils.tournament_utils import generar_cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    partidos = db.obtener_partidos(categoria['id'])
    
    # Calcular clasificados
    clasificados = []
    for cuadro_num in sorted(cuadros.keys()):
        participantes_cuadro = cuadros[cuadro_num]
        if len(participantes_cuadro) < 2:
            continue
            
        victorias = {p: 0 for p in participantes_cuadro}
        
        for partido in partidos:
            if partido['cuadro_numero'] == cuadro_num and partido['ganador']:
                if partido['ganador'] in victorias:
                    victorias[partido['ganador']] += 1
        
        jugadores_ordenados = sorted(participantes_cuadro, key=lambda x: victorias.get(x, 0), reverse=True)
        
        if len(jugadores_ordenados) >= 1:
            clasificados.append(jugadores_ordenados[0])
        if len(jugadores_ordenados) >= 2:
            clasificados.append(jugadores_ordenados[1])
    
    if len(clasificados) < 2:
        st.warning("⚠️ Se necesitan al menos 2 clasificados")
        return
    
    # Mostrar clasificados
    st.subheader(f"🏅 Clasificados ({len(clasificados)} jugadores)")
    cols = st.columns(min(4, len(clasificados)))
    for i, clasificado in enumerate(clasificados):
        with cols[i % len(cols)]:
            st.info(clasificado)
    
    st.markdown("---")
    
    # Generar estructura de bracket
    num_participantes = len(clasificados)
    num_rondas = math.ceil(math.log2(num_participantes)) if num_participantes > 1 else 1
    
    # Inicializar bracket
    bracket_key = f'bracket_{categoria["id"]}'
    if bracket_key not in st.session_state:
        next_power_of_2 = 2 ** num_rondas
        while len(clasificados) < next_power_of_2:
            clasificados.append(None)
        
        bracket = {1: clasificados.copy()}
        for ronda in range(2, num_rondas + 1):
            bracket[ronda] = [None] * (len(bracket[ronda - 1]) // 2)
        
        st.session_state[bracket_key] = bracket
    
    bracket = st.session_state[bracket_key]
    
    # Mostrar bracket simplificado y funcional
    st.subheader("🎯 Bracket Eliminatorio")
    
    st.markdown('<div class="bracket-container">', unsafe_allow_html=True)
    
    # Mostrar cada ronda
    for ronda in range(1, num_rondas + 1):
        # Título de la ronda
        if ronda == num_rondas:
            titulo = "🏆 FINAL"
        elif ronda == num_rondas - 1 and num_rondas > 2:
            titulo = "🥉 SEMIFINAL"
        else:
            titulo = f"Ronda {ronda}"
        
        st.markdown('<div class="round-section">', unsafe_allow_html=True)
        st.markdown(f'<div class="round-header">{titulo}</div>', unsafe_allow_html=True)
        
        participantes_ronda = bracket[ronda]
        
        # Mostrar enfrentamientos
        for i in range(0, len(participantes_ronda), 2):
            if i + 1 < len(participantes_ronda):
                jugador1 = participantes_ronda[i]
                jugador2 = participantes_ronda[i + 1]
                
                if jugador1 and jugador2:
                    match_key = f"match_r{ronda}_m{i//2}"
                    
                    # Clase del enfrentamiento
                    match_class = 'match-item final-match' if ronda == num_rondas else 'match-item'
                    st.markdown(f'<div class="{match_class}">', unsafe_allow_html=True)
                    
                    # Mostrar nombres de jugadores
                    if ronda == num_rondas:
                        # Final - mostrar con indicador de campeón
                        campeon_key = f'campeon_{categoria["id"]}'
                        campeon_actual = st.session_state.get(campeon_key)
                        
                        j1_class = 'player-name champion-highlight' if campeon_actual == jugador1 else 'player-name'
                        j2_class = 'player-name champion-highlight' if campeon_actual == jugador2 else 'player-name'
                        
                        st.markdown(f'<div class="{j1_class}">{jugador1}</div>', unsafe_allow_html=True)
                        st.markdown('<div style="text-align: center; margin: 10px 0; font-weight: bold; color: #ffc107;">🏆 VS 🏆</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="{j2_class}">{jugador2}</div>', unsafe_allow_html=True)
                        
                        if campeon_actual:
                            st.markdown(f'<div style="text-align: center; margin-top: 10px; font-weight: bold; color: #ffc107;">👑 CAMPEÓN: {campeon_actual}</div>', unsafe_allow_html=True)
                    else:
                        # Rondas anteriores
                        ganador_actual = bracket[ronda + 1][i // 2] if ronda < num_rondas else None
                        
                        j1_class = 'player-name winner-highlight' if ganador_actual == jugador1 else 'player-name'
                        j2_class = 'player-name winner-highlight' if ganador_actual == jugador2 else 'player-name'
                        
                        st.markdown(f'<div class="{j1_class}">{jugador1}</div>', unsafe_allow_html=True)
                        st.markdown('<div style="text-align: center; margin: 10px 0; font-weight: bold;">⚔️ VS ⚔️</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="{j2_class}">{jugador2}</div>', unsafe_allow_html=True)
                        
                        if ganador_actual:
                            st.markdown(f'<div style="text-align: center; margin-top: 10px; font-weight: bold; color: #28a745;">➡️ Ganador: {ganador_actual}</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                elif jugador1:  # Pase automático
                    st.info(f"🎯 **{jugador1}** pasa automáticamente")
                    if ronda < num_rondas:
                        bracket[ronda + 1][i // 2] = jugador1
        
        st.markdown('</div>', unsafe_allow_html=True)  # Cerrar round-section
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar bracket-container
    
    # Controles interactivos
    if puede_editar:
        st.markdown("---")
        st.subheader("🎮 Controles del Bracket")
        
        # Crear columnas para los controles
        cols = st.columns(num_rondas)
        
        for ronda in range(1, num_rondas + 1):
            with cols[ronda - 1]:
                if ronda == num_rondas:
                    st.markdown("### 🏆 FINAL")
                elif ronda == num_rondas - 1 and num_rondas > 2:
                    st.markdown("### 🥉 SEMIFINAL")
                else:
                    st.markdown(f"### Ronda {ronda}")
                
                participantes_ronda = bracket[ronda]
                
                for i in range(0, len(participantes_ronda), 2):
                    if i + 1 < len(participantes_ronda):
                        jugador1 = participantes_ronda[i]
                        jugador2 = participantes_ronda[i + 1]
                        
                        if jugador1 and jugador2:
                            match_key = f"match_r{ronda}_m{i//2}"
                            
                            st.markdown(f"**Enfrentamiento {i//2 + 1}:**")
                            
                            if ronda == num_rondas:
                                # Final - seleccionar campeón
                                campeon_key = f'campeon_{categoria["id"]}'
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"👑 {jugador1}", key=f"{match_key}_j1", use_container_width=True):
                                        st.session_state[campeon_key] = jugador1
                                        st.rerun()
                                
                                with col2:
                                    if st.button(f"👑 {jugador2}", key=f"{match_key}_j2", use_container_width=True):
                                        st.session_state[campeon_key] = jugador2
                                        st.rerun()
                            else:
                                # Rondas anteriores
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"✅ {jugador1}", key=f"{match_key}_j1", use_container_width=True):
                                        bracket[ronda + 1][i // 2] = jugador1
                                        st.rerun()
                                
                                with col2:
                                    if st.button(f"✅ {jugador2}", key=f"{match_key}_j2", use_container_width=True):
                                        bracket[ronda + 1][i // 2] = jugador2
                                        st.rerun()
                            
                            st.markdown("---")
    
    # Mostrar campeón final
    campeon_key = f'campeon_{categoria["id"]}'
    campeon_final = st.session_state.get(campeon_key)
    
    if campeon_final:
        st.balloons()
        st.markdown(
            f"""
            <div style='background: linear-gradient(135deg, #FFD700 0%, #FFA000 100%); 
                        border-radius: 25px; padding: 40px; text-align: center; 
                        box-shadow: 0 15px 40px rgba(255,215,0,0.4); 
                        border: 4px solid #FFD700; margin: 40px auto; max-width: 500px;
                        transform: scale(1.05);'>
                <h1 style='color: #333; margin: 0; text-shadow: 3px 3px 6px rgba(0,0,0,0.2); font-size: 2.5em;'>
                    🏆 CAMPEÓN 🏆
                </h1>
                <h2 style='color: #333; margin: 20px 0 0 0; font-size: 2em;'>{campeon_final}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # Botón guardar
    if puede_editar:
        st.markdown("---")
        if st.button("💾 Guardar Bracket", type="primary"):
            st.session_state[bracket_key] = bracket
            st.success("✅ Bracket guardado exitosamente!")
            st.rerun()

if __name__ == "__main__":
    vista_llaves_page()