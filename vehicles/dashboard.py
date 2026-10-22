from django.conf import settings
import pandas as pd

DATA_PATH = settings.BASE_DIR / 'vehicles_ml_dataset (1).csv'
REQUIRED = ['manufacturer', 'body_type', 'year', 'fuel_type', 'transmission', 'kilometers_driven', 'selling_price']

def load_data():
    df = pd.read_csv(DATA_PATH, keep_default_na=False)
    missing = set(REQUIRED) - set(df.columns)
    if missing:
        raise ValueError('Missing CSV columns: ' + ', '.join(sorted(missing)))
    # Keep every source column; aliases support the existing dashboard controls.
    df['vehicle_id'] = [f'ROW-{i:05d}' for i in range(1, len(df) + 1)]
    df['model'] = df['body_type']
    df['price'] = pd.to_numeric(df['selling_price'], errors='raise')
    df['year'] = pd.to_numeric(df['year'], errors='raise')
    for column in ['year', 'price']:
        if df[column].isna().any() or not df[column].map(lambda v: float('-inf') < v < float('inf')).all() or (df[column] < 0).any():
            raise ValueError(f'{column} must contain finite, nonnegative numbers.')
    mileage = pd.to_numeric(df['kilometers_driven'], errors='coerce')
    df['mileage'] = mileage.where(mileage.map(lambda v: 0 <= v < float('inf')))
    return df

def filter_data(df, params):
    for column in ['manufacturer', 'fuel_type', 'transmission']:
        if params.get(column):
            df = df[df[column] == params[column]]
    query = params.get('q', '').strip()
    if query:
        mask = df[['vehicle_id', 'manufacturer', 'model']].astype(str).apply(lambda col: col.str.contains(query, case=False, regex=False)).any(axis=1)
        df = df[mask]
    return df

def frequencies(df, column='manufacturer'):
    counts = df[column].value_counts()
    return [{'label': str(label), 'count': int(count), 'share': round(count / len(df) * 100, 1), 'width': round(count / counts.max() * 100, 1)} for label, count in counts.items()]

def frequency_table(df):
    counts = df['manufacturer'].value_counts().rename_axis('Manufacturer').reset_index(name='Count')
    return counts.to_html(
        classes='table table-bordered table-striped table-sm',
        float_format='%.2f', justify='center', escape=True,
    )
