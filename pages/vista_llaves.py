import streamlit as st
from database.db_operations import DatabaseOperations
from pages.bracket_component import render_bracket

def vista_llaves_page():
    """Vista de llaves eliminatorias con bracket dinámico premium"""
    
    # CSS Premium
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .stApp {
        background: transparent;
    }
    
    .llaves-hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 28px 32px;
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .llaves-hero::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 300px;
        height: 300px;
        background: rgba(255,255,255,0.05);
        border-radius: 50%;
    }
    .llaves-hero h1 {
        color: white;
        margin: 0;
        font-family: 'Inter', sans-serif;
        font-size: 28px;
        font-weight: 800;
    }
    .llaves-hero p {
        color: rgba(255,255,255,0.85);
        margin: 8px 0 0 0;
        font-size: 16px;
        font-family: 'Inter', sans-serif;
    }
    
    /* Clasificados Grid */
    .clasificados-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
        gap: 12px;
        margin: 20px 0;
    }
    .clasificado-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 12px;
        padding: 16px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-family: 'Inter', sans-serif;
        transition: all 0.2s ease;
    }
    .clasificado-card:hover {
        background: rgba(99, 102, 241, 0.1);
        border-color: rgba(99, 102, 241, 0.3);
        transform: translateY(-2px);
    }
    .clasificado-seed {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 10px;
        font-weight: 800;
        font-size: 15px;
        flex-shrink: 0;
    }
    .seed-gold {
        background: linear-gradient(135deg, #fbbf24, #f59e0b);
        color: #fff;
        box-shadow: 0 4px 12px rgba(251,191,36,0.3);
    }
    .seed-silver {
        background: linear-gradient(135deg, #94a3b8, #64748b);
        color: #fff;
    }
    .clasificado-info {
        flex: 1;
        min-width: 0;
    }
    .clasificado-name {
        color: #e2e8f0;
        font-weight: 600;
        font-size: 14px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .clasificado-origin {
        color: #64748b;
        font-size: 11px;
        margin-top: 2px;
    }
    
    /* Champion celebration */
    .champion-celebration {
        background: linear-gradient(135deg, rgba(251,191,36,0.15), rgba(245,158,11,0.1));
        border: 2px solid rgba(251,191,36,0.4);
        border-radius: 24px;
        padding: 48px;
        text-align: center;
        margin: 40px auto;
        max-width: 520px;
        position: relative;
        overflow: hidden;
        font-family: 'Inter', sans-serif;
        animation: celebration-pulse 2s ease-in-out infinite alternate;
    }
    @keyframes celebration-pulse {
        0% { box-shadow: 0 0 30px rgba(251,191,36,0.2); }
        100% { box-shadow: 0 0 60px rgba(251,191,36,0.35), 0 0 100px rgba(251,191,36,0.1); }
    }
    .champion-celebration::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(
            from 0deg,
            transparent 0deg 340deg,
            rgba(251,191,36,0.1) 340deg 360deg
        );
        animation: confetti-spin 4s linear infinite;
    }
    @keyframes confetti-spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .champion-celebration .trophy {
        font-size: 64px;
        margin-bottom: 16px;
        position: relative;
        z-index: 1;
        animation: trophy-bounce 1s ease-in-out infinite alternate;
    }
    @keyframes trophy-bounce {
        from { transform: translateY(0); }
        to { transform: translateY(-8px); }
    }
    .champion-celebration h1 {
        color: #fbbf24;
        font-size: 20px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 3px;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    .champion-celebration h2 {
        color: #e2e8f0;
        font-size: 32px;
        font-weight: 800;
        margin: 16px 0 0 0;
        position: relative;
        z-index: 1;
    }
    
    /* Dark section for clasificados */
    .dark-section {
        background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 40%, #312e81 100%);
        border-radius: 16px;
        padding: 28px;
        margin: 24px 0;
    }
    .dark-section h3 {
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
        font-size: 18px;
        font-weight: 700;
        margin: 0 0 16px 0;
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
    
    # Header Premium
    st.markdown(f"""
    <div class='llaves-hero'>
        <h1>🏆 Llaves — {categoria['nombre']}</h1>
        <p>📅 {torneo['nombre']} &nbsp;•&nbsp; Fase Eliminatoria</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("← Volver a Cuadros", type="secondary"):
        st.session_state.current_page = 'vista_cuadros'
        st.rerun()
    
    # Obtener clasificados
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    from utils.tournament_utils import generar_cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    partidos = db.obtener_partidos(categoria['id'])
    personas_que_pasan = categoria.get('personas_que_pasan', 2)
    
    # Calcular clasificados con SEEDING correcto
    # Paso 1: Obtener ranking de cada cuadro con estadísticas
    cuadros_rankings = {}
    
    for cuadro_num in sorted(cuadros.keys()):
        participantes_cuadro = cuadros[cuadro_num]
        if len(participantes_cuadro) < 2:
            continue
            
        victorias = {p: 0 for p in participantes_cuadro}
        sets_ganados = {p: 0 for p in participantes_cuadro}
        sets_perdidos = {p: 0 for p in participantes_cuadro}
        
        for partido in partidos:
            if partido['cuadro_numero'] == cuadro_num and partido['ganador']:
                if partido['ganador'] in victorias:
                    victorias[partido['ganador']] += 1
                try:
                    s1, s2 = map(int, partido['resultado'].split('-'))
                    if partido['jugador1'] in sets_ganados:
                        sets_ganados[partido['jugador1']] += s1
                        sets_perdidos[partido['jugador1']] += s2
                    if partido['jugador2'] in sets_ganados:
                        sets_ganados[partido['jugador2']] += s2
                        sets_perdidos[partido['jugador2']] += s1
                except:
                    pass
        
        jugadores_ordenados = sorted(
            participantes_cuadro, 
            key=lambda x: (victorias.get(x, 0), sets_ganados.get(x, 0) - sets_perdidos.get(x, 0)), 
            reverse=True
        )
        
        cuadros_rankings[cuadro_num] = []
        for pos_idx in range(min(personas_que_pasan, len(jugadores_ordenados))):
            jugador = jugadores_ordenados[pos_idx]
            cuadros_rankings[cuadro_num].append({
                'nombre': jugador,
                'victorias': victorias.get(jugador, 0),
                'diff_sets': sets_ganados.get(jugador, 0) - sets_perdidos.get(jugador, 0),
                'cuadro': cuadro_num,
                'posicion': pos_idx + 1
            })
    
    # Paso 2: Agrupar por TIER y asignar seeds
    tiers = {}
    for cuadro_num, ranking in cuadros_rankings.items():
        for jugador_info in ranking:
            pos = jugador_info['posicion']
            if pos not in tiers:
                tiers[pos] = []
            tiers[pos].append(jugador_info)
    
    for pos in tiers:
        tiers[pos].sort(key=lambda x: (x['victorias'], x['diff_sets']), reverse=True)
    
    # Lista de seeds en orden: S1, S2, ..., SN (con info de cuadro)
    seeded = []
    for pos in sorted(tiers.keys()):
        seeded.extend(tiers[pos])
    
    seed_map = {}
    for idx, p in enumerate(seeded):
        seed_map[p['nombre']] = idx + 1
    
    n = len(seeded)
    if n < 2:
        st.warning("⚠️ Se necesitan al menos 2 clasificados. Completa los resultados en los cuadros.")
        return
    
    import math
    next_power = 2 ** math.ceil(math.log2(n)) if n > 1 else 2
    
    # Paso 3: Generar orden estándar de seeding
    def gen_seed_order(size):
        if size == 1: return [0]
        if size == 2: return [0, 1]
        half = size // 2
        top = gen_seed_order(half)
        result = []
        for i in top:
            result.append(i)
            result.append(size - 1 - i)
        return result
    
    order = gen_seed_order(next_power)
    
    # Colocar en bracket según seed order
    bracket = []
    for idx in order:
        if idx < n:
            bracket.append(seeded[idx])
        else:
            bracket.append(None)  # BYE
    
    # Paso 4: RESOLVER CONFLICTOS de mismo cuadro en Ronda 1
    # Si dos jugadores del MISMO cuadro se enfrentan en R1, intercambiar
    for m in range(0, len(bracket), 2):
        p1 = bracket[m]
        p2 = bracket[m + 1]
        
        if p1 is None or p2 is None:
            continue  # Match con BYE, no hay conflicto
        
        if p1['cuadro'] == p2['cuadro']:
            # ¡Conflicto! Buscar swap con jugador de otro match del mismo tier
            resolved = False
            for swap_m in range(0, len(bracket), 2):
                if swap_m == m:
                    continue
                # Intentar intercambiar p2 con cada jugador del otro match
                for swap_pos in [swap_m, swap_m + 1]:
                    swap_p = bracket[swap_pos]
                    if swap_p is None:
                        continue
                    # El swap es válido si:
                    # 1) swap_p es de diferente cuadro que p1 (resuelve nuestro conflicto)
                    # 2) p2 no crearía conflicto en el match destino
                    other_in_swap = bracket[swap_m + 1] if swap_pos == swap_m else bracket[swap_m]
                    swap_valid = (
                        swap_p['cuadro'] != p1['cuadro'] and
                        (other_in_swap is None or p2['cuadro'] != other_in_swap['cuadro'])
                    )
                    if swap_valid:
                        bracket[m + 1] = swap_p
                        bracket[swap_pos] = p2
                        resolved = True
                        break
                if resolved:
                    break
    
    # Construir lista final
    bracket_players = []
    for p in bracket:
        if p is None:
            bracket_players.append("BYE")
        else:
            bracket_players.append(p['nombre'])
    
    # Renderizar bracket (la lista ya tiene el orden correcto, NO reordenar)
    render_bracket(bracket_players, categoria['id'], puede_editar, torneo_id=torneo['id'], seed_map=seed_map)
    
    # Mostrar campeón si existe
    campeon_key = f'campeon_{categoria["id"]}'
    campeon_final = st.session_state.get(campeon_key)
    
    if campeon_final:
        st.balloons()
        st.markdown(
            f"""
            <div class='champion-celebration'>
                <div class='trophy'>🏆</div>
                <h1>CAMPEÓN</h1>
                <h2>{campeon_final}</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    vista_llaves_page()