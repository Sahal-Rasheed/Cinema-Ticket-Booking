# 🎬 Cinema Seat Booking (FastAPI + Redis)

A simple cinema seat booking system demonstrating **concurrency-safe seat reservation** using **FastAPI** and **Redis**.

## ▶️ Demo

```html
<video controls width="100%">
  <source
    src="https://github.com/user-attachments/assets/063c832b-4325-4bce-afc5-26bff664a6c3"
    type="video/webm"
  />
  Your browser does not support the video tag.
</video>
```

## ✨ Features

- Hold a seat with expiry (TTL)
- Confirm booking
- Release seat
- Prevent double booking (atomic Redis locks)
- Real-time seat updates (polling UI)
- Concurrency-safe (tested with high load)

## 🧱 Tech Stack

- FastAPI
- Redis (async)
- Docker
- HTML/CSS/JS (UI)
- Pytest (integration + concurrency tests)

## 🚀 Getting Started

### 1. Run the app

```bash
1. Clone the repo.
2. Install dependencies.
    - uv sync
3. Start the app.
	- sh run.sh
4. Open the UI.
	- Visit `http://127.0.0.1:8000`
```

- API: http://127.0.0.1:8000/docs
- Redis Commander: http://127.0.0.1:8081

### 2. Run tests

```python
1. Ensure the app is running.
2. Run tests.
    - pytest
```

---
