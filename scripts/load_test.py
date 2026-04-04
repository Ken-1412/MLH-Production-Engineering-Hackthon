#!/usr/bin/env python3
import concurrent.futures
import time
import urllib.request
import json
import statistics

BASE_URL = "http://localhost:5000"
NUM_REQUESTS = 500
CONCURRENCY = 20

def fetch_health():
    start = time.time()
    try:
        req = urllib.request.Request(f"{BASE_URL}/health")
        with urllib.request.urlopen(req) as response:
            status = response.status
            response.read()
            end = time.time()
            return status, (end - start) * 1000
    except Exception as e:
        return 500, (time.time() - start) * 1000

print(f"Starting Load Test: {NUM_REQUESTS} requests, Concurrency: {CONCURRENCY}")
start_time = time.time()

with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENCY) as executor:
    results = list(executor.map(lambda _: fetch_health(), range(NUM_REQUESTS)))

total_time = time.time() - start_time
latencies = [r[1] for r in results if r[0] == 200]
errors = [r for r in results if r[0] != 200]

print("\n--- Results ---")
print(f"Total Requests: {NUM_REQUESTS}")
print(f"Total Time: {total_time:.2f}s")
print(f"Throughput: {NUM_REQUESTS / total_time:.2f} req/s")
if latencies:
    print(f"p95 Latency: {statistics.quantiles(latencies, n=20)[-1]:.2f} ms")
    print(f"Avg Latency: {statistics.mean(latencies):.2f} ms")
print(f"Error Rate: {(len(errors) / NUM_REQUESTS) * 100:.2f}%")
