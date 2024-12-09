# AI PR Reviewer

AI-powered tool for reviewing GitHub Pull Requests (PRs). This project uses artificial intelligence to analyze PRs for code style, best practices, bugs, and more.

## Project Setup

Follow these steps to get the project up and running:

### Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.11.6** or higher
- **PostgreSQL**
- **Redis**

Alternatively, you can use **Docker** to spin up these services.

---

### Clone the Repository

Start by cloning the repository to your local machine:

```bash
git clone https://github.com/avirajbhatt99/pr_reviewer.git
cd pr_reviewer
```

---

### Setting Up Python

1. **Create a Virtual Environment**:

   This isolates your dependencies from the global Python environment.

   ```bash
   python3 -m venv .venv
   ```

2. **Activate the Virtual Environment**:

   - **For Linux/macOS**:

     ```bash
     source .venv/bin/activate
     ```

3. **Install Required Packages**:

   After activating the virtual environment, install the necessary Python packages.

   ```bash
   pip install -r requirements.txt
   ```

---

### Setting Up Postgres and Redis

To run **Postgres** and **Redis** locally, you can use Docker Compose.

1. **Run PostgreSQL**:

   From the project root, run the following command to start the PostgreSQL container:

   ```bash
   docker-compose -f docker_compose/postgres/docker-compose.yaml up
   ```

2. **Run Redis**:

   Similarly, start the Redis container:

   ```bash
   docker-compose -f docker_compose/redis/docker-compose.yaml up
   ```

   Both services will run in the background.

---

### Environment Setup

The project uses environment variables for configuration. You'll need to create a `.env` file to store these variables.

1. **Copy the Example Environment File**:

   Copy the example environment file and rename it to `.env`:

   ```bash
   cp .env.development .env
   ```

2. **Edit the `.env` File**:

   Open `.env` and fill in the required values (e.g., database connection settings, Redis settings, etc.):

   ```bash
   nano .env
   ```

3. **Source the `.env` File**:

   Load the environment variables into your shell:

   ```bash
   source .env
   ```

---

### Running the Server

To start the API server, run the following command:

```bash
python src/server.py
```

The server will be available at `http://localhost:8000`.

---

### Running Celery

Celery is used to process tasks asynchronously. To run the Celery worker, execute the following:

```bash
celery -A src.worker.celery worker --loglevel=info
```

The worker will process tasks like PR analysis, and you should see logs indicating task processing.

---

### **Steps to Install and Run Ollama Locally:**

#### 1. **Download and Install Ollama CLI:**

- Go to the [Ollama download page](https://ollama.com/download).
- Choose the appropriate version for your operating system (macOS, Windows, or Linux).
- Download and install the Ollama CLI by following the instructions on the page.

#### 2. **Run Ollama:**

Once the Ollama CLI is installed, you can use the following command to run **LLama 3.2** locally:

```bash
ollama run llama3.2
```

This will start the Llama 3.2 model locally.

---

## **API Documentation**

**GET** `/v1/health`

#### Description:

This endpoint checks the health status of the server. It is typically used for monitoring purposes to ensure that the server is running and accessible.

#### Response:

- **200 OK**:
  - The server is running and responsive.

#### Response Example:

```json
{
  "message": "Server is running"
}
```

---

**POST** `/v1/analyze-pr`

#### Description:

This endpoint initiates an asynchronous analysis of a GitHub Pull Request (PR). The PR is analyzed for potential code style issues, bugs, performance improvements, and best practices. If the PR has already been analyzed, the task is fetched from the cache.

- **Cache Check**: If the PR has been analyzed previously, it returns the `task_id` of the ongoing or completed task.
- **Cache Miss**: If the PR is not in the cache, a new Celery task is triggered to analyze the PR, and the task ID is returned.

#### Request Body:

The request body should be a JSON object with the following fields:

- `repo_url` (string): The URL of the GitHub repository (e.g., `https://github.com/user/repo`).
- `pr_number` (integer): The pull request number (e.g., `123`).

#### Example Request:

```json
{
  "repo_url": "https://github.com/potpie-ai/potpie",
  "pr_number": 123
}
```

#### Response:

- **200 OK** (Cache Hit):

  - If the PR analysis is already in progress or completed and cached, it returns the cached `task_id`.

- **202 ACCEPTED** (Task Submitted):
  - If the PR is being analyzed for the first time, the task is created in Celery, and a new `task_id` is returned.

#### Response Example:

- **200 OK** (Cache Hit):

  ```json
  {
    "task_id": "12345"
  }
  ```

- **202 ACCEPTED** (Task Created):
  ```json
  {
    "task_id": "67890"
  }
  ```

#### Error Responses:

- **400 Bad Request**:

  - If the request is missing required fields, the API will return a 400 status code with an error message.

  Example:

  ```json
  {
    "detail": "Missing required fields"
  }
  ```

---

**GET** `/v1/status/{task_id}`

#### Description:

This endpoint allows you to check the status of a specific task by its `task_id`. The task ID corresponds to an ongoing or completed task that was created for analyzing a pull request (PR). If the task is found, it will return its current status and details. If the task does not exist, it returns an error message.

#### Path Parameters:

- `task_id` (string): The unique identifier for the task, typically provided when a task is created (e.g., `12345`).

#### Response:

- **200 OK**:

  - If the task is found, it returns the task status with relevant details.

- **404 Not Found**:
  - If the task is not found in the system, it returns an error message.

#### Response Example:

- **200 OK** (Task Found):

  ```json
  {
    "task_id": "12345",
    "status": "completed"
  }
  ```

- **404 Not Found** (Task Not Found):
  ```json
  {
    "error": "Task not found"
  }
  ```
  Here is the API documentation for the `/results/{task_id}` endpoint:

---

**GET** `/v1/results/{task_id}`

#### Description:

This endpoint allows you to retrieve the results of a task based on the provided `task_id`. If the task results are already cached, they will be returned from the cache. Otherwise, the system will fetch the results from the database and cache them for future requests. If the task has not been completed or found, an error message is returned.

#### Path Parameters:

- `task_id` (string): The unique identifier for the task. This ID corresponds to the task created for analyzing a pull request (PR) and can be used to fetch the task results.

#### Response:

- **200 OK**:

  - If the task results are found (either from cache or database), it returns the results along with the task status as "completed".

- **404 Not Found**:
  - If the task is not found or no results are available for the given `task_id`, it returns an error message.

#### Response Example:

- **200 OK** (Task Found, Results Retrieved):

  ```json
  {
    "task_id": "12345",
    "status": "completed",
    "results": {
      "files": [
        {
          "name": "main.py",
          "issues": [
            {
              "type": "style",
              "line": 15,
              "description": "Line too long",
              "suggestion": "Break line into multiple lines"
            },
            {
              "type": "bug",
              "line": 23,
              "description": "Potential null pointer",
              "suggestion": "Add null check"
            }
          ]
        }
      ],
      "summary": {
        "total_files": 1,
        "total_issues": 2,
        "critical_issues": 1
      }
    }
  }
  ```

- **404 Not Found** (Task Not Found):
  ```json
  {
    "error": "Task not found"
  }
  ```

---
