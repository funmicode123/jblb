# JBLB Backend 🧩
A production-ready **Django backend** powering the JBLB ecosystem — an on-chain, gamified sustainability marketplace built for transparency, social engagement, and digital collaboration.

This backend exposes REST APIs for user management, club creation, and battle logic while integrating blockchain interactions via **Anoma SDK (future)** and **Hedera SDK** for tokenized actions.

---

## 🧩 Overview

The **JBLB Backend** is designed using a modular Django architecture:

- **Users Module:** Authentication, profile management, and wallet linking  
- **Clubs Module:** Creation and management of clubs  
- **Battles Module:** On-chain sustainability battles between clubs  
- **Blockchain Module:** Integrations with Hedera and (future) Anoma SDK  
- **Services Layer:** Business logic and blockchain interaction layer  
- **Config Layer:** Environment and settings management for production  

It’s optimized for hackathon prototyping and enterprise scaling.

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-------------|
| Framework | Django 5 (Python 3.11) |
| Database | PostgreSQL |
| Container | Docker |
| CI/CD | GitHub Actions + GHCR |
| Blockchain | Hedera SDK + Anoma SDK (mock) |
| Auth | JWT |
| Deployment | Render / Railway / AWS ECS |
| Testing | Django TestCase + Pytest |

---

## 🧩 Architecture Summary

```plaintext
jblb-backend/
├── jblb_backend/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── users/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   └── views.py
├── clubs/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   └── views.py
├── battles/
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   └── views.py
├── blockchain/
│   ├── hedera_client.py
│   └── anoma_client.py
├── Dockerfile
├── requirements.txt
├── manage.py
└── .github/
    └── workflows/
        └── jblb-docker.yml


---

## ⚙️ Installation

### 1️⃣ Clone Repository
```bash
git clone https://github.com/<your-username>/jblb-backend.git
cd jblb-backend

### 2️⃣ Create Virtual Environment
```bash

python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

### 3️⃣ Install Dependencies
pip install -r requirements.txt

### 4️⃣ Configure Environment Variables

Create a .env file in the project root:
DEBUG=1
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://postgres:postgres@localhost:5432/jblb_db
ALLOWED_HOSTS=localhost,127.0.0.1

###5️⃣ Run Migrations
python manage.py migrate

### 6️⃣ Start Server
python manage.py runserver

Visit 👉 http://localhost:8000

🔁 CI/CD Pipeline (GitHub Actions)

The pipeline in .github/workflows/django-docker.yml:

Build & Test:

Runs linting and unit tests using Postgres service

Docker Build & Push:

Builds image and pushes to GitHub Container Registry (GHCR)

Cache Optimization:

Speeds up subsequent builds via buildx caching

Image is automatically tagged:

ghcr.io/<your-username>/jblb-backend:latest
ghcr.io/<your-username>/jblb-backend:<run_number>

🐳 Docker Usage
Build Docker Image
docker build -t jblb-backend .

Run Container
docker run -p 8000:8000 --env-file .env jblb-backend


Then visit http://localhost:8000

🚀 Deployment
🟩 Render / Railway

Create a new web service

Choose “Deploy from Dockerfile”

Set PORT=8000 in environment variables

Add other env vars from your .env file

Deploy — your API is live! 🎉

🟦 GitHub Container Registry

To use GHCR image directly:

docker pull ghcr.io/<your-username>/jblb-backend:latest
docker run -d -p 8000:8000 ghcr.io/<your-username>/jblb-backend:latest

🟨 AWS ECS / Fargate (Optional)

Create ECS service using GHCR image

Configure secrets via AWS Secrets Manager

Attach RDS Postgres instance

👩🏽‍💻 Contributors
Name	        Role	                GitHub
Funmilola Sanni	Backend Developer / DevOps	@funmicode123
Timmy           Backend Developer
Team JBLB	    Blockchain & Product Design	—


1️⃣ Fork the Repository

Click Fork at the top right of the repository.

2️⃣ Create Feature Branch
git checkout -b feature/<feature-name>

3️⃣ Commit Changes
git commit -m "Add new feature"

4️⃣ Push Branch
git push origin feature/<feature-name>

5️⃣ Open Pull Request

Submit a PR with detailed description and screenshots (if applicable).

🧑‍💻 Maintainers
Name	Role	GitHub
Funmilola Sanni	Backend Developer / DevOps	@funmilola

Team JBLB	Blockchain & Product Design	—
💚 License

This project is licensed under the MIT License — see LICENSE for details.

✨ Summary

You now have:

A CI/CD ready Django backend

Full Docker support

Automated GitHub Actions pipeline

Ready for GHCR + Cloud Deployment

Well-structured contributor workflow


---
