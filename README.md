# synapse-lite

**Synapse-Lite** is a modular, enterprise-grade real-time Bitcoin fraud detection system. It leverages Apache Spark, Neo4j, Kafka, and AI (Google Gemini LLM) to provide streaming analytics, graph-based fraud detection, and a professional Streamlit dashboard for monitoring and investigation.

---

## Features

- **Real-time Bitcoin transaction monitoring**
- **AI-powered fraud detection** using Google Gemini LLM
- **Graph analytics** with Neo4j for advanced pattern detection
- **Professional Streamlit dashboard** for visualization and alerting
- **Synthetic data generation** for testing and demos
- **Modular microservices architecture** (Dockerized)

---

## Directory Structure

- `ai_service/` – Flask API for Gemini LLM-powered SAR generation and Neo4j integration
- `data/` – Synthetic Bitcoin transaction generator (Kafka producer)
- `neo4j_scripts/` – Initialization scripts for Neo4j
- `spark_app/` – Spark Streaming app for fraud detection and feature extraction
- `streamlit_app/` – Streamlit dashboard for analytics, alerts, and investigation

---

## Quick Start (Docker Compose)

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd synapse-lite
   ```

2. **Set up environment variables:**
   - Create a `.env` file in the root directory.
   - Add your Google Gemini API key:
     ```
     GEMINI_API_KEY=your_gemini_api_key_here
     ```

3. **Start all services:**
   ```bash
   docker-compose up --build
   ```

4. **Access the dashboard:**
   - Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Main Components

### 1. **Streamlit Dashboard**
- Location: `streamlit_app/`
- Run standalone (for development):
  ```bash
  cd streamlit_app
  pip install -r requirements.txt
  streamlit run streamlit_app.py
  ```

### 2. **Spark Streaming App**
- Location: `spark_app/`
- Consumes transactions from Kafka, processes features, writes to Neo4j, and calls the AI service.

### 3. **AI Service (LLM)**
- Location: `ai_service/`
- Flask API for generating Suspicious Activity Reports (SAR) using Gemini LLM.

### 4. **Synthetic Data Generator**
- Location: `data/`
- Produces synthetic Bitcoin transactions to Kafka for testing.

### 5. **Neo4j**
- Graph database for storing and querying transaction networks.

---

## Configuration

- All services are configured via environment variables (see `docker-compose.yml`).
- Key variables:
  - `GEMINI_API_KEY` (required for AI service)
  - `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`
  - `KAFKA_BROKER`, `KAFKA_TOPIC`

---

## Health Checks

- Each service exposes a health check endpoint or command for Docker Compose.
- Example: AI service health at `http://localhost:5000/health`

---

## Development & Testing

- Each subdirectory contains its own `requirements.txt` for local development.
- To run individual services outside Docker, install dependencies and run the main script.

---

## Troubleshooting

- Ensure all Docker images build successfully.
- Check `.env` for required environment variables.
- For detailed bug fixes and improvements, see:
  - `bug_fixes_summary.md`
  - `docker_fixes_summary.md`
  - `UI_Improvements_Summary.md`

---

## License

MIT License (or specify your license here)

---

## Acknowledgements

- [Streamlit](https://streamlit.io/)
- [Apache Spark](https://spark.apache.org/)
- [Neo4j](https://neo4j.com/)
- [Google Gemini LLM](https://ai.google.dev/)
- [Kafka](https://kafka.apache.org/)
