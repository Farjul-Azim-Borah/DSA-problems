import os
import re
import json
import subprocess
import time
from pathlib import Path

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIG
# ============================================================

load_dotenv()

USERNAME = os.getenv("LEETCODE_USERNAME")
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRF_TOKEN = os.getenv("LEETCODE_CSRF")

GITHUB_REPO_DIR = os.getenv(
    "GITHUB_REPO_DIR",
    str(Path(__file__).resolve().parent)
)

# Number of recent accepted submissions to check.
# 100 is safer than the old 20.
RECENT_LIMIT = int(os.getenv("RECENT_LIMIT", "100"))

# Number of retries for temporary LeetCode failures.
MAX_RETRIES = 3

GRAPHQL_URL = "https://leetcode.com/graphql/"


# ============================================================
# CHECK ENVIRONMENT
# ============================================================

if not USERNAME:
    raise RuntimeError(
        "LEETCODE_USERNAME is missing."
    )

if not LEETCODE_SESSION:
    raise RuntimeError(
        "LEETCODE_SESSION is missing."
    )


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "Content-Type": "application/json",

    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36",

    "Referer": "https://leetcode.com/",

    "Origin": "https://leetcode.com",

    "Accept": "application/json, text/plain, */*",

    "Accept-Encoding": "gzip, deflate",
})


# LeetCode login cookie
session.cookies.set(
    "LEETCODE_SESSION",
    LEETCODE_SESSION,
    domain=".leetcode.com"
)


# CSRF cookie/header
if CSRF_TOKEN:
    session.cookies.set(
        "csrftoken",
        CSRF_TOKEN,
        domain=".leetcode.com"
    )

    session.headers["x-csrftoken"] = CSRF_TOKEN


# ============================================================
# GRAPHQL REQUEST
# ============================================================

def graphql(query, variables=None, operation_name=None):

    payload = {
        "query": query,
        "variables": variables or {}
    }

    if operation_name:
        payload["operationName"] = operation_name

    for attempt in range(1, MAX_RETRIES + 1):

        try:

            response = session.post(
                GRAPHQL_URL,
                json=payload,
                timeout=30
            )

        except requests.RequestException as e:

            print(
                f"Network error "
                f"(attempt {attempt}/{MAX_RETRIES}):"
            )
            print(e)

            if attempt < MAX_RETRIES:
                time.sleep(3)
                continue

            return None

        print(
            f"LeetCode HTTP status: "
            f"{response.status_code}"
        )

        # Temporary server/rate-limit error
        if response.status_code in (429, 500, 502, 503, 504):

            if attempt < MAX_RETRIES:
                print("Temporary error. Retrying...")
                time.sleep(3 * attempt)
                continue

            print("LeetCode request failed after retries.")
            return None

        # Authentication / Cloudflare / invalid session
        if response.status_code != 200:

            print()
            print("LeetCode request failed.")
            print(
                "HTTP status:",
                response.status_code
            )

            print()
            print(
                "Your LEETCODE_SESSION may have expired."
            )

            print(
                response.text[:1000]
            )

            return None

        try:

            result = response.json()

        except Exception:

            print(
                "LeetCode returned invalid JSON."
            )

            print(
                response.text[:1000]
            )

            return None

        if "errors" in result:

            print()
            print("GraphQL errors:")

            print(
                json.dumps(
                    result["errors"],
                    indent=2
                )
            )

            return None

        return result.get("data")

    return None


# ============================================================
# GET RECENT ACCEPTED SUBMISSIONS
# ============================================================

def get_recent_submissions():

    query = """
    query recentAcSubmissionList(
        $username: String!,
        $limit: Int!
    ) {

        recentAcSubmissionList(
            username: $username,
            limit: $limit
        ) {

            id
            title
            titleSlug
            timestamp
        }
    }
    """

    variables = {
        "username": USERNAME,
        "limit": RECENT_LIMIT
    }

    data = graphql(
        query,
        variables,
        "recentAcSubmissionList"
    )

    if not data:
        return []

    submissions = (
        data.get("recentAcSubmissionList")
        or []
    )

    if not isinstance(submissions, list):
        print(
            "Unexpected response from "
            "recentAcSubmissionList."
        )
        return []

    return submissions


# ============================================================
# GET SUBMISSION DETAILS
# ============================================================

def get_submission_details(submission_id):

    query = """
    query submissionDetails(
        $submissionId: Int!
    ) {

        submissionDetails(
            submissionId: $submissionId
        ) {

            id
            code
            statusDisplay

            runtime
            memory
            timestamp

            lang {
                name
                verboseName
            }

            question {
                questionId
                questionFrontendId
                title
                titleSlug
                difficulty
            }
        }
    }
    """

    variables = {
        "submissionId": int(submission_id)
    }

    data = graphql(
        query,
        variables,
        "submissionDetails"
    )

    if not data:
        return None

    details = (
        data.get("submissionDetails")
    )

    if not details:
        print(
            "submissionDetails returned null."
        )
        return None

    return details


# ============================================================
# CLEAN FILE/FOLDER NAME
# ============================================================

def clean_name(name):

    if not name:
        return "unknown"

    name = name.lower()

    name = re.sub(
        r"[^a-z0-9]+",
        "-",
        name
    )

    return name.strip("-")


# ============================================================
# LANGUAGE → EXTENSION
# ============================================================

def get_extension(language):

    language = (
        language or "unknown"
    ).lower().strip()

    mapping = {

        "cpp": "cpp",
        "c++": "cpp",

        "c": "c",

        "java": "java",

        "python": "py",
        "python3": "py",

        "javascript": "js",

        "typescript": "ts",

        "go": "go",

        "rust": "rs",

        "kotlin": "kt",

        "swift": "swift",

        "csharp": "cs",

        "ruby": "rb",

        "php": "php",

        "scala": "scala",

        "dart": "dart",

        "mysql": "sql",

        "mssql": "sql",

        "postgresql": "sql"
    }

    return mapping.get(
        language,
        "txt"
    )


# ============================================================
# README
# ============================================================

def create_readme(
    folder,
    number,
    title,
    difficulty,
    language,
    slug,
    submission_id,
    timestamp
):

    content = f"""# {number}. {title}

- Difficulty: {difficulty}
- Language: {language}
- Submission ID: {submission_id}
- Submission timestamp: {timestamp}

## LeetCode

https://leetcode.com/problems/{slug}/

## Submission

https://leetcode.com/problems/{slug}/submissions/{submission_id}/
"""

    readme = folder / "README.md"

    readme.write_text(
        content,
        encoding="utf-8"
    )


# ============================================================
# PROCESS ONE SUBMISSION
# ============================================================

def process_submission(submission):

    submission_id = submission.get("id")

    if not submission_id:
        print("Submission ID missing.")
        return False

    print()
    print("=" * 70)
    print(
        "Submission ID:",
        submission_id
    )
    print(
        "Problem:",
        submission.get("title")
    )
    print(
        "Slug:",
        submission.get("titleSlug")
    )
    print("=" * 70)

    # --------------------------------------------------------
    # GET ACTUAL SUBMISSION CODE
    # --------------------------------------------------------

    print("Getting submission details...")

    details = get_submission_details(
        submission_id
    )

    if not details:

        print(
            "Could not get submission details."
        )

        return False

    # --------------------------------------------------------
    # VERIFY ACCEPTED
    # --------------------------------------------------------

    status = details.get(
        "statusDisplay"
    )

    print(
        "Status:",
        status
    )

    if status != "Accepted":

        print(
            "Submission is not accepted."
        )

        return False

    # --------------------------------------------------------
    # CODE
    # --------------------------------------------------------

    code = details.get("code")

    if not code:

        print(
            "Submission code is empty."
        )

        return False

    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    lang_info = (
        details.get("lang")
        or {}
    )

    language = (
        lang_info.get("name")
        or submission.get("lang")
        or "unknown"
    )

    print(
        "Language:",
        language
    )

    # --------------------------------------------------------
    # QUESTION
    # --------------------------------------------------------

    question = (
        details.get("question")
        or {}
    )

    slug = (
        question.get("titleSlug")
        or submission.get("titleSlug")
    )

    title = (
        question.get("title")
        or submission.get("title")
        or "Unknown Problem"
    )

    number = (
        question.get(
            "questionFrontendId"
        )
        or question.get(
            "questionId"
        )
    )

    difficulty = (
        question.get("difficulty")
        or "Unknown"
    )

    if not slug:
        print("Problem slug missing.")
        return False

    if not number:
        print("Problem number missing.")
        return False

    # --------------------------------------------------------
    # REPOSITORY
    # --------------------------------------------------------

    repo = Path(
        GITHUB_REPO_DIR
    )

    if not repo.exists():

        print()
        print(
            "Repository does not exist:"
        )
        print(repo)

        return False

    # --------------------------------------------------------
    # LEETCODE FOLDER
    # --------------------------------------------------------

    leetcode_folder = (
        repo / "leetcode"
    )

    leetcode_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # PROBLEM FOLDER
    # --------------------------------------------------------

    try:

        folder_name = (
            f"{int(number):04d}-"
            f"{clean_name(slug)}"
        )

    except Exception:

        folder_name = (
            f"{number}-"
            f"{clean_name(slug)}"
        )

    problem_folder = (
        leetcode_folder /
        folder_name
    )

    problem_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    # --------------------------------------------------------
    # SOLUTION FILE
    # --------------------------------------------------------

    extension = get_extension(
        language
    )

    solution_file = (
        problem_folder /
        f"solution.{extension}"
    )

    # --------------------------------------------------------
    # WRITE CODE
    # --------------------------------------------------------

    old_code = None

    if solution_file.exists():

        try:

            old_code = solution_file.read_text(
                encoding="utf-8"
            )

        except Exception:
            pass

    if old_code == code:

        print(
            "Solution already up to date."
        )

    else:

        solution_file.write_text(
            code,
            encoding="utf-8"
        )

        print()
        print(
            "SUCCESS! Solution saved:"
        )

        print(solution_file)

    # --------------------------------------------------------
    # README
    # --------------------------------------------------------

    timestamp = details.get(
        "timestamp"
    ) or submission.get(
        "timestamp"
    )

    create_readme(
        problem_folder,
        number,
        title,
        difficulty,
        language,
        slug,
        submission_id,
        timestamp
    )

    print(
        "README updated."
    )

    return True


# ============================================================
# GIT
# ============================================================

def git_push():

    repo = Path(
        GITHUB_REPO_DIR
    )

    print()
    print("=" * 70)
    print("                 GITHUB PUSH")
    print("=" * 70)

    # --------------------------------------------------------
    # CHECK STATUS
    # --------------------------------------------------------

    result = subprocess.run(
        [
            "git",
            "status",
            "--porcelain"
        ],
        cwd=repo,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print(
            "git status failed."
        )

        print(result.stderr)

        return False

    if not result.stdout.strip():

        print()
        print(
            "Nothing new to push."
        )

        return True

    print()
    print("Changes:")
    print(result.stdout)

    # --------------------------------------------------------
    # ADD
    # --------------------------------------------------------

    print("Adding files...")

    subprocess.run(
        [
            "git",
            "add",
            "."
        ],
        cwd=repo,
        check=True
    )

    # --------------------------------------------------------
    # CHECK AGAIN
    # --------------------------------------------------------

    result = subprocess.run(
        [
            "git",
            "diff",
            "--cached",
            "--quiet"
        ],
        cwd=repo
    )

    if result.returncode == 0:

        print(
            "Nothing staged to commit."
        )

        return True

    # --------------------------------------------------------
    # COMMIT
    # --------------------------------------------------------

    print(
        "Creating commit..."
    )

    subprocess.run(
        [
            "git",
            "config",
            "user.name",
            "github-actions[bot]"
        ],
        cwd=repo,
        check=True
    )

    subprocess.run(
        [
            "git",
            "config",
            "user.email",
            "41898282+github-actions[bot]@users.noreply.github.com"
        ],
        cwd=repo,
        check=True
    )

    subprocess.run(
        [
            "git",
            "commit",
            "-m",
            "Sync accepted LeetCode solutions"
        ],
        cwd=repo,
        check=True
    )

    # --------------------------------------------------------
    # PUSH
    # --------------------------------------------------------

    print(
        "Pushing to GitHub..."
    )

    result = subprocess.run(
        [
            "git",
            "push"
        ],
        cwd=repo,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:

        print()
        print(
            "Git push failed."
        )

        print(result.stdout)
        print(result.stderr)

        return False

    print()
    print(
        "Successfully pushed to GitHub! ✅"
    )

    return True


# ============================================================
# MAIN SYNC
# ============================================================

def sync():

    print()
    print("=" * 70)
    print("              LEETCODE → GITHUB SYNC")
    print("=" * 70)

    print()
    print(
        "Username:",
        USERNAME
    )

    print(
        "Repository:",
        GITHUB_REPO_DIR
    )

    print(
        "Checking last",
        RECENT_LIMIT,
        "accepted submissions..."
    )

    # --------------------------------------------------------
    # GET RECENT ACCEPTED SUBMISSIONS
    # --------------------------------------------------------

    submissions = (
        get_recent_submissions()
    )

    if not submissions:

        print()
        print(
            "No recent accepted submissions found."
        )

        return

    print()
    print(
        "Found",
        len(submissions),
        "recent accepted submissions."
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATE PROBLEMS
    #
    # recentAcSubmissionList is already ordered newest first.
    # Therefore, if the same problem appears multiple times,
    # we process the newest accepted submission.
    # --------------------------------------------------------

    unique = {}

    for submission in submissions:

        slug = submission.get(
            "titleSlug"
        )

        if not slug:
            continue

        if slug not in unique:

            unique[slug] = submission

    print(
        "Unique problems:",
        len(unique)
    )

    # --------------------------------------------------------
    # PROCESS
    # --------------------------------------------------------

    successful = 0
    failed = 0

    for submission in unique.values():

        try:

            if process_submission(
                submission
            ):

                successful += 1

            else:

                failed += 1

        except Exception as e:

            print()
            print(
                "ERROR while processing:"
            )

            print(
                submission.get(
                    "title"
                )
            )

            print(e)

            failed += 1

    # --------------------------------------------------------
    # PUSH
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("SYNC SUMMARY")
    print("=" * 70)

    print(
        "Successful:",
        successful
    )

    print(
        "Failed:",
        failed
    )

    print()

    # Even if one submission failed, still push
    # successful submissions.
    push_success = git_push()

    if not push_success:

        raise RuntimeError(
            "Git push failed."
        )

    print()
    print("=" * 70)
    print("SYNC COMPLETE ✅")
    print("=" * 70)


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    try:

        sync()

    except KeyboardInterrupt:

        print()
        print(
            "Stopped."
        )

    except Exception as e:

        print()
        print("=" * 70)
        print("FATAL ERROR")
        print("=" * 70)

        print(e)

        raise