from flask import Flask,jsonify,request,render_template,redirect,url_for
from data_base import user_insert, load_data,get_event
from recommendation import recommend_by_query,recommend_similar_event

app=Flask(__name__)

# home-------------------------------------------------------------------------

@app.route("/",methods=['GET','POST'])
def home():
    if request.method=='POST':
        name=request.form.get('username')
        email=request.form.get('email')
        #password=request.form.get('password')
        if(user_insert(name,email)):
            return redirect(url_for("search",username=name))
    return render_template("home.html")

# helper routes-----------------------------------------------------------------

@app.route("/load_data")
def load_data_route():
    data = load_data()
    return jsonify(data)

@app.route("/<username>/event/<event_id>", methods=['GET'])
def event_details(username, event_id):
    # Fetch user-specific events from the database
    event = get_event(event_id)
    suggestions = recommend_similar_event(event_id)
    return render_template("event_details.html",username=username, event=event, suggestions=suggestions)

# main pages---------------------------------------------------------------------

@app.route("/<username>/search",methods=['GET','POST'])
def search(username):
    return render_template("search.html",username=username)

@app.route("/semantic_search", methods=['POST'])
def semantic_search():
    query=request.json.get('query', '')
    if not query:
        return jsonify([])
    results = recommend_by_query(query,100)
    return jsonify(results)

@app.route("/<username>/recommender",methods=['GET','POST'])
def recommender(username):
    if request.method == 'POST':
        # Handle recommendation logic here
        pass
    return render_template("recommender.html",username=username)

app.run(debug=True)
