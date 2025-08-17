# Tüm veri seti ve proje dosya yolları burada merkezi olarak tanımlanır

import os

# Proje ana dizini
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Dataset klasörü
DATASET_DIR = os.path.join(PROJECT_ROOT, 'dataset')

# Ana veri seti dosyası
DATASET_CSV = os.path.join(DATASET_DIR, 'dynamic_supply_chain_logistics_dataset.csv')

# Dataset hakkında bilgi dosyası
DATASET_ABOUT = os.path.join(DATASET_DIR, 'dataset_about.txt')

# (Gerekirse başka yollar da eklenebilir) 