import os

import resend
from dotenv import load_dotenv


load_dotenv()


RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_FROM_EMAIL = os.getenv("RESEND_FROM_EMAIL")


def send_verification_email(
    email: str,
    code: str,
):
    if not RESEND_API_KEY:
        print(
            f"[EMAIL DEV] Verification code for {email}: {code}"
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
    if not RESEND_API_KEY:
        print(
            f"[EMAIL DEV] Password reset code for {email}: {code}"
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