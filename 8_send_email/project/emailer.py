"""
emailer.py

Generic, reusable email delivery: loading and validating SMTP/email
configuration from the environment, assembling an EmailMessage with an
HTML body and a file attachment, and sending it over SMTP with STARTTLS.
Knows nothing about any particular report or message content.

CONFIGURATION
--------------
All secrets and addresses are read from environment variables, loaded from
a .env file next to the calling script (see .env.example). Nothing secret
is hardcoded here.

Required:
    SMTP_HOST        e.g. smtp.gmail.com
    SMTP_PORT        e.g. 587
    SMTP_USERNAME    login username for your SMTP account
    SMTP_PASSWORD    password / app password for your SMTP account
    EMAIL_FROM       the From: address
    EMAIL_TO         comma-separated list of recipient addresses

Optional:
    CSV_FOLDER       folder of sales CSVs (default: ./sample_data)
    OUTPUT_PATH      where to write the .xlsx (default: ./monthly_report.xlsx)
    EMAIL_SUBJECT    subject line (default: "Weekly Sales Report - <date>")
"""

#from __future__ import annotations

import argparse
import mimetypes
import os
import smtplib
from datetime import date
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent/".env"
load_dotenv(ENV_PATH)

REQUIRED_ENV_VARS = [
    "SMTP_HOST",
    "SMTP_PORT",
    "SMTP_USERNAME",
    "SMTP_PASSWORD",
    "EMAIL_FROM",
    "EMAIL_TO",
]


def load_config(env_path: Path) -> dict[str, str]:
    """Load and validate configuration from environment / .env file."""
    load_dotenv(dotenv_path=env_path if env_path.exists() else None)

    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            f"{', '.join(missing)}\n"
            f"Set them in {env_path} (see .env.example) or export them directly."
        )

    return {
        "smtp_host": os.environ["SMTP_HOST"],
        "smtp_port": int(os.environ["SMTP_PORT"]),
        "smtp_username": os.environ["SMTP_USERNAME"],
        "smtp_password": os.environ["SMTP_PASSWORD"],
        "email_from": os.environ["EMAIL_FROM"],
        "email_to": [addr.strip() for addr in os.environ["EMAIL_TO"].split(",") if addr.strip()],
        "csv_folder": Path(os.environ.get("CSV_FOLDER", "sample_data")),
        "output_path": Path(os.environ.get("OUTPUT_PATH", "monthly_report.xlsx")),
        "subject": os.environ.get("EMAIL_SUBJECT", f"Weekly Sales Report - {date.today():%Y-%m-%d}"),
    }


def build_message(config: dict, attachments: list[Path], html_body: str) -> EmailMessage:
    """Assemble the EmailMessage with HTML body and .xlsx attachment."""
    msg = EmailMessage()
    msg["Subject"] = config["subject"]
    msg["From"] = config["email_from"]
    msg["To"] = ", ".join(config["email_to"])
    msg.set_content("This report requires an HTML-capable email client to view the summary.")
    msg.add_alternative(html_body, subtype="html")
    for path in attachments:
        mime_type, _ = mimetypes.guess_type(path.name)
        maintype, subtype = (mime_type or "application/octet-stream").split("/",1)
        with path.open("rb") as f:
            msg.add_attachment(
                f.read(),
                maintype=maintype,
                subtype=subtype,
                filename=path.name,
            )
    return msg


def send_message(config: dict, msg: EmailMessage) -> None:
    """Send msg over SMTP with STARTTLS."""
    with smtplib.SMTP(config["smtp_host"], config["smtp_port"]) as server:
        server.starttls()
        server.login(config["smtp_username"], config["smtp_password"])
        server.send_message(msg)

def send_email(
        *,
        subject:str,
        html_body:str,
        attachments:list[Path] | None = None,
        to_addr:str | None = None,
)->None:
    config = load_config(ENV_PATH)
    config["subject"] = subject
    if to_addr:
        config["email_to"] = [to_addr]
    msg = build_message(config,list(attachments or []),html_body)
    send_message(config,msg)    

def main()->None:
    parser = argparse.ArgumentParser(
        description="Reusable email sender. Run --selftest to email yourself."
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="send a test email"
    )
    args = parser.parse_args()

    if not args.selftest:
        print("Nothing sent , run 'python emailer.py --selftest to yourself a test")
        return
    try:
        send_email(
            subject="emailer.py selftest",
            html_body="<p>It works</p>"
        ) 
    except RuntimeError as exc:
        raise SystemExit(str(exc))    
    print(f"seft test set to {os.environ.get('EMAIL_TO')}. Check your email")

if __name__ =="__main__":
    main()    



