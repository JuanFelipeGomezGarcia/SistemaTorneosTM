"""
Componente de Bracket Dinámico para Torneos
Sistema completamente dinámico que genera brackets tipo torneo clásico
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import math

def generate_bracket_html(players, bracket_state, categoria_id, puede_editar=True):
    """
    Genera HTML/CSS/JS para un bracket dinámico
    
    Args:
        players: Lista de nombres de jugadores
        bracket_state: Estado actual del bracket {ronda: [jugadores]}
        categoria_id: ID único para el bracket
        puede_editar: Si se puede editar o es solo lectura
    """
    
    # Calcular estructura del bracket
    num_players = len(players)
    num_rounds = math.ceil(math.log2(num_players)) if num_players > 1 else 1
    next_power = 2 ** num_rounds
    
    # Agregar BYEs si es necesario
    while len(players) < next_power:
        players.append("BYE")
    
    # Preparar datos para JavaScript
    bracket_data = {
        'players': players,
        'state': bracket_state,
        'numRounds': num_rounds,
        'categoriaId': categoria_id,
        'canEdit': puede_editar
    }
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 40px;
                overflow-x: auto;
            }}
            
            .bracket-container {{
                display: flex;
                justify-content: center;
                min-height: 100vh;
                padding: 20px;
            }}
            
            .bracket {{
                display: flex;
                gap: 100px;
                position: relative;
            }}
            
            .round {{
                display: flex;
                flex-direction: column;
                position: relative;
            }}
            
            .round-title {{
                text-align: center;
                font-weight: bold;
                font-size: 15px;
                color: #2c3e50;
                background: white;
                padding: 8px 20px;
                border-radius: 8px;
                margin-bottom: 40px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            }}
            
            .match-wrapper {{
                position: relative;
                margin-bottom: 0;
            }}
            
            .match {{
                display: flex;
                flex-direction: column;
                position: relative;
            }}
            
            .player-line {{
                display: flex;
                align-items: center;
                position: relative;
                height: 40px;
                margin: 0;
            }}
            
            .player {{
                background: white;
                border: 2px solid #333;
                padding: 0 15px;
                height: 100%;
                display: flex;
                align-items: center;
                cursor: pointer;
                transition: all 0.2s ease;
                font-size: 14px;
                font-weight: 500;
                min-width: 180px;
                position: relative;
                z-index: 10;
            }}
            
            .player:hover {{
                background: #e3f2fd;
                border-color: #2196F3;
                transform: translateX(3px);
            }}
            
            .player.winner {{
                background: #4caf50;
                color: white;
                border-color: #4caf50;
                font-weight: bold;
            }}
            
            .player.bye {{
                background: #f5f5f5;
                color: #999;
                cursor: default;
                border-style: dashed;
            }}
            
            .player.bye:hover {{
                transform: none;
                background: #f5f5f5;
            }}
            
            /* Líneas horizontales desde cada jugador */
            .line-h {{
                position: absolute;
                height: 2px;
                background: #333;
                left: 100%;
                width: 50px;
                top: 19px;
                z-index: 5;
            }}
            
            /* Línea vertical conectando dos jugadores del mismo match */
            .line-v {{
                position: absolute;
                width: 2px;
                background: #333;
                left: calc(100% + 50px);
                z-index: 5;
            }}
            
            /* Línea horizontal hacia la siguiente ronda */
            .connector-to-next {{
                position: absolute;
                height: 2px;
                background: #333;
                left: calc(100% + 50px);
                width: 50px;
                z-index: 5;
            }}
            
            .final-match .player {{
                border-color: #ffd700;
                border-width: 3px;
            }}
        </style>
    </head>
    <body>
        <div class="bracket-container">
            <div id="bracket" class="bracket"></div>
        </div>
        
        <script>
            const bracketData = {json.dumps(bracket_data)};
            let bracketState = bracketData.state || {{}};
            
            // Inicializar bracket si está vacío
            if (Object.keys(bracketState).length === 0) {{
                bracketState[1] = [...bracketData.players];
                for (let r = 2; r <= bracketData.numRounds; r++) {{
                    const prevRound = bracketState[r - 1];
                    bracketState[r] = new Array(prevRound.length / 2).fill(null);
                }}
            }}
            
            // Procesar BYEs automáticamente
            function processByes() {{
                for (let round = 1; round < bracketData.numRounds; round++) {{
                    const players = bracketState[round];
                    for (let i = 0; i < players.length; i += 2) {{
                        const p1 = players[i];
                        const p2 = players[i + 1];
                        
                        if (p1 === "BYE" && p2 && p2 !== "BYE") {{
                            bracketState[round + 1][Math.floor(i / 2)] = p2;
                        }} else if (p2 === "BYE" && p1 && p1 !== "BYE") {{
                            bracketState[round + 1][Math.floor(i / 2)] = p1;
                        }}
                    }}
                }}
            }}
            
            processByes();
            
            function selectWinner(round, matchIndex, player) {{
                if (!bracketData.canEdit || player === "BYE") return;
                
                // Actualizar estado local
                if (round < bracketData.numRounds) {{
                    bracketState[round + 1][matchIndex] = player;
                }}
                
                // Notificar a Streamlit
                window.parent.postMessage({{
                    type: round === bracketData.numRounds ? 'champion' : 'winner',
                    categoriaId: bracketData.categoriaId,
                    round: round,
                    matchIndex: matchIndex,
                    winner: player
                }}, '*');
                
                renderBracket();
            }}
            
            function renderBracket() {{
                const bracket = document.getElementById('bracket');
                bracket.innerHTML = '';
                
                const LINE_HEIGHT = 40;
                
                for (let round = 1; round <= bracketData.numRounds; round++) {{
                    const roundDiv = document.createElement('div');
                    roundDiv.className = 'round';
                    
                    // Título de ronda
                    const title = document.createElement('div');
                    title.className = 'round-title';
                    if (round === bracketData.numRounds) {{
                        title.textContent = '🏆 FINAL';
                    }} else if (round === bracketData.numRounds - 1 && bracketData.numRounds > 2) {{
                        title.textContent = '🥉 SEMIFINAL';
                    }} else {{
                        title.textContent = `Ronda ${{round}}`;
                    }}
                    roundDiv.appendChild(title);
                    
                    const players = bracketState[round];
                    const matchesInRound = players.length / 2;
                    const verticalSpacing = LINE_HEIGHT * Math.pow(2, round);
                    
                    for (let i = 0; i < players.length; i += 2) {{
                        const matchWrapper = document.createElement('div');
                        matchWrapper.className = 'match-wrapper';
                        
                        // Espaciado entre matches
                        if (i > 0) {{
                            matchWrapper.style.marginTop = `${{verticalSpacing - LINE_HEIGHT}}px`;
                        }} else if (round > 1) {{
                            matchWrapper.style.marginTop = `${{(verticalSpacing / 2) - LINE_HEIGHT}}px`;
                        }}
                        
                        const matchDiv = document.createElement('div');
                        matchDiv.className = 'match';
                        if (round === bracketData.numRounds) {{
                            matchDiv.classList.add('final-match');
                        }}
                        
                        const p1 = players[i];
                        const p2 = players[i + 1];
                        const matchIndex = Math.floor(i / 2);
                        const winner = round < bracketData.numRounds ? bracketState[round + 1][matchIndex] : null;
                        
                        // Jugador 1
                        if (p1) {{
                            const line1 = document.createElement('div');
                            line1.className = 'player-line';
                            
                            const player1 = document.createElement('div');
                            player1.className = 'player';
                            if (p1 === "BYE") {{
                                player1.classList.add('bye');
                                player1.textContent = 'BYE';
                            }} else if (winner === p1) {{
                                player1.classList.add('winner');
                                player1.textContent = `✓ ${{p1}}`;
                            }} else {{
                                player1.textContent = p1;
                            }}
                            
                            if (bracketData.canEdit && p1 !== "BYE") {{
                                player1.onclick = () => selectWinner(round, matchIndex, p1);
                            }}
                            
                            line1.appendChild(player1);
                            
                            // Línea horizontal desde jugador 1
                            if (round < bracketData.numRounds && p1 !== "BYE" && p2 !== "BYE") {{
                                const lineH1 = document.createElement('div');
                                lineH1.className = 'line-h';
                                line1.appendChild(lineH1);
                            }}
                            
                            matchDiv.appendChild(line1);
                        }}
                        
                        // Jugador 2
                        if (p2) {{
                            const line2 = document.createElement('div');
                            line2.className = 'player-line';
                            
                            const player2 = document.createElement('div');
                            player2.className = 'player';
                            if (p2 === "BYE") {{
                                player2.classList.add('bye');
                                player2.textContent = 'BYE';
                            }} else if (winner === p2) {{
                                player2.classList.add('winner');
                                player2.textContent = `✓ ${{p2}}`;
                            }} else {{
                                player2.textContent = p2;
                            }}
                            
                            if (bracketData.canEdit && p2 !== "BYE") {{
                                player2.onclick = () => selectWinner(round, matchIndex, p2);
                            }}
                            
                            line2.appendChild(player2);
                            
                            // Línea horizontal desde jugador 2
                            if (round < bracketData.numRounds && p1 !== "BYE" && p2 !== "BYE") {{
                                const lineH2 = document.createElement('div');
                                lineH2.className = 'line-h';
                                line2.appendChild(lineH2);
                            }}
                            
                            matchDiv.appendChild(line2);
                        }}
                        
                        // Línea vertical conectando los dos jugadores
                        if (round < bracketData.numRounds && p1 && p2 && p1 !== "BYE" && p2 !== "BYE") {{
                            const lineV = document.createElement('div');
                            lineV.className = 'line-v';
                            lineV.style.top = `19px`;
                            lineV.style.height = `${{LINE_HEIGHT}}px`;
                            matchDiv.appendChild(lineV);
                            
                            // Línea horizontal hacia la siguiente ronda
                            const connectorH = document.createElement('div');
                            connectorH.className = 'connector-to-next';
                            connectorH.style.top = `${{LINE_HEIGHT - 1}}px`;
                            matchDiv.appendChild(connectorH);
                        }}
                        
                        matchWrapper.appendChild(matchDiv);
                        roundDiv.appendChild(matchWrapper);
                    }}
                    
                    bracket.appendChild(roundDiv);
                }}
            }}
            
            renderBracket();
        </script>
    </body>
    </html>
    """
    
    return html_code


def render_bracket(players, categoria_id, puede_editar=True):
    """
    Renderiza el bracket en Streamlit
    """
    # Obtener estado del bracket desde session_state
    bracket_key = f'bracket_state_{categoria_id}'
    if bracket_key not in st.session_state:
        st.session_state[bracket_key] = {}
    
    bracket_state = st.session_state[bracket_key]
    
    # Generar HTML
    html_code = generate_bracket_html(players, bracket_state, categoria_id, puede_editar)
    
    # Renderizar componente
    components.html(html_code, height=800, scrolling=True)
