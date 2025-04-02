import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog, simpledialog
from typing import Set, Dict, Tuple, List, Optional
import json
import os
import re

# Try to import visualization libraries, but provide fallback if not available
try:
    import matplotlib.pyplot as plt
    import networkx as nx
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("Warning: Visualization libraries not found. Running in text-only mode.")
    print("To enable visualization, install the required packages:")
    print("pip install matplotlib networkx")

class NFA:
    def __init__(self, states: Set[str], alphabet: Set[str], transition_function: Dict[Tuple[str, str], Set[str]], 
                 start_state: str, final_states: Set[str]):
        self.states = {str(s) for s in states}
        self.alphabet = {str(s) for s in alphabet}
        self.transition_function = {(str(k[0]), str(k[1])): {str(s) for s in v} 
                                  for k, v in transition_function.items()}
        self.start_state = str(start_state)
        self.final_states = {str(s) for s in final_states}

    def epsilon_closure(self, state: str) -> Set[str]:
        state = str(state)
        closure = {state}
        stack = [state]
        while stack:
            current = stack.pop()
            for next_state in self.transition_function.get((str(current), 'ε'), set()):
                next_state = str(next_state)
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)
        return closure
    
    def to_dict(self):
        """Convert NFA to a dictionary for serialization"""
        return {
            "states": list(self.states),
            "alphabet": list(self.alphabet),
            "transition_function": {f"{k[0]},{k[1]}": list(v) for k, v in self.transition_function.items()},
            "start_state": self.start_state,
            "final_states": list(self.final_states)
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create an NFA from a dictionary"""
        states = set(data["states"])
        alphabet = set(data["alphabet"])
        transition_function = {}
        for k, v in data["transition_function"].items():
            state, symbol = k.split(',')
            transition_function[(state, symbol)] = set(v)
        start_state = data["start_state"]
        final_states = set(data["final_states"])
        return cls(states, alphabet, transition_function, start_state, final_states)
    
    def visualize(self, title="NFA Visualization"):
        """Create a visualization of the NFA using networkx and matplotlib"""
        if not VISUALIZATION_AVAILABLE:
            return None
            
        G = nx.DiGraph()
        
        # Add nodes
        for state in self.states:
            node_color = 'lightblue'
            if state == self.start_state:
                node_color = 'lightgreen'
            if state in self.final_states:
                node_color = 'lightcoral'
            if state == self.start_state and state in self.final_states:
                node_color = 'lightyellow'
                
            G.add_node(state, color=node_color)
        
        # Add edges with proper transition labels
        for (from_state, symbol), to_states in self.transition_function.items():
            for to_state in to_states:
                # Convert symbol to string and handle special characters
                symbol_str = str(symbol)
                if symbol_str == 'ε':
                    symbol_str = 'ε'
                elif symbol_str == '0':
                    symbol_str = '0'
                G.add_edge(from_state, to_state, label=symbol_str)
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G, k=1, iterations=50, seed=42)
        
        # Draw nodes
        node_colors = [G.nodes[node]['color'] for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700)
        
        # Draw edges with proper arrow style
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
        
        plt.title(title)
        plt.axis('off')
        
        return plt.gcf()

class DFA:
    def __init__(self, states: Set[frozenset], alphabet: Set[str], transition_function: Dict[Tuple[frozenset, str], frozenset], 
                 start_state: frozenset, final_states: Set[frozenset]):
        # Convert all state elements to strings
        self.states = {frozenset(str(s) for s in state) for state in states}
        self.alphabet = {str(s) for s in alphabet}
        self.transition_function = {
            (frozenset(str(s) for s in k[0]), str(k[1])): frozenset(str(s) for s in v)
            for k, v in transition_function.items()
        }
        self.start_state = frozenset(str(s) for s in start_state)
        self.final_states = {frozenset(str(s) for s in state) for state in final_states}
    
    def visualize(self, title="DFA Visualization"):
        """Create a visualization of the DFA using networkx and matplotlib"""
        if not VISUALIZATION_AVAILABLE:
            return None
            
        G = nx.DiGraph()
        
        # Add nodes
        for state in self.states:
            state_str = str(state)
            node_color = 'lightblue'
            if state == self.start_state:
                node_color = 'lightgreen'
            if state in self.final_states:
                node_color = 'lightcoral'
            if state == self.start_state and state in self.final_states:
                node_color = 'lightyellow'
                
            G.add_node(state_str, color=node_color)
        
        # Add edges
        for (from_state, symbol), to_state in self.transition_function.items():
            if to_state:  # Only add if there's a valid transition
                G.add_edge(str(from_state), str(to_state), label=symbol)
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes
        node_colors = [G.nodes[node]['color'] for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=700)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', arrows=True, arrowsize=20)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold')
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
        
        plt.title(title)
        plt.axis('off')
        
        return plt.gcf()
    
    def minimize(self):
        """Minimize the DFA using the partitioning algorithm"""
        # Step 1: Remove unreachable states
        reachable = {self.start_state}
        stack = [self.start_state]
        
        while stack:
            state = stack.pop()
            for symbol in self.alphabet:
                next_state = self.transition_function.get((state, symbol))
                if next_state and next_state not in reachable:
                    reachable.add(next_state)
                    stack.append(next_state)
        
        # Step 2: Find equivalent states
        # Initial partition: final and non-final states
        partitions = [reachable.intersection(self.final_states), 
                     reachable - self.final_states]
        partitions = [p for p in partitions if p]  # Remove empty partitions
        
        # Refine partitions
        while True:
            new_partitions = []
            for partition in partitions:
                if len(partition) <= 1:
                    new_partitions.append(partition)
                    continue
                
                # Split partition based on transitions
                splits = {}
                for state in partition:
                    key = tuple()
                    for symbol in self.alphabet:
                        next_state = self.transition_function.get((state, symbol))
                        # Find which partition contains the next state
                        for i, p in enumerate(partitions):
                            if next_state in p:
                                key += (i,)
                                break
                    
                    if key not in splits:
                        splits[key] = set()
                    splits[key].add(state)
                
                new_partitions.extend(splits.values())
            
            if len(new_partitions) == len(partitions):
                break
            partitions = new_partitions
        
        # Step 3: Build minimized DFA
        min_states = {frozenset(p) for p in partitions}
        min_start = None
        min_final = set()
        min_transitions = {}
        
        # Find start and final states
        for partition in partitions:
            if self.start_state in partition:
                min_start = frozenset(partition)
            if any(s in self.final_states for s in partition):
                min_final.add(frozenset(partition))
        
        # Build transitions
        for partition in partitions:
            state = next(iter(partition))  # Take any state from the partition
            for symbol in self.alphabet:
                next_state = self.transition_function.get((state, symbol))
                if next_state:
                    # Find which partition contains the next state
                    for p in partitions:
                        if next_state in p:
                            min_transitions[(frozenset(partition), symbol)] = frozenset(p)
                            break
        
        return DFA(min_states, self.alphabet, min_transitions, min_start, min_final)

def nfa_to_dfa(nfa: NFA) -> DFA:
    start_closure = nfa.epsilon_closure(str(nfa.start_state))
    dfa_states = {frozenset(str(s) for s in start_closure)}
    dfa_start_state = frozenset(str(s) for s in start_closure)
    dfa_final_states = set()
    dfa_transitions = {}
    unprocessed_states = [frozenset(str(s) for s in start_closure)]

    while unprocessed_states:
        current = unprocessed_states.pop()
        for symbol in nfa.alphabet:
            symbol = str(symbol)
            next_states = set()
            for state in current:
                state = str(state)
                next_states.update(nfa.transition_function.get((state, symbol), set()))
            closure = set()
            for state in next_states:
                state = str(state)
                closure.update(nfa.epsilon_closure(state))
            closure = frozenset(str(s) for s in closure)

            if closure and closure not in dfa_states:
                dfa_states.add(closure)
                unprocessed_states.append(closure)

            dfa_transitions[(current, symbol)] = closure

            if closure and any(str(s) in nfa.final_states for s in closure):
                dfa_final_states.add(closure)

    return DFA(dfa_states, nfa.alphabet, dfa_transitions, dfa_start_state, dfa_final_states)

class ThompsonNFA:
    """Class for building NFAs using Thompson's construction"""
    
    def __init__(self):
        self.state_counter = 0
        self.states = set()
        self.alphabet = set()
        self.transitions = {}
        self.start_state = None
        self.final_states = set()
    
    def new_state(self) -> str:
        """Create a new state and return its name"""
        state = str(f"q{self.state_counter}")
        self.state_counter += 1
        self.states.add(state)
        return state
    
    def add_transition(self, from_state: str, symbol: str, to_state: str):
        """Add a transition to the NFA"""
        from_state = str(from_state)
        symbol = str(symbol)
        to_state = str(to_state)
        
        key = (from_state, symbol)
        if key not in self.transitions:
            self.transitions[key] = set()
        self.transitions[key].add(to_state)
        if symbol != 'ε':
            self.alphabet.add(symbol)
    
    def basic_nfa(self, symbol: str) -> Tuple[str, str]:
        """Create a basic NFA for a single symbol"""
        symbol = str(symbol)
        start = self.new_state()
        end = self.new_state()
        self.add_transition(start, symbol, end)
        return start, end
    
    def concatenation(self, first: Tuple[str, str], second: Tuple[str, str]) -> Tuple[str, str]:
        """Concatenate two NFAs"""
        first = (str(first[0]), str(first[1]))
        second = (str(second[0]), str(second[1]))
        self.add_transition(first[1], 'ε', second[0])
        return first[0], second[1]
    
    def alternation(self, first: Tuple[str, str], second: Tuple[str, str]) -> Tuple[str, str]:
        """Create an alternation (union) of two NFAs"""
        first = (str(first[0]), str(first[1]))
        second = (str(second[0]), str(second[1]))
        start = self.new_state()
        end = self.new_state()
        
        self.add_transition(start, 'ε', first[0])
        self.add_transition(start, 'ε', second[0])
        self.add_transition(first[1], 'ε', end)
        self.add_transition(second[1], 'ε', end)
        
        return start, end
    
    def kleene_star(self, nfa: Tuple[str, str]) -> Tuple[str, str]:
        """Apply Kleene star to an NFA"""
        nfa = (str(nfa[0]), str(nfa[1]))
        start = self.new_state()
        end = self.new_state()
        
        self.add_transition(start, 'ε', nfa[0])
        self.add_transition(nfa[1], 'ε', nfa[0])
        self.add_transition(start, 'ε', end)
        self.add_transition(nfa[1], 'ε', end)
        
        return start, end
    
    def plus(self, nfa: Tuple[str, str]) -> Tuple[str, str]:
        """Apply plus (one or more) to an NFA"""
        nfa = (str(nfa[0]), str(nfa[1]))
        start = self.new_state()
        end = self.new_state()
        
        self.add_transition(start, 'ε', nfa[0])
        self.add_transition(nfa[1], 'ε', nfa[0])
        self.add_transition(nfa[1], 'ε', end)
        
        return start, end
    
    def question_mark(self, nfa: Tuple[str, str]) -> Tuple[str, str]:
        """Apply question mark (zero or one) to an NFA"""
        nfa = (str(nfa[0]), str(nfa[1]))
        start = self.new_state()
        end = self.new_state()
        
        self.add_transition(start, 'ε', nfa[0])
        self.add_transition(start, 'ε', end)
        self.add_transition(nfa[1], 'ε', end)
        
        return start, end
    
    def build_from_regex(self, regex: str) -> NFA:
        """Build an NFA from a regular expression using Thompson's construction"""
        # Reset the NFA
        self.__init__()
        
        # Process the regex character by character
        stack = []
        i = 0
        while i < len(regex):
            char = str(regex[i])  # Convert to string
            
            if char == '(':
                stack.append(char)
            elif char == ')':
                # Process until we find the matching '('
                temp_stack = []
                while stack and stack[-1] != '(':
                    temp_stack.append(stack.pop())
                if stack:
                    stack.pop()  # Remove '('
                
                # Process the subexpression
                result = None
                while temp_stack:
                    item = temp_stack.pop()
                    if isinstance(item, str) and item == '|':
                        # Handle alternation
                        second = stack.pop()
                        first = stack.pop()
                        result = self.alternation(first, second)
                    else:
                        if result is None:
                            result = item
                        else:
                            result = self.concatenation(result, item)
                
                if result:
                    stack.append(result)
            elif char in '*+?':
                if stack:
                    nfa = stack.pop()
                    if char == '*':
                        stack.append(self.kleene_star(nfa))
                    elif char == '+':
                        stack.append(self.plus(nfa))
                    else:  # ?
                        stack.append(self.question_mark(nfa))
            elif char == '|':
                stack.append(char)
            else:
                # Handle basic symbol
                nfa = self.basic_nfa(char)
                
                # If previous item was an NFA (not an operator), concatenate
                if stack and isinstance(stack[-1], tuple):
                    prev = stack.pop()
                    stack.append(self.concatenation(prev, nfa))
                else:
                    stack.append(nfa)
            
            i += 1
        
        # Process any remaining items in the stack
        result = None
        while stack:
            item = stack.pop()
            if isinstance(item, str) and item == '|':
                # Handle alternation
                second = result
                first = stack.pop()
                result = self.alternation(first, second)
            else:
                if result is None:
                    result = item
                else:
                    result = self.concatenation(item, result)
        
        if result:
            self.start_state = str(result[0])
            self.final_states = {str(result[1])}
            return NFA(self.states, self.alphabet, self.transitions, self.start_state, self.final_states)
        else:
            raise ValueError("Invalid regular expression")

class NFAToDFAConverter:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("NFA to DFA Converter")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")
        
        self.style = ttk.Style()
        self.style.configure("TLabel", background="#f0f0f0")
        self.style.configure("TButton", padding=5)
        self.style.configure("TLabelframe", background="#f0f0f0")
        self.style.configure("TLabelframe.Label", background="#f0f0f0", font=("Arial", 10, "bold"))
        self.style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff")
        self.style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        
        self.transitions = {}
        self.saved_configs = []
        self.config_dir = os.path.join(os.path.expanduser("~"), ".nfa_dfa_converter")
        self.ensure_config_dir()
        self.load_saved_configs()
        
        self.current_nfa = None
        self.current_dfa = None
        self.current_min_dfa = None
        
        self.create_widgets()
        self.root.mainloop()
    
    def ensure_config_dir(self):
        """Ensure the configuration directory exists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def load_saved_configs(self):
        """Load saved configurations from disk"""
        config_file = os.path.join(self.config_dir, "saved_configs.json")
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    self.saved_configs = json.load(f)
            except:
                self.saved_configs = []
    
    def save_configs(self):
        """Save configurations to disk"""
        config_file = os.path.join(self.config_dir, "saved_configs.json")
        with open(config_file, 'w') as f:
            json.dump(self.saved_configs, f)

    def create_widgets(self):
        # Create main container with paned window for resizable sections
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Left panel for input
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right panel for output and visualization
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)
        
        # Input Frame
        input_frame = ttk.LabelFrame(left_frame, text="NFA Definition", padding=10)
        input_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Create notebook for different input methods
        input_notebook = ttk.Notebook(input_frame)
        input_notebook.pack(fill="both", expand=True, pady=5)

        # Manual input tab
        manual_frame = ttk.Frame(input_notebook)
        input_notebook.add(manual_frame, text="Manual Input")

        # Thompson construction tab
        thompson_frame = ttk.Frame(input_notebook)
        input_notebook.add(thompson_frame, text="Thompson Construction")

        # Basic info frame for manual input
        basic_frame = ttk.Frame(manual_frame)
        basic_frame.pack(fill="x", pady=5)

        labels = [
            ("States (comma-separated):", "entry_states"),
            ("Alphabet (comma-separated):", "entry_alphabet"),
            ("Start State:", "entry_start"),
            ("Final States (comma-separated):", "entry_final")
        ]

        self.entries = {}
        for i, (label_text, entry_name) in enumerate(labels):
            frame = ttk.Frame(basic_frame)
            frame.pack(fill="x", pady=2)
            ttk.Label(frame, text=label_text, width=20).pack(side="left")
            entry = ttk.Entry(frame)
            entry.pack(side="left", fill="x", expand=True)
            self.entries[entry_name] = entry
            
            # Add event binding for states and alphabet
            if entry_name in ["entry_states", "entry_alphabet"]:
                entry.bind('<KeyRelease>', self.on_input_changed)

        # Transitions Frame for manual input
        trans_frame = ttk.LabelFrame(manual_frame, text="Transitions", padding=10)
        trans_frame.pack(fill="both", expand=True, pady=5)

        # Transition input controls
        trans_control_frame = ttk.Frame(trans_frame)
        trans_control_frame.pack(fill="x", pady=5)

        ttk.Label(trans_control_frame, text="From State:").pack(side="left", padx=2)
        self.from_state = ttk.Combobox(trans_control_frame, width=10)
        self.from_state.pack(side="left", padx=2)

        ttk.Label(trans_control_frame, text="Symbol:").pack(side="left", padx=2)
        self.symbol = ttk.Combobox(trans_control_frame, width=5)
        self.symbol.pack(side="left", padx=2)

        ttk.Label(trans_control_frame, text="To State(s):").pack(side="left", padx=2)
        self.to_states = ttk.Entry(trans_control_frame, width=15)
        self.to_states.pack(side="left", padx=2)

        add_btn = ttk.Button(trans_control_frame, text="Add Transition", command=self.add_transition)
        add_btn.pack(side="left", padx=5)
        
        delete_btn = ttk.Button(trans_control_frame, text="Delete Selected", command=self.delete_transition)
        delete_btn.pack(side="left", padx=5)

        # Transition display
        self.trans_tree = ttk.Treeview(trans_frame, columns=("from", "symbol", "to"), show="headings")
        self.trans_tree.heading("from", text="From State")
        self.trans_tree.heading("symbol", text="Symbol")
        self.trans_tree.heading("to", text="To State(s)")
        self.trans_tree.pack(fill="both", expand=True)
        
        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(trans_frame, orient="vertical", command=self.trans_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.trans_tree.configure(yscrollcommand=scrollbar.set)

        # Thompson construction frame
        thompson_input_frame = ttk.Frame(thompson_frame)
        thompson_input_frame.pack(fill="x", pady=5)

        ttk.Label(thompson_input_frame, text="Regular Expression:").pack(side="left", padx=5)
        self.regex_entry = ttk.Entry(thompson_input_frame, width=40)
        self.regex_entry.pack(side="left", padx=5)

        ttk.Button(thompson_input_frame, text="Build NFA", command=self.build_thompson_nfa).pack(side="left", padx=5)

        # Buttons Frame
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(btn_frame, text="Convert", command=self.convert).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Clear", command=self.clear).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save Configuration", command=self.save_current_config).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Load Configuration", command=self.load_config).pack(side="left", padx=5)
        
        # Right panel content
        # Notebook for tabs
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Text output tab
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="Text Output")
        
        self.result_text = scrolledtext.ScrolledText(text_frame, height=15, wrap=tk.WORD)
        self.result_text.pack(fill="both", expand=True)
        
        # Visualization tab (only if visualization is available)
        if VISUALIZATION_AVAILABLE:
            viz_frame = ttk.Frame(self.notebook)
            self.notebook.add(viz_frame, text="Visualization")
            
            # Visualization controls
            viz_control_frame = ttk.Frame(viz_frame)
            viz_control_frame.pack(fill="x", pady=5)
            
            ttk.Label(viz_control_frame, text="Select Automaton:").pack(side="left", padx=5)
            self.viz_type = ttk.Combobox(viz_control_frame, values=["NFA", "DFA", "Minimized DFA"], width=15)
            self.viz_type.set("NFA")
            self.viz_type.pack(side="left", padx=5)
            self.viz_type.bind("<<ComboboxSelected>>", self.update_visualization)
            
            # Canvas for visualization
            self.viz_canvas_frame = ttk.Frame(viz_frame)
            self.viz_canvas_frame.pack(fill="both", expand=True, pady=5)
        else:
            # Create a message frame for when visualization is not available
            viz_frame = ttk.Frame(self.notebook)
            self.notebook.add(viz_frame, text="Visualization")
            
            message_frame = ttk.Frame(viz_frame)
            message_frame.pack(fill="both", expand=True, pady=20)
            
            ttk.Label(message_frame, text="Visualization is not available", font=("Arial", 12, "bold")).pack(pady=10)
            ttk.Label(message_frame, text="To enable visualization, install the required packages:").pack()
            ttk.Label(message_frame, text="pip install matplotlib networkx").pack(pady=5)
            
            # Create a button to open the requirements file
            ttk.Button(message_frame, text="View Requirements", command=self.show_requirements).pack(pady=10)
        
        # Test string tab
        test_frame = ttk.Frame(self.notebook)
        self.notebook.add(test_frame, text="Test String")
        
        # Test string input
        test_input_frame = ttk.Frame(test_frame)
        test_input_frame.pack(fill="x", pady=5)
        
        ttk.Label(test_input_frame, text="Enter string to test:").pack(side="left", padx=5)
        self.test_string = ttk.Entry(test_input_frame, width=30)
        self.test_string.pack(side="left", padx=5)
        
        ttk.Button(test_input_frame, text="Test", command=self.test_string_accepted).pack(side="left", padx=5)
        
        # Test result
        self.test_result = scrolledtext.ScrolledText(test_frame, height=5, wrap=tk.WORD)
        self.test_result.pack(fill="both", expand=True, pady=5)

    def show_requirements(self):
        """Show the requirements.txt file"""
        try:
            with open("requirements.txt", "r") as f:
                requirements = f.read()
                
            dialog = tk.Toplevel(self.root)
            dialog.title("Requirements")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            ttk.Label(dialog, text="Required packages:").pack(pady=10)
            
            text = scrolledtext.ScrolledText(dialog, wrap=tk.WORD)
            text.pack(fill="both", expand=True, padx=10, pady=10)
            text.insert(tk.END, requirements)
            text.config(state=tk.DISABLED)
            
            ttk.Button(dialog, text="Close", command=dialog.destroy).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open requirements file: {str(e)}")

    def on_input_changed(self, event):
        """Update comboboxes when states or alphabet changes"""
        self.update_comboboxes()

    def update_comboboxes(self):
        """Update the comboboxes with current states and alphabet"""
        states = [s.strip() for s in self.entries["entry_states"].get().split(',') if s.strip()]
        alphabet = [s.strip() for s in self.entries["entry_alphabet"].get().split(',') if s.strip()]
        
        self.from_state['values'] = states
        self.symbol['values'] = alphabet + ['ε']  # Add epsilon as an option
        
        # Update the to_states entry with a combobox for multiple selection
        if hasattr(self, 'to_states_combo'):
            self.to_states_combo['values'] = states

    def add_transition(self):
        from_state = self.from_state.get().strip()
        symbol = self.symbol.get().strip()
        to_states = [s.strip() for s in self.to_states.get().split(',') if s.strip()]
        
        if not from_state or not symbol or not to_states:
            messagebox.showerror("Error", "All fields must be filled")
            return
            
        key = (from_state, symbol)
        if key in self.transitions:
            self.transitions[key].update(to_states)
        else:
            self.transitions[key] = set(to_states)
        
        # Update the treeview
        self.trans_tree.insert("", "end", values=(from_state, symbol, ", ".join(to_states)))
        
        # Clear input fields
        self.from_state.set('')
        self.symbol.set('')
        self.to_states.delete(0, tk.END)
    
    def delete_transition(self):
        """Delete the selected transition"""
        selected = self.trans_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a transition to delete")
            return
            
        for item in selected:
            values = self.trans_tree.item(item)['values']
            key = (values[0], values[1])
            if key in self.transitions:
                del self.transitions[key]
            self.trans_tree.delete(item)

    def save_current_config(self):
        """Save the current configuration"""
        if not self.validate_inputs():
            return
            
        try:
            states = set(s.strip() for s in self.entries["entry_states"].get().split(','))
            alphabet = set(s.strip() for s in self.entries["entry_alphabet"].get().split(','))
            start_state = self.entries["entry_start"].get().strip()
            final_states = set(s.strip() for s in self.entries["entry_final"].get().split(','))
            
            # Get transitions from treeview
            transitions = {}
            for child in self.trans_tree.get_children():
                values = self.trans_tree.item(child)['values']
                key = (values[0], values[1])
                to_states = set(s.strip() for s in values[2].split(','))
                transitions[key] = to_states
                
            nfa = NFA(states, alphabet, transitions, start_state, final_states)
            config_data = nfa.to_dict()
            
            # Ask for configuration name
            name = simpledialog.askstring("Save Configuration", "Enter a name for this configuration:")
            if not name:
                return
                
            # Add to saved configs
            self.saved_configs.append({"name": name, "data": config_data})
            self.save_configs()
            
            messagebox.showinfo("Success", f"Configuration '{name}' saved successfully!")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving configuration: {str(e)}")
    
    def load_config(self):
        """Load a saved configuration"""
        if not self.saved_configs:
            messagebox.showinfo("No Configurations", "No saved configurations found.")
            return
            
        # Create a dialog to select configuration
        dialog = tk.Toplevel(self.root)
        dialog.title("Load Configuration")
        dialog.geometry("300x400")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Select a configuration to load:").pack(pady=10)
        
        # Create a listbox with scrollbar
        frame = ttk.Frame(dialog)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set)
        listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=listbox.yview)
        
        # Add configurations to listbox
        for config in self.saved_configs:
            listbox.insert(tk.END, config["name"])
            
        def on_select():
            selection = listbox.curselection()
            if not selection:
                return
                
            config = self.saved_configs[selection[0]]
            self.load_config_data(config["data"])
            dialog.destroy()
            
        ttk.Button(dialog, text="Load", command=on_select).pack(pady=10)
    
    def load_config_data(self, config_data):
        """Load configuration data into the UI"""
        try:
            # Clear current data
            self.clear()
            
            # Set basic info
            self.entries["entry_states"].insert(0, ", ".join(config_data["states"]))
            self.entries["entry_alphabet"].insert(0, ", ".join(config_data["alphabet"]))
            self.entries["entry_start"].insert(0, config_data["start_state"])
            self.entries["entry_final"].insert(0, ", ".join(config_data["final_states"]))
            
            # Update comboboxes
            self.update_comboboxes()
            
            # Add transitions
            for k, v in config_data["transition_function"].items():
                state, symbol = k.split(',')
                self.trans_tree.insert("", "end", values=(state, symbol, ", ".join(v)))
                
            messagebox.showinfo("Success", "Configuration loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading configuration: {str(e)}")

    def validate_inputs(self) -> bool:
        try:
            states = set(s.strip() for s in self.entries["entry_states"].get().split(','))
            alphabet = set(s.strip() for s in self.entries["entry_alphabet"].get().split(','))
            start_state = self.entries["entry_start"].get().strip()
            final_states = set(s.strip() for s in self.entries["entry_final"].get().split(','))
            
            if not states or not alphabet or not start_state:
                raise ValueError("All fields must be filled")
            if start_state not in states:
                raise ValueError("Start state must be in states set")
            if not final_states.issubset(states):
                raise ValueError("Final states must be subset of states")
            if not self.transitions and not self.trans_tree.get_children():
                raise ValueError("At least one transition must be added")

            return True
        except Exception as e:
            messagebox.showerror("Input Error", str(e))
            return False

    def convert(self):
        if not self.validate_inputs():
            return

        try:
            states = set(s.strip() for s in self.entries["entry_states"].get().split(','))
            alphabet = set(s.strip() for s in self.entries["entry_alphabet"].get().split(','))
            start_state = self.entries["entry_start"].get().strip()
            final_states = set(s.strip() for s in self.entries["entry_final"].get().split(','))
            
            # Convert the transitions from the treeview to the required format
            transitions = {}
            for child in self.trans_tree.get_children():
                values = self.trans_tree.item(child)['values']
                key = (values[0], values[1])
                to_states = set(s.strip() for s in values[2].split(','))
                transitions[key] = to_states

            self.current_nfa = NFA(states, alphabet, transitions, start_state, final_states)
            self.current_dfa = nfa_to_dfa(self.current_nfa)
            self.current_min_dfa = self.current_dfa.minimize()

            result = "DFA Conversion Result:\n\n"
            result += f"States: {set(str(s) for s in self.current_dfa.states)}\n"
            result += f"Alphabet: {self.current_dfa.alphabet}\n"
            result += f"Start State: {str(self.current_dfa.start_state)}\n"
            result += f"Final States: {set(str(s) for s in self.current_dfa.final_states)}\n"
            result += "Transitions:\n"
            for (state, symbol), next_state in self.current_dfa.transition_function.items():
                result += f"  {str(state)} --{symbol}--> {str(next_state)}\n"
                
            result += "\nMinimized DFA:\n\n"
            result += f"States: {set(str(s) for s in self.current_min_dfa.states)}\n"
            result += f"Alphabet: {self.current_min_dfa.alphabet}\n"
            result += f"Start State: {str(self.current_min_dfa.start_state)}\n"
            result += f"Final States: {set(str(s) for s in self.current_min_dfa.final_states)}\n"
            result += "Transitions:\n"
            for (state, symbol), next_state in self.current_min_dfa.transition_function.items():
                result += f"  {str(state)} --{symbol}--> {str(next_state)}\n"

            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
            
            # Update visualization if available
            if VISUALIZATION_AVAILABLE:
                self.update_visualization()
            
        except Exception as e:
            messagebox.showerror("Conversion Error", f"Error during conversion: {str(e)}")
    
    def update_visualization(self, event=None):
        """Update the visualization based on the selected automaton type"""
        if not VISUALIZATION_AVAILABLE or not hasattr(self, 'viz_canvas_frame'):
            return
            
        # Clear previous visualization
        for widget in self.viz_canvas_frame.winfo_children():
            widget.destroy()
            
        if not self.current_nfa:
            ttk.Label(self.viz_canvas_frame, text="No automaton to visualize. Convert an NFA first.").pack(pady=20)
            return
            
        try:
            viz_type = self.viz_type.get()
            if viz_type == "NFA":
                fig = self.current_nfa.visualize("NFA Visualization")
            elif viz_type == "DFA":
                fig = self.current_dfa.visualize("DFA Visualization")
            else:  # Minimized DFA
                fig = self.current_min_dfa.visualize("Minimized DFA Visualization")
                
            if fig:
                canvas = FigureCanvasTkAgg(fig, master=self.viz_canvas_frame)
                canvas.draw()
                canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            ttk.Label(self.viz_canvas_frame, text=f"Error creating visualization: {str(e)}").pack(pady=20)
    
    def test_string_accepted(self):
        """Test if a string is accepted by the current DFA"""
        if not self.current_dfa:
            messagebox.showinfo("Info", "Please convert an NFA to DFA first")
            return
            
        test_str = self.test_string.get().strip()
        if not test_str:
            messagebox.showinfo("Info", "Please enter a string to test")
            return
            
        try:
            # Use the minimized DFA for testing
            current_state = self.current_min_dfa.start_state
            
            for symbol in test_str:
                if symbol not in self.current_min_dfa.alphabet:
                    self.test_result.delete(1.0, tk.END)
                    self.test_result.insert(tk.END, f"String contains invalid symbol: {symbol}")
                    return
                    
                current_state = self.current_min_dfa.transition_function.get((current_state, symbol))
                if not current_state:
                    self.test_result.delete(1.0, tk.END)
                    self.test_result.insert(tk.END, f"String rejected: No transition for symbol '{symbol}' from state {current_state}")
                    return
            
            if current_state in self.current_min_dfa.final_states:
                self.test_result.delete(1.0, tk.END)
                self.test_result.insert(tk.END, f"String accepted: {test_str}")
            else:
                self.test_result.delete(1.0, tk.END)
                self.test_result.insert(tk.END, f"String rejected: Final state not reached")
                
        except Exception as e:
            self.test_result.delete(1.0, tk.END)
            self.test_result.insert(tk.END, f"Error testing string: {str(e)}")

    def clear(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.trans_tree.delete(*self.trans_tree.get_children())
        self.transitions = {}
        self.result_text.delete(1.0, tk.END)
        self.test_result.delete(1.0, tk.END)
        self.test_string.delete(0, tk.END)
        
        # Clear combo boxes
        self.from_state.set('')
        self.symbol.set('')
        self.to_states.delete(0, tk.END)
        
        # Clear current automata
        self.current_nfa = None
        self.current_dfa = None
        self.current_min_dfa = None
        
        # Clear visualization if available
        if VISUALIZATION_AVAILABLE and hasattr(self, 'viz_canvas_frame'):
            for widget in self.viz_canvas_frame.winfo_children():
                widget.destroy()
            ttk.Label(self.viz_canvas_frame, text="No automaton to visualize").pack(pady=20)

    def build_thompson_nfa(self):
        """Build an NFA using Thompson's construction from a regular expression"""
        regex = self.regex_entry.get().strip()
        if not regex:
            messagebox.showerror("Error", "Please enter a regular expression")
            return
        
        try:
            # Create Thompson NFA
            thompson = ThompsonNFA()
            self.current_nfa = thompson.build_from_regex(regex)
            
            # Update the UI with the constructed NFA
            self.entries["entry_states"].delete(0, tk.END)
            self.entries["entry_states"].insert(0, ", ".join(sorted(self.current_nfa.states)))
            
            self.entries["entry_alphabet"].delete(0, tk.END)
            self.entries["entry_alphabet"].insert(0, ", ".join(sorted(self.current_nfa.alphabet)))
            
            self.entries["entry_start"].delete(0, tk.END)
            self.entries["entry_start"].insert(0, self.current_nfa.start_state)
            
            self.entries["entry_final"].delete(0, tk.END)
            self.entries["entry_final"].insert(0, ", ".join(sorted(self.current_nfa.final_states)))
            
            # Clear and update transitions
            self.trans_tree.delete(*self.trans_tree.get_children())
            for (from_state, symbol), to_states in self.current_nfa.transition_function.items():
                self.trans_tree.insert("", "end", values=(from_state, symbol, ", ".join(sorted(to_states))))
            
            # Update comboboxes
            self.update_comboboxes()
            
            messagebox.showinfo("Success", "NFA constructed successfully from regular expression")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error building NFA: {str(e)}")

if __name__ == "__main__":
    app = NFAToDFAConverter()