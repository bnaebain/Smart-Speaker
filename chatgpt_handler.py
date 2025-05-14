import openai
from config import OPENAI_API_KEY
import json
from datetime import datetime

# ✅ Make sure this is defined at the top
client = openai.OpenAI(api_key=OPENAI_API_KEY)

today = datetime.now().strftime("%A")

def ask_chatgpt(prompt):
    system_prompt = f"""
You are a smart assistant for a home voice control system. Today is {today}.

If the user asks about the weather:

- For specific days (like "Thursday" or "Sunday"), return:
  {{
    "intent": "get_weather",
    "day_offset": N
  }}

- If the user asks about **this weekend** (Saturday or Sunday), return:
  {{
    "intent": "get_weather_weekend"
  }}

- If the user asks about this week, the next few days, or a general forecast,
  return:
  {{
    "intent": "get_weather_summary"
  }}

If the date is more than 4 days away (like “next Friday”), respond with:
  {{
    "intent": "out_of_range"
  }}

For music commands:

If the user says something like:

- "play music"
- "play Muse"
- "play Hozier"
- "play my chill playlist"
- "play jazz"

    Return a JSON object like this:

    {{
    "intent": "spotify_play",
    "query": "<the exact artist, playlist, track, or genre they mentioned>"
    }}

    Examples:
    - "play music" → query = "music"
    - "play Muse" → query = "Muse"
    - "play artist Hozier" → query = "Hozier"
    - "play my workout mix" → query = "my workout mix"
    - "play something chill" → query = "chill"

- If they say "pause music", return:
  {{
    "intent": "spotify_pause"
  }}

- If they say "skip", return:
  {{
    "intent": "spotify_skip"
  }}

- If they ask "what's playing", return:
  {{
    "intent": "spotify_status"
  }}

If the user asks how far something is or how long it takes to get somewhere, return:

{{
  "intent": "maps_travel_time",
  "destination": "<place they mentioned>"
}}

Examples:
- "How far is Target?" → destination = "Target"
- "How long to get to work?" → destination = "work"
- "How long to get to the gym?" → destination = "gym"
- "How far is O'Hare?" → destination = "O'Hare airport"

If the user asks how long it takes to get somewhere at a specific time (e.g., "How long to get to work at 8:30am"), return:

{{
  "intent": "maps_travel_time",
  "destination": "work",
  "departure_time": "08:30"
}}

Use lowercase names for known aliases like "work", "home", "gym" so they can be resolved internally.

For anything else, return:
  {{
    "intent": "chat",
    "response": "..."
  }}


Only return valid JSON. Do not include day names or explanations.
"""
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {"role": "user", "content": prompt}
        ],
        timeout=10
    )
    return response.choices[0].message.content

def get_weather_commentary(summary_text):
    prompt = f"""
You are a friendly weather assistant. Given a 5-day forecast, generate a brief, natural-sounding summary highlighting key points.

Respond like you're talking to a human, and use clear, conversational English. Mention rain days, clear days, temperature trends, etc.

Only respond in this JSON format:
{{
  "intent": "chat",
  "response": "your commentary here"
}}

Here’s the 5-day forecast:
\"\"\"
{summary_text}
\"\"\"
"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": "You're a helpful weather assistant."},
            {"role": "user", "content": prompt.strip()}
        ],
        timeout=10
    )

    return json.loads(response.choices[0].message.content)["response"]