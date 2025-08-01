from flask import Flask, request, jsonify
import threading, time, requests, logging, os
from byte import Encrypt_ID, encrypt_api

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
app.logger.setLevel(logging.INFO)

RAW_TOKENS = [
    ("4067715006", "C6B714258ACBB566DF8609843FB2CC523412D80F4B95E3DAA1A9B983E34244E7"),
    # أضف المزيد إن أردت
]

JWT_TOKENS = {}

def get_author_info():
    return "🔥 API BY XZANJA 🔥"

def fetch_jwt(uid, password):
    try:
        response = requests.get(f"https://jwt-gen-api-v2.onrender.com/token?uid={uid}&password={password}")
        if response.status_code == 200:
            return response.json().get("jwt")
        else:
            app.logger.error(f"❌ فشل في جلب JWT لـ UID {uid}")
            return None
    except Exception as e:
        app.logger.error(f"❌ خطأ أثناء جلب JWT: {e}")
        return None

def update_all_jwt_tokens():
    while True:
        for uid, raw in RAW_TOKENS:
            jwt = fetch_jwt(uid, raw)
            if jwt:
                JWT_TOKENS[uid] = jwt
        time.sleep(1)

def send_friend_request(target_uid, jwt_token):
    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1801"
        encrypted_payload = encrypt_api(payload)
        url = "https://clientbp.ggblueshark.com/RequestAddingFriend"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB49",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(encrypted_payload)),
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "close",
            "Accept-Encoding": "gzip, deflate, br"
        }
        res = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload))
        return res.status_code == 200
    except Exception as e:
        app.logger.error(f"🚫 إرسال فاشل: {e}")
        return False

def remove_friend_request(target_uid, jwt_token):
    try:
        encrypted_id = Encrypt_ID(target_uid)
        payload = f"08a7c4839f1e10{encrypted_id}1802"
        encrypted_payload = encrypt_api(payload)
        url = "https://clientbp.ggblueshark.com/RemoveFriend"
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "X-Unity-Version": "2018.4.11f1",
            "X-GA": "v1 1",
            "ReleaseVersion": "OB49",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(encrypted_payload)),
            "User-Agent": "Dalvik/2.1.0 (Linux; Android 9)",
            "Host": "clientbp.ggblueshark.com",
            "Connection": "close",
            "Accept-Encoding": "gzip, deflate, br"
        }
        res = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload))
        return res.status_code == 200
    except Exception as e:
        app.logger.error(f"🚫 حذف فاشل: {e}")
        return False

def infinite_spam_loop(target_uid):
    count = 0
    while True:
        for uid, _ in RAW_TOKENS:
            jwt = JWT_TOKENS.get(uid)
            if not jwt:
                continue
            sent = send_friend_request(target_uid, jwt)
            if sent:
                removed = remove_friend_request(target_uid, jwt)
                status = "✅" if removed else "⚠️ لم يُحذف"
            else:
                status = "❌ فشل الإرسال"
            count += 1
            print(f"[{status}] #{count} من UID {uid} إلى {target_uid}")
            time.sleep(0.15)

@app.route("/m9", methods=["GET", "POST"])
def start_spam():
    try:
        target_uid = request.args.get("uid") if request.method == "GET" else request.json.get("uid")
        if not target_uid:
            return jsonify({"error": "⚠️ UID مفقود", "developer": get_author_info()}), 400

        threading.Thread(target=infinite_spam_loop, args=(target_uid,), daemon=True).start()

        return jsonify({
            "status": "🚀 بدأ السبام",
            "target_uid": target_uid,
            "developer": get_author_info()
        }), 200
    except Exception as e:
        app.logger.error(f"❌ خطأ في /m9: {str(e)}", exc_info=True)
        return jsonify({"error": "❌ خطأ داخلي", "details": str(e)}), 500

if __name__ == "__main__":
    threading.Thread(target=update_all_jwt_tokens, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))