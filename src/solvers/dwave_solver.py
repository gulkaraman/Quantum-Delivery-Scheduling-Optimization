import time
from dimod import SimulatedAnnealingSampler
import numpy as np

def solve_with_dwave(qubo, offset, num_couriers, num_packages, num_timeslots, num_reads=100, **kwargs):
    """
    QUBO'yu klasik SimulatedAnnealingSampler ile çözer ve çözümü teslimat çizelgesine dönüştürür.
    D-Wave API anahtarı gerekmez.
    """
    sampler = SimulatedAnnealingSampler()
    start = time.time()
    response = sampler.sample_qubo(qubo, num_reads=num_reads)
    runtime = time.time() - start
    best_sample = response.first.sample
    best_energy = response.first.energy + offset

    # Çözümü çizelgeye dönüştür
    schedule = []
    for c in range(num_couriers):
        for p in range(num_packages):
            for t in range(num_timeslots):
                var = f"x[{c}][{p}][{t}]"
                if best_sample.get(var, 0) == 1:
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
    result = solve_with_dwave(qubo, offset, NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS)
    print("Çözüm çizelgesi:")
    for row in result['schedule']:
        print(row)
    print(f"Enerji: {result['energy']}")
    print(f"Çözüm süresi: {result['runtime']:.3f} sn") 