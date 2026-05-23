import io
import mailbox
import os
import sys
import tempfile
from email.header import decode_header

# ensure the terminal can display UTF-8 characters (e.g. emoji in subjects)
if isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MBOX_PATH = os.path.join(os.path.dirname(__file__), 'dataset.mbox')
PAGE_SIZE = 20


def decode_str(s):
    if not s:
        return ''
    parts = decode_header(s)
    out = []
    for part, enc in parts:
        if isinstance(part, bytes):
            out.append(part.decode(enc or 'utf-8', errors='replace'))
        else:
            out.append(part)
    return ''.join(out)


def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain' and 'attachment' not in str(part.get('Content-Disposition', '')):
                charset = part.get_content_charset() or 'utf-8'
                try:
                    return part.get_payload(decode=True).decode(charset, errors='replace')
                except Exception:
                    pass
    else:
        charset = msg.get_content_charset() or 'utf-8'
        try:
            return msg.get_payload(decode=True).decode(charset, errors='replace')
        except Exception:
            return str(msg.get_payload())
    return ''


def load_index(path):
    print('Indexing emails (this may take a moment)...')
    mbox = mailbox.mbox(path)
    index = []
    for i, msg in enumerate(mbox):
        index.append({
            'i':       i,
            'from':    decode_str(msg.get('From', '')),
            'to':      decode_str(msg.get('To', '')),
            'subject': decode_str(msg.get('Subject', '(no subject)')),
            'date':    msg.get('Date', ''),
        })
        if (i + 1) % 1000 == 0:
            print(f'  {i + 1} indexed...', end='\r', flush=True)
    print(f'  {len(index)} emails ready.        ')
    return mbox, index


def search(index, query):
    q = query.lower()
    return [e for e in index if
            q in e['from'].lower() or
            q in e['subject'].lower() or
            q in e['to'].lower() or
            q in e['date'].lower()]


def show_page(results, page):
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(results))
    total_pages = max(1, (len(results) + PAGE_SIZE - 1) // PAGE_SIZE)
    print(f'\n  {"#":>5}  {"Date":<22}  {"From":<30}  Subject')
    print('  ' + '-' * 90)
    for rank, e in enumerate(results[start:end], start=start + 1):
        date = e['date'][:20] if e['date'] else ''
        frm  = e['from'][:28] + '..' if len(e['from']) > 30 else e['from']
        subj = e['subject'][:45] + '..' if len(e['subject']) > 47 else e['subject']
        print(f"  {rank:>5}  {date:<22}  {frm:<30}  {subj}")
    print(f'\n  Page {page + 1}/{total_pages}  |  results {start + 1}-{end} of {len(results)}')


def open_email(mbox, entry):
    msg = mbox[entry['i']]
    body = get_body(msg)
    content = (
        f"From:    {entry['from']}\n"
        f"To:      {entry['to']}\n"
        f"Date:    {entry['date']}\n"
        f"Subject: {entry['subject']}\n"
        f"\n{'=' * 72}\n\n"
        f"{body}"
    )
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8')
    tmp.write(content)
    tmp.close()
    os.startfile(tmp.name)
    print(f'  Opened: {tmp.name}')


def main():
    mbox, index = load_index(MBOX_PATH)
    results = index
    page = 0

    print('\nCommands:  [number] open email  |  s  search  |  n  next page  |  p  prev page  |  r  reset  |  q  quit\n')

    while True:
        show_page(results, page)
        total_pages = max(1, (len(results) + PAGE_SIZE - 1) // PAGE_SIZE)

        try:
            cmd = input('\n> ').strip()
        except (EOFError, KeyboardInterrupt):
            print('\nBye!')
            break

        if cmd.lower() == 'q':
            print('Bye!')
            break
        elif cmd.lower() == 'n':
            if page < total_pages - 1:
                page += 1
            else:
                print('  Already on last page.')
        elif cmd.lower() == 'p':
            if page > 0:
                page -= 1
            else:
                print('  Already on first page.')
        elif cmd.lower() == 'r':
            results = index
            page = 0
            print(f'  Showing all {len(index)} emails.')
        elif cmd.lower() == 's':
            query = input('  Search query: ').strip()
            if query:
                results = search(index, query)
                page = 0
                print(f'  Found {len(results)} match(es) for "{query}".')
            else:
                print('  (empty query, keeping current results)')
        elif cmd.isdigit():
            rank = int(cmd) - 1
            if 0 <= rank < len(results):
                open_email(mbox, results[rank])
            else:
                print(f'  Invalid number. Enter 1–{len(results)}.')
        else:
            print('  Unknown command.')


if __name__ == '__main__':
    main()
