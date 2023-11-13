import requests
import json
import datetime


def date_regulate(n):
    today = datetime.date.today()
    delta = n - today.weekday()
    result = (datetime.datetime.now() + datetime.timedelta(days=delta)).strftime("%d.%m")
    return result


def get_subjects():
    current_week = requests.get('https://iis.bsuir.by/api/v1/schedule/current-week')
    res = requests.get('https://iis.bsuir.by/api/v1/schedule?studentGroup=373904')
    data = json.loads(res.text)
    week = json.loads(current_week.text)
    wednesday = data["schedules"]["Среда"]
    thursday = data["schedules"]["Четверг"]
    friday = data["schedules"]["Пятница"]
    saturday = data["schedules"]["Суббота"]
    total_list = []

    for i in range(len(wednesday)):
        if week in wednesday[i]["weekNumber"]:
            if wednesday[i]["lessonTypeAbbrev"] == 'ЛР':
                less = wednesday[i]["subject"]
                if wednesday[i]["numSubgroup"] == 1:
                    less += '(1)'
                elif wednesday[i]["numSubgroup"] == 2:
                    less += '(2)'
                less += f' {date_regulate(2)}'

                total_list.append(less)

    for i in range(len(thursday)):
        if week in thursday[i]["weekNumber"]:
            if thursday[i]["lessonTypeAbbrev"] == 'ЛР':
                less = thursday[i]["subject"]
                if thursday[i]["numSubgroup"] == 1:
                    less += '(1)'
                elif thursday[i]["numSubgroup"] == 2:
                    less += '(2)'
                less += f' {date_regulate(3)}'

                total_list.append(less)

    for i in range(len(friday)):
        if week in friday[i]["weekNumber"]:
            if friday[i]["lessonTypeAbbrev"] == 'ЛР':
                less = friday[i]["subject"]
                if friday[i]["numSubgroup"] == 1:
                    less += '(1)'
                elif friday[i]["numSubgroup"] == 2:
                    less += '(2)'
                less += f' {date_regulate(4)}'

                total_list.append(less)

    for i in range(len(saturday)):
        if week in saturday[i]["weekNumber"]:
            if saturday[i]["lessonTypeAbbrev"] == 'ЛР':
                less = saturday[i]["subject"]
                if saturday[i]["numSubgroup"] == 1:
                    less += '(1)'
                elif saturday[i]["numSubgroup"] == 2:
                    less += '(2)'
                less += f' {date_regulate(5)}'

                total_list.append(less)

    return total_list


print(get_subjects())
