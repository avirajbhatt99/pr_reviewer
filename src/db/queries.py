import json
from src.db.postgres import fetch_data, insert_data


def get_task_status(task_id):
    """
    Get task status for given task_id
    """
    query = f"SELECT status FROM analyzed_pr WHERE task_id = '{task_id}'"
    rows = fetch_data(query)
    if rows:
        return rows[0]
    else:
        return None


def insert_task(repo_url, pr_number, task_id, status):
    """
    Insert task into analyzed_pr table
    """
    query = f"INSERT INTO analyzed_pr (repo_url, pr_number, task_id, status) VALUES (%s, %s, %s, %s);"
    insert_data(query, (repo_url, pr_number, task_id, status))


def update_result(task_id, result):
    """
    Update result and status for given task_id
    """
    query = (
        f"UPDATE analyzed_pr SET result = %s, status = 'completed' WHERE task_id = %s;"
    )
    insert_data(query, (json.dumps(result), task_id))


def get_results(task_id):
    """
    Get results for given task_id
    """
    query = f"SELECT result FROM analyzed_pr WHERE task_id = '{task_id}';"
    rows = fetch_data(query)
    if rows:
        return (
            json.loads(rows[0]["result"]) if isinstance(rows[0]["result"], str) else []
        )
    else:
        return None
