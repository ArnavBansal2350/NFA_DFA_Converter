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
    """
    Generate a pure SVG graph without Graphviz.
    Nodes are laid out in a horizontal line.
    """
    n = len(node_names)
    if n == 0:
        return '<svg viewBox="0 0 200 100" xmlns="http://www.w3.org/2000/svg"><text x="100" y="50" text-anchor="middle" fill="#914F1E">No states</text></svg>'

    # Layout
    R = 35  # node radius
    H_GAP = 150  # horizontal gap between centers
    MARGIN_LEFT = 100
    MARGIN_TOP = 100
    cols_per_row = max(4, n)
    rows = math.ceil(n / cols_per_row)

    # Assign positions
    positions = {}
    for i, name in enumerate(node_names):
        col = i % cols_per_row
        row = i // cols_per_row
        x = MARGIN_LEFT + col * H_GAP
        y = MARGIN_TOP + row * 120
        positions[name] = (x, y)

    width = MARGIN_LEFT + (min(n, cols_per_row)) * H_GAP + 40
    height = MARGIN_TOP + rows * 120 + 40

    svg = f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:auto;">\n'

    # Defs
    svg += '''<defs>
  <marker id="arr" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#914F1E"/>
  </marker>
  <marker id="arr-self" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
    <polygon points="0 0, 8 3, 0 6" fill="#914F1E"/>
  </marker>
</defs>\n'''

    # Group edges by (src, dst)
    edge_map = {}
    for src, dst, label in edges:
        key = (src, dst)
        if key not in edge_map:
            edge_map[key] = []
        edge_map[key].append(label)

    # Draw edges
    drawn = set()
    for (src, dst), labels in edge_map.items():
        label = ",".join(labels)
        if src not in positions or dst not in positions:
            continue

        x1, y1 = positions[src]
        x2, y2 = positions[dst]

        if src == dst:
            # Self loop
            cx = x1
            cy = y1 - R
            svg += f'<path d="M {x1-15} {y1-R} C {x1-40} {y1-80} {x1+40} {y1-80} {x1+15} {y1-R}" fill="none" stroke="#914F1E" stroke-width="1.5" marker-end="url(#arr)"/>\n'
            svg += f'<text x="{cx}" y="{y1-75}" text-anchor="middle" font-family="Courier New" font-size="11" fill="#914F1E">{label}</text>\n'
        else:
            # Check if reverse edge exists
            rev = (dst, src)
            is_bidirectional = rev in edge_map

            if is_bidirectional and src > dst:
                continue  # already drawn

            dx = x2 - x1
            dy = y2 - y1
            dist = math.sqrt(dx*dx + dy*dy)
            if dist == 0:
                continue

            # Unit vector
            ux = dx / dist
            uy = dy / dist

            # Start and end points on circle edges
            sx = x1 + ux * R
            sy = y1 + uy * R
            ex = x2 - ux * R
            ey = y2 - uy * R

            if is_bidirectional:
                # Curved arrow
                perp_x = -uy * 30
                perp_y = ux * 30
                mx = (sx + ex) / 2 + perp_x
                my = (sy + ey) / 2 + perp_y
                svg += f'<path d="M {sx:.1f} {sy:.1f} Q {mx:.1f} {my:.1f} {ex:.1f} {ey:.1f}" fill="none" stroke="#914F1E" stroke-width="1.5" marker-end="url(#arr)"/>\n'
                lx = mx
                ly = my - 10
                svg += f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" font-family="Courier New" font-size="11" fill="#914F1E">{label}</text>\n'

                # Reverse edge
                rev_labels = ",".join(edge_map[rev])
                perp_x2 = -perp_x
                perp_y2 = -perp_y
                mx2 = (ex + sx) / 2 + perp_x2
                my2 = (ey + sy) / 2 + perp_y2
                svg += f'<path d="M {ex:.1f} {ey:.1f} Q {mx2:.1f} {my2:.1f} {sx:.1f} {sy:.1f}" fill="none" stroke="#914F1E" stroke-width="1.5" marker-end="url(#arr)"/>\n'
                lx2 = mx2
                ly2 = my2 + 18
                svg += f'<text x="{lx2:.1f}" y="{ly2:.1f}" text-anchor="middle" font-family="Courier New" font-size="11" fill="#914F1E">{rev_labels}</text>\n'
                drawn.add(rev)
            else:
                svg += f'<line x1="{sx:.1f}" y1="{sy:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" stroke="#914F1E" stroke-width="1.5" marker-end="url(#arr)"/>\n'
                lx = (sx + ex) / 2 - uy * 14
                ly = (sy + ey) / 2 + ux * 14
                svg += f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="middle" font-family="Courier New" font-size="11" fill="#914F1E">{label}</text>\n'

    # Draw start arrow
    if start_name in positions:
        sx, sy = positions[start_name]
        svg += f'<line x1="{sx-R-25}" y1="{sy}" x2="{sx-R-2}" y2="{sy}" stroke="#914F1E" stroke-width="2" marker-end="url(#arr)"/>\n'

    # Draw nodes
    for name in node_names:
        x, y = positions[name]
        is_final = name in final_names
        is_dead = name in dead_names
        is_start = name == start_name

        if is_dead:
            fill = '#f5c6c6'
            stroke = '#c0392b'
        elif is_final:
            fill = '#DEAC80'
            stroke = '#914F1E'
        elif is_start:
            fill = '#F7DCB9'
            stroke = '#C07830'
        else:
            fill = '#ffffff'
            stroke = '#914F1E'

        svg += f'<circle cx="{x}" cy="{y}" r="{R}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>\n'

        if is_final:
            svg += f'<circle cx="{x}" cy="{y}" r="{R-7}" fill="none" stroke="{stroke}" stroke-width="1.5"/>\n'

        # Wrap long text
        if len(name) > 6:
            parts = name.strip('{}').split(',')
            mid = len(parts) // 2
            line1 = '{' + ','.join(parts[:mid]) + ','
            line2 = ','.join(parts[mid:]) + '}'
            svg += f'<text x="{x}" y="{y-4}" text-anchor="middle" font-family="Courier New" font-size="10" fill="#2C1A0E">{line1}</text>\n'
            svg += f'<text x="{x}" y="{y+10}" text-anchor="middle" font-family="Courier New" font-size="10" fill="#2C1A0E">{line2}</text>\n'
        else:
            svg += f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="Courier New" font-size="13" fill="#2C1A0E">{name}</text>\n'

    svg += '</svg>'
    return svg


def generate_nfa_graph(states, symbols, start_state, final_states, nfa):
    """Generate NFA SVG without Graphviz."""
    # Build edges
    edge_labels = {}
    for state in states:
        for sym in symbols:
            targets = nfa[state].get(sym, set())
            for t in targets:
                key = (state, t)
                edge_labels.setdefault(key, []).append(sym)

    edges = [(src, dst, ",".join(labels)) for (src, dst), labels in edge_labels.items()]

    return generate_svg_graph(
        node_names=states,
        edges=edges,
        start_name=start_state,
        final_names=list(final_states)
    )


def generate_dfa_graph(dfa_states, dfa_transitions, dfa_final_states, symbols, start_state):
    """Generate DFA SVG without Graphviz."""
    start_fs = frozenset([start_state])
    node_names = [state_name(s) for s in dfa_states]
    final_names = [state_name(s) for s in dfa_final_states]
    dead_names = [state_name(s) for s in dfa_states if not s]
    start_name = state_name(start_fs)

    # Build edges
    edge_labels = {}
    for state in dfa_states:
        src = state_name(state)
        for sym in symbols:
            dest = dfa_transitions[state][sym]
            dst = state_name(dest)
            key = (src, dst)
            edge_labels.setdefault(key, []).append(sym)

    edges = [(src, dst, ",".join(labels)) for (src, dst), labels in edge_labels.items()]

    return generate_svg_graph(
        node_names=node_names,
        edges=edges,
        start_name=start_name,
        final_names=final_names,
        dead_names=dead_names
    )


# ---------------------------------------
# NFA TO DFA CONVERSION STEPS EXPLANATION
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

        step_detail = {
            'type': 'process',
            'current': state_name(current),
            'transitions': []
        }

        for sym in symbols:
            next_state = set()
            detail_parts = []

            for sub_state in current:
                targets = nfa[sub_state].get(sym, set())
                if targets:
                    detail_parts.append(f'{sub_state} →({sym})→ {"{" + ",".join(sorted(targets)) + "}"}')
                    next_state.update(targets)

            next_state = frozenset(next_state)
            dfa_transitions[current][sym] = next_state
            is_new = next_state not in dfa_states

            if next_state not in dfa_states:
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
        'message': f'Final DFA states (contain at least one NFA final state): {", ".join(dfa_final) if dfa_final else "None"}'
    })

    return steps