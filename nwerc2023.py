
import json
import bs4
import requests

url = 'https://2023.nwerc.eu/main/scoreboard/'
response = requests.get(url)
response.encoding = 'utf-8'

# #standings_wrapper > div > section.strip.strip-item-plain > div > table
# find the table

bs = bs4.BeautifulSoup(response.text, 'html.parser')
# #team\:6 > td.scoretn.cl_FFFFFF > a > span:nth-child(1) > span
# erase this element
bs.select(
    '#team\\:6 > td.scoretn.cl_FFFFFF > a > span:nth-child(1) > span')[0].extract()

tbody = bs.select(
    'body > div > div > div > div > table.scoreboard.center > tbody')[0]
# print number of children

contestants = []
for tr in tbody.find_all('tr'):
    if not tr.has_attr('id'):
        break
    # select contestant_id which is `id` attribute which tr has
    contestant_id = tr['id']
    contestant_name = tr.select(
        'td.scoretn.cl_FFFFFF > a > span:nth-child(1)')[0].text.strip()

    contestants.append({
        'contestant_id': contestant_id.split(':'),
        'contestant_name': contestant_name
    })

contestants.sort(key=lambda x: int(x['contestant_id'][1]))

# concatenate the id
for i, contestant in enumerate(contestants):
    contestant['contestant_id'] = ''.join(contestant['contestant_id'])

# body > div > div > div > div > table.scoreboard.center > thead > tr
tr = bs.select(
    'body > div > div > div > div > table.scoreboard.center > thead > tr')[0]

problems = []
for th in tr.find_all('th'):
    if not th.has_attr('title') or not th['title'].startswith('problem'):
        continue

    problem_id = th.select('a > span > span')[0].text.strip()
    problem_name = th['title'].split(' ', 1)[1]

    problems.append({
        'problem_id': problem_id,
        'problem_name': problem_name
    })

standings = []

for tr in tbody.find_all('tr'):
    if not tr.has_attr('id'):
        break

    contestant_id = tr['id']
    contestant_name = tr.select(
        'td.scoretn.cl_FFFFFF > a > span:nth-child(1)')[0].text.strip()

    solve = int(tr.select('td.scorenc')[0].text.strip())
    penalty_sum = int(tr.select('td.scorett')[0].text.strip())

    judge = []

    # for td wwith class score_cell
    for i, td in enumerate(tr.select('td.score_cell')):
        problem_id = problems[i]['problem_id']
        problem_name = problems[i]['problem_name']

        status = None
        # #team\:6 > td:nth-child(7) > a > div
        # if this div has class named `score_correct`` status is accepted
        if td.select('a > div.score_correct'):
            status = 'accepted'
        elif td.select('a > div.score_incorrect'):
            status = 'wronganswer'

        submission = 0
        # #team\:6 > td:nth-child(7) > a > div > span
        # if this div has span, it is submission
        if td.select('a > div > span'):
            submission = int(td.select('a > div > span')[
                             0].text.strip().split(' ')[0])

        # #team\:6 > td:nth-child(7) > a > div
        # if this div has found and text is not empty, it is time
        if status == 'accepted' and td.select(
                'a > div') and td.select('a > div')[0].text.strip():
            time = int(td.select('a > div')[0].text.strip().split(' ')[0])
        else:
            time = None

        # #team\:6 > td:nth-child(7) > a > div > span
        if status == 'accepted':
            penalty = 20 * (submission - 1) + time
        else:
            penalty = None

        judge.append({
            'problem_id': problem_id,
            'problem_name': problem_name,
            'status': status,
            'submission': submission,
            'time': time,
            'penalty': penalty
        })

    standings.append({
        'contestant_id': contestant_id,
        'contestant_name': contestant_name,
        'solve': solve,
        'penalty': penalty_sum,
        'judge': judge
    })

scoreboard = {
    'duration': 300,
    'contestants': contestants,
    'problems': problems,
    'standings': standings
}

# save to `nwerc2023.json`
with open('nwerc2023.json', 'w', encoding='utf-8') as f:
    json.dump(scoreboard, f, indent=4)
