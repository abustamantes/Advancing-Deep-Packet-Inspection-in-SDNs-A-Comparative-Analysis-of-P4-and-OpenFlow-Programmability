import requests
import json

def send_get_request(url):
    response = requests.get(url)
    print("Response from GET request:")
    print(response.text)

def send_post_request(url):
    print("Enter your JSON data (in dictionary format, e.g., {'key': 'value'}):")
    user_input = input()
    try:
        data = json.loads(user_input)
    except json.JSONDecodeError:
        print("Invalid JSON. Please enter valid JSON data.")
        return

    response = requests.post(url, json=data)
    print("Response from POST request:")
    print(response.text)

def main():
    server_url = "http://7.com"  # Change this to your server's URL
    while True:
        print("\nOptions:")
        print("1. Send GET request")
        print("2. Send POST request")
        print("3. Exit")
        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == '1':
            send_get_request(server_url)
        elif choice == '2':
            send_post_request(server_url + "/data")
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
