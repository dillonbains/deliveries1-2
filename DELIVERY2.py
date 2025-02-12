import pexpect
import difflib

# Device credentials
ip_address = '192.168.56.101'
username = 'prne'
password = 'cisco123!'
password_enable = 'cisco123!'

# Establish an SSH session
try:
    session = pexpect.spawn(f'ssh {username}@{ip_address}', encoding='utf-8', timeout=20)
    session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
    session.sendline(password)
    session.expect(['>', pexpect.TIMEOUT, pexpect.EOF])

    # Enter enable mode
    session.sendline('enable')
    session.expect(['Password:', pexpect.TIMEOUT, pexpect.EOF])
    session.sendline(password_enable)
    session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])

    # Function to fetch configuration
    def fetch_config(command):
        session.sendline(command)
        session.expect(['#', pexpect.TIMEOUT, pexpect.EOF])
        output = session.before.split('\n', 1)[1].strip()  # Remove command echo
        return output

    # Fetch running and startup configurations
    running_config = fetch_config('show running-config')
    startup_config = fetch_config('show startup-config')

    # Save configurations to local files
    with open('running_config.txt', 'w') as f:
        f.write(running_config)

    with open('startup_config.txt', 'w') as f:
        f.write(startup_config)

    # Compare running vs startup configuration
    diff = difflib.unified_diff(
        running_config.splitlines(),
        startup_config.splitlines(),
        lineterm='',
        fromfile='Running Configuration',
        tofile='Startup Configuration'
    )

    print("\nDifferences between Running and Startup Configurations:")
    for line in diff:
        print(line)

    # Compare running config with a local offline version
    try:
        with open('local_offline_config.txt', 'r') as f:
            offline_config = f.read()

        diff_local = difflib.unified_diff(
            running_config.splitlines(),
            offline_config.splitlines(),
            lineterm='',
            fromfile='Running Configuration',
            tofile='Offline Configuration'
        )

        print("\nDifferences between Running Configuration and Offline Configuration:")
        for line in diff_local:
            print(line)

    except FileNotFoundError:
        print("\nOffline configuration file 'local_offline_config.txt' not found.")

    # Close the session
    session.sendline('exit')
    session.close()

except Exception as e:
    print(f"An error occurred: {e}")
