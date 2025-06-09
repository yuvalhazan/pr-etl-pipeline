# PR - ETL - PIPELINE 
This script communicates with GitHub API using a Personal Access Token (PAT),
which should be saved in your environment as GITHUB_TOKEN.

What it does:
- Connects to a repository using .env file(details below).
- Pulls all merged PRs
- For each PR, it grabs:
  1. Basic details: number, title, author, merged date
  2. All the PR reviews.
  3. The latest check-suites that ran on the PR
- All of that is saved into a single JSON file
- Reads the raw JSON file
- For each PR checks:
    - CR_Passed: Did at least one reviewer approved this PR?
    - CHECKS_PASSED: did the latest check suites were completed successfully?
- writes a CSV report including these columns:
    PR_number, PR_title, Author, Merge date, CR_Passed, CHECKS_PASSED

### Please Note: A default.env file is provided for your convenience.
Copy it to a file named .env in the project root and then edit the variables inside,
(GITHUB_TOKEN, GITHUB_OWNER, GITHUB_REPO) with your own values.

### Use Docker Compose to build and run the application:
docker-compose up --build
