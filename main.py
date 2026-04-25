import math

# ------------------------------
# NFA TO DFA CONVERSION LOGIC
# ------------------------------

def nfa_to_dfa(states, symbols, start_state, final_states, nfa):
    dfa_states = []
    dfa_transitions = {}
    queue = []

    start = frozenset([start_state])
    queue.append(start)
    dfa_states.append(start)

    while queue:
        current = queue.pop(0)
        dfa_transitions[current] = {}

        for sym in symbols:
            next_state = set()
            for sub_state in current:
                if sub_state in nfa and sym in nfa[sub_state]:
                    next_state.update(nfa[sub_state][sym])

            next_state = frozenset(next_state)
            dfa_transitions[current][sym] = next_state

            if next_state not in dfa_states:
                dfa_states.append(next_state)
                queue.append(next_state)

    dfa_final_states = []
    for state in dfa_states:
        if any(s in final_states for s in state):
            dfa_final_states.append(state)

    return dfa_states, dfa_transitions, dfa_final_states


def state_name(state):
    if not state:
        return "d"
    return "{" + ",".join(sorted(state)) + "}"


def get_dfa_table(dfa_states, dfa_transitions, dfa_final_states, symbols, start_state):
    rows = []
    start_fs = frozenset([start_state])
    for state in dfa_states:
        row = {
            "state": state_name(state),
            "is_start": state == start_fs,
            "is_final": state in dfa_final_states,
            "transitions": {}
        }
        for sym in symbols:
            dest = dfa_transitions[state][sym]
            row["transitions"][sym] = state_name(dest)
        rows.append(row)
    return rows


# ------------------------------
# PURE SVG GRAPH GENERATION
# ------------------------------

def generate_svg_graph(node_names, edges, start_name, final_names, dead_names=[]):
    n = len(node_names)
    if n == 0:
        return '<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg"></svg>'

    R = 40        # node radius
    GAP = 160     # gap between node centers
    ML = 100      # left margin
    MT = 110      # top margin (enough for self loops above)
    LOOP_H = 55   # self loop height above node

    width  = ML + (n - 1) * GAP + R + 60
    height = MT + R + 80   # room below node

    svg  = f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
    svg += f'style="width:100%;height:100%;">\n'

    svg += '''<defs>
  <marker id="ah" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
    <polygon points="0 0, 10 3.5, 0 7" fill="#914F1E"/>
  </marker>
</defs>\n'''

    # positions
    pos = {}
    for i, name in enumerate(node_names):
        pos[name] = (ML + i * GAP, MT)

    # Group edges
    edge_map = {}
    for src, dst, label in edges:
        edge_map.setdefault((src, dst), []).append(label)

    drawn_pairs = set()

    for (src, dst), labels in edge_map.items():
        label = ",".join(sorted(set(labels)))
        if src not in pos or dst not in pos:
            continue

        x1, y1 = pos[src]
        x2, y2 = pos[dst]

        if src == dst:
            # Self loop — draw above node
            lx = x1 - LOOP_H
            rx = x1 + LOOP_H
            top = y1 - R - LOOP_H * 1.5

            svg += (f'<path d="M {x1-R*0.6:.1f} {y1-R*0.8:.1f} '
                    f'C {lx:.1f} {top:.1f}, {rx:.1f} {top:.1f}, '
                    f'{x1+R*0.6:.1f} {y1-R*0.8:.1f}" '
                    f'fill="none" stroke="#914F1E" stroke-width="1.8" '
                    f'marker-end="url(#ah)"/>\n')
            svg += (f'<text x="{x1}" y="{top - 8}" text-anchor="middle" '
                    f'font-family="Courier New" font-size="12" fill="#914F1E">'
                    f'{label}</text>\n')

        else:
            rev = (dst, src)
            pair = tuple(sorted([src, dst]))
            is_bi = rev in edge_map

            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx*dx + dy*dy)
            ux, uy = dx/dist, dy/dist

            # arrow start/end on circle edge
            sx = x1 + ux * (R + 2)
            sy = y1 + uy * (R + 2)
            ex = x2 - ux * (R + 2)
            ey = y2 - uy * (R + 2)

            if is_bi and pair not in drawn_pairs:
                drawn_pairs.add(pair)
                CURVE = 28
                # forward
                px = -uy * CURVE
                py =  ux * CURVE
                mx = (sx + ex)/2 + px
                my = (sy + ey)/2 + py
                svg += (f'<path d="M {sx:.1f} {sy:.1f} Q {mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" '
                        f'fill="none" stroke="#914F1E" stroke-width="1.8" '
                        f'marker-end="url(#ah)"/>\n')
                svg += (f'<text x="{mx + px*0.4:.1f}" y="{my + py*0.4 - 6:.1f}" '
                        f'text-anchor="middle" font-family="Courier New" font-size="12" '
                        f'fill="#914F1E">{label}</text>\n')
                # reverse
                rev_label = ",".join(sorted(set(edge_map[rev])))
                mx2 = (ex + sx)/2 - px
                my2 = (ey + sy)/2 - py
                svg += (f'<path d="M {ex:.1f} {ey:.1f} Q {mx2:.1f} {my2:.1f} {sx:.1f} {sy:.1f}" '
                        f'fill="none" stroke="#914F1E" stroke-width="1.8" '
                        f'marker-end="url(#ah)"/>\n')
                svg += (f'<text x="{mx2 - px*0.4:.1f}" y="{my2 - py*0.4 + 16:.1f}" '
                        f'text-anchor="middle" font-family="Courier New" font-size="12" '
                        f'fill="#914F1E">{rev_label}</text>\n')

            elif not is_bi:
                # straight arrow
                svg += (f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
                        f'stroke="#914F1E" stroke-width="1.8" marker-end="url(#ah)"/>\n')
                lx = (sx + ex)/2 - uy * 16
                ly = (sy + ey)/2 + ux * 16 - 6
                svg += (f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" '
                        f'font-family="Courier New" font-size="12" fill="#914F1E">'
                        f'{label}</text>\n')

    # Start arrow
    if start_name in pos:
        sx, sy = pos[start_name]
        svg += (f'<line x1="{sx - R - 35}" y1="{sy}" x2="{sx - R - 3}" y2="{sy}" '
                f'stroke="#914F1E" stroke-width="2" marker-end="url(#ah)"/>\n')

    # Draw nodes (on top of edges)
    for name in node_names:
        x, y = pos[name]
        is_dead  = name in dead_names
        is_final = name in final_names

        if is_dead:
            fill, stroke = '#f5c6c6', '#c0392b'
        elif is_final:
            fill, stroke = '#DEAC80', '#914F1E'
        elif name == start_name:
            fill, stroke = '#F7DCB9', '#C07830'
        else:
            fill, stroke = '#ffffff', '#914F1E'

        svg += (f'<circle cx="{x}" cy="{y}" r="{R}" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="2.2"/>\n')

        if is_final:
            svg += (f'<circle cx="{x}" cy="{y}" r="{R-7}" '
                    f'fill="none" stroke="{stroke}" stroke-width="1.6"/>\n')

        # Label — wrap if long
        parts = name.replace('{','').replace('}','').split(',')
        if len(parts) > 3:
            mid = math.ceil(len(parts)/2)
            l1 = '{' + ','.join(parts[:mid]) + ','
            l2 = ','.join(parts[mid:]) + '}'
            svg += (f'<text x="{x}" y="{y - 5}" text-anchor="middle" '
                    f'font-family="Courier New" font-size="11" fill="#2C1A0E">{l1}</text>\n')
            svg += (f'<text x="{x}" y="{y + 10}" text-anchor="middle" '
                    f'font-family="Courier New" font-size="11" fill="#2C1A0E">{l2}</text>\n')
        else:
            fs = 13 if len(name) <= 6 else 10
            svg += (f'<text x="{x}" y="{y + 5}" text-anchor="middle" '
                    f'font-family="Courier New" font-size="{fs}" fill="#2C1A0E">'
                    f'{name}</text>\n')

    svg += '</svg>'
    return svg


def generate_nfa_graph(states, symbols, start_state, final_states, nfa):
    """Generate DOT string for NFA — rendered by Viz.js in browser."""
    dot = 'digraph NFA {\n'
    dot += '  rankdir=LR;\n'
    dot += '  bgcolor="white";\n'
    dot += '  node [fontname="Courier New" fontsize=13];\n'
    dot += '  edge [fontname="Courier New" fontsize=11 color="#914F1E"];\n'
    dot += '  "" [shape=none width=0 height=0];\n'

    for state in states:
        if state in final_states:
            dot += f'  "{state}" [shape=doublecircle style=filled fillcolor="#DEAC80" color="#914F1E" fontcolor="#2C1A0E"];\n'
        elif state == start_state:
            dot += f'  "{state}" [shape=circle style=filled fillcolor="#F7DCB9" color="#C07830" fontcolor="#2C1A0E"];\n'
        else:
            dot += f'  "{state}" [shape=circle style=filled fillcolor="#ffffff" color="#914F1E" fontcolor="#2C1A0E"];\n'

    dot += f'  "" -> "{start_state}";\n'

    edge_map = {}
    for state in states:
        for sym in symbols:
            for t in nfa[state].get(sym, set()):
                edge_map.setdefault((state, t), []).append(sym)

    for (src, dst), labels in edge_map.items():
        dot += f'  "{src}" -> "{dst}" [label="{",".join(labels)}"];\n'

    dot += '}\n'
    return dot


def generate_dfa_graph(dfa_states, dfa_transitions, dfa_final_states, symbols, start_state):
    """Generate DOT string for DFA — rendered by Viz.js in browser."""
    start_fs = frozenset([start_state])
    start_name = state_name(start_fs)

    dot = 'digraph DFA {\n'
    dot += '  rankdir=LR;\n'
    dot += '  bgcolor="white";\n'
    dot += '  node [fontname="Courier New" fontsize=11];\n'
    dot += '  edge [fontname="Courier New" fontsize=10 color="#914F1E"];\n'
    dot += '  "" [shape=none width=0 height=0];\n'

    for state in dfa_states:
        name = state_name(state)
        if not state:
            dot += f'  "{name}" [shape=circle style=filled fillcolor="#f5c6c6" color="#c0392b" fontcolor="#2C1A0E"];\n'
        elif state in dfa_final_states:
            dot += f'  "{name}" [shape=doublecircle style=filled fillcolor="#DEAC80" color="#914F1E" fontcolor="#2C1A0E"];\n'
        elif state == start_fs:
            dot += f'  "{name}" [shape=circle style=filled fillcolor="#F7DCB9" color="#C07830" fontcolor="#2C1A0E"];\n'
        else:
            dot += f'  "{name}" [shape=circle style=filled fillcolor="#ffffff" color="#914F1E" fontcolor="#2C1A0E"];\n'

    dot += f'  "" -> "{start_name}";\n'

    edge_map = {}
    for state in dfa_states:
        src = state_name(state)
        for sym in symbols:
            dst = state_name(dfa_transitions[state][sym])
            edge_map.setdefault((src, dst), []).append(sym)

    for (src, dst), labels in edge_map.items():
        dot += f'  "{src}" -> "{dst}" [label="{",".join(labels)}"];\n'

    dot += '}\n'
    return dot


# ---------------------------------------
# CONVERSION STEPS
# ---------------------------------------

def get_conversion_steps(states, symbols, start_state, final_states, nfa):
    steps = []
    dfa_states = []
    dfa_transitions = {}
    queue = []

    start = frozenset([start_state])
    queue.append(start)
    dfa_states.append(start)

    steps.append({
        'type': 'start',
        'message': f'Initial DFA state = {state_name(start)} (start state of NFA)'
    })

    while queue:
        current = queue.pop(0)
        dfa_transitions[current] = {}
        step_detail = {'type': 'process', 'current': state_name(current), 'transitions': []}

        for sym in symbols:
            next_state = set()
            detail_parts = []
            for sub_state in current:
                targets = nfa[sub_state].get(sym, set())
                if targets:
                    detail_parts.append(
                        f'{sub_state} →({sym})→ {"{" + ",".join(sorted(targets)) + "}"}'
                    )
                    next_state.update(targets)

            next_state = frozenset(next_state)
            dfa_transitions[current][sym] = next_state
            is_new = next_state not in dfa_states

            if is_new:
                dfa_states.append(next_state)
                queue.append(next_state)

            step_detail['transitions'].append({
                'symbol': sym,
                'parts': detail_parts if detail_parts else [f'No transitions on "{sym}"'],
                'result': state_name(next_state),
                'is_new': is_new
            })

        steps.append(step_detail)

    dfa_final = [state_name(s) for s in dfa_states if any(x in final_states for x in s)]
    steps.append({
        'type': 'finals',
        'message': f'Final DFA states: {", ".join(dfa_final) if dfa_final else "None"}'
    })

    return steps
