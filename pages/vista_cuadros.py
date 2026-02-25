import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

def vista_cuadros_page():
    """Vista de cuadros tipo tabla Round Robin - Diseño Premium con edición inline"""
    
    # ─── CSS Global Premium ───
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .cuadro-wrapper {
        font-family: 'Inter', sans-serif;
        margin-bottom: 40px;
    }
    .cuadro-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px 28px;
        border-radius: 16px 16px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .cuadro-header-left h3 {
        color: white;
        margin: 0;
        font-size: 20px;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .cuadro-header-left span {
        color: rgba(255,255,255,0.8);
        font-size: 13px;
    }
    .progress-badge {
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(8px);
        padding: 8px 16px;
        border-radius: 20px;
        color: white;
        font-size: 13px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .progress-bar-bg {
        width: 80px;
        height: 6px;
        background: rgba(255,255,255,0.3);
        border-radius: 3px;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        background: #4ade80;
        border-radius: 3px;
        transition: width 0.4s ease;
    }
    
    /* ── Estilos para celdas de la tabla ── */
    .rr-header-cell {
        background: #1e293b;
        color: #f1f5f9;
        padding: 12px 8px;
        text-align: center;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid #334155;
        border-radius: 0;
        font-family: 'Inter', sans-serif;
    }
    .rr-header-cell-first {
        background: #1e293b;
        color: #f1f5f9;
        padding: 12px 8px;
        text-align: center;
        font-weight: 600;
        font-size: 12px;
        border: 1px solid #334155;
        font-family: 'Inter', sans-serif;
    }
    .rr-name-cell {
        background: #f8fafc;
        color: #1e293b;
        padding: 10px 12px;
        font-weight: 600;
        font-size: 13px;
        border: 1px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .player-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        background: #667eea;
        color: white;
        border-radius: 5px;
        font-size: 10px;
        font-weight: 700;
        margin-right: 6px;
    }
    .cell-diagonal {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        height: 45px;
        border: 1px solid #334155;
    }
    .cell-win {
        background: #dcfce7;
        color: #166534;
        font-weight: 700;
        font-size: 14px;
        padding: 10px 6px;
        text-align: center;
        border: 1px solid #bbf7d0;
        font-family: 'Inter', sans-serif;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .cell-loss {
        background: #fee2e2;
        color: #991b1b;
        font-weight: 600;
        font-size: 14px;
        padding: 10px 6px;
        text-align: center;
        border: 1px solid #fecaca;
        font-family: 'Inter', sans-serif;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .cell-pending {
        background: #f8fafc;
        color: #94a3b8;
        padding: 10px 6px;
        text-align: center;
        border: 1px solid #e2e8f0;
        font-family: 'Inter', sans-serif;
        height: 45px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* ── Header Principal ── */
    .page-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .page-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
    }
    .page-hero h1 {
        color: white;
        margin: 0;
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 800;
    }
    .page-hero p {
        color: rgba(255,255,255,0.85);
        margin: 8px 0 0 0;
        font-size: 16px;
        font-family: 'Inter', sans-serif;
    }
    
    /* Cerrar cuadro wrapper con borde inferior */
    .cuadro-bottom {
        background: #ffffff;
        border-radius: 0 0 16px 16px;
        padding: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        border-top: 1px solid #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ─── Validaciones ───
    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("❌ No hay categoría seleccionada")
        return
    
    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()
    
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    # ─── Header Principal ───
    st.markdown(f"""
    <div class='page-hero'>
        <h1>🎯 {categoria['nombre']}</h1>
        <p>📅 {torneo['nombre']} &nbsp;•&nbsp; Fase de Grupos (Round Robin)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Info de permisos
    if es_admin:
        estado_text = "En Curso ✅" if torneo['estado'] == 'en_curso' else "Finalizado 🔴"
        permiso_text = "Edición habilitada ✏️" if puede_editar else "Solo lectura 👁️"
        st.info(f"🔧 Estado: {estado_text} | {permiso_text}")
    
    # Botón volver
    if st.button("← Volver a Categorías", type="secondary"):
        st.session_state.current_page = 'vista_categorias'
        st.rerun()
    
    # ─── Obtener datos ───
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    if len(participantes) < 2:
        st.warning("⚠️ Necesitas al menos 2 participantes")
        return
    
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    partidos_guardados = db.obtener_partidos(categoria['id'])
    
    total_cuadros = len(cuadros)
    
    # Pre-calcular todos los resultado_map de una vez para evitar loops repetidos
    resultado_maps = {}
    for cuadro_num in cuadros.keys():
        resultado_maps[cuadro_num] = {}
        for p in partidos_guardados:
            if p['cuadro_numero'] == cuadro_num:
                key = (p['jugador1'], p['jugador2'])
                resultado_maps[cuadro_num][key] = {'resultado': p['resultado'], 'ganador': p['ganador']}
    
    # ─── Mostrar cada cuadro ───
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
        
        jugadores = participantes_cuadro
        n = len(jugadores)
        
        # Usar el resultado_map pre-calculado
        resultado_map = resultado_maps[cuadro_num]
        
        # Calcular progreso
        total_partidos = n * (n - 1) // 2
        partidos_completados = 0
        for i in range(n):
            for j in range(i + 1, n):
                res = resultado_map.get((jugadores[i], jugadores[j]))
                if res and res['resultado']:
                    partidos_completados += 1
        
        progreso_pct = (partidos_completados / total_partidos * 100) if total_partidos > 0 else 0
        
        # ── Header del cuadro ──
        st.markdown(f"""
        <div class='cuadro-wrapper'>
        <div class='cuadro-header'>
            <div class='cuadro-header-left'>
                <h3>🏓 Cuadro {cuadro_num}</h3>
                <span>Grupo {cuadro_num} de {total_cuadros} &nbsp;•&nbsp; {n} participantes</span>
            </div>
            <div class='progress-badge'>
                {partidos_completados}/{total_partidos} partidos
                <div class='progress-bar-bg'>
                    <div class='progress-bar-fill' style='width: {progreso_pct}%'></div>
                </div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)
        
        # ── Tabla Round Robin con st.columns (edición inline) ──
        
        # Encabezado de la tabla
        cols = st.columns([2] + [1 for _ in jugadores])
        cols[0].markdown("<div class='rr-header-cell-first'>DEPORTISTA / EQUIPO</div>", unsafe_allow_html=True)
        for i in range(n):
            cols[i+1].markdown(f"<div class='rr-header-cell'>{i+1}</div>", unsafe_allow_html=True)
        
        # Filas de la tabla
        for i, jugador_fila in enumerate(jugadores):
            cols = st.columns([2] + [1 for _ in jugadores])
            
            # Nombre del jugador
            cols[0].markdown(f"<div class='rr-name-cell'><span class='player-num'>{i+1}</span>{jugador_fila}</div>", unsafe_allow_html=True)
            
            for j, jugador_col in enumerate(jugadores):
                
                # Celda diagonal
                if i == j:
                    cols[j+1].markdown("<div class='cell-diagonal'></div>", unsafe_allow_html=True)
                    continue
                
                # Buscar resultado guardado (buscar en ambas direcciones)
                res_data = resultado_map.get((jugador_fila, jugador_col))
                resultado_guardado = ""
                ganador_guardado = ""
                
                if res_data and res_data['resultado']:
                    resultado_guardado = res_data['resultado']
                    ganador_guardado = res_data['ganador']
                
                # Celda editable o de solo lectura
                if puede_editar:
                    # Solo permitir editar la mitad superior (i < j)
                    if i < j:
                        key = f"rr_{cuadro_num}_{i}_{j}"
                        opciones = ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"]
                        idx_actual = opciones.index(resultado_guardado) if resultado_guardado in opciones else 0
                        
                        with cols[j+1]:
                            nuevo_resultado = st.selectbox(
                                f"{jugador_fila} vs {jugador_col}",
                                opciones,
                                index=idx_actual,
                                key=key,
                                label_visibility="collapsed"
                            )
                            
                            # Guardar si cambió
                            if nuevo_resultado != resultado_guardado:
                                if nuevo_resultado == "":
                                    if resultado_guardado:
                                        db.guardar_resultado_partido(categoria['id'], cuadro_num, jugador_fila, jugador_col, "", "")
                                        st.rerun()
                                else:
                                    try:
                                        partes = nuevo_resultado.split("-")
                                        num1, num2 = int(partes[0]), int(partes[1])
                                        ganador = jugador_fila if num1 > num2 else jugador_col
                                        db.guardar_resultado_partido(categoria['id'], cuadro_num, jugador_fila, jugador_col, nuevo_resultado, ganador)
                                        st.rerun()
                                    except (ValueError, IndexError):
                                        st.error("Formato inválido")
                    else:
                        # Mitad inferior: mostrar resultado espejo (solo lectura)
                        res_espejo = resultado_map.get((jugador_col, jugador_fila))
                        if res_espejo and res_espejo['resultado']:
                            # Invertir el resultado para mostrarlo desde la perspectiva de la fila
                            resultado_original = res_espejo['resultado']
                            try:
                                partes = resultado_original.split("-")
                                resultado_invertido = f"{partes[1]}-{partes[0]}"
                            except:
                                resultado_invertido = resultado_original
                            
                            if res_espejo['ganador'] == jugador_fila:
                                cols[j+1].markdown(f"<div class='cell-win'>{resultado_invertido}</div>", unsafe_allow_html=True)
                            else:
                                cols[j+1].markdown(f"<div class='cell-loss'>{resultado_invertido}</div>", unsafe_allow_html=True)
                        else:
                            cols[j+1].markdown("<div class='cell-pending'>—</div>", unsafe_allow_html=True)
                
                else:
                    # Solo lectura (competidor)
                    if resultado_guardado:
                        if ganador_guardado == jugador_fila:
                            cols[j+1].markdown(f"<div class='cell-win'>{resultado_guardado}</div>", unsafe_allow_html=True)
                        else:
                            cols[j+1].markdown(f"<div class='cell-loss'>{resultado_guardado}</div>", unsafe_allow_html=True)
                    else:
                        # Buscar resultado espejo
                        res_espejo = resultado_map.get((jugador_col, jugador_fila))
                        if res_espejo and res_espejo['resultado']:
                            try:
                                partes = res_espejo['resultado'].split("-")
                                resultado_invertido = f"{partes[1]}-{partes[0]}"
                            except:
                                resultado_invertido = res_espejo['resultado']
                            
                            if res_espejo['ganador'] == jugador_fila:
                                cols[j+1].markdown(f"<div class='cell-win'>{resultado_invertido}</div>", unsafe_allow_html=True)
                            else:
                                cols[j+1].markdown(f"<div class='cell-loss'>{resultado_invertido}</div>", unsafe_allow_html=True)
                        else:
                            cols[j+1].markdown("<div class='cell-pending'>—</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # ─── Botón final ───
    st.markdown("---")
    
    # Validar si todos los cuadros están completos (reusar los resultado_maps ya calculados)
    todos_completos = True
    total_partidos_global = 0
    partidos_completados_global = 0
    
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
        
        jugadores = participantes_cuadro
        n = len(jugadores)
        resultado_map = resultado_maps[cuadro_num]
        
        # Calcular progreso
        total_partidos = n * (n - 1) // 2
        partidos_completados = 0
        for i in range(n):
            for j in range(i + 1, n):
                res = resultado_map.get((jugadores[i], jugadores[j]))
                if res and res['resultado']:
                    partidos_completados += 1
        
        total_partidos_global += total_partidos
        partidos_completados_global += partidos_completados
    
    if partidos_completados_global < total_partidos_global:
        todos_completos = False
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if todos_completos:
            boton_text = "🏆 Ir a Llaves" if puede_editar else "🏆 Ver Llaves"
            if st.button(boton_text, type="primary", use_container_width=True):
                st.session_state.current_page = 'vista_llaves'
                st.rerun()
        else:
            st.button(
                f"🏆 Ir a Llaves ({partidos_completados_global}/{total_partidos_global} partidos)",
                type="primary",
                use_container_width=True,
                disabled=True,
                help="Completa todos los resultados de los cuadros para habilitar las llaves"
            )
            # Mensaje diferente para admin y competidor
            if es_admin:
                st.warning(f"⚠️ Completa todos los resultados de los cuadros para acceder a las llaves. Progreso: {partidos_completados_global}/{total_partidos_global} partidos")
            else:
                st.info(f"ℹ️ Las llaves estarán disponibles cuando se completen todos los resultados. Progreso: {partidos_completados_global}/{total_partidos_global} partidos")

if __name__ == "__main__":
    vista_cuadros_page()