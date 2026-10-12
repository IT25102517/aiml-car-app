from pathlib import Path
import sys

runtime = Path(__file__).resolve().parent.parent / 'Car-Price-Predictor' / '.model-runtime'
if runtime.exists():
    sys.path.insert(0, str(runtime))

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import argparse
import json
import math
import joblib
import numpy as np
import pandas as pd

folder = Path(__file__).resolve().parent
if not (folder / 'model_bundle.joblib').exists():
    raise SystemExit('Run build_model.py first to prepare the model.')
bundle = joblib.load(folder / 'model_bundle.joblib')


def predict(details):
    # Check the entered details before preparing the model inputs.
    limits = {'Year': (1998, 2019), 'Kilometers_Driven': (0, bundle['cutoff']),
              'Seats': (1, 12), 'Mileage_kmpl': (0, 100), 'Engine_cc': (100, 10000), 'Power_bhp': (1, 1000)}
    values = {}
    for name, (low, high) in limits.items():
        value = details.get(name)
        if value is None or value == '':
            if name not in bundle['medians']:
                raise ValueError('Please enter ' + name.replace('_', ' ') + '.')
            values[name] = bundle['medians'][name]
            continue
        if isinstance(value, bool):
            raise ValueError('Please enter a number for ' + name + '.')
        try:
            number = float(value)
        except (ValueError, TypeError):
            raise ValueError('Please enter a number for ' + name + '.')
        if not math.isfinite(number) or not low <= number <= high:
            raise ValueError(name.replace('_', ' ') + ' must be between ' + str(low) + ' and ' + str(round(high)) + '.')
        if name in ['Year', 'Seats'] and not number.is_integer():
            raise ValueError(name + ' must be a whole number.')
        values[name] = number
    for name, allowed in {**bundle['categories'], 'Owner_Type': list(bundle['owners'])}.items():
        if details.get(name) not in allowed:
            raise ValueError('Please choose a supported ' + name.replace('_', ' ') + '.')

    # Reuse the exact training column order and fitted scaler.
    row = pd.DataFrame(0.0, index=[0], columns=bundle['columns'])
    for name in ['Kilometers_Driven', 'Seats', 'Mileage_kmpl', 'Engine_cc', 'Power_bhp']:
        row.loc[0, name] = values[name]
    row.loc[0, 'Car_Age'] = bundle['reference_year'] - values['Year']
    row.loc[0, 'Owner_Type_Code'] = bundle['owners'][details['Owner_Type']]
    for category in ['Fuel_Type', 'Transmission']:
        indicator = category + '_' + details[category]
        if indicator in row.columns:
            row.loc[0, indicator] = 1.0
    row[bundle['scale_columns']] = bundle['scaler'].transform(row[bundle['scale_columns']])
    estimate = float(bundle['model'].predict(row)[0])
    if not math.isfinite(estimate) or estimate <= 0:
        raise ValueError('The model could not produce a positive price estimate for these details.')
    return {'price_lakhs': estimate, 'price_inr': estimate * 100000,
            'imputed_fields': [name for name in bundle['medians'] if details.get(name) in [None, '']]}


