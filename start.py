import os
import subprocess
import curses

def list_servers(base_dir):
    """List all server directories"""
    return [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and d.endswith("-container")
    ]

def display_menu(stdscr, servers, colors):
    """Display the server menu with navigation."""
    curses.curs_set(0) 
    current_row = 0

    while True:
        stdscr.clear()

        for idx, server in enumerate(servers):
            if idx == current_row:
                stdscr.addstr(idx, 0, f"> {server}", curses.color_pair(colors[idx]))
            else:
                stdscr.addstr(idx, 0, f"  {server}")

        stdscr.addstr(len(servers), 0, "Press Enter to select, 'q' to quit")

        key = stdscr.getch()

        if key == curses.KEY_UP and current_row > 0:
            current_row -= 1
        elif key == curses.KEY_DOWN and current_row < len(servers) - 1:
            current_row += 1
        elif key == ord("\n"): 
            return current_row
        elif key == ord("q"): 
            return -1

def start_container(server_path, proxy_path):
    print(f"Starting proxy in {proxy_path}...")
    subprocess.run(["docker-compose", "up", "-d"], cwd=proxy_path)

    """Start the selected container."""
    subprocess.run(["docker-compose", "up", "-d"], cwd=server_path)

def stop_container(server_path, proxy_path):
    print(f"Stopping proxy in {proxy_path}...")
    subprocess.run(["docker-compose", "down"], cwd=proxy_path)

    """Stop the selected container."""
    subprocess.run(["docker-compose", "down"], cwd=server_path)

def view_logs(server_path, stdscr):
    """View logs of the selected container."""
    stdscr.clear()
    stdscr.addstr(0, 0, f"Fetching logs for {os.path.basename(server_path)}...")
    stdscr.refresh()
    subprocess.run(["docker-compose", "logs", "--tail=20"], cwd=server_path)

def view_status(server_path, stdscr):
    """Check the status of the selected container."""
    stdscr.clear()
    stdscr.addstr(0, 0, f"Status for {os.path.basename(server_path)}:\n")
    stdscr.refresh()

    result = subprocess.run(["docker-compose", "ps"], cwd=server_path, text=True, capture_output=True)

    if result.stdout:
        lines = result.stdout.strip().split("\n")
        for idx, line in enumerate(lines, start=1):
            stdscr.addstr(idx, 0, line)
    else:
        stdscr.addstr(1, 0, "No containers found or unable to fetch status.")

    stdscr.addstr(len(lines) + 1, 0, "\nPress any key to return to the menu.")
    stdscr.refresh()
    stdscr.getch()


def main(stdscr):
    curses.start_color()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(base_dir):
        stdscr.addstr(0, 0, f"Error: Directory '{base_dir}' does not exist.")
        stdscr.refresh()
        stdscr.getch()
        return

    servers = list_servers(base_dir)

    colors = {}
    for idx in range(len(servers)):
        curses.init_pair(idx + 1, idx + 1, curses.COLOR_BLACK)
        colors[idx] = idx + 1

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "Navigate with arrow keys. Press Enter to select a server.")
        stdscr.refresh()

        choice = display_menu(stdscr, servers, colors)

        if choice == -1:  # User pressed 'q' to quit
            break

        server_name = servers[choice]
        server_path = os.path.join(base_dir, server_name)
        proxy_path = os.path.join(base_dir, "proxy")

        while True:
            stdscr.clear()
            stdscr.addstr(0, 0, f"Selected server: {server_name}")
            stdscr.addstr(1, 0, "Press 's' to start, 't' to stop, 'l' to view logs,")
            stdscr.addstr(2, 0, "'v' to view status, or 'q' to go back.")
            stdscr.refresh()

            key = stdscr.getch()
            if key == ord("s"):
                start_container(server_path, proxy_path)
                stdscr.addstr(4, 0, f"Started {server_name}. Press any key to continue.")
                stdscr.refresh()
                stdscr.getch()
            elif key == ord("t"):
                stop_container(server_path, proxy_path)
                stdscr.addstr(4, 0, f"Stopped {server_name}. Press any key to continue.")
                stdscr.refresh()
                stdscr.getch()
            elif key == ord("l"):
                view_logs(server_path, stdscr)
                stdscr.addstr(4, 0, "Press any key to return to the menu.")
                stdscr.refresh()
                stdscr.getch()
            elif key == ord("v"):
                view_status(server_path, stdscr)
                stdscr.addstr(4, 0, "Press any key to return to the menu.")
                stdscr.refresh()
                stdscr.getch()
            elif key == ord("q"):
                break

if __name__ == "__main__":
    curses.wrapper(main)
