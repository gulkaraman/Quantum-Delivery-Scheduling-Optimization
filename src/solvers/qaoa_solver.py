import time
import numpy as np
from qiskit_optimization import QuadraticProgram
from qiskit_optimization.algorithms import MinimumEigenOptimizer
from qiskit.algorithms import QAOA
from qiskit.primitives import Sampler
from qiskit import Aer
from qiskit.utils import algorithm_globals
from qiskit_optimization.converters import QuadraticProgramToQubo
from qiskit.primitives import Estimator
from qiskit.algorithms import QAOA
from qiskit.utils import QuantumInstance


def qubo_to_quadratic_program(qubo):
    """
    QUBO dict'ini Qiskit QuadraticProgram formatına dönüştürür.
    """
    qp = QuadraticProgram()
    variables = set()
    for (i, j) in qubo:
        variables.add(i)
        variables.add(j)
    for v in variables:
        qp.binary_var(v)
    linear = {}
    quadratic = {}
    constant = 0.0
    for (i, j), v in qubo.items():
        if i == j:
            linear[i] = linear.get(i, 0) + v
        else:
            quadratic[(i, j)] = quadratic.get((i, j), 0) + v
    qp.minimize(constant=constant, linear=linear, quadratic=quadratic)
    return qp


def solve_with_qaoa(qubo, offset, num_couriers, num_packages, num_timeslots, reps=1, seed=42, provider=None, backend=None):
    """
    QUBO'yu Qiskit QAOA ile çözer ve çözümü teslimat çizelgesine dönüştürür.
    Eğer provider ve backend verilirse IBM Qiskit bulutunda, yoksa klasik simülatörde çalışır.
    """
    qp = qubo_to_quadratic_program(qubo)
    algorithm_globals.random_seed = seed
    backend = Aer.get_backend('qasm_simulator')
    quantum_instance = QuantumInstance(backend)
    qaoa = QAOA(quantum_instance=quantum_instance, reps=reps)
    optimizer = MinimumEigenOptimizer(qaoa)
    start = time.time()
    result = optimizer.solve(qp)
    runtime = time.time() - start
    best_sample = result.samples[0].x
    best_energy = result.samples[0].fval + offset
    var_names = qp.variables

    # Çözümü çizelgeye dönüştür
    schedule = []
    for idx, value in enumerate(best_sample):
        if value == 1:
            var = var_names[idx].name
            # x[c][p][t] formatını ayrıştır
            if var.startswith('x['):
                c, p, t = map(int, var[2:-1].split(']['))
                schedule.append({
                    'courier_id': c,
                    'package_id': p,
                    'timeslot': t
                })
    return {
        'schedule': schedule,
        'energy': best_energy,
        'runtime': runtime,
        'raw_sample': best_sample
    }

if __name__ == "__main__":
    from src.qubo_formulation import model, NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS
    feed_dict = {'A': 5.0, 'B': 5.0, 'C': 2.0, 'D': 1.0}
    qubo, offset = model.to_qubo(feed_dict=feed_dict)
    # IBMProvider ve backend örneği
    try:
        from qiskit_ibm_provider import IBMProvider
        provider = IBMProvider(token="YOUR_IBM_API_KEY")
        backend = provider.get_backend("ibmq_qasm_simulator")
    except Exception:
        provider = None
        backend = None
    result = solve_with_qaoa(qubo, offset, NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS, reps=1, provider=provider, backend=backend)
    print("Çözüm çizelgesi:")
    for row in result['schedule']:
        print(row)
    print(f"Enerji: {result['energy']} ")
    print(f"Çözüm süresi: {result['runtime']:.3f} sn") 