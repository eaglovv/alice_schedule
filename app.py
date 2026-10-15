from flask import Flask, request, jsonify
import datetime
from zoneinfo import ZoneInfo

app = Flask(__name__)

TIMEZONE = ZoneInfo("Asia/Yekaterinburg")

REFERENCE_MONDAY = datetime.date(2026, 10, 12)

PAIR_TIMES = {


    1: "к первой паре к 8:00",


    2: "ко второй паре к 9:40",


    3: "к третьей паре к 11:30",


    4: "к четвёртой паре к 13:20",


    5: "к пятой паре к 15:00",


    6: "к шестой паре к 16:40",


}

SCHEDULE = {
    "odd": {
        0: (
            1,
            "Всего две пары: в 8:00 иностранный язык в 114-й аудитории корпуса А, "
            "а в 9:40 — прикладная физкультура."
        ),
        1: (
            2,
            "Всего три пары: в 9:40 введение в инженерную деятельность в 229-й корпуса А, "
            "в 11:30 лекция по математике в 5б корпуса Д, "
            "и в 13:20 лекция по физкультуре в 6б корпуса Д."
        ),
        2: (
            4,
            "Можно выспаться! Три пары в 6б корпуса Д: в 13:20 лекция по основам российской государственности, "
            "в 15:00 лекция по истории России, и в 16:40 практика по государственности."
        ),
        3: (
            2,
            "Всего три пары: в 9:40 и в 11:30 — две практики подряд по математике в 104-й корпуса В, "


            "затем в 13:20 практика по учебно-исследовательской работе в 127-й корпуса А."


        ),


        4: (


            2,


            "Четыре пары: в 9:40 физкультура, в 11:30 лекция по дискретной математике в 402-й корпуса А, "


            "в 13:20 лаба по основам алгоритмизации в 409-й корпуса А, и в 15:00 лаба по информатике там же."


        ),


        5: (None, "В субботу пар нет, отдыхай!"),


        6: (None, "В воскресенье выходной, набирайся сил.")


    },


    "even": {


        0: (


            1,


            "Всего две пары: в 8:00 иностранный язык в 114-й аудитории корпуса А, "


            "а в 9:40 — прикладная физкультура."


        ),


        1: (


            2,


            "По чётной неделе только две пары: в 9:40 введение в инженерную деятельность в 229-й корпуса А, "


            "и в 11:30 лекция по математике в 5б корпуса Д."


        ),


        2: (


            3,


            "Четыре пары: в 11:30 практика по дискретной математике в 406-й корпуса А, "


            "затем в 6б корпуса Д три пары подряд: в 13:20 практика по истории, "


            "в 15:00 лекция по истории и в 16:40 практика по государственности."


        ),


        3: (


            2,


            "Четыре лекции: в 9:40 учебно-исследовательская работа в 416-й корпуса А, "


            "а дальше три лекции в 5б корпуса Д: в 11:30 информатика, "


            "в 13:20 основы алгоритмизации и в 15:00 введение в инженерную деятельность."


        ),


        4: (


            2,


            "Четыре пары: в 9:40 физкультура, в 11:30 лекция по дискретной математике в 402-й корпуса А, "


            "в 13:20 лаба по основам алгоритмизации в 409-й корпуса А, и в 15:00 лаба по информатике там же."


        ),


        5: (None, "В субботу пар нет, чиллим!"),


        6: (None, "В воскресенье выходной!")


    }


}





DAYS_RU = {


    0: "в понедельник",


    1: "во вторник",


    2: "в среду",


    3: "в четверг",


    4: "в пятницу",


    5: "в субботу",


    6: "в воскресенье"


}





WEEKDAY_KEYWORDS = {


    "понедельник": 0,


    "вторник": 1,


    "сред": 2,


    "четверг": 3,


    "пятниц": 4,


    "суббот": 5,


    "воскресен": 6


}








def get_week_type(target_date: datetime.date) -> str:


    """Вычисляет чётная или нечётная неделя относительно 12 октября 2026."""


    # Находим понедельник той недели, к которой относится target_date


    target_monday = target_date - datetime.timedelta(days=target_date.weekday())


    weeks_passed = (target_monday - REFERENCE_MONDAY).days // 7


    # weeks_passed == 0 -> 1-я нечётная неделя ("odd"), weeks_passed == 1 -> чётная ("even") и т.д.


    return "odd" if weeks_passed % 2 == 0 else "even"








def resolve_target_date(command: str, today: datetime.date):


    """Определяет, про какой день спрашивает пользователь."""


    if "послезавтра" in command:


        return today + datetime.timedelta(days=2), "Послезавтра"


    if "сегодня" in command:


        return today, "Сегодня"





    for stem, wd in WEEKDAY_KEYWORDS.items():


        if stem in command:


            days_ahead = (wd - today.weekday()) % 7


            if days_ahead == 0:


                days_ahead = 7


            return today + datetime.timedelta(days=days_ahead), "Ближайший день —"





    return today + datetime.timedelta(days=1), "Завтра"








@app.route("/alice", methods=["POST"])


def alice_webhook():


    data = request.json or {}


    command = data.get("request", {}).get("original_utterance", "").lower()





    today = datetime.datetime.now(TIMEZONE).date()


    target_date, prefix = resolve_target_date(command, today)





    weekday = target_date.weekday()


    week_type = get_week_type(target_date)


    week_label = "нечётная неделя" if week_type == "odd" else "чётная неделя"


    day_name = DAYS_RU[weekday]





    first_pair, details = SCHEDULE[week_type][weekday]





    if first_pair is None:


        answer = f"{prefix} {day_name} — пар нет! {details}"


    else:


        pair_time = PAIR_TIMES[first_pair]


        answer = f"{prefix} {day_name} ({week_label}) тебе {pair_time}. {details}"





    return jsonify({
        "version": "1.0",
        "response": {
            "text": answer,
            "tts": answer,
            "end_session": True
        }


    })

if __name__ == "__main__":
    
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'ok'}), 200
    
    app.run(host="0.0.0.0", port=5000)


