import pytest
from app import app, db, Task


@pytest.fixture
def client():
    # Configure app for testing with in-memory database
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_home_page(client):
    """Test that home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'TaskPilot' in response.data


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'UP'
    assert json_data['service'] == 'todo-application'


def test_metrics_endpoint(client):
    """Test Prometheus metrics endpoint."""
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'http_requests_total' in response.data or b'todo_tasks_total' in response.data


def test_create_task(client):
    """Test creating a new task via API (POST)."""
    payload = {
        'title': 'Setup Jenkins CI Pipeline',
        'description': 'Configure GitHub webhook and pipeline stages',
        'priority': 'High',
        'due_date': '2026-10-30'
    }
    response = client.post('/api/tasks', json=payload)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['id'] is not None
    assert json_data['title'] == 'Setup Jenkins CI Pipeline'
    assert json_data['completed'] is False
    assert json_data['priority'] == 'High'


def test_create_task_empty_title_validation(client):
    """Test validation: cannot create task without a title."""
    response = client.post('/api/tasks', json={'title': '   '})
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data


def test_get_tasks(client):
    """Test fetching all tasks (GET)."""
    client.post('/api/tasks', json={'title': 'Task 1', 'priority': 'Low'})
    client.post('/api/tasks', json={'title': 'Task 2', 'priority': 'Medium'})

    response = client.get('/api/tasks')
    assert response.status_code == 200
    tasks = response.get_json()
    assert len(tasks) == 2


def test_get_task_by_id(client):
    """Test fetching a specific task by id."""
    res = client.post('/api/tasks', json={'title': 'Unique Task'})
    task_id = res.get_json()['id']

    response = client.get(f'/api/tasks/{task_id}')
    assert response.status_code == 200
    assert response.get_json()['title'] == 'Unique Task'


def test_get_task_not_found(client):
    """Test getting a non-existent task returns 404."""
    response = client.get('/api/tasks/99999')
    assert response.status_code == 404
    assert 'error' in response.get_json()


def test_update_task(client):
    """Test updating task details (PUT)."""
    res = client.post('/api/tasks', json={'title': 'Original Title', 'priority': 'Low'})
    task_id = res.get_json()['id']

    update_payload = {
        'title': 'Updated Title',
        'description': 'Updated details',
        'priority': 'High'
    }
    response = client.put(f'/api/tasks/{task_id}', json=update_payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Updated Title'
    assert data['description'] == 'Updated details'
    assert data['priority'] == 'High'


def test_update_task_empty_title_validation(client):
    """Test updating task with blank title returns 400."""
    res = client.post('/api/tasks', json={'title': 'Task before empty update'})
    task_id = res.get_json()['id']

    response = client.put(f'/api/tasks/{task_id}', json={'title': '   '})
    assert response.status_code == 400


def test_toggle_task(client):
    """Test toggling task completion status (PATCH)."""
    res = client.post('/api/tasks', json={'title': 'Task to toggle'})
    task_id = res.get_json()['id']
    assert res.get_json()['completed'] is False

    # Toggle to true
    toggle_res1 = client.patch(f'/api/tasks/{task_id}/toggle')
    assert toggle_res1.status_code == 200
    assert toggle_res1.get_json()['completed'] is True

    # Toggle back to false
    toggle_res2 = client.patch(f'/api/tasks/{task_id}/toggle')
    assert toggle_res2.status_code == 200
    assert toggle_res2.get_json()['completed'] is False


def test_delete_task(client):
    """Test deleting a task (DELETE)."""
    res = client.post('/api/tasks', json={'title': 'Task to delete'})
    task_id = res.get_json()['id']

    del_res = client.delete(f'/api/tasks/{task_id}')
    assert del_res.status_code == 200

    # Ensure it's deleted
    get_res = client.get(f'/api/tasks/{task_id}')
    assert get_res.status_code == 404


def test_filter_tasks_by_status(client):
    """Test filtering tasks by status query param."""
    client.post('/api/tasks', json={'title': 'Pending Task 1', 'completed': False})
    client.post('/api/tasks', json={'title': 'Completed Task 2', 'completed': True})

    pending_res = client.get('/api/tasks?status=pending')
    assert pending_res.status_code == 200
    assert len(pending_res.get_json()) == 1
    assert pending_res.get_json()[0]['title'] == 'Pending Task 1'

    completed_res = client.get('/api/tasks?status=completed')
    assert completed_res.status_code == 200
    assert len(completed_res.get_json()) == 1
    assert completed_res.get_json()[0]['title'] == 'Completed Task 2'
