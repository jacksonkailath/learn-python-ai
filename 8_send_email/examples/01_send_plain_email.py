from pathlib import Path
import os
import smtplib
import sys
from email.message import EmailMessage

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / "project" / ".env"
load_dotenv(ENV_PATH)

# The environment variables this script needs. Keeping the names in one place
# makes the "what's missing?" check below trivial to read.
REQUIRED_VARS = (
    "SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD",
    "EMAIL_FROM", "EMAIL_TO",
)


def send_plain_email() -> None:
    """Build and send a one-line plain-text email from the current user to self."""
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    user = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]
    from_addr = os.environ["EMAIL_FROM"]
    to_addr = os.environ["EMAIL_TO"]

    # EmailMessage is the modern, batteries-included way to build a message.
    # It handles headers and encoding so you don't hand-assemble raw text.
    message = EmailMessage()
    message["Subject"] = "Hello from Python "
    message["From"] = from_addr
    message["To"] = to_addr
    message.set_content(
        "This plain-text email was sent by a Python script.\n\n"
        "If you're reading it in your inbox, your SMTP credentials work — "
        "which means the scheduled Monday report will work too."
    )

    # STARTTLS = connect in the clear on port 587, then upgrade the SAME
    # connection to encrypted before we ever send the password. Standard for
    # Gmail, Outlook, Fastmail, and most providers.
    print(f"Connecting to {host}:{port} ...")
    with smtplib.SMTP(host, port) as server:
        server.starttls()          # encrypt the channel https://... instead of http://
        server.login(user, password)
        server.send_message(message)

    print(f"Sent a plain-text email to {to_addr}.")


def main() -> None:
    missing = [name for name in REQUIRED_VARS if not os.environ.get(name)] #['SMTP_HOST']
    if missing:
        print("Email not sent — configuration missing.")
        print(f"Set these environment variables first: {', '.join(missing)}")
        print(
            "\n refer previous lecture where we discussed the .env file."
        )
        print(
            "Reminder: SMTP_PASSWORD is a Gmail *App Password*, not your normal "
            "password."
        )
        return  # graceful exit — no traceback, no attempted connection

    try:
        send_plain_email()
    except smtplib.SMTPAuthenticationError:
        print(
            "Login was rejected. For Gmail this almost always means you used "
            "your normal password instead of a 16-character App Password, or "
            "2-Step Verification isn't enabled on the account.",
            file=sys.stderr,
        )
    except OSError as error:
        # Network unreachable, wrong host/port, DNS failure, etc.
        print(f"Could not reach the mail server: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
