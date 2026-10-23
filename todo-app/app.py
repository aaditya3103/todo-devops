from datetime import datetime, timezone
import os
import time
from flask import Flask, jsonify, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///todo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-123')

db = SQLAlchemy(app)

# Prometheus Metrics
HTTP_REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP Requests',
    ['method', 'endpoint', 'status_code']
)

HTTP_REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['endpoint']
)

TASK_COUNT_GAUGE = Gauge(
    'todo_tasks_total',
    'Total number of tasks by completion status',
    ['status']
)

def update_task_metrics():
    """Update prometheus gauge metrics for active and completed tasks."""
    try:
        total_pending = Task.query.filter_by(completed=False).count()
        total_completed = Task.query.filter_by(completed=True).count()
        TASK_COUNT_GAUGE.labels(status='pending').set(total_pending)
        TASK_COUNT_GAUGE.labels(status='completed').set(total_completed)
    except Exception:
        pass


@app.before_request
def start_timer():
    request.start_time = time.time()


@app.after_request
def record_metrics(response):
    if hasattr(request, 'start_time'):
        latency = time.time() - request.start_time
        endpoint = request.endpoint or 'unknown'
        HTTP_REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
        HTTP_REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            status_code=response.status_code
        ).inc()
    return response


# Data Model
class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(500), default='')
    priority = db.Column(db.String(20), default='Medium')  # Low, Medium, High
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.String(20), default='')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'completed': self.completed,
            'due_date': self.due_date,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }


# Ensure tables are created
with app.app_context():
    db.create_all()
    update_task_metrics()


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/health')
def health_check():
    return jsonify({
        'status': 'UP',
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'service': 'todo-application'
    }), 200


@app.route('/metrics')
def metrics():
    update_task_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


# REST API Endpoints
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    status = request.args.get('status')
    query = Task.query

    if status == 'completed':
        query = query.filter_by(completed=True)
    elif status == 'pending':
        query = query.filter_by(completed=False)

    tasks = query.order_by(Task.id.desc()).all()
    return jsonify([t.to_dict() for t in tasks]), 200


@app.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404
    return jsonify(task.to_dict()), 200


@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json() or {}
    title = data.get('title', '').strip()

    if not title:
        return jsonify({'error': 'Title is required'}), 400

    task = Task(
        title=title,
        description=data.get('description', '').strip(),
        priority=data.get('priority', 'Medium'),
        due_date=data.get('due_date', '').strip(),
        completed=bool(data.get('completed', False))
    )
    db.session.add(task)
    db.session.commit()
    update_task_metrics()

    return jsonify(task.to_dict()), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json() or {}
    if 'title' in data:
        title = data['title'].strip()
        if not title:
            return jsonify({'error': 'Title cannot be empty'}), 400
        task.title = title

    if 'description' in data:
        task.description = data['description'].strip()
    if 'priority' in data:
        task.priority = data['priority']
    if 'due_date' in data:
        task.due_date = data['due_date'].strip()
    if 'completed' in data:
        task.completed = bool(data['completed'])

    db.session.commit()
    update_task_metrics()
    return jsonify(task.to_dict()), 200


@app.route('/api/tasks/<int:task_id>/toggle', methods=['PATCH'])
def toggle_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    task.completed = not task.completed
    db.session.commit()
    update_task_metrics()
    return jsonify(task.to_dict()), 200


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return jsonify({'error': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()
    update_task_metrics()
    return jsonify({'message': f'Task {task_id} deleted successfully'}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
