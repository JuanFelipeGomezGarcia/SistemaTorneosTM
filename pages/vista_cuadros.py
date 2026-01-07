import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

def vista_cuadros_page():
    """Vista de cuadros tipo tabla Round Robin"""
    
    # CSS para tabla Round Robin
    st.markdown("""
    <style>
    .cuadro-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .cuadro-title {
        color: white;
        font-size: 24px;
        font-weight: bold;
        text-align: center;
        margin-bottom: 15px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .tabla-container {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        overflow-x: auto;
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
    
    # Permisos
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    # Header
    st.markdown(f"""
    <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 15px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>🎯 {categoria['nombre']}</h1>
        <p style='color: #f8f9fa; margin: 10px 0 0 0; font-size: 18px;'>📅 {torneo['nombre']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Info de permisos
    if es_admin:
        estado_text = "En Curso" if torneo['estado'] == 'en_curso' else "Finalizado"
        permiso_text = "Edición habilitada" if puede_editar else "Solo lectura"
        st.info(f"🔧 Estado: {estado_text} | {permiso_text}")
    
    # Botón volver
    if st.button("← Volver a Categorías", type="secondary"):
        st.session_state.current_page = 'vista_categorias'
        st.rerun()
    
    # Obtener datos
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    if len(participantes) < 2:
        st.warning("⚠️ Necesitas al menos 2 participantes")
        return
    
    # Generar cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    partidos_guardados = db.obtener_partidos(categoria['id'])
    
    # Mostrar cada cuadro
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
        
        # Container del cuadro
        st.markdown(f"""
        <div class='cuadro-container'>
            <div class='cuadro-title'>🏓 Cuadro {cuadro_num}</div>
            <div class='tabla-container'>
        """, unsafe_allow_html=True)
        
        jugadores = participantes_cuadro
        
        # Encabezado de la tabla
        cols = st.columns([2] + [1 for _ in jugadores])
        cols[0].markdown("<div style='background: #2c3e50; color: white; padding: 12px; text-align: center; font-weight: bold; border: 1px solid #34495e;'>DEPORTISTA / EQUIPO</div>", unsafe_allow_html=True)
        for i in range(len(jugadores)):
            cols[i+1].markdown(f"<div style='background: #2c3e50; color: white; padding: 12px; text-align: center; font-weight: bold; border: 1px solid #34495e;'>{i+1}</div>", unsafe_allow_html=True)
        
        # Filas de la tabla
        for i, jugador_fila in enumerate(jugadores):
            cols = st.columns([2] + [1 for _ in jugadores])
            
            # Nombre del jugador
            cols[0].markdown(f"<div style='background: #34495e; color: white; padding: 12px; font-weight: bold; border: 1px solid #bdc3c7; text-align: left; padding-left: 12px;'>{i+1}. {jugador_fila}</div>", unsafe_allow_html=True)
            
            for j, jugador_col in enumerate(jugadores):
                
                # Celda diagonal
                if i == j:
                    cols[j+1].markdown("<div style='background: linear-gradient(45deg, #2c3e50, #34495e); height: 45px; border: 1px solid #bdc3c7;'></div>", unsafe_allow_html=True)
                    continue
                
                # Buscar resultado guardado
                resultado_guardado = ""
                ganador_guardado = ""
                
                for partido in partidos_guardados:
                    if (
                        partido['cuadro_numero'] == cuadro_num and
                        partido['jugador1'] == jugador_fila and
                        partido['jugador2'] == jugador_col
                    ):
                        resultado_guardado = partido['resultado']
                        ganador_guardado = partido['ganador']
                        break
                
                # Celda editable o de solo lectura
                if puede_editar:
                    key = f"rr_{cuadro_num}{i}{j}{jugador_fila}{jugador_col}"
                    
                    with cols[j+1]:
                        nuevo_resultado = st.selectbox(
                            "Resultado",
                            ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"],
                            index=0 if not resultado_guardado else ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"].index(resultado_guardado) if resultado_guardado in ["", "3-0", "3-1", "3-2", "0-3", "1-3", "2-3"] else 0,
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
                                    st.error("Formato de resultado inválido")
                
                else:
                    # Solo mostrar resultado
                    if resultado_guardado:
                        if ganador_guardado == jugador_fila:
                            color = "#27ae60"
                        else:
                            color = "#e74c3c"
                        cols[j+1].markdown(f"<div style='background: {color}; color: white; padding: 12px; text-align: center; font-weight: bold; border: 1px solid #bdc3c7; height: 45px; display: flex; align-items: center; justify-content: center;'>{resultado_guardado}</div>", unsafe_allow_html=True)
                    else:
                        cols[j+1].markdown("<div style='background: #ecf0f1; padding: 12px; text-align: center; border: 1px solid #bdc3c7; height: 45px; display: flex; align-items: center; justify-content: center;'>-</div>", unsafe_allow_html=True)
        
        # Cerrar containers
        st.markdown("</div></div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Botones finales
    st.markdown("""
    <div style='background: #f8f9fa; padding: 20px; border-radius: 15px; margin-top: 30px; text-align: center;'>
        <h4 style='color: #2c3e50; margin-bottom: 20px;'>⚡ Acciones Rápidas</h4>
    </div>
    """, unsafe_allow_html=True)
    
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