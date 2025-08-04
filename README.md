# pytruder — Lightweight HTTP Intruder-Style Fuzzer

fuzz HTTP requests with multi-position payloads, save full responses, and optionally grep for interesting matches.

---

## Features

- Replace multiple placeholders like `§1§`, `§2§` in a raw HTTP request template
- Send each request using the `requests` library
- Save responses to files (`outdir/###_payload.txt`)
- Optional grep for strings (e.g. SQL errors, flags)
- CSV summary output for quick triage

---

## Usage

```bash
python pytruder.py \
  -r request.txt \
  -p generated_payloads.csv \
  -o outdir \
  --base-url http://192.168.10.10 \
  --grep "pg_query()" \
  --csv results.csv \
  --grep-output matches.txt \
  --delay 0.2
```

### Required:
- `-r`: Path to raw HTTP request template (with `§1§`, `§2§`, etc.)
- `-p`: Path to CSV payload list (1 row = 1 request)
- `-o`: Output directory for responses
- `--base-url`: Scheme + domain (e.g. `http://localhost:8080`)

---

## Input Files

### request.txt

```http
POST /login HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded

username=§1§&password=§2§
```

You can also fuzz headers:

```
Authorization: Bearer §1§
```

---

### payloads.csv

```csv
admin,password123
admin,' OR 1=1 --
' OR 'a'='a,pass
```

Each row provides values for `§1§`, `§2§`, ...
Each row is ONE request, there is a `generate_payloads.py` in this repo to help with creating these rows.

---

## Output

- `outdir/000_admin_password123.txt` — Full HTTP body
- `results.csv` (optional):

  | Index | Payloads              | Status | Length | GrepMatch |
  |-------|------------------------|--------|--------|-----------|
  | 000   | admin\|password123     | 200    | 1342   | No        |

---

## Options

| Flag         | Description                                 |
|--------------|---------------------------------------------|
| `--grep`     | Highlight responses that contain this string |
| `--csv`      | Write summary of all results to CSV         |
| `--delay`    | Wait (seconds) between each request         |

---

## Example: SQLi Fuzz

```bash
python pytruder.py -r login.req -p sqli.csv -o out --base-url http://10.10.10.10 \
  --grep "syntax error" --csv output.csv --delay 0.25
```

---
