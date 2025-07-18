# Kafka + Streamlit Real-time Metrics Demo

A lean, production-ready stack featuring:
- **Kafka in KRaft mode** (no ZooKeeper needed)
- **Python producer** streaming random metrics
- **Streamlit dashboard** displaying live data

## 🚀 Quick Start

### 1. Start the services
```bash
docker compose up -d
```

This starts:
- Kafka broker + controller on ports 9092/9093
- Streamlit dashboard on port 8501

### 2. Run the producer
```bash
# Install dependencies
pip install -r requirements.txt

# Start sending metrics to Kafka
python metrics_producer.py
```

### 3. View the dashboard
Open http://localhost:8501 to see real-time metrics updating every second.

## 🔧 Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Producer       │───▶│  Kafka (KRaft)  │───▶│  Streamlit      │
│  (Python)       │    │  Port 9092      │    │  Dashboard      │
│                 │    │                 │    │  Port 8501      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Files

- `docker-compose.yml` - Kafka + Streamlit services
- `metrics_producer.py` - Generates random metrics
- `dashboard.py` - Real-time Streamlit dashboard
- `requirements.txt` - Python dependencies

## 🎯 Key Features

- **No ZooKeeper** - Uses Kafka's built-in KRaft consensus
- **Real-time streaming** - Sub-second latency from producer to dashboard
- **Simple setup** - Just two Docker services
- **Production-ready** - Based on Confluent's official Kafka image

## 🛑 Cleanup

```bash
docker compose down
```

## 💡 Demo Tips

- Show Kafka ports 9092/9093 in the architecture
- Highlight the absence of ZooKeeper
- Demonstrate real-time updates by watching the chart
- Mention this scales to production workloads
