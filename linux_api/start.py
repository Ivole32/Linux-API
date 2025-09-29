import os
import subprocess
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Working directory: {script_dir}")

    script_path = os.path.join(script_dir, "start.sh")

    if not os.path.exists(script_path):
        print(f"Error: {script_path} not found.")
        sys.exit(1)

    os.chmod(script_path, 0o755)

    try:
        subprocess.run(["bash", script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing {script_path}: {e}")

if __name__ == "__main__":
    main()