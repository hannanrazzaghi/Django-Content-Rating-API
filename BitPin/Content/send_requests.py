import aiohttp
import asyncio
import random
import time

BASE_URL = "http://127.0.0.1:8000/api/v1/content/score/"
NUM_WORKERS = 10

async def send_request(session, data, semaphore):
    async with semaphore:
        async with session.post(BASE_URL, json=data) as response:
            if response.status != 200 and response.status != 201:
                return f"Error: {response.status} - {await response.text()}"
            return "Success"


async def generate_data():
    return {
        "content_id": random.randint(1, 100),
        "user_id": random.randint(1, 1000),
        "score_value": random.randint(0, 5)
    }


async def send_requests(num_requests=5000):
    semaphore = asyncio.Semaphore(NUM_WORKERS)
    async with aiohttp.ClientSession() as session:
        tasks = [
            send_request(session, await generate_data(), semaphore)
            for _ in range(num_requests)
        ]
        results = await asyncio.gather(*tasks)
        successful_requests = sum(1 for result in results if result == "Success")
        failed_requests = num_requests - successful_requests
        print(f"Total Successful Requests: {successful_requests}")
        print(f"Total Failed Requests: {failed_requests}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(send_requests(num_requests=200))
    print(f"Total Time: {time.time() - start_time} seconds")