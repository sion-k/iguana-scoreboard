import json
import os
import sys
from os import path

PATH_ROOT = os.getcwd()
PATH_CONTESTS = path.join(PATH_ROOT, "contests.json")


def check_schema(file_path):
    if not path.exists(file_path):
        print("Input file doesn't exist.")
        return False
    try:
        js = json.load(open(file_path, 'r', encoding='utf-8'))
        if not js:
            raise Exception("Empty JSON file.")

        duration = js['duration']
        ensure_type(duration, int)
        contestants = js['contestants']
        ensure_type(contestants, list)
        problems = js['problems']
        ensure_type(problems, list)
        standings = js['standings']
        ensure_type(standings, list)

        # contestant_dict = dict()
        for contestant in filter(lambda x: ensure_type(x, dict), contestants):
            contestant_id = contestant['contestant_id']
            contestant_name = contestant['contestant_name']
            ensure_type(contestant_name, str)
            # contestant_dict[contestant_id] = contestant_name

        problem_dict = dict()
        for problem in filter(lambda x: ensure_type(x, dict), problems):
            problem_id = problem['problem_id']
            ensure_type(problem_id, str)
            problem_name = problem['problem_name']
            ensure_type(problem_name, str)
            problem_dict[problem_id] = problem_name

        for standing in filter(lambda x: ensure_type(x, dict), standings):
            contestant_id = standing['contestant_id']
            contestant_name = standing['contestant_name']
            ensure_type(contestant_name, str)
            solve = standing['solve']
            ensure_type(solve, int)
            penalty = standing['penalty']
            ensure_type(penalty, int)
            judge = standing['judge']
            ensure_type(judge, list)

            # ensure_eq(contestant_dict[contestant_id], contestant_name)
            ensure_eq(len(judge), len(problem_dict))
            summation = 0
            for j in judge:
                ensure_type(j, dict)
                problem_id = j['problem_id']
                ensure_type(problem_id, str)
                problem_name = j['problem_name']
                ensure_type(problem_name, str)
                status = j['status']
                ensure_type(status, str | None)
                submission = j['submission']
                ensure_type(submission, int)
                time = j['time']
                ensure_type(time, int | None)
                j_penalty = j['penalty']
                ensure_type(j_penalty, int | None)

                ensure_eq(problem_dict[problem_id], problem_name)
                if status is not None:
                    ensure(
                        status in [
                            'accepted',
                            'wronganswer'],
                        f"Invalid status: {status}")
                if time is not None:
                    # ensure(0 <= time <= duration, f"Invalid time: {time}")
                    ensure(0 <= time, f"Invalid time: {time}")
                summation += j_penalty if j_penalty is not None else 0

            # ensure_eq(penalty, summation)
        return True
    except Exception as e:
        print("Invalid JSON schema. Reason:", e)
        return False


def read_contests():
    try:
        js = json.load(open(PATH_CONTESTS, 'r', encoding='utf-8'))
        if not js:
            raise Exception("Empty JSON file.")
        return js
    except Exception as e:
        print("Invalid JSON schema. Reason:", e)
        return None


def ensure_type(obj, t):
    if not isinstance(obj, t):
        raise Exception(f"Invalid {t.__name__} object.")
    return True


def ensure_eq(a, b):
    if a != b:
        raise Exception(f"Expected {a} to be equal to {b}.")
    return True


def ensure(exp, msg):
    if not exp:
        raise Exception(msg)
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Invalid command.")
        quit(1)
    if sys.argv[1] == "check":
        input_file = sys.argv[2]
        if check_schema(input_file):
            print("Valid JSON schema.")
            quit(0)
        else:
            quit(1)
    if sys.argv[1] == "check-all":
        contests = read_contests()
        for contest in contests:
            print(f"Checking {contest['contest_name']}...")
            if not check_schema(contest['location']):
                quit(1)
        print("All contests are valid.")

    else:
        print("Invalid command.")
        quit(1)
