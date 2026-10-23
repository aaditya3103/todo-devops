let tasks = [];
let currentFilter = 'all';

// DOM Elements
const taskForm = document.getElementById('task-form');
const taskTitle = document.getElementById('task-title');
const taskDesc = document.getElementById('task-desc');
const taskPriority = document.getElementById('task-priority');
const taskDue = document.getElementById('task-due');
const taskList = document.getElementById('task-list');
const searchInput = document.getElementById('search-input');
const filterBtns = document.querySelectorAll('.filter-btn');

const statTotal = document.getElementById('stat-total');
const statPending = document.getElementById('stat-pending');
const statCompleted = document.getElementById('stat-completed');

// Edit Modal Elements
const editModal = document.getElementById('edit-modal');
const editForm = document.getElementById('edit-form');
const editTaskId = document.getElementById('edit-task-id');
const editTitle = document.getElementById('edit-title');
const editDesc = document.getElementById('edit-desc');
const editPriority = document.getElementById('edit-priority');
const editDue = document.getElementById('edit-due');
const closeModal = document.getElementById('close-modal');
const cancelEdit = document.getElementById('cancel-edit');

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    fetchTasks();

    taskForm.addEventListener('submit', handleAddTask);
    editForm.addEventListener('submit', handleSaveEdit);
    searchInput.addEventListener('input', renderTasks);

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentFilter = btn.dataset.filter;
            renderTasks();
        });
    });

    closeModal.addEventListener('click', closeEditModal);
    cancelEdit.addEventListener('click', closeEditModal);

    window.addEventListener('click', (e) => {
        if (e.target === editModal) closeEditModal();
    });
});

// Fetch all tasks from backend
async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks');
        if (!response.ok) throw new Error('Failed to fetch tasks');
        tasks = await response.json();
        updateStats();
        renderTasks();
    } catch (err) {
        taskList.innerHTML = `<div class="empty-state">Error loading tasks: ${err.message}</div>`;
    }
}

// Update Header Statistics
function updateStats() {
    const total = tasks.length;
    const completed = tasks.filter(t => t.completed).length;
    const pending = total - completed;

    statTotal.textContent = total;
    statCompleted.textContent = completed;
    statPending.textContent = pending;
}

// Render task list based on active filter and search query
function renderTasks() {
    const query = searchInput.value.toLowerCase().trim();

    let filtered = tasks.filter(task => {
        if (currentFilter === 'pending') return !task.completed;
        if (currentFilter === 'completed') return task.completed;
        return true;
    });

    if (query) {
        filtered = filtered.filter(task =>
            task.title.toLowerCase().includes(query) ||
            (task.description && task.description.toLowerCase().includes(query))
        );
    }

    if (filtered.length === 0) {
        taskList.innerHTML = `<div class="empty-state">No tasks found.</div>`;
        return;
    }

    taskList.innerHTML = filtered.map(task => `
        <div class="task-card ${task.completed ? 'completed' : ''}" data-id="${task.id}">
            <input type="checkbox" class="task-checkbox" ${task.completed ? 'checked' : ''} onchange="toggleTask(${task.id})">
            <div class="task-content">
                <div class="task-header-row">
                    <span class="task-title">${escapeHtml(task.title)}</span>
                </div>
                ${task.description ? `<p class="task-desc">${escapeHtml(task.description)}</p>` : ''}
                <div class="task-meta">
                    <span class="badge badge-${task.priority.toLowerCase()}">${task.priority}</span>
                    ${task.due_date ? `<span class="due-badge">📅 Due: ${task.due_date}</span>` : ''}
                </div>
            </div>
            <div class="task-actions">
                <button class="btn-icon" title="Edit" onclick="openEditModal(${task.id})">✏️</button>
                <button class="btn-icon delete-btn" title="Delete" onclick="deleteTask(${task.id})">🗑️</button>
            </div>
        </div>
    `).join('');
}

// Add Task Handler
async function handleAddTask(e) {
    e.preventDefault();
    const title = taskTitle.value.trim();
    if (!title) return;

    const newTask = {
        title: title,
        description: taskDesc.value.trim(),
        priority: taskPriority.value,
        due_date: taskDue.value
    };

    try {
        const response = await fetch('/api/tasks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newTask)
        });

        if (!response.ok) throw new Error('Failed to create task');

        const created = await response.json();
        tasks.unshift(created);
        taskForm.reset();
        updateStats();
        renderTasks();
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

// Toggle Task Completed
async function toggleTask(id) {
    try {
        const response = await fetch(`/api/tasks/${id}/toggle`, {
            method: 'PATCH'
        });

        if (!response.ok) throw new Error('Failed to toggle status');

        const updated = await response.json();
        const index = tasks.findIndex(t => t.id === id);
        if (index !== -1) {
            tasks[index] = updated;
            updateStats();
            renderTasks();
        }
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

// Open Edit Modal
function openEditModal(id) {
    const task = tasks.find(t => t.id === id);
    if (!task) return;

    editTaskId.value = task.id;
    editTitle.value = task.title;
    editDesc.value = task.description || '';
    editPriority.value = task.priority;
    editDue.value = task.due_date || '';

    editModal.classList.add('open');
}

// Close Edit Modal
function closeEditModal() {
    editModal.classList.remove('open');
    editForm.reset();
}

// Save Edit Handler
async function handleSaveEdit(e) {
    e.preventDefault();
    const id = parseInt(editTaskId.value, 10);
    const updatedData = {
        title: editTitle.value.trim(),
        description: editDesc.value.trim(),
        priority: editPriority.value,
        due_date: editDue.value
    };

    try {
        const response = await fetch(`/api/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        });

        if (!response.ok) throw new Error('Failed to update task');

        const updated = await response.json();
        const index = tasks.findIndex(t => t.id === id);
        if (index !== -1) {
            tasks[index] = updated;
            updateStats();
            renderTasks();
        }
        closeEditModal();
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

// Delete Task Handler
async function deleteTask(id) {
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
        const response = await fetch(`/api/tasks/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) throw new Error('Failed to delete task');

        tasks = tasks.filter(t => t.id !== id);
        updateStats();
        renderTasks();
    } catch (err) {
        alert('Error: ' + err.message);
    }
}

// Utility: Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
