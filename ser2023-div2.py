
import json
import bs4
import requests

url = 'https://nasouth23.kattis.com/contests/nasouth23d2/standings'
response = requests.get(url)

# #standings_wrapper > div > section.strip.strip-item-plain > div > table
# find the table

table = bs4.BeautifulSoup(response.text, 'html.parser').select_one(
    '#standings_wrapper > div > section.strip.strip-item-plain > div > table')

assert response.status_code == 200

# trim the table to only the rows
rows = table.select('tr')[1:-1]

contestants = []
for row in rows:
    contestant = {
        'contestant_id': row.select_one('td:nth-child(1)').text.strip(),
        'contestant_name': row.select_one('td:nth-child(2)').text.strip(),
    }
    contestants.append(contestant)


problems = []
thead = table.select_one('thead')
for th in thead.select('th')[3:]:
    problem = {
        'problem_id': th.text.strip(),
        # find a tag's title attribute
        'problem_name': th.find('a')['title']
    }

    problems.append(problem)

standings = []

for row in rows:
    standing = {
        'contestant_id': row.select_one('td:nth-child(1)').text.strip(),
        'contestant_name': row.select_one('td:nth-child(2)').text.strip(),
        'solve': int(row.select_one('td:nth-child(5)').text.strip()),
        'penalty': int(row.select_one('td:nth-child(6)').text.strip()),
    }

    judges = []
    for idx, td in enumerate(row.select('td')[6:]):
        judge = {
            'problem_id': problems[idx]['problem_id'],
            'problem_name': problems[idx]['problem_name'],
        }
        if 'class' in td.attrs:
            if td['class'][0] == 'solved' or td['class'][0] == 'first':
                judge['status'] = 'accepted'
            else:
                judge['status'] = 'wronganswer'
        else:
            judge['status'] = None

        solved_tag = td.select_one('.standings-table-result-cell-text')
        if solved_tag:
            submission = int(solved_tag.contents[0].strip())  # Gets the '1'
            time_tag = solved_tag.select_one(
                '.standings-table-result-cell-time')
            if time_tag:
                # Extract only the number part from '18 min'
                time = ''.join(
                    filter(
                        str.isdigit,
                        time_tag.text.strip()))
                time = int(time) if time else None
            else:
                time = None
            judge['submission'] = submission
            judge['time'] = time
        else:
            judge['submission'] = 0
            judge['time'] = None

        if judge['submission'] is not None and judge['time'] is not None:
            judge['penalty'] = (judge['submission'] - 1) * 20 + judge['time']
        else:
            judge['penalty'] = None

        judges.append(judge)

    standing['judge'] = judges
    standings.append(standing)

scoreboard = {
    'duration': 300,
    'contestants': contestants,
    'problems': problems,
    'standings': standings
}

# save to `ser2023-div2.json`
with open('ser2023-div2.json', 'w') as f:
    json.dump(scoreboard, f, indent=4)
