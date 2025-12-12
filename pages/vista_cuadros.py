import streamlit as st
from database.db_operations import DatabaseOperations
from utils.tournament_utils import generar_cuadros

def vista_cuadros_page():
    """Página para mostrar y editar los cuadros de una categoría"""
    
    # CSS personalizado para mejorar el diseño
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
    .round-robin-table {
        width: 100%;
        border-collapse: collapse;
        margin: 10px 0;
        font-size: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    .round-robin-table th {
        background: #2c3e50;
        color: white;
        padding: 12px 8px;
        text-align: center;
        font-weight: bold;
        border: 1px solid #34495e;
    }
    .round-robin-table td {
        padding: 8px;
        text-align: center;
        border: 1px solid #bdc3c7;
        vertical-align: middle;
        height: 45px;
    }
    .player-name-cell {
        background: #34495e;
        color: white;
        font-weight: bold;
        text-align: left;
        padding-left: 12px;
    }
    .diagonal-cell {
        background: linear-gradient(45deg, #2c3e50, #34495e);
    }
    .result-cell {
        background: #ecf0f1;
    }
    .result-win {
        background: #27ae60;
        color: white;
        font-weight: bold;
    }
    .result-loss {
        background: #e74c3c;
        color: white;
        font-weight: bold;
    }
    .info-badge {
        background: #3498db;
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 14px;
        display: inline-block;
        margin: 5px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Validar categoría seleccionada
    if 'selected_category' not in st.session_state or not st.session_state.selected_category:
        st.error("❌ No hay categoría seleccionada")
        return
    
    categoria = st.session_state.selected_category
    torneo = st.session_state.selected_tournament
    db = DatabaseOperations()
    
    # Verificar permisos de edición
    es_admin = st.session_state.user_type == "admin"
    puede_editar = es_admin and torneo['estado'] == 'en_curso'
    
    # Header elegante
    st.markdown(f"""
    <div style='text-align: center; padding: 20px; background: linear-gradient(90deg, #667eea, #764ba2); border-radius: 15px; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);'>🎯 {categoria['nombre']}</h1>
        <p style='color: #f8f9fa; margin: 10px 0 0 0; font-size: 18px;'>📅 {torneo['nombre']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Información de estado
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"<div class='info-badge'>👤 Tipo: {st.session_state.user_type.title()}</div>", unsafe_allow_html=True)
    with col2:
        estado_color = "#27ae60" if torneo['estado'] == 'en_curso' else "#e74c3c"
        st.markdown(f"<div class='info-badge' style='background: {estado_color};'>📊 Estado: {torneo['estado'].title()}</div>", unsafe_allow_html=True)
    with col3:
        permiso_text = "✏️ Edición" if puede_editar else "👁️ Solo Lectura"
        permiso_color = "#27ae60" if puede_editar else "#f39c12"
        st.markdown(f"<div class='info-badge' style='background: {permiso_color};'>{permiso_text}</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Botón volver elegante
    if st.button("← Volver a Categorías", type="secondary"):
        st.session_state.current_page = 'vista_categorias'
        st.rerun()
    
    # Obtener participantes
    participantes_data = db.obtener_participantes(categoria['id'])
    participantes = [p['nombre'] for p in participantes_data]
    
    if len(participantes) < 2:
        st.warning("⚠️ Esta categoría necesita al menos 2 participantes para generar cuadros")
        return
    
    # Generar cuadros
    cuadros = generar_cuadros(participantes, categoria['cantidad_cuadros'], categoria['personas_por_cuadro'])
    
    # Obtener resultados guardados desde BD
    partidos_guardados = db.obtener_partidos(categoria['id'])
    
    # Estadísticas rápidas
    total_participantes = len(participantes)
    total_cuadros = len(cuadros)
    st.markdown(f"""
    <div style='background: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #3498db; margin: 20px 0;'>
        <h4 style='margin: 0; color: #2c3e50;'>📊 Información de Cuadros</h4>
        <p style='margin: 5px 0; color: #34495e;'>👥 <strong>{total_participantes}</strong> participantes distribuidos en <strong>{total_cuadros}</strong> cuadro(s)</p>
    </div>
    """, unsafe_allow_html=True)
    
    # RECORRER CADA CUADRO
    for cuadro_num, participantes_cuadro in cuadros.items():
        if len(participantes_cuadro) < 2:
            continue
        
        # Container del cuadro con diseño elegante
        st.markdown(f"""
        <div class='cuadro-container'>
            <div class='cuadro-title'>🏓 Cuadro {cuadro_num}</div>
            <div class='tabla-container'>
        """, unsafe_allow_html=True)
        
        jugadores = participantes_cuadro
        
        # ======== GENERAR TABLA ROUND ROBIN ========
        
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
                        # Verificar si este campo debe limpiarse por error
                        clear_key = f"clear_{key}"
                        if st.session_state.get(clear_key, False):
                            valor_mostrar = ""
                            st.session_state[clear_key] = False  # Reset flag
                        else:
                            valor_mostrar = resultado_guardado
                            
                        nuevo_resultado = st.text_input(
                            "",
                            value=valor_mostrar,
                            key=key,
                            label_visibility="collapsed",
                            placeholder="#-#",
                            help="Formato: número-número (ej: 3-1)",
                            max_chars=10
                        )
                        
                        # Validar formato y guardar si cambió
                        if nuevo_resultado != resultado_guardado:
                            if nuevo_resultado == "":
                                # Permitir borrar resultado
                                if resultado_guardado:  # Solo si había un resultado previo
                                    db.guardar_resultado_partido(
                                        categoria['id'],
                                        cuadro_num,
                                        jugador_fila,
                                        jugador_col,
                                        "",
                                        ""
                                    )
                                    st.rerun()
                            elif "-" in nuevo_resultado:
                                # Validar formato #-#
                                partes = nuevo_resultado.split("-")
                                if len(partes) == 2 and partes[0].isdigit() and partes[1].isdigit():
                                    num1, num2 = int(partes[0]), int(partes[1])
                                    # Determinar ganador
                                    ganador = jugador_fila if num1 > num2 else jugador_col
                                    
                                    db.guardar_resultado_partido(
                                        categoria['id'],
                                        cuadro_num,
                                        jugador_fila,
                                        jugador_col,
                                        nuevo_resultado,
                                        ganador
                                    )
                                    st.rerun()
                                else:
                                    # Formato inválido - marcar para limpiar y mostrar toast
                                    st.session_state[f"clear_{key}"] = True
                                    st.toast("⚠️ Formato inválido. Use: número-número", icon="⚠️")
                                    st.rerun()
                            else:
                                # No contiene guión - formato inválido
                                st.session_state[f"clear_{key}"] = True
                                st.toast("⚠️ Formato inválido. Use: número-número (ej: 3-1)", icon="⚠️")
                                st.rerun()
                
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
    
    # ======== BOTONES FINALES ELEGANTES ========
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