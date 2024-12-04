# Django Content Rating API

A high-performance Django application built with **Django REST Framework (DRF)** to manage content and user ratings. The application is designed to handle large-scale ratings while preventing fraudulent or biased ratings from affecting the overall scores. It includes optimization techniques to handle thousands of requests per second.

---

## Features

### 1. Display List of Contents
- Lists all content with:
  - **Title**
  - **Number of ratings**
  - **Average score**
- Optimized for performance using precomputed aggregates and efficient database queries.
- **Pagination** is used to handle large datasets in a scalable way, ensuring that responses remain fast even with thousands of content items.
- **Caching**: The list of content is cached for 5 minutes to minimize database hits. If the cache is expired or unavailable, the content list is fetched from the database and cached again for faster subsequent responses.

### 2. Rate Content
- Allows users to rate content with a score between **0 and 5**.
- If a user has already rated a content, their score will be updated.
- Designed for high throughput, efficiently handling millions of ratings without performance degradation.
- **Indexing** is applied to speed up database queries, especially for frequently accessed fields like `user_id` and `content_id` in Score model and `title` in Content model.
- **Cache**: The score for each user and content pair is cached for one hour. This reduces redundant database queries when a user repeatedly rates the same content.

#### APIs for Rating and Content Interaction

##### **Content API (ContentView)**:
The `ContentView` API provides a list of all content, optimized for performance with pagination and caching.

- **GET Request**: Fetches all content with pagination, displaying:
  - **Title** of content
  - **Number of ratings**
  - **Average score**
  - **User's score** (if the user has rated)
  
- **Optimizations**:
  - **Pagination**: The API supports paginated responses to handle large datasets efficiently. The `page_size` is set to 100.
  - **Caching**: A cache is used to store the list of content for 5 minutes (`all_contents`), minimizing repeated database queries. If the cache is unavailable or expired, the content is fetched from the database and then cached again for subsequent requests.

##### **Score API (ScoreView)**:
The `ScoreView` API allows users to rate or update their rating on content. It includes robust caching and optimization techniques.

- **POST Request**: Submits a score for a content item.
  - Checks if the user has already rated the content:
    - If yes, it updates the score.
    - If no, it adds the new score.
  
- **Optimizations**:
  - **Atomic Transactions**: The database operations are wrapped in a transaction to ensure consistency (using `transaction.atomic()`).
  - **Caching**: The score for a specific user and content pair is cached for 1 hour, reducing the need to fetch scores from the database for each subsequent request.
  - **Efficient Updates**: If the score hasn't changed, the API doesn't update the database, improving performance by avoiding unnecessary writes.
  - **Score Average Calculation**: The average score for the content is dynamically updated whenever a new score is added or an existing score is modified.
  - **Concurrency Control**: The `select_for_update()` ensures that multiple users cannot update the same score concurrently, preventing race conditions.

### 3. Fraud Detection
- The system checks for potential fraud by comparing recent scores (in the last hour) to overall scores. If the recent average score differs significantly (more than 2 times the standard deviation) from the overall average, and there are enough scores, it flags potential fraud. If fraud is detected, it adjusts the overall average by excluding the suspicious scores. The 2 * standard deviation threshold is a common statistical method for identifying significant anomalies.
- The fraud detection algorithm uses statistical methods to detect outliers, flagging fraudulent ratings for further review. 
- **Celery** and **Redis** are used to handle background tasks efficiently, including the fraud detection mechanism, which processes ratings asynchronously without slowing down the main application.
- For more advanced fraud detection, a **Random Forest model** could be implemented to identify more complex patterns in the data, but for simplicity, we have implemented a basic algorithm that looks at the number of ratings within the past hour and compares their average scores to detect inconsistencies.

---

## Installation

### Prerequisites
- Python 3.9+
- Django 4.0+
- PostgreSQL (recommended for production)
- Redis (for Celery task queue)

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/content-rating-api.git
   cd content-rating-api
2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
3. Set up your PostgreSQL database and Redis server. You will need a running instance of both.
4. Migrate the database:
    ```bash
   python manage.py migrate
5. (Optional) Populate the database with dummy users and content:
   You can use the `populate_data.py` script to create some initial data for testing. This script generates 1000 users
and 100 content items with random ratings.
    ```bash
   python populate_data.py
### Optimizations
1. **send_requests.py - Efficient Request Handling**  
   The `send_requests.py` script is designed to simulate large numbers of requests. To optimize this, we use `asyncio` and `aiohttp` for asynchronous request handling.  
   Concurrency control is achieved through the use of a Semaphore, which limits the number of concurrent requests being made to the server, preventing overload.  
   Prior to optimization, sending 200 requests on a personal system took about 50 seconds. After implementing these optimizations, the same 200 requests now take about 10 seconds, showcasing the significant performance improvement.

2. **Cache and Database Optimization**  
   The Score API view uses caching to store frequent queries and reduce database load. This improves response time and decreases the server load.  
   Indexing is used in the models to speed up database queries, especially for frequently accessed fields like `user_id` and `content_id`.

3. **Fraud Detection via Celery**  
   Fraudulent ratings are detected using a background task managed by Celery and Redis.  
   The task checks the ratings in real-time and identifies suspicious patterns, such as unusual rating spikes. This process runs asynchronously, so it does not affect the user experience.  
   The fraud detection process compares the current ratings with the average rating scores over the last hour. If there is an unusually high or low rating score, it is flagged as suspicious.  
   This approach prevents fraudulent ratings from affecting the content's average score.

### Performance Comparison
**Before optimization:**
- Sending 200 requests on a personal system took approximately 50 seconds.

**After optimization:**
- With the use of `asyncio`, `aiohttp`, caching, indexing, and Celery tasks for fraud detection, the same 200 requests now take approximately 10 seconds.  
  These improvements significantly reduce the response time and increase the scalability of the application.

### Future Improvements
While the current fraud detection method is effective for basic use cases, more complex methods like **Random Forest** could be integrated to detect intricate patterns of fraudulent behavior. This would allow for a more precise fraud detection mechanism, analyzing patterns from multiple data points to identify sophisticated fraud tactics.

### Conclusion
This Django Content Rating API is optimized for high performance and scalability, with mechanisms in place to handle a large volume of requests and ratings. The inclusion of fraud detection ensures that the integrity of the ratings is maintained, and the use of caching, Celery, and Redis enhances overall performance. The application is ready to be deployed in production and can easily scale as needed.
