// ===========================
// GLOBAL STATE
// ===========================
let appData = {
  states: [],
  symbols: [],
  start_state: '',
  final_states: [],
  nfa: {},
  dfa_table: [],
  nfa_svg: '',
  dfa_svg: ''
};

// ===========================
// STEP INDICATORS
// ===========================
function updateSteps(activeStep) {
  for (let i = 1; i <= 4; i++) {
    const dot = document.getElementById(`dot${i}`);
    dot.classList.remove('active', 'done');
    if (i < activeStep) dot.classList.add('done');
    else if (i === activeStep) dot.classList.add('active');
  }
}

// ===========================
// PHASE NAVIGATION
// ===========================
function showPhase(n) {
  document.querySelectorAll('.phase').forEach(p => p.classList.remove('active'));
  document.getElementById(`phase${n}`).classList.add('active');
  updateSteps(n);
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function goBack(n) {
  showPhase(n);
}

// ===========================
// HELPER: SHOW ERROR
// ===========================
function showError(id, msg) {
  const el = document.getElementById(id);
  el.textContent = msg;
  el.style.display = 'block';
}

function hideError(id) {
  document.getElementById(id).style.display = 'none';
}

// ===========================
// PHASE 1 → PHASE 2
// Generate NFA Transition Table
// ===========================
function generateNFATable() {
  hideError('form-error');

  const numStates = parseInt(document.getElementById('num_states').value);
  const symbolsRaw = document.getElementById('symbols_input').value.trim();
  const startState = document.getElementById('start_state').value.trim();
  const finalStatesRaw = document.getElementById('final_states').value.trim();

  // Validation
  if (!numStates || numStates < 1) return showError('form-error', 'Please enter a valid number of states (minimum 1).');
  if (!symbolsRaw) return showError('form-error', 'Please enter at least one input symbol.');
  if (!startState) return showError('form-error', 'Please enter the start state.');
  if (!finalStatesRaw) return showError('form-error', 'Please enter at least one final state.');

  const states = Array.from({ length: numStates }, (_, i) => `q${i}`);
  const symbols = symbolsRaw.split(/\s+/).filter(Boolean);
  const finalStates = finalStatesRaw.split(/\s+/).filter(Boolean);

  if (!states.includes(startState))
    return showError('form-error', `Start state "${startState}" is not valid. States are: ${states.join(', ')}`);

  for (const fs of finalStates) {
    if (!states.includes(fs))
      return showError('form-error', `Final state "${fs}" is not valid. States are: ${states.join(', ')}`);
  }

  // Store
  appData.states = states;
  appData.symbols = symbols;
  appData.start_state = startState;
  appData.final_states = finalStates;

  // Build table
  const wrapper = document.getElementById('nfa_table_wrapper');
  let html = `<table><thead><tr>
    <th>State</th>`;
  for (const sym of symbols) html += `<th>δ(q, ${sym})</th>`;
  html += `</tr></thead><tbody>`;

  for (const state of states) {
    const isStart = state === startState;
    const isFinal = finalStates.includes(state);
    let stateLabel = state;
 
    html += `<tr>
      <td>
        <div class="state-cell">
          ${isStart ? '<span class="badge start-badge">→</span>' : ''}
          ${isFinal ? '<span class="badge final-badge">★</span>' : ''}
          ${stateLabel}
        </div>
      </td>`;

    for (const sym of symbols) {
      html += `<td><input
        class="nfa-input"
        id="nfa_${state}_${sym}"
        type="text"
        placeholder="-"
        autocomplete="off"
      /></td>`;
    }
    html += `</tr>`;
  }
  html += `</tbody></table>`;
  wrapper.innerHTML = html;

  showPhase(2);
}

// ===========================
// PARSE NFA INPUT
// ===========================
function parseNFAInput() {
  const nfa = {};
  let valid = true;
  let errorMsg = '';

  for (const state of appData.states) {
    nfa[state] = {};
    for (const sym of appData.symbols) {
      const input = document.getElementById(`nfa_${state}_${sym}`);
      const val = input.value.trim();
      input.classList.remove('error-field');

      if (!val || val === '-') {
        nfa[state][sym] = [];
      } else {
        const parts = val.split(',').map(s => s.trim()).filter(Boolean);
        const invalid = parts.filter(p => !appData.states.includes(p));
        if (invalid.length > 0) {
          input.classList.add('error-field');
          errorMsg = `Invalid state(s): "${invalid.join(', ')}" in δ(${state}, ${sym}). Valid states: ${appData.states.join(', ')}`;
          valid = false;
        }
        nfa[state][sym] = parts;
      }
    }
  }

  return { valid, nfa, errorMsg };
}

// ===========================
// PHASE 2 → PHASE 3
// Convert NFA to DFA
// ===========================
async function convertNFA() {
  hideError('nfa-error');

  const { valid, nfa, errorMsg } = parseNFAInput();
  if (!valid) return showError('nfa-error', errorMsg);

  appData.nfa = nfa;

  // Show loading state
  const btn = document.querySelector('#phase2 .btn-primary');
  btn.textContent = 'Converting...';
  btn.disabled = true;

  try {
    const response = await fetch('/convert', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        states: appData.states,
        symbols: appData.symbols,
        start_state: appData.start_state,
        final_states: appData.final_states,
        nfa: appData.nfa
      })
    });

    const data = await response.json();

    if (!data.success) {
      showError('nfa-error', data.error);
      return;
    }

    appData.dfa_table = data.dfa_table;
    appData.nfa_svg = data.nfa_svg;
    appData.dfa_svg = data.dfa_svg;

    renderDFATable(data.dfa_table, data.symbols);
    showPhase(3);

  } catch (err) {
    showError('nfa-error', 'Server error. Make sure Flask is running.');
  } finally {
    btn.innerHTML = 'Convert to DFA <span class="btn-arrow">→</span>';
    btn.disabled = false;
  }
}

// ===========================
// RENDER DFA TABLE
// ===========================
function renderDFATable(dfaTable, symbols) {
  const wrapper = document.getElementById('dfa_table_wrapper');
  let html = `<table><thead><tr><th>DFA State</th>`;
  for (const sym of symbols) html += `<th>${sym}</th>`;
  html += `</tr></thead><tbody>`;

  const sortedTable = [...dfaTable].sort((a, b) => (a.state === 'd') - (b.state === 'd'));
  for (const row of sortedTable) {
    const isDead = row.state === 'd';
    const rowClass = row.is_final ? 'final-row' : (row.is_start ? 'start-row' : '');

    html += `<tr class="${rowClass}">
      <td>
        <div class="state-cell">
          ${row.is_start ? '<span class="badge start-badge">→</span>' : ''}
          ${row.is_final ? '<span class="badge final-badge">★</span>' : ''}
          ${isDead ? '<span class="badge dead-badge">d</span>' : row.state}
        </div>
      </td>`;

    for (const sym of symbols) {
      const dest = row.transitions[sym];
      const cellClass = (dest === 'd' || isDead) ? 'dead-cell' : '';
      html += `<td class="${cellClass}">${dest === 'd' || isDead ? 'd' : dest}</td>`;
    }
    html += `</tr>`;
  }

  html += `</tbody></table>`;
  wrapper.innerHTML = html;
}

// ===========================
// PHASE 3 → PHASE 4
// Show Graphs
// ===========================
function showGraphs() {
  document.getElementById('nfa_graph').innerHTML = appData.nfa_svg || '<p>No graph available</p>';
  document.getElementById('dfa_graph').innerHTML = appData.dfa_svg || '<p>No graph available</p>';

  document.querySelectorAll('#nfa_graph svg, #dfa_graph svg').forEach(svg => {
    svg.removeAttribute('width');
    svg.removeAttribute('height');
    svg.style.maxWidth = '100%';
    svg.style.height = 'auto';
  });

  // Re-add zoom buttons
  ['nfa_graph', 'dfa_graph'].forEach(id => {
    const btn = document.createElement('button');
    btn.className = 'zoom-btn';
    btn.innerHTML = '🔍';
    btn.onclick = () => openModal(id);
    document.getElementById(id).appendChild(btn);
  });

  showPhase(4);
}

// ===========================
// RESET
// ===========================
function resetAll() {
  appData = { states: [], symbols: [], start_state: '', final_states: [], nfa: {}, dfa_table: [], nfa_svg: '', dfa_svg: '' };
  document.getElementById('num_states').value = '';
  document.getElementById('symbols_input').value = '';
  document.getElementById('start_state').value = '';
  document.getElementById('final_states').value = '';
  document.getElementById('nfa_table_wrapper').innerHTML = '';
  document.getElementById('dfa_table_wrapper').innerHTML = '';
  document.getElementById('nfa_graph').innerHTML = '';
  document.getElementById('dfa_graph').innerHTML = '';
  hideError('form-error');
  hideError('nfa-error');
  showPhase(1);
}

// ===========================
// MODAL ZOOM & PAN
// ===========================
let modalScale = 1, modalPanX = 0, modalPanY = 0;
let isPanning = false, startX = 0, startY = 0;
let modalSvg = null;

function openModal(graphId) {
  const src = document.querySelector(`#${graphId} svg`);
  if (!src) return;

  const clone = src.cloneNode(true);
  clone.removeAttribute('width');
  clone.removeAttribute('height');
  clone.style.width = '800px';
  clone.style.height = '600px';

  const body = document.getElementById('modal-body');
  body.innerHTML = '';
  body.appendChild(clone);
  modalSvg = clone;

  modalScale = 1; modalPanX = 0; modalPanY = 0;
  applyModalTransform();

  document.getElementById('graph-modal').classList.add('active');

  // Drag
  body.addEventListener('mousedown', startPan);
  window.addEventListener('mousemove', doPan);
  window.addEventListener('mouseup', stopPan);
  body.addEventListener('wheel', wheelZoom, { passive: false });
}

function closeModal() {
  document.getElementById('graph-modal').classList.remove('active');
  const body = document.getElementById('modal-body');
  body.removeEventListener('mousedown', startPan);
  window.removeEventListener('mousemove', doPan);
  window.removeEventListener('mouseup', stopPan);
  body.removeEventListener('wheel', wheelZoom);
}

function applyModalTransform() {
  if (modalSvg) modalSvg.style.transform = `translate(${modalPanX}px, ${modalPanY}px) scale(${modalScale})`;
}

function zoomIn()  { modalScale = Math.min(modalScale * 1.2, 8); applyModalTransform(); }
function zoomOut() { modalScale = Math.max(modalScale * 0.8, 0.2); applyModalTransform(); }
function resetZoom() { modalScale = 1; modalPanX = 0; modalPanY = 0; applyModalTransform(); }

function wheelZoom(e) {
  e.preventDefault();
  const delta = e.deltaY > 0 ? 0.9 : 1.1;
  modalScale = Math.min(Math.max(modalScale * delta, 0.2), 8);
  applyModalTransform();
}

function startPan(e) {
  isPanning = true;
  startX = e.clientX - modalPanX;
  startY = e.clientY - modalPanY;
  e.currentTarget.style.cursor = 'grabbing';
}

function doPan(e) {
  if (!isPanning) return;
  modalPanX = e.clientX - startX;
  modalPanY = e.clientY - startY;
  applyModalTransform();
}

function stopPan() {
  isPanning = false;
  const body = document.getElementById('modal-body');
  if (body) body.style.cursor = 'grab';
}