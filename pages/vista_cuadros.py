import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros


def calcular_ranking_cuadro(jugadores, resultado_map, partidos_cuadro, categoria_id=None, cuadro_num=None):
    """
    Calcula el ranking de un cuadro con desempates:
    1. Victorias (más victorias = mejor posición)
    2. Empate de 2: head-to-head (quién ganó el partido entre ellos)
    3. Empate de 3+: coeficiente de sets (sets ganados / sets perdidos)
    4. Si sigue empatado: marcado para selección manual
    
    Retorna lista de dicts:
      {'nombre', 'victorias', 'sets_ganados', 'sets_perdidos', 'coeficiente',
       'posicion', 'metodo_desempate', 'empate_sin_resolver'}
    """
    # Calcular estadísticas
    victorias = {p: 0 for p in jugadores}
    sets_ganados = {p: 0 for p in jugadores}
    sets_perdidos = {p: 0 for p in jugadores}
    
    for partido in partidos_cuadro:
        if partido.get('ganador'):
            ganador = partido['ganador']
            if ganador in victorias:
                victorias[ganador] += 1
            try:
                s1, s2 = map(int, partido['resultado'].split('-'))
                j1, j2 = partido['jugador1'], partido['jugador2']
                if j1 in sets_ganados:
                    sets_ganados[j1] += s1
                    sets_perdidos[j1] += s2
                if j2 in sets_ganados:
                    sets_ganados[j2] += s2
                    sets_perdidos[j2] += s1
            except:
                pass
    
    # Construir mapa head-to-head
    h2h = {}
    for partido in partidos_cuadro:
        if partido.get('ganador'):
            j1, j2, g = partido['jugador1'], partido['jugador2'], partido['ganador']
            h2h[(j1, j2)] = g
            h2h[(j2, j1)] = g
    
    # Agrupar por victorias
    from collections import defaultdict
    grupos_victorias = defaultdict(list)
    for p in jugadores:
        grupos_victorias[victorias[p]].append(p)
    
    # Obtener selecciones manuales guardadas en session_state
    manual_key = f"tiebreak_manual_{categoria_id}_{cuadro_num}" if categoria_id and cuadro_num else None
    selecciones_manuales = st.session_state.get(manual_key, {}) if manual_key else {}
    
    # Resolver desempates dentro de cada grupo
    ranking_final = []
    posicion = 1
    
    for vic_count in sorted(grupos_victorias.keys(), reverse=True):
        grupo = grupos_victorias[vic_count]
        
        if len(grupo) == 1:
            # Sin empate
            p = grupo[0]
            coef = (sets_ganados[p] / sets_perdidos[p]) if sets_perdidos[p] > 0 else (float('inf') if sets_ganados[p] > 0 else 0)
            ranking_final.append({
                'nombre': p,
                'victorias': victorias[p],
                'sets_ganados': sets_ganados[p],
                'sets_perdidos': sets_perdidos[p],
                'coeficiente': coef,
                'posicion': posicion,
                'metodo_desempate': '',
                'empate_sin_resolver': False
            })
            posicion += 1
        
        elif len(grupo) == 2:
            # Empate de 2: head-to-head
            p1, p2 = grupo[0], grupo[1]
            ganador_h2h = h2h.get((p1, p2))
            
            if ganador_h2h == p1:
                orden = [p1, p2]
            elif ganador_h2h == p2:
                orden = [p2, p1]
            else:
                # No hay partido entre ellos (no debería pasar en round robin completo)
                orden = grupo
            
            for p in orden:
                coef = (sets_ganados[p] / sets_perdidos[p]) if sets_perdidos[p] > 0 else (float('inf') if sets_ganados[p] > 0 else 0)
                ranking_final.append({
                    'nombre': p,
                    'victorias': victorias[p],
                    'sets_ganados': sets_ganados[p],
                    'sets_perdidos': sets_perdidos[p],
                    'coeficiente': coef,
                    'posicion': posicion,
                    'metodo_desempate': '🏓 Head-to-head',
                    'empate_sin_resolver': False
                })
                posicion += 1
        
        else:
            # Empate de 3+: coeficiente de sets
            coefs = {}
            for p in grupo:
                if sets_perdidos[p] > 0:
                    coefs[p] = sets_ganados[p] / sets_perdidos[p]
                elif sets_ganados[p] > 0:
                    coefs[p] = float('inf')
                else:
                    coefs[p] = 0.0
            
            # Ordenar por coeficiente descendente
            grupo_ordenado = sorted(grupo, key=lambda p: coefs[p], reverse=True)
            
            # Verificar si hay subgrupos aún empatados en coeficiente
            sub_grupos = []
            current_sub = [grupo_ordenado[0]]
            for k in range(1, len(grupo_ordenado)):
                if abs(coefs[grupo_ordenado[k]] - coefs[grupo_ordenado[k-1]]) < 1e-9:
                    current_sub.append(grupo_ordenado[k])
                else:
                    sub_grupos.append(current_sub)
                    current_sub = [grupo_ordenado[k]]
            sub_grupos.append(current_sub)
            
            for sub in sub_grupos:
                if len(sub) == 1:
                    p = sub[0]
                    ranking_final.append({
                        'nombre': p,
                        'victorias': victorias[p],
                        'sets_ganados': sets_ganados[p],
                        'sets_perdidos': sets_perdidos[p],
                        'coeficiente': coefs[p],
                        'posicion': posicion,
                        'metodo_desempate': '📊 Coeficiente de sets',
                        'empate_sin_resolver': False
                    })
                    posicion += 1
                else:
                    # Intentar resolver con selección manual
                    # Clave para este subgrupo empatado
                    sub_key = "_".join(sorted(sub))
                    manual_orden = selecciones_manuales.get(sub_key, [])
                    
                    if manual_orden and set(manual_orden) == set(sub):
                        # Hay selección manual válida
                        for p in manual_orden:
                            ranking_final.append({
                                'nombre': p,
                                'victorias': victorias[p],
                                'sets_ganados': sets_ganados[p],
                                'sets_perdidos': sets_perdidos[p],
                                'coeficiente': coefs[p],
                                'posicion': posicion,
                                'metodo_desempate': '👆 Selección manual',
                                'empate_sin_resolver': False
                            })
                            posicion += 1
                    else:
                        # Empate sin resolver
                        for p in sub:
                            ranking_final.append({
                                'nombre': p,
                                'victorias': victorias[p],
                                'sets_ganados': sets_ganados[p],
                                'sets_perdidos': sets_perdidos[p],
                                'coeficiente': coefs[p],
                                'posicion': posicion,
                                'metodo_desempate': '⚠️ Empate sin resolver',
                                'empate_sin_resolver': True
                            })
                        posicion += len(sub)
    
    return ranking_final


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
    
    /* ── Tabla de Posiciones ── */
    .standings-wrapper {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.06);
        margin-top: 8px;
        margin-bottom: 24px;
        border: 1px solid #e2e8f0;
    }
    .standings-title {
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .standings-table {
        width: 100%;
        border-collapse: collapse;
        font-family: 'Inter', sans-serif;
    }
    .standings-table th {
        background: #f1f5f9;
        color: #475569;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 10px 12px;
        text-align: center;
        border-bottom: 2px solid #e2e8f0;
    }
    .standings-table th:first-child,
    .standings-table td:first-child {
        text-align: center;
        width: 40px;
    }
    .standings-table th:nth-child(2),
    .standings-table td:nth-child(2) {
        text-align: left;
    }
    .standings-table td {
        padding: 10px 12px;
        text-align: center;
        font-size: 13px;
        color: #334155;
        border-bottom: 1px solid #f1f5f9;
    }
    .standings-table tr:hover {
        background: #f8fafc;
    }
    .pos-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 13px;
    }
    .pos-1 { background: linear-gradient(135deg, #fbbf24, #f59e0b); color: white; }
    .pos-2 { background: linear-gradient(135deg, #94a3b8, #64748b); color: white; }
    .pos-3 { background: linear-gradient(135deg, #cd7f32, #a0522d); color: white; }
    .pos-other { background: #e2e8f0; color: #475569; }
    .tiebreak-badge {
        display: inline-block;
        font-size: 11px;
        padding: 3px 8px;
        border-radius: 6px;
        font-weight: 600;
    }
    .tiebreak-h2h { background: #dbeafe; color: #1d4ed8; }
    .tiebreak-coef { background: #f3e8ff; color: #7c3aed; }
    .tiebreak-manual { background: #fef3c7; color: #b45309; }
    .tiebreak-unresolved { background: #fee2e2; color: #dc2626; }
    .empate-select-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 6px 16px;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        font-size: 13px;
        font-weight: 600;
        cursor: pointer;
        border: 2px solid #667eea;
        background: white;
        color: #667eea;
        transition: all 0.2s ease;
        margin: 4px;
    }
    .empate-select-btn:hover {
        background: #667eea;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(102,126,234,0.3);
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
    progreso_cuadros = {}  # Guardar progreso de cada cuadro
    total_partidos_global = 0
    partidos_completados_global = 0
    
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
            
        # Construir resultado_map
        resultado_maps[cuadro_num] = {}
        for p in partidos_guardados:
            if p['cuadro_numero'] == cuadro_num:
                key = (p['jugador1'], p['jugador2'])
                resultado_maps[cuadro_num][key] = {'resultado': p['resultado'], 'ganador': p['ganador']}
        
        # Calcular progreso de este cuadro
        jugadores = participantes_cuadro
        n = len(jugadores)
        total_partidos = n * (n - 1) // 2
        partidos_completados = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                res = resultado_maps[cuadro_num].get((jugadores[i], jugadores[j]))
                if res and res['resultado']:
                    partidos_completados += 1
        
        progreso_cuadros[cuadro_num] = {
            'total': total_partidos,
            'completados': partidos_completados,
            'porcentaje': (partidos_completados / total_partidos * 100) if total_partidos > 0 else 0
        }
        
        total_partidos_global += total_partidos
        partidos_completados_global += partidos_completados
    
    # ─── Mostrar cada cuadro ───
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
        
        jugadores = participantes_cuadro
        n = len(jugadores)
        
        # Usar el resultado_map pre-calculado
        resultado_map = resultado_maps[cuadro_num]
        
        # Usar el progreso pre-calculado
        progreso = progreso_cuadros[cuadro_num]
        partidos_completados = progreso['completados']
        total_partidos = progreso['total']
        progreso_pct = progreso['porcentaje']
        
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
        
        # ── Tabla de Posiciones con Desempate ──
        # Filtrar partidos de este cuadro
        partidos_cuadro = [p for p in partidos_guardados if p['cuadro_numero'] == cuadro_num]
        
        ranking = calcular_ranking_cuadro(
            jugadores, resultado_map, partidos_cuadro,
            categoria_id=categoria['id'], cuadro_num=cuadro_num
        )
        
        # Solo mostrar tabla de posiciones si hay al menos un partido completado
        if partidos_completados > 0:
            # Construir filas HTML
            filas_html = ""
            for r in ranking:
                # Badge de posición
                pos_class = f"pos-{r['posicion']}" if r['posicion'] <= 3 else "pos-other"
                pos_badge = f"<span class='pos-badge {pos_class}'>{r['posicion']}</span>"
                
                # Coeficiente formateado
                if r['coeficiente'] == float('inf'):
                    coef_str = "∞"
                else:
                    coef_str = f"{r['coeficiente']:.2f}"
                
                # Badge de método de desempate
                metodo_html = ""
                if r['metodo_desempate']:
                    if 'Head-to-head' in r['metodo_desempate']:
                        metodo_html = f"<span class='tiebreak-badge tiebreak-h2h'>{r['metodo_desempate']}</span>"
                    elif 'Coeficiente' in r['metodo_desempate']:
                        metodo_html = f"<span class='tiebreak-badge tiebreak-coef'>{r['metodo_desempate']}</span>"
                    elif 'manual' in r['metodo_desempate'].lower():
                        metodo_html = f"<span class='tiebreak-badge tiebreak-manual'>{r['metodo_desempate']}</span>"
                    elif 'sin resolver' in r['metodo_desempate']:
                        metodo_html = f"<span class='tiebreak-badge tiebreak-unresolved'>{r['metodo_desempate']}</span>"
                
                filas_html += f"""
                <tr>
                    <td>{pos_badge}</td>
                    <td style='font-weight:600;'>{r['nombre']}</td>
                    <td><strong>{r['victorias']}</strong></td>
                    <td style='color:#166534;'>{r['sets_ganados']}</td>
                    <td style='color:#991b1b;'>{r['sets_perdidos']}</td>
                    <td>{coef_str}</td>
                    <td>{metodo_html}</td>
                </tr>
                """
            
            st.markdown(f"""
            <div class='standings-wrapper'>
                <div class='standings-title'>📊 Posiciones — Cuadro {cuadro_num}</div>
                <table class='standings-table'>
                    <thead>
                        <tr>
                            <th>Pos</th>
                            <th>Jugador</th>
                            <th>Vic</th>
                            <th>S+</th>
                            <th>S-</th>
                            <th>Coef</th>
                            <th>Desempate</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filas_html}
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)
            
            # ── Selección manual para empates sin resolver ──
            empates_sin_resolver = [r for r in ranking if r['empate_sin_resolver']]
            if empates_sin_resolver and puede_editar:
                # Agrupar empates sin resolver por posición
                from collections import defaultdict
                grupos_empate = defaultdict(list)
                for r in empates_sin_resolver:
                    grupos_empate[r['posicion']].append(r['nombre'])
                
                for pos_empate, jugadores_empatados in grupos_empate.items():
                    st.warning(f"⚠️ **Empate sin resolver en posición {pos_empate}** del Cuadro {cuadro_num}: {', '.join(jugadores_empatados)}")
                    st.markdown("Haz clic en los jugadores en el **orden de clasificación** (primero = mejor posición):")
                    
                    manual_key = f"tiebreak_manual_{categoria['id']}_{cuadro_num}"
                    if manual_key not in st.session_state:
                        st.session_state[manual_key] = {}
                    
                    sub_key = "_".join(sorted(jugadores_empatados))
                    
                    # Estado temporal para la selección en curso
                    seleccion_key = f"seleccion_temp_{categoria['id']}_{cuadro_num}_{sub_key}"
                    if seleccion_key not in st.session_state:
                        st.session_state[seleccion_key] = []
                    
                    seleccion_actual = st.session_state[seleccion_key]
                    
                    # Mostrar jugadores ya seleccionados
                    if seleccion_actual:
                        orden_text = " → ".join([f"**{i+1}.** {p}" for i, p in enumerate(seleccion_actual)])
                        st.markdown(f"Orden actual: {orden_text}")
                    
                    # Mostrar botones para jugadores aún no seleccionados
                    pendientes = [p for p in jugadores_empatados if p not in seleccion_actual]
                    
                    if pendientes:
                        btn_cols = st.columns(len(pendientes))
                        for idx_btn, p in enumerate(pendientes):
                            with btn_cols[idx_btn]:
                                if st.button(f"👆 {p}", key=f"sel_{cuadro_num}_{sub_key}_{p}", use_container_width=True):
                                    st.session_state[seleccion_key].append(p)
                                    # Si ya seleccionamos todos, guardar
                                    if len(st.session_state[seleccion_key]) == len(jugadores_empatados):
                                        st.session_state[manual_key][sub_key] = st.session_state[seleccion_key].copy()
                                        del st.session_state[seleccion_key]
                                    st.rerun()
                    else:
                        st.success(f"✅ Orden definido para posición {pos_empate}")
                    
                    # Botón para resetear la selección
                    if seleccion_actual:
                        if st.button(f"🔄 Reiniciar selección", key=f"reset_{cuadro_num}_{sub_key}"):
                            st.session_state[seleccion_key] = []
                            if sub_key in st.session_state.get(manual_key, {}):
                                del st.session_state[manual_key][sub_key]
                            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
    
    # ─── Botón final ───
    st.markdown("---")
    
    # Usar los totales ya calculados
    todos_completos = (partidos_completados_global >= total_partidos_global)
    
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