import os
import re
import json
import subprocess
import requests
from pathlib import Path
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
    r"C:\Users\farju\OneDrive\Desktop\lc\leetcode-github-sync"
)

GRAPHQL_URL = "https://leetcode.com/graphql/"


# ============================================================
# CHECK ENV
# ============================================================

if not USERNAME:
    raise Exception("LEETCODE_USERNAME missing in .env")

if not LEETCODE_SESSION:
    raise Exception("LEETCODE_SESSION missing in .env")


# ============================================================
# SESSION
# ============================================================

session = requests.Session()

session.headers.update({

    "Content-Type": "application/json",

    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36",

    "Referer":
        "https://leetcode.com/",

    "Origin":
        "https://leetcode.com",

    "Accept":
        "application/json, text/plain, */*",

    "Accept-Encoding":
        "gzip, deflate"

})


session.cookies.set(
    "LEETCODE_SESSION",
    LEETCODE_SESSION,
    domain=".leetcode.com"
)


if CSRF_TOKEN:

    session.cookies.set(
        "csrftoken",
        CSRF_TOKEN,
        domain=".leetcode.com"
    )

    session.headers["x-csrftoken"] = CSRF_TOKEN


# ============================================================
# GRAPHQL
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

        print("Network error:")
        print(e)

        return None


    print(
        "HTTP status:",
        response.status_code
    )


    try:

        result = response.json()

    except Exception:

        print(
            "Invalid JSON returned by LeetCode."
        )

        print(
            response.text[:2000]
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


# ============================================================
# GET RECENT ACCEPTED PROBLEMS
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


    return (
        data.get(
            "recentAcSubmissionList"
        )
        or []
    )


# ============================================================
# GET ACCEPTED SUBMISSION FROM PROBLEM
#
# THIS IS THE IMPORTANT FIX
# ============================================================

def get_accepted_submission(slug):

    query = """
    query submissionList(
        $offset: Int!,
        $limit: Int!,
        $lastKey: String,
        $questionSlug: String!
    ) {

        questionSubmissionList(

            offset: $offset,

            limit: $limit,

            lastKey: $lastKey,

            questionSlug: $questionSlug

        ) {

            lastKey

            hasNext

            submissions {

                id

                status

                statusDisplay

                lang

                runtime

                memory

                timestamp

                titleSlug

            }
        }
    }
    """


    variables = {

        "offset": 0,

        "limit": 20,

        "lastKey": None,

        "questionSlug": slug

    }


    data = graphql(

        query,

        variables,

        "submissionList"

    )


    if not data:

        return None


    submission_data = (
        data.get(
            "questionSubmissionList"
        )
    )


    if not submission_data:

        print(
            "questionSubmissionList returned null."
        )

        return None


    submissions = (
        submission_data.get(
            "submissions"
        )
        or []
    )


    print(
        "Found",
        len(submissions),
        "submissions for this problem."
    )


    # --------------------------------------------------------
    # FIND ACCEPTED SUBMISSION
    # --------------------------------------------------------

    for submission in submissions:

        status = (
            submission.get(
                "statusDisplay"
            )
            or ""
        ).lower()


        if status == "accepted":

            print(
                "Accepted submission ID:",
                submission.get("id")
            )

            print(
                "Language:",
                submission.get("lang")
            )

            return submission


    print(
        "No Accepted submission found."
    )

    return None


# ============================================================
# GET SUBMISSION CODE
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

        "submissionId":
            int(submission_id)

    }


    data = graphql(

        query,

        variables,

        "submissionDetails"

    )


    if not data:

        return None


    details = (
        data.get(
            "submissionDetails"
        )
    )


    if not details:

        print(
            "submissionDetails returned NULL."
        )

        return None


    return details


# ============================================================
# GET QUESTION INFO
# ============================================================

def get_question_info(slug):

    query = """
    query questionData(
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

        "questionData"

    )


    if not data:

        return None


    return data.get(
        "question"
    )


# ============================================================
# CLEAN NAME
# ============================================================

def clean_name(name):

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
    ).lower()


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

def create_readme(
    folder,
    number,
    title,
    difficulty,
    language,
    slug
):

    content = f"""# {number}. {title}

- Difficulty: {difficulty}
- Language: {language}

## LeetCode

https://leetcode.com/problems/{slug}/
"""


    readme = (
        folder / "README.md"
    )


    readme.write_text(
        content,
        encoding="utf-8"
    )


# ============================================================
# PROCESS ONE PROBLEM
# ============================================================

def process_problem(problem):

    slug = problem.get(
        "titleSlug"
    )

    title = problem.get(
        "title"
    )


    print()
    print("=" * 60)

    print(
        "Problem:",
        title
    )

    print(
        "Slug:",
        slug
    )

    print("=" * 60)


    if not slug:

        print(
            "No slug."
        )

        return


    # --------------------------------------------------------
    # STEP 1
    # GET ACCEPTED SUBMISSION FROM QUESTION
    # --------------------------------------------------------

    print()
    print(
        "Finding accepted submission..."
    )


    submission = (
        get_accepted_submission(
            slug
        )
    )


    if not submission:

        print(
            "Could not find accepted submission."
        )

        return


    submission_id = (
        submission.get("id")
    )


    if not submission_id:

        print(
            "Submission ID missing."
        )

        return


    # --------------------------------------------------------
    # STEP 2
    # GET ACTUAL CODE
    # --------------------------------------------------------

    print()
    print(
        "Getting submission code..."
    )


    details = (
        get_submission_details(
            submission_id
        )
    )


    if not details:

        print()
        print(
            "Could not get submission details."
        )

        print(
            "Submission ID:",
            submission_id
        )

        return


    code = details.get(
        "code"
    )


    if not code:

        print(
            "Submission code is empty."
        )

        return


    # --------------------------------------------------------
    # STATUS
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
            "Not accepted."
        )

        return


    # --------------------------------------------------------
    # LANGUAGE
    # --------------------------------------------------------

    lang_info = (
        details.get("lang")
        or {}
    )


    language = (
        lang_info.get(
            "name"
        )
        or submission.get(
            "lang"
        )
        or "unknown"
    )


    print(
        "Language:",
        language
    )


    # --------------------------------------------------------
    # QUESTION INFO
    # --------------------------------------------------------

    question = (
        details.get(
            "question"
        )
    )


    if not question:

        question = (
            get_question_info(
                slug
            )
        )


    if not question:

        print(
            "Could not get question info."
        )

        return


    number = (
        question.get(
            "questionFrontendId"
        )
    )


    if not number:

        number = (
            question.get(
                "questionId"
            )
        )


    title = (
        question.get(
            "title"
        )
        or title
    )


    difficulty = (
        question.get(
            "difficulty"
        )
        or "Unknown"
    )


    # --------------------------------------------------------
    # FOLDER
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


    repo = Path(
        GITHUB_REPO_DIR
    )


    if not repo.exists():

        print(
            "Repository does not exist:"
        )

        print(repo)

        return


    leetcode_folder = (
        repo / "leetcode"
    )


    leetcode_folder.mkdir(
        parents=True,
        exist_ok=True
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
    # FILE
    # --------------------------------------------------------

    extension = (
        get_extension(
            language
        )
    )


    solution_file = (
        problem_folder /
        f"solution.{extension}"
    )


    # --------------------------------------------------------
    # DON'T OVERWRITE
    # --------------------------------------------------------

    if solution_file.exists():

        print()
        print(
            "Already exists:"
        )

        print(
            solution_file
        )

        return


    # --------------------------------------------------------
    # WRITE CODE
    # --------------------------------------------------------

    solution_file.write_text(
        code,
        encoding="utf-8"
    )


    print()
    print(
        "SUCCESS! Solution saved:"
    )

    print(
        solution_file
    )


    # --------------------------------------------------------
    # README
    # --------------------------------------------------------

    create_readme(

        problem_folder,

        number,

        title,

        difficulty,

        language,

        slug

    )


    print(
        "README created."
    )


# ============================================================
# GIT
# ============================================================

def git_push():

    repo = Path(
        GITHUB_REPO_DIR
    )


    print()
    print("=" * 60)

    print(
        "        PUSHING TO GITHUB"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # STATUS
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


    if not result.stdout.strip():

        print()
        print(
            "Nothing new to push."
        )

        return


    print()
    print(
        "Changes:"
    )

    print(
        result.stdout
    )


    # --------------------------------------------------------
    # ADD
    # --------------------------------------------------------

    print(
        "Adding files..."
    )


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
    # COMMIT
    # --------------------------------------------------------

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

        cwd=repo,

        check=True
    )


    # --------------------------------------------------------
    # PUSH
    # --------------------------------------------------------

    print(
        "Pushing to GitHub..."
    )


    subprocess.run(

        [
            "git",
            "push"
        ],

        cwd=repo,

        check=True
    )


    print()
    print(
        "Successfully pushed to GitHub! ✅"
    )


# ============================================================
# MAIN SYNC
# ============================================================

def sync():

    print()
    print("=" * 60)

    print(
        "       LEETCODE → GITHUB SYNC"
    )

    print("=" * 60)


    # --------------------------------------------------------
    # GET RECENT ACCEPTED
    # --------------------------------------------------------

    print()
    print(
        "Getting recent accepted problems..."
    )


    problems = (
        get_recent_submissions()
    )


    if not problems:

        print(
            "No recent accepted submissions."
        )

        return


    print()
    print(
        "Found",
        len(problems),
        "recent accepted problems."
    )


    # --------------------------------------------------------
    # PROCESS EACH
    # --------------------------------------------------------

    for problem in problems:

        try:

            process_problem(
                problem
            )

        except Exception as e:

            print()
            print(
                "ERROR:"
            )

            print(e)

            print(
                "Skipping..."
            )


    # --------------------------------------------------------
    # GITHUB
    # --------------------------------------------------------

    git_push()


    print()
    print("=" * 60)

    print(
        "SYNC COMPLETE"
    )

    print("=" * 60)


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
        print(
            "FATAL ERROR:"
        )

        print(e)