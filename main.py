from graphviz import Digraph
import os

# ------------------------------
# NFA TO DFA CONVERSION LOGIC
# ------------------------------

def nfa_to_dfa(states, symbols, start_state, final_states, nfa):
    """
    Convert NFA to DFA using Subset Construction.
    Returns dfa_states, dfa_transitions, dfa_final_states
    """
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
    """Convert frozenset to readable name."""
    if not state:
        return "d"
    return "{" + ",".join(sorted(state)) + "}"


def get_dfa_table(dfa_states, dfa_transitions, dfa_final_states, symbols, start_state):
    """Build DFA transition table as list of dicts for JSON."""
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
# GRAPH GENERATION - NFA
# ------------------------------

def generate_nfa_graph(states, symbols, start_state, final_states, nfa):
    """Generate NFA graph using Graphviz and return SVG string."""
    dot = Digraph(format='svg')
    dot.attr(rankdir='LR', bgcolor='white')
    dot.attr('node', fontname='Courier New', fontsize='13')
    dot.attr('edge', fontname='Courier New', fontsize='11')

    for state in states:
        if state in final_states:
            dot.node(state, shape='doublecircle', style='filled',
                     fillcolor='#DEAC80', color='#914F1E', fontcolor='#2C1A0E')
        elif state == start_state:
            dot.node(state, shape='circle', style='filled',
                     fillcolor='#F7DCB9', color='#C07830', fontcolor='#2C1A0E')
        else:
            dot.node(state, shape='circle', style='filled',
                     fillcolor='#ffffff', color='#914F1E', fontcolor='#2C1A0E')

    dot.node('', shape='none', width='0', height='0')
    dot.edge('', start_state, arrowhead='vee')

    # Group edges by (from, to) to combine labels
    edge_labels = {}
    for state in states:
        for sym in symbols:
            targets = nfa[state].get(sym, set())
            for t in targets:
                key = (state, t)
                edge_labels.setdefault(key, []).append(sym)

    for (src, dst), labels in edge_labels.items():
        dot.edge(src, dst, label=",".join(labels), color='#914F1E')

    svg_data = dot.pipe(format='svg').decode('utf-8')
    # Strip XML header for embedding
    svg_start = svg_data.find('<svg')
    return svg_data[svg_start:]


# ------------------------------
# GRAPH GENERATION - DFA
# ------------------------------

def generate_dfa_graph(dfa_states, dfa_transitions, dfa_final_states, symbols, start_state):
    """Generate DFA graph using Graphviz and return SVG string."""
    dot = Digraph(format='svg')
    dot.attr(rankdir='LR', bgcolor='white')
    dot.attr('node', fontname='Courier New', fontsize='13')
    dot.attr('edge', fontname='Courier New', fontsize='11')

    start_fs = frozenset([start_state])

    for state in dfa_states:
        name = state_name(state)
        if not state:  # dead state
            dot.node(name, shape='circle', style='filled',
                     fillcolor='#f5c6c6', color='#c0392b', fontcolor='#2C1A0E')
        elif state in dfa_final_states:
            dot.node(name, shape='doublecircle', style='filled',
                     fillcolor='#DEAC80', color='#914F1E', fontcolor='#2C1A0E')
        elif state == start_fs:
            dot.node(name, shape='circle', style='filled',
                     fillcolor='#F7DCB9', color='#C07830', fontcolor='#2C1A0E')
        else:
            dot.node(name, shape='circle', style='filled',
                     fillcolor='#ffffff', color='#914F1E', fontcolor='#2C1A0E')

    dot.node('', shape='none', width='0', height='0')
    dot.edge('', state_name(start_fs), arrowhead='vee')

    # Group edges
    edge_labels = {}
    for state in dfa_states:
        for sym in symbols:
            dest = dfa_transitions[state][sym]
            key = (state_name(state), state_name(dest))
            edge_labels.setdefault(key, []).append(sym)

    for (src, dst), labels in edge_labels.items():
        dot.edge(src, dst, label=",".join(labels), color='#914F1E')

    svg_data = dot.pipe(format='svg').decode('utf-8')
    svg_start = svg_data.find('<svg')
    return svg_data[svg_start:]