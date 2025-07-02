from datetime import datetime, time

def time_calculate(time_start, time_end):
    try:
        if isinstance(time_start, datetime) and isinstance(time_end, datetime):
            time_diff = time_end - time_start

        elif isinstance(time_start, str) and isinstance(time_end, str):
            t_start = datetime.strptime(time_start, "%H:%M:%S").time()
            t_end = datetime.strptime(time_end, "%H:%M:%S").time()

            dt_start = datetime.combine(datetime.today(), t_start)
            dt_end = datetime.combine(datetime.today(), t_end)

            time_diff = dt_end - dt_start

        elif isinstance(time_start, time) and isinstance(time_end, time):
            dt_start = datetime.combine(datetime.today(), time_start)
            dt_end = datetime.combine(datetime.today(), time_end)
            time_diff = dt_end - dt_start
        else:
            time_diff = None

        return round(time_diff.total_seconds() / 3600, 2) if time_diff else None
    except (ValueError, TypeError, AttributeError) as e:
        print(f"Ошибка обработки времени: {e}")
        return None