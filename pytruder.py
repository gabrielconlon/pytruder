import os
import csv
import time
import argparse
import requests
from pathlib import Path

def parse_template(template_path):
    with open(template_path, 'r') as f:
        lines = f.read().splitlines()

    try:
        empty_line_index = lines.index('')
        header_lines = lines[:empty_line_index]
        body_lines = lines[empty_line_index + 1:]
    except ValueError:
        header_lines = lines
        body_lines = []

    method_line = header_lines[0]
    method, path, _ = method_line.split(' ')
    headers = {}
    for line in header_lines[1:]:
        key, value = line.split(':', 1)
        headers[key.strip()] = value.strip()

    body = '\n'.join(body_lines)
    return method, path, headers, body

def apply_payloads(template: str, payloads: list) -> str:
    result = template
    for i, value in enumerate(payloads, start=1):
        result = result.replace(f"§{i}§", value)
    return result

def send_request(base_url, method, path, headers, body):
    url = base_url + path
    response = requests.request(method, url, headers=headers, data=body)
    return response

def main():
    parser = argparse.ArgumentParser(description="Multi-position HTTP fuzzer with grep capture")
    parser.add_argument('-r', '--request', required=True, help='Path to HTTP request template file')
    parser.add_argument('-p', '--payloads', required=True, help='Path to CSV payloads file')
    parser.add_argument('-o', '--output', required=True, help='Directory to write response files')
    parser.add_argument('--base-url', required=True, help='Base URL, e.g., http://127.0.0.1:8080')
    parser.add_argument('--grep', help='Keyword to search in response')
    parser.add_argument('--grep-output', help='Optional output file to save matching lines')
    parser.add_argument('--csv', help='Optional output CSV summary file')
    parser.add_argument('--delay', type=float, default=0.0, help='Delay between requests (seconds)')
    args = parser.parse_args()

    method, path, headers, body_template = parse_template(args.request)
    Path(args.output).mkdir(parents=True, exist_ok=True)

    with open(args.payloads, 'r') as f:
        reader = csv.reader(f)
        payload_rows = [row for row in reader if row]

    if args.csv:
        csv_output_path = Path(args.csv)
        csv_file = open(csv_output_path, 'w', newline='', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Index', 'Payloads', 'Status', 'Length', 'GrepMatch', 'GrepLines'])

    grep_lines_file = None
    if args.grep_output:
        grep_lines_file = open(args.grep_output, 'w', encoding='utf-8')

    for i, payloads in enumerate(payload_rows):
        try:
            request_body = apply_payloads(body_template, payloads)
            updated_headers = {k: apply_payloads(v, payloads) for k, v in headers.items()}
            if 'Content-Length' in updated_headers:
                updated_headers['Content-Length'] = str(len(request_body))

            response = send_request(args.base_url, method, path, updated_headers, request_body)
            out_path = Path(args.output) / f"{i:03d}_{'_'.join(payloads).replace('/', '_')}.txt"
            with open(out_path, 'w', encoding='utf-8') as f_out:
                f_out.write(f"### PAYLOADS: {payloads}\n")
                f_out.write(f"### STATUS CODE: {response.status_code}\n")
                f_out.write(response.text)

            grep_result = False
            grep_lines = []
            if args.grep:
                for line in response.text.splitlines():
                    if args.grep in line:
                        grep_result = True
                        grep_lines.append(line)
                        if grep_lines_file:
                            grep_lines_file.write(f"[{i:03d} | {'|'.join(payloads)}] {line}\n")

            print(f"[{'MATCH' if grep_result else '....'}] {i:03d} {payloads} -> {out_path}")

            if args.csv:
                csv_writer.writerow([
                    i,
                    '|'.join(payloads),
                    response.status_code,
                    len(response.text),
                    'YES' if grep_result else 'NO',
                    '\\n'.join(grep_lines)
                ])

        except Exception as e:
            print(f"[!] Error with payloads {payloads}: {e}")

        time.sleep(args.delay)

    if args.csv:
        csv_file.close()
    if grep_lines_file:
        grep_lines_file.close()

if __name__ == "__main__":
    main()
