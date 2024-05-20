from flask import Flask, request

app = Flask(__name__)

@app.route("/", methods=['GET'])
def handle_get():
    domain = request.args.get('Host', 'Unknown domain')  # Assuming domain is passed as a query parameter
    response_message = f"Domain {domain} received"
    return response_message

@app.errorhandler(500)
def handle_500_error(e):
    return f"Internal server error: {e}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
