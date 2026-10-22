from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from .dashboard import load_data, filter_data, frequencies, frequency_table

def dataset():
    try:
        return load_data(), None
    except (OSError, ValueError) as exc:
        return None, f'Unable to load vehicle data: {exc}'

def dashboard_view(request):
    source, error = dataset()
    if error:
        return render(request, 'vehicles/dashboard.html', {'error': error}, status=503)
    df = filter_data(source, request.GET)
    group = request.GET.get('group', 'manufacturer')
    if group not in ['manufacturer', 'fuel_type', 'transmission', 'year', 'body_type']:
        group = 'manufacturer'
    sort = request.GET.get('sort', 'vehicle_id')
    if sort.removeprefix('-') not in source.columns:
        sort = 'vehicle_id'
    df = df.sort_values(sort.removeprefix('-'), ascending=not sort.startswith('-'))
    page = Paginator(df.to_dict('records'), 15).get_page(request.GET.get('page'))
    params = request.GET.copy()
    params.pop('page', None)
    return render(request, 'vehicles/dashboard.html', {
        'frequency_table': frequency_table(df),
        'total': len(df), 'source_total': len(source), 'brands': df.manufacturer.nunique(),
        'avg_price': df.price.mean() if len(df) else 0,
        'avg_mileage': df.mileage.mean() if df.mileage.notna().any() else None,
        'invalid_mileage': int(source.mileage.isna().sum()), 'mileage_count': int(df.mileage.notna().sum()),
        'manufacturers': sorted(source.manufacturer.unique()), 'fuels': sorted(source.fuel_type.unique()),
        'transmissions': sorted(source.transmission.unique()), 'frequency': frequencies(df, group), 'group': group,
        'manufacturer_chart': frequencies(df), 'fuel_chart': frequencies(df, 'fuel_type'),
        'page': page, 'params': params.urlencode(), 'sort': sort,
    })

def export_csv(request):
    source, error = dataset()
    if error:
        return HttpResponse(error, status=503, content_type='text/plain')
    df = filter_data(source, request.GET).copy()
    for col in df.select_dtypes(include='object'):
        df[col] = df[col].map(lambda v: "'" + v if str(v).lstrip().startswith(('=', '+', '-', '@')) else v)
    df = df.drop(columns=['vehicle_id', 'model', 'price', 'mileage'])
    response = HttpResponse(df.to_csv(index=False), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vehicles.csv"'
    return response
