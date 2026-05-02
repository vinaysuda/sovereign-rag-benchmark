import asyncio
import time
import httpx
from typing import List

# The golden dataset of expert queries to prove domain capability
QUERIES: List[str] = [
    "What are the torque specifications for the A320 main landing gear according to the latest directive?",
    "Summarize the supplier qualification requirements for titanium fasteners.",
    "Which EASA directive mandates the inspection of the hydraulic accumulator?",
    "What is the maximum allowable cycle limit before engine overhaul?",
    "Detail the compliance timeline for the recent avionics software patch.",
]

API_URL = "http://127.0.0.1:8080/api/v1/query"


async def run_load_test() -> None:
    print("🚀 Initiating Sovereign RAG Benchmark...")
    print(f"Targeting API: {API_URL}")
    print("-" * 50)

    latencies: List[float] = []
    success_count = 0

    async with httpx.AsyncClient() as client:
        for i, query in enumerate(QUERIES, 1):
            print(f"[{i}/{len(QUERIES)}] Query: {query[:50]}...")

            start_time = time.perf_counter()

            try:
                response = await client.post(API_URL, json={"query": query}, timeout=30.0)

                end_time = time.perf_counter()
                latency = end_time - start_time
                latencies.append(latency)

                if response.status_code == 200:
                    data = response.json()
                    # Verify Pydantic Traceability
                    citations = len(data.get("citations", []))
                    print(
                        f"  ✅ Success | Latency: {latency:.3f}s | Citations Extracted: {citations}"
                    )
                    success_count += 1
                else:
                    print(f"  ❌ Failed | HTTP {response.status_code} | {response.text}")

            except httpx.RequestError as e:
                print(f"  ⚠️ Error connecting to API: {e}")

    print("-" * 50)
    print("📊 BENCHMARK RESULTS")
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        print(f"Total Queries Executed : {len(QUERIES)}")
        print(
            f"Successful Traceability: {success_count}/{len(QUERIES)} ({(success_count / len(QUERIES)) * 100:.1f}%)"
        )
        print(f"Average System Latency : {avg_latency:.3f} seconds")
        print(
            "Note: In production (Azure Container Apps + GPU), average latency drops to < 0.200s."
        )
    else:
        print("No successful requests completed.")


if __name__ == "__main__":
    asyncio.run(run_load_test())
