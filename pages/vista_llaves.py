import streamlit as st
from database.db_operations import DatabaseOperations
import math

def vista_llaves_page():
    """Vista de llaves eliminatorias con diseño profesional"""
    
    # CSS mejorado para bracket profesional
    st.markdown("""
    <style>
    .bracket-main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 30px;
        border-radius: 20px;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    .bracket-grid {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        gap: 40px;
        overflow-x: auto;
        padding: 20px;
    }
    .round-column {
        display: flex;
        flex-direction: column;
        align-items: center;
        min-width: 220px;
        position: relative;
    }
    .round-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 25px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 1.1em;
        margin-bottom: 25px;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
        text-align: center;
        min-width: 150px;
    }
    .match-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border: 2px solid #e8f4fd;
        transition: all 0.3s ease;
        position: relative;
        min-width: 200px;
    }
    .match-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    .final-card {
        background: linear-gradient(135deg, #fff9c4 0%, #ffecb3 100%);
        border: 3px solid #ffd700;
        box-shadow: 0 12px 40px rgba(255, 215, 0, 0.3);
    }
    .player-btn {
        width: 100%;
        padding: 15px 20px;
        margin: 8px 0;
        border: 2px solid #ddd;
        border-radius: 10px;
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #333;
        font-weight: bold;
        font-size: 1em;
        cursor: pointer;
        transition: all 0.3s ease;
        text-align: center;
    }
    .player-btn:hover {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
        border-color: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 123, 255, 0.3);
    }
    .vs-divider {
        text-align: center;
        font-weight: bold;
        color: #666;
        margin: 15px 0;
        font-size: 1.1em;
    }
    .final-divider {
        background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
        color: #333;
        padding: 8px 15px;
        border-radius: 20px;
        text-align: center;
        font-weight: bold;
        margin: 15px 0;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
    }
    .winner-badge {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        padding: 10px 20px;
        border-radius: 25px;
        text-align: center;
        margin-top: 15px;
        font-weight: bold;
        box-shadow: 0 6px 20px rgba(40, 167, 69, 0.3);
    }
    .champion-badge {
        background: linear-gradient(135deg, #ffd700 0%, #ffb300 100%);
        color: #333;
        padding: 12px 25px;
        border-radius: 30px;
        text-align: center;
        margin-top: 15px;
        font-weight: bold;
        font-size: 1.1em;
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4);
    }
    .bye-card {
        background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
        color: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        text-align: center;
        font-weight: bold;
        box-shadow: 0 6px 20px rgba(23, 162, 184, 0.3);
    }
    .connector-line {
        position: absolute;
        right: -20px;
        top: 50%;
        width: 40px;
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transform: translateY(-1px);
        z-index: 1;
    }
    .round-column:last-child .connector-line {
        display: none;
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
    
    # Mostrar bracket con diseño mejorado
    st.markdown('<div class="bracket-main">', unsafe_allow_html=True)
    st.markdown('<div class="bracket-grid">', unsafe_allow_html=True)
    
    # Crear columnas para cada ronda
    for ronda in range(1, num_rondas + 1):
        st.markdown('<div class="round-column">', unsafe_allow_html=True)
        
        # Título de la ronda
        if ronda == num_rondas:
            titulo = "🏆 FINAL"
        elif ronda == num_rondas - 1 and num_rondas > 2:
            titulo = "🥉 SEMIFINAL"
        else:
            titulo = f"Ronda {ronda}"
        
        st.markdown(f'<div class="round-header">{titulo}</div>', unsafe_allow_html=True)
        
        participantes_ronda = bracket[ronda]
        
        # Mostrar enfrentamientos
        for i in range(0, len(participantes_ronda), 2):
            if i + 1 < len(participantes_ronda):
                jugador1 = participantes_ronda[i]
                jugador2 = participantes_ronda[i + 1]
                
                if jugador1 and jugador2:
                    match_key = f"match_r{ronda}_m{i//2}"
                    
                    # Clase de la tarjeta
                    card_class = 'match-card final-card' if ronda == num_rondas else 'match-card'
                    st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
                    
                    if puede_editar:
                        if ronda == num_rondas:
                            # Final - seleccionar campeón
                            campeon_key = f'campeon_{categoria["id"]}'
                            campeon_actual = st.session_state.get(campeon_key)
                            
                            if st.button(jugador1, key=f"{match_key}_j1", help="Click para CAMPEÓN"):
                                st.session_state[campeon_key] = jugador1
                                st.rerun()
                            
                            st.markdown('<div class="final-divider">🏆 FINAL 🏆</div>', unsafe_allow_html=True)
                            
                            if st.button(jugador2, key=f"{match_key}_j2", help="Click para CAMPEÓN"):
                                st.session_state[campeon_key] = jugador2
                                st.rerun()
                            
                            if campeon_actual:
                                st.markdown(f'<div class="champion-badge">👑 CAMPEÓN: {campeon_actual}</div>', unsafe_allow_html=True)
                        else:
                            # Rondas anteriores
                            ganador_actual = bracket[ronda + 1][i // 2] if ronda < num_rondas else None
                            
                            if st.button(jugador1, key=f"{match_key}_j1", help="Click para ganar"):
                                bracket[ronda + 1][i // 2] = jugador1
                                st.rerun()
                            
                            st.markdown('<div class="vs-divider">⚔️ VS ⚔️</div>', unsafe_allow_html=True)
                            
                            if st.button(jugador2, key=f"{match_key}_j2", help="Click para ganar"):
                                bracket[ronda + 1][i // 2] = jugador2
                                st.rerun()
                            
                            if ganador_actual:
                                st.markdown(f'<div class="winner-badge">✅ Ganador: {ganador_actual}</div>', unsafe_allow_html=True)
                    else:
                        # Solo mostrar
                        st.markdown(f'<div style="text-align: center; font-weight: bold; margin: 10px 0;">{jugador1}</div>', unsafe_allow_html=True)
                        
                        if ronda == num_rondas:
                            st.markdown('<div class="final-divider">🏆 FINAL 🏆</div>', unsafe_allow_html=True)
                            campeon_key = f'campeon_{categoria["id"]}'
                            campeon_actual = st.session_state.get(campeon_key)
                            if campeon_actual:
                                st.markdown(f'<div class="champion-badge">👑 CAMPEÓN: {campeon_actual}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="vs-divider">⚔️ VS ⚔️</div>', unsafe_allow_html=True)
                            if bracket[ronda + 1][i // 2]:
                                ganador = bracket[ronda + 1][i // 2]
                                st.markdown(f'<div class="winner-badge">✅ Ganador: {ganador}</div>', unsafe_allow_html=True)
                        
                        st.markdown(f'<div style="text-align: center; font-weight: bold; margin: 10px 0;">{jugador2}</div>', unsafe_allow_html=True)
                    
                    # Línea conectora
                    if ronda < num_rondas:
                        st.markdown('<div class="connector-line"></div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                
                elif jugador1:  # Pase automático
                    st.markdown(f'<div class="bye-card">🎯 {jugador1}<br><small>Pase automático</small></div>', unsafe_allow_html=True)
                    if ronda < num_rondas:
                        bracket[ronda + 1][i // 2] = jugador1
        
        st.markdown('</div>', unsafe_allow_html=True)  # Cerrar round-column
    
    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar bracket-grid
    st.markdown('</div>', unsafe_allow_html=True)  # Cerrar bracket-main
    
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