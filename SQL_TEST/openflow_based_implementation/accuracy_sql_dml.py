import subprocess
import time
import csv

def accuracy_sql_dml():
    def execute_mysql_command(command, timeout=2):
        """
        Executes a MySQL command and measures the response time.
        Returns a tuple (delay, status) where:
        - delay: Response time in milliseconds
        - status: 'success' if the command executed successfully, 'error' otherwise
        """
        start_time = time.time()
        try:
            process = subprocess.Popen([
                "timeout",  # Use the 'timeout' command (available on Unix-like systems)
                str(timeout),  # Convert timeout to string
                "mysql",
                f"--user={config['user']}",
                f"--password={config['password']}",
                f"--host={config['host']}",
                config.get('database', ''),  # Include database if provided
                "--execute",
                command
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            _, _ = process.communicate()  # Wait for process to complete
            end_time = time.time()
            delay_ms = (end_time - start_time) * 1000
            if delay_ms > 2000:
                return delay_ms, 'unreachable'
            return delay_ms, 'reachable'
        except subprocess.CalledProcessError:
            return timeout * 1000, 'unreachable'

    config = {
        'user': 'username',
        'password': 'password',
        'host': '192.168.118.136',
        'database': 'sqli',  # Assuming this is the active database
    }

    try:
        commands = [
            "INSERT INTO countries (name, population) VALUES ('Testland', 123456)",
            "UPDATE countries SET population = 654321 WHERE name = 'Testland'",
            "DELETE FROM countries WHERE name = 'Testland'",
            """
            INSERT INTO countries (name, population) VALUES ('Testland', 123456)
            ON DUPLICATE KEY UPDATE population = VALUES(population)
            """,
            "SELECT * FROM countries"
        ]

        # Execute commands and write to CSV
        with open('accuracy_sql.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            # Check if file is empty to add header only once
            if csvfile.tell() == 0:
                writer.writerow(['command', 'delay(ms)', 'status'])
            for cmd in commands:
                delay, status = execute_mysql_command(cmd)
                writer.writerow([cmd, delay, status])
                if cmd.strip().startswith("SELECT"):
                    print(f"Executed successfully: {cmd}, Delay: {delay:.3f} ms, Status: {status}")
                else:
                    print(f"Executed successfully: {cmd}, Delay: {delay:.3f} ms, Status: {status}")
    finally:
        print("MySQL commands execution completed.")
accuracy_sql_dml()