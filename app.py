from flask import Flask, render_template, request, jsonify
from services.social_api import (
    get_posts, get_post, get_post_comments,
    get_users, get_user, get_user_posts, get_stats
)
from services.translate_api import translate_to_spanish
from services.stadiums_api  import get_location_by_ip, geocode_city, get_stadiums_near

app = Flask(__name__)

# ── SOCIAL ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html", posts=get_posts(20))

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    return render_template("post.html",
                           post=get_post(post_id),
                           comments=get_post_comments(post_id))

@app.route("/users")
def users():
    return render_template("user.html", users=get_users(20))

@app.route("/user/<int:user_id>")
def user_detail(user_id):
    return render_template("user.html",
                           user=get_user(user_id),
                           posts=get_user_posts(user_id),
                           detail=True)

@app.route("/stats")
def stats():
    return render_template("stats.html", data=get_stats())

# ── TRADUCCIÓN ───────────────────────────────────────────────────────────────
@app.route("/translate")
def translate_page():
    return render_template("translate.html")

@app.route("/api/translate", methods=["POST"])
def api_translate():
    data = request.get_json()
    text = data.get("text", "").strip()
    if not text:
        return jsonify({"error": "Texto vacío"}), 400
    return jsonify(translate_to_spanish(text))

# ── ESTADIOS ─────────────────────────────────────────────────────────────────
@app.route("/stadiums")
def stadiums_page():
    # Detectar ciudad por IP al cargar la página
    location = get_location_by_ip()
    stadiums = []
    search_city = ""
    radius = 50

    city_param = request.args.get("city", "").strip()
    radius_param = int(request.args.get("radius", 50))

    if city_param:
        geo = geocode_city(city_param)
        if geo["success"]:
            stadiums   = get_stadiums_near(geo["lat"], geo["lon"], radius_param)
            search_city = city_param
            radius      = radius_param
            location    = {**location, "city": city_param, "lat": geo["lat"], "lon": geo["lon"]}
    elif location.get("success"):
        stadiums = get_stadiums_near(location["lat"], location["lon"], radius_param)
        radius   = radius_param

    return render_template("stadiums.html",
                           location=location,
                           stadiums=stadiums,
                           search_city=search_city,
                           radius=radius)

@app.route("/api/stadiums")
def api_stadiums():
    city   = request.args.get("city", "").strip()
    radius = int(request.args.get("radius", 50))
    if not city:
        return jsonify({"error": "Ciudad requerida"}), 400
    geo = geocode_city(city)
    if not geo["success"]:
        return jsonify({"error": geo.get("error", "No encontrada")}), 404
    stadiums = get_stadiums_near(geo["lat"], geo["lon"], radius)
    return jsonify({"stadiums": stadiums, "location": geo})

if __name__ == "__main__":
    app.run(debug=True)