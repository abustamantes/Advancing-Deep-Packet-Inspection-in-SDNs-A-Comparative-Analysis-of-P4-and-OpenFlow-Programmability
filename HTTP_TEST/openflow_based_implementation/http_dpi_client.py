import requests
import time
import csv
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

def send_get_request(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=2)  # 2-second timeout for the GET request
        elapsed_time = (time.time() - start_time) * 1000  # Convert time to milliseconds
        if response.status_code == 200:
            return "completed", elapsed_time
        else:
            return "unreachable", elapsed_time
    except requests.exceptions.RequestException:
        return "unreachable", (time.time() - start_time) * 1000  # Convert time to milliseconds

def calculate_metrics(real, predicted, delays):
    accuracy = accuracy_score(real, predicted)
    precision = precision_score(real, predicted, pos_label='positive')
    recall = recall_score(real, predicted, pos_label='positive')
    f1 = f1_score(real, predicted, pos_label='positive')
    tn, fp, fn, tp = confusion_matrix(real, predicted, labels=["positive", "negative"]).ravel()
    tpr = tp / (tp + fn) if (tp + fn) != 0 else 0  # True Positive Rate
    fpr = fp / (fp + tn) if (fp + tn) != 0 else 0  # False Positive Rate

    results = [
        f"Accuracy: {accuracy:.2f}",
        f"Precision: {precision:.2f}",
        f"Recall: {recall:.2f}",
        f"F1 Score: {f1:.2f}",
        f"True Positive Rate (TPR): {tpr:.2f}",
        f"False Positive Rate (FPR): {fpr:.2f}"
    ]
    if delays:
        min_delay = min(delays)
        max_delay = max(delays)
        avg_delay = sum(delays) / len(delays)
        results += [
            f"Minimum Delay: {min_delay:.2f} ms",
            f"Maximum Delay: {max_delay:.2f} ms",
            f"Average Delay: {avg_delay:.2f} ms"
        ]
    else:
        results.append("No completed entries to calculate delay statistics.")

    with open("dp_metric_results.txt", "w") as file:
        file.write("\n".join(results))
    print("\nAccuracy and Delay Results:\n")
    for result in results:
        print(result)

def main():
    input_output_filename = "openflow_test.csv"
    rows = []
    real_results = []
    tested_results = []
    delays = []

    with open(input_output_filename, mode='r', newline='') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            domain = row['domain'].strip()
            server_url = f"http://{domain}"
            status, delay = send_get_request(server_url)
            tested_result = "positive" if status == "completed" else "negative"
            row.update({
                'status': status,
                'tested_result': tested_result,
                'delay(ms)': f"{delay:.2f}"
            })
            rows.append(row)
            real_results.append(row['real_result'])
            tested_results.append(tested_result)
            if status == "completed":
                delays.append(delay)

    with open(input_output_filename, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=['domain', 'real_result', 'status', 'tested_result', 'delay(ms)'])
        writer.writeheader()
        writer.writerows(rows)

    calculate_metrics(real_results, tested_results, delays)

if __name__ == "__main__":
    main()
