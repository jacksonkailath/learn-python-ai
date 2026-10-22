from pathlib import Path
import os
#import os loads Python's built-in operating system interface module. 
# In this script it's used for exactly one thing: reading environment variables.
import smtplib
#loads Python's built-in SMTP client module — the thing that actually talks to a mail server and sends your email.
#SMTP is: Simple Mail Transfer Protocol — the standard protocol for sending email across the internet.
#When you hit "send" in Gmail, something SMTP-like happens behind the scenes. smtplib lets your Python script speak that protocol directly.
import sys
#import sys loads Python's interpreter/system module. 
#"Interpreter" = the Python program itself — the thing that runs when you type python. It reads your .py file and executes it.
#sys is the module that lets your script talk to and about that running interpreter.
# In this script it's used for exactly one thing: printing error messages to the right output stream.
#It's good hygiene. Success messages → stdout. Failure messages (bad password, unreachable server) → stderr.
from email.message import EmailMessage
#This imports the EmailMessage class — the modern tool for building an email — from Python's built-in email package.
#email is a package (a folder of modules), message is a module inside it, and EmailMessage is a class inside that module.
'''
message = EmailMessage()                          # create an empty message
message["Subject"] = "Hello from Python"       # set headers like dict keys
message["From"] = from_addr
message["To"] = to_addr
message.set_content("This plain-text email...")   # set the body

#Then the finished object is handed to smtplib for delivery:
server.send_message(message)
'''

from dotenv import load_dotenv
#dotenv is the package, load_dotenv is a function inside it.

ENV_PATH = Path(__file__).resolve().parent.parent / "project" / ".env"
load_dotenv(ENV_PATH)
#1.Opens the .env file at the given path (or searches current/parent folders if no path given)
#2.Parses each KEY=value line
#3.Inserts each pair into os.environ for this process only
#4.Returns True if it found and loaded a file, False if not

# The environment variables this script needs. Keeping the names in one place
# makes the "what's missing?" check below trivial to read.
REQUIRED_VARS = (
    "SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD",
    "EMAIL_FROM", "EMAIL_TO",
)
'''
"SMTP_HOST" - the mail server's address, e.g. smtp.gmail.com for gmail . Every provider runs its own server

"SMTP_PORT" - the network port on that server, typically 587 for STARTTLS. 
A server can listen on multiple ports with different encryption styles
What a port is, first. One server machine (smtp.gmail.com) runs many services and many simultaneous conversations. 
A port is a numbered "door" (0–65535) so the network knows which service you want. 
The host gets you to the building; the port gets you to the right door.

Port 587 — the modern standard (what this script expects). Called the submission port. 
The connection starts unencrypted, then the client immediately says STARTTLS and the same connection upgrades to encrypted before any login or message is sent. 
This matches the script exactly:
587 = connect then upgrade;
The script's starttls() call assumes 587-style, so the port must match.
encrypt means : scramble the data so that anyone watching the network traffic sees gibberish instead of your actual content.
When your script talks to smtp.gmail.com, hops through your WiFi router, your ISP, and a dozen intermediate machines on the internet. 
Without encryption, every one of those hops can read the raw bytes passing through — and those bytes would include your username and App Password, in readable text and the full email content

What encryption does mechanically. Before sending, your machine and the server agree on a secret key (via a handshake, using math that lets them agree on the key). After that:
Your side: readable data → scrambled with the key → sent
Server side: received → unscrambled with the key → readable again

The technology's name is TLS (Transport Layer Security) 
— the same thing that puts the padlock 🔒 in your browser and 
the "s" in https. Email just reuses it.

"SMTP_USERNAME" - your account on that server, your full email address.Mail servers don't relay for anonymous strangers (that's how spam happens), so you must log in.
"SMTP_PASSWORD" - the credential for that login. For Gmail, specifically a 16-character App Password, because Google blocks normal passwords for scripts.
"EMAIL_FROM" - what goes in the message's From:
"EMAIL_TO" - the recipient's address
'''



def send_plain_email() -> None:
    """Build and send a one-line plain-text email from the current user to self."""
    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"]) #environment variables are always strings
    user = os.environ["SMTP_USERNAME"]
    password = os.environ["SMTP_PASSWORD"]
    from_addr = os.environ["EMAIL_FROM"]
    to_addr = os.environ["EMAIL_TO"]

    # EmailMessage is the modern, batteries-included way to build a message.
    # It handles headers and encoding so you don't hand-assemble raw text.
    message = EmailMessage() #creates a new, empty email message object
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
        #this pattern was previously used to open a file
        #smtplib.SMTP(host, port) is calling a class to create an object.
        #it opens a live network connection to the mail server right then. 
        # The object you get back represents that open connection.
        #as server — names the object so the indented block can use it
        #with ... : — wraps the whole thing in the cleanup guarantee.
        #the guarantee is that the cleanup code(written inside smtplib) will always run - the connection gets closed.
        server.starttls()          # encrypt the channel,The connection to port 587 opened unencrypted. This call performs the upgrade;client says STARTTLS, both sides do the TLS handshake (agree on a secret key), and the same connection switches to encrypted mode. Everything after this line travels scrambled.
        server.login(user, password) #could raise SMTPAuthenticationError - without with - > that exception would jump straight out to the except handler in main(), skipping any server.quit()
        server.send_message(message) #the EmailMessage object we built gets serialized into raw email format and transmitted.

    print(f"Sent a plain-text email to {to_addr}.")


def main() -> None:
    missing = [name for name in REQUIRED_VARS if not os.environ.get(name)]
    #if not os.environ.get(name)
    #os.environ["SMTP_HOST"] → crashes with KeyError if not set
    #os.environ.get("SMTP_HOST") → returns None if not set, no crash
    if missing:
        print("Email not sent — configuration missing.")
        print(f"Set these environment variables first: {', '.join(missing)}")
        #prints all elements in the list called missing comma separated 
        print(
            "\nThe easy way (used by the rest of this section): copy "
            "project/.env.example to project/.env, fill it in, and load it with "
            "python-dotenv (see 03_secrets_with_dotenv.py)."
        )
        print(
            "Reminder: SMTP_PASSWORD is a Gmail *App Password*, not your normal "
            "password."
        )
        return  # graceful exit — no traceback, no attempted connection

    try:
        send_plain_email()
    except smtplib.SMTPAuthenticationError:
        #you reached the server fine, but it rejected your login. Network is good, host/port are good — the problem is credentials.
        print(
            "Login was rejected. For Gmail this almost always means you used "
            "your normal password instead of a 16-character App Password, or "
            "2-Step Verification isn't enabled on the account.",
            file=sys.stderr,
        )
    except OSError as error:
        #you never reached the server at all. No WiFi, wrong hostname, firewall, DNS failure. Credentials never even came up. So the message talks about the mail server being unreachable.
        # Network unreachable, wrong host/port, DNS failure, etc.
        #OSError :Python's built-in exception for "the operating system couldn't do what you asked."
        print(f"Could not reach the mail server: {error}", file=sys.stderr)


if __name__ == "__main__":
    main()
