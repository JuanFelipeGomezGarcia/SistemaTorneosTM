import streamlit as st
from database.db_operations import DatabaseOperations
import math

def vista_llaves_page():
    """Vista de llaves eliminatorias con diseño profesional"""
    
    # CSS para bracket horizontal tipo llave tradicional
    st.markdown("""
    <style>
    .tournament-bracket {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 40px 20px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 15px;
        margin: 20px 0;
        overflow-x: auto;
        min-height: 600px;
    }
    .bracket-round {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        margin: 0 30px;
        position: relative;
        min-height: 500px;
    }
    .round-title {
        position: absolute;
        top: -40px;
        left: 50%;
        transform: translateX(-50%);
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 20px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9em;
        white-space: nowrap;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .match-box {
        background: white;
        border: 2px solid #dee2e6;
        border-radius: 8px;
        margin: 10px 0;
        position: relative;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .match-box:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    .final-match {
        border: 3px solid #ffd700;
        background: linear-gradient(135deg, #fff9c4 0%, #ffecb3 100%);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
    }
    .player-slot {
        padding: 12px 20px;
        border-bottom: 1px solid #dee2e6;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 500;
    }
    .player-slot:last-child {
        border-bottom: none;
    }
    .player-slot:hover {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
    }
    .winner-slot {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        font-weight: bold;
    }
    .champion-slot {
        background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
        color: #333;
        font-weight: bold;
    }
    .bracket-line {
        position: absolute;
        background: #6c757d;
        z-index: 1;
    }
    .line-horizontal {
        height: 2px;
        right: -30px;
        top: 50%;
        width: 30px;
        transform: translateY(-1px);
    }
    .line-vertical {
        width: 2px;
        right: -30px;
        background: #6c757d;
    }
    .winner-indicator {
        position: absolute;
        right: -25px;
        top: 50%;
        transform: translateY(-50%);
        background: #28a745;
        color: white;
        padding: 4px 8px;
        border-radius: 10px;
        font-size: 0.8em;
        font-weight: bold;
        white-space: nowrap;
    }
    .champion-indicator {
        background: #ffd700;
        color: #333;
    }
    .bye-match {
        background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
        color: white;
        text-align: center;
        padding: 20px;
        border-radius: 8px;
        font-weight: bold;
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
    
    # Mostrar bracket horizontal tipo llave
    st.subheader("🎯 Bracket Eliminatorio")
    
    # Crear estructura HTML del bracket
    bracket_html = '<div class="tournament-bracket">'
    
    # Generar cada ronda
    for ronda in range(1, num_rondas + 1):
        # Título de la ronda
        if ronda == num_rondas:
            titulo = "🏆 FINAL"
        elif ronda == num_rondas - 1 and num_rondas > 2:
            titulo = "🥉 SEMIFINAL"
        else:
            titulo = f"Ronda {ronda}"
        
        bracket_html += f'<div class="bracket-round">'
        bracket_html += f'<div class="round-title">{titulo}</div>'
        
        participantes_ronda = bracket[ronda]
        
        # Mostrar enfrentamientos
        for i in range(0, len(participantes_ronda), 2):
            if i + 1 < len(participantes_ronda):
                jugador1 = participantes_ronda[i]
                jugador2 = participantes_ronda[i + 1]
                
                if jugador1 and jugador2:
                    match_key = f"match_r{ronda}_m{i//2}"
                    
                    # Clase de la caja
                    match_class = 'match-box final-match' if ronda == num_rondas else 'match-box'
                    bracket_html += f'<div class="{match_class}" style="position: relative;">'
                    
                    # Líneas conectoras
                    if ronda < num_rondas:
                        bracket_html += '<div class="bracket-line line-horizontal"></div>'
                    
                    bracket_html += '</div>'
                
                elif jugador1:  # Pase automático
                    bracket_html += f'<div class="bye-match">🎯 {jugador1}<br><small>Pase automático</small></div>'
                    if ronda < num_rondas:
                        bracket[ronda + 1][i // 2] = jugador1
        
        bracket_html += '</div>'  # Cerrar bracket-round
    
    bracket_html += '</div>'  # Cerrar tournament-bracket
    
    # Mostrar el HTML del bracket
    st.markdown(bracket_html, unsafe_allow_html=True)
    
    # Ahora mostrar los controles interactivos debajo
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
                        
                        if puede_editar:
                            if ronda == num_rondas:
                                # Final - seleccionar campeón
                                campeon_key = f'campeon_{categoria["id"]}'
                                campeon_actual = st.session_state.get(campeon_key)
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"👑 {jugador1}", key=f"{match_key}_j1", use_container_width=True):
                                        st.session_state[campeon_key] = jugador1
                                        st.rerun()
                                
                                with col2:
                                    if st.button(f"👑 {jugador2}", key=f"{match_key}_j2", use_container_width=True):
                                        st.session_state[campeon_key] = jugador2
                                        st.rerun()
                                
                                if campeon_actual:
                                    st.success(f"🏆 CAMPEÓN: {campeon_actual}")
                            else:
                                # Rondas anteriores
                                ganador_actual = bracket[ronda + 1][i // 2] if ronda < num_rondas else None
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button(f"✅ {jugador1}", key=f"{match_key}_j1", use_container_width=True):
                                        bracket[ronda + 1][i // 2] = jugador1
                                        st.rerun()
                                
                                with col2:
                                    if st.button(f"✅ {jugador2}", key=f"{match_key}_j2", use_container_width=True):
                                        bracket[ronda + 1][i // 2] = jugador2
                                        st.rerun()
                                
                                if ganador_actual:
                                    st.info(f"➡️ Ganador: {ganador_actual}")
                        else:
                            # Solo mostrar
                            st.write(f"- {jugador1}")
                            st.write(f"- {jugador2}")
                            
                            if ronda == num_rondas:
                                campeon_key = f'campeon_{categoria["id"]}'
                                campeon_actual = st.session_state.get(campeon_key)
                                if campeon_actual:
                                    st.success(f"🏆 CAMPEÓN: {campeon_actual}")
                            else:
                                if bracket[ronda + 1][i // 2]:
                                    ganador = bracket[ronda + 1][i // 2]
                                    st.info(f"➡️ Ganador: {ganador}")
                        
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