from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from groq import Groq
from dotenv import load_dotenv
import os
import re


load_dotenv()

chatbot_bp = Blueprint("chatbot", __name__)

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = (
    "You are a supportive and empathetic assistant in a mental wellbeing app. "
    "Be kind, positive, and encouraging. "
    "Never give medical advice, diagnoses, or discuss self-harm/suicide. "
    "If such topics come up, respond with a safe fallback message."
)

FALLBACK_MESSAGE = (
    "I care about your safety. I cannot provide medical or crisis advice. "
    "If you’re struggling, please reach out to a trusted friend, family member, "
    "or a qualified professional. If this is an emergency, please call your local emergency number immediately."
)

@chatbot_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    body = request.get_json(silent=True) or {}
    user_msg = (body.get("message") or "").strip()

    if not user_msg:
        return jsonify({"error": "message is required"}), 400

    try:
        chat_completion = client.chat.completions.create(
            model="deepseek-r1-distill-llama-70b",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
        )
        reply = chat_completion.choices[0].message.content.strip()
        # Remove <think>...</think> blocks if present
        reply = re.sub(r"<think>.*?</think>", "", reply, flags=re.DOTALL).strip()
    except Exception as e:
        print("Groq error:", e)
        reply = "Sorry, I’m having trouble responding right now. Try again later."

    return jsonify({"reply": reply})