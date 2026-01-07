import streamlit as st
from database.db_operations import DatabaseOperations
# from database.db_local import LocalDatabaseOperations
import math

def vista_llaves_page():
    """Página para mostrar las llaves eliminatorias tipo bracket"""
    
    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("No hay categoría seleccionada")
        return
    
    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()
    
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    st.title(f"🏆 Bracket - {categoria['nombre']}")
    st.write(f"Torneo: {torneo['nombre']}")
    
    if st.button("← Volver a Cuadros"):
        st.session_state.current_page = 'vista_cuadros'
        st.rerun()
    
    st.markdown("---")
    
    # Obtener ganadores de cuadros
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    from utils.tournament_utils import generar_cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    
    partidos = db.obtener_partidos(categoria['id'])
    ganadores_por_cuadro = {}
    cuadros_con_resultados = set()
    
    for partido in partidos:
        cuadro = partido['cuadro_numero']
        if partido['ganador']:
            cuadros_con_resultados.add(cuadro)
            if cuadro not in ganadores_por_cuadro:
                ganadores_por_cuadro[cuadro] = []
            ganadores_por_cuadro[cuadro].append(partido['ganador'])
    
    cuadros_necesarios = set(c for c in cuadros.keys() if len(cuadros[c]) >= 2)
    
    if not cuadros_necesarios.issubset(cuadros_con_resultados):
        st.warning("⚠️ Completa todos los cuadros antes de generar las llaves.")
        return
    
    # Obtener ganadores únicos por cuadro
    ganadores_cuadros = []
    for cuadro in sorted(ganadores_por_cuadro.keys()):
        ganadores = ganadores_por_cuadro[cuadro]
        conteo_victorias = {}
        for ganador in ganadores:
            conteo_victorias[ganador] = conteo_victorias.get(ganador, 0) + 1
        
        if conteo_victorias:
            ganador_cuadro = max(conteo_victorias, key=conteo_victorias.get)
            ganadores_cuadros.append(ganador_cuadro)
    
    if len(ganadores_cuadros) < 2:
        st.warning("Se necesitan al menos 2 ganadores de cuadros")
        return
    
    # Generar estructura de bracket
    num_participantes = len(ganadores_cuadros)
    num_rondas = math.ceil(math.log2(num_participantes)) if num_participantes > 1 else 1
    
    # Inicializar bracket
    if f'bracket_{categoria["id"]}' not in st.session_state:
        bracket = {}
        bracket[1] = ganadores_cuadros.copy()
        for ronda in range(2, num_rondas + 1):
            bracket[ronda] = [None] * (len(bracket[ronda - 1]) // 2)
        st.session_state[f'bracket_{categoria["id"]}'] = bracket
    
    bracket = st.session_state[f'bracket_{categoria["id"]}']
    
    # CSS para el bracket
    st.markdown("""
    <style>
    .bracket-container {
        display: flex;
        justify-content: center;
        align-items: flex-start;
        gap: 40px;
        margin: 20px 0;
    }
    .bracket-round {
        display: flex;
        flex-direction: column;
        gap: 20px;
        min-width: 200px;
    }
    .bracket-match {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 2px solid #e0e0e0;
    }
    .bracket-player {
        background: white;
        padding: 8px 12px;
        margin: 3px 0;
        border-radius: 5px;
        border-left: 4px solid #4CAF50;
        font-weight: bold;
        color: #333;
    }
    .bracket-player.winner {
        border-left-color: #FFD700;
        background: #FFF9C4;
    }
    .bracket-vs {
        text-align: center;
        color: white;
        font-weight: bold;
        margin: 5px 0;
    }
    .bracket-title {
        text-align: center;
        font-weight: bold;
        margin-bottom: 15px;
        color: #333;
        background: #f0f0f0;
        padding: 8px;
        border-radius: 5px;
    }
    .champion-box {
        background: linear-gradient(135deg, #FFD700 0%, #FFA000 100%);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(255,215,0,0.3);
        border: 3px solid #FFD700;
    }
    .champion-text {
        color: #333;
        font-size: 24px;
        font-weight: bold;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar bracket horizontal
    st.markdown('<div class="bracket-container">', unsafe_allow_html=True)
    
    cols = st.columns(num_rondas)
    
    for ronda_idx in range(num_rondas):
        ronda = ronda_idx + 1
        with cols[ronda_idx]:
            if ronda == num_rondas:
                st.markdown('<div class="bracket-title">🏆 FINAL</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bracket-title">Ronda {ronda}</div>', unsafe_allow_html=True)
            
            participantes_ronda = bracket[ronda]
            
            if ronda == 1:
                # Primera ronda
                for i in range(0, len(participantes_ronda), 2):
                    if i + 1 < len(participantes_ronda):
                        jugador1 = participantes_ronda[i]
                        jugador2 = participantes_ronda[i + 1]
                        
                        st.markdown('<div class="bracket-match">', unsafe_allow_html=True)
                        
                        if puede_editar:
                            ganador1_key = f"bracket_r{ronda}_{i}"
                            ganador2_key = f"bracket_r{ronda}_{i+1}"
                            
                            ganador1 = st.checkbox(
                                jugador1, 
                                key=ganador1_key,
                                value=st.session_state.get(ganador1_key, False)
                            )
                            
                            st.markdown('<div class="bracket-vs">VS</div>', unsafe_allow_html=True)
                            
                            ganador2 = st.checkbox(
                                jugador2, 
                                key=ganador2_key,
                                value=st.session_state.get(ganador2_key, False)
                            )
                            
                            # Lógica de selección exclusiva
                            if ganador1 and st.session_state.get(ganador2_key, False):
                                st.session_state[ganador2_key] = False
                            elif ganador2 and st.session_state.get(ganador1_key, False):
                                st.session_state[ganador1_key] = False
                            
                            # Actualizar siguiente ronda
                            if ganador1:
                                if len(bracket) > ronda:
                                    bracket[ronda + 1][i // 2] = jugador1
                            elif ganador2:
                                if len(bracket) > ronda:
                                    bracket[ronda + 1][i // 2] = jugador2
                            else:
                                if len(bracket) > ronda:
                                    bracket[ronda + 1][i // 2] = None
                        else:
                            # Solo mostrar
                            player1_class = "bracket-player winner" if bracket.get(ronda + 1, [None] * 10)[i // 2] == jugador1 else "bracket-player"
                            player2_class = "bracket-player winner" if bracket.get(ronda + 1, [None] * 10)[i // 2] == jugador2 else "bracket-player"
                            
                            st.markdown(f'<div class="{player1_class}">{jugador1}</div>', unsafe_allow_html=True)
                            st.markdown('<div class="bracket-vs">VS</div>', unsafe_allow_html=True)
                            st.markdown(f'<div class="{player2_class}">{jugador2}</div>', unsafe_allow_html=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                        st.markdown('<br>', unsafe_allow_html=True)
            
            else:
                # Rondas siguientes
                for i in range(0, len(participantes_ronda), 2):
                    if i + 1 < len(participantes_ronda):
                        jugador1 = participantes_ronda[i]
                        jugador2 = participantes_ronda[i + 1]
                        
                        if jugador1 and jugador2:
                            st.markdown('<div class="bracket-match">', unsafe_allow_html=True)
                            
                            if puede_editar:
                                ganador1_key = f"bracket_r{ronda}_{i}"
                                ganador2_key = f"bracket_r{ronda}_{i+1}"
                                
                                ganador1 = st.checkbox(
                                    jugador1, 
                                    key=ganador1_key,
                                    value=st.session_state.get(ganador1_key, False)
                                )
                                
                                st.markdown('<div class="bracket-vs">VS</div>', unsafe_allow_html=True)
                                
                                ganador2 = st.checkbox(
                                    jugador2, 
                                    key=ganador2_key,
                                    value=st.session_state.get(ganador2_key, False)
                                )
                                
                                # Lógica de selección exclusiva
                                if ganador1 and st.session_state.get(ganador2_key, False):
                                    st.session_state[ganador2_key] = False
                                elif ganador2 and st.session_state.get(ganador1_key, False):
                                    st.session_state[ganador1_key] = False
                                
                                # Actualizar siguiente ronda
                                if ronda < num_rondas:
                                    if ganador1:
                                        bracket[ronda + 1][i // 2] = jugador1
                                    elif ganador2:
                                        bracket[ronda + 1][i // 2] = jugador2
                                    else:
                                        bracket[ronda + 1][i // 2] = None
                            else:
                                # Solo mostrar
                                next_round_winner = bracket.get(ronda + 1, [None] * 10)[i // 2] if ronda < num_rondas else None
                                player1_class = "bracket-player winner" if next_round_winner == jugador1 else "bracket-player"
                                player2_class = "bracket-player winner" if next_round_winner == jugador2 else "bracket-player"
                                
                                st.markdown(f'<div class="{player1_class}">{jugador1}</div>', unsafe_allow_html=True)
                                st.markdown('<div class="bracket-vs">VS</div>', unsafe_allow_html=True)
                                st.markdown(f'<div class="{player2_class}">{jugador2}</div>', unsafe_allow_html=True)
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            st.markdown('<br>', unsafe_allow_html=True)
                        
                        elif jugador1:
                            st.markdown('<div class="bracket-match">', unsafe_allow_html=True)
                            st.markdown(f'<div class="bracket-player">{jugador1}</div>', unsafe_allow_html=True)
                            st.markdown('<div class="bracket-vs">Pasa automáticamente</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            if ronda < num_rondas:
                                bracket[ronda + 1][i // 2] = jugador1
                    
                    elif len(participantes_ronda) % 2 == 1 and i < len(participantes_ronda):
                        jugador = participantes_ronda[i]
                        if jugador:
                            st.markdown('<div class="bracket-match">', unsafe_allow_html=True)
                            st.markdown(f'<div class="bracket-player">{jugador}</div>', unsafe_allow_html=True)
                            st.markdown('<div class="bracket-vs">Pasa automáticamente</div>', unsafe_allow_html=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            if ronda < num_rondas:
                                bracket[ronda + 1][i // 2] = jugador
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Mostrar campeón
    if num_rondas > 0 and bracket[num_rondas] and bracket[num_rondas][0]:
        campeon = bracket[num_rondas][0]
        st.markdown('<br><br>', unsafe_allow_html=True)
        st.markdown('<div class="champion-box">', unsafe_allow_html=True)
        st.markdown(f'<p class="champion-text">🏆 CAMPEÓN: {campeon} 🏆</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Botón guardar
    if puede_editar:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("💾 Guardar Bracket", type="primary"):
            st.session_state[f'bracket_{categoria["id"]}'] = bracket
            st.success("Bracket guardado exitosamente!")
            st.rerun()