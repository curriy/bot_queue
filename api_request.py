import requests
import json
import datetime


day_map = {
    "Понедельник": 1,
    "Вторник": 2,
    "Среда": 3,
    "Четверг": 4,
    "Пятница": 5,
    "Суббота": 6,
    "Воскресенье": 7,
}

def date_regulate(n):
    today = datetime.date.today()
    delta = n - today.weekday()
    result = (datetime.datetime.now() + datetime.timedelta(days=delta)).strftime("%d.%m")
    return result


def get_subjects():
    try:
        current_week = requests.get('https://iis.bsuir.by/api/v1/schedule/current-week')
        current_week.raise_for_status()
        res = requests.get('https://iis.bsuir.by/api/v1/schedule?studentGroup=373904')
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return []

    try:
        data = json.loads(res.text)
        week = json.loads(current_week.text)

        schedules = data.get("schedules", {})
        total_list = []

        for day in schedules:
            lessons = schedules[day]
            for lesson in lessons:
                if week in lesson.get("weekNumber", []):
                    if lesson.get("lessonTypeAbbrev") == 'ЛР':
                        less = lesson.get("subject", "")
                        subgroup = f'({lesson.get("numSubgroup")})' if lesson.get("numSubgroup") else ""
                        less += subgroup + f' {date_regulate(day_map[day])}'
                        total_list.append(less)

        return total_list
    except json.JSONDecodeError as e:

        print(f"Error parsing JSON data: {e}")
        return []
