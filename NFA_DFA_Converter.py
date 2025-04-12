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
        
        # Add nodes with improved styling
        for state in self.states:
            if state == self.start_state:
                node_color = '#C8E6C9'  # Light green for start state
            elif state in self.final_states:
                node_color = '#FFCDD2'  # Light red for final states
            else:
                node_color = 'white'  # White for other states
                
            G.add_node(state, color=node_color)
        
        # Add edges with proper transition labels
        edge_colors = []
        edge_styles = []
        
        # Sort transitions for consistent visualization
        sorted_transitions = sorted(self.transition_function.items(), 
                                 key=lambda x: (x[0][0], x[0][1]))
        
        # Track edges between same nodes to adjust their curves
        edge_count = {}
        
        for (from_state, symbol), to_states in sorted_transitions:
            for to_state in to_states:
                # Create a unique edge key
                edge_key = (from_state, to_state)
                if edge_key not in edge_count:
                    edge_count[edge_key] = 0
                edge_count[edge_key] += 1
                
                # Calculate curve based on number of edges between these nodes
                curve = 0.2 * edge_count[edge_key]
                
                # Add the edge with the exact symbol from transition function
                G.add_edge(from_state, to_state, 
                          label=str(symbol),  # Convert symbol to string to ensure proper display
                          connectionstyle=f'arc3,rad={curve}')
                
                # Set edge style based on symbol type
                if symbol == 'ε':
                    edge_colors.append('#9E9E9E')  # Gray for ε-transitions
                    edge_styles.append('dashed')
                else:
                    edge_colors.append('#2196F3')  # Blue for normal transitions
                    edge_styles.append('solid')
        
        # Create the plot
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw nodes
        node_colors = [G.nodes[node]['color'] for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, 
                             node_color=node_colors, 
                             node_size=1000,
                             edgecolors='#424242', 
                             linewidths=2)
        
        # Draw edges with different styles for ε-transitions
        edges = G.edges()
        for i, (u, v) in enumerate(edges):
            edge_style = edge_styles[i]
            edge_color = edge_colors[i]
            nx.draw_networkx_edges(G, pos,
                                 edgelist=[(u, v)],
                                 edge_color=edge_color,
                                 style=edge_style,
                                 arrows=True,
                                 arrowsize=20,
                                 width=2,
                                 connectionstyle=G.edges[u, v]['connectionstyle'])
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, 
                              font_size=14, 
                              font_weight='bold')
        
        # Draw edge labels with better positioning and background
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos,
                                   edge_labels=edge_labels,
                                   font_size=12,
                                   font_weight='bold',
                                   bbox=dict(facecolor='white', 
                                           edgecolor='none', 
                                           alpha=0.8,
                                           pad=0.5))
        
        plt.title(title, fontsize=16, pad=20)
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
        
        # Helper function to format state labels
        def format_state_label(state):
            if isinstance(state, frozenset):
                return '{' + ', '.join(sorted(state)) + '}'
            return str(state)
        
        # Add nodes with improved styling
        for state in self.states:
            node_color = '#E1F5FE'  # Light blue
            if state == self.start_state:
                node_color = '#C8E6C9'  # Light green
            if state in self.final_states:
                node_color = '#FFCDD2'  # Light red
            if state == self.start_state and state in self.final_states:
                node_color = '#FFF9C4'  # Light yellow
                
            # Use the formatted label for the node
            state_label = format_state_label(state)
            G.add_node(state_label, color=node_color)
        
        # Add edges with proper transition labels
        edge_colors = []
        edge_styles = []
        for (from_state, symbol), to_state in self.transition_function.items():
            if to_state:  # Only add if there's a valid transition
                from_label = format_state_label(from_state)
                to_label = format_state_label(to_state)
                G.add_edge(from_label, to_label, label=symbol)
                edge_colors.append('#2196F3')  # Blue for transitions
                edge_styles.append('solid')
        
        # Create the plot
        plt.figure(figsize=(12, 8))
        
        # Use a more spread out layout
        pos = nx.spring_layout(G, k=2, iterations=50)
        
        # Draw nodes
        node_colors = [G.nodes[node]['color'] for node in G.nodes()]
        nx.draw_networkx_nodes(G, pos, 
                             node_color=node_colors,
                             node_size=3000,  # Larger nodes
                             edgecolors='#424242',
                             linewidths=2)
        
        # Draw edges with different styles
        edges = G.edges()
        for i, (u, v) in enumerate(edges):
            edge_style = edge_styles[i]
            edge_color = edge_colors[i]
            nx.draw_networkx_edges(G, pos,
                                 edgelist=[(u, v)],
                                 edge_color=edge_color,
                                 style=edge_style,
                                 arrows=True,
                                 arrowsize=20,
                                 width=2,
                                 arrowstyle='->',
                                 connectionstyle='arc3,rad=0.2')
        
        # Draw labels with word wrapping for long state names
        labels = {}
        for node in G.nodes():
            # Split long labels into multiple lines
            label = str(node)
            if len(label) > 20:
                words = label.split(', ')
                new_label = ''
                line = ''
                for word in words:
                    if len(line + word) > 20:
                        new_label += line + '\n'
                        line = word + ', '
                    else:
                        line += word + ', '
                new_label += line.rstrip(', ')
                labels[node] = new_label
            else:
                labels[node] = label
                
        nx.draw_networkx_labels(G, pos,
                              labels=labels,
                              font_size=10,
                              font_weight='bold')
        
        # Draw edge labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos,
                                   edge_labels=edge_labels,
                                   font_size=12,
                                   font_weight='bold')
        
        plt.title(title, fontsize=16, pad=20)
        plt.axis('off')
        
        return plt.gcf()
    
    def minimize(self):
        """Minimize the DFA using Hopcroft's algorithm"""
        return minimize_dfa(self)

def nfa_to_dfa(nfa: NFA) -> DFA:
    """Convert NFA to DFA using subset construction algorithm"""
    # Get epsilon closure of start state
    start_closure = nfa.epsilon_closure(nfa.start_state)
    dfa_states = {frozenset(start_closure)}
    dfa_start_state = frozenset(start_closure)
    dfa_final_states = set()
    dfa_transitions = {}
    unprocessed_states = [frozenset(start_closure)]

    # If any state in epsilon closure of start state is final, add to DFA final states
    if any(state in nfa.final_states for state in start_closure):
        dfa_final_states.add(frozenset(start_closure))

    while unprocessed_states:
        current_states = unprocessed_states.pop(0)
        
        # For each input symbol (excluding epsilon)
        for symbol in nfa.alphabet:
            if symbol == 'ε':
                continue
                
            next_states = set()
            # For each NFA state in the current DFA state
            for state in current_states:
                # Get states reachable by symbol
                if (state, symbol) in nfa.transition_function:
                    # Get direct transitions
                    direct_states = nfa.transition_function[(state, symbol)]
                    # For each direct state, add its epsilon closure
                    for direct_state in direct_states:
                        next_states.update(nfa.epsilon_closure(direct_state))

            if next_states:  # Only add if there are reachable states
                next_state_set = frozenset(next_states)
                
                # Add to DFA states if new
                if next_state_set not in dfa_states:
                    dfa_states.add(next_state_set)
                    unprocessed_states.append(next_state_set)
                    # Check if this new state should be final
                    if any(state in nfa.final_states for state in next_states):
                        dfa_final_states.add(next_state_set)
                
                # Add transition
                dfa_transitions[(current_states, symbol)] = next_state_set

    # Remove epsilon from alphabet
    dfa_alphabet = {s for s in nfa.alphabet if s != 'ε'}

    # Simplify state names for better readability
    state_map = {}
    for i, state in enumerate(dfa_states):
        state_map[state] = f"q{i}"

    # Create new DFA with simplified state names
    new_states = set(state_map.values())
    new_transitions = {}
    for (state, symbol), next_state in dfa_transitions.items():
        new_transitions[(state_map[state], symbol)] = state_map[next_state]
    new_start = state_map[dfa_start_state]
    new_finals = {state_map[s] for s in dfa_final_states}

    return DFA(new_states, dfa_alphabet, new_transitions, new_start, new_finals)

def minimize_dfa(dfa: DFA) -> DFA:
    """Minimize DFA using Hopcroft's algorithm"""
    # Step 1: Create initial partition (final and non-final states)
    final = frozenset(dfa.final_states)
    non_final = frozenset(s for s in dfa.states if s not in dfa.final_states)
    partitions = {final, non_final} if non_final else {final}
    
    # Remove empty sets
    partitions = {p for p in partitions if p}
    
    # Step 2: Refine partitions until no more refinement is possible
    while True:
        new_partitions = set()
        changed = False
        
        for partition in partitions:
            # For each symbol in the alphabet
            for symbol in dfa.alphabet:
                # Group states by their transitions
                transition_groups = {}
                for state in partition:
                    # Find which partition contains the destination state
                    dest_state = dfa.transition_function.get((state, symbol))
                    if dest_state is not None:
                        dest_partition = None
                        for p in partitions:
                            if dest_state in p:
                                dest_partition = p
                                break
                        # Group states by their destination partitions
                        key = dest_partition
                        if key not in transition_groups:
                            transition_groups[key] = set()
                        transition_groups[key].add(state)
                
                # If states were split into multiple groups
                if len(transition_groups) > 1:
                    new_partitions.update(frozenset(group) for group in transition_groups.values())
                    changed = True
                    break
            if changed:
                # Add remaining partitions
                new_partitions.update(p for p in partitions if p != partition)
                break
        
        if not changed:
            break
            
        partitions = new_partitions
    
    # Step 3: Create the minimized DFA
    # Create a mapping from old states to their partition representative
    state_map = {}
    for i, partition in enumerate(partitions):
        rep = f"q{i}"  # Use simple state names
        for state in partition:
            state_map[state] = rep
    
    # Create new transition function
    new_transitions = {}
    for (state, symbol), next_state in dfa.transition_function.items():
        new_state = state_map[state]
        new_next = state_map[next_state]
        new_transitions[(new_state, symbol)] = new_next
    
    # Create new states set
    new_states = set(state_map.values())
    
    # Map start and final states
    new_start = state_map[dfa.start_state]
    new_finals = {state_map[s] for s in dfa.final_states}
    
    return DFA(new_states, dfa.alphabet, new_transitions, new_start, new_finals)

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
        self.root.configure(bg="#f5f5f5")
        
        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Use clam theme for modern look
        
        # Configure colors
        self.style.configure("TFrame", background="#f5f5f5")
        self.style.configure("TLabel", background="#f5f5f5", font=("Segoe UI", 10))
        self.style.configure("TButton", 
                           background="#2196F3", 
                           foreground="white",
                           padding=10,
                           font=("Segoe UI", 10))
        self.style.configure("TLabelframe", 
                           background="#f5f5f5",
                           borderwidth=0)
        self.style.configure("TLabelframe.Label", 
                           background="#f5f5f5",
                           font=("Segoe UI", 11, "bold"))
        self.style.configure("Treeview", 
                           background="white",
                           fieldbackground="white",
                           font=("Segoe UI", 10))
        self.style.configure("Treeview.Heading", 
                           font=("Segoe UI", 10, "bold"))
        self.style.configure("TNotebook", 
                           background="#f5f5f5",
                           borderwidth=0)
        self.style.configure("TNotebook.Tab", 
                           background="#e0e0e0",
                           padding=[10, 5],
                           font=("Segoe UI", 10))
        self.style.map("TNotebook.Tab",
                      background=[("selected", "#2196F3")],
                      foreground=[("selected", "white")])
        
        # Configure hover effects for buttons
        self.style.map("TButton",
                      background=[("active", "#1976D2")],
                      foreground=[("active", "white")])
        
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
        main_paned.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left panel for input
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, weight=1)
        
        # Right panel for output and visualization
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        # Input Frame
        input_frame = ttk.LabelFrame(left_frame, text="NFA Definition", padding=15)
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
        basic_frame.pack(fill="x", pady=10)

        # Create a modern input style
        input_style = {"width": 30, "font": ("Segoe UI", 10)}
        label_style = {"font": ("Segoe UI", 10, "bold")}

        labels = [
            ("States (comma-separated):", "entry_states"),
            ("Alphabet (comma-separated):", "entry_alphabet"),
            ("Start State:", "entry_start"),
            ("Final States (comma-separated):", "entry_final")
        ]

        self.entries = {}
        for i, (label_text, entry_name) in enumerate(labels):
            frame = ttk.Frame(basic_frame)
            frame.pack(fill="x", pady=5)
            ttk.Label(frame, text=label_text, **label_style).pack(side="left", padx=(0, 10))
            entry = ttk.Entry(frame, **input_style)
            entry.pack(side="left", fill="x", expand=True)
            self.entries[entry_name] = entry

            # Add event binding for states and alphabet
            if entry_name in ["entry_states", "entry_alphabet"]:
                entry.bind('<KeyRelease>', self.on_input_changed)

        # Transitions Frame for manual input
        trans_frame = ttk.LabelFrame(manual_frame, text="Transitions", padding=15)
        trans_frame.pack(fill="both", expand=True, pady=10)

        # Transition input controls with modern style
        trans_control_frame = ttk.Frame(trans_frame)
        trans_control_frame.pack(fill="x", pady=10)

        # Create modern comboboxes
        combo_style = {"width": 15, "font": ("Segoe UI", 10)}
        
        ttk.Label(trans_control_frame, text="From State:", **label_style).pack(side="left", padx=5)
        self.from_state = ttk.Combobox(trans_control_frame, **combo_style)
        self.from_state.pack(side="left", padx=5)

        ttk.Label(trans_control_frame, text="Symbol:", **label_style).pack(side="left", padx=5)
        self.symbol = ttk.Combobox(trans_control_frame, width=8, font=("Segoe UI", 10))
        self.symbol.pack(side="left", padx=5)

        ttk.Label(trans_control_frame, text="To State(s):", **label_style).pack(side="left", padx=5)
        self.to_states = ttk.Entry(trans_control_frame, width=20, font=("Segoe UI", 10))
        self.to_states.pack(side="left", padx=5)

        # Modern buttons
        button_frame = ttk.Frame(trans_control_frame)
        button_frame.pack(side="left", padx=10)
        
        add_btn = ttk.Button(button_frame, text="Add Transition", command=self.add_transition)
        add_btn.pack(side="left", padx=5)

        delete_btn = ttk.Button(button_frame, text="Delete Selected", command=self.delete_transition)
        delete_btn.pack(side="left", padx=5)

        # Transition display with modern style
        self.trans_tree = ttk.Treeview(trans_frame, columns=("from", "symbol", "to"), 
                                     show="headings", height=8)
        self.trans_tree.heading("from", text="From State")
        self.trans_tree.heading("symbol", text="Symbol")
        self.trans_tree.heading("to", text="To State(s)")
        self.trans_tree.pack(fill="both", expand=True)

        # Add scrollbar to treeview
        scrollbar = ttk.Scrollbar(trans_frame, orient="vertical", command=self.trans_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.trans_tree.configure(yscrollcommand=scrollbar.set)

        # Thompson construction frame with modern style
        thompson_input_frame = ttk.Frame(thompson_frame)
        thompson_input_frame.pack(fill="x", pady=20)

        ttk.Label(thompson_input_frame, text="Regular Expression:", 
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=5)
        self.regex_entry = ttk.Entry(thompson_input_frame, width=40, font=("Segoe UI", 10))
        self.regex_entry.pack(side="left", padx=5)

        ttk.Button(thompson_input_frame, text="Build NFA", 
                  command=self.build_thompson_nfa).pack(side="left", padx=5)

        # Buttons Frame with modern style
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        # Create modern action buttons
        convert_btn = ttk.Button(btn_frame, text="Convert", command=self.convert)
        convert_btn.pack(side="left", padx=5)
        
        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear)
        clear_btn.pack(side="left", padx=5)
        
        save_btn = ttk.Button(btn_frame, text="Save Configuration", 
                            command=self.save_current_config)
        save_btn.pack(side="left", padx=5)
        
        load_btn = ttk.Button(btn_frame, text="Load Configuration", 
                            command=self.load_config)
        load_btn.pack(side="left", padx=5)
        
        # Right panel content
        # Notebook for tabs with modern style
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Text output tab
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="Text Output")
        
        self.result_text = scrolledtext.ScrolledText(text_frame, height=15, 
                                                   wrap=tk.WORD, font=("Segoe UI", 10))
        self.result_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Visualization tab (only if visualization is available)
        if VISUALIZATION_AVAILABLE:
            viz_frame = ttk.Frame(self.notebook)
            self.notebook.add(viz_frame, text="Visualization")
            
            # Visualization controls with modern style
            viz_control_frame = ttk.Frame(viz_frame)
            viz_control_frame.pack(fill="x", pady=10)
            
            ttk.Label(viz_control_frame, text="Select Automaton:", 
                     font=("Segoe UI", 11, "bold")).pack(side="left", padx=5)
            self.viz_type = ttk.Combobox(viz_control_frame, 
                                        values=["NFA", "DFA", "Minimized DFA"], 
                                        width=15, font=("Segoe UI", 10))
            self.viz_type.set("NFA")
            self.viz_type.pack(side="left", padx=5)
            self.viz_type.bind("<<ComboboxSelected>>", self.update_visualization)
            
            # Canvas for visualization
            self.viz_canvas_frame = ttk.Frame(viz_frame)
            self.viz_canvas_frame.pack(fill="both", expand=True, pady=10)
        else:
            # Create a message frame for when visualization is not available
            viz_frame = ttk.Frame(self.notebook)
            self.notebook.add(viz_frame, text="Visualization")
            
            message_frame = ttk.Frame(viz_frame)
            message_frame.pack(fill="both", expand=True, pady=20)
            
            ttk.Label(message_frame, text="Visualization is not available", 
                     font=("Segoe UI", 12, "bold")).pack(pady=10)
            ttk.Label(message_frame, text="To enable visualization, install the required packages:").pack()
            ttk.Label(message_frame, text="pip install matplotlib networkx").pack(pady=5)
            
            # Create a button to open the requirements file
            ttk.Button(message_frame, text="View Requirements", 
                      command=self.show_requirements).pack(pady=10)
        
        # Test string tab with modern style
        test_frame = ttk.Frame(self.notebook)
        self.notebook.add(test_frame, text="Test String")
        
        # Test string input with modern style
        test_input_frame = ttk.Frame(test_frame)
        test_input_frame.pack(fill="x", pady=10)
        
        ttk.Label(test_input_frame, text="Enter string to test:", 
                 font=("Segoe UI", 11, "bold")).pack(side="left", padx=5)
        self.test_string = ttk.Entry(test_input_frame, width=30, font=("Segoe UI", 10))
        self.test_string.pack(side="left", padx=5)
        
        ttk.Button(test_input_frame, text="Test", 
                  command=self.test_string_accepted).pack(side="left", padx=5)
        
        # Test result with modern style
        self.test_result = scrolledtext.ScrolledText(test_frame, height=5, 
                                                   wrap=tk.WORD, font=("Segoe UI", 10))
        self.test_result.pack(fill="both", expand=True, padx=10, pady=10)

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

            # Helper function to format state sets
            def format_state_set(state_set):
                if isinstance(state_set, frozenset):
                    return '{' + ', '.join(sorted(state_set)) + '}'
                return str(state_set)

            # Format DFA output
            result = "DFA Conversion Result:\n\n"
            result += f"States: {{{', '.join(format_state_set(s) for s in self.current_dfa.states)}}}\n"
            result += f"Alphabet: {{{', '.join(sorted(self.current_dfa.alphabet))}}}\n"
            result += f"Start State: {format_state_set(self.current_dfa.start_state)}\n"
            result += f"Final States: {{{', '.join(format_state_set(s) for s in self.current_dfa.final_states)}}}\n\n"
            
            # Create transition table for DFA
            result += "Transition Table:\n"
            # Header
            result += "+------------------------------+---------------+------------------------------+\n"
            result += "|          From State          |    Symbol    |           To State          |\n"
            result += "+------------------------------+---------------+------------------------------+\n"
            
            # Sort transitions for better readability
            sorted_transitions = sorted(self.current_dfa.transition_function.items(), 
                                     key=lambda x: (str(x[0][0]), x[0][1]))
            
            # Add transitions
            for (state, symbol), next_state in sorted_transitions:
                result += f"|{format_state_set(state):^30}|{symbol:^15}|{format_state_set(next_state):^30}|\n"
            result += "+------------------------------+---------------+------------------------------+\n\n"
                
            # Format Minimized DFA output
            result += "Minimized DFA:\n\n"
            result += f"States: {{{', '.join(format_state_set(s) for s in self.current_min_dfa.states)}}}\n"
            result += f"Alphabet: {{{', '.join(sorted(self.current_min_dfa.alphabet))}}}\n"
            result += f"Start State: {format_state_set(self.current_min_dfa.start_state)}\n"
            result += f"Final States: {{{', '.join(format_state_set(s) for s in self.current_min_dfa.final_states)}}}\n\n"
            
            # Create transition table for minimized DFA
            result += "Transition Table:\n"
            # Header
            result += "+------------------------------+---------------+------------------------------+\n"
            result += "|          From State          |    Symbol    |           To State          |\n"
            result += "+------------------------------+---------------+------------------------------+\n"
            
            # Sort transitions for better readability
            sorted_min_transitions = sorted(self.current_min_dfa.transition_function.items(),
                                         key=lambda x: (str(x[0][0]), x[0][1]))
            
            # Add transitions
            for (state, symbol), next_state in sorted_min_transitions:
                result += f"|{format_state_set(state):^30}|{symbol:^15}|{format_state_set(next_state):^30}|\n"
            result += "+------------------------------+---------------+------------------------------+\n"

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