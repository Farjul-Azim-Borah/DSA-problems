import os
import re
import json
import subprocess
import requests
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# LOAD CONFIGURATION
# ============================================================

load_dotenv()

USERNAME = os.getenv("LEETCODE_USERNAME")
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRF_TOKEN = os.getenv("LEETCODE_CSRF")

GITHUB_REPO_DIR = os.getenv(
    "GITHUB_REPO_DIR",
    r"C:\Users\farju\OneDrive\Desktop\lc\leetcode-github-sync"
)

GRAPHQL_URL = "https://leetcode.com/graphql/"


if not USERNAME:
    raise Exception("LEETCODE_USERNAME is missing from .env")

if not LEETCODE_SESSION:
    raise Exception("LEETCODE_SESSION is missing from .env")


# ============================================================
# LEETCODE SESSION
# ============================================================

session = requests.Session()

session.headers.update({
    "Content-Type": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "Referer": "https://leetcode.com/",
    "Origin": "https://leetcode.com"
})

session.cookies.update({
    "LEETCODE_SESSION": LEETCODE_SESSION
})

if CSRF_TOKEN:
    session.cookies.update({
        "csrftoken": CSRF_TOKEN
    })

    session.headers.update({
        "x-csrftoken": CSRF_TOKEN
    })


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

    try:

        response = session.post(
            GRAPHQL_URL,
            json=payload,
            timeout=30
        )

    except requests.RequestException as e:

        print("\nNetwork error:")
        print(e)

        return None


    print("HTTP status:", response.status_code)


    if response.status_code != 200:

        print("\nLeetCode returned an HTTP error:")
        print(response.text[:3000])

        return None


    try:

        result = response.json()

    except Exception:

        print("\nLeetCode returned invalid JSON:")
        print(response.text[:3000])

        return None


    if "errors" in result:

        print("\nGraphQL error:")
        print(
            json.dumps(
                result["errors"],
                indent=2
            )
        )

        return None


    return result.get("data")


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
        "limit": 20
    }


    data = graphql(
        query,
        variables,
        "recentAcSubmissionList"
    )


    if not data:
        return []


    submissions = data.get(
        "recentAcSubmissionList"
    )


    if not submissions:
        return []


    return submissions


# ============================================================
# GET SUBMISSION DETAILS
# ============================================================

def get_submission_code(submission_id):

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


    return data.get(
        "submissionDetails"
    )


# ============================================================
# GET QUESTION INFORMATION
# ============================================================

def get_question_info(slug):

    query = """
    query questionTitle(
        $titleSlug: String!
    ) {

        question(
            titleSlug: $titleSlug
        ) {

            questionId

            questionFrontendId

            title

            titleSlug

            difficulty

        }
    }
    """


    variables = {
        "titleSlug": slug
    }


    data = graphql(
        query,
        variables,
        "questionTitle"
    )


    if not data:
        return None


    return data.get("question")


# ============================================================
# CLEAN PROBLEM NAME
# ============================================================

def clean_name(name):

    name = name.lower()

    name = re.sub(
        r"[^a-z0-9]+",
        "-",
        name
    )

    name = name.strip("-")

    return name


# ============================================================
# LANGUAGE -> FILE EXTENSION
# ============================================================

def get_extension(language):

    language = language.lower()

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
# CREATE README
# ============================================================

def create_problem_readme(
    folder,
    number,
    title,
    difficulty,
    language,
    slug
):

    content = f"""# {title}

- **Problem Number:** {number}
- **Difficulty:** {difficulty}
- **Language:** {language}
- **LeetCode:** https://leetcode.com/problems/{slug}/
"""


    readme = folder / "README.md"

    readme.write_text(
        content,
        encoding="utf-8"
    )


# ============================================================
# PROCESS ONE PROBLEM
# ============================================================

def process_problem(recent_submission):

    submission_id = recent_submission.get("id")

    slug = recent_submission.get(
        "titleSlug"
    )

    title = recent_submission.get(
        "title"
    )


    if not submission_id or not slug:

        return


    print()
    print("-" * 60)

    print("Problem:", title)

    print("Slug:", slug)

    print(
        "Submission ID:",
        submission_id
    )


    # --------------------------------------------------------
    # GET SUBMISSION DETAILS
    # --------------------------------------------------------

    details = get_submission_code(
        submission_id
    )


    if not details:

        print(
            "Could not get submission details."
        )

        return


    # --------------------------------------------------------
    # CHECK ACCEPTED
    # --------------------------------------------------------

    status = details.get(
        "statusDisplay"
    )


    if status != "Accepted":

        print(
            "Submission is not Accepted."
        )

        return


    print(
        "Status:",
        status
    )


    # --------------------------------------------------------
    # GET CODE
    # --------------------------------------------------------

    code = details.get(
        "code"
    )


    if not code:

        print(
            "Submission code is empty."
        )

        return


    # --------------------------------------------------------
    # GET LANGUAGE
    #
    # IMPORTANT:
    # LeetCode now returns lang as an object:
    #
    # lang {
    #     name
    # }
    # --------------------------------------------------------

    lang_info = details.get(
        "lang"
    ) or {}


    language = lang_info.get(
        "name",
        "unknown"
    )


    print(
        "Language:",
        language
    )


    # --------------------------------------------------------
    # QUESTION INFORMATION
    # --------------------------------------------------------

    question = details.get(
        "question"
    )


    if not question:

        question = get_question_info(
            slug
        )


    if not question:

        print(
            "Could not get question information."
        )

        return


    number = (
        question.get(
            "questionFrontendId"
        )
        or
        question.get(
            "questionId"
        )
    )


    title = question.get(
        "title",
        title
    )


    difficulty = question.get(
        "difficulty",
        "Unknown"
    )


    # --------------------------------------------------------
    # CREATE FOLDER NAME
    # --------------------------------------------------------

    try:

        number_int = int(number)

        folder_name = (
            f"{number_int:04d}-"
            f"{clean_name(slug)}"
        )

    except (
        ValueError,
        TypeError
    ):

        folder_name = (
            f"{number}-"
            f"{clean_name(slug)}"
        )


    # --------------------------------------------------------
    # REPOSITORY
    # --------------------------------------------------------

    repo_dir = Path(
        GITHUB_REPO_DIR
    )


    if not repo_dir.exists():

        print()
        print(
            "ERROR: GitHub repository "
            "directory does not exist:"
        )

        print(repo_dir)

        return


    root = (
        repo_dir / "leetcode"
    )


    root.mkdir(
        parents=True,
        exist_ok=True
    )


    folder = (
        root / folder_name
    )


    folder.mkdir(
        parents=True,
        exist_ok=True
    )


    # --------------------------------------------------------
    # CREATE SOLUTION FILE
    # --------------------------------------------------------

    extension = get_extension(
        language
    )


    solution_file = (
        folder /
        f"solution.{extension}"
    )


    # --------------------------------------------------------
    # DON'T OVERWRITE EXISTING SOLUTION
    # --------------------------------------------------------

    if solution_file.exists():

        print()
        print(
            "Already exists:"
        )

        print(solution_file)

        return


    # --------------------------------------------------------
    # WRITE CODE
    # --------------------------------------------------------

    solution_file.write_text(
        code,
        encoding="utf-8"
    )


    print()
    print("Created:")

    print(solution_file)


    # --------------------------------------------------------
    # CREATE README
    # --------------------------------------------------------

    create_problem_readme(
        folder,
        number,
        title,
        difficulty,
        language,
        slug
    )


    print()
    print(
        "Added:",
        number,
        "-",
        title
    )


# ============================================================
# GIT PUSH
# ============================================================

def git_push(repo_dir):

    print()

    print("=" * 60)

    print(
        "        PUSHING TO GITHUB"
    )

    print("=" * 60)


    try:

        # ----------------------------------------------------
        # CHECK GIT REPOSITORY
        # ----------------------------------------------------

        result = subprocess.run(
            [
                "git",
                "rev-parse",
                "--is-inside-work-tree"
            ],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )


        if result.returncode != 0:

            print()
            print("ERROR:")

            print(
                "This folder is not "
                "a Git repository."
            )

            return


        # ----------------------------------------------------
        # CHECK CHANGES
        # ----------------------------------------------------

        result = subprocess.run(
            [
                "git",
                "status",
                "--porcelain"
            ],
            cwd=repo_dir,
            capture_output=True,
            text=True
        )


        if not result.stdout.strip():

            print()

            print(
                "Nothing new to push."
            )

            return


        # ----------------------------------------------------
        # GIT ADD
        # ----------------------------------------------------

        print()

        print(
            "Adding files..."
        )


        subprocess.run(
            [
                "git",
                "add",
                "."
            ],
            cwd=repo_dir,
            check=True
        )


        # ----------------------------------------------------
        # GIT COMMIT
        # ----------------------------------------------------

        print(
            "Creating commit..."
        )


        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "Add accepted LeetCode solutions"
            ],
            cwd=repo_dir,
            check=True
        )


        # ----------------------------------------------------
        # GIT PUSH
        # ----------------------------------------------------

        print(
            "Pushing to GitHub..."
        )


        subprocess.run(
            [
                "git",
                "push"
            ],
            cwd=repo_dir,
            check=True
        )


        print()

        print(
            "Successfully pushed "
            "to GitHub! ✅"
        )


    except subprocess.CalledProcessError as e:

        print()

        print(
            "Git error:"
        )

        print(e)


    except Exception as e:

        print()

        print(
            "Unexpected Git error:"
        )

        print(e)


# ============================================================
# MAIN SYNC
# ============================================================

def sync():

    print()

    print("=" * 60)

    print(
        "        LEETCODE → GITHUB SYNC"
    )

    print("=" * 60)

    print()


    # --------------------------------------------------------
    # GET RECENT ACCEPTED SUBMISSIONS
    # --------------------------------------------------------

    print(
        "Checking LeetCode..."
    )


    recent = get_recent_submissions()


    if not recent:

        print()

        print(
            "No accepted submissions found."
        )

        return


    print()

    print(
        f"Found {len(recent)} "
        f"recent accepted submissions."
    )


    # --------------------------------------------------------
    # PROCESS EACH SUBMISSION
    # --------------------------------------------------------

    for submission in recent:

        try:

            process_problem(
                submission
            )

        except Exception as e:

            print()

            print(
                "Error while processing "
                "problem:"
            )

            print(e)

            print(
                "Skipping this problem..."
            )


    # --------------------------------------------------------
    # PUSH TO GITHUB
    # --------------------------------------------------------

    repo_dir = Path(
        GITHUB_REPO_DIR
    )


    git_push(
        repo_dir
    )


    print()

    print("=" * 60)

    print(
        "SYNC COMPLETE"
    )

    print("=" * 60)

    print()


# ============================================================
# PROGRAM START
# ============================================================

if __name__ == "__main__":

    try:

        sync()

    except KeyboardInterrupt:

        print()

        print(
            "Sync cancelled."
        )

    except Exception as e:

        print()

        print("=" * 60)

        print(
            "FATAL ERROR"
        )

        print("=" * 60)

        print()

        print(e)

        print()