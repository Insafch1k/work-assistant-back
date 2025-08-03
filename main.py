from flask_cors import CORS
from project import create_app
from project.utils.metrics_collector import MetricsCollector
import threading
import time

app = create_app()
CORS(app)

def run_metrics_collection():
    """Запускает периодический сбор метрик каждые 10 минут"""
    with app.app_context():
        while True:
            MetricsCollector.collect_daily_metrics()
            time.sleep(600)  # 10 минут

# Запускаем фоновую задачу для сбора метрик
if __name__ == '__main__':
    metrics_thread = threading.Thread(target=run_metrics_collection, daemon=True)
    metrics_thread.start()
    app.run(host="0.0.0.0", port=8000, debug=True)