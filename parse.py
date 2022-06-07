#! /usr/bin/python3

import re, json, sys

FREQ_ENTRY_REGEX_1 = re.compile(
    '\s*Frequenzteilplan:\s*(?P<Frequenzteilplan>\S+)'
    '\s*Eintrag:\s*(?P<Eintrag>\S+).*\n\n'
    '\s*Frequenzbereich:\s*(?P<Frequenzbereich>.*)\n\n'
    '\s*Nutzungsbestimmung\(en\):\s*(?P<Nutzungsbestimmungen>.*)\n\n'
    '\s*Funkdienst:\s*(?P<Funkdienst>.*)\n\n'
    '\s*Nutzung:\s*(?P<Nutzung>.*)\n\n'
    '\s*Frequenznutzung:\s*(?P<Frequenznutzung>.*)\n\n'
   '\s*Frequenzteilbereich\(e\):\s*(?P<Frequenzteilbereiche>.*)\n\n\n'
    '\s*Frequenznutzungs-\s*(?P<Frequenznutzungsbedingungen_1>.*)\n'
    '\s*bedingungen:(?P<Frequenznutzungsbedingungen_2>[\s\S]*)\n\n\n'
)
FREQ_ENTRY_REGEX_2 = re.compile(
    '\s*Frequenzteilplan:\s*(?P<Frequenzteilplan>\S+)'
    '\s*Eintrag:\s*(?P<Eintrag>\S+).*\n\n'
    '\s*Frequenzbereich:\s*(?P<Frequenzbereich>.*)\n\n'
    '\s*Nutzungsbestimmung\(en\):\s*(?P<Nutzungsbestimmungen>.*)\n\n'
    '\s*(?P<Funkdienst_1>.*)\n'
    '\s*Funkdienst:\n'
    '\s*(?P<Funkdienst_2>.*)\n\n'
    '\s*Nutzung:\s*(?P<Nutzung>.*)\n\n'
    '\s*Frequenznutzung:\s*(?P<Frequenznutzung>.*)\n\n'
    '\s*Frequenzteilbereich\(e\):\s*(?P<Frequenzteilbereiche>.*)\n\n\n'
    '\s*Frequenznutzungs-\s*(?P<Frequenznutzungsbedingungen_1>.*)\n'
    '\s*bedingungen:(?P<Frequenznutzungsbedingungen_2>[\s\S]*)\n\n\n'
)

input = sys.argv[1] if len(sys.argv) > 1 else 'Frequenzplan.txt'
output = sys.argv[2] if len(sys.argv) > 1 else 'html/data.json'

txt = re.sub('\x0c© Bundesnetzagentur\s+Frequenzplan', '', open(input).read())

entries = []

for e in re.findall('Frequenzteilplan:.*?\n\n\n\n', txt, re.DOTALL):
    m = re.match(FREQ_ENTRY_REGEX_1, e) 
    if m:
        entry = m.groupdict()
    else:
        m = re.match(FREQ_ENTRY_REGEX_2, e)
        if m:
            entry = m.groupdict()
            entry['Funkdienst'] = '\n'.join( 
                    [l.lstrip() for l in (entry.pop('Funkdienst_1') + '\n' + entry.pop('Funkdienst_2')).splitlines()] )
        else:
            print(e)
            sys.exit(1)
    entry['Frequenznutzungsbedingungen'] = '\n'.join( 
            [l.lstrip() for l in (entry.pop('Frequenznutzungsbedingungen_1') + '\n' + entry.pop('Frequenznutzungsbedingungen_2')).splitlines()] )
    
    entries.append(entry)

json.dump({
    'data': entries },
    open(output, 'w'), separators=(',',':'))
