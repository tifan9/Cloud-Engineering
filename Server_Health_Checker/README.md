# Server Health Checker

This is a simple Python tool to check if your servers and websites are working correctly. It checks multiple URLs at the same time and tells you if they are up, down, slow, or timing out.

## What this tool does
1. **Reads your list of servers** from an environment variable or a `servers.json` file.
2. **Checks all servers at the same time** (in parallel) so it runs fast.
3. **Tries again (retries)** up to 2 times if a server fails before saying it is down.
4. **Checks three things** on each URL:
   - Does it return a good status code (200-299)?
   - Does it take less than 500ms to respond?
   - If the response is JSON, does it say `"status": "ok"`?
5. **Prints a clear summary** to your screen.
6. **Saves bad servers** to a file named `alerts.log`.

---

## Setup (How to install)

You do not need to install external libraries. This project only uses standard Python tools.

1. Download or copy the `health_checker.py` file to your computer.
2. Create a file named `servers.json` in the same folder with your URLs. Example format:

```json
{
  "servers": [
    "[https://httpbin.org/status/200](https://httpbin.org/status/200)",
    "[https://httpbin.org/status/500](https://httpbin.org/status/500)",
    "[https://httpbin.org/delay/2](https://httpbin.org/delay/2)",
    "[https://httpbin.org/json](https://httpbin.org/json)"
  ]
}