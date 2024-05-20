import subprocess
import time
import csv
import signal
import os

def accuracy_sql_ddl():
    def execute_mysql_command(command, timeout=2):
        """
        Executes a MySQL command and measures the response time.
        Returns a tuple (delay, status) where:
        - delay: Response time in milliseconds
        - status: 'success' if the command executed successfully, 'error' otherwise
        """
        start_time = time.time()
        process = None
        try:
            process = subprocess.Popen([
                "mysql",
                f"--user={config['user']}",
                f"--password={config['password']}",
                f"--host={config['host']}",
                config.get('database', ''),  # Include database if provided
                "--execute",
                command
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            try:
                _, _ = process.communicate(timeout=timeout)  # Set the timeout directly here
                end_time = time.time()
                delay_ms = (end_time - start_time) * 1000
                if delay_ms > 2000:
                    return delay_ms, 'unreachable'
                return delay_ms, 'reachable'
            except subprocess.TimeoutExpired:
                process.kill()  # Kill the process if timeout
                process.wait()  # Wait for the process to terminate
                return timeout * 1000, 'unreachable'
        except Exception as e:
            if process:
                process.kill()  # Ensure process is killed in case of any error
                process.wait()
            print(f"Error executing command: {command}, Error: {str(e)}")
            return timeout * 1000, 'unreachable'

    config = {
        'user': 'username',
        'password': 'password',
        'host': '192.168.118.136',
        'database': 'sqli',
    }

    try:
        commands = [
        "CREATE DATABASE IF NOT EXISTS temp_db",
        "USE temp_db",
        """
        CREATE TABLE IF NOT EXISTS temp_table (
            id INT AUTO_INCREMENT PRIMARY KEY,
            data VARCHAR(100)
        )
        """,
        "CREATE INDEX idx_data ON temp_table(data)",
        """
        CREATE VIEW view_data AS
        SELECT data FROM temp_table
        """,
        """
        CREATE PROCEDURE SelectAll()
        BEGIN
            SELECT * FROM temp_table;
        END
        """,
        """
        CREATE FUNCTION GetDataCount() RETURNS INT
        BEGIN
            DECLARE cnt INT;
            SELECT COUNT(*) INTO cnt FROM temp_table;
            RETURN cnt;
        END
        """,
        """
        CREATE TRIGGER BeforeInsert
        BEFORE INSERT ON temp_table FOR EACH ROW
        SET NEW.data = CONCAT('Prefix_', NEW.data)
        """,
        "ALTER TABLE temp_table ADD COLUMN new_column VARCHAR(100)",
        "ALTER TABLE temp_table DROP COLUMN new_column",
        "DROP INDEX idx_data ON temp_table",
        "DROP TRIGGER BeforeInsert",
        "DROP FUNCTION GetDataCount",
        "DROP PROCEDURE SelectAll",
        "DROP VIEW view_data",
        "DROP TABLE temp_table",
        "DROP DATABASE temp_db"
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
    finally:
        print("MySQL commands execution completed.")

accuracy_sql_ddl()
