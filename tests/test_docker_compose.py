#!/usr/bin/env python3
"""
Automated Docker Compose test for REMIXER-AI.
- Builds and runs the containers
- Checks for errors in logs
- Cleans up failed containers/images
- Prints clear instructions if errors are found
"""
import subprocess
import sys
import time

# Names must match those in your compose files
CONTAINERS = ["remixer-python-app", "remixer-static-frontend"]
IMAGES = ["remixer-python-app", "remixer-static-frontend"]
COMPOSE_FILE = "docker-compose.prod.yaml"


def run(cmd, check=True, capture_output=False, text=True):
    return subprocess.run(cmd, shell=True, check=check, capture_output=capture_output, text=text)


def main():
    print("\n[INFO] Building and starting containers...")
    try:
        run(f"docker compose -f {COMPOSE_FILE} build --no-cache")
        run(f"docker compose -f {COMPOSE_FILE} up -d --remove-orphans")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Docker Compose failed: {e}")
        cleanup()
        sys.exit(1)

    print("[INFO] Waiting for containers to start...")
    time.sleep(10)  # Wait for services to initialize

    error_found = False
    for container in CONTAINERS:
        print(f"[INFO] Checking logs for {container}...")
        try:
            logs = run(f"docker logs {container}", capture_output=True).stdout
            if any(err in logs.lower() for err in ["error", "traceback", "exception", "fail"]):
                print(f"[ERROR] Problem detected in {container} logs:")
                print("-"*40)
                print(logs)
                print("-"*40)
                error_found = True
        except subprocess.CalledProcessError:
            print(f"[ERROR] Could not get logs for {container} (container may not have started)")
            error_found = True

    if error_found:
        print("[FAIL] One or more containers had errors. Cleaning up...")
        cleanup()
        print("\n[INSTRUCTIONS] Fix the errors above, then re-run this script until all containers start cleanly.")
        sys.exit(1)
    else:
        print("[SUCCESS] All containers started without critical errors!")
        cleanup(stop_only=True)
        sys.exit(0)


def cleanup(stop_only=False):
    for container in CONTAINERS:
        try:
            print(f"[INFO] Stopping and removing container: {container}")
            run(f"docker stop {container}", check=False)
            run(f"docker rm {container}", check=False)
        except Exception:
            pass
    if not stop_only:
        for image in IMAGES:
            try:
                print(f"[INFO] Removing image: {image}")
                run(f"docker rmi -f {image}", check=False)
            except Exception:
                pass

if __name__ == "__main__":
    main()
