import subprocess
import sys

if __name__ == "__main__":
    # Command to run Granian
    command = [
        sys.executable,  # Use the current Python interpreter
        "-m",
        "granian",
        "--interface", "asgi",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
        "src.entrypoints.main_app:app",
    ]

    # Execute the command
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Failed to start Granian: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("Granian server stopped.")
        sys.exit(0)
