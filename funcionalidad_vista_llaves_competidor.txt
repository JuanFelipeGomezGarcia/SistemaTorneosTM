import streamlit as st
import math
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

# ======================================================
# FUNCIÓN SVG PARA DIBUJAR LAS LLAVES (TIPO IMAGEN)
# ======================================================
def render_bracket_svg(bracket):
    round_width = 180
    match_height = 60
    text_offset = 15

    num_rondas = len(bracket)
    max_matches = len(bracket[1]) // 2

    svg_width = round_width * num_rondas + 100
    svg_height = max_matches * match_height * 2

    svg = [
        f'<svg width="{svg_width}" height="{svg_height}" '
        f'xmlns="http://www.w3.org/2000/svg">'
    ]

    # Títulos de rondas
    titles = ["16vos", "8vos", "4tos", "Semifinal", "FINAL"]
    for r in range(1, num_rondas + 1):
        title = titles[-r] if num_rondas <= len(titles) else f"Ronda {r}"
        svg.append(
            f'<text x="{(r-1)*round_width+40}" y="20" '
            f'font-size="16" font-weight="bold">{title}</text>'
        )

    for ronda, jugadores in bracket.items():
        x = (ronda - 1) * round_width + 40
        spacing = svg_height / (len(jugadores) + 1)

        for i in range(0, len(jugadores), 2):
            y1 = spacing * (i + 1)
            y2 = spacing * (i + 2)

            p1 = jugadores[i]
            p2 = jugadores[i + 1] if i + 1 < len(jugadores) else None

            # Texto jugadores
            if p1:
                svg.append(f'<text x="{x}" y="{y1}" font-size="14">{p1}</text>')
            if p2:
                svg.append(f'<text x="{x}" y="{y2}" font-size="14">{p2}</text>')

            # Líneas horizontales
            if p1:
                svg.append(f'<line x1="{x+90}" y1="{y1-5}" x2="{x+130}" y2="{y1-5}" stroke="black"/>')
            if p2:
                svg.append(f'<line x1="{x+90}" y1="{y2-5}" x2="{x+130}" y2="{y2-5}" stroke="black"/>')

            # Línea vertical
            if p1 and p2:
                svg.append(
                    f'<line x1="{x+130}" y1="{y1-5}" '
                    f'x2="{x+130}" y2="{y2-5}" stroke="black"/>'
                )

            # Línea hacia siguiente ronda
            if ronda < num_rondas:
                mid_y = (y1 + y2) / 2
                svg.append(
                    f'<line x1="{x+130}" y1="{mid_y-5}" '
                    f'x2="{x+round_width}" y2="{mid_y-5}" stroke="black"/>'
                )

    svg.append("</svg>")
    return "".join(svg)

# ======================================================
# VISTA PRINCIPAL
# ======================================================
def vista_llaves_page():

    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("❌ No hay categoría seleccionada")
        return

    if 'selected_tournament' not in st.session_state or not st.session_state.selected_tournament:
        st.error("❌ No hay torneo seleccionado")
        return

    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament

    st.title(f"🏆 Llaves eliminatorias – {categoria['nombre']}")
    st.caption(f"Torneo: {torneo['nombre']}")

    if st.button("← Volver a Cuadros"):
        st.session_state.current_page = 'vista_cuadros'
        st.rerun()

    db = DatabaseOperations()

    # ======================================================
    # CLASIFICADOS DESDE CUADROS
    # ======================================================
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]

    cuadros = generar_cuadros(
        participantes,
        categoria['cantidad_cuadros'],
        categoria['personas_por_cuadro']
    )

    partidos = db.obtener_partidos(categoria['id'])
    clasificados = []

    for cuadro_num, jugadores in cuadros.items():
        victorias = {j: 0 for j in jugadores}

        for p in partidos:
            if p['cuadro_numero'] == cuadro_num and p['ganador']:
                victorias[p['ganador']] += 1

        ordenados = sorted(jugadores, key=lambda j: victorias[j], reverse=True)

        if len(ordenados) >= 1:
            clasificados.append(ordenados[0])
        if len(ordenados) >= 2:
            clasificados.append(ordenados[1])

    if len(clasificados) < 2:
        st.warning("⚠️ No hay suficientes clasificados")
        return

    # ======================================================
    # ARMAR BRACKET
    # ======================================================
    num_rondas = math.ceil(math.log2(len(clasificados)))
    total_slots = 2 ** num_rondas

    while len(clasificados) < total_slots:
        clasificados.append(None)

    bracket = {1: clasificados}

    for r in range(2, num_rondas + 1):
        bracket[r] = [None] * (len(bracket[r - 1]) // 2)

    # ======================================================
    # MOSTRAR SVG
    # ======================================================
    st.markdown("---")
    st.subheader("🗂️ Bracket")

    svg = render_bracket_svg(bracket)

    st.markdown(
        f"""
        <div style="overflow-x:auto; border:1px solid #ccc; padding:20px">
            {svg}
        </div>
        """,
        unsafe_allow_html=True
    )
