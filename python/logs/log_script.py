import sys
import re
from collections import defaultdict


def get_params():
    files = []
    stats = []
    for param in sys.argv[1:]:
        if "--" == param[:2]:
            stats.append(param[2:])
        else:
            files.append(param)
    return {'files': files, 'stats': stats}


def make_log_entry(line):
    regex_pattern = (
        r'(\S+) - - \[(.*)\] "(GET|PUT|POST|HEAD|OPTIONS|DELETE) (\S+) (\S+)" '
        r'(\d+) (\d+) "(.*?)" "(.*?)" (\d+)?'
    )
    regex = re.compile(regex_pattern)
    matching = regex.match(line)
    if matching:
        log_entry = {
            'ip': matching.group(1),
            'date': matching.group(2),
            'request': matching.group(3),
            'page_name': matching.group(4),
            'type_version': matching.group(5),
            'response_code': matching.group(6),
            'response_size': matching.group(7),
            'referrer': matching.group(8),
            'user_agent': matching.group(9),
            'processing_time': int(matching.group(10))
            if matching.group(10) else None
        }
        return log_entry
    return None


def parse_logfile(filename):
    with open(filename, 'r') as file:
        lines = [make_log_entry(line) for line in file
                 if make_log_entry(line) is not None]
    return lines


def most_popular_page(data):
    page_counter = defaultdict(int)
    for entry in data:
        page_name = entry.get('page_name')
        if page_name is not None:
            page_counter[page_name] += 1
    most_popular = None
    max_count = -1
    for page, count in page_counter.items():
        if count > max_count:
            max_count = count
            most_popular = page
        elif count == max_count:
            if most_popular is None or page < most_popular:
                most_popular = page
    return most_popular, max_count


def most_active_client(data):
    counter = defaultdict(int)
    for entry in data:
        user_id = entry.get('ip')
        if user_id is not None:
            counter[user_id] += 1
    most_active = None
    max_count = -1
    for ip, count in counter.items():
        if count > max_count:
            max_count = count
            most_active = ip
        elif count == max_count:
            if most_active is None or ip < most_active:
                most_active = ip
    return most_active, max_count


def analyze(files, stats):
    for filename in files:
        print(f"============= {filename} =============")
        data = parse_logfile(filename)
        if 'mppage' in stats:
            most_popular = most_popular_page(data)
            print("Most Popular Page:")
            print(f"{most_popular[0]} : {most_popular[1]}")
            print()
        if 'maclient' in stats:
            most_active = most_active_client(data)
            print("Most Active Client:")
            print(f"{most_active[0]} : {most_active[1]}")
            print()


def main():
    params = get_params()
    analyze(params["files"], params["stats"])


if __name__ == "__main__":
    main()

# Пример ввода
# python log_script.py example_1.log example_2.log --mppage --maclient
