import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from gtts import gTTS
import pygame
import os
import openai
from datetime import datetime

# Initialize components
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Conversation history with enhanced memory prompt
conversation_history = [
    {
        "role": "system", 
        "content": """You are Luca, a bilingual(nepali,english) assistant. Remember these rules:
        1. Maintain conversation context between interactions
        2. Remember personal details like names, preferences, and important facts
        3. Acknowledge when you're told to remember something
        4. Keep responses under 2 sentences unless asked for more"""
    }
]

def speak(text):
    tts = gTTS(text)
    tts.save('temp.mp3')
    pygame.mixer.init()
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    pygame.mixer.music.unload()
    os.remove("temp.mp3")

def aiProcess(command):
    global conversation_history
    try:
        client = openai.OpenAI(api_key=os.getenv("myfirstkey"))
        
        # Update conversation history
        conversation_history.append({"role": "user", "content": command})
        
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_history,
            temperature=0.7,
            max_tokens=150
        )
        
        response = completion.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": response})
        
        return response
    except Exception as e:
        return f"Error processing request: {str(e)}"

def processCommand(command):
    global conversation_history
    
    # Special commands
    if "go to sleep" in command.lower():
        speak("Goodbye! Say 'Luca' to wake me up.")
        return "sleep"
    
    if "reset memory" in command.lower():
        conversation_history = conversation_history[:1]
        speak("Memory cleared. What can I help you with?")
        return
    
    # Standard commands
    if "open google" in command.lower():
        webbrowser.open("https://google.com")
        return
    
    if "open youtube" in command.lower():
        webbrowser.open("https://youtube.com")
        return
    
    if command.lower().startswith("play"):
        try:
            song = command.lower().split(" ", 1)[1]
            webbrowser.open(musicLibrary.music.get(song, ""))
        except:
            speak("Song not found in library")
        return
    
    if any(phrase in command.lower() for phrase in ["news", "headlines"]):
        news_api = os.getenv("news_api")
        if news_api:
            try:
                response = requests.get(f"https://newsapi.org/v2/top-headlines?country=us&apiKey={news_api}")
                if response.status_code == 200:
                    articles = response.json().get('articles', [])[:5]  # Limit to 5 headlines
                    for article in articles:
                        speak(article['title'])
                        # Check for stop command
                        try:
                            with sr.Microphone() as source:
                                audio = recognizer.listen(source, timeout=1)
                                if "stop" in recognizer.recognize_google(audio).lower():
                                    speak("Stopping news updates")
                                    return
                        except:
                            continue
                else:
                    speak("Failed to fetch news updates")
            except Exception as e:
                speak(f"News error: {str(e)}")
        return
    
    if any(phrase in command.lower() for phrase in ["time", "clock"]):
        current_time = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
        return
    
    # Default AI processing
    response = aiProcess(command)
    speak(response)

if __name__ == "__main__":
    speak("Initializing Luca...")
    active = False
    
    while True:
        try:
            with sr.Microphone() as source:
                if not active:
                    print("Waiting for wake word...")
                    audio = recognizer.listen(source, timeout=3)
                    try:
                        wake_word = recognizer.recognize_google(audio).lower()
                        if "luca" in wake_word:
                            active = True
                            speak("How can I help you?")
                    except:
                        pass
                else:
                    print("Listening for command...")
                    audio = recognizer.listen(source, phrase_time_limit=7)
                    try:
                        command = recognizer.recognize_google(audio)
                        print("You:", command)
                        
                        result = processCommand(command)
                        if result == "sleep":
                            active = False
                    except sr.UnknownValueError:
                        speak("Could you repeat that?")
                    except Exception as e:
                        print(f"Error: {str(e)}")
                        speak("There was an error processing your request")
        
        except KeyboardInterrupt:
            speak("Shutting down...")
            break
        except Exception as e:
            print(f"System error: {str(e)}")