document.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length === 0) return;
    setTimeout(function () {
        alerts.forEach(function (el) {
            try {
                // Use Bootstrap's alert plugin if available
                if (typeof $(el).alert === 'function') {
                    $(el).alert('close');
                } else {
                    // Fallback: remove element
                    el.parentNode && el.parentNode.removeChild(el);
                }
            } catch (e) {
                el.parentNode && el.parentNode.removeChild(el);
            }
        });
    }, 3000);
});

const deleteTask = (taskId) => {
    fetch("/delete-task", {
        method: "POST",
        body: JSON.stringify({ task_id: taskId }),
    }).then(() => {
        window.location.href = "/";
    })
}

const updateTask = (taskId, field, value) => {
    fetch("/update-task", {
        method: "POST",
        body: JSON.stringify({ task_id: taskId, field, value }),
    }).then(() => {
        // no reload needed; leaving as is for quick UX
    })
}

const toggleTaskEdit = (taskId) => {
    const el = document.getElementById(`task-edit-${taskId}`);
    if (!el) return;
    el.classList.toggle('d-none');
}

const saveTaskEdit = (taskId) => {
    const status = document.getElementById(`edit-status-${taskId}`)?.value;
    const priority = document.getElementById(`edit-priority-${taskId}`)?.value;
    const start_date = document.getElementById(`edit-start-${taskId}`)?.value;
    const end_date = document.getElementById(`edit-end-${taskId}`)?.value;

    fetch("/update-task", {
        method: "POST",
        body: JSON.stringify({ task_id: taskId, data: { status, priority, start_date, end_date } }),
    }).then(() => {
        window.location.href = "/";
    })
}