document.addEventListener("DOMContentLoaded", function () {
    // Enhanced alert animations
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        alerts.forEach((alert, index) => {
            alert.style.animationDelay = `${index * 0.1}s`;
        });
        
        setTimeout(function () {
            alerts.forEach(function (el) {
                el.style.animation = 'slideOutRight 0.5s ease-out forwards';
                setTimeout(() => {
                    try {
                        if (typeof $(el).alert === 'function') {
                            $(el).alert('close');
                        } else {
                            el.parentNode && el.parentNode.removeChild(el);
                        }
                    } catch (e) {
                        el.parentNode && el.parentNode.removeChild(el);
                    }
                }, 500);
            });
        }, 3000);
    }

    // Add loading states to buttons
    const buttons = document.querySelectorAll('button[type="submit"], .btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (this.type === 'submit' || this.classList.contains('btn-success')) {
                this.style.position = 'relative';
                this.style.overflow = 'hidden';
                
                // Add ripple effect
                const ripple = document.createElement('span');
                ripple.style.position = 'absolute';
                ripple.style.borderRadius = '50%';
                ripple.style.background = 'rgba(255,255,255,0.6)';
                ripple.style.transform = 'scale(0)';
                ripple.style.animation = 'ripple 0.6s linear';
                ripple.style.left = '50%';
                ripple.style.top = '50%';
                ripple.style.width = '20px';
                ripple.style.height = '20px';
                ripple.style.marginLeft = '-10px';
                ripple.style.marginTop = '-10px';
                
                this.appendChild(ripple);
                
                setTimeout(() => {
                    ripple.remove();
                }, 600);
            }
        });
    });

    // Enhanced form interactions
    const formControls = document.querySelectorAll('.form-control');
    formControls.forEach(control => {
        control.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        control.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
    });

    // Add stagger animation to task items
    const taskItems = document.querySelectorAll('.list-group-item');
    taskItems.forEach((item, index) => {
        item.style.animationDelay = `${index * 0.1}s`;
    });
});

// Enhanced delete task with animation
const deleteTask = (taskId) => {
    const taskElement = document.getElementById(`task-${taskId}`);
    if (taskElement) {
        // Add loading state
        const deleteBtn = taskElement.querySelector('.close');
        if (deleteBtn) {
            deleteBtn.innerHTML = '<span class="loading-spinner"></span>';
            deleteBtn.style.pointerEvents = 'none';
        }
        
        // Slide out animation
        taskElement.style.animation = 'slideOutLeft 0.3s ease-out forwards';
        
        fetch("/delete-task", {
            method: "POST",
            body: JSON.stringify({ task_id: taskId }),
        }).then(() => {
            setTimeout(() => {
                window.location.href = "/";
            }, 300);
        }).catch(() => {
            // Reset button on error
            if (deleteBtn) {
                deleteBtn.innerHTML = '<span aria-hidden="true">&times</span>';
                deleteBtn.style.pointerEvents = 'auto';
            }
            taskElement.style.animation = '';
        });
    }
}

const updateTask = (taskId, field, value) => {
    fetch("/update-task", {
        method: "POST",
        body: JSON.stringify({ task_id: taskId, field, value }),
    }).then(() => {
        // Add success animation
        const taskElement = document.getElementById(`task-${taskId}`);
        if (taskElement) {
            taskElement.style.animation = 'pulse 0.6s ease-out';
            setTimeout(() => {
                taskElement.style.animation = '';
            }, 600);
        }
    })
}

const toggleTaskEdit = (taskId) => {
    const el = document.getElementById(`task-edit-${taskId}`);
    if (!el) return;
    
    if (el.classList.contains('d-none')) {
        el.classList.remove('d-none');
        el.style.opacity = '0';
        el.style.transform = 'translateY(-10px)';
        
        // Animate in
        setTimeout(() => {
            el.style.transition = 'all 0.3s ease-out';
            el.style.opacity = '1';
            el.style.transform = 'translateY(0)';
        }, 10);
    } else {
        // Animate out
        el.style.transition = 'all 0.3s ease-out';
        el.style.opacity = '0';
        el.style.transform = 'translateY(-10px)';
        
        setTimeout(() => {
            el.classList.add('d-none');
            el.style.transition = '';
            el.style.opacity = '';
            el.style.transform = '';
        }, 300);
    }
}

const saveTaskEdit = (taskId) => {
    const saveBtn = document.querySelector(`button[onclick="saveTaskEdit(${taskId})"]`);
    if (saveBtn) {
        saveBtn.innerHTML = '<span class="loading-spinner"></span> Lưu...';
        saveBtn.disabled = true;
    }
    
    const status = document.getElementById(`edit-status-${taskId}`)?.value;
    const priority = document.getElementById(`edit-priority-${taskId}`)?.value;
    const start_date = document.getElementById(`edit-start-${taskId}`)?.value;
    const end_date = document.getElementById(`edit-end-${taskId}`)?.value;

    fetch("/update-task", {
        method: "POST",
        body: JSON.stringify({ task_id: taskId, data: { status, priority, start_date, end_date } }),
    }).then(() => {
        // Success animation
        const taskElement = document.getElementById(`task-${taskId}`);
        if (taskElement) {
            taskElement.style.animation = 'bounce 0.6s ease-out';
        }
        
        setTimeout(() => {
            window.location.href = "/";
        }, 600);
    }).catch(() => {
        // Reset button on error
        if (saveBtn) {
            saveBtn.innerHTML = 'Lưu';
            saveBtn.disabled = false;
        }
    });
}

// Password reset validation
document.addEventListener("DOMContentLoaded", function () {
    const resetForm = document.querySelector('form[action*="reset-password"]');
    if (resetForm) {
        const newPasswordInput = document.getElementById('new_password');
        const confirmPasswordInput = document.getElementById('confirm_password');
        
        function validatePasswords() {
            const newPassword = newPasswordInput.value;
            const confirmPassword = confirmPasswordInput.value;
            
            if (newPassword.length !== 8) {
                newPasswordInput.setCustomValidity('Mật khẩu phải đúng 8 ký tự');
                return false;
            }
            
            if (newPassword !== confirmPassword) {
                confirmPasswordInput.setCustomValidity('Mật khẩu xác nhận không trùng khớp');
                return false;
            }
            
            newPasswordInput.setCustomValidity('');
            confirmPasswordInput.setCustomValidity('');
            return true;
        }
        
        newPasswordInput.addEventListener('input', validatePasswords);
        confirmPasswordInput.addEventListener('input', validatePasswords);
        
        resetForm.addEventListener('submit', function(e) {
            if (!validatePasswords()) {
                e.preventDefault();
            }
        });
    }
});