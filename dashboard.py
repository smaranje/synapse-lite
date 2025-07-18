import json, queue, threading, time
import pandas as pd
import streamlit as st
from kafka import KafkaConsumer

# 1️⃣  background listener thread ➜ queue
q = queue.Queue(maxsize=5_000)

def consume():
    consumer = KafkaConsumer(
        "metrics",
        bootstrap_servers="kafka:9092",   # service name inside compose
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        group_id="dashboard",
    )
    for msg in consumer:
        q.put(msg.value)

threading.Thread(target=consume, daemon=True).start()

# 2️⃣  Streamlit UI
st.set_page_config(page_title="Kafka Metrics", layout="wide")
st.title("📈 Real-time metrics from Kafka")

placeholder = st.empty()
data = []

while True:
    while not q.empty():
        data.append(q.get())
    if data:
        df = pd.DataFrame(data)
        placeholder.line_chart(df.set_index("ts")["value"])
    time.sleep(0.5)
    st.experimental_rerun()