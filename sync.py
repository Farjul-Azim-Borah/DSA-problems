import os
import re
import json
import requests
from pathlib import Path
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

load_dotenv()

USERNAME = os.getenv("LEETCODE_USERNAME")
LEETCODE_SESSION = os.getenv("LEETCODE_SESSION")
CSRF_TOKEN = os.getenv("LEETCODE_CSRF")

GRAPHQL_URL = "https://leetcode.com/graphql/"


# ============================================================
# CHECK ENVIRONMENT
# ============================================================

if not USERNAME:
    raise Exception(
        "LEETCODE_USERNAME is missing from .env"
    )

if not LEETCODE_SESSION:
    raise Exception(
        "LEETCODE_SESSION is missing from .env"
    )


# ============================================================
# CREATE HTTP SESSION
# ============================================================

session = requests.Session()

session.headers.update({

    "Content-Type": "application/json",

    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36",

    "Referer":
        "https://leetcode.com/",

    "Origin":
        "https://leetcode.com"
})


session.cookies.update({

    "LEETCODE_SESSION":
        LEETCODE_SESSION
})


if CSRF_TOKEN:

    session.cookies.update({

        "csrftoken":
            CSRF_TOKEN
    })

    session.headers.update({

        "x-csrftoken":
            CSRF_TOKEN
    })


# ============================================================
# GRAPHQL FUNCTION
# ============================================================

def graphql(query, variables=None, operation_name=None):

    payload = {

        "query":
            query,

        "variables":
            variables or {}
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

        print()
        print("Network error:")
        print(e)

        return None


    print(
        "HTTP status:",
        response.status_code
    )


    # --------------------------------------------------------
    # HTTP ERROR
    # --------------------------------------------------------

    if response.status_code != 200:

        print()
        print(
            "LeetCode returned an HTTP error:"
        )

        print(
            response.text[:3000]
        )

        return None


    # --------------------------------------------------------
    # JSON
    # --------------------------------------------------------

    try:

        result = response.json()

    except Exception:

        print()
        print(
            "LeetCode returned invalid JSON:"
        )

        print(
            response.text[:3000]
        )

        return None


    # --------------------------------------------------------
    # GRAPHQL ERROR
    # --------------------------------------------------------

    if "errors" in result:

        print()
        print(
            "GraphQL error:"
        )

        print(
            json.dumps(
                result["errors"],
                indent=2
            )
        )

        return None


    return result.get(
        "data"
    )


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

        "username":
            USERNAME,

        "limit":
            20
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
# GET SUBMISSIONS FOR A PARTICULAR PROBLEM
# ============================================================

def get_problem_submissions(slug):

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

                statusDisplay

                lang

                timestamp

            }
        }
    }

    """


    variables = {

        "offset":
            0,

        "limit":
            20,

        "lastKey":
            "",

        "questionSlug":
            slug
    }


    data = graphql(

        query,

        variables,

        "submissionList"
    )


    if not data:

        return []


    result = data.get(

        "questionSubmissionList"
    )


    if not result:

        return []


    return result.get(

        "submissions",

        []
    )


# ============================================================
# GET ACTUAL SUBMITTED CODE
# ============================================================

def get_submission_code(submission_id):

    query = """

    query submissionDetails(
        $submissionId: Int!
    ) {

        submissionDetails(

            submissionId:
                $submissionId

        ) {

            id

            code

            statusDisplay

            runtime

            memory

            timestamp

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

        "titleSlug":
            slug
    }


    data = graphql(

        query,

        variables,

        "questionTitle"
    )


    if not data:

        return None


    return data.get(

        "question"
    )


# ============================================================
# CLEAN NAME FOR FOLDER
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
# GET FILE EXTENSION
# ============================================================

def get_extension(language):

    language = language.lower()


    mapping = {

        "cpp":
            "cpp",

        "c++":
            "cpp",

        "c":
            "c",

        "java":
            "java",

        "python":
            "py",

        "python3":
            "py",

        "javascript":
            "js",

        "typescript":
            "ts",

        "go":
            "go",

        "rust":
            "rs",

        "kotlin":
            "kt",

        "swift":
            "swift",

        "csharp":
            "cs",

        "ruby":
            "rb",

        "php":
            "php",

        "scala":
            "scala",

        "dart":
            "dart",

        "mysql":
            "sql",

        "mssql":
            "sql",

        "postgresql":
            "sql"
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

    slug = recent_submission.get(
        "titleSlug"
    )

    title = recent_submission.get(
        "title"
    )


    if not slug:

        return


    print()
    print("-" * 60)

    print(
        "Problem:",
        title
    )

    print(
        "Slug:",
        slug
    )


    # --------------------------------------------------------
    # GET SUBMISSIONS
    # --------------------------------------------------------

    submissions = get_problem_submissions(

        slug
    )


    if not submissions:

        print(
            "Could not find submissions."
        )

        return


    # --------------------------------------------------------
    # FIND ACCEPTED SUBMISSION
    # --------------------------------------------------------

    accepted = None


    for submission in submissions:

        if submission.get(
            "statusDisplay"
        ) == "Accepted":

            accepted = submission

            break


    if not accepted:

        print(
            "No Accepted submission found."
        )

        return


    submission_id = accepted.get(
        "id"
    )


    language = accepted.get(
        "lang",
        "unknown"
    )


    print(
        "Submission ID:",
        submission_id
    )

    print(
        "Language:",
        language
    )


    # --------------------------------------------------------
    # GET CODE
    # --------------------------------------------------------

    details = get_submission_code(

        submission_id
    )


    if not details:

        print(
            "Could not get submission details."
        )

        return


    code = details.get(
        "code"
    )


    question = details.get(
        "question"
    )


    if not code:

        print(
            "Submission code is empty."
        )

        return


    # --------------------------------------------------------
    # QUESTION INFO
    # --------------------------------------------------------

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
    # FOLDER NAME
    # --------------------------------------------------------

    try:

        number_int = int(
            number
        )

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


    root = Path(
        "leetcode"
    )


    root.mkdir(
        exist_ok=True
    )


    folder = root / folder_name


    folder.mkdir(

        parents=True,

        exist_ok=True
    )


    # --------------------------------------------------------
    # FILE
    # --------------------------------------------------------

    extension = get_extension(

        language
    )


    solution_file = (

        folder /
        f"solution.{extension}"
    )


    # --------------------------------------------------------
    # DON'T OVERWRITE
    # --------------------------------------------------------

    if solution_file.exists():

        print(
            "Already exists:"
        )

        print(
            solution_file
        )

        return


    # --------------------------------------------------------
    # WRITE SOLUTION
    # --------------------------------------------------------

    solution_file.write_text(

        code,

        encoding="utf-8"
    )


    print(
        "Created:"
    )

    print(
        solution_file
    )


    # --------------------------------------------------------
    # WRITE README
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
# MAIN SYNC FUNCTION
# ============================================================

def sync():

    print()
    print("=" * 60)
    print(
        "        LEETCODE → GITHUB SYNC"
    )
    print("=" * 60)
    print()


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
        "recent accepted submissions."
    )


    for submission in recent:

        try:

            process_problem(
                submission
            )

        except Exception as e:

            print()
            print(
                "Error while processing problem:"
            )

            print(e)

            print(
                "Skipping this problem..."
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