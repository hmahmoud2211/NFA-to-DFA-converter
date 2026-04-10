# NFA to DFA Converter — Full Project Report

## 1) Detailed Description of What the Project Does

This project is a desktop application that helps users define an NFA (Nondeterministic Finite Automaton), convert it to an equivalent DFA (Deterministic Finite Automaton), visualize both automata, and test whether strings are accepted.

It supports two ways to create an NFA:
1. **Manual definition** (states, alphabet, start state, final states, transitions).
2. **Regular expression input** using **Thompson’s Construction** to automatically build the NFA.

After building the NFA, the application runs subset construction to generate a DFA and shows:
- DFA states
- DFA alphabet
- start/final states
- transition table
- graphical visualization (if visualization libraries are installed)

---

## 2) What Does It Do?

### Core Features

- **Manual NFA Builder**
  - Users enter automaton components and transitions through GUI controls.
- **Regex to NFA (Thompson)**
  - Converts a regex into an NFA using operators:
    - Union: `|`
    - Concatenation (implicit)
    - Kleene star: `*`
    - One or more: `+`
    - Zero or one: `?`
    - Grouping: `(...)`
- **NFA to DFA Conversion**
  - Uses epsilon-closure and subset construction.
- **Transition Table Output**
  - Displays a formatted transition table for the generated DFA.
- **Visualization Tab**
  - Draws NFA/DFA graphs using `networkx` + `matplotlib` (optional feature).
- **String Testing**
  - Runs an input string through the DFA and reports accept/reject.
- **Save/Load Configurations**
  - Saves NFA definitions locally in JSON and reloads them later.

### Practical Use Cases

- Teaching and learning finite automata.
- Demonstrating NFA→DFA equivalence.
- Validating simple regular-language patterns.
- Visual classroom demonstration of transition graphs.

---

## 3) Input Format

The app accepts two input styles.

### A) Manual Input Format

#### Required fields
- **States**: comma-separated labels (example: `q0, q1, q2`)
- **Alphabet**: comma-separated symbols (example: `a, b`)
- **Start State**: one label from the states set (example: `q0`)
- **Final States**: comma-separated subset of states (example: `q2` or `q1, q2`)

#### Transition format
Each transition row contains:
- **From State**
- **Symbol** (alphabet symbol or `ε`)
- **To State(s)**: comma-separated list

Example transition rows:
- `(q0, a) -> q0, q1`
- `(q1, b) -> q2`
- `(q0, ε) -> q2`

### B) Thompson Construction Input Format

- A single **regular expression** string in the regex field.
- Supported operators and tokens:
  - Literals like `a`, `b`, `0`, `1`, etc.
  - `|`, `*`, `+`, `?`, and parentheses.

Example regex inputs:
- `(a|b)*abb`
- `a+b?`
- `(ab|ba)*`

---

## 4) Output Format

The project provides three output surfaces.

### A) Text Output (DFA Conversion Result)
Shows:
1. **States**
2. **Alphabet**
3. **Start State**
4. **Final States**
5. **Transition Table**

Table style:
- Fixed-width, row-by-row mapping from `(state, symbol)` to `next_state`.

### B) Visualization Output
If visualization dependencies are installed, the app displays:
- NFA graph
- DFA graph

Visual styling includes:
- Different node background colors for start/final states.
- Directed edges with labels.
- Curved edges to separate multiple transitions between same nodes.

### C) String Test Output
Given a string:
- Reports **accepted** if final state reached after consuming all symbols.
- Reports **rejected** otherwise.
- Reports error for invalid symbol outside DFA alphabet.

---

## 5) Inside Mechanism

### 5.1 Architecture Overview

Main components are:
- `NFA` class
- `DFA` class
- `ThompsonNFA` class
- `nfa_to_dfa()` function
- `NFAToDFAConverter` GUI controller class

### 5.2 NFA Model

`NFA` stores:
- set of states
- alphabet
- transition function: key `(state, symbol)` → set of destination states
- start state
- set of final states

It provides:
- `epsilon_closure(state)` for traversing `ε` transitions.
- serialization helpers (`to_dict()`, `from_dict()`).
- visualization method for plotting NFA.

### 5.3 Thompson Construction Engine

`ThompsonNFA` constructs an NFA from regex by composing fragments.

Implemented fragment operations:
- `basic_nfa(symbol)`
- `concatenation(first, second)`
- `alternation(first, second)`
- `kleene_star(nfa)`
- `plus(nfa)`
- `question_mark(nfa)`

Mechanism summary:
- Reads regex character-by-character.
- Uses a stack for symbols/operators/grouping.
- Builds and merges NFA fragments until one final fragment remains.

### 5.4 NFA → DFA Conversion (Subset Construction)

The conversion algorithm:
1. Compute epsilon-closure of NFA start state.
2. Use that closure as initial DFA state.
3. Iteratively process unvisited DFA states:
   - For each symbol (except `ε`), collect reachable states.
   - Expand each reachable state using epsilon-closure.
   - Create new DFA states as needed.
4. Mark a DFA state as final if it contains any NFA final state.
5. Build deterministic transition map.

Implementation detail:
- Composite DFA states are represented as `frozenset` during computation.
- Then remapped to simplified labels (`q0`, `q1`, …) for display.

### 5.5 GUI Workflow

The `NFAToDFAConverter` class manages:
- Widget creation and layout (`tkinter`, `ttk` notebook/tabs).
- Validation of inputs before conversion.
- Transition table insertion/removal.
- Save/load JSON configurations.
- Visualization rendering on a Tk canvas.
- String acceptance test execution.

### 5.6 Persistence

Saved configurations are written to:
- user home folder: `.nfa_dfa_converter/saved_configs.json`

Stored data includes all NFA components and transitions.

---

## 6) Programming Language, Tools & Libraries Used

### Programming Language
- **Python 3**

### Built-in/Standard Modules
- `tkinter` (GUI)
- `typing` (type hints)
- `json` (serialization)
- `os` (filesystem paths)
- `re` (regex utility)
- `subprocess`, `sys` (installation script)

### Third-Party Libraries
- `matplotlib` — plotting figures and embedding chart canvas in GUI
- `networkx` — graph model and graph drawing helpers
- `numpy` — numerical backend dependency used by plotting/graph operations

### Project Files
- [NFA_DFA_Converter.py](NFA_DFA_Converter.py): main application logic + GUI
- [install.py](install.py): dependency installer helper
- [requirements.txt](requirements.txt): package versions
- [README.md](README.md): project overview

---

## 7) Images of the Project with Output

> Note: This environment cannot capture GUI screenshots directly. The following image slots and captions are ready for your final report.

### Image 1 — Manual NFA Input Screen
- Capture the **Manual Input** tab after filling states, alphabet, start/final states and several transitions.
- Suggested caption: “Manual NFA definition with transitions before conversion.”

### Image 2 — DFA Text Output
- Capture the **Text Output** tab after pressing **Convert**.
- Ensure the conversion summary and transition table are visible.
- Suggested caption: “Generated DFA details and transition table.”

### Image 3 — NFA Visualization
- Capture **Visualization** tab with selector on **NFA**.
- Suggested caption: “Graphical representation of the source NFA.”

### Image 4 — DFA Visualization
- Capture **Visualization** tab with selector on **DFA**.
- Suggested caption: “Graphical representation of the converted DFA.”

### Image 5 — String Test Result
- Capture **Test String** tab after testing an accepted and rejected sample.
- Suggested caption: “String acceptance/rejection result using generated DFA.”

---

## 8) Summary

This project delivers a complete educational automata workflow in one desktop tool:
- define/build NFA,
- convert to DFA,
- visualize structures,
- and test string acceptance.

It combines formal-language concepts with a practical and user-friendly GUI, making it suitable for coursework, demonstrations, and self-learning.
