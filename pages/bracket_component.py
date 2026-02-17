"""
Componente de Bracket Dinámico para Torneos
Design premium con conectores curvos SVG, animaciones y tipografía moderna
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import math

def generate_bracket_html(players, bracket_state, categoria_id, puede_editar=True):
    """
    Genera HTML/CSS/JS para un bracket dinámico premium
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
        'canEdit': puede_editar,
        'numOriginalPlayers': num_players
    }
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Inter', sans-serif;
                background: linear-gradient(160deg, #0f172a 0%, #1e1b4b 40%, #312e81 100%);
                padding: 40px;
                overflow-x: auto;
                min-height: 100vh;
            }}
            
            .bracket-title {{
                text-align: center;
                margin-bottom: 32px;
            }}
            .bracket-title h2 {{
                color: #e2e8f0;
                font-size: 22px;
                font-weight: 800;
                letter-spacing: -0.5px;
            }}
            .bracket-title p {{
                color: #94a3b8;
                font-size: 14px;
                margin-top: 4px;
            }}
            
            .bracket-container {{
                display: flex;
                justify-content: center;
                padding: 20px;
                position: relative;
            }}
            
            .bracket {{
                display: flex;
                gap: 60px;
                position: relative;
            }}
            
            .round {{
                display: flex;
                flex-direction: column;
                position: relative;
                min-width: 200px;
            }}
            
            .round-label {{
                text-align: center;
                font-weight: 700;
                font-size: 12px;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 1.5px;
                padding: 10px 16px;
                margin-bottom: 32px;
                background: rgba(255,255,255,0.05);
                border-radius: 8px;
                border: 1px solid rgba(255,255,255,0.08);
            }}
            .round-label.final {{
                background: linear-gradient(135deg, rgba(251,191,36,0.15), rgba(245,158,11,0.15));
                border-color: rgba(251,191,36,0.3);
                color: #fbbf24;
            }}
            
            .match-wrapper {{
                position: relative;
                margin-bottom: 0;
            }}
            
            .match {{
                display: flex;
                flex-direction: column;
                position: relative;
                gap: 2px;
            }}
            
            .player-slot {{
                display: flex;
                align-items: center;
                height: 44px;
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 0 14px;
                cursor: pointer;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                z-index: 10;
                overflow: hidden;
            }}
            
            .player-slot:first-child {{
                border-radius: 8px 8px 2px 2px;
            }}
            .player-slot:last-child {{
                border-radius: 2px 2px 8px 8px;
            }}
            
            .player-slot:hover {{
                background: rgba(99, 102, 241, 0.15);
                border-color: rgba(99, 102, 241, 0.4);
                transform: translateX(3px);
                box-shadow: 0 0 20px rgba(99, 102, 241, 0.1);
            }}
            
            .player-slot .seed {{
                display: inline-flex;
                align-items: center;
                justify-content: center;
                width: 22px;
                height: 22px;
                background: rgba(255,255,255,0.08);
                border-radius: 6px;
                font-size: 10px;
                font-weight: 700;
                color: #94a3b8;
                margin-right: 10px;
                flex-shrink: 0;
            }}
            
            .player-slot .name {{
                color: #e2e8f0;
                font-size: 13px;
                font-weight: 500;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}
            
            .player-slot.winner {{
                background: linear-gradient(135deg, rgba(34,197,94,0.2), rgba(22,163,74,0.15));
                border-color: rgba(34,197,94,0.5);
                box-shadow: 0 0 16px rgba(34,197,94,0.15);
            }}
            .player-slot.winner .name {{
                color: #4ade80;
                font-weight: 700;
            }}
            .player-slot.winner .seed {{
                background: rgba(34,197,94,0.3);
                color: #4ade80;
            }}
            .player-slot.winner::before {{
                content: '✓';
                position: absolute;
                right: 12px;
                color: #4ade80;
                font-weight: 700;
                font-size: 14px;
            }}
            
            .player-slot.bye {{
                background: rgba(255,255,255,0.02);
                border-style: dashed;
                border-color: rgba(255,255,255,0.06);
                cursor: default;
            }}
            .player-slot.bye:hover {{
                transform: none;
                background: rgba(255,255,255,0.02);
                box-shadow: none;
            }}
            .player-slot.bye .name {{
                color: #475569;
                font-style: italic;
            }}
            
            .player-slot.champion {{
                background: linear-gradient(135deg, rgba(251,191,36,0.25), rgba(245,158,11,0.2));
                border-color: rgba(251,191,36,0.6);
                box-shadow: 0 0 24px rgba(251,191,36,0.2), 0 0 48px rgba(251,191,36,0.1);
                animation: champion-glow 2s ease-in-out infinite alternate;
            }}
            .player-slot.champion .name {{
                color: #fbbf24;
                font-weight: 800;
            }}
            .player-slot.champion .seed {{
                background: rgba(251,191,36,0.3);
                color: #fbbf24;
            }}
            .player-slot.champion::before {{
                content: '🏆';
                position: absolute;
                right: 12px;
                font-size: 16px;
            }}
            
            @keyframes champion-glow {{
                0% {{ box-shadow: 0 0 24px rgba(251,191,36,0.2), 0 0 48px rgba(251,191,36,0.1); }}
                100% {{ box-shadow: 0 0 32px rgba(251,191,36,0.35), 0 0 64px rgba(251,191,36,0.15); }}
            }}
            
            .player-slot.empty {{
                background: rgba(255,255,255,0.02);
                border-style: dashed;
                border-color: rgba(255,255,255,0.06);
                cursor: default;
            }}
            .player-slot.empty:hover {{
                transform: none;
                box-shadow: none;
            }}
            .player-slot.empty .name {{
                color: #334155;
                font-style: italic;
            }}
            
            /* SVG connectors overlay */
            .svg-connectors {{
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 1;
            }}

            .final-match .player-slot {{
                border-width: 2px;
            }}
        </style>
    </head>
    <body>
        <div class="bracket-title">
            <h2>⚔️ Cuadro Eliminatorio</h2>
            <p>{num_players} clasificados &nbsp;•&nbsp; {num_rounds} ronda{'s' if num_rounds > 1 else ''}</p>
        </div>
        
        <div class="bracket-container">
            <div id="bracket" class="bracket"></div>
            <svg id="connectors" class="svg-connectors"></svg>
        </div>
        
        <script>
            const bracketData = {json.dumps(bracket_data)};
            let bracketState = bracketData.state || {{}};
            
            // Initialize bracket
            if (Object.keys(bracketState).length === 0) {{
                bracketState[1] = [...bracketData.players];
                for (let r = 2; r <= bracketData.numRounds; r++) {{
                    const prevRound = bracketState[r - 1];
                    bracketState[r] = new Array(prevRound.length / 2).fill(null);
                }}
            }}
            
            // Process BYEs
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
            
            // Seed map (original index -> seed number)
            const seedMap = {{}};
            bracketData.players.forEach((p, i) => {{
                if (p !== "BYE") seedMap[p] = i + 1;
            }});
            
            function selectWinner(round, matchIndex, player) {{
                if (!bracketData.canEdit || player === "BYE") return;
                
                if (round < bracketData.numRounds) {{
                    bracketState[round + 1][matchIndex] = player;
                }} else {{
                    // Final: actualizar estado local y enviar mensaje
                    bracketState['champion'] = player;
                    console.log("Champion selected:", player);
                    window.parent.postMessage({{
                        type: 'bracket_champion',
                        player: player,
                        categoriaId: bracketData.categoriaId
                    }}, '*');
                }}
                renderBracket();
            }}
            
            function renderBracket() {{
                const bracket = document.getElementById('bracket');
                bracket.innerHTML = '';
                
                const SLOT_HEIGHT = 44;
                const SLOT_GAP = 2;
                const MATCH_HEIGHT = SLOT_HEIGHT * 2 + SLOT_GAP;
                
                const roundElements = [];
                
                for (let round = 1; round <= bracketData.numRounds; round++) {{
                    const roundDiv = document.createElement('div');
                    roundDiv.className = 'round';
                    roundDiv.setAttribute('data-round', round);
                    
                    // Round label
                    const label = document.createElement('div');
                    label.className = 'round-label';
                    if (round === bracketData.numRounds) {{
                        label.classList.add('final');
                        label.textContent = '🏆 FINAL';
                    }} else if (round === bracketData.numRounds - 1 && bracketData.numRounds > 2) {{
                        label.textContent = 'SEMIFINAL';
                    }} else if (round === bracketData.numRounds - 2 && bracketData.numRounds > 3) {{
                        label.textContent = 'CUARTOS';
                    }} else {{
                        label.textContent = `RONDA ${{round}}`;
                    }}
                    roundDiv.appendChild(label);
                    
                    const players = bracketState[round];
                    const matchesInRound = players.length / 2;
                    const verticalSpacing = MATCH_HEIGHT * Math.pow(2, round - 1);
                    
                    for (let i = 0; i < players.length; i += 2) {{
                        const matchWrapper = document.createElement('div');
                        matchWrapper.className = 'match-wrapper';
                        
                        // Spacing between matches
                        const extraGap = round === 1 ? 12 : 0;
                        if (i > 0) {{
                            matchWrapper.style.marginTop = `${{verticalSpacing - MATCH_HEIGHT + extraGap}}px`;
                        }} else if (round > 1) {{
                            matchWrapper.style.marginTop = `${{(verticalSpacing - MATCH_HEIGHT) / 2}}px`;
                        }}
                        
                        const matchDiv = document.createElement('div');
                        matchDiv.className = 'match';
                        if (round === bracketData.numRounds) matchDiv.classList.add('final-match');
                        
                        const p1 = players[i];
                        const p2 = players[i + 1];
                        const matchIndex = Math.floor(i / 2);
                        let winner = null;
                        if (round < bracketData.numRounds) {{
                            winner = bracketState[round + 1]?.[matchIndex];
                        }} else {{
                            winner = bracketState['champion'] || bracketState.champion;
                        }}
                        
                        const isFinalAndWon = round === bracketData.numRounds && winner;
                        
                        // Create player slots
                        [p1, p2].forEach((player, slotIdx) => {{
                            const slot = document.createElement('div');
                            slot.className = 'player-slot';
                            
                            if (!player) {{
                                slot.classList.add('empty');
                                const nameSpan = document.createElement('span');
                                nameSpan.className = 'name';
                                nameSpan.textContent = 'Por definir';
                                slot.appendChild(nameSpan);
                            }} else if (player === "BYE") {{
                                slot.classList.add('bye');
                                const nameSpan = document.createElement('span');
                                nameSpan.className = 'name';
                                nameSpan.textContent = 'BYE';
                                slot.appendChild(nameSpan);
                            }} else {{
                                if (isFinalAndWon && winner === player) {{
                                    slot.classList.add('champion');
                                }} else if (winner === player) {{
                                    slot.classList.add('winner');
                                }}
                                
                                const seedSpan = document.createElement('span');
                                seedSpan.className = 'seed';
                                seedSpan.textContent = seedMap[player] || '?';
                                slot.appendChild(seedSpan);
                                
                                const nameSpan = document.createElement('span');
                                nameSpan.className = 'name';
                                nameSpan.textContent = player;
                                slot.appendChild(nameSpan);
                                
                                if (bracketData.canEdit) {{
                                    slot.onclick = () => selectWinner(round, matchIndex, player);
                                }}
                            }}
                            
                            slot.setAttribute('data-round', round);
                            slot.setAttribute('data-match', matchIndex);
                            slot.setAttribute('data-slot', slotIdx);
                            
                            matchDiv.appendChild(slot);
                        }});
                        
                        matchWrapper.appendChild(matchDiv);
                        roundDiv.appendChild(matchWrapper);
                    }}
                    
                    bracket.appendChild(roundDiv);
                    roundElements.push(roundDiv);
                }}
                
                // Draw SVG connectors
                drawConnectors();
            }}
            
            function drawConnectors() {{
                const svg = document.getElementById('connectors');
                const container = document.querySelector('.bracket-container');
                const containerRect = container.getBoundingClientRect();
                
                svg.setAttribute('width', container.scrollWidth);
                svg.setAttribute('height', container.scrollHeight);
                svg.innerHTML = '';
                
                for (let round = 1; round < bracketData.numRounds; round++) {{
                    const currentRound = document.querySelector(`[data-round="${{round}}"].round`);
                    const nextRound = document.querySelector(`[data-round="${{round + 1}}"].round`);
                    
                    if (!currentRound || !nextRound) continue;
                    
                    const currentMatches = currentRound.querySelectorAll('.match');
                    const nextMatches = nextRound.querySelectorAll('.match');
                    
                    for (let m = 0; m < currentMatches.length; m += 2) {{
                        const match1 = currentMatches[m];
                        const match2 = currentMatches[m + 1];
                        const nextMatch = nextMatches[Math.floor(m / 2)];
                        
                        if (!match1 || !nextMatch) continue;
                        
                        // Get center points
                        const m1Rect = match1.getBoundingClientRect();
                        const m1CenterY = m1Rect.top + m1Rect.height / 2 - containerRect.top;
                        const m1Right = m1Rect.right - containerRect.left;
                        
                        const nmRect = nextMatch.getBoundingClientRect();
                        const nmCenterY = nmRect.top + nmRect.height / 2 - containerRect.top;
                        const nmLeft = nmRect.left - containerRect.left;
                        
                        if (match2) {{
                            const m2Rect = match2.getBoundingClientRect();
                            const m2CenterY = m2Rect.top + m2Rect.height / 2 - containerRect.top;
                            const m2Right = m2Rect.right - containerRect.left;
                            
                            const midX = (m1Right + nmLeft) / 2;
                            
                            // Curved path from match1 to next
                            const path1 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                            path1.setAttribute('d', 
                                `M ${{m1Right}} ${{m1CenterY}} C ${{midX}} ${{m1CenterY}}, ${{midX}} ${{nmCenterY}}, ${{nmLeft}} ${{nmCenterY}}`
                            );
                            path1.setAttribute('fill', 'none');
                            path1.setAttribute('stroke', 'rgba(148,163,184,0.3)');
                            path1.setAttribute('stroke-width', '2');
                            svg.appendChild(path1);
                            
                            // Curved path from match2 to next
                            const path2 = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                            path2.setAttribute('d', 
                                `M ${{m2Right}} ${{m2CenterY}} C ${{midX}} ${{m2CenterY}}, ${{midX}} ${{nmCenterY}}, ${{nmLeft}} ${{nmCenterY}}`
                            );
                            path2.setAttribute('fill', 'none');
                            path2.setAttribute('stroke', 'rgba(148,163,184,0.3)');
                            path2.setAttribute('stroke-width', '2');
                            svg.appendChild(path2);
                        }} else {{
                            // Single line
                            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                            const midX = (m1Right + nmLeft) / 2;
                            path.setAttribute('d', 
                                `M ${{m1Right}} ${{m1CenterY}} C ${{midX}} ${{m1CenterY}}, ${{midX}} ${{nmCenterY}}, ${{nmLeft}} ${{nmCenterY}}`
                            );
                            path.setAttribute('fill', 'none');
                            path.setAttribute('stroke', 'rgba(148,163,184,0.3)');
                            path.setAttribute('stroke-width', '2');
                            svg.appendChild(path);
                        }}
                    }}
                }}
            }}
            
            renderBracket();
            window.addEventListener('resize', drawConnectors);
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
    
    # Calcular altura dinámica basada en el número de jugadores
    num_players = len(players)
    num_rounds = math.ceil(math.log2(num_players)) if num_players > 1 else 1
    next_power = 2 ** num_rounds
    base_height = max(next_power * 55, 400)  # 55px por jugador mínimo
    dynamic_height = min(base_height + 120, 1200)  # Cap en 1200px
    
    # Procesar selección de campeón desde query params (click en la final)
    params = st.query_params
    bw_champion = params.get('bw_champion', '')
    bw_cat = params.get('bw_cat', '')
    
    if bw_champion and bw_cat and str(categoria_id) == str(bw_cat) and puede_editar:
        campeon_key = f'campeon_{categoria_id}'
        st.session_state[campeon_key] = bw_champion
        st.query_params.clear()
        st.rerun()
    
    # Inyectar listener en la página padre para capturar postMessage del iframe
    st.markdown(f"""
    <script>
    if (!window._bracketListenerAdded) {{
        window._bracketListenerAdded = true;
        window.addEventListener('message', function(event) {{
            if (event.data && event.data.type === 'bracket_champion') {{
                const url = new URL(window.location.href);
                url.searchParams.set('bw_champion', event.data.player);
                url.searchParams.set('bw_cat', event.data.categoriaId);
                window.location.href = url.toString();
            }}
        }});
    }}
    </script>
    """, unsafe_allow_html=True)
    
    # Renderizar componente
    components.html(html_code, height=dynamic_height, scrolling=True)
