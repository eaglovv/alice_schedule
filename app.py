def resolve_target_date(command: str, today: datetime.date):
    """Определяет, про какой день спрашивает пользователь. 
    Возвращает (дата, префикс) или (None, None), если день не распознан."""
    if "послезавтра" in command:
        return today + datetime.timedelta(days=2), "Послезавтра"
    if "сегодня" in command:
        return today, "Сегодня"
    if "завтра" in command:
        return today + datetime.timedelta(days=1), "Завтра"

    for stem, wd in WEEKDAY_KEYWORDS.items():
        if stem in command:
            days_ahead = (wd - today.weekday()) % 7
            if days_ahead == 0 and "следующ" in command:
                days_ahead = 7
            return today + datetime.timedelta(days=days_ahead), "В ближайший указанный день —"

    # Если ни одно ключевое слово не найдено, возвращаем None
    return None, None

@app.route("/alice", methods=["POST"])
def alice_webhook():
    data = request.json or {}
    command = data.get("request", {}).get("original_utterance", "").lower()
    is_new_session = data.get("session", {}).get("new", False)

    # Проверка на новую сессию (самый первый запуск навыка)
    if is_new_session or not command.strip():
        answer = "Привет! Я твой личный помощник по расписанию занятий. Спроси меня, например: 'Что завтра?' или 'Какие пары в четверг?'"
        return jsonify({
            "version": "1.0",
            "response": {
                "text": answer,
                "tts": answer,
                "end_session": False
            }
        })

    today = datetime.datetime.now(TIMEZONE).date()
    target_date, prefix = resolve_target_date(command, today)

    # Если пользователь написал то, что мы не смогли распознать
    if target_date is None:
        answer = "Я тебя не совсем поняла. Повтори, пожалуйста, вопрос про расписание или конкретный день недели."
        return jsonify({
            "version": "1.0",
            "response": {
                "text": answer,
                "tts": answer,
                "end_session": False
            }
        })

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
            "end_session": False
        }
    })
