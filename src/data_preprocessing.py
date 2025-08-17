import pandas as pd
import numpy as np
from paths import DATASET_CSV


def load_dataset(path=DATASET_CSV, nrows=None):
    """
    Veri setini okur ve temel öznitelikleri çıkarır.
    """
    df = pd.read_csv(path, nrows=nrows)
    return df


def extract_features(df, num_couriers=3):
    """
    QUBO modellemesi için gerekli öznitelikleri çıkarır.
    Her teslimata package_id, her araca courier_id atar.
    """
    df = df.copy()
    df['package_id'] = df.index  # Her satır bir paket
    # Courier/vehicle assignment: round robin
    df['courier_id'] = df['package_id'] % num_couriers
    # Pickup time window: timestamp (başlangıç), timestamp + loading_unloading_time (bitiş)
    df['pickup_time'] = pd.to_datetime(df['timestamp'])
    df['dropoff_time'] = df['pickup_time'] + pd.to_timedelta(df['loading_unloading_time'], unit='h')
    # Delivery duration
    df['delivery_duration'] = df['loading_unloading_time']
    # Capacity: örnek olarak warehouse_inventory_level veya sabit değer
    df['capacity'] = df['warehouse_inventory_level']
    # Soft constraints: trafik, hava, risk
    df['traffic'] = df['traffic_congestion_level']
    df['weather'] = df['weather_condition_severity']
    df['risk'] = df['route_risk_level']
    # Order fulfilled?
    df['fulfilled'] = df['order_fulfillment_status']
    # Gerekli sütunları seç
    features = df[['package_id', 'courier_id', 'pickup_time', 'dropoff_time', 'delivery_duration',
                   'capacity', 'traffic', 'weather', 'risk', 'fulfilled',
                   'vehicle_gps_latitude', 'vehicle_gps_longitude']]
    return features

if __name__ == "__main__":
    df = load_dataset(nrows=20)  # Küçük örnekle test
    features = extract_features(df)
    print(features.head()) 