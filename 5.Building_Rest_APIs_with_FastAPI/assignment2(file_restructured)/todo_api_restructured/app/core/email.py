import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from app.core.config import settings


async def send_email(to_email: str, subject: str, body: str):
    """
    Send email notification.
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: HTML email body
    """
    try:
        message = MIMEMultipart()
        message["From"] = settings.FROM_EMAIL
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        
        async with aiosmtplib.SMTP(
            hostname=settings.SMTP_SERVER,
            port=settings.SMTP_PORT
        ) as smtp:
            await smtp.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            await smtp.send_message(message)
    except Exception as e:
        print(f"Email error: {e}")


async def notify_task_assigned(user_email: str, task_name: str, admin_email: str):
    """
    Notify user of task assignment.
    
    Args:
        user_email: User's email address
        task_name: Name of the assigned task
        admin_email: Admin's email address
    """
    subject = f"New Task Assigned: {task_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>New Task Assigned</h2>
        <p>Hi {user_email},</p>
        <p>Admin {admin_email} has assigned you a new task: <strong>{task_name}</strong></p>
        <p>Please log in to view details.</p>
        <hr>
        <p style="font-size: 12px; color: #666;">
            This is an automated message from {settings.APP_NAME}
        </p>
    </body>
    </html>
    """
    await send_email(user_email, subject, body)


async def notify_task_completed(admin_email: str, task_name: str, user_email: str):
    """
    Notify admin of task completion.
    
    Args:
        admin_email: Admin's email address
        task_name: Name of the completed task
        user_email: User's email address
    """
    subject = f"Task Completed: {task_name}"
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h2>Task Completed</h2>
        <p>Hi {admin_email},</p>
        <p>User {user_email} has completed the task: <strong>{task_name}</strong></p>
        <hr>
        <p style="font-size: 12px; color: #666;">
            This is an automated message from {settings.APP_NAME}
        </p>
    </body>
    </html>
    """
    await send_email(admin_email, subject, body)
