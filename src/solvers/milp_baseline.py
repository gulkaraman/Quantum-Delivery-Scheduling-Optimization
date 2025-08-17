from ortools.sat.python import cp_model
import time

def solve_with_milp(num_couriers, num_packages, num_timeslots, capacity=2):
    """
    Teslimat çizelgeleme problemini MILP olarak çözer.
    """
    model = cp_model.CpModel()
    x = {}
    for c in range(num_couriers):
        for p in range(num_packages):
            for t in range(num_timeslots):
                x[c, p, t] = model.NewBoolVar(f"x_{c}_{p}_{t}")

    # 1. Her paket tam bir kez alınmalı
    for p in range(num_packages):
        model.Add(sum(x[c, p, t] for c in range(num_couriers) for t in range(num_timeslots)) == 1)

    # 2. Kurye kapasitesi (her kurye, her zaman diliminde en fazla 'capacity' paket alabilir)
    for c in range(num_couriers):
        for t in range(num_timeslots):
            model.Add(sum(x[c, p, t] for p in range(num_packages)) <= capacity)

    # 3. Zaman penceresi (örnek: paket p sadece t==p zamanında alınabilir)
    for p in range(num_packages):
        for c in range(num_couriers):
            for t in range(num_timeslots):
                if t != p:
                    model.Add(x[c, p, t] == 0)

    # 4. Amaç fonksiyonu: makespan (örnek: toplam teslimat süresi)
    makespan = model.NewIntVar(0, num_timeslots, 'makespan')
    for c in range(num_couriers):
        for p in range(num_packages):
            for t in range(num_timeslots):
                # Eğer x[c,p,t]=1 ise makespan >= t+1
                model.Add(makespan >= (t+1) * x[c, p, t])

    model.Minimize(makespan)

    # Çözümü bul
    solver = cp_model.CpSolver()
    start = time.time()
    status = solver.Solve(model)
    runtime = time.time() - start

    schedule = []
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for c in range(num_couriers):
            for p in range(num_packages):
                for t in range(num_timeslots):
                    if solver.Value(x[c, p, t]) == 1:
                        schedule.append({
                            'courier_id': c,
                            'package_id': p,
                            'timeslot': t
                        })
        best_obj = solver.ObjectiveValue()
    else:
        best_obj = None
    return {
        'schedule': schedule,
        'makespan': best_obj,
        'runtime': runtime,
        'status': status
    }

if __name__ == "__main__":
    from src.qubo_formulation import NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS
    result = solve_with_milp(NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS, capacity=2)
    print("Çözüm çizelgesi:")
    for row in result['schedule']:
        print(row)
    print(f"Makespan: {result['makespan']}")
    print(f"Çözüm süresi: {result['runtime']:.3f} sn") 