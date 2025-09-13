import datetime

from project.utils.db_connection import DBConnection


class MetricsDAL(DBConnection):
    @staticmethod
    def track_metric(event_name, user_id):
        conn = MetricsDAL.connect_db()
        try:
            with conn.cursor() as cur:
                query = """
                       INSERT INTO events (event_name, user_id, timestamp)
                       VALUES (%s, %s, %s)
                       """
                cur.execute(query, (event_name,
                    user_id,
                    datetime.datetime.now(),))
                conn.commit()
        except Exception as e:
            conn.rollback()
            raise ValueError(f"Ошибка добавления события: {e}")

        finally:
            conn.close()

    @staticmethod
    def get_metrics_by_period(period_type: str, metric_name: str, limit: int):
        # Определяем формат группировки в зависимости от типа периода
        period_formats = {
            'hour': 'YYYY-MM-DD HH24:00',
            'day': 'YYYY-MM-DD',
            'month': 'YYYY-MM',
            'year': 'YYYY'
        }

        if period_type not in period_formats:
            raise ValueError("period_type must be 'hour', 'day', 'month' or 'year'")

        # Запрос для разных метрик
        metric_queries = {
            'total_users': """
                    WITH periods AS (
                        SELECT generate_series(
                            date_trunc(%s, now()) - (%s || ' ' || %s)::interval,
                            date_trunc(%s, now()),
                            ('1 ' || %s)::interval
                        ) as period
                        ORDER BY period DESC
                        LIMIT %s
                    )
                    SELECT 
                        TO_CHAR(p.period, %s) as period,
                        COUNT(DISTINCT e.user_id) as value
                    FROM periods p
                    LEFT JOIN events e ON 
                        date_trunc(%s, e.timestamp) = p.period
                        AND e.event_name = 'user_registered'
                    GROUP BY p.period
                    ORDER BY p.period DESC
                """,

            'daily_active_users': """
                    WITH periods AS (
                        SELECT generate_series(
                            date_trunc(%s, now()) - (%s || ' ' || %s)::interval,
                            date_trunc(%s, now()),
                            ('1 ' || %s)::interval
                        ) as period
                        ORDER BY period DESC
                        LIMIT %s
                    )
                    SELECT 
                        TO_CHAR(p.period, %s) as period,
                        COUNT(DISTINCT e.user_id) as value
                    FROM periods p
                    LEFT JOIN events e ON date_trunc(%s, e.timestamp) = p.period
                    GROUP BY p.period
                    ORDER BY p.period DESC
                """,

            'new_vacancies': """
                    WITH periods AS (
                        SELECT generate_series(
                            date_trunc(%s, now()) - (%s || ' ' || %s)::interval,
                            date_trunc(%s, now()),
                            ('1 ' || %s)::interval
                        ) as period
                        ORDER BY period DESC
                        LIMIT %s
                    )
                    SELECT 
                        TO_CHAR(p.period, %s) as period,
                        COUNT(e.id) as value
                    FROM periods p
                    LEFT JOIN events e ON 
                        date_trunc(%s, e.timestamp) = p.period
                        AND e.event_name = 'vacancy_published'
                    GROUP BY p.period
                    ORDER BY p.period DESC
                """,

            'responses_count': """
                    WITH periods AS (
                        SELECT generate_series(
                            date_trunc(%s, now()) - (%s || ' ' || %s)::interval,
                            date_trunc(%s, now()),
                            ('1 ' || %s)::interval
                        ) as period
                        ORDER BY period DESC
                        LIMIT %s
                    )
                    SELECT 
                        TO_CHAR(p.period, %s) as period,
                        COUNT(e.id) as value
                    FROM periods p
                    LEFT JOIN events e ON 
                        date_trunc(%s, e.timestamp) = p.period
                        AND e.event_name = 'response_sent'
                    GROUP BY p.period
                    ORDER BY p.period DESC
                """,

            'response_rate': """
                    WITH periods AS (
                        SELECT generate_series(
                            date_trunc(%s, now()) - (%s || ' ' || %s)::interval,
                            date_trunc(%s, now()),
                            ('1 ' || %s)::interval
                        ) as period
                        ORDER BY period DESC
                        LIMIT %s
                    ),
                    responses AS (
                        SELECT 
                            date_trunc(%s, e.timestamp) as period,
                            COUNT(*) as responses_count
                        FROM events e 
                        WHERE e.event_name = 'response_sent'
                        GROUP BY date_trunc(%s, e.timestamp)
                    ),
                    users AS (
                        SELECT 
                            date_trunc(%s, e.timestamp) as period,
                            COUNT(DISTINCT e.user_id) as users_count
                        FROM events e 
                        GROUP BY date_trunc(%s, e.timestamp)
                    )
                    SELECT 
                        TO_CHAR(p.period, %s) as period,
                        CASE 
                            WHEN u.users_count > 0 THEN r.responses_count::FLOAT / u.users_count
                            ELSE 0 
                        END as value
                    FROM periods p
                    LEFT JOIN responses r ON r.period = p.period
                    LEFT JOIN users u ON u.period = p.period
                    ORDER BY p.period DESC
                """

        }

        if metric_name not in metric_queries:
            raise ValueError(f"metric_name must be one of: {list(metric_queries.keys())}")

        conn = MetricsDAL.connect_db()
        try:
            with conn.cursor() as cur:
                if metric_name == 'response_rate':
                    # Особый случай для response_rate - два параметра периода
                    cur.execute(
                        metric_queries[metric_name],
                        (period_type, str(limit - 1), f'{period_type}s',
                         period_type, f'{period_type}s', limit,
                         period_type, period_type, period_type,
                         period_type, period_formats[period_type])
                    )
                else:
                    cur.execute(
                        metric_queries[metric_name],
                        (period_type, str(limit - 1), f'{period_type}s',
                         period_type, f'{period_type}s', limit,
                         period_formats[period_type], period_type)
                    )

                results = cur.fetchall()

                # Преобразуем в список словарей
                metrics_data = []
                for row in results:
                    metrics_data.append({
                        'period': row[0],
                        'value': float(row[1]) if row[1] is not None else 0.0
                    })

                return metrics_data

        except Exception as e:
            print(f"Ошибка получения метрик: {e}")
            raise

        finally:
            conn.close()
