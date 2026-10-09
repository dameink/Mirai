import os

from fastapi import HTTPException
import resend
from dotenv import load_dotenv


load_dotenv()


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")


def require_email_configuration():
    from core.operations import closed_beta
    if closed_beta():
        raise HTTPException(status_code=503, detail="Mirai is in a private test. Email registration and recovery are not available yet.")
    if os.getenv("MIRAI_EMAIL_DEV_MODE", "").lower() == "true":
        return
    if not RESEND_API_KEY or not RESEND_FROM_EMAIL:
        raise HTTPException(status_code=503, detail="Email delivery is temporarily unavailable.")


def send_verification_email(
    email: str,
    code: str,
):
    require_email_configuration()
    if not RESEND_API_KEY:
        print(
            "[EMAIL DEV] Verification delivery skipped"
        )
        return

    if not RESEND_FROM_EMAIL:
        raise RuntimeError(
            "RESEND_FROM_EMAIL is not configured."
        )

    resend.api_key = RESEND_API_KEY

    resend.Emails.send(
        {
            "from": RESEND_FROM_EMAIL,
            "to": [email],
            "subject": "Your Mirai verification code",
            "html": f"""
                <div style="font-family: Arial, sans-serif;">
                    <h2>Verify your Mirai account</h2>

                    <p>Your verification code is:</p>

                    <h1 style="letter-spacing: 6px;">
                        {code}
                    </h1>

                    <p>
                        This code expires in 10 minutes.
                    </p>

                    <p>
                        If you did not create a Mirai account,
                        you can ignore this email.
                    </p>
                </div>
            """,
        }
    )

def send_password_reset_email(
    email: str,
    code: str,
):
    require_email_configuration()
    if not RESEND_API_KEY:
        print(
            "[EMAIL DEV] Password reset delivery skipped"
        )
        return

    if not RESEND_FROM_EMAIL:
        raise RuntimeError(
            "RESEND_FROM_EMAIL is not configured."
        )

    resend.api_key = RESEND_API_KEY

    resend.Emails.send(
        {
            "from": RESEND_FROM_EMAIL,
            "to": [email],
            "subject": "Reset your Mirai password",
            "html": f"""
                <div style="font-family: Arial, sans-serif;">
                    <h2>Reset your Mirai password</h2>

                    <p>Your password reset code is:</p>

                    <h1 style="letter-spacing: 6px;">
                        {code}
                    </h1>

                    <p>
                        This code expires in 10 minutes.
                    </p>

                    <p>
                        If you did not request a password reset,
                        you can ignore this email.
                    </p>
                </div>
            """,
        }
    )