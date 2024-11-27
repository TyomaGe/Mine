import sys
import re
from collections import defaultdict
from statistics import mean
from datetime import datetime


def get_params():
    files = []
    stats = []
    for param in sys.argv[1:]:
        if "--" == param[:2]:
            stats.append(param[2:])
        else:
            files.append(param)
    return {'files': files, 'stats': stats}


class LogAnalyzer:
    def __init__(self, files, stats):
        self.__files = files
        self.__stats = stats

    def __make_log_entry(self, line):
        regex_pattern = (
            r'(\S+) - - \[(.*)\] "(GET|PUT|POST|HEAD|OPTIONS|DELETE) (\S+) '
            r'(\S+)" (\d+) (\d+) "(.*?)" "(.*?)" (\d+)?'
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
                'processing_time': int(matching.group(10)) if matching.group(
                    10) else None
            }
            return log_entry
        return None

    def __parse_logfile(self, filename):
        with open(filename, 'r') as file:
            lines = [self.__make_log_entry(line) for line in file if
                     self.__make_log_entry(line) is not None]
        return lines

    def __slowest_page(self, data):
        max_time = 0
        slowest = None
        for entry in data:
            processing_time = entry.get('processing_time')
            if processing_time is not None:
                processing_time = int(processing_time)
            else:
                processing_time = 0
            if processing_time >= max_time:
                max_time = processing_time
                slowest = entry
        return slowest

    def __fastest_page(self, data):
        min_time = 9999999999999
        fastest = None
        for entry in data:
            processing_time = entry.get('processing_time')
            if processing_time is not None:
                processing_time = int(processing_time)
                if processing_time <= min_time:
                    min_time = processing_time
                    fastest = entry
        return fastest

    def __slowest_page_avg(self, data):
        page_times = defaultdict(list)
        for entry in data:
            processing_time = entry.get('processing_time')
            if processing_time is not None:
                page_name = entry.get('page_name')
                page_times[page_name].append(int(processing_time))
        avg_times = {}
        for page, times in page_times.items():
            avg_times[page] = mean(times)
        slowest_page = None
        highest_avg = -1
        for page, avg_time in avg_times.items():
            if avg_time > highest_avg:
                highest_avg = avg_time
                slowest_page = page
            elif avg_time == highest_avg:
                if slowest_page is None or page < slowest_page:
                    slowest_page = page
        return slowest_page, highest_avg

    def __most_popular_page(self, data):
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

    def __most_active_client(self, data):
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

    def __most_popular_browser(self, data):
        counter = defaultdict(int)
        for entry in data:
            browser_info = entry.get('user_agent')
            if browser_info is not None:
                browser = browser_info.split('/')[0]
                counter[browser] += 1
        most_popular = None
        max_count = -1
        for browser, count in counter.items():
            if count > max_count:
                max_count = count
                most_popular = browser
            elif count == max_count:
                if most_popular is None or browser < most_popular:
                    most_popular = browser
        return most_popular, max_count

    def __most_active_client_by_day(self, data):
        client_activity = defaultdict(lambda: defaultdict(int))
        for entry in data:
            ip = entry.get('ip')
            date_str = entry.get('date')
            if ip and date_str:
                date = datetime.strptime(date_str,
                                         "%d/%b/%Y:%H:%M:%S %z").date()
                client_activity[ip][date] += 1
        most_active_client = None
        max_requests = -1
        max_day = None
        for ip, dates in client_activity.items():
            for date, requests in dates.items():
                if requests > max_requests or (requests == max_requests and (
                        most_active_client is None
                        or ip < most_active_client)):
                    max_requests = requests
                    most_active_client = ip
                    max_day = date
        return most_active_client, max_requests, max_day

    def analyze(self):
        for filename in self.__files:
            print(f"============= {filename} =============")
            data = self.__parse_logfile(filename)
            if 'mppage' in self.__stats:
                most_popular = self.__most_popular_page(data)
                print("Most Popular Page:")
                print(f"{most_popular[0]} : {most_popular[1]}")
                print()
            if 'maclient' in self.__stats:
                most_active = self.__most_active_client(data)
                print("Most Active Client:")
                print(f"{most_active[0]} : {most_active[1]}")
                print()
            if 'spage' in self.__stats:
                slowest = self.__slowest_page(data)
                print("Slowest Page:")
                print(
                    f"{slowest['page_name']} :"
                    f" {slowest.get('processing_time')}")
                print()
            if 'fpage' in self.__stats:
                fastest = self.__fastest_page(data)
                print("Fastest Page:")
                print(
                    f"{fastest['page_name']} :"
                    f" {fastest.get('processing_time')}")
                print()
            if 'savgpage' in self.__stats:
                slowest_avg = self.__slowest_page_avg(data)
                print("Slowest Page (Average):")
                print(f"{slowest_avg[0]} : {slowest_avg[1]}")
                print()
            if 'popbrowser' in self.__stats:
                popular_browser = self.__most_popular_browser(data)
                print("Most Popular Browser:")
                print(f"{popular_browser[0]} : {popular_browser[1]}")
                print()
            if 'maclientday' in self.__stats:
                most_active_client_day = self.__most_active_client_by_day(data)
                print("Most Active Client by Day:")
                print(
                    f"{most_active_client_day[0]} on "
                    f"{most_active_client_day[2]} "
                    f": {most_active_client_day[1]}")
                print()


def main():
    params = get_params()
    analyzer = LogAnalyzer(params['files'], params['stats'])
    analyzer.analyze()
    print(type(analyzer.analyze))
    print(type(get_params))


if __name__ == "__main__":
    main()

# Примеры ввода
# python log_script.py example_1.log example_2.log --fpage
# python log_script.py example_2.log --maclientday --savgpage
# python log_script.py example_1.log example_2.log --mppage --maclient

# Все параметры
# --mppage --maclient --spage --fpage
# --savgpage --popbrowser --maclientday
