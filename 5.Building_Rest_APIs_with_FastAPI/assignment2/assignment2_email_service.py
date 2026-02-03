import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from sqlalchemy.orm import Session
from datetime import datetime

from assignment2_config import (
    SMTP_SERVER, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL
)
from assignment2_models import EmailNotificationLog, Task, User


# Email templates
TASK_ASSIGNMENT_TEMPLATE = """
<html> 
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { background-color: #4CAF50; color: white; padding: 20px; }
        .content { padding: 20px; }
        .task-details { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }
        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>New Task Assigned</h1>
        </div>
        <div class="content">
            <p>Hi {{ user_name }},</p>
            <p>A new task has been assigned to you:</p>
            <div class="task-details">
                <p><strong>Task Name:</strong> {{ task_name }}</p>
                <p><strong>Description:</strong> {{ task_description }}</p>
                <p><strong>Start Date:</strong> {{ start_date }}</p>
                <p><strong>End Date:</strong> {{ end_date }}</p>
                <p><strong>Priority:</strong> {{ priority }}</p>
            </div>
            <p>Please log in to your account to view more details and manage your tasks.</p>
            <p>Best regards,<br/>Todo App Team</p>
        </div>
        <div class="footer">
            <p>If you don't want to receive these emails, you can unsubscribe from your account settings.</p>
        </div>
    </div>
</body>
</html>
"""

TASK_COMPLETION_TEMPLATE = """
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { background-color: #2196F3; color: white; padding: 20px; }
        .content { padding: 20px; }
        .task-details { background-color: #f5f5f5; padding: 15px; border-radius: 5px; }
        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Task Completed</h1>
        </div>
        <div class="content">
            <p>Hi {{ admin_name }},</p>
            <p>A task has been completed by {{ user_name }}:</p>
            <div class="task-details">
                <p><strong>Task Name:</strong> {{ task_name }}</p>
                <p><strong>Description:</strong> {{ task_description }}</p>
                <p><strong>Completed By:</strong> {{ user_name }}</p>
                <p><strong>Completion Time:</strong> {{ completion_time }}</p>
            </div>
            <p>Please log in to review the task completion details.</p>
            <p>Best regards,<br/>Todo App Team</p>
        </div>
        <div class="footer">
            <p>This is an automated notification for task management.</p>
        </div>
    </div>
</body>
</html>
"""


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send email via SMTP"""
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = FROM_EMAIL
        message["To"] = to_email

        part = MIMEText(html_content, "html")
        message.attach(part)

        async with aiosmtplib.SMTP(hostname=SMTP_SERVER, port=SMTP_PORT) as smtp:
            await smtp.login(SMTP_USER, SMTP_PASSWORD)
            await smtp.sendmail(FROM_EMAIL, [to_email], message.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        return False


async def notify_task_assignment(
    db: Session,
    task: Task,
    assigned_user: User,
    admin: User
):
    """Send notification email when task is assigned"""
    if not assigned_user.receive_notifications:
        return

    template = Template(TASK_ASSIGNMENT_TEMPLATE)
    html_content = template.render(
        user_name=assigned_user.email,
        task_name=task.name,
        task_description=task.description or "No description",
        start_date=task.start_date.strftime("%Y-%m-%d %H:%M"),
        end_date=task.end_date.strftime("%Y-%m-%d %H:%M"),
        priority=task.priority.value
    )

    subject = f"New Task Assigned: {task.name}"
    
    success = await send_email(assigned_user.email, subject, html_content)
    
    # Log notification
    notification_log = EmailNotificationLog(
        user_id=assigned_user.id,
        task_id=task.id,
        notification_type="task_assigned",
        recipient_email=assigned_user.email,
        subject=subject,
        sent_successfully=success
    )
    db.add(notification_log)
    db.commit()


async def notify_task_completion(
    db: Session,
    task: Task,
    completed_by_user: User,
    admin: User
):
    """Send notification email when task is completed"""
    template = Template(TASK_COMPLETION_TEMPLATE)
    html_content = template.render(
        admin_name=admin.email,
        user_name=completed_by_user.email,
        task_name=task.name,
        task_description=task.description or "No description",
        completion_time=datetime.utcnow().strftime("%Y-%m-%d %H:%M")
    )

    subject = f"Task Completed: {task.name}"
    
    success = await send_email(admin.email, subject, html_content)
    
    # Log notification
    notification_log = EmailNotificationLog(
        user_id=admin.id,
        task_id=task.id,
        notification_type="Task_Completed",
        recipient_email=admin.email,
        subject=subject,
        sent_successfully=success
    )
    db.add(notification_log)
    db.commit()
