import streamlit as st
import pandas as pd
from typing import List, Dict

def generar_cuadros(participantes: List[str], cantidad_cuadros: int, personas_por_cuadro: int):
    """Genera los cuadros distribuyendo los participantes"""
    cuadros = {}
    
    # Inicializar cuadros vacíos
    for i in range(1, cantidad_cuadros + 1):
        cuadros[i] = []
    
    # Distribuir participantes
    for idx, participante in enumerate(participantes):
        cuadro_num = (idx % cantidad_cuadros) + 1
        if len(cuadros[cuadro_num]) < personas_por_cuadro:
            cuadros[cuadro_num].append(participante)
    
    return cuadros

def mostrar_cuadro(cuadro_num: int, participantes: List[str], es_admin: bool = True):
    """Función eliminada - usar nueva vista_cuadros.py"""
    pass

def generar_llaves(ganadores_cuadros: List[str]):
    """Genera la estructura de llaves eliminatorias"""
    import math
    
    # Calcular número de rondas necesarias
    num_participantes = len(ganadores_cuadros)
    num_rondas = math.ceil(math.log2(num_participantes))
    
    # Crear estructura de llaves
    llaves = {}
    
    # Primera ronda
    llaves[1] = ganadores_cuadros.copy()
    
    # Rondas siguientes
    for ronda in range(2, num_rondas + 1):
        llaves[ronda] = [None] * (len(llaves[ronda - 1]) // 2)
    
    return llaves

def mostrar_llaves(llaves: Dict, es_admin: bool = True):
    """Muestra las llaves eliminatorias"""
    st.subheader("Llaves Eliminatorias")
    
    for ronda, participantes in llaves.items():
        st.write(f"**Ronda {ronda}**")
        
        if ronda == 1:
            # Primera ronda - mostrar enfrentamientos
            for i in range(0, len(participantes), 2):
                if i + 1 < len(participantes):
                    col1, col2, col3 = st.columns([2, 1, 2])
                    
                    with col1:
                        if es_admin:
                            ganador1 = st.checkbox(participantes[i], key=f"llave_r{ronda}_{i}")
                        else:
                            st.write(participantes[i])
                    
                    with col2:
                        st.write("vs")
                    
                    with col3:
                        if es_admin:
                            ganador2 = st.checkbox(participantes[i + 1], key=f"llave_r{ronda}_{i+1}")
                        else:
                            st.write(participantes[i + 1])
        else:
            # Rondas siguientes
            for i, participante in enumerate(participantes):
                if participante:
                    if es_admin:
                        st.checkbox(participante, key=f"llave_r{ronda}_{i}")
                    else:
                        st.write(f"- {participante}")
                else:
                    st.write("- TBD")
        
        st.write("---")

def validar_cuadros_completos(cuadros_resultados: Dict) -> bool:
    """Valida si todos los cuadros tienen resultados completos"""
    for cuadro, resultados in cuadros_resultados.items():
        if not resultados:  # Si no hay resultados en el cuadro
            return False
    return True