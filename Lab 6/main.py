#!/usr/bin/env python3
"""
Unified Python Vulnerability Scanner with Analysis
Runs Semgrep, Bandit, and Pylint on three repositories.
Exports all CWE-based findings into a single consolidated CSV.
Performs coverage analysis and IoU computation.
"""

import subprocess
import json
import sys
import os
import csv
import re
from collections import defaultdict
from typing import Dict, List, Set, Optional
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# === CWE Top 25 Most Dangerous Software Weaknesses (2024) ===
CWE_TOP_25_2024 = {
    'CWE-79', 'CWE-787', 'CWE-89', 'CWE-352', 'CWE-22',
    'CWE-125', 'CWE-78', 'CWE-416', 'CWE-862', 'CWE-434',
    'CWE-94', 'CWE-20', 'CWE-77', 'CWE-287', 'CWE-269',
    'CWE-502', 'CWE-200', 'CWE-863', 'CWE-918', 'CWE-119',
    'CWE-476', 'CWE-798', 'CWE-190', 'CWE-400', 'CWE-306'
}

# === Repositories to scan ===
REPOSITORIES = [
    ("https://github.com/ArchiveBox/ArchiveBox.git", "ArchiveBox"),
    ("https://github.com/agronholm/apscheduler.git", "ApScheduler"),
    ("https://github.com/psf/requests.git", "Requests")
]

# === Utility Helpers ===
def normalize_cwe_id(cwe_string: str) -> Optional[str]:
    """
    Extract and normalize CWE ID from various formats.
    Examples:
        'CWE-79' -> 'CWE-79'
        'CWE-79: Improper Neutralization...' -> 'CWE-79'
        '79' -> 'CWE-79'
    """
    if not cwe_string:
        return None
    
    # Extract CWE-XXX pattern
    match = re.search(r'CWE[-_]?(\d+)', str(cwe_string), re.IGNORECASE)
    if match:
        return f"CWE-{match.group(1)}"
    
    # If it's just a number
    if str(cwe_string).isdigit():
        return f"CWE-{cwe_string}"
    
    return None


def is_in_top_25(cwe_id: str) -> str:
    """Check if a CWE ID is in the Top 25 list."""
    normalized = normalize_cwe_id(cwe_id)
    return "Yes" if normalized and normalized in CWE_TOP_25_2024 else "No"


def run_subprocess(cmd: List[str], check=False) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=check, capture_output=True, text=True, encoding="utf-8", errors="replace")


def safe_project_dir_name(name: str) -> str:
    return "".join(c if (c.isalnum() or c in ("_", "-")) else "_" for c in name).lower()


def install_tool(tool_name: str, package_name: Optional[str] = None):
    """Ensure tool is installed."""
    package_name = package_name or tool_name
    try:
        run_subprocess([tool_name, "--version"], check=True)
        print(f"[+] {tool_name} is already installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"[*] Installing {package_name} ...")
        run_subprocess([sys.executable, "-m", "pip", "install", package_name], check=True)
        print(f"[+] {package_name} installed successfully")


def clone_repository(repo_url: str, target_dir: str) -> Optional[str]:
    """Clone repository if not already cloned."""
    print(f"[*] Cloning repository: {repo_url}")
    if os.path.exists(target_dir):
        print(f"[!] Directory {target_dir} already exists. Using existing directory.")
        return target_dir
    try:
        run_subprocess(["git", "clone", repo_url, target_dir], check=True)
        print(f"[+] Repository cloned successfully to {target_dir}")
        return target_dir
    except subprocess.CalledProcessError as e:
        print(f"[-] Error cloning repository: {e.stderr}")
        return None


# === SEMGREP ===
def run_semgrep(repo_path: str) -> Dict:
    print("[*] Running Semgrep scan...")
    cmd = [
        "semgrep",
        "--config=p/security-audit",
        "--config=p/python",
        "--json",
        "--metrics=off",
        repo_path
    ]
    result = run_subprocess(cmd)
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"results": []}


def extract_cwes_semgrep(finding: Dict) -> Set[str]:
    """Extract and normalize CWE IDs from Semgrep findings."""
    cwes = set()
    metadata = finding.get("extra", {}).get("metadata", {})
    if not metadata:
        return cwes
    
    # Check 'cwe' field
    if "cwe" in metadata:
        cwe_data = metadata["cwe"]
        if isinstance(cwe_data, list):
            for c in cwe_data:
                normalized = normalize_cwe_id(str(c))
                if normalized:
                    cwes.add(normalized)
        else:
            normalized = normalize_cwe_id(str(cwe_data))
            if normalized:
                cwes.add(normalized)
    
    # Check references for CWE links
    if "references" in metadata:
        for ref in metadata["references"]:
            if isinstance(ref, str) and "cwe.mitre.org" in ref:
                cwe_id = ref.split("/")[-1].replace(".html", "")
                normalized = normalize_cwe_id(cwe_id)
                if normalized:
                    cwes.add(normalized)
    
    return cwes


def aggregate_semgrep(repo_name: str, data: Dict) -> List[Dict]:
    counts = defaultdict(int)
    for f in data.get("results", []):
        cwes = extract_cwes_semgrep(f)
        if not cwes:
            cwes = {"CWE-UNKNOWN"}
        for c in cwes:
            counts[c] += 1
    
    return [{
        "Project_name": repo_name,
        "Tool_name": "Semgrep",
        "CWE_ID": c,
        "Number_of_Findings": n,
        "Is_In_CWE_Top_25": is_in_top_25(c)
    } for c, n in counts.items()]


# === BANDIT ===
BANDIT_CWE_MAPPING = {
    # SQL Injection
    'B608': ['CWE-89'],
    
    # Path Traversal
    'B308': ['CWE-22'],
    'B310': ['CWE-22'],
    
    # Command Injection
    'B102': ['CWE-78'],
    'B601': ['CWE-78'],
    'B602': ['CWE-78'],
    'B603': ['CWE-78'],
    'B604': ['CWE-78'],
    'B605': ['CWE-78'],
    'B606': ['CWE-78'],
    'B607': ['CWE-78'],
    
    # Code Injection / Eval
    'B307': ['CWE-94'],
    'B313': ['CWE-94'],
    'B314': ['CWE-94'],
    'B315': ['CWE-94'],
    'B703': ['CWE-94'],
    
    # Deserialization
    'B301': ['CWE-502'],
    'B302': ['CWE-502'],
    'B303': ['CWE-502'],
    'B304': ['CWE-502'],
    'B305': ['CWE-502'],
    'B306': ['CWE-502'],
    'B403': ['CWE-502'],
    'B404': ['CWE-502'],
    'B405': ['CWE-502'],
    'B406': ['CWE-502'],
    'B407': ['CWE-502'],
    'B408': ['CWE-502'],
    'B409': ['CWE-502'],
    'B410': ['CWE-502'],
    'B411': ['CWE-502'],
    'B412': ['CWE-502'],
    'B413': ['CWE-502'],
    'B506': ['CWE-502'],
    
    # Hardcoded Credentials
    'B105': ['CWE-798'],
    'B106': ['CWE-798'],
    'B107': ['CWE-798'],
    
    # Weak Cryptography
    'B303': ['CWE-327'],
    'B304': ['CWE-327'],
    'B305': ['CWE-327'],
    'B324': ['CWE-327'],
    'B501': ['CWE-327'],
    'B502': ['CWE-327'],
    'B503': ['CWE-327'],
    'B504': ['CWE-327'],
    'B505': ['CWE-327'],
    
    # Weak Random
    'B311': ['CWE-330'],
    
    # XML vulnerabilities
    'B317': ['CWE-611'],
    'B318': ['CWE-611'],
    'B320': ['CWE-611'],
    'B405': ['CWE-611'],
    
    # Insecure temp file
    'B108': ['CWE-377'],
    
    # Flask debug mode
    'B201': ['CWE-489'],
    
    # Improper Certificate Validation
    'B501': ['CWE-295'],
    
    # Try/except pass
    'B110': ['CWE-703'],
    
    # Assert used
    'B101': ['CWE-703'],
    
    # exec used
    'B102': ['CWE-94'],
    
    # Binding to all interfaces
    'B104': ['CWE-200'],
    
    # Request without timeout
    'B113': ['CWE-400'],
    
    # Django XSS
    'B308': ['CWE-79'],
    'B703': ['CWE-79'],
}


def run_bandit(repo_path: str) -> Dict:
    print("[*] Running Bandit scan...")
    result = run_subprocess(["bandit", "-r", repo_path, "-f", "json", "-ll"])
    try:
        return json.loads(result.stdout)
    except Exception:
        return {"results": []}


def aggregate_bandit(repo_name: str, data: Dict) -> List[Dict]:
    counts = defaultdict(int)
    for f in data.get("results", []):
        test_id = f.get("test_id")
        cwes = BANDIT_CWE_MAPPING.get(test_id, ["CWE-UNKNOWN"])
        for c in cwes:
            counts[c] += 1
    
    return [{
        "Project_name": repo_name,
        "Tool_name": "Bandit",
        "CWE_ID": c,
        "Number_of_Findings": n,
        "Is_In_CWE_Top_25": is_in_top_25(c)
    } for c, n in counts.items()]


# === PYLINT ===
# Pylint message to CWE mapping based on common security patterns
PYLINT_CWE_MAPPING = {
    # Code execution vulnerabilities
    'W0123': ['CWE-94'],  # eval-used
    'W0611': ['CWE-561'], # unused-import (dead code)
    'W0612': ['CWE-563'], # unused-variable (dead code)
    
    # Exception handling
    'W0702': ['CWE-703'], # bare-except
    'W0703': ['CWE-703'], # broad-except
    'W0705': ['CWE-703'], # duplicate-except
    'E0711': ['CWE-703'], # notimplemented-raised
    
    # Import issues
    'E0401': ['CWE-829'], # import-error (untrusted source)
    
    # SQL Injection potential
    'W1401': ['CWE-89'],  # anomalous-backslash-in-string (potential SQL)
    
    # Dangerous functions
    'W1505': ['CWE-676'], # deprecated-method (using deprecated/dangerous APIs)
    
    # Information exposure
    'W1201': ['CWE-532'], # logging-not-lazy (may log sensitive data)
    'W1202': ['CWE-532'], # logging-format-interpolation
    
    # Input validation
    'W0106': ['CWE-20'],  # expression-not-assigned (improper input handling)
    
    # Weak cryptography indicators
    'C0103': ['CWE-330'], # invalid-name (e.g., weak random seed names)
    
    # Resource management
    'W1514': ['CWE-400'], # unspecified-encoding
    'R1732': ['CWE-404'], # consider-using-with (resource leak)
    'W1509': ['CWE-404'], # subprocess-popen-preexec-fn
    
    # Type confusion
    'E1101': ['CWE-843'], # no-member (type confusion)
    'E1102': ['CWE-843'], # not-callable
    
    # Path traversal potential
    'W1113': ['CWE-22'],  # keyword-arg-before-vararg (path manipulation)
    
    # Expanded mappings to reduce UNKNOWNs
    'E0001': ['CWE-20'],   # syntax-error (input validation)
    'E1136': ['CWE-843'],  # unsubscriptable-object (type confusion)
    'E1120': ['CWE-20'],   # no-value-for-parameter
    'E1121': ['CWE-20'],   # too-many-function-args
    'E1133': ['CWE-664'],  # not-an-iterable (improper resource use)
    'E0102': ['CWE-710'],  # function-redefined
    'W0101': ['CWE-691'],  # unreachable (control flow)
    'W0622': ['CWE-732'],  # redefined-builtin (privilege issue)
    'W0613': ['CWE-563'],  # unused-argument
    'R1705': ['CWE-691'],  # no-else-return
}


def run_pylint(repo_path: str) -> Dict:
    """Run Pylint and return JSON output."""
    print("[*] Running Pylint scan...")
    cmd = [
        "pylint",
        repo_path,
        "--output-format=json",
        "--disable=C,R",  # Disable convention and refactoring, focus on warnings and errors
        "--exit-zero"  # Don't fail on warnings
    ]
    result = run_subprocess(cmd)
    try:
        return {"results": json.loads(result.stdout)}
    except Exception as e:
        print(f"[!] Pylint parsing error: {e}")
        return {"results": []}


def aggregate_pylint(repo_name: str, data: Dict) -> List[Dict]:
    """Aggregate Pylint findings by CWE."""
    counts = defaultdict(int)
    for finding in data.get("results", []):
        msg_id = finding.get("message-id", "")
        symbol = finding.get("symbol", "")
        
        # Try to map by message-id first, then symbol
        cwes = PYLINT_CWE_MAPPING.get(msg_id, PYLINT_CWE_MAPPING.get(symbol, ["CWE-UNKNOWN"]))
        
        for cwe in cwes:
            if cwe != "CWE-UNKNOWN":
                counts[cwe] += 1
                
        # for cwe in cwes:       
        #     counts[cwe] += 1
    
    return [{
        "Project_name": repo_name,
        "Tool_name": "Pylint",
        "CWE_ID": c,
        "Number_of_Findings": n,
        "Is_In_CWE_Top_25": is_in_top_25(c)
    } for c, n in counts.items()]


# === ANALYSIS FUNCTIONS ===
def compute_tool_cwe_coverage(csv_file: str) -> Dict[str, Dict]:
    """
    Compute CWE coverage statistics for each tool.
    Returns: {tool_name: {
        'unique_cwes': set of CWE IDs,
        'top25_cwes': set of Top 25 CWE IDs,
        'coverage_pct': percentage coverage
    }}
    """
    df = pd.read_csv(csv_file)
    
    # Exclude CWE-UNKNOWN from analysis
    df = df[df['CWE_ID'] != 'CWE-UNKNOWN']
    
    tools = df['Tool_name'].unique()
    coverage_data = {}
    
    for tool in tools:
        tool_data = df[df['Tool_name'] == tool]
        unique_cwes = set(tool_data['CWE_ID'].unique())
        
        # Find intersection with Top 25
        top25_cwes = unique_cwes.intersection(CWE_TOP_25_2024)
        coverage_pct = (len(top25_cwes) / len(CWE_TOP_25_2024)) * 100
        
        coverage_data[tool] = {
            'unique_cwes': unique_cwes,
            'top25_cwes': top25_cwes,
            'coverage_pct': coverage_pct,
            'total_unique_cwes': len(unique_cwes),
            'top25_count': len(top25_cwes)
        }
    
    return coverage_data


def compute_iou_matrix(coverage_data: Dict[str, Dict]) -> pd.DataFrame:
    """
    Compute IoU (Jaccard Index) for each tool pair.
    IoU(A, B) = |A ∩ B| / |A ∪ B|
    """
    tools = list(coverage_data.keys())
    n = len(tools)
    iou_matrix = np.zeros((n, n))
    
    for i, tool1 in enumerate(tools):
        for j, tool2 in enumerate(tools):
            cwes1 = coverage_data[tool1]['unique_cwes']
            cwes2 = coverage_data[tool2]['unique_cwes']
            
            if i == j:
                iou_matrix[i][j] = 1.0  # Perfect overlap with itself
            else:
                intersection = len(cwes1.intersection(cwes2))
                union = len(cwes1.union(cwes2))
                iou_matrix[i][j] = intersection / union if union > 0 else 0.0
    
    return pd.DataFrame(iou_matrix, index=tools, columns=tools)


def visualize_coverage(coverage_data: Dict[str, Dict], output_file: str = "coverage_analysis.png"):
    """Create visualization for CWE coverage analysis."""
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Tool-Level CWE Coverage Analysis', fontsize=16, fontweight='bold')
    
    tools = list(coverage_data.keys())
    
    # 1. Top 25 Coverage Bar Chart
    ax1 = axes[0, 0]
    coverage_pcts = [coverage_data[tool]['coverage_pct'] for tool in tools]
    bars = ax1.bar(tools, coverage_pcts, color=['#2E86AB', '#A23B72', '#F18F01'])
    ax1.set_ylabel('Coverage (%)', fontweight='bold')
    ax1.set_title('Top 25 CWE Coverage by Tool', fontweight='bold')
    ax1.set_ylim(0, 100)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    # 2. Total Unique CWEs Detected
    ax2 = axes[0, 1]
    total_cwes = [coverage_data[tool]['total_unique_cwes'] for tool in tools]
    bars = ax2.bar(tools, total_cwes, color=['#2E86AB', '#A23B72', '#F18F01'])
    ax2.set_ylabel('Number of Unique CWEs', fontweight='bold')
    ax2.set_title('Total Unique CWEs Detected by Tool', fontweight='bold')
    ax2.grid(axis='y', alpha=0.3)
    
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # 3. Top 25 vs Non-Top 25 Stacked Bar
    ax3 = axes[1, 0]
    top25_counts = [coverage_data[tool]['top25_count'] for tool in tools]
    non_top25_counts = [coverage_data[tool]['total_unique_cwes'] - coverage_data[tool]['top25_count'] 
                        for tool in tools]
    
    x = np.arange(len(tools))
    width = 0.6
    
    p1 = ax3.bar(x, top25_counts, width, label='Top 25 CWEs', color='#C73E1D')
    p2 = ax3.bar(x, non_top25_counts, width, bottom=top25_counts, 
                 label='Other CWEs', color='#6A994E')
    
    ax3.set_ylabel('Number of CWEs', fontweight='bold')
    ax3.set_title('CWE Distribution: Top 25 vs Others', fontweight='bold')
    ax3.set_xticks(x)
    ax3.set_xticklabels(tools)
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3)
    
    # 4. Venn-style comparison
    ax4 = axes[1, 1]
    
    # Calculate overlaps
    all_tools_cwes = set()
    for tool in tools:
        all_tools_cwes = all_tools_cwes.union(coverage_data[tool]['unique_cwes'])
    
    tool_combinations = []
    for tool in tools:
        only_this_tool = coverage_data[tool]['unique_cwes'].copy()
        for other_tool in tools:
            if other_tool != tool:
                only_this_tool = only_this_tool - coverage_data[other_tool]['unique_cwes']
        tool_combinations.append((f'{tool} only', len(only_this_tool)))
    
    # Common to all
    common_all = coverage_data[tools[0]]['unique_cwes'].copy()
    for tool in tools[1:]:
        common_all = common_all.intersection(coverage_data[tool]['unique_cwes'])
    tool_combinations.append(('Common to all', len(common_all)))
    
    labels = [x[0] for x in tool_combinations]
    values = [x[1] for x in tool_combinations]
    
    colors_pie = ['#2E86AB', '#A23B72', '#F18F01', '#4A7C59']
    wedges, texts, autotexts = ax4.pie(values, labels=labels, autopct='%1.1f%%',
                                         colors=colors_pie, startangle=90)
    ax4.set_title('CWE Detection Overlap Distribution', fontweight='bold')
    
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"[+] Coverage visualization saved to {output_file}")
    plt.close()


def visualize_iou_matrix(iou_df: pd.DataFrame, output_file: str = "iou_matrix.png"):
    """Create heatmap visualization for IoU matrix."""
    plt.figure(figsize=(10, 8))
    
    # Create heatmap
    sns.heatmap(iou_df, annot=True, fmt='.3f', cmap='YlOrRd', 
                square=True, linewidths=1, cbar_kws={'label': 'IoU Score'},
                vmin=0, vmax=1)
    
    plt.title('Tool Pairwise Agreement (IoU Matrix)\nJaccard Index for CWE Detection', 
              fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Tool', fontweight='bold', fontsize=12)
    plt.ylabel('Tool', fontweight='bold', fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"[+] IoU matrix visualization saved to {output_file}")
    plt.close()


def print_analysis_report(coverage_data: Dict[str, Dict], iou_df: pd.DataFrame):
    """Print comprehensive analysis report."""
    print("\n" + "=" * 80)
    print("TOOL-LEVEL CWE COVERAGE ANALYSIS")
    print("=" * 80)
    
    for tool, data in coverage_data.items():
        print(f"\n{tool}:")
        print(f"  Total Unique CWEs Detected: {data['total_unique_cwes']}")
        print(f"  Top 25 CWEs Detected: {data['top25_count']}/25")
        print(f"  Top 25 Coverage: {data['coverage_pct']:.2f}%")
        print(f"  Top 25 CWEs Found: {sorted(data['top25_cwes'])}")
    
    print("\n" + "=" * 80)
    print("PAIRWISE AGREEMENT (IoU) ANALYSIS")
    print("=" * 80)
    print("\nIoU Matrix:")
    print(iou_df.to_string())
    
    # Find best and worst pairs
    tools = list(iou_df.index)
    max_iou = 0
    min_iou = 1
    max_pair = None
    min_pair = None
    
    for i in range(len(tools)):
        for j in range(i+1, len(tools)):
            iou_val = iou_df.iloc[i, j]
            if iou_val > max_iou:
                max_iou = iou_val
                max_pair = (tools[i], tools[j])
            if iou_val < min_iou:
                min_iou = iou_val
                min_pair = (tools[i], tools[j])
    
    print(f"\n[*] Highest Agreement: {max_pair[0]} ↔ {max_pair[1]} (IoU: {max_iou:.3f})")
    print(f"[*] Lowest Agreement: {min_pair[0]} ↔ {min_pair[1]} (IoU: {min_iou:.3f})")
    
    print("\n" + "=" * 80)
    print("INSIGHTS & INTERPRETATIONS")
    print("=" * 80)
    
    # Tool diversity analysis
    avg_iou = iou_df.values[np.triu_indices_from(iou_df.values, k=1)].mean()
    print(f"\n[*] Average Pairwise IoU: {avg_iou:.3f}")
    
    if avg_iou < 0.3:
        print("    → Tools show HIGH DIVERSITY - they detect largely different CWE sets")
        print("    → Recommendation: Use multiple tools for comprehensive coverage")
    elif avg_iou < 0.6:
        print("    → Tools show MODERATE OVERLAP with complementary strengths")
        print("    → Recommendation: Strategic tool combination can improve coverage")
    else:
        print("    → Tools show HIGH SIMILARITY - significant overlap in detection")
        print("    → Recommendation: Any single tool may suffice for basic scanning")
    
    # Coverage maximization
    all_cwes = set()
    all_top25 = set()
    for tool, data in coverage_data.items():
        all_cwes = all_cwes.union(data['unique_cwes'])
        all_top25 = all_top25.union(data['top25_cwes'])
    
    combined_coverage = (len(all_top25) / len(CWE_TOP_25_2024)) * 100
    
    print(f"\n[*] Combined Tool Coverage:")
    print(f"    → All tools together detect {len(all_cwes)} unique CWEs")
    print(f"    → Combined Top 25 coverage: {len(all_top25)}/25 ({combined_coverage:.1f}%)")
    
    # Find best combination
    print(f"\n[*] Best Tool Combination for Maximum Coverage:")
    best_combo_cwes = set()
    best_combo_tools = []
    
    # Greedy selection: add tool that contributes most new CWEs
    remaining_tools = list(coverage_data.keys())
    while remaining_tools:
        max_contribution = 0
        best_tool = None
        for tool in remaining_tools:
            new_cwes = len(coverage_data[tool]['unique_cwes'] - best_combo_cwes)
            if new_cwes > max_contribution:
                max_contribution = new_cwes
                best_tool = tool
        
        if best_tool:
            best_combo_tools.append(best_tool)
            best_combo_cwes = best_combo_cwes.union(coverage_data[best_tool]['unique_cwes'])
            remaining_tools.remove(best_tool)
            top25_in_combo = best_combo_cwes.intersection(CWE_TOP_25_2024)
            print(f"    → {' + '.join(best_combo_tools)}: "
                  f"{len(best_combo_cwes)} CWEs, "
                  f"{len(top25_in_combo)}/25 Top 25 "
                  f"({len(top25_in_combo)/25*100:.1f}%)")
    
    print("\n" + "=" * 80)


# === MAIN ===
def main():
    # Install required tools
    install_tool("semgrep")
    install_tool("bandit")
    install_tool("pylint")
    
    # Install analysis libraries
    print("[*] Installing analysis libraries...")
    for lib in ["matplotlib", "seaborn", "pandas", "numpy"]:
        try:
            __import__(lib)
        except ImportError:
            run_subprocess([sys.executable, "-m", "pip", "install", lib], check=True)

    consolidated_rows = []

    # Scan all repositories
    for repo_url, project_name in REPOSITORIES:
        print("\n" + "=" * 80)
        print(f"Scanning project: {project_name}")
        print("=" * 80)

        repo_dir = safe_project_dir_name(project_name)
        repo_path = clone_repository(repo_url, repo_dir)
        if not repo_path:
            print(f"[-] Skipping {project_name} due to clone failure.")
            continue

        # SEMGREP
        semgrep_res = run_semgrep(repo_path)
        semgrep_csv = aggregate_semgrep(project_name, semgrep_res)
        consolidated_rows.extend(semgrep_csv)

        # BANDIT
        bandit_res = run_bandit(repo_path)
        bandit_csv = aggregate_bandit(project_name, bandit_res)
        consolidated_rows.extend(bandit_csv)

        # PYLINT
        pylint_res = run_pylint(repo_path)
        pylint_csv = aggregate_pylint(project_name, pylint_res)
        consolidated_rows.extend(pylint_csv)

        print(f"[+] Completed scanning for {project_name}\n")

    # Write consolidated CSV
    csv_out = "cwe_findings.csv"
    with open(csv_out, "w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=["Project_name", "Tool_name", "CWE_ID", "Number_of_Findings", "Is_In_CWE_Top_25"])
        writer.writeheader()
        writer.writerows(consolidated_rows)

    print(f"\n[+] Consolidated CWE findings saved to {csv_out}")
    
    # Perform analysis
    print("\n" + "=" * 80)
    print("PERFORMING CWE COVERAGE AND IoU ANALYSIS")
    print("=" * 80)
    
    # Compute coverage
    coverage_data = compute_tool_cwe_coverage(csv_out)
    
    # Compute IoU matrix
    iou_matrix = compute_iou_matrix(coverage_data)
    
    # Save IoU matrix to CSV
    iou_matrix.to_csv("iou_matrix.csv")
    print(f"[+] IoU matrix saved to iou_matrix.csv")
    
    # Generate visualizations
    visualize_coverage(coverage_data)
    visualize_iou_matrix(iou_matrix)
    
    # Print comprehensive report
    print_analysis_report(coverage_data, iou_matrix)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("  1. cwe_findings.csv - Consolidated vulnerability findings")
    print("  2. iou_matrix.csv - Tool pairwise IoU scores")
    print("  3. coverage_analysis.png - CWE coverage visualizations")
    print("  4. iou_matrix.png - IoU heatmap visualization")
    print("=" * 80)


if __name__ == "__main__":
    main()