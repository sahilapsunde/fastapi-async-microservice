# FastAPI Async Microservice
High-performance async Python microservice with Redis caching,
Kafka event streaming, and PostgreSQL on Kubernetes/AWS EC2.
## Highlights- 40% faster API response via Redis cache-aside strategy- 500+ concurrent requests with Python async/await- Kafka event streaming for decoupled architecture- JWT authentication, rate limiting, structured logging- Docker + Kubernetes orchestration on AWS EC2
## Tech Stack
Python · FastAPI · async/await · Redis · Kafka · PostgreSQL · Docker · Kubernetes · AWS EC2 · JWT
## Quick Start
```bash
git clone https://github.com/sahilapsunde/fastapi-async-microservice.git
cd fastapi-async-microservice
pip install -r requirements.txt
uvicorn main:app --reload
```
