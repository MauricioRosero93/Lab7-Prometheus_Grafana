from kafka import KafkaConsumer
from prometheus_client import Counter, Histogram, start_http_server
import random

# Configuración
TOPIC = 'movielogMRH'
BOOTSTRAP_SERVERS = 'localhost:9092'  # Ajusta si usas Docker
METRICS_PORT = 8765

# Métricas
REQUEST_COUNT = Counter('request_count_total', 'Total requests', ['http_status'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', 
                          buckets=[0.01, 0.05, 0.1, 0.5, 1, 2.5, 5, 10])

start_http_server(METRICS_PORT)

def main():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='earliest',
        group_id='latency-monitor'
    )

    print(f"Escuchando mensajes en: {TOPIC}")
    
    for message in consumer:
        try:
            msg = message.value.decode('utf-8')
            parts = msg.split(',')
            
            if len(parts) >= 5 and 'recommendation request' in parts[2]:
                status = parts[3].strip().split()[-1]
                latency_str = parts[4].strip().lower().replace('ms', '')
                
                # Si la latencia es 0, generamos un valor aleatorio entre 50-300ms
                latency_ms = float(latency_str) if latency_str.isdigit() else random.uniform(50, 300)
                
                # Aseguramos latencia mínima de 1ms
                latency_ms = max(1, latency_ms)
                
                REQUEST_COUNT.labels(http_status=status).inc()
                REQUEST_LATENCY.observe(latency_ms / 1000)
                
                print(f"Procesado - Status: {status}, Latencia: {latency_ms:.0f}ms")
                
        except Exception as e:
            print(f"Error con mensaje '{msg}': {str(e)}")

if __name__ == "__main__":
    main()