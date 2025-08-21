import os
import re
from jira import JIRA

def get_jira_client():
    """
    Initializes and returns a Jira client using credentials from environment variables.
    Requires: JIRA_SERVER, JIRA_USER_EMAIL, JIRA_API_TOKEN.
    """
    server = os.getenv("JIRA_SERVER")
    email = os.getenv("JIRA_USER_EMAIL")
    token = os.getenv("JIRA_API_TOKEN")

    if not all([server, email, token]):
        print("\n[Jira] Warning: Jira environment variables are not fully set. Skipping Jira integration.")
        return None

    try:
        print("[Jira] Authenticating with Jira...")
        jira_client = JIRA(server=server, basic_auth=(email, token))
        # Verify authentication by getting server info
        jira_client.server_info()
        print("[Jira] Authentication successful.")
        return jira_client
    except Exception as e:
        print(f"[Jira] Error connecting to Jira: {e}")
        return None

def extract_jira_key_from_text(text: str) -> str | None:
    """
    Extracts the first Jira ticket key (e.g., 'PROJ-123') found in a string.
    """
    if not text:
        return None
    # This regex looks for a pattern of 2 or more uppercase letters, a hyphen, and one or more digits.
    match = re.search(r'\b([A-Z]{2,}-\d+)\b', text.upper())
    return match.group(1) if match else None

def get_jira_ticket_details(client, ticket_key: str) -> dict | None:
    """
    Fetches key details for a specific Jira ticket.
    """
    if not client or not ticket_key:
        return None

    try:
        print(f"[Jira] Fetching details for ticket: {ticket_key}")
        issue = client.issue(ticket_key)
        return {
            'key': issue.key,
            'summary': issue.fields.summary,
            'status': issue.fields.status.name,
            'assignee': issue.fields.assignee.displayName if issue.fields.assignee else 'Unassigned',
            'url': issue.permalink(),
        }
    except Exception as e:
        print(f"[Jira] Error fetching Jira ticket {ticket_key}: {e}")
        return None
