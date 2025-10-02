from enum import Enum

class CategoryEnum(str, Enum):
    FOR_EMPLOYERS = "for_employers"
    FOR_STUDENTS = "for_students"
    FOR_RETIRES = "for_retires"
    REMOTE_WORK = "remote_work"
    PHYSICAL_WORK = "physical_work"
    FREELANCE = "freelance"
    LIFEHACKS = "lifehacks"
    TIPS = "tips"

class ArticleSortEnum(str, Enum):
    DATE_ASC = "asc"
    DATE_DESC = "desc"

