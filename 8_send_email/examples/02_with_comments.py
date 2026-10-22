"""Example 2 — an HTML email body with a file attachment.

A plain-text email (Example 1) is fine for a one-liner. A *report* email wants
two upgrades:

  1. an **HTML body**, so the message can have headings, a table, bold numbers —
     anything a browser can render;
  2. an **attachment**, so the actual .xlsx / .pdf / .png rides along.

Both come from the same idea: an email is a little tree of "parts". A message
with an HTML body *and* a file is a `multipart/mixed` message — one part is the
HTML you see, the other is the file you download.

This example writes a tiny throwaway attachment next to itself, attaches it,
and sends. Like every script in this section it is env-guarded: with no SMTP
config it prints what to set and exits without sending.

Run it:
    python 02_html_and_attachments.py
"""

import mimetypes
#mimetypes is a standard library module that maps file extensions → MIME types.
#A MIME type is a label like application/pdf, image/png, or text/plain that tells software (email clients, browsers) what kind of data a file contains — because the receiving end can't rely on file extensions alone.
#add_attachment() needs the type split into two pieces — maintype="application", subtype="pdf" — so the email client knows how to display or handle the attachment
import os
import smtplib
import sys
from email.message import EmailMessage
from pathlib import Path

from dotenv import load_dotenv

ENV_PATH = Path(__file__).resolve().parent.parent / "project" / ".env"
load_dotenv(ENV_PATH)

REQUIRED_VARS = (
    "SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD",
    "EMAIL_FROM", "EMAIL_TO",
)

# A small HTML body. Email clients support a *subset* of HTML/CSS, so real
# report emails lean on simple, inline styling — no external stylesheets.
HTML_BODY = """\
<html>
  <body style="font-family: Arial, sans-serif; color: #222;">
    <h2 style="color: #305496;">Weekly Sales Report</h2>
    <p>Here is this week's summary. The full workbook is attached.</p>
    <table style="border-collapse: collapse;">
      <tr style="background: #305496; color: white;">
        <th style="padding: 6px 12px;">Metric</th>
        <th style="padding: 6px 12px;">Value</th>
      </tr>
      <tr>
        <td style="padding: 6px 12px;">Orders</td>
        <td style="padding: 6px 12px;">1,204</td>
      </tr>
      <tr>
        <td style="padding: 6px 12px;">Revenue</td>
        <td style="padding: 6px 12px;">$482,910.00</td>
      </tr>
    </table>
    <p style="color: #888; font-size: 12px;">Sent automatically by a Python script.</p>
  </body>
</html>
"""


def attach_file(message: EmailMessage, path: Path) -> None:
    """Attach *path* to *message*, guessing a sensible MIME type from its name."""
    # Guess "application/pdf", "image/png", etc. from the extension; fall back
    # to a generic binary type the receiving client can still download.
    mime_type, _ = mimetypes.guess_type(path.name)
    #A MIME type is a label like application/pdf, image/png, or text/plain that tells software (email clients, browsers) what kind of data a file contains — because the receiving end can't rely on file extensions alone.
    #add_attachment() needs the type split into two pieces — maintype="application", subtype="pdf" — so the email client knows how to display or handle the attachment
    #it returns None for unknown extensions
    #so below we say (mime_type or "application/octet-stream") and it takes for None - "application/octet-stream"
    #"application/octet-stream" is the MIME type for "generic binary data — I'm not telling you what this is."
    maintype, subtype = (mime_type or "application/octet-stream").split("/", 1)
    #MIME types are always maintype/subtype
    #The 1 (maxsplit) says "cut only at the first slash,"
    #unpacks into 2 variables

    data = path.read_bytes()
    #read_bytes() opens the file, reads its entire contents as raw bytes, closes the file, and returns the result as a bytes object.
    #we had previously seen read_text() but this would crash for example for pdf, png, xlsx
    message.add_attachment(
        data, maintype=maintype, subtype=subtype, filename=path.name
    )
    #file becomes part of the email


def send_html_with_attachment(attachment: Path) -> None:
    """Send an HTML-bodied email with one file attached, to yourself."""
    user = os.environ["SMTP_USERNAME"]
    from_addr = os.environ["EMAIL_FROM"]
    to_addr = os.environ["EMAIL_TO"]

    message = EmailMessage()
    message["Subject"] = "Weekly Sales Report 📊"
    message["From"] = from_addr
    message["To"] = to_addr

    # set_content() writes a plain-text fallback (for clients that won't render
    # HTML); add_alternative(..., subtype="html") adds the rich version. Good
    # clients show the HTML; ancient ones still show readable text.
    message.set_content(
        "Your email client can't display HTML. This week: 1,204 orders, "
        "$482,910.00 revenue. The full workbook is attached."
    )
    message.add_alternative(HTML_BODY, subtype="html")
    #build a two-version body: a plain-text version and an HTML version of the same message. The receiving client picks whichever it can render.

    attach_file(message, attachment)

    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])
    password = os.environ["SMTP_PASSWORD"]

    print(f"Connecting to {host}:{port} ...")
    with smtplib.SMTP(host, port) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(message)

    print(f"Sent an HTML email with {attachment.name} attached to {to_addr}.")


def main() -> None:
    missing = [name for name in REQUIRED_VARS if not os.environ.get(name)]
    if missing:
        print("Email not sent — configuration missing.")
        print(f"Set these environment variables first: {', '.join(missing)}")
        print(
            "\nCopy project/.env.example to project/.env, fill it in, and see "
            "03_secrets_with_dotenv.py for loading it."
        )
        return

    # Build a tiny attachment to demonstrate with (in the real project this is
    # the .xlsx from Section 7). Written to the scratch dir, cleaned up after.
    sample = Path(__file__).parent / "_sample_attachment.txt"
    sample.write_text(
        "Pretend this is monthly_report.xlsx.\n"
        "The real Monday report attaches the Section 7 workbook here.\n",
        encoding="utf-8",
    )
    try:
        send_html_with_attachment(sample)
    except smtplib.SMTPAuthenticationError:
        print(
            "Login rejected — use a Gmail App Password, not your normal "
            "password.",
            file=sys.stderr,
        )
    except OSError as error:
        print(f"Could not reach the mail server: {error}", file=sys.stderr)
    finally:
        #always runs
        sample.unlink(missing_ok=True)  # tidy up the demo file
        #unlink() is the Path method that deletes a file
        #missing_ok=True: if the file's already gone, that's fine — do nothing, don't raise.


if __name__ == "__main__":
    main()
