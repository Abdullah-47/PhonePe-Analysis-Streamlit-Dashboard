import os
import json
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='your-password', # Replace with your MySQL password
    database='db-name'  # Replace with your database name
)
cursor = conn.cursor()

def extract_year_quarter(path):
    parts = path.split(os.sep)
    year = int(parts[-2])
    quarter = int(os.path.splitext(parts[-1])[0])
    return year, quarter

# 1. map/transaction/hover
def load_transaction_hover(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                year, quarter = extract_year_quarter(root + os.sep + file)
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    for item in data['data']['hoverDataList']:
                        name = item['name']
                        for metric in item['metric']:
                            cursor.execute(
                                "INSERT INTO map_transaction_hover (year, quarter, name, metric_type, count, amount) VALUES (%s, %s, %s, %s, %s, %s)",
                                (year, quarter, name, metric['type'], metric['count'], metric['amount'])
                            )
    conn.commit()

# 2. map/user/hover
def load_user_hover(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                year, quarter = extract_year_quarter(root + os.sep + file)
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    for name, vals in data['data']['hoverData'].items():
                        cursor.execute(
                            "INSERT INTO map_user_hover (year, quarter, name, registered_users, app_opens) VALUES (%s, %s, %s, %s, %s)",
                            (year, quarter, name, vals['registeredUsers'], vals['appOpens'])
                        )
    conn.commit()
# 3. map/insurance/hover
def load_insurance_hover(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                year, quarter = extract_year_quarter(root + os.sep + file)
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    for item in data['data']['hoverDataList']:
                        name = item['name']
                        for metric in item['metric']:
                            cursor.execute(
                                "INSERT INTO map_insurance_hover (year, quarter, name, metric_type, count, amount) VALUES (%s, %s, %s, %s, %s, %s)",
                                (year, quarter, name, metric['type'], metric['count'], metric['amount'])
                            )
    conn.commit()

# 1. aggregated/transaction
def load_aggregated_transaction(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                year, quarter = extract_year_quarter(root + os.sep + file)
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    from_ts = data['data'].get('from')
                    to_ts = data['data'].get('to')
                    for item in data['data']['transactionData']:
                        category = item['name']
                        for instrument in item['paymentInstruments']:
                            cursor.execute(
                                "INSERT INTO aggregated_transaction (year, quarter, from_ts, to_ts, category, instrument_type, count, amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                (year, quarter, from_ts, to_ts, category, instrument['type'], instrument['count'], instrument['amount'])
                            )
    conn.commit()

# 2. aggregated/user
def load_aggregated_user(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                year, quarter = extract_year_quarter(root + os.sep + file)
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    agg = data['data']['aggregated']
                    cursor.execute(
                        "INSERT INTO aggregated_user (year, quarter, registered_users, app_opens) VALUES (%s, %s, %s, %s)",
                        (year, quarter, agg['registeredUsers'], agg['appOpens'])
                    )
                    user_id = cursor.lastrowid
                    users_by_device = data['data'].get('usersByDevice')
                    if users_by_device:
                        for device in data['data']['usersByDevice']:
                            cursor.execute(
                                "INSERT INTO aggregated_user_device (user_id, brand, count, percentage) VALUES (%s, %s, %s, %s)",
                                (user_id, device['brand'], device['count'], device['percentage'])
                            )
    conn.commit()

# 3. aggregated/insurance
def load_aggregated_insurance(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                year, quarter = extract_year_quarter(root + os.sep + file)
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    from_ts = data['data'].get('from')
                    to_ts = data['data'].get('to')
                    for item in data['data']['transactionData']:
                        category = item['name']
                        for instrument in item['paymentInstruments']:
                            cursor.execute(
                                "INSERT INTO aggregated_insurance (year, quarter, from_ts, to_ts, category, instrument_type, count, amount) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                                (year, quarter, from_ts, to_ts, category, instrument['type'], instrument['count'], instrument['amount'])
                            )
    conn.commit()

def load_top_transaction(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                year, quarter = extract_year_quarter(root + os.sep + file)
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    # Ensure 'data' is a dict before using .get()
                    if not isinstance(data.get('data'), dict):
                        continue  # Skip files with no data or wrong format
                    for level in ['states', 'districts', 'pincodes']:
                        items = data['data'].get(level, []) or []
                        for item in items:
                            cursor.execute(
                                "INSERT INTO top_transaction (year, quarter, entity_level, entity_name, metric_type, count, amount) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                (
                                    year, quarter, 
                                    level[:-1], # state, district, pincode
                                    item['entityName'],
                                    item['metric']['type'],
                                    item['metric']['count'],
                                    item['metric']['amount']
                                )
                            )
    conn.commit()

def load_top_insurance(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                year, quarter = extract_year_quarter(root + os.sep + file)
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    for level in ['states', 'districts', 'pincodes']:
                        items = data['data'].get(level, []) or []
                        for item in items:
                            cursor.execute(
                                "INSERT INTO top_insurance (year, quarter, entity_level, entity_name, metric_type, count, amount) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                                (
                                    year, quarter, 
                                    level[:-1], # state, district, pincode
                                    item['entityName'],
                                    item['metric']['type'],
                                    item['metric']['count'],
                                    item['metric']['amount']
                                )
                            )
    conn.commit()

def load_top_user(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.json'):
                year, quarter = extract_year_quarter(root + os.sep + file)
                with open(os.path.join(root, file)) as f:
                    data = json.load(f)
                    for level in ['states', 'districts', 'pincodes']:
                        items = data['data'].get(level, []) or []
                        for item in items:
                            cursor.execute(
                                "INSERT INTO top_user (year, quarter, entity_level, entity_name, registered_users) VALUES (%s, %s, %s, %s, %s)",
                                (
                                    year, quarter,
                                    level[:-1], # state, district, pincode
                                    item['name'],
                                    item['registeredUsers']
                                )
                            )
    conn.commit()

# Example usage:
load_top_transaction('top/transaction/country/india')
load_top_insurance('top/insurance/country/india')
load_top_user('top/user/country/india')




# Example usage:
load_aggregated_transaction('aggregated/transaction/country/india')
load_aggregated_user('aggregated/user/country/india')
load_aggregated_insurance('aggregated/insurance/country/india')


# Example usage:
load_transaction_hover('map/transaction/hover/country/india')
load_user_hover('map/user/hover/country/india')
load_insurance_hover('map/insurance/hover/country/india')

cursor.close()
conn.close()