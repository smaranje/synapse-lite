import json, random, time
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

while True:
    msg = {"ts": time.time(), "value": random.random() * 100}
    producer.send("metrics", value=msg)
    producer.flush()
    print("sent", msg)
    time.sleep(1)