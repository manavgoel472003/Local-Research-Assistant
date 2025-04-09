from flask import Flask, request, render_template, redirect, url_for, jsonify
from local_research_agent import inference  # Ensure this import matches your module

app = Flask(__name__)

# This route displays the main chat interface.
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    query = ""
    if request.method == "POST":
        query = request.form.get("query", "").strip()
        if query:
            try:
                # Log the incoming query
                app.logger.info("Received query: %s", query)
                # Call your inference function with the query text
                result = inference(query)
            except Exception as e:
                app.logger.error("Error processing query: %s", e)
                result = "An error occurred while processing your query. Please try again."
    # Render the updated chat interface with the new prompt and output formatting
    return render_template("index.html", result=result, query=query)

# Optional: API endpoint for asynchronous requests (e.g., AJAX)
@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.get_json() or {}
    query = data.get("query", "").strip()
    if query:
        try:
            result = inference(query)
            return jsonify({"result": result})
        except Exception as e:
            app.logger.error("API error: %s", e)
            return jsonify({"error": "An error occurred processing your query"}), 500
    return jsonify({"error": "No query provided"}), 400

if __name__ == "__main__":
    app.run(debug=True)
