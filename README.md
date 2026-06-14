# getjticket

> A Jira ticket information fetcher tool via terminal. 

`getjticket` allows you to fetch and display JIRA ticket information directly from your terminal. This tool uses the REST API of JIRA to interact with your JIRA server, and requires environment variables for configuration.
---

## Features
  
- **Fetch JIRA ticket information** directly from the terminal
- **Display time tracking information** for JIRA issues
- **Display issue description** for JIRA issues
- **Environment variable configuration** for JIRA server, username, and password
- **Works as** a global CLI command after installation

---

## Installation

```bash
pip install getjticket
```

Or install from source:

```bash
git clone https://github.com/JuanJoseSolorzano/getjticket_project.git 
cd getjticket_project
pip install .
```
## Required Environment Variables
- `JIRA_SERVER`: The URL of your JIRA server (e.g., `yourdomain.atlassian.net`).
- `JIRA_USERNAME`: Your JIRA username (usually your email address).
- `JIRA_PASSWORD`: Your JIRA API token or password.
---

## Usage

```bash

positional arguments:
  issue_id              The ID of the JIRA issue (e.g., 6552 for SETV-6552).

optional arguments:
  -h, --help    show this help message and exit

  -t TIME,        --time         Shows the time tracking information for the JIRA issue in a pretty format [optional].
  -d DESCRIPTION, --description  Shows the description of the JIRA issue in a pretty format [optional].

  NOTE: If no optional arguments are provided, the tool will display the issue summary and key by default.
```

### Examples

```bash
getjticket 6552 -t "Time tracking information for the JIRA issue."
getjticket 6552 -d "Description of the JIRA issue."
```
---

## License

See [LICENSE](LICENSE) for details.

---

## Author

**Juan Jose Solorzano Carrillo** — juanjose.solorzano.c@gmail.com
