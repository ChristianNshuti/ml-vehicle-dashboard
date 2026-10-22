import csv
import io
from unittest.mock import patch
import pandas as pd
from django.test import TestCase
from .dashboard import load_data, frequencies, frequency_table

class DashboardTests(TestCase):
    def test_overview_and_totals(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total'], 10000)
        self.assertEqual(sum(r['count'] for r in response.context['frequency']), 10000)
        self.assertTemplateUsed(response, 'vehicles/dashboard.html')
        self.assertContains(response, 'Vehicle Machine Learning Dashboard')
        self.assertContains(response, 'table table-bordered table-striped table-sm')
        self.assertContains(response, 'bootstrap@5.3.2')
        self.assertEqual(len(response.context['page']), 15)

    def test_filters_export_and_pagination_agree(self):
        params = {'manufacturer': 'Toyota', 'fuel_type': 'gasoline', 'sort': '-price'}
        response = self.client.get('/', params)
        rows = list(csv.DictReader(io.StringIO(self.client.get('/export/', params).content.decode())))
        self.assertEqual(len(rows), response.context['total'])
        self.assertTrue(all(r['manufacturer'] == 'Toyota' and r['fuel_type'] == 'gasoline' for r in rows))
        prices = [r['price'] for r in response.context['page']]
        self.assertEqual(prices, sorted(prices, reverse=True))
        self.assertContains(response, 'Toyota')

    def test_empty_and_invalid_parameters(self):
        response = self.client.get('/', {'q': 'no-such-car', 'page': 'bad', 'sort': 'bad', 'group': 'bad'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total'], 0)
        self.assertEqual(response.context['frequency'], [])
        self.assertContains(response, 'Frequency Tables (One-way)')

    def test_alternative_group_and_literal_search(self):
        response = self.client.get('/', {'group': 'year', 'page': 2})
        self.assertEqual(response.context['page'].number, 2)
        self.assertEqual(sum(r['count'] for r in response.context['frequency']), 10000)
        self.assertEqual(self.client.get('/', {'q': '['}).status_code, 200)

    def test_missing_dataset_is_actionable(self):
        with patch('vehicles.views.load_data', side_effect=FileNotFoundError('missing file')):
            self.assertContains(self.client.get('/'), 'Dataset unavailable', status_code=503)
            self.assertEqual(self.client.get('/export/').status_code, 503)

    def test_frequency_escapes_html(self):
        df = pd.DataFrame({'manufacturer': ['<script>alert(1)</script>']})
        self.assertNotIn('<script>', frequency_table(df))
        self.assertEqual(frequencies(df)[0]['share'], 100)

    def test_export_neutralizes_formulas(self):
        df = load_data().head(1).copy()
        df.loc[df.index[0], 'client_name'] = '=1+1'
        with patch('vehicles.views.load_data', return_value=df):
            response = self.client.get('/export/')
            self.assertIn("'=1+1", response.content.decode())

    def test_source_mapping_and_invalid_mileage(self):
        df = load_data()
        raw = pd.read_csv('vehicles_ml_dataset (1).csv')
        self.assertEqual(len(df), len(raw))
        self.assertEqual(df.price.tolist(), raw.selling_price.tolist())
        self.assertEqual(df.model.tolist(), raw.body_type.tolist())
        self.assertEqual(int(df.mileage.isna().sum()), 1)
        response = self.client.get('/', {'q': 'ROW-00003'})
        self.assertEqual(response.context['total'], 1)
        self.assertEqual(response.context['mileage_count'], 0)
        self.assertContains(response, 'Nissan')
        self.assertNotContains(response, 'nan')
        rows = list(csv.DictReader(io.StringIO(self.client.get('/export/').content.decode())))
        self.assertEqual(list(rows[0]), raw.columns.tolist())
        self.assertEqual(rows[2]['kilometers_driven'], 'active')
        self.assertEqual(len(rows), 10000)
