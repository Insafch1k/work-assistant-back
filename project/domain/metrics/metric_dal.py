from datetime import datetime
from typing import List
from sqlalchemy import func, text, and_, case, Float
from project.application.entities.event import PeriodType, MetricName, MetricEvents
from project.domain.core.models.event import EventModel
from project.utils.data_state import DataState, DataFailedMessage, DataSuccess
from project.utils.db_connection import connection_db

class MetricsDal:
    PERIOD_FORMATS = {
        PeriodType.HOUR: 'YYYY-MM-DD HH24:MI',
        PeriodType.DAY: 'YYYY-MM-DD',
        PeriodType.MONTH: 'YYYY-MM',
        PeriodType.YEAR: 'YYYY'
    }

    DATE_TRUNC_MAP = {
        PeriodType.HOUR: lambda col: func.date_trunc('hour', col),
        PeriodType.DAY: lambda col: func.date_trunc('day', col),
        PeriodType.MONTH: lambda col: func.date_trunc('month', col),
        PeriodType.YEAR: lambda col: func.date_trunc('year', col),
    }

    @staticmethod
    def track_metric(event_name: str, user_id: int) -> DataState:
        Session = connection_db()
        if not Session:
            return DataFailedMessage(
                "Database connection error")  # когда создается DataFailedMessage автоматом ошибка логируется

        with Session() as session:
            try:
                event = EventModel(
                    event_name=event_name,
                    user_id=user_id,
                    timestamp=datetime.now()
                )
                session.add(event)
                session.commit()
                return DataSuccess(f'Событие {event_name} добавлено!')
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f'Не удалось добавить событие {event_name}!', error=e)

    @staticmethod
    def get_metrics_by_period(
            period_type: PeriodType,
            metric_name: MetricName,
            limit: int
    ) -> DataState:
        # Валидация параметров
        Session = connection_db()
        with Session() as session:
            try:
                if metric_name == MetricName.REGISTERED_USERS:
                    return MetricsDal._get_registered_users(session, period_type, limit)
                elif metric_name == MetricName.ACTIVE_USERS:
                    return MetricsDal._get_active_users(session, period_type, limit)
                elif metric_name == MetricName.NEW_VACANCIES:
                    return MetricsDal._get_new_vacancies(session, period_type, limit)
                elif metric_name == MetricName.RESPONSES_COUNT:
                    return MetricsDal._get_responses_count(session, period_type, limit)
                elif metric_name == MetricName.RESPONSE_RATE:
                    return MetricsDal._get_response_rate(session, period_type, limit)
            except Exception as e:
                session.rollback()
                return DataFailedMessage(f'Не удалось получить метрики по {metric_name}!', error=e)

    @staticmethod
    def _generate_periods(session, period_type: PeriodType, limit: int):
        """Генерация периодов через SQLAlchemy"""
        period_expr = MetricsDal.DATE_TRUNC_MAP[period_type]

        # Создаем CTE с периодами
        periods_cte = (
            session.query(
                func.generate_series(
                    period_expr(func.now()) - text(f"interval '{limit - 1} {period_type.value}s'"),
                    period_expr(func.now()),
                    text(f"interval '1 {period_type.value}'")
                ).label('period')
            )
            .order_by(text('period DESC'))
            .limit(limit)
            .cte('periods')
        )
        return periods_cte

    @staticmethod
    def _get_registered_users(session, period_type: PeriodType, limit: int) -> DataState:
        """Метрика: зарегистрированные пользователи"""
        periods_cte = MetricsDal._generate_periods(session, period_type, limit)
        period_expr = MetricsDal.DATE_TRUNC_MAP[period_type]

        query = (
            session.query(
                func.to_char(periods_cte.c.period, MetricsDal.PERIOD_FORMATS[period_type]).label('period'),
                func.count(func.distinct(EventModel.user_id)).label('value')
            )
            .select_from(periods_cte)
            .outerjoin(
                EventModel,
                and_(
                    period_expr(EventModel.timestamp) == periods_cte.c.period,
                    EventModel.event_name == 'user_registered'
                )
            )
            .group_by(periods_cte.c.period)
            .order_by(periods_cte.c.period.desc())
        )

        return DataSuccess([{"period": row.period, "value": float(row.value or 0)}
                for row in query.all()])

    @staticmethod
    def _get_active_users(session, period_type: PeriodType, limit: int) -> DataState:
        """Метрика: активные пользователи"""
        periods_cte = MetricsDal._generate_periods(session, period_type, limit)
        period_expr = MetricsDal.DATE_TRUNC_MAP[period_type]

        query = (
            session.query(
                func.to_char(periods_cte.c.period, MetricsDal.PERIOD_FORMATS[period_type]).label('period'),
                func.count(func.distinct(EventModel.user_id)).label('value')
            )
            .select_from(periods_cte)
            .outerjoin(EventModel, period_expr(EventModel.timestamp) == periods_cte.c.period)
            .group_by(periods_cte.c.period)
            .order_by(periods_cte.c.period.desc())
        )

        return DataSuccess([{"period": row.period, "value": float(row.value or 0)}
                for row in query.all()])

    @staticmethod
    def _get_new_vacancies( session, period_type: PeriodType, limit: int) -> DataState:
        """Метрика: новые вакансии"""
        periods_cte = MetricsDal._generate_periods(session, period_type, limit)
        period_expr = MetricsDal.DATE_TRUNC_MAP[period_type]

        query = (
            session.query(
                func.to_char(periods_cte.c.period, MetricsDal.PERIOD_FORMATS[period_type]).label('period'),
                func.count(EventModel.id).label('value')
            )
            .select_from(periods_cte)
            .outerjoin(
                EventModel,
                and_(
                    period_expr(EventModel.timestamp) == periods_cte.c.period,
                    EventModel.event_name == 'vacancy_published'
                )
            )
            .group_by(periods_cte.c.period)
            .order_by(periods_cte.c.period.desc())
        )

        return DataSuccess([{"period": row.period, "value": float(row.value or 0)}
                for row in query.all()])

    @staticmethod
    def _get_responses_count(session, period_type: PeriodType, limit: int) -> DataState:
        """Метрика: количество откликов"""
        periods_cte = MetricsDal._generate_periods(session, period_type, limit)
        period_expr = MetricsDal.DATE_TRUNC_MAP[period_type]

        query = (
            session.query(
                func.to_char(periods_cte.c.period, MetricsDal.PERIOD_FORMATS[period_type]).label('period'),
                func.count(EventModel.id).label('value')
            )
            .select_from(periods_cte)
            .outerjoin(
                EventModel,
                and_(
                    period_expr(EventModel.timestamp) == periods_cte.c.period,
                    EventModel.event_name == 'vacancy_sent'
                )
            )
            .group_by(periods_cte.c.period)
            .order_by(periods_cte.c.period.desc())
        )

        return DataSuccess([{"period": row.period, "value": float(row.value or 0)}
                for row in query.all()])

    @staticmethod
    def _get_response_rate(session, period_type: PeriodType, limit: int) -> DataState:
        """Метрика: rate откликов"""
        periods_cte = MetricsDal._generate_periods(session, period_type, limit)
        period_expr = MetricsDal.DATE_TRUNC_MAP[period_type]

        # CTE для откликов
        responses_cte = (
            session.query(
                period_expr(EventModel.timestamp).label('period'),
                func.count(EventModel.id).label('responses_count')
            )
            .filter(EventModel.event_name == 'vacancy_sent')
            .group_by(period_expr(EventModel.timestamp))
            .cte('responses')
        )

        # CTE для пользователей
        users_cte = (
            session.query(
                period_expr(EventModel.timestamp).label('period'),
                func.count(func.distinct(EventModel.user_id)).label('users_count')
            )
            .group_by(period_expr(EventModel.timestamp))
            .cte('users')
        )

        query = (
            session.query(
                func.to_char(periods_cte.c.period, MetricsDal.PERIOD_FORMATS[period_type]).label('period'),
                case(
                    [(users_cte.c.users_count > 0,
                      responses_cte.c.responses_count.cast(Float) / users_cte.c.users_count)],
                    else_=0.0
                ).label('value')
            )
            .select_from(periods_cte)
            .outerjoin(responses_cte, responses_cte.c.period == periods_cte.c.period)
            .outerjoin(users_cte, users_cte.c.period == periods_cte.c.period)
            .order_by(periods_cte.c.period.desc())
        )

        return DataSuccess([{"period": row.period, "value": float(row.value or 0)}
                for row in query.all()])
