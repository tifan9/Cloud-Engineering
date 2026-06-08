import os
import json
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_FILE = "servers.json"
TIMEOUT = 5
SLOW_THRESHOLD = 500
RETRIES = 2


def load_servers():
    # Look for env variable first. If not found, look for the file.
    env_servers = os.environ.get("SERVERS")
    if env_servers:
        servers = [s.strip() for s in env_servers.split(",") if s.strip()]
        print(f"Loaded {len(servers)} servers")
        return servers

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            servers = json.load(f).get("servers", [])
            print(f"Loaded {len(servers)} servers")
            return servers

    raise Exception("No configuration found. Set SERVERS env var or create servers.json")


def check_server(url):
    # This function checks one server. It tries again if the check fails.
    status, status_code, err_type, elapsed, body = "DOWN", None, None, 0, ""

    for attempt in range(RETRIES):
        start = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HealthChecker/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                status_code = resp.getcode()
                body = resp.read().decode('utf-8')
                elapsed = round((time.time() - start) * 1000)
                err_type = None
                break
        except urllib.error.HTTPError as e:
            status_code = e.code
            elapsed = round((time.time() - start) * 1000)
            err_type = "HTTP_ERROR"
        except (urllib.error.URLError, TimeoutError):
            status_code = None
            elapsed = round((time.time() - start) * 1000)
            err_type = "TIMEOUT"
        except Exception:
            status_code = None
            elapsed = round((time.time() - start) * 1000)
            err_type = "DOWN"

        if attempt < RETRIES - 1:
            time.sleep(1)

    # Check if the text from the server has standard "status": "ok" JSON.
    json_ok = False
    if body:
        try:
            json_ok = json.loads(body).get("status") == "ok"
        except json.JSONDecodeError:
            pass

    # Use the status code and JSON check to see if the server is good.
    if err_type is None and ((status_code and 200 <= status_code < 300) or json_ok):
        status = "OK"
    elif err_type == "TIMEOUT":
        status = "TIMEOUT"

    return {
        "url": url,
        "status": status,
        "status_code": status_code,
        "ms": elapsed,
        "slow": elapsed > SLOW_THRESHOLD and status == "OK"
    }


def format_result(result):
    # Make a clean text line to print. Show the full path so names are not identical.
    display_name = result["url"].replace("https://", "").replace("http://", "")

    if result["status"] == "OK":
        suffix = "  [slow]" if result["slow"] else ""
        return f"{display_name:25} — OK ({result['status_code']})    — {result['ms']}ms{suffix}"
    elif result["status"] == "TIMEOUT":
        return f"{display_name:25} — TIMEOUT"
    else:
        return f"{display_name:25} — DOWN ({result['status_code'] or '503'})"


def check_all_servers():
    # Check all servers at the same time using multiple threads.
    servers = load_servers()
    results, failed_services = [], []

    print("\nChecking servers...\n")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(check_server, url): url for url in servers}

        for future in as_completed(futures):
            res = future.result()
            results.append(res)

            # Print the result right now.
            print(format_result(res))

            # If the server is bad, add its name to the bad list.
            if res["status"] != "OK":
                display_name = res["url"].replace("https://", "").replace("http://", "")
                failed_services.append(display_name)

    return results, failed_services


def send_alerts(failed_services):
    # Write the bad server names into a file named alerts.log.
    if not failed_services:
        return
    with open("alerts.log", "a") as f:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] FAILED: {', '.join(failed_services)}\n")


def main():
    try:
        results, failed = check_all_servers()
    except Exception as e:
        print(f"Error: {e}")
        return

    # Print the final summary text at the bottom.
    print()
    if failed:
        print(f"Failed services: {', '.join(failed)}")
        send_alerts(failed)
    else:
        print("All services are healthy")


if __name__ == "__main__":
    main()