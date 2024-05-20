import subprocess
import time
import csv

def accuracy_sql_show():
    def execute_mysql_command(command, timeout=2):
        """
        Executes a MySQL command and measures the response time.
        Returns a tuple (delay, status) where:
        - delay: Response time in milliseconds
        - status: 'reachable' if response received, 'unreachable' otherwise
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
                config['database'],
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

    # Configuration
    config = {
        'user': 'username',
        'password': 'password',
        'host': '192.168.118.136',
        'database': 'sqli',
    }

    # List of commands
    commands = [
            "SHOW DATABASES",
            "SHOW TABLES",
            "SHOW COLUMNS FROM countries",
            "SHOW INDEX FROM countries",
            "SHOW TABLE STATUS LIKE 'countries'",
            "SHOW PROCESSLIST",
            "SHOW GRANTS FOR 'username'@'localhost'",
            "SHOW CREATE TABLE countries",
            "SHOW VARIABLES",
            "SHOW STATUS",
            "SHOW ERRORS",
            "SHOW WARNINGS"
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
            print(f"Command: {cmd}, Delay: {delay:.3f} ms, Status: {status}")
accuracy_sql_show()