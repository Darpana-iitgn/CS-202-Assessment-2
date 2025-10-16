import re
import sys

# Function to clean up the code for display/block content (now primarily used for text sanitization)
def preprocess_code(code):
    # Just split by newline to map to lines easily, no need for full parsing here
    lines = [line.strip() for line in code.split('\n')]
    # Remove blank lines and lines containing only braces (simplifies manual block mapping)
    lines = [line for line in lines if line and not re.match(r'^[\{\}]$', line)]
    return lines

def escape_label(text):
    """Escapes special characters for DOT graph labels."""
    text = text.replace("\\", "\\\\")
    text = text.replace("\"", "\\\"")
    text = text.replace("{", "\\{").replace("}", "\\}")
    text = text.replace("<", "\\<").replace(">", "\\>")
    # Use newline for formatting within the DOT node
    text = text.replace("\n", "\\n") 
    return text

def write_dot(blocks, edges, filename="cfg.dot"):
    """Generates the CFG in DOT format."""
    with open(filename, "w", encoding="utf-8") as f:
        f.write("digraph CFG {\n")
        
        # Global graph settings
        f.write("rankdir=TB;\n") # Top to Bottom layout
        f.write("node [shape=box, style=filled, fontname=Inter];\n")
        
        # Define START and END nodes with distinct color/shape
        f.write('START [shape=Msquare, style=filled, color="peru", fontcolor=white, label="START"];\n')
        f.write('END [shape=Msquare, style=filled, color="peru", fontcolor=white, label="END"];\n')
        
        # Write basic blocks (nodes) with clean labels
        f.write("node [shape=box, style=filled, color=lightgray];\n")
        for label, block in blocks:
            # Join block lines with newline for display (since we simplified the blocks, this is now clean)
            code = "\\n".join(block)
            code = escape_label(code)
            # Use only the descriptive text as the label
            f.write(f'{label} [label="{code}"];\n') 

        # Write edges
        # Map B0 start to START node
        f.write(f'START -> B0 [label=""];\n')
        for src, dst, typ in edges:
            # Use 'label=""' if the type is just sequential and should be a clean arrow
            label_text = f'label="{typ}"' if typ else 'label=""'
            f.write(f'{src} -> {dst} [{label_text}];\n')
            
        # Map exit blocks to END node
        f.write('B3 -> END [label=""];\n')
        f.write('B24 -> END [label=""];\n')
        
        f.write("}\n")
    print(f"[+] CFG DOT file saved as {filename}")

def main():
    # --- Manual Definition of Basic Blocks for main() with SIMPLIFIED Labels ---
    # We are using conditional statements directly as block labels for decision points (B2, B6, B10, etc.)
    # and concise descriptions for action blocks.
    main_blocks_data = [
        ("B0", ["Initialize Variables"]),
        ("B1", ['Input Array Size (n)']),
        ("B2", ["n <= 0 || n > MAX"]),         # Conditional Check
        ("B3", ['Error: Invalid Size\\n& Exit']),
        ("B4", ['Prompt Array Input']),
        ("B5", ['For Loop Init (i=0)']),
        ("B6", ['i < n']),                      # Loop Condition
        ("B7", ['Input arr[i]']),
        ("B8", ['i++']),
        ("B9", ['Menu Loop: Input Choice']),    # Simplified Block for clean CFG
        ("B10", ["choice == 1"]),              # Conditional Check
        ("B11", ["Call bubbleSort()"]),
        ("B12", ["choice == 2"]),              # Conditional Check
        ("B13", ["Call insertionSort()"]),
        ("B14", ["choice == 3"]),              # Conditional Check
        ("B15", ["Input Target\\n& Call binarySearch()"]),
        ("B16", ["index != -1"]),              # Conditional Check
        ("B17", ['Print "Element Found"']),
        ("B18", ['Print "Not Found"']),
        ("B19", ["choice == 4"]),              # Conditional Check
        ("B20", ["Call display()"]),
        ("B21", ["choice == 5"]),              # Conditional Check
        ("B22", ['Exit Message & Break Loop']),
        ("B23", ['Print "Invalid Choice"']),
        ("B24", ["Program Exit (return 0)"])
    ]
    
    # --- Manual Definition of Control Flow Edges for main() ---
    
    # (Source Block, Destination Block, Edge Label)
    main_edges_data = [
        ("B0", "B1", ""),
        ("B1", "B2", ""),
        ("B2", "B3", "True"),
        ("B2", "B4", "False"),
        ("B4", "B5", ""),
        ("B5", "B6", ""),
        ("B6", "B7", "True"),
        ("B6", "B9", "False"), # Loop exit to Menu
        ("B7", "B8", ""),
        ("B8", "B6", "Loop"), # Back to loop condition
        
        ("B9", "B10", ""), # Menu prompt to first choice check
        
        ("B10", "B11", "True"),
        ("B10", "B12", "False"),
        ("B11", "B9", ""), # Action 1 back to menu loop header
        
        ("B12", "B13", "True"),
        ("B12", "B14", "False"),
        ("B13", "B9", ""), # Action 2 back to menu loop header
        
        ("B14", "B15", "True"),
        ("B14", "B19", "False"),
        ("B15", "B16", ""),
        
        ("B16", "B17", "True"),
        ("B16", "B18", "False"),
        ("B17", "B9", ""), # Search Found back to menu
        ("B18", "B9", ""), # Search Not Found back to menu
        
        ("B19", "B20", "True"),
        ("B19", "B21", "False"),
        ("B20", "B9", ""), # Action 4 back to menu loop header
        
        ("B21", "B22", "True"),
        ("B21", "B23", "False"),
        ("B22", "B24", "Break"), # Break to final return 0
        ("B23", "B9", ""), # Action Else back to menu loop header
    ]
    
    output_name = "cfg_main_manual_clean.dot"
    write_dot(main_blocks_data, main_edges_data, output_name)

    # Compute metrics (optional, but good practice)
    N = len(main_blocks_data)
    # Total edges including START and END connections
    E = len(main_edges_data) + 2 # +2 for START -> B0 and B22 -> B24
    
    # Cyclomatic complexity M = Number of predicates + 1 = 8 + 1 = 9
    CC = 9
    
    print(f"[+] Found {N} basic blocks and {E} total edges.")
    print(f"[+] Cyclomatic Complexity (CC) = {CC}")

if __name__ == "__main__":
    main()
