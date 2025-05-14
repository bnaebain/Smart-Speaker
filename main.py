import json
from chatgpt_handler import ask_chatgpt, get_weather_commentary
from weather_handler import get_weather, get_weather_summary, get_weekend_weather_summary
from spotify_handler import play, pause, skip, current_track
from maps_handler import get_travel_time


print("💬 Welcome to your smart speaker POC. Type 'exit' to quit.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        break

    try:
        raw_response = ask_chatgpt(user_input)

        response_json = json.loads(raw_response)
        intent = response_json.get("intent")

        if intent == "get_weather":
            day_offset = int(response_json.get("day_offset", 1))
            day_offset = max(0, min(day_offset, 4))
            if day_offset > 4:
                print("🌧️ Sorry, I can only look ahead 5 days. Try asking for a day this week.")
            else:
                print("🌦", get_weather(day_offset))

        elif intent == "get_weather_summary":
            summary = get_weather_summary()
            print("📆", summary)
            print("💬", get_weather_commentary(summary))
        elif intent == "get_weather_weekend":
            print("📆", get_weekend_weather_summary())
            print("💬", get_weather_commentary(get_weekend_weather_summary()))
        elif intent == "spotify_play":
            try:
                query = response_json.get("query", "").strip()  # 👈 This is key
                message = play(query)
                print(message)
            except Exception as e:
                print(f"⚠️ Couldn’t play music: {e}")

        elif intent == "spotify_pause":
            pause()
            print("⏸ Music paused.")

        elif intent == "spotify_skip":
            skip()
            print("⏭ Skipping to the next track.")

        elif intent == "spotify_status":
            print("🎶", current_track())
        
        elif intent == "maps_travel_time":
            destination = response_json.get("destination", "Target, Chicago")
            departure = response_json.get("departure_time")
            print("🗺️", get_travel_time(destination, departure))

        elif intent == "chat":
            print("🤖", response_json.get("response"))
        else:
            print(f"🤖 I didn’t understand that (intent: {intent})")

    except Exception as e:
        print(f"⚠️ Error: {e}")