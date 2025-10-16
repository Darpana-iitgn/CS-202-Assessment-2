# python reaching_defs.py <program.c>

import sys
from cfg_cc import analyze_cfg, compute_predecessors
import re
import pandas as pd


def find_definitions(blocks):
    definitions = {}
    def_id = 1
    var_defs = {}

    for label, block in blocks:
        for line in block:
            match = re.match(r'.*([a-zA-Z_]\w*)\s*=\s*[^;]+;', line)
            if match:
                var = match.group(1)
                d = f"D{def_id}"
                definitions[d] = {"line": line, "var": var, "block": label}
                var_defs.setdefault(var, set()).add(d)
                def_id += 1

    return definitions, var_defs


def compute_gen_kill(blocks, definitions, var_defs):
    gen = {}
    kill = {}

    for label, block in blocks:
        gen[label] = set()
        kill[label] = set()
        for line in block:
            for d, info in definitions.items():
                if info["line"] == line:
                    var = info["var"]
                    gen[label].add(d)
                    kill[label].update(var_defs[var] - {d})
    return gen, kill


def compute_predecessors(blocks, edges):
    preds = {label: set() for label, _ in blocks}
    for src, dst, _ in edges:
        if dst in preds:
            preds[dst].add(src)
    return preds


def reaching_definitions(blocks, edges, definitions, var_defs):
    gen, kill = compute_gen_kill(blocks, definitions, var_defs)
    preds = compute_predecessors(blocks, edges)

    in_b = {label: set() for label, _ in blocks}
    out_b = {label: set() for label, _ in blocks}

    changed = True
    iteration = 0
    results = []

    while changed:
        iteration += 1
        changed = False
        iteration_table = []

        for label, _ in blocks:
            new_in = set().union(*(out_b[p] for p in preds[label])) if preds[label] else set()
            new_out = gen[label].union(new_in - kill[label])

            if new_out != out_b[label]:
                changed = True

            in_b[label] = new_in
            out_b[label] = new_out

            iteration_table.append({
                "Block": label,
                "gen": gen[label],
                "kill": kill[label],
                "in": in_b[label],
                "out": out_b[label]
            })

        results.append((iteration, iteration_table))

    return results


import os
import pandas as pd

def print_rd_results(results, filename):
    # Extract base name of the C file (e.g. sorting_and_search.c → sorting_and_search)
    base = os.path.splitext(os.path.basename(filename))[0]

    for iteration, table in results:
        print(f"\n=== Iteration {iteration} ({base}) ===")
        # print("{:<10} {:<25} {:<25} {:<25} {:<25}".format(
        #     "Block", "gen[B]", "kill[B]", "in[B]", "out[B]"))
        print("-" * 120)

        data = []
        for row in table:
            gen_str = "{" + ",".join(sorted(row["gen"])) + "}" if row["gen"] else "{}"
            kill_str = "{" + ",".join(sorted(row["kill"])) + "}" if row["kill"] else "{}"
            in_str = "{" + ",".join(sorted(row["in"])) + "}" if row["in"] else "{}"
            out_str = "{" + ",".join(sorted(row["out"])) + "}" if row["out"] else "{}"

            # print("{:<10} {:<25} {:<25} {:<25} {:<25}".format(
            #     row["Block"], gen_str, kill_str, in_str, out_str))

            data.append({
                "Basic Block": row["Block"],
                "gen[B]": gen_str,
                "kill[B]": kill_str,
                "in[B]": in_str,
                "out[B]": out_str
            })

        # # Save CSV for this iteration
        # csv_name = f"{base}_iteration_{iteration}.csv"
        # pd.DataFrame(data).to_csv(csv_name, index=False)
        # print(f"Saved table for Iteration {iteration} → {csv_name}")

    # After all iterations, save a combined Excel file (each sheet = one iteration)
    xlsx_name = f"{base}_reaching_definitions.xlsx"
    with pd.ExcelWriter(xlsx_name) as writer:
        for iteration, table in results:
            df = pd.DataFrame([
                {
                    "Basic Block": row["Block"],
                    "gen[B]": "{" + ",".join(sorted(row["gen"])) + "}" if row["gen"] else "{}",
                    "kill[B]": "{" + ",".join(sorted(row["kill"])) + "}" if row["kill"] else "{}",
                    "in[B]": "{" + ",".join(sorted(row["in"])) + "}" if row["in"] else "{}",
                    "o"
                    "ut[B]": "{" + ",".join(sorted(row["out"])) + "}" if row["out"] else "{}"
                }
                for row in table
            ])
            df.to_excel(writer, sheet_name=f"Iteration_{iteration}", index=False)
    print(f"All iterations saved to {xlsx_name}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python reaching_defs.py <program.c>")
        sys.exit(1)

    filename = sys.argv[1]

    # Import CFG info from cfg_cc.py
    blocks, edges, N, E, CC = analyze_cfg(filename)

    print(f"Using CFG from {filename}")
    print(f"{N} blocks, {E} edges, CC = {CC}")

    definitions, var_defs = find_definitions(blocks)
    results = reaching_definitions(blocks, edges, definitions, var_defs)

    print_rd_results(results, filename)

    # print("\nDefinition Mapping:")
    # for d, info in definitions.items():
    #     print(f"{d}: {info['line']}")

if __name__ == "__main__":
    main()
