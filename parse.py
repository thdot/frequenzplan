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
    'Frequenzbereich:\s*(?P<Frequenzbereich>'
        '(?P<Frequenzbereich_Start>[\d,\.]+)\s*-\s*'
        '(?P<Frequenzbereich_Ende>[\d,\.]+) '
        '(?P<Frequenzbereich_Einheit>kHz|MHz|GHz))\n'
    'Nutzungsbestimmung\(en\):\s*(?P<Nutzungsbestimmungen>.*)\n'
    'Funkdienst:\s*(?P<Funkdienst>[\s\S]*)\n'
    'Nutzung:\s*(?P<Nutzung>.*)\n'
    'Frequenznutzung:\s*(?P<Frequenznutzung>.*)\n'
    'Frequenzteilbereich\(e\):\s*(?P<Frequenzteilbereiche>'
        '(?P<Frequenzteilbereiche_Start>[\d,\.]+)\s*-\s*'
        '(?P<Frequenzteilbereiche_Ende>[\d,\.]+) '
        '(?P<Frequenzteilbereiche_Einheit>kHz|MHz|GHz))\n'
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

def convert_freq_to_hz(freq, unit):
    FREQ_TO_HZ = {
        'kHz': 1000,
        'MHz': 1000 * 1000,
        'GHz': 1000 * 1000 * 1000
    }
    return int(float(freq.replace(',', '.')) * FREQ_TO_HZ[unit])

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
        for attr in ('Frequenzbereich', 'Frequenzteilbereiche'):
            entry[attr + '_Start'] = convert_freq_to_hz(entry[attr + '_Start'], entry[attr + '_Einheit'])
            entry[attr + '_Ende'] = convert_freq_to_hz(entry[attr + '_Ende'], entry[attr + '_Einheit'])
            entry.pop(attr + '_Einheit')
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
