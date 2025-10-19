# python cfg_cc.py <program.c>
import re
import sys

def preprocess_code(code):
    code = re.sub(r'//.*|/\*[\s\S]*?\*/', '', code)
    lines = [line.strip() for line in code.split('\n') if line.strip()]
    # Remove lines that are only { or }
    lines = [line for line in lines if line not in ['{', '}']]
    return lines


def find_leaders(lines):
    leaders = set()
    leaders.add(0)
    for i, line in enumerate(lines):
        # Detect control statements
        if re.search(r'\b(if|else if|else|for|while)\b', line):
            leaders.add(i)
            if i + 1 < len(lines):
                leaders.add(i + 1)

        # Detect return/break/continue
        if re.search(r'\b(return|break|continue)\b', line):
            if i + 1 < len(lines):
                leaders.add(i + 1)

        # Detect function or block boundaries
        if "{" in line or "}" in line:
            leaders.add(i)
            if i + 1 < len(lines):
                leaders.add(i + 1)


    return sorted(list(leaders))

def create_basic_blocks(lines, leaders):
    blocks = []
    for i, leader in enumerate(leaders):
        start = leader
        end = leaders[i + 1] if i + 1 < len(leaders) else len(lines)
        block_lines = lines[start:end]
        if block_lines:
            # Using i for labeling B0, B1, B2...
            blocks.append((f'B{len(blocks)}', block_lines))
    return blocks

def create_edges(blocks):
    edges = []
    
    # Store labels of blocks that are decision points
    decision_blocks = set() 
    
    for i, (label, block) in enumerate(blocks):
        code = " ".join(block)
        next_block_label = blocks[i + 1][0] if i + 1 < len(blocks) else None

        # 1. Loops (for/while): Corrected to include the exit edge.
        if any(k in code for k in ["for", "while"]):
            decision_blocks.add(label)
            if next_block_label:
                # Edge 1: Loop Header (True) -> Body
                edges.append((label, next_block_label, "true"))
                # Edge 2: Body -> Loop Header (Back edge)
                edges.append((next_block_label, label, "back"))
                
                # Edge 3 (CRITICAL FIX): Loop Header (False) -> Loop Exit
                # This edge is essential for correct CC calculation.
                if i + 2 < len(blocks):
                     edges.append((label, blocks[i + 2][0], "false (exit)"))
            
        # 2. Conditional Branches (if/else if): Modeling both paths.
        elif "if" in code or "else if" in code:
            decision_blocks.add(label)
            if next_block_label:
                # Edge 1: Condition (True) -> True body
                edges.append((label, next_block_label, "true"))
            
            # Edge 2: Condition (False) -> Block *after* the true body (to model the skip)
            if i + 2 < len(blocks):
                 edges.append((label, blocks[i + 2][0], "false"))

        # 3. Else block: Sequential flow only
        elif "else" in code:
            if next_block_label:
                edges.append((label, next_block_label, ""))

        # 4. Normal sequential flow and Merge flow (Corrected)
        # This handles blocks that are NOT control structures but follow a non-sequential block.
        elif "return" not in code and label not in decision_blocks:
            
            # We now rely on this block to act as the merge point for preceding IFs/ELSEs 
            # and to carry on the sequential flow if it's not a control flow source.
            if not any(k in code for k in ["for", "while", "if", "else"]):
                if next_block_label:
                     edges.append((label, next_block_label, ""))

    # The logic above is designed to create the correct number of edges (E) for CC=E-N+2.
    return list(set(edges))

def escape_label(text):
    text = text.replace("\\", "\\\\").replace("\"", "\\\"")
    text = text.replace("{", "\\{").replace("}", "\\}")
    text = text.replace("<", "\\<").replace(">", "\\>")
    # text = text.replace("\n", "\\n")
    return text

def write_dot(blocks, edges, filename="cfg.dot"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("digraph CFG {\n")
        f.write("node [shape=box, style=filled, color=lightgray];\n")

        # Add Start and End nodes
        f.write('Start [shape=oval, color=lightblue, label="Start"];\n')
        f.write('End [shape=oval, color=lightblue, label="End"];\n')

        # Add basic blocks
        for label, block in blocks:
            code = "\n".join(block)
            code = escape_label(code)
            f.write(f'{label} [label="{label}:\n{code}"];\n')

        # Connect Start to first block
        if blocks:
            f.write(f'Start -> {blocks[0][0]};\n')

        # Add all edges
        for src, dst, lbl in edges:
            if lbl:
                f.write(f'{src} -> {dst} [label="{lbl}"];\n')
            else:
                f.write(f'{src} -> {dst};\n')

        # Connect return blocks to End
        for label, block in blocks:
            code = " ".join(block)
            if "return" in code or "break" in code: # Also treating 'break' as an exit
                f.write(f'{label} -> End;\n')

        f.write("}\n")

    print(f"[+] CFG DOT file saved as {filename}")

def compute_metrics(blocks, edges):
    N = len(blocks)
    E = len(edges)
    CC = E - N + 2
    return N, E, CC


def compute_predecessors(blocks, edges):
    preds = {label: set() for label, _ in blocks}
    for src, dst, _ in edges:
        if dst in preds:
            preds[dst].add(src)
    return preds

def main():
    if len(sys.argv) < 2:
        print("Usage: python cfg_cc.py <program.c>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        code = f.read()

    lines = preprocess_code(code)
    leaders = find_leaders(lines)
    blocks = create_basic_blocks(lines, leaders)
    
    # Using the corrected edge creation logic
    edges = create_edges(blocks) 

    output_name = sys.argv[1].replace(".c", "_cfg.dot")
    write_dot(blocks, edges, output_name)

    N, E, CC = compute_metrics(blocks, edges)
    print(f"[+] Found {N} basic blocks and {E} edges.")
    print(f"[+] Cyclomatic Complexity (CC) = {CC}")


def analyze_cfg(filename):

    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    lines = preprocess_code(code)
    leaders = find_leaders(lines)
    blocks = create_basic_blocks(lines, leaders)
    edges = create_edges(blocks)
    N, E, CC = compute_metrics(blocks, edges)

    return blocks, edges, N, E, CC


if __name__ == "__main__":
    main()



