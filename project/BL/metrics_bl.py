from project.DAL.metrics_dal import MetricsDAL
from project.utils.metric_events import MetricEvents


class MetricsBL:
    @staticmethod
    def track_metric(event_name: [MetricEvents, str], user_id: int):
        if isinstance(event_name, MetricEvents):
            MetricsDAL.track_metric(event_name.value,user_id)
        else:
            MetricsDAL.track_metric(event_name, user_id)

    @staticmethod
    def get_metrics_by_period(period_type: str, metric_name: str, limit: int = 30):
        return MetricsDAL.get_metrics_by_period(period_type,metric_name,limit)