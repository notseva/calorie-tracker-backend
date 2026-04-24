from flask import Flask, request, jsonify
from flask_cors import CORS
import anthropic, json, re, os

app = Flask(__name__)
CORS(app)
client = anthropic.Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        img = data.get('image', '')
        mt = data.get('media_type', 'image/jpeg')
        if ',' in img:
            img = img.split(',')[1]
        r = client.messages.create(
            model='claude-opus-4-6',
            max_tokens=500,
            messages=[{'role': 'user', 'content': [
                {'type': 'image', 'source': {'type': 'base64', 'media_type': mt, 'data': img}},
                {'type': 'text', 'text': 'Return ONLY JSON: {"food":"Russian name","ingredients":"list","portion":"~Xg","kcal":0,"protein":0,"fat":0,"carbs":0,"confidence":95}'}
            ]}]
        )
        text = r.content[0].text.strip()
        m = re.search(r'{[\s\S]*}', text)
        if not m:
            raise ValueError('No JSON')
        return jsonify({'success': True, 'data': json.loads(m.group())})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
