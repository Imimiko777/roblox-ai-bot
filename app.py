from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Ключ будем брать из переменной окружения (так безопаснее)
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-твой_ключ_сюда_если_не_используешь_переменную")

# Системный промпт — объясняем DeepSeek, как себя вести
SYSTEM_PROMPT = """
Ты — ИИ-помощник в игре Roblox. Ты можешь общаться с игроками и выполнять команды по управлению игрой.
Игрок пишет тебе сообщение. Твоя задача — понять, хочет ли он просто поболтать или отдать команду.

Если это команда (например, "телепортируй меня", "создай куб", "дай мне меч"), ты должен ответить JSON-объектом с полем "type": "command" и дополнительными полями, описывающими команду.
Если это обычный разговор, ответь JSON-объектом с "type": "chat" и полем "message" с текстом ответа.

Примеры команд:
- {"type": "command", "command": "teleport", "destination": "spawn"}
- {"type": "command", "command": "create_part", "color": "red", "size": [4,1,2]}
- {"type": "command", "command": "give_item", "item": "sword"}

Для обычного ответа: {"type": "chat", "message": "Привет! Чем могу помочь?"}

Отвечай только JSON-объектом, без лишних пояснений.
"""

@app.route('/ask', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        player_name = data.get('player_name', 'Unknown')
        
        if not user_message:
            return jsonify({'error': 'No message'}), 400

        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': SYSTEM_PROMPT},
                {'role': 'user', 'content': f"Игрок {player_name} говорит: {user_message}"}
            ]
        }

        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            ai_reply = result['choices'][0]['message']['content']
            try:
                reply_json = json.loads(ai_reply)
            except:
                reply_json = {"type": "chat", "message": ai_reply}
            
            return jsonify(reply_json)
        else:
            return jsonify({'error': 'DeepSeek API error'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
