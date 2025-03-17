import subprocess
import sys

def run_script(script_name):
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script_name}: {e}")
        sys.exit(e.returncode)

def main():
    print("Starting job URL extraction (crawl.py)...")
    run_script("crawl.py")
    print("Job URL extraction completed.\nStarting contact extraction (crawl-llm.py)...")
    run_script("crawl-llm.py")
    print("Contact extraction completed.")

if __name__ == "__main__":
    main()
