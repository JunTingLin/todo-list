"""Performance test script to validate latency requirements."""

import time
import statistics
from typing import List
import requests

BASE_URL = "http://localhost:8000"


def measure_latency(func, iterations: int = 100) -> List[float]:
    """Measure latency for a given function over multiple iterations."""
    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        latencies.append((end - start) * 1000)  # Convert to milliseconds
    return latencies


def test_create_todo():
    """Test POST /todos latency."""
    requests.post(f"{BASE_URL}/todos", json={"title": "Performance test"})


def test_get_todos():
    """Test GET /todos latency."""
    requests.get(f"{BASE_URL}/todos")


def test_get_todo_by_id():
    """Test GET /todos/{id} latency."""
    # Create a todo first
    resp = requests.post(f"{BASE_URL}/todos", json={"title": "Test"})
    todo_id = resp.json()["id"]

    def get_todo():
        requests.get(f"{BASE_URL}/todos/{todo_id}")

    return get_todo


def test_update_todo():
    """Test PUT /todos/{id} latency."""
    # Create a todo first
    resp = requests.post(f"{BASE_URL}/todos", json={"title": "Test"})
    todo_id = resp.json()["id"]

    def update_todo():
        requests.put(f"{BASE_URL}/todos/{todo_id}", json={"completed": True})

    return update_todo


def test_health_check():
    """Test GET /health latency."""
    requests.get(f"{BASE_URL}/health")


def calculate_percentiles(latencies: List[float]):
    """Calculate percentiles from latency measurements."""
    sorted_latencies = sorted(latencies)
    return {
        "min": min(latencies),
        "max": max(latencies),
        "mean": statistics.mean(latencies),
        "median": statistics.median(latencies),
        "p95": sorted_latencies[int(len(sorted_latencies) * 0.95)],
        "p99": sorted_latencies[int(len(sorted_latencies) * 0.99)],
    }


def main():
    """Run performance tests."""
    print("Starting performance tests...")
    print("=" * 60)

    # Test CRUD operations (SC-001: p95 < 100ms)
    print("\n1. Testing POST /todos (Create)")
    create_latencies = measure_latency(test_create_todo, 100)
    create_stats = calculate_percentiles(create_latencies)
    print(f"   p95: {create_stats['p95']:.2f}ms (target: <100ms)")
    print(f"   p99: {create_stats['p99']:.2f}ms")
    print(f"   mean: {create_stats['mean']:.2f}ms")

    print("\n2. Testing GET /todos (List)")
    list_latencies = measure_latency(test_get_todos, 100)
    list_stats = calculate_percentiles(list_latencies)
    print(f"   p95: {list_stats['p95']:.2f}ms (target: <100ms)")
    print(f"   p99: {list_stats['p99']:.2f}ms")
    print(f"   mean: {list_stats['mean']:.2f}ms")

    print("\n3. Testing GET /todos/{id} (Get by ID)")
    get_func = test_get_todo_by_id()
    get_latencies = measure_latency(get_func, 100)
    get_stats = calculate_percentiles(get_latencies)
    print(f"   p95: {get_stats['p95']:.2f}ms (target: <100ms)")
    print(f"   p99: {get_stats['p99']:.2f}ms")
    print(f"   mean: {get_stats['mean']:.2f}ms")

    print("\n4. Testing PUT /todos/{id} (Update)")
    update_func = test_update_todo()
    update_latencies = measure_latency(update_func, 100)
    update_stats = calculate_percentiles(update_latencies)
    print(f"   p95: {update_stats['p95']:.2f}ms (target: <100ms)")
    print(f"   p99: {update_stats['p99']:.2f}ms")
    print(f"   mean: {update_stats['mean']:.2f}ms")

    # Test health check (SC-005: p99 < 10ms)
    print("\n5. Testing GET /health (Health Check)")
    health_latencies = measure_latency(test_health_check, 100)
    health_stats = calculate_percentiles(health_latencies)
    print(f"   p99: {health_stats['p99']:.2f}ms (target: <10ms)")
    print(f"   p95: {health_stats['p95']:.2f}ms")
    print(f"   mean: {health_stats['mean']:.2f}ms")

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION RESULTS:")
    print("=" * 60)

    crud_p95_pass = all(
        [
            create_stats["p95"] < 100,
            list_stats["p95"] < 100,
            get_stats["p95"] < 100,
            update_stats["p95"] < 100,
        ]
    )

    health_p99_pass = health_stats["p99"] < 10

    print(f"\nSC-001: CRUD p95 < 100ms: {'PASS ✓' if crud_p95_pass else 'FAIL ✗'}")
    print(f"  - POST /todos p95: {create_stats['p95']:.2f}ms")
    print(f"  - GET /todos p95: {list_stats['p95']:.2f}ms")
    print(f"  - GET /todos/{{id}} p95: {get_stats['p95']:.2f}ms")
    print(f"  - PUT /todos/{{id}} p95: {update_stats['p95']:.2f}ms")

    print(
        f"\nSC-005: Health check p99 < 10ms: {'PASS ✓' if health_p99_pass else 'FAIL ✗'}"
    )
    print(f"  - GET /health p99: {health_stats['p99']:.2f}ms")

    if crud_p95_pass and health_p99_pass:
        print("\n✓ All performance requirements met!")
        return 0
    else:
        print("\n✗ Some performance requirements not met")
        return 1


if __name__ == "__main__":
    exit(main())
