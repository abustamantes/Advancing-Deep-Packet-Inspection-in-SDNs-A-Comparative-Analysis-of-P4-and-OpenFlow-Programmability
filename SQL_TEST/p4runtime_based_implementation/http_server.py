from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=['GET'])
def hello_world():
    app.logger.info(f"Connection attempt from {request.remote_addr}")
    print("We just got a GET consult!")
    return "Hello, World!"

@app.route("/data", methods=['POST'])
def receive_data():
    # Check if the request has JSON data
    if request.is_json:
        # Parse the JSON data
        data = request.get_json()
        app.logger.info(f"Received data: {data}")
        # You can process the data here as needed
        print(f"Message received: {data}")
        return jsonify({"message": "Data received", "data": data}), 200
    else:
        return jsonify({"message": "Request must be JSON"}), 400

@app.errorhandler(500)
def handle_500_error(e):
    app.logger.error(f"Server error: {e}")
    return "Internal server error", 500

if __name__ == "__main__":
    # Setup the basic logger configuration
    import logging
    logging.basicConfig(filename='app.log', level=logging.INFO)

    # Specify the host and port number you wish to run the app on.
    # Default port for HTTP is 80. Here, we're using the commonly used port for development, 5000.
    app.run(host="0.0.0.0", port=80, debug=True)
