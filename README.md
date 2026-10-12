# Used Car Price Predictor

A web form for the group's selected Gradient Boosting model. Predictions use the original fitted Colab model and its fitted preprocessing, without retraining. Prices are in INR lakhs.

## Deploy to Render

1. Upload the files in this folder to the root of a new GitHub repository, including `model_bundle.joblib` and `render.yaml`.
2. Sign in to Render with GitHub.
3. Choose **New > Blueprint** and connect that repository.
4. Apply the blueprint. It selects a **Free** Python web service.
5. Open the service's public URL after deployment finishes.

Alternatively, create a Web Service with these settings:

| Setting | Value |
| --- | --- |
| Runtime | Python 3 |
| Build command | `pip install -r requirements.txt` |
| Start command | `gunicorn web:application --bind 0.0.0.0:$PORT --workers 1 --timeout 120` |
| Health check path | `/health` |
| Environment variable | `PYTHON_VERSION=3.12.8` |
| Instance type | Free |

Free services sleep after 15 minutes of inactivity and can take about a minute to wake up.

## Run locally

Install `requirements.txt` using Python 3.12, then run `python web.py`. The local address is http://127.0.0.1:8766. Gunicorn is used on the Linux hosting service.

The dataset is not needed to run the saved model. This is an academic demonstration based on the historical training data.
