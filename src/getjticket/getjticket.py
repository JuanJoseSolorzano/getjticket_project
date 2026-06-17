import requests
import os
import argparse
import re
import sys
sys.stdout.reconfigure(encoding="utf-8")#type: ignore
sys.stderr.reconfigure(encoding="utf-8")#type: ignore
from colored import Fore,Style
from requests.auth import HTTPBasicAuth
from pygments import highlight
from pygments.lexers import TextLexer, get_lexer_by_name
from pygments.formatters import TerminalTrueColorFormatter
from rich.console import Console
from datetime import date

JIRA_SERVER = os.getenv("JIRA_SERVER","")
USERNAME = os.getenv("JIRA_USERNAME","")
PASSWORD = os.getenv("JIRA_PASSWORD","")
TODAY = date.today().strftime("%d/%m/%Y")
ISSUE_KEY = "SETV-%s"
URL = "https://{0}/rest/api/2/issue/{1}/comment"
HEADERS = {"Accept": "application/json","Content-Type": "application/json"}
PAYLOAD = {"body": ""}
SEPARATOR = '─' * 100
SEPARATOR_2 = '═' * 100
PINK =   Fore.rgb("100%", "0%", "60%")
GRAY = Fore.rgb("50%", "50%", "50%")
PARAMS = {"fields": "summary,description,timespent,timeestimate,timetracking,worklog,comment"}
CONSOLE = Console()


def parse_args():
    parser = argparse.ArgumentParser(description="Add a comment to a JIRA issue.")
    parser.add_argument("issue_id", type=int, help="The ID of the JIRA issue (e.g., 6552 for SETV-6552).")
    parser.add_argument("-d", "--description", action="store_true", default=False, help="Show detailed information about the issue.")
    parser.add_argument("-t", "--time", action="store_true", default=False, help="Show time tracking information for the issue.")
    parser.add_argument("-c", "--comment", action="store_true", default=False, help="Get the comment of the issue.")
    return parser.parse_args()

def markup2markdown(text):
    # Remove separators
    text = re.sub(r'^[-=]{4,}\s*$', '', text, flags=re.MULTILINE)
    # Headings: h1. text -> # text
    for i in range(1, 7):
        text = re.sub(rf'^h{i}\.\s*(.*)$', lambda m: f"{'#' * i} {m.group(1)}", text, flags=re.MULTILINE)
    # Bullet points
    text = re.sub(r'^\s*\*\s+', '- ', text, flags=re.MULTILINE)
    # Blockquotes
    text = re.sub(r'^\s*>\s?', '> ', text, flags=re.MULTILINE)
    # Bold: *text* -> **text**
    text = re.sub(r'\*(.*?)\*', r'**\1**', text)
    # Italic: _text_ -> _text_
    text = re.sub(r'_(.*?)_', r'_\1_', text)
    # Inline code: {{code}} -> `code`
    text = re.sub(r'\{\{(.*?)\}\}', r'`\1`', text)
    # Clean extra blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def connect_jira(issue_id:str) -> requests.Response:
    url = f"https://{JIRA_SERVER}/rest/api/2/issue/{ISSUE_KEY % issue_id}"
    return requests.get(
        url,
        params=PARAMS,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers={"Accept": "application/json"}
    )

def get_time_tracking_info(fields, linK_to_issue, issue_id) -> None:
    worklogs = fields["worklog"]["worklogs"]
    estimated = fields["timetracking"]["originalEstimate"]
    remaining = fields["timetracking"]["remainingEstimate"]
    try:
        time_spent = fields["timetracking"]["timeSpent"]
    except KeyError:
        time_spent = "0s"
    print(SEPARATOR)
    print(f"Issue ID: {ISSUE_KEY % issue_id}")
    print(f"Summary: {fields['summary']}")
    print(f"Link to Issue: {linK_to_issue}")
    print(" ")
    print(f"{'':<25}[- TIME TRACKING INFORMATION -]")
    print(" ")
    print(f"{'Original Estimate:':<20} {estimated}")
    print(f"{'Remaining Time:':<20} {remaining}")
    print(f"{'Time Spent:':<20} {time_spent}")

    print(SEPARATOR_2)
    print(f"{'Author':<25} {'Started':<20} {'Time Spent':<12} Comment")
    print(SEPARATOR)

    for worklogged in worklogs:
        author = worklogged["author"]["displayName"]
        time_spent = worklogged["timeSpent"]
        started = worklogged["started"].replace("T", " ").replace(".000+0000", "")
        comment = worklogged.get("comment", "")
        comment = comment[:50] + "..." if len(comment) > 50 else comment
        print(f"{author:<25} {started:<20} {time_spent:<12} {comment}")
    print(SEPARATOR_2)

def get_description(fields, linK_to_issue, issue_id) -> None:
    description = fields.get("description", "No description provided.")
    cleaned = markup2markdown(description)
    lexer = get_lexer_by_name("markdown", stripall=True)
    colored_output = highlight(cleaned, lexer, TerminalTrueColorFormatter()).splitlines()
    print(SEPARATOR_2)
    print(f"  {GRAY}{ISSUE_KEY % issue_id} - {fields['summary']}")
    print(f"  [{linK_to_issue}]{Style.reset}")
    print(f"{SEPARATOR}")
    for line_number, line in enumerate(colored_output, start=1):
        print(f"{GRAY}{line_number:<2}│ {Style.reset}{line}")
    print(SEPARATOR_2)

def get_comments(fields, linK_to_issue, issue_id) -> None:
    comments = fields["comment"]["comments"]
    print(SEPARATOR_2)
    print(f"  {GRAY}{ISSUE_KEY % issue_id} - {fields['summary']}")
    print(f"  [{linK_to_issue}]{Style.reset}")
    print(f"{SEPARATOR}")
    for comment in comments:
        author = comment["author"]["displayName"]
        created = comment["created"].replace("T", " ").replace(".000+0000", "")
        body = markup2markdown(comment["body"])
        lexer = get_lexer_by_name("markdown", stripall=True)
        colored_output = highlight(body, lexer, TerminalTrueColorFormatter()).splitlines()
        print(f"{PINK}{author} commented on {created}:{Style.reset}")
        for line_number, line in enumerate(colored_output, start=1):
            line_info = f"{GRAY}{line_number:<2}│ {Style.reset}{line}"
            print(line_info)
        print(SEPARATOR)
    print(SEPARATOR_2)

def run()->None:
    args = parse_args()
    issue_id = args.issue_id
    linK_to_issue = f"https://{JIRA_SERVER}/browse/{ISSUE_KEY % issue_id}"
    response = connect_jira(issue_id).json()
    fields = response["fields"]

    if args.description:
        get_description(fields, linK_to_issue, issue_id)
    elif args.time:
        get_time_tracking_info(fields, linK_to_issue, issue_id)
    elif args.comment:
        get_comments(fields, linK_to_issue, issue_id)
    else:
        get_description(fields, linK_to_issue, issue_id)
        get_time_tracking_info(fields, linK_to_issue, issue_id)

if __name__ == "__main__":
    run()    
        
