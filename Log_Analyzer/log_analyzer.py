import sys
import json
import csv
import re
from datetime import datetime


def read_log_file(file_path):
    # Just read the lines and strip whitespace, skip empty lines
    lines = []
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    lines.append(line)
        return lines
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def parse_log_line(line):
    # Try parsing as JSON first
    try:
        data = json.loads(line)
        return data.get('timestamp', ''), data.get('level', '').upper(), data.get('message', '')
    except json.JSONDecodeError:
        pass

    # Fallback to plain text regex: YYYY-MM-DD HH:MM:SS LEVEL message
    match = re.match(r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+(\w+)\s+(.*)$', line)
    if match:
        return match.group(1), match.group(2).upper(), match.group(3)

    return None, 'UNKNOWN', line


def analyze_logs(lines, level_filter=None, from_time=None, to_time=None):
    counters = {'ERROR': 0, 'WARNING': 0, 'INFO': 0, 'UNKNOWN': 0}
    error_messages = {}
    failure_timestamps = []

    for line in lines:
        timestamp, level, message = parse_log_line(line)

        if not timestamp:
            continue

        if level_filter and level != level_filter:
            continue

        # Time range filtering
        if from_time or to_time:
            try:
                # Truncate seconds from log timestamp to match standard filter format easily
                log_time = datetime.strptime(timestamp[:16], '%Y-%m-%d %H:%M')
                if from_time and log_time < from_time:
                    continue
                if to_time and log_time > to_time:
                    continue
            except ValueError:
                pass

        # Count levels
        if level in counters:
            counters[level] += 1
        else:
            counters['UNKNOWN'] += 1

        # Track specific errors
        if level == 'ERROR':
            error_messages[message] = error_messages.get(message, 0) + 1
            time_part = timestamp.split()[1] if ' ' in timestamp else timestamp
            failure_timestamps.append(time_part)

    # Find the most common error message
    most_common_error = None
    if error_messages:
        most_common_error = max(error_messages, key=error_messages.get)

    return counters, most_common_error, failure_timestamps


def export_to_csv(filename, total_logs, counters, most_common_error):
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['metric', 'value'])
            writer.writerow(['total_logs', total_logs])
            writer.writerow(['errors', counters.get('ERROR', 0)])
            writer.writerow(['warnings', counters.get('WARNING', 0)])
            writer.writerow(['info', counters.get('INFO', 0)])
            writer.writerow(['most_common_error', most_common_error or 'None'])
        print(f"\nSummary exported to {filename}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")


def main():
    if len(sys.argv) < 3 or '-file' not in sys.argv:
        print("\nUsage: python log_analyzer.py -file <logfile> [options]")
        print("Options: --level LEVEL, --from 'YYYY-MM-DD HH:MM', --to 'YYYY-MM-DD HH:MM', -export FILE")
        sys.exit(1)

    # Simple index hunting for args—classic junior approach, easy to read
    file_path = sys.argv[sys.argv.index('-file') + 1]

    level_filter = None
    if '--level' in sys.argv:
        level_filter = sys.argv[sys.argv.index('--level') + 1].upper()

    from_time = None
    if '--from' in sys.argv:
        try:
            from_time = datetime.strptime(sys.argv[sys.argv.index('--from') + 1], '%Y-%m-%d %H:%M')
        except ValueError:
            print("Warning: Invalid '--from' format. Use 'YYYY-MM-DD HH:MM'")

    to_time = None
    if '--to' in sys.argv:
        try:
            to_time = datetime.strptime(sys.argv[sys.argv.index('--to') + 1], '%Y-%m-%d %H:%M')
        except ValueError:
            print("Warning: Invalid '--to' format. Use 'YYYY-MM-DD HH:MM'")

    export_file = None
    if '-export' in sys.argv:
        export_file = sys.argv[sys.argv.index('-export') + 1]

    # Process file
    log_lines = read_log_file(file_path)
    counters, most_common_error, failure_timestamps = analyze_logs(log_lines, level_filter, from_time, to_time)

    total_logs = counters['ERROR'] + counters['WARNING'] + counters['INFO']

    if export_file:
        export_to_csv(export_file, total_logs, counters, most_common_error)

    # Output results
    print("\n" + "=" * 40)
    print("LOG ANALYSIS SUMMARY")
    print("=" * 40)
    print(f"Total logs:           {total_logs}")
    print(f"Errors:               {counters['ERROR']}")
    print(f"Warnings:             {counters['WARNING']}")
    print(f"Info:                 {counters['INFO']}")
    if counters['UNKNOWN'] > 0:
        print(f"Unknown format:       {counters['UNKNOWN']}")
    print(f"Most frequent error:  {f'\"{most_common_error}\"' if most_common_error else 'None'}")

    if failure_timestamps:
        shown_timestamps = failure_timestamps[:10]
        output_str = ", ".join(shown_timestamps)
        if len(failure_timestamps) > 10:
            output_str += f" ... and {len(failure_timestamps) - 10} more"
        print(f"Failure timestamps:   {output_str}")
    print("=" * 40)


if __name__ == "__main__":
    main()
