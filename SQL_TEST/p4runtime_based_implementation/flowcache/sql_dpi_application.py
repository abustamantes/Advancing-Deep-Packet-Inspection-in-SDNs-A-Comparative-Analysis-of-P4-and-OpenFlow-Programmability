from scapy.all import *

def process_sql(packet, blacklist_commands):
    try:
        if packet.haslayer(Raw):
            payload_data = packet[Raw].load
            print("\nPayload Data:")
            sql_payload = payload_data.decode('utf-8')
            sql_payload = ''.join(char for char in sql_payload if char.isprintable())
            # Split the payload into words and get the first word, converting it to lowercase
            first_word = sql_payload.strip().split()[0].lower() if sql_payload.strip().split() else ""
            print(f"SQL payload first word: {first_word}")
            print("SQL payload:", sql_payload)
            print(f"Lets see the type of first word: {type(first_word)}")
            print(f"Lets see the length of first word: {len(first_word)}")

            # Check if the first word is "show"
            if first_word in blacklist_commands:
                print(f"Dropping packet due to 'show' command detected.")
                return True  # Indicate that the packet should be dropped

    except Exception as e:
        print("Error accessing TCP payload:", e)

    return False  # Indicate that the packet should not be dropped
