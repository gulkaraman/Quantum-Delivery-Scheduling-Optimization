import numpy as np
import pandas as pd
from pyqubo import Array, Constraint, Placeholder, solve_qubo
from paths import DATASET_CSV

# Parametreler (örnek)
NUM_COURIERS = 2
NUM_PACKAGES = 5
NUM_TIMESLOTS = 5

# Zaman dilimleri (örnek)
time_slots = list(range(NUM_TIMESLOTS))

# QUBO değişkenleri: x[c][p][t]
x = Array.create('x', shape=(NUM_COURIERS, NUM_PACKAGES, NUM_TIMESLOTS), vartype='BINARY')

# 1. Her paket tam bir kez alınmalı
one_pick_per_package = 0
for p in range(NUM_PACKAGES):
    one_pick_per_package += Constraint((sum(x[c][p][t] for c in range(NUM_COURIERS) for t in time_slots) - 1) ** 2, label=f"one_pick_p{p}")

# 2. Kurye kapasitesi (örnek: her kurye aynı anda en fazla 2 paket alabilir)
courier_capacity = 0
for c in range(NUM_COURIERS):
    for t in time_slots:
        courier_capacity += Constraint((sum(x[c][p][t] for p in range(NUM_PACKAGES)) - 2) ** 2, label=f"cap_c{c}_t{t}")

# 3. Zaman penceresi kısıtı (örnek: paket p sadece t==p zamanında alınabilir, aksi cezalandırılır)
time_window_penalty = 0
for p in range(NUM_PACKAGES):
    for c in range(NUM_COURIERS):
        for t in time_slots:
            if t != p:  # Sadece örnek için: her paket kendi index zamanında alınmalı
                time_window_penalty += x[c][p][t]

# 4. Amaç fonksiyonu: makespan (örnek: toplam teslimat süresi)
makespan = sum(x[c][p][t] * (t+1) for c in range(NUM_COURIERS) for p in range(NUM_PACKAGES) for t in time_slots)

# QUBO modelini oluştur
H = (
    Placeholder('A') * one_pick_per_package +
    Placeholder('B') * courier_capacity +
    Placeholder('C') * time_window_penalty +
    Placeholder('D') * makespan
)

model = H.compile()

if __name__ == "__main__":
    # Parametreler
    feed_dict = {'A': 5.0, 'B': 5.0, 'C': 2.0, 'D': 1.0}
    qubo, offset = model.to_qubo(feed_dict=feed_dict)
    print("QUBO matrisi boyutu:", len(qubo))
    print("Offset:", offset)
    # QUBO matrisinin küçük bir kısmını göster
    for i, (k, v) in enumerate(qubo.items()):
        if i < 10:
            print(k, v)
    # Model kaydedilebilir veya solver'a verilebilir 