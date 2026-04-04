# NFA → DFA Converter
### Theory of Automata & Formal Languages

A web-based visualization tool that demonstrates the **Subset Construction Method** used to convert a Nondeterministic Finite Automaton (NFA) into an equivalent Deterministic Finite Automaton (DFA).

---

## 📌 Project Overview

This application helps students understand the equivalence between nondeterministic and deterministic automata by providing:

- An interactive step-by-step conversion process
- Graphical representation of both the original NFA and the resulting DFA
- A clear visualization of how multiple NFA states combine into single DFA states

---

## ✨ Features

- **Step 1** → Define your NFA (states, symbols, start state, final states)
- **Step 2** → Fill in the NFA transition table interactively
- **Step 3** → Auto-generated DFA transition table using Subset Construction
- **Step 4** → Side-by-side visualization of NFA and DFA graphs
- 🔍 Zoom & drag support for graph exploration
- ☠️ Dead state (`d`) detection and visualization
- ✅ Input validation at every step

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python + Flask |
| Frontend | HTML + CSS + JavaScript |
| Graph Generation | Graphviz (Digraph) |
| Visualization | SVG |

---

## 📁 Project Structure

```
NFA_to_DFA/
│
├── main.py              ← NFA to DFA logic + graph generation
├── app.py               ← Flask routes
├── requirements.txt     ← Python dependencies
├── templates/
│   └── index.html       ← Main web interface
└── static/
    ├── style.css        ← Styling
    └── script.js        ← Frontend logic
```

---

## 🚀 How to Run Locally

**Step 1 — Clone the repository:**
```bash
git clone https://github.com/ArnavBansal2350/NFA_DFA_Converter.git
cd NFA_to_DFA
```

**Step 2 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 3 — Run the app:**
```bash
python app.py
```

**Step 4 — Open in browser:**
```
http://127.0.0.1:5000
```

---

## 📖 How to Use

1. Enter number of states, input symbols, start state and final states
2. Fill in the NFA transition table (use comma separated states e.g. `q0,q1` or `-` for no transition)
3. Click **Convert to DFA** to apply Subset Construction
4. View the generated DFA transition table
5. Click **Visualize Graphs** to see both NFA and DFA diagrams side by side
6. Use the 🔍 magnifier button to zoom and explore graphs

---

## 🧠 Algorithm Used

**Subset Construction (Powerset Construction)**
- Each DFA state represents a **subset of NFA states**
- Starting from the initial NFA state, we compute reachable state sets for each input symbol
- The process continues until no new subsets are discovered
- A DFA state is a **final state** if it contains at least one NFA final state
- Empty subsets are represented as **dead state `d`**

---

## 📚 Subject

> Theory of Automata & Formal Languages

---

## 👨‍💻 Author

**Arnav Bansal**  
GitHub: [@ArnavBansal2350](https://github.com/ArnavBansal2350)
