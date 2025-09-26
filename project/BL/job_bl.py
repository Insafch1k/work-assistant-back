import asyncio

from project.DAL.job_dal import JobDAL
from project.DAL.jobs_seeAll_dal import Jobs

from project.utils.methods_for_datetime import time_calculate, format_any_datetime


class JobBL:
    @staticmethod
    def add_job(curr_id, data):
        new_job = JobDAL.add_job(
            curr_id,
            data["title"],
            data["wanted_job"],
            data["description"],
            data["salary"],
            data["date"],
            data["time_start"],
            data["time_end"],
            data["address"],
            data["city"],  # Добавляем город
            data.get("is_urgent", False),
            data["xp"],
            data["age"],
            data.get("car", False)
        )
        new_job['message'] = "Объявление успешно создано"
        return new_job

    @staticmethod
    def get_job_see_all(finder_id, job_id):
        job_json = Jobs.get_job_seeAll(finder_id, job_id)

        hours = (time_calculate(job_json["time_start"], job_json["time_end"])
                 if job_json["time_start"] and job_json["time_end"] else None,)
        job_json["hours"] = hours[0]

        formatted_date_of_work = format_any_datetime(job_json["date"], with_hour=False)
        job_json["date"] = formatted_date_of_work
        return job_json


def run_async(coro):
    """Запуск асинхронной функции в отдельном event loop"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
