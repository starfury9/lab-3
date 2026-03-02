#!/usr/bin/env python3
"""
BSCCS2003 Week-3 Lab Assignment.
Reads data.csv, accepts -s <student_id> or -c <course_id>, generates output.html
and (for course) a histogram image.
"""
import argparse
import csv
import os

# Use Agg backend for matplotlib to avoid display (file-only)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def normalize_key(key):
    return key.strip().lower().replace(' ', '')


def load_data():
    """Load data.csv from current directory. Returns list of (student_id, course_id, marks)."""
    path = 'data.csv'
    if not os.path.isfile(path):
        return []
    rows = []
    with open(path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if not header or len(header) < 3:
            return []
        # Map column indices by normalized header names
        col_map = {}
        for i, h in enumerate(header):
            n = normalize_key(h)
            if 'student' in n and 'id' in n:
                col_map['student_id'] = i
            elif 'course' in n and 'id' in n:
                col_map['course_id'] = i
            elif 'mark' in n:
                col_map['marks'] = i
        if len(col_map) != 3:
            # Fallback: assume order is Student id, Course id, Marks
            col_map = {'student_id': 0, 'course_id': 1, 'marks': 2}
        for row in reader:
            if len(row) < 3:
                continue
            try:
                sid = str(row[col_map['student_id']]).strip()
                cid = str(row[col_map['course_id']]).strip()
                marks = float(row[col_map['marks']])
                rows.append((sid, cid, marks))
            except (ValueError, IndexError, KeyError):
                continue
    return rows


def write_error_html():
    """Write output.html for invalid input: Wrong Inputs, Something went wrong, no table, no image."""
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Wrong Inputs</title>
</head>
<body>
<h1>Wrong Inputs</h1>
<p>Something went wrong</p>
</body>
</html>'''
    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(html)


def write_student_html(rows, student_id):
    """Write output.html for valid student: table with Student id, Course id, Marks and total."""
    total = int(sum(r[2] for r in rows))
    th = '<th>Student id</th><th>Course id</th><th>Marks</th>'
    trs = []
    for sid, cid, marks in rows:
        m = int(marks) if marks == int(marks) else marks
        trs.append(f'<tr><td>{sid}</td><td>{cid}</td><td>{m}</td></tr>')
    trs.append(f'<tr><td>Total Marks</td><td></td><td>{total}</td></tr>')
    table_rows = '\n'.join(trs)
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Student Details</title>
</head>
<body>
<h1>Student Details</h1>
<table>
<thead>
<tr>{th}</tr>
</thead>
<tbody>
{table_rows}
</tbody>
</table>
</body>
</html>'''
    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(html)


def write_course_html(avg_marks, max_marks, image_filename):
    """Write output.html for valid course: table Average Marks, Maximum Marks and histogram image."""
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Course Details</title>
</head>
<body>
<h1>Course Details</h1>
<table>
<thead>
<tr><th>Average Marks</th><th>Maximum Marks</th></tr>
</thead>
<tbody>
<tr><td>{avg_marks}</td><td>{max_marks}</td></tr>
</tbody>
</table>
<img src="{image_filename}" alt="Marks histogram">
</body>
</html>'''
    with open('output.html', 'w', encoding='utf-8') as f:
        f.write(html)


def create_histogram(marks_list, filename='histogram.png'):
    """Create and save a histogram of marks."""
    if not marks_list:
        return
    plt.figure()
    plt.hist(marks_list, bins=10, edgecolor='black', alpha=0.7)
    plt.xlabel('Marks')
    plt.ylabel('Frequency')
    plt.title('Marks Distribution')
    plt.savefig(filename)
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-s', dest='student_id', metavar='STUDENT_ID', help='Student ID')
    group.add_argument('-c', dest='course_id', metavar='COURSE_ID', help='Course ID')
    args = parser.parse_args()

    data = load_data()
    if not data:
        write_error_html()
        return

    if args.student_id is not None:
        sid = str(args.student_id).strip()
        student_rows = [r for r in data if r[0] == sid]
        if not student_rows:
            write_error_html()
            return
        write_student_html(student_rows, sid)
        return

    if args.course_id is not None:
        cid = str(args.course_id).strip()
        course_rows = [r for r in data if r[1] == cid]
        if not course_rows:
            write_error_html()
            return
        marks_list = [r[2] for r in course_rows]
        avg_marks = round(sum(marks_list) / len(marks_list), 1)
        max_marks = int(max(marks_list))
        image_name = 'histogram.png'
        create_histogram(marks_list, image_name)
        write_course_html(avg_marks, max_marks, image_name)
        return


if __name__ == '__main__':
    main()
