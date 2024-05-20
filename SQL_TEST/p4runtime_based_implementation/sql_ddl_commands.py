import subprocess

config = {
    'user': 'username',
    'password': 'password',
    'host': '192.168.118.136',
}

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

# The MySQL command line executable path
mysql_executable_path = 'mysql'

for cmd in commands:
    print(f"Sending command: {cmd}")
    process = subprocess.Popen([
        mysql_executable_path,
        f"--user={config['user']}",
        f"--password={config['password']}",
        f"--host={config['host']}",
        "--execute", cmd,
    ])
    # We are not waiting for the process to complete
    # process.communicate()  # This line would wait for completion

print("All commands sent.")
