import streamlit as st
import math
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

# ======================================================
# SVG DEL BRACKET
# ======================================================
def render_bracket_svg(bracket):
    round_w = 180
    svg_h = 600
    svg_w = round_w * len(bracket) + 120

    svg = [f'<svg width="{svg_w}" height="{svg_h}" xmlns="http://www.w3.org/2000/svg">']

    # Títulos
    titles = ["16vos", "8vos", "4tos", "Semifinal", "FINAL"]
    for i in range(1, len(bracket) + 1):
        title = titles[-i] if len(bracket) <= len(titles) else f"Ronda {i}"
        svg.append(
            f'<text x="{(i-1)*round_w+40}" y="25" font-size="16" font-weight="bold">{title}</text>'
        )

    for ronda, jugadores in bracket.items():
        x = (ronda - 1) * round_w + 40
        spacing = svg_h / (len(jugadores) + 1)

        for i in range(0, len(jugadores), 2):
            y1 = spacing * (i + 1)
            y2 = spacing * (i + 2)

            p1 = jugadores[i]
            p2 = jugadores[i + 1] if i + 1 < len(jugadores) else None

            if p1:
                svg.append(f'<text x="{x}" y="{y1}" font-size="14">{p1}</text>')
                svg.append(f'<line x1="{x+90}" y1="{y1-5}" x2="{x+130}" y2="{y1-5}" stroke="black"/>')

            if p2:
                svg.append(f'<text x="{x}" y="{y2}" font-size="14">{p2}</text>')
                svg.append(f'<line x1="{x+90}" y1="{y2-5}" x2="{x+130}" y2="{y2-5}" stroke="black"/>')

            if p1 and p2:
                svg.append(
                    f'<line x1="{x+130}" y1="{y1-5}" '
                    f'x2="{x+130}" y2="{y2-5}" stroke="black"/>'
                )

            if ronda < len(bracket):
                mid = (y1 + y2) / 2
                svg.append(
                    f'<line x1="{x+130}" y1="{mid-5}" '
                    f'x2="{x+round_w}" y2="{mid-5}" stroke="black"/>'
                )

    svg.append("</svg>")
    return "".join(svg)

# ======================================================
# VISTA PRINCIPAL
# ======================================================
def vista_llaves_page():

    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()

    st.title(f"🏆 Llaves – {categoria['nombre']}")
    st.caption(torneo['nombre'])

    # ======================================================
    # CLASIFICADOS
    # ======================================================
    participantes = [p['nombre'] for p in db.obtener_participantes(categoria['id'])]
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    partidos = db.obtener_partidos(categoria['id'])

    clasificados = []
    for c, jugadores in cuadros.items():
        victorias = {j: 0 for j in jugadores}
        for p in partidos:
            if p['cuadro_numero'] == c and p['ganador']:
                victorias[p['ganador']] += 1
        orden = sorted(jugadores, key=lambda j: victorias[j], reverse=True)
        clasificados.extend(orden[:2])

    if len(clasificados) < 2:
        st.warning("No hay suficientes clasificados")
        return

    # ======================================================
    # ARMAR BRACKET
    # ======================================================
    num_rondas = math.ceil(math.log2(len(clasificados)))
    total = 2 ** num_rondas

    while len(clasificados) < total:
        clasificados.append(None)

    key_bracket = f"bracket_{categoria['id']}"
    if key_bracket not in st.session_state:
        st.session_state[key_bracket] = {1: clasificados}
        for r in range(2, num_rondas + 1):
            st.session_state[key_bracket][r] = [None] * (len(st.session_state[key_bracket][r - 1]) // 2)

    bracket = st.session_state[key_bracket]

    # ======================================================
    # SELECCIÓN DE GANADORES
    # ======================================================
    st.subheader("🎯 Seleccionar ganadores")

    for ronda in range(1, num_rondas):
        st.markdown(f"### Ronda {ronda}")
        jugadores = bracket[ronda]

        for i in range(0, len(jugadores), 2):
            p1, p2 = jugadores[i], jugadores[i + 1]
            if not p1 or not p2:
                continue

            ganador = st.radio(
                f"{p1} vs {p2}",
                [p1, p2],
                key=f"r{ronda}_m{i}",
                horizontal=True
            )

            bracket[ronda + 1][i // 2] = ganador

    # ======================================================
    # MOSTRAR BRACKET
    # ======================================================
    st.markdown("---")
    st.subheader("🗂️ Llaves")

    st.markdown(
        f"""
        <div style="overflow-x:auto; border:1px solid #ccc; padding:20px">
            {render_bracket_svg(bracket)}
        </div>
        """,
        unsafe_allow_html=True
    )

    # ======================================================
    # CAMPEÓN
    # ======================================================
    final = bracket[num_rondas][0]
    if final:
        st.success(f"🏆 CAMPEÓN: {final}")
