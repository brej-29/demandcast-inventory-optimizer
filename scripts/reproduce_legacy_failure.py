"""A deterministic counterexample to the old forecast-spread uncertainty rule."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from demandcast.inventory.optimizer import _summarise_forecast

_, predicted_std, _ = _summarise_forecast(pd.DataFrame({'yhat': [20.0] * 14}))
observed = np.array([5.0, 35.0] * 14)
report = {'example': 'Synthetic counterexample, not retail data', 'predicted_daily_std': predicted_std, 'observed_daily_std': float(observed.std(ddof=1)), 'legacy_95pct_buffer_7days': float(1.645 * predicted_std * np.sqrt(7)), 'failure': 'Flat predictions imply zero safety stock despite volatile observations.'}
assert predicted_std == 0 and observed.std(ddof=1) > 0
(ROOT / 'docs' / 'verification').mkdir(exist_ok=True, parents=True)
(ROOT / 'docs' / 'verification' / 'legacy-counterexample.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report))
