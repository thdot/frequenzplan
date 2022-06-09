#! /usr/bin/python3

import re, json, sys, subprocess

SUB_REGEXS = (
    '\x0c',
    '© Bundesnetzagentur\s+Frequenzplan\n',
    '© Bundesnetzagentur',
    'Seite \d+ von \d+',
    'Stand: \w+ \d+'
)
FREQ_ENTRY_REGEX = re.compile(
    'Frequenzteilplan:\s*(?P<Frequenzteilplan>\S+)\s+'
    'Eintrag:\s*(?P<Eintrag>\S+).*\n'
    'Frequenzbereich:\s*(?P<Frequenzbereich>.*)\n'
    'Nutzungsbestimmung\(en\):\s*(?P<Nutzungsbestimmungen>.*)\n'
    'Funkdienst:\s*(?P<Funkdienst>[\s\S]*)\n'
    'Nutzung:\s*(?P<Nutzung>.*)\n'
    'Frequenznutzung:\s*(?P<Frequenznutzung>.*)\n'
    'Frequenzteilbereich\(e\):\s*(?P<Frequenzteilbereiche>.*)\n'
    'Frequenznutzungs-\nbedingungen:\s*(?P<Frequenznutzungsbedingungen>[\s\S]*)\n'
)
TERMS_OF_USE_REGEX = re.compile(
    '(?s)'
    '.*\n\s*Teil B: Nutzungsbestimmungen\s\n'
    '([\s\S]+)'
    '\n\s*Abkürzungsverzeichnis\s*\n'
)
TERM_REGEX = re.compile(
    '(?s)'
    '\n*([A-Z0-9]+)\s+(.+?)\n\n'
)


def get_pdf_as_txt(input, mode):
    txt = subprocess.run(['pdftotext', mode, input, '-'],
            check=True, stdout=subprocess.PIPE).stdout.decode('utf-8')
    for r in SUB_REGEXS:
        txt = re.sub(r, '', txt)
    return txt

def parse(input, output):
    txt = get_pdf_as_txt(input, '-raw')
    txt = re.sub('\nFrequenzteilplan:', '\n\nFrequenzteilplan:', txt)
    entries = []
    for e in re.findall('Frequenzteilplan:.*?\n\n', txt, re.DOTALL):
        m = re.match(FREQ_ENTRY_REGEX, e)
        if not m:
            print(e)
            sys.exit(1)
        entry = m.groupdict()
        entries.append(entry)

    txt = get_pdf_as_txt(input, '-layout')
    terms_of_use = {}
    for t in re.findall(TERM_REGEX, re.match(TERMS_OF_USE_REGEX, txt).group(1)):
        terms_of_use[t[0]] = '\n'.join( [l.lstrip() for l in t[1].splitlines()] )

    json.dump({
            'entries': entries,
            'terms_of_use': terms_of_use },
        open(output, 'w'), separators=(',',':'), indent=2)


if __name__ == '__main__':
    input = sys.argv[1] if len(sys.argv) > 1 else 'Frequenzplan.pdf'
    output = sys.argv[2] if len(sys.argv) > 2 else 'html/data.json'
    parse(input, output)
