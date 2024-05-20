import csv
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from accuracy_sql_dcl import accuracy_sql_dcl
from accuracy_sql_ddl import accuracy_sql_ddl
from accuracy_sql_dml import accuracy_sql_dml
from accuracy_sql_show import accuracy_sql_show
from accuracy_sql_tc import accuracy_sql_tc
from accuracy_sql_utility import accuracy_sql_utility

#accuracy_sql_dcl()
#accuracy_sql_ddl()
#accuracy_sql_dml()
#accuracy_sql_show()
#accuracy_sql_tc()
#accuracy_sql_utility()

# Read the actual statuses from the CSV file
actual_statuses = []
with open('accuracy_sql.csv', mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        # Add the actual status to the list
        actual_statuses.append(row['status'].strip().lower())

# Now we know the length of our actual data, we can create a predicted list of the same length
# Assuming all commands should be 'unreachable' as per your requirement
predicted_statuses = ['unreachable'] * len(actual_statuses)

# Convert the actual and predicted statuses to binary classes
# Consider 'unreachable' as the positive class (1) and 'reachable' as the negative class (0)
actual_binary = [0 if status == 'unreachable' else 1 for status in actual_statuses]
predicted_binary = [0] * len(actual_statuses)  # All predicted are 'unreachable' which is considered as 1 here

# Calculate metrics
accuracy = accuracy_score(actual_binary, predicted_binary)
precision = precision_score(actual_binary, predicted_binary, zero_division=0)
recall = recall_score(actual_binary, predicted_binary, zero_division=0)
f1 = f1_score(actual_binary, predicted_binary, zero_division=0)

# Since we predicted everything as 'unreachable', TPR and FPR would be:
tpr = recall  # True Positive Rate is the same as Recall in this binary classification
fpr = 1 - precision  # False Positive Rate would be the inverse of Precision since everything was predicted as 'unreachable'

# Print the metrics
print("\nAccuracy results\n")
print(f'Accuracy: {accuracy}')
print(f'Precision: {precision}')
print(f'Recall: {recall}')
print(f'F1 Score: {f1}')
print(f'True Positive Rate (TPR): {tpr}')
print(f'False Positive Rate (FPR): {fpr}')
print("\n")

# Append metrics to the CSV file
with open('accuracy_sql.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Accuracy', accuracy])
    writer.writerow(['Precision', precision])
    writer.writerow(['Recall', recall])
    writer.writerow(['F1 Score', f1])
    writer.writerow(['True Positive Rate (TPR)', tpr])
    writer.writerow(['False Positive Rate (FPR)', fpr])
