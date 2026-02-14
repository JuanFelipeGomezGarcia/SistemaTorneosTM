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
                padding: 30px;
                overflow-x: auto;
            }}
            
            .bracket-container {{
                display: flex;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
                padding: 20px;
            }}
            
            .bracket {{
                display: flex;
                gap: 80px;
                position: relative;
            }}
            
            .round {{
                display: flex;
                flex-direction: column;
                justify-content: space-around;
                position: relative;
            }}
            
            .round-title {{
                text-align: center;
                font-weight: bold;
                font-size: 16px;
                color: #2c3e50;
                background: white;
                padding: 8px 16px;
                border-radius: 8px;
                margin-bottom: 30px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            
            .match {{
                position: relative;
                display: flex;
                flex-direction: column;
            }}
            
            .player {{
                position: relative;
                height: 35px;
                display: flex;
                align-items: center;
                padding: 0 15px;
                background: white;
                border: 2px solid #ddd;
                cursor: pointer;
                transition: all 0.3s ease;
                font-size: 14px;
                font-weight: 500;
                min-width: 200px;
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
                font-style: italic;
            }}
            
            .player.bye:hover {{
                transform: none;
                background: #f5f5f5;
                border-color: #ddd;
            }}
            
            .player-top {{
                border-radius: 5px 5px 0 0;
                border-bottom: 1px solid #ddd;
            }}
            
            .player-bottom {{
                border-radius: 0 0 5px 5px;
            }}
            
            /* Líneas conectoras */
            .connector {{
                position: absolute;
                background: #333;
            }}
            
            .connector-h {{
                height: 2px;
                width: 40px;
                right: -40px;
                top: 50%;
                transform: translateY(-1px);
            }}
            
            .connector-v {{
                width: 2px;
                right: -40px;
            }}
            
            .final-match .player {{
                border-color: #ffd700;
                border-width: 3px;
            }}
            
            .champion {{
                text-align: center;
                margin-top: 30px;
                padding: 20px;
                background: linear-gradient(135deg, #FFD700 0%, #FFA000 100%);
                border-radius: 15px;
                box-shadow: 0 8px 25px rgba(255, 215, 0, 0.4);
            }}
            
            .champion h2 {{
                color: #333;
                font-size: 24px;
                margin-bottom: 10px;
            }}
            
            .champion h3 {{
                color: #555;
                font-size: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="bracket-container">
            <div id="bracket" class="bracket"></div>
        </div>
        <div id="champion-display"></div>
        
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
                    const matchHeight = 80;
                    const spacing = matchHeight * Math.pow(2, round - 1);
                    
                    for (let i = 0; i < players.length; i += 2) {{
                        const matchDiv = document.createElement('div');
                        matchDiv.className = 'match';
                        if (round === bracketData.numRounds) {{
                            matchDiv.classList.add('final-match');
                        }}
                        
                        // Espaciado superior
                        if (i > 0) {{
                            matchDiv.style.marginTop = `${{spacing}}px`;
                        }} else if (round > 1) {{
                            matchDiv.style.marginTop = `${{spacing / 2}}px`;
                        }}
                        
                        const p1 = players[i];
                        const p2 = players[i + 1];
                        const matchIndex = Math.floor(i / 2);
                        const winner = round < bracketData.numRounds ? bracketState[round + 1][matchIndex] : null;
                        
                        // Jugador 1
                        if (p1) {{
                            const player1 = document.createElement('div');
                            player1.className = 'player player-top';
                            if (p1 === "BYE") {{
                                player1.classList.add('bye');
                            }} else if (winner === p1) {{
                                player1.classList.add('winner');
                                player1.textContent = `✓ ${{p1}}`;
                            }} else {{
                                player1.textContent = p1;
                            }}
                            
                            if (bracketData.canEdit && p1 !== "BYE") {{
                                player1.onclick = () => selectWinner(round, matchIndex, p1);
                            }}
                            
                            matchDiv.appendChild(player1);
                        }}
                        
                        // Jugador 2
                        if (p2) {{
                            const player2 = document.createElement('div');
                            player2.className = 'player player-bottom';
                            if (p2 === "BYE") {{
                                player2.classList.add('bye');
                            }} else if (winner === p2) {{
                                player2.classList.add('winner');
                                player2.textContent = `✓ ${{p2}}`;
                            }} else {{
                                player2.textContent = p2;
                            }}
                            
                            if (bracketData.canEdit && p2 !== "BYE") {{
                                player2.onclick = () => selectWinner(round, matchIndex, p2);
                            }}
                            
                            matchDiv.appendChild(player2);
                        }}
                        
                        // Líneas conectoras
                        if (round < bracketData.numRounds && p1 && p2 && p1 !== "BYE" && p2 !== "BYE") {{
                            // Línea horizontal desde el centro del match
                            const connH = document.createElement('div');
                            connH.className = 'connector connector-h';
                            matchDiv.appendChild(connH);
                            
                            // Línea vertical solo en el primer match de cada par
                            if (i % 4 === 0 && i + 2 < players.length) {{
                                const connV = document.createElement('div');
                                connV.className = 'connector connector-v';
                                const verticalHeight = spacing + matchHeight;
                                connV.style.top = `${{matchHeight / 2}}px`;
                                connV.style.height = `${{verticalHeight}}px`;
                                matchDiv.appendChild(connV);
                            }}
                        }}
                        
                        roundDiv.appendChild(matchDiv);
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
