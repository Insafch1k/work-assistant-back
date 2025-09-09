import asyncio
from threading import Thread

from project.utils.logger import Logger
from datetime import datetime, time, timedelta


def time_calculate(time_start, time_end):
    try:
        if isinstance(time_start, datetime) and isinstance(time_end, datetime):
            if time_start <= time_end:
                time_diff = time_end - time_start
            else:
                time_diff = (time_end + timedelta(days=1)) - time_start
        elif isinstance(time_start, str) and isinstance(time_end, str):
            t_start = datetime.strptime(time_start, "%H:%M:%S").time()
            t_end = datetime.strptime(time_end, "%H:%M:%S").time()

            dt_start = datetime.combine(datetime.today(), t_start)
            dt_end = datetime.combine(datetime.today(), t_end)

            if dt_start <= dt_end:
                time_diff = dt_end - dt_start
            else:
                time_diff = (dt_end + timedelta(days=1)) - dt_start

        elif isinstance(time_start, time) and isinstance(time_end, time):
            dt_start = datetime.combine(datetime.today(), time_start)
            dt_end = datetime.combine(datetime.today(), time_end)

            if dt_start <= dt_end:
                time_diff = dt_end - dt_start
            else:
                time_diff = (dt_end + timedelta(days=1)) - dt_start
        else:
            time_diff = None

        return round(time_diff.total_seconds() / 3600, 2) if time_diff else None
    except (ValueError, TypeError, AttributeError) as e:
        Logger.error(f"Error time calculate {str(e)}")
        return None


def run_async(coro):
    def run():
        asyncio.run(coro)

    Thread(target=run).start()
