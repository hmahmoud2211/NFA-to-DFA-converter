# NFA to DFA Converter

A graphical tool for converting Non-deterministic Finite Automata (NFA) to Deterministic Finite Automata (DFA) with visualization capabilities.

## Features

- Convert NFA to DFA with visualization
- Thompson Construction for building NFAs from regular expressions
- DFA minimization
- Test strings against the automata
- Save and load automata configurations
- Visual representation of automata using graphs

## Requirements

- Python 3.6 or higher
- matplotlib
- networkx

## Installation

There are two ways to install the required dependencies:

### Method 1: Using the Installation Script

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Run the installation script:
   ```bash
   python install.py
   ```

### Method 2: Manual Installation

1. Open a terminal/command prompt
2. Navigate to the project directory
3. Install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

After installation, you can run the application using:
```bash
python NFA_DFA_Converter.py
```

## Usage

### Manual NFA Creation
1. Enter states (comma-separated), e.g., "q0, q1, q2"
2. Enter alphabet (comma-separated), e.g., "a, b"
3. Select start state
4. Enter final states (comma-separated)
5. Add transitions using the transition controls
6. Click "Convert" to convert to DFA

### Thompson Construction
1. Click on the "Thompson Construction" tab
2. Enter a regular expression (e.g., "a(b|c)*")
3. Click "Build NFA" to create the NFA
4. Click "Convert" to convert to DFA

### Testing Strings
1. After converting to DFA, go to the "Test String" tab
2. Enter a string to test
3. Click "Test" to check if the string is accepted

### Visualization
- Select between NFA, DFA, and Minimized DFA views in the visualization tab
- The graph shows:
  - Start states in green
  - Final states in red
  - Regular states in blue
  - Transitions with labels

## Troubleshooting

If you encounter visualization issues:
1. Make sure matplotlib and networkx are properly installed
2. Try reinstalling the dependencies using the installation script
3. Check if your Python version is 3.6 or higher

## Support

If you encounter any issues:
1. Check that all requirements are installed
2. Verify your Python version
3. Try running the installation script again
4. Check the error messages in the application 