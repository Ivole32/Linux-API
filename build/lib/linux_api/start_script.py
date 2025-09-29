import os
import subprocess

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    start_script = os.path.abspath(os.path.join(base_path, "../start.sh"))
    subprocess.run(["bash", start_script], check=True)
