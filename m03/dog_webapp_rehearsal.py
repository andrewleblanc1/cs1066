### m03/dog_webapp_rehearsal.py
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

import doggy

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8000"))

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Random Dog Fetcher</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #e8f2ff;
      color: #102a43;
    }
    body {
      margin: 0;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
    }
    .page {
      width: min(100%, 780px);
      background: white;
      border-radius: 28px;
      box-shadow: 0 28px 80px rgba(16, 42, 67, 0.14);
      overflow: hidden;
    }
    .hero {
      padding: 36px 40px 28px;
      text-align: center;
      background: linear-gradient(135deg, #4f6ef7 0%, #75c2ff 100%);
      color: white;
    }
    .hero h1 {
      margin: 0;
      font-size: clamp(2rem, 3vw, 3rem);
      line-height: 1.05;
    }
    .hero p {
      margin: 16px auto 0;
      max-width: 640px;
      color: rgba(255, 255, 255, 0.9);
      font-size: 1rem;
      line-height: 1.7;
    }
    .content {
      padding: 30px 32px 40px;
    }
    .controls {
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      align-items: center;
      justify-content: center;
      margin-bottom: 24px;
    }
    button {
      border: none;
      border-radius: 999px;
      background: linear-gradient(135deg, #3469f7 0%, #46b4ff 100%);
      color: white;
      font-size: 1rem;
      font-weight: 700;
      padding: 16px 28px;
      cursor: pointer;
      transition: transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease;
      box-shadow: 0 16px 28px rgba(52, 105, 247, 0.24);
    }
    button:hover:not(:disabled) {
      transform: translateY(-1px);
      box-shadow: 0 22px 36px rgba(52, 105, 247, 0.28);
    }
    button:disabled {
      opacity: 0.65;
      cursor: default;
    }
    #status {
      font-size: 0.98rem;
      color: #334e68;
      min-width: 220px;
      text-align: center;
    }
    .image-card {
      border-radius: 24px;
      overflow: hidden;
      background: #f4f8ff;
      border: 1px solid rgba(51, 78, 104, 0.08);
      box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.8);
    }
    .image-card img {
      width: 100%;
      display: block;
      aspect-ratio: 16 / 10;
      object-fit: cover;
      background: #d8e6ff;
    }
    .hint {
      margin-top: 16px;
      font-size: 0.95rem;
      color: #627d98;
      line-height: 1.6;
      text-align: center;
    }
  </style>
</head>
<body>
  <div class="page">
    <section class="hero">
      <h1>Fetch a Random Dog</h1>
      <p>Press the button whenever you want a fresh, adorable dog image delivered from thedogapi.com.</p>
    </section>

    <section class="content">
      <div class="controls">
        <button id="fetchButton" type="button">fetch</button>
        <div id="status">Ready for a new pup.</div>
      </div>

      <div class="image-card">
        <img id="dogImage" alt="Random dog image" src="/random" />
      </div>

      <div class="hint">Use the button to refresh the picture. The image updates with each successful call.</div>
    </section>
  </div>

  <script>
    const fetchButton = document.getElementById("fetchButton");
    const status = document.getElementById("status");
    const dogImage = document.getElementById("dogImage");

    async function fetchDog() {
      fetchButton.disabled = true;
      status.textContent = "Fetching a new dog...";

      try {
        const response = await fetch("/fetch", { method: "POST" });
        const result = await response.json();

        if (!response.ok) {
          throw new Error(result.error || "Unable to retrieve a dog image.");
        }

        dogImage.src = `/random?ts=${Date.now()}`;
        status.textContent = "A new dog is here!";
      } catch (error) {
        status.textContent = `Error: ${error.message}`;
      } finally {
        fetchButton.disabled = false;
      }
    }

    fetchButton.addEventListener("click", fetchDog);
    dogImage.addEventListener("error", () => {
      dogImage.alt = "No dog image available yet.";
    });
  </script>
</body>
</html>
"""


class DogWebAppHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self._send_html()
        elif self.path.startswith("/random"):
            self._send_random_image()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == "/fetch":
            self._handle_fetch()
        else:
            self.send_error(404, "Not Found")

    def _send_html(self):
        body = HTML.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_random_image(self):
        image_path = Path(doggy.OUTPUT_FILE)
        if not image_path.exists():
            self.send_error(404, "No dog image has been fetched yet.")
            return

        self.send_response(200)
        self.send_header("Content-Type", "image/jpeg")
        self.send_header("Content-Length", str(image_path.stat().st_size))
        self.end_headers()
        with image_path.open("rb") as f:
            self.wfile.write(f.read())

    def _handle_fetch(self):
        api_key = doggy.get_api_key()
        if api_key == "YOUR_API_KEY_HERE":
            return self._json_error(
                "Set the CS1066_THEDOGAPIKEY environment variable before using fetch.",
                status=400,
            )

        try:
            doggy.download_random_dog_image(api_key)
        except Exception as exc:
            return self._json_error(str(exc), status=500)

        self._json_response({"status": "ok"})

    def _json_response(self, data, status=200):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _json_error(self, message, status=500):
        self._json_response({"error": message}, status=status)

    def log_message(self, format, *args):
        return


def run_server():
    address = (HOST, PORT)
    with HTTPServer(address, DogWebAppHandler) as server:
        print(f"Dog web app is running at http://{HOST}:{PORT}/")
        print("Press Ctrl+C to stop.")
        server.serve_forever()


if __name__ == "__main__":
    run_server()
