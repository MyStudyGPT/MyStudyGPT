from flask import Flask, request, abort
from bot import process_webhook_update
from config import TELEGRAM_TOKEN

app = Flask(__name__)

@app.route(f"/webhook/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        process_webhook_update(request.get_json())
        return '', 200
    else:
        abort(403)