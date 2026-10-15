from flask import Flask, request, jsonify

app = Flask(__name__)

# Эндпоинт для проверки здоровья (решает проблему с 404 на Render)
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

# Основной эндпоинт для связи с Алисой
@app.route('/alice', methods=['POST'])
def main():
    req = request.json
    command = req.get('request', {}).get('command', '').lower()
    
    response_text = "Сессия завершена"
    
    # Твоя логика ответов на запросы про расписание и пары
    if "завтра" in command or "паре" in command or "расписание" in command or "какой" in command:
        response_text = "Завтра в пятницу (нечётная неделя) тебе ко второй паре к 9:40. Четыре пары: в 9:40 физкультура, в 11:30 лекция по дискретной математике в 402-й корпуса А, в 13:20 лаба по основам алгоритмизации в 409-й корпуса А, и в 15:00 лаба по информатике там же."
    else:
        response_text = "Сессия завершена"

    return jsonify({
        "response": {
            "text": response_text,
            "tts": response_text,
            "end_session": False
        },
        "version": "1.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
