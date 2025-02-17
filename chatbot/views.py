import json
import os
import openai
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Message
from slack_sdk import WebClient
from slack_sdk.signature import SignatureVerifier
from django.conf import settings 

SLACK_BOT_TOKEN = settings.SLACK_BOT_TOKEN
SLACK_SIGNING_SECRET = settings.SLACK_SIGNING_SECRET
OPENAI_API_KEY = settings.OPENAI_API_KEY 

client = WebClient(token=SLACK_BOT_TOKEN)
verifier = SignatureVerifier(SLACK_SIGNING_SECRET)
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)

@csrf_exempt
def slack_events(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            print("Received payload:", payload)            
            if "challenge" in payload:
                return JsonResponse({"challenge": payload["challenge"]})            
            if "event" in payload:
                event = payload["event"]
                print("Event received:", event)  
                user_id = event.get("user")
                channel_id = event.get("channel")
                user_message = event.get("text")              
                if user_id is None or user_id == "USLACKBOT":
                    return JsonResponse({"status": "ignored"})
                print(f"User ({user_id}) said: {user_message}")               
                response = openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": user_message}]
                )
                bot_reply = response.choices[0].message.content
                print("Bot reply:", bot_reply)              
                client.chat_postMessage(channel=channel_id, text=bot_reply)
            return JsonResponse({"status": "ok"})
        except Exception as e:
            print("Error:", str(e)) 
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "Invalid request method"}, status=400)

    
from django.shortcuts import render
from django.http import JsonResponse
from .models import Message

def chat_history(request):
    messages = Message.objects.all().order_by("-timestamp")[:10]  
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        messages_data = [
            {"user_message": msg.user_message, "bot_response": msg.bot_response}
            for msg in messages
        ]
        return JsonResponse({"messages": messages_data})
    return render(request, "chat_history.html", {"messages": messages})
