from project.application.routes.metrics.metric_schemas import TrackEventValidateSchema, GetMetricsValidateSchema
from project.domain.metrics.metric_dal import MetricsDal


class MetricsBL:
    @staticmethod
    def track_metric(result: TrackEventValidateSchema):
        return MetricsDal.track_metric(result.event_name.value,result.user_id)


    @staticmethod
    def get_metrics_by_period(result: GetMetricsValidateSchema):
        return MetricsDal.get_metrics_by_period(result.period,result.metric_name,result.limit)