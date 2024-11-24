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
            'processing_time': matching.group(10) if matching.group(
                10) else None
        }
        return log_entry
    return None


def parse_logfile(filename):
    with open(filename, 'r') as file:
        lines = [make_log_entry(line) for line in file if
                 make_log_entry(line) is not None]
    return lines


def pretty_print(stats, title):
    print(f"{title}:")
    print(f"{stats[0][0]} : {stats[0][1]}")
    print()


def make_stat(data, parameter):
    counter = defaultdict(int)
    for entry in data:
        value = entry.get(parameter)
        counter[value] += 1
    return sorted(counter.items(), key=lambda x: x[1], reverse=True)


def most_popular_resource(data):
    return make_stat(data, "page_name")


def most_active_client(data):
    return make_stat(data, "ip")


def main():
    # Примеры использования через консоль
    # python log_script.py example_1.log example_2.log --client
    # python log_script.py example_2.log --resource --client

    params = get_params()
    for filename in params["files"]:
        print(f"============= {filename} =============")
        data = parse_logfile(filename)
        if 'resource' in params["stats"]:
            most_popular = most_popular_resource(data)
            pretty_print(most_popular, "Most Popular Resource")
        if 'client' in params["stats"]:
            most_popular = most_active_client(data)
            pretty_print(most_popular, "Most Active Client")


if __name__ == "__main__":
    main()
