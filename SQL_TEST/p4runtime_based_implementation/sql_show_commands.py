import subprocess

config = {
    'user': 'username',
    'password': 'password',
    'host': '192.168.118.136',
    'database': 'sqli',
}

commands = [
    "SHOW DATABASES",
    "SHOW TABLES",
    # ... other commands
]

for cmd in commands:
    print(f"Sending command: {cmd}")
    subprocess.Popen([
        "mysql",
        f"--user={config['user']}",
        f"--password={config['password']}",
        f"--host={config['host']}",
        config['database'],
        "--execute",
        cmd
    ])
