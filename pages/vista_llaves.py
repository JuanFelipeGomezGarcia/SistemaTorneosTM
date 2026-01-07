import streamlit as st
from database.db_operations import DatabaseOperations
import math
from collections import Counter

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
    
    # Obtener participantes y generar cuadros
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    from utils.tournament_utils import generar_cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    
    # Obtener todos los partidos
    partidos = db.obtener_partidos(categoria['id'])
    
    # Calcular los 2 primeros de cada cuadro
    clasificados = []
    
    for cuadro_num in sorted(cuadros.keys()):
        participantes_cuadro = cuadros[cuadro_num]
        if len(participantes_cuadro) < 2:
            continue
            
        # Contar victorias por jugador en este cuadro
        victorias = Counter()
        
        for partido in partidos:
            if partido['cuadro_numero'] == cuadro_num and partido['ganador']:
                victorias[partido['ganador']] += 1
        
        # Ordenar por victorias (descendente)
        jugadores_ordenados = sorted(participantes_cuadro, key=lambda x: victorias[x], reverse=True)
        
        # Tomar los 2 primeros
        primero = jugadores_ordenados[0] if len(jugadores_ordenados) > 0 else None
        segundo = jugadores_ordenados[1] if len(jugadores_ordenados) > 1 else None
        
        if primero:
            clasificados.append(f"{primero} (C{cuadro_num}-1°)")
        if segundo:
            clasificados.append(f"{segundo} (C{cuadro_num}-2°)")
    
    if len(clasificados) < 2:
        st.warning("⚠️ Completa los cuadros para generar las llaves. Se necesitan al menos 2 clasificados.")
        return
    
    # CSS para el bracket
    st.markdown("""
    <style>
    .bracket-wrapper {
        display: flex;
        justify-content: center;
        overflow-x: auto;
        padding: 20px 0;
        min-height: 400px;
    }
    .bracket-container {
        display: flex;
        align-items: flex-start;
        gap: 60px;
        min-width: fit-content;
    }
    .bracket-round {
        display: flex;
        flex-direction: column;
        justify-content: space-around;
        min-width: 220px;
        min-height: 400px;
    }
    .bracket-match {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        border: 2px solid #e0e0e0;
        position: relative;
    }
    .bracket-player {
        background: white;
        padding: 10px 15px;
        margin: 4px 0;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        font-weight: bold;
        color: #333;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 14px;
    }
    .bracket-player:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    .bracket-player.winner {
        border-left-color: #FFD700;
        background: linear-gradient(135deg, #FFF9C4 0%, #FFECB3 100%);
        box-shadow: 0 4px 15px rgba(255,215,0,0.3);
    }
    .bracket-vs {
        text-align: center;
        color: white;
        font-weight: bold;
        margin: 8px 0;
        font-size: 16px;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    .bracket-title {
        text-align: center;
        font-weight: bold;
        margin-bottom: 20px;
        color: #333;
        background: linear-gradient(135deg, #f0f0f0 0%, #e0e0e0 100%);
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        font-size: 16px;
    }
    .champion-box {
        background: linear-gradient(135deg, #FFD700 0%, #FFA000 100%);
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        box-shadow: 0 12px 35px rgba(255,215,0,0.4);
        border: 4px solid #FFD700;
        margin: 30px auto;
        max-width: 400px;
    }
    .champion-text {
        color: #333;
        font-size: 28px;
        font-weight: bold;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .empty-slot {
        background: #f5f5f5;
        color: #999;
        border-left-color: #ccc;
        font-style: italic;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
    if f'bracket_{categoria["id"]}' not in st.session_state:
        bracket = {}
        bracket[1] = clasificados.copy()
        
        # Completar con slots vacíos si es necesario
        next_power_of_2 = 2 ** num_rondas
        while len(bracket[1]) < next_power_of_2:
            bracket[1].append(None)
        
        for ronda in range(2, num_rondas + 1):
            bracket[ronda] = [None] * (len(bracket[ronda - 1]) // 2)
        
        st.session_state[f'bracket_{categoria["id"]}'] = bracket
    
    bracket = st.session_state[f'bracket_{categoria["id"]}']
    
    # Mostrar bracket horizontal
    st.markdown('<div class="bracket-wrapper"><div class="bracket-container">', unsafe_allow_html=True)
    
    cols = st.columns(num_rondas)
    
    for ronda_idx in range(num_rondas):
        ronda = ronda_idx + 1
        with cols[ronda_idx]:
            # Título de la ronda
            if ronda == num_rondas:
                st.markdown('<div class="bracket-title">🏆 FINAL</div>', unsafe_allow_html=True)
            elif ronda == num_rondas - 1 and num_rondas > 2:
                st.markdown('<div class="bracket-title">🥉 SEMIFINAL</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bracket-title">Ronda {ronda}</div>', unsafe_allow_html=True)
            
            participantes_ronda = bracket[ronda]
            
            # Mostrar enfrentamientos
            for i in range(0, len(participantes_ronda), 2):
                if i + 1 < len(participantes_ronda):
                    jugador1 = participantes_ronda[i]
                    jugador2 = participantes_ronda[i + 1]
                    
                    st.markdown('<div class="bracket-match">', unsafe_allow_html=True)
                    
                    if puede_editar and jugador1 and jugador2:
                        # Modo edición
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
                        # Modo solo lectura
                        next_round_winner = bracket.get(ronda + 1, [None] * 10)[i // 2] if ronda < num_rondas else None
                        
                        if jugador1:
                            player1_class = "bracket-player winner" if next_round_winner == jugador1 else "bracket-player"
                            st.markdown(f'<div class="{player1_class}">{jugador1}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="bracket-player empty-slot">Por definir</div>', unsafe_allow_html=True)
                        
                        st.markdown('<div class="bracket-vs">VS</div>', unsafe_allow_html=True)
                        
                        if jugador2:
                            player2_class = "bracket-player winner" if next_round_winner == jugador2 else "bracket-player"
                            st.markdown(f'<div class="{player2_class}">{jugador2}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown('<div class="bracket-player empty-slot">Por definir</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown('<br>', unsafe_allow_html=True)
                
                elif len(participantes_ronda) % 2 == 1 and i < len(participantes_ronda):
                    # Jugador que pasa automáticamente
                    jugador = participantes_ronda[i]
                    if jugador:
                        st.markdown('<div class="bracket-match">', unsafe_allow_html=True)
                        st.markdown(f'<div class="bracket-player winner">{jugador}</div>', unsafe_allow_html=True)
                        st.markdown('<div class="bracket-vs">Pasa automáticamente</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        if ronda < num_rondas:
                            bracket[ronda + 1][i // 2] = jugador
    
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Mostrar campeón
    if num_rondas > 0 and bracket[num_rondas] and bracket[num_rondas][0]:
        campeon = bracket[num_rondas][0]
        st.markdown('<div class="champion-box">', unsafe_allow_html=True)
        st.markdown(f'<p class="champion-text">🏆 CAMPEÓN<br>{campeon.split(" (")[0]} 🏆</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Botón guardar
    if puede_editar:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("💾 Guardar Bracket", type="primary"):
            st.session_state[f'bracket_{categoria["id"]}'] = bracket
            st.success("Bracket guardado exitosamente!")
            st.rerun()