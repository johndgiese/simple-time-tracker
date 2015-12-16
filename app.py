from datetime import datetime
from flask import Flask, request, render_template, redirect


app = Flask(__name__)


logfile = 'entries.txt'


def log_entry(name):
    if ',' in name:
        raise Exception("Comma is not allowed in name.")

    now = datetime.utcnow()
    with open(logfile, 'a') as log:
        log.write('{},{}\n'.format(name, now))


def get_totals_from_log():
    results = {}
    with open(logfile, 'r') as log:
        for line in log:
            name, entry_datetime_str = tuple(line.strip().split(','))
            entry_datetime = datetime.strptime(entry_datetime_str, '%Y-%m-%d %H:%M:%S.%f')

            if name in results:
                if results[name]['start'] is None:
                    results[name]['start'] = entry_datetime
                else:
                    results[name]['total'] += minutes(entry_datetime, results[name]['start'])
                    results[name]['start'] = None
            else:
                results[name] = {}
                results[name]['total'] = 0.0
                results[name]['start'] = entry_datetime

    now = datetime.utcnow()
    for result in results.values():
        if result['start'] is not None:
            result['total'] += minutes(now, result['start'])

    return results


def minutes(start, stop):
    seconds = (start - stop).total_seconds()
    return seconds/3600.0


@app.route('/<your_name>/', methods=['GET', 'POST'])
def index(your_name):
    your_name = your_name.lower()
    if request.method == 'POST':
        log_entry(your_name)
        return redirect(request.url)
    else:
        totals = get_totals_from_log()
        clock_running = (your_name in totals) and (totals[your_name]['start'] is not None)
        return render_template('index.html', clock_running=clock_running, totals=totals)


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'Specify your name in the URL, like: "/john/".'


if __name__ == "__main__":
    open(logfile, 'a').close()  # create logfile if doesn't exist
    app.run(debug=True)
