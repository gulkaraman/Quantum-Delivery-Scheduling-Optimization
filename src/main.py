import sys
import traceback
import json
import os
from paths import DATASET_CSV, DATASET_ABOUT
from data_preprocessing import load_dataset, extract_features
from qubo_formulation import model, NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS
from solvers.neal_solver import solve_with_neal
from solvers.dwave_solver import solve_with_dwave
from solvers.milp_baseline import solve_with_milp
from visualization import (
    print_comparison_table, plot_gantt_chart, plot_qubo_heatmap, plot_runtime_comparison,
    plot_constraint_violations, plot_metrics_comparison, plot_solution_tables,
    plot_feasibility, plot_solution_quality, critical_analysis
)

def print_ibm_backend_info(provider, backend):
    if provider is not None and backend is not None:
        print("\n--- IBM Quantum Backend Info ---")
        config = backend.configuration()
        print(f"Name: {config.backend_name}")
        print(f"Qubits: {config.n_qubits}")
        print(f"Simulator: {config.simulator}")
        print(f"Local: {config.local}")
        print(f"Max shots: {config.max_shots}")
        print(f"Basis gates: {config.basis_gates}")
        print(f"Coupling map: {config.coupling_map}")
        print(f"Description: {config.description}")
    else:
        print("\nNo IBM Quantum backend connected.")

# IBM API key from apikey.json
APIKEY_PATH = os.path.join(os.path.dirname(__file__), "apikey.json")
if os.path.exists(APIKEY_PATH):
    with open(APIKEY_PATH, "r") as f:
        apikeys = json.load(f)
    ibm_api_key = apikeys.get("apikey")
else:
    ibm_api_key = None

try:
    from qiskit_ibm_provider import IBMProvider
    if ibm_api_key:
        provider = IBMProvider(token=ibm_api_key)
        backend = provider.get_backend("ibmq_qasm_simulator")
    else:
        provider = None
        backend = None
except Exception as e:
    print("IBMProvider connection error:", e)
    provider = None
    backend = None

def main():
    # Print IBM Quantum backend info
    print_ibm_backend_info(provider, backend)

    # 1. Data preprocessing
    df = load_dataset(nrows=NUM_PACKAGES)
    features = extract_features(df, num_couriers=NUM_COURIERS)
    print("Features:")
    print(features.head())

    # 2. QUBO creation
    feed_dict = {'A': 5.0, 'B': 5.0, 'C': 2.0, 'D': 1.0}
    qubo, offset = model.to_qubo(feed_dict=feed_dict)
    print(f"QUBO matrix size: {len(qubo)}")

    results = {}

    # 3. Neal (Simulated Annealing)
    print("\n[NEAL] Solving...")
    try:
        res_neal = solve_with_neal(qubo, offset, NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS)
        results['neal'] = {
            'makespan': max([s['timeslot']+1 for s in res_neal['schedule']]) if res_neal['schedule'] else None,
            'energy': res_neal['energy'],
            'runtime': res_neal['runtime'],
            'violations': 0,  # Constraint violation check can be added
            'schedule': res_neal['schedule']
        }
    except Exception as e:
        print("Neal solver error:", e)
        traceback.print_exc()

    # 4. D-Wave
    print("\n[D-WAVE] Solving...")
    try:
        res_dwave = solve_with_dwave(qubo, offset, NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS)
        results['dwave'] = {
            'makespan': max([s['timeslot']+1 for s in res_dwave['schedule']]) if res_dwave['schedule'] else None,
            'energy': res_dwave['energy'],
            'runtime': res_dwave['runtime'],
            'violations': 0,
            'schedule': res_dwave['schedule']
        }
    except Exception as e:
        print("D-Wave solver error:", e)
        traceback.print_exc()

    # 5. MILP (OR-Tools)
    print("\n[MILP] Solving...")
    try:
        res_milp = solve_with_milp(NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS, capacity=2)
        results['milp'] = {
            'makespan': res_milp['makespan'],
            'energy': None,
            'runtime': res_milp['runtime'],
            'violations': 0,
            'schedule': res_milp['schedule']
        }
    except Exception as e:
        print("MILP solver error:", e)
        traceback.print_exc()

    # 6. Results comparison
    print("\n--- RESULTS COMPARISON TABLE ---")
    df_results = print_comparison_table(results)

    # 7. Gantt chart (for each solver)
    for solver, res in results.items():
        if res['schedule']:
            plot_gantt_chart(res['schedule'], title=f"Gantt Chart - {solver}")

    # 8. QUBO heatmap
    plot_qubo_heatmap(qubo, title="QUBO Heatmap")

    # 9. Runtime comparison
    plot_runtime_comparison(results)

    # 10. Constraint satisfaction (example: violations=0, more advanced check can be added)
    plot_constraint_violations(results)

    # 11. Advanced metrics and visualizations
    plot_metrics_comparison(results)
    plot_solution_tables(results)
    plot_feasibility(results)
    plot_solution_quality(results)

    # 12. Critical analysis and summary
    print("\n--- CRITICAL ANALYSIS ---")
    critical_analysis(results)
    print("\nPipeline completed. All metrics and visualizations are shown above.")

if __name__ == "__main__":
    main() 