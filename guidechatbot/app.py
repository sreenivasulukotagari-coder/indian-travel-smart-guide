from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

travel_data = {
    "andhra pradesh": {
        "low": ["Tirupati", "Srisailam", "Vijayawada", "Lepakshi", "Ahobilam"],
        "medium": ["Visakhapatnam", "Araku Valley", "Rajahmundry", "Papikondalu", "Horsley Hills"],
        "high": ["Luxury Araku Resorts", "Vizag Beach Resorts", "Papikondalu Cruise"]
    },
    "telangana": {
        "low": ["Yadadri", "Warangal Fort", "Basar"],
        "medium": ["Hyderabad Tour", "Nagarjuna Sagar"],
        "high": ["Ramoji Film City"]
    },
    "tamil nadu": {
        "low": ["Madurai", "Rameswaram"],
        "medium": ["Ooty", "Kodaikanal"],
        "high": ["Luxury Hill Resorts"]
    }
}

USERS = ["family", "friends", "solo", "old age"]
BUDGETS = ["low", "medium", "high"]

session = {"started": False, "user": None, "state": None, "budget": None}

# ---------- HELPERS ----------
def normalize(text):
    return " ".join(text.lower().strip().split())

def find_key(user_input, options):
    user_input = normalize(user_input)
    for opt in options:
        if user_input == normalize(opt):
            return opt
    return None

def show_places():
    places = travel_data[session["state"]][session["budget"]]
    reply = f"✨ Places in {session['state'].title()} ({session['budget'].title()} budget):\n"
    for i, p in enumerate(places, 1):
        reply += f"{i}. {p}\n"
    reply += "\nYou can type or say:\nchange user family/friends/solo/old age\nchange budget low/medium/high"
    return jsonify({"reply": reply})

# ---------- ROUTES ----------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    raw_msg = request.json["message"]
    msg = normalize(raw_msg)

    # START
    if not session["started"]:
        if msg == "hi":
            session["started"] = True
            return jsonify({"reply": "Hi 👋 Who are you traveling with? (family / friends / solo / old age)"})
        return jsonify({"reply": "Please type or say HI to start 😊"})

    # CHANGE USER
    if msg.startswith("change user"):
        user = find_key(msg.replace("change user", ""), USERS)
        if not user:
            return jsonify({"reply": "Invalid user type."})
        session["user"] = user
        if session["state"] and session["budget"]:
            return show_places()
        return jsonify({"reply": "User updated 👍 Continue."})

    # CHANGE BUDGET
    if msg.startswith("change budget"):
        budget = find_key(msg.replace("change budget", ""), BUDGETS)
        if not budget:
            return jsonify({"reply": "Invalid budget."})
        session["budget"] = budget
        if session["state"] and session["user"]:
            return show_places()
        return jsonify({"reply": "Budget updated 👍 Continue."})

    # USER
    if not session["user"]:
        user = find_key(msg, USERS)
        if not user:
            return jsonify({"reply": "Choose: family / friends / solo / old age"})
        session["user"] = user
        return jsonify({"reply": "Which state do you want to visit?"})

    # STATE
    if not session["state"]:
        state = find_key(msg, travel_data.keys())
        if not state:
            return jsonify({"reply": "Please say or type a valid state."})
        session["state"] = state
        return jsonify({"reply": "Select budget: low / medium / high"})

    # BUDGET
    if not session["budget"]:
        budget = find_key(msg, BUDGETS)
        if not budget:
            return jsonify({"reply": "Choose budget: low / medium / high"})
        session["budget"] = budget
        return show_places()

    # RESTART
    if msg == "restart":
        session.update({"started": False, "user": None, "state": None, "budget": None})
        return jsonify({"reply": "Restarted 🔄 Type or say HI"})

    return jsonify({"reply": "You can say: change user / change budget / restart"})

if __name__ == "__main__":
    app.run(debug=True)