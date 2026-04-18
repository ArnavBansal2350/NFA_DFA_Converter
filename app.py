import os
from flask import Flask, render_template, request, jsonify
from main import nfa_to_dfa, get_dfa_table, generate_nfa_graph, generate_dfa_graph, get_conversion_steps

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/generate_nfa_graph', methods=['POST'])
def generate_nfa_graph_route():
    """Generate NFA graph from user input and return SVG."""
    data = request.json
    states = data['states']
    symbols = data['symbols']
    start_state = data['start_state']
    final_states = set(data['final_states'])
    nfa = {s: {sym: set(v) for sym, v in trans.items()} for s, trans in data['nfa'].items()}

    try:
        svg = generate_nfa_graph(states, symbols, start_state, final_states, nfa)
        return jsonify({'success': True, 'svg': svg})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/convert', methods=['POST'])
def convert():
    """Convert NFA to DFA and return table + graphs."""
    data = request.json

    states = data['states']
    symbols = data['symbols']
    start_state = data['start_state']
    final_states = set(data['final_states'])
    nfa = {s: {sym: set(v) for sym, v in trans.items()} for s, trans in data['nfa'].items()}

    # Validate
    if start_state not in states:
        return jsonify({'success': False, 'error': f'Start state "{start_state}" not in states list.'})
    for fs in final_states:
        if fs not in states:
            return jsonify({'success': False, 'error': f'Final state "{fs}" not in states list.'})

    try:
        dfa_states, dfa_transitions, dfa_final_states = nfa_to_dfa(
            states, symbols, start_state, final_states, nfa
        )

        dfa_table = get_dfa_table(dfa_states, dfa_transitions, dfa_final_states, symbols, start_state)

        nfa_svg = generate_nfa_graph(states, symbols, start_state, final_states, nfa)
        dfa_svg = generate_dfa_graph(dfa_states, dfa_transitions, dfa_final_states, symbols, start_state)

        steps = get_conversion_steps(states, symbols, start_state, final_states, nfa)

        return jsonify({
            'success': True,
            'dfa_table': dfa_table,
            'symbols': symbols,
            'nfa_svg': nfa_svg,
            'dfa_svg': dfa_svg,
            'steps': steps
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)