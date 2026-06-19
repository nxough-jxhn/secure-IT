import os
import smtplib
from email.message import EmailMessage


def send_verification_email(to_email: str, verification_url: str, year_level: str, profile_picture_url: str = "") -> bool:
    host = os.getenv("MAILTRAP_HOST")
    port = int(os.getenv("MAILTRAP_PORT", "2525"))
    username = os.getenv("MAILTRAP_USER")
    password = os.getenv("MAILTRAP_PASS")

    if not host or not username or not password:
        return False

    message = EmailMessage()
    message["Subject"] = "Verify your Secure-IT account"
    message["From"] = os.getenv("EMAIL_FROM", "Secure-IT <noreply@secure-it.local>")
    message["To"] = to_email
    message.set_content(
        f"Welcome to Secure-IT!\n\nYour year level: {year_level or 'Not set'}\n\nVerify your account here:\n{verification_url}\n"
    )

    image_html = ""
    if profile_picture_url:
        image_html = f'<img src="{profile_picture_url}" alt="Profile picture" style="width:72px;height:72px;border-radius:9999px;object-fit:cover;margin-top:12px;" />'

    message.add_alternative(
        f"""
        <html>
          <body style="margin:0;padding:24px;background:#0f172a;color:#e2e8f0;font-family:Arial,sans-serif;">
            <div style="max-width:560px;margin:0 auto;background:#111827;border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:24px;">
              <h2 style="margin-top:0;color:#fff;">Verify your Secure-IT account</h2>
              <p>Your year level: <strong>{year_level or 'Not set'}</strong></p>
              {image_html}
              <p style="line-height:1.6;color:#cbd5e1;">Click the button below to verify your email address and activate your Secure-IT account.</p>
              <p><a href="{verification_url}" style="display:inline-block;background:linear-gradient(90deg,#77f2a2,#46d6ff);color:#020617;text-decoration:none;font-weight:800;padding:12px 18px;border-radius:14px;">Verify Email</a></p>
              <p style="font-size:12px;color:#94a3b8;">If you did not create this account, you can ignore this message.</p>
            </div>
          </body>
        </html>
        """,
        subtype="html",
    )

    try:
        with smtplib.SMTP(host, port, timeout=15) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(username, password)
            smtp.send_message(message)
    except Exception:
        return False

    return True