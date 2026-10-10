from flask import Flask, render_template, request
import datetime
import urllib.request
import urllib.parse
import json
import pyttsx3


app = Flask(__name__)

# -----------------------------
# ChatBot Memory
# -----------------------------
responses = {
    "hi": "Hello! I am a smart Chatbot to help you",
    "hello": "Hi, welcome! How can I help you?",
    "how are you": "I am very fine, thank you!",
    "who are you": "I am a Smart ChatBot.",
    
}

# -----------------------------
# Step 1: look in my own memory
# -----------------------------
def getresponses(userQuestion):
    userQuestion = userQuestion.lower()
    for eachkey in responses:
        if eachkey in userQuestion:
            return responses[eachkey]
    return None   # nothing found


# -----------------------------
# Step 2: if not found, search Wikipedia
# -----------------------------
def search_wikipedia(question):
    headers = {"User-Agent": "SmartChatBot/1.0 (student project)"}

    # remove common starting words so the search works better
    cleaned = question.lower()
    for word in ["what is", "who is", "what are", "tell me about", "explain", "?"]:
        cleaned = cleaned.replace(word, "")
    cleaned = cleaned.strip()

    if not cleaned:
        return None


def wiki_get(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": "SmartChatBot/1.0 (student project)"}
    )
    with urllib.request.urlopen(req, timeout=8) as r:
        return json.loads(r.read().decode("utf-8"))


def search_wikipedia(question):
    cleaned = question.lower()
    for word in ["what is", "who is", "what are", "tell me about", "explain", "?"]:
        cleaned = cleaned.replace(word, "")
    cleaned = cleaned.strip()

    if not cleaned:
        return None

    try:
        q = urllib.parse.quote(cleaned)
        data = wiki_get(
            "https://en.wikipedia.org/w/api.php?action=query&list=search"
            "&srsearch=" + q + "&format=json&srlimit=1"
        )

        results = data["query"]["search"]
        if not results:
            print("WIKIPEDIA: no results for", cleaned)
            return None

        title = results[0]["title"]
        page = wiki_get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/"
            + urllib.parse.quote(title.replace(" ", "_"))
        )

        text = page.get("extract")
        if not text:
            return None

        sentences = text.split(". ")
        return ". ".join(sentences[:2]).strip() + "."

    except Exception as e:
        print("WIKIPEDIA ERROR:", e)   # shows the real problem in the terminal
        return None

    # Initialize voice engine
engine = pyttsx3.init()
engine.setProperty("rate", 160)



# -----------------------------
# Main reply function
# -----------------------------
def get_bot_reply(question):
    answer = getresponses(question)          # my own answers first

    if answer is None:
        answer = search_wikipedia(question)  # then search online

    if answer is None:
        answer = "Sorry, I could not find an answer to that."

    return answer


# -----------------------------
# Greeting according to time
# -----------------------------
def get_greeting(name):
    presentHour = datetime.datetime.now().hour

    if 0 <= presentHour < 12:
        return f"Good Morning, {name}!"
    elif 12 <= presentHour < 17:
        return f"Good Afternoon, {name}!"
    else:
        return f"Good Evening, {name}!"


# -----------------------------
# Home Page
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    greeting = ""
    bot_response = ""
    name = ""

    if request.method == "POST":
        name = request.form.get("name", "")
        user_input = request.form.get("question", "")

        if name:
            greeting = get_greeting(name)

        if user_input:
            if "bye" in user_input.lower():
                bot_response = "Goodbye! Thank you for chatting with me. 👋"
            else:
                bot_response = get_bot_reply(user_input)

    return render_template(
        "index.html",
        greeting=greeting,
        bot_response=bot_response,
        name=name
    )


if __name__ == "__main__":
    app.run(debug=True)