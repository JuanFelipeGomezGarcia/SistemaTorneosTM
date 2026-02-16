import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

def vista_cuadros_page():
    """Vista de cuadros tipo tabla Round Robin - Diseño Premium"""
    
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
    
    /* ── Tabla Round Robin ── */
    .rr-table-container {
        background: #ffffff;
        border-radius: 0 0 16px 16px;
        padding: 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.08);
        overflow-x: auto;
    }
    .rr-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
    }
    .rr-table th {
        background: #1e293b;
        color: #f1f5f9;
        padding: 14px 12px;
        font-weight: 600;
        font-size: 13px;
        text-align: center;
        border: 1px solid #334155;
        white-space: nowrap;
    }
    .rr-table th:first-child {
        text-align: left;
        padding-left: 16px;
        min-width: 160px;
    }
    .rr-table td {
        padding: 0;
        border: 1px solid #e2e8f0;
        text-align: center;
        font-size: 13px;
        height: 48px;
        vertical-align: middle;
    }
    .rr-table td:first-child {
        text-align: left;
        padding: 10px 16px;
        font-weight: 600;
        background: #f8fafc;
        color: #1e293b;
        white-space: nowrap;
    }
    .rr-table tr:hover td:first-child {
        background: #f1f5f9;
    }
    .cell-diagonal {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%) !important;
    }
    .cell-win {
        background: #dcfce7 !important;
        color: #166534 !important;
        font-weight: 700;
        font-size: 14px;
    }
    .cell-loss {
        background: #fee2e2 !important;
        color: #991b1b !important;
        font-weight: 600;
        font-size: 14px;
    }
    .cell-pending {
        background: #f8fafc !important;
        color: #94a3b8 !important;
    }
    .player-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        background: #667eea;
        color: white;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 8px;
    }
    
    /* ── Tabla de Posiciones ── */
    .ranking-section {
        margin-top: 0;
        padding: 24px;
        background: #ffffff;
        border-radius: 0 0 16px 16px;
        border-top: 2px solid #e2e8f0;
    }
    .ranking-section h4 {
        color: #1e293b;
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 700;
    }
    .ranking-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
    }
    .ranking-table th {
        background: #f1f5f9;
        color: #475569;
        padding: 10px 12px;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: 2px solid #e2e8f0;
        text-align: center;
    }
    .ranking-table th:nth-child(2) {
        text-align: left;
    }
    .ranking-table td {
        padding: 12px;
        border-bottom: 1px solid #f1f5f9;
        text-align: center;
        font-size: 14px;
        color: #334155;
    }
    .ranking-table td:nth-child(2) {
        text-align: left;
        font-weight: 600;
    }
    .ranking-table tr:hover td {
        background: #f8fafc;
    }
    .rank-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 13px;
    }
    .rank-1 { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: #fff; }
    .rank-2 { background: linear-gradient(135deg, #94a3b8, #64748b); color: #fff; }
    .rank-3 { background: linear-gradient(135deg, #d97706, #b45309); color: #fff; }
    .rank-other { background: #f1f5f9; color: #64748b; }
    .clasificado-tag {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #fff;
        font-size: 10px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
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
    personas_que_pasan = categoria.get('personas_que_pasan', 2)
    
    total_cuadros = len(cuadros)
    
    # ─── Mostrar cada cuadro ───
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
        
        jugadores = participantes_cuadro
        n = len(jugadores)
        
        # Calcular progreso
        total_partidos = n * (n - 1) // 2
        partidos_completados = 0
        for i, j1 in enumerate(jugadores):
            for j, j2 in enumerate(jugadores):
                if i < j:
                    for p in partidos_guardados:
                        if (p['cuadro_numero'] == cuadro_num and
                            p['jugador1'] == j1 and p['jugador2'] == j2 and p['resultado']):
                            partidos_completados += 1
                            break
        
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
        """, unsafe_allow_html=True)
        
        # ── Generar tabla Round Robin como HTML ──
        # Construir lookup de resultados
        resultado_map = {}
        for p in partidos_guardados:
            if p['cuadro_numero'] == cuadro_num:
                key = (p['jugador1'], p['jugador2'])
                resultado_map[key] = {'resultado': p['resultado'], 'ganador': p['ganador']}
        
        # Header de tabla
        table_html = "<div class='rr-table-container'><table class='rr-table'><thead><tr>"
        table_html += "<th>DEPORTISTA / EQUIPO</th>"
        for i in range(n):
            table_html += f"<th>{i+1}</th>"
        table_html += "</tr></thead><tbody>"
        
        # Filas
        for i, jugador_fila in enumerate(jugadores):
            table_html += "<tr>"
            table_html += f"<td><span class='player-num'>{i+1}</span>{jugador_fila}</td>"
            
            for j, jugador_col in enumerate(jugadores):
                if i == j:
                    table_html += "<td class='cell-diagonal'></td>"
                    continue
                
                # Buscar resultado
                res_data = resultado_map.get((jugador_fila, jugador_col))
                
                if not puede_editar:
                    # Solo lectura
                    if res_data and res_data['resultado']:
                        if res_data['ganador'] == jugador_fila:
                            table_html += f"<td class='cell-win'>{res_data['resultado']}</td>"
                        else:
                            table_html += f"<td class='cell-loss'>{res_data['resultado']}</td>"
                    else:
                        table_html += "<td class='cell-pending'>—</td>"
                else:
                    # Modo admin: cerrar HTML, usar selectbox de Streamlit, luego reabrir
                    table_html += "<td class='cell-pending'>⏎</td>"
            
            table_html += "</tr>"
        
        table_html += "</tbody></table></div>"
        
        # Renderizar tabla (solo lectura) o usar sistema mixto
        if not puede_editar:
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            # Para admin: usar columnas de Streamlit para editar resultados
            st.markdown(table_html.replace("⏎", "↓"), unsafe_allow_html=True)
            
            st.markdown(f"##### ✏️ Editar resultados — Cuadro {cuadro_num}")
            
            # Mostrar solo la mitad superior (sin duplicados)
            for i, jugador_fila in enumerate(jugadores):
                for j, jugador_col in enumerate(jugadores):
                    if i >= j:
                        continue
                    
                    res_data = resultado_map.get((jugador_fila, jugador_col))
                    resultado_actual = res_data['resultado'] if res_data else ""
                    
                    col1, col2, col3 = st.columns([3, 2, 3])
                    with col1:
                        st.markdown(f"**{jugador_fila}**")
                    with col2:
                        key = f"rr_{cuadro_num}_{i}_{j}"
                        opciones = ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"]
                        idx_actual = opciones.index(resultado_actual) if resultado_actual in opciones else 0
                        nuevo_resultado = st.selectbox(
                            "vs",
                            opciones,
                            index=idx_actual,
                            key=key,
                            label_visibility="collapsed"
                        )
                        
                        if nuevo_resultado != resultado_actual:
                            if nuevo_resultado == "":
                                if resultado_actual:
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
                    with col3:
                        st.markdown(f"**{jugador_col}**")
        
        # ── Tabla de Posiciones ──
        victorias = {p: 0 for p in jugadores}
        derrotas = {p: 0 for p in jugadores}
        sets_ganados = {p: 0 for p in jugadores}
        sets_perdidos = {p: 0 for p in jugadores}
        partidos_jugados = {p: 0 for p in jugadores}
        
        for key, data in resultado_map.items():
            j1, j2 = key
            if data['resultado'] and j1 in victorias and j2 in victorias:
                partidos_jugados[j1] += 1
                partidos_jugados[j2] += 1
                try:
                    s1, s2 = map(int, data['resultado'].split('-'))
                    sets_ganados[j1] += s1
                    sets_perdidos[j1] += s2
                    sets_ganados[j2] += s2
                    sets_perdidos[j2] += s1
                except:
                    pass
                if data['ganador'] == j1:
                    victorias[j1] += 1
                    derrotas[j2] += 1
                elif data['ganador'] == j2:
                    victorias[j2] += 1
                    derrotas[j1] += 1
        
        # Ordenar por victorias, luego por diferencia de sets
        ranking = sorted(jugadores, key=lambda x: (victorias[x], sets_ganados[x] - sets_perdidos[x]), reverse=True)
        
        ranking_html = """
        <div class='ranking-section'>
            <h4>📊 Tabla de Posiciones</h4>
            <table class='ranking-table'>
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Jugador</th>
                        <th>PJ</th>
                        <th>V</th>
                        <th>D</th>
                        <th>SG</th>
                        <th>SP</th>
                        <th>Dif</th>
                        <th></th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for pos, jugador in enumerate(ranking, 1):
            rank_class = f"rank-{pos}" if pos <= 3 else "rank-other"
            dif = sets_ganados[jugador] - sets_perdidos[jugador]
            dif_str = f"+{dif}" if dif > 0 else str(dif)
            clasif_tag = f"<span class='clasificado-tag'>Clasifica</span>" if pos <= personas_que_pasan else ""
            
            ranking_html += f"""
                <tr>
                    <td><span class='rank-badge {rank_class}'>{pos}</span></td>
                    <td>{jugador} {clasif_tag}</td>
                    <td>{partidos_jugados[jugador]}</td>
                    <td><strong>{victorias[jugador]}</strong></td>
                    <td>{derrotas[jugador]}</td>
                    <td>{sets_ganados[jugador]}</td>
                    <td>{sets_perdidos[jugador]}</td>
                    <td><strong>{dif_str}</strong></td>
                    <td></td>
                </tr>
            """
        
        ranking_html += "</tbody></table></div></div>"  # Close ranking-section and cuadro-wrapper
        st.markdown(ranking_html, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # ─── Botones finales ───
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        subcol1, subcol2 = st.columns(2)
        with subcol1:
            if st.button("🔄 Actualizar", type="secondary", use_container_width=True):
                st.rerun()
        with subcol2:
            boton_text = "🏆 Ir a Llaves" if puede_editar else "🏆 Ver Llaves"
            if st.button(boton_text, type="primary", use_container_width=True):
                st.session_state.current_page = 'vista_llaves'
                st.rerun()

if __name__ == "__main__":
    vista_cuadros_page()