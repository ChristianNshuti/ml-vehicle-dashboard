from pathlib import Path
import csv,random
rng=random.Random(42)
models={'Toyota':['Corolla','Camry','RAV4'],'Ford':['Focus','Fusion','Escape'],'BMW':['320i','X3','X5'],'Honda':['Civic','Accord','CR-V'],'Mercedes-Benz':['C200','E300','GLC'],'Hyundai':['Elantra','Tucson','Sonata'],'Nissan':['Altima','Sentra','Rogue'],'Volkswagen':['Golf','Passat','Tiguan']}
Path('dummy_data').mkdir(exist_ok=True)
with Path('dummy_data/vehicles_data_1000.csv').open('w',newline='',encoding='utf8') as f:
 w=csv.writer(f);w.writerow(['vehicle_id','manufacturer','model','year','fuel_type','transmission','mileage','price'])
 for i in range(1,1001):
  brand=rng.choices(list(models),weights=[23,17,10,16,8,12,8,6])[0]
  year=rng.randint(2015,2025); age=2026-year; mileage=rng.randint(5000,22000)*age
  fuel=rng.choices(['Petrol','Diesel','Hybrid','Electric'],weights=[49,26,19,6])[0]
  premium=1.8 if brand in ['BMW','Mercedes-Benz'] else 1
  price=round(max(4000,(35000-age*1800-mileage*.025)*premium+rng.randint(-2500,4000)),-2)
  w.writerow([f'VH-{i:04}',brand,rng.choice(models[brand]),year,fuel,rng.choice(['Automatic','Manual']),mileage,price])
