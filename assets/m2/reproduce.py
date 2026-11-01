"""Recalculate the quantitative SFA M2 snapshot. Python 3; no dependencies.
Keep survey-coded.json next to this file and run: python3 reproduce.py
Qualitative theme assignments are interpretive and documented in research-notes.html.
"""
from pathlib import Path
from collections import Counter
import json

data = json.loads(Path(__file__).with_name('survey-coded.json').read_text(encoding='utf-8'))
rows = [r for r in data['rows'] if r['cohort'] == 'main_102']
recent_values = {'O dată', 'De 2–3 ori', 'De 4 ori sau mai mult'}
repeat_values = {'De 2–3 ori', 'De 4 ori sau mai mult'}
multi_values = {'Doi', 'Trei', 'Patru sau mai mulți'}
slow_values = {'6–15 minute', '16–30 de minute', 'Mai mult de 30 de minute'}
easy_values = {'Foarte ușor', 'Mai degrabă ușor'}
recent = [r for r in rows if r['E'] in recent_values]
multi = [r for r in rows if r['C'] in multi_values]
both = [r for r in multi if r['E'] in recent_values]
repeated = [r for r in both if r['E'] in repeat_values]
repeated_slow = [r for r in repeated if r['H'] in slow_values]

def fraction(n, d): return {'count': n, 'base': d, 'percent': round(n/d*100, 1) if d else None}
def count(rs, key): return dict(Counter(r[key] for r in rs))
def group(rs):
    rr = [r for r in rs if r['E'] in recent_values]
    return {'n':len(rs), 'frequency':count(rs,'E'), 'connections':count(rs,'L'),
            'recent_n':len(rr), 'recent_time':count(rr,'H'), 'recent_difficulty':count(rr,'I'),
            'recent_methods':{label:sum(option in r['G_selected_options'] for r in rr) for label,option in data['method_options'].items()},
            'recent_other_method':sum(r['G_other_present'] for r in rr)}

result = {
 'main_n':len(rows),
 'multi_service':fraction(len(multi),len(rows)),
 'any_recent':fraction(len(recent),len(rows)),
 'recent_among_multi':fraction(len(both),len(multi)),
 'repeated_among_recent_multi':fraction(len(repeated),len(both)),
 'six_plus_minutes_among_recent_multi':fraction(sum(r['H'] in slow_values for r in both),len(both)),
 'easy_among_recent_multi':fraction(sum(r['I'] in easy_values for r in both),len(both)),
 'repeated_slow':fraction(len(repeated_slow),len(repeated)),
 'easy_within_repeated_slow':fraction(sum(r['I'] in easy_values for r in repeated_slow),len(repeated_slow)),
 'repeated_slow_ids':[r['id'] for r in repeated_slow],
 'final_question_classification':count(rows,'N_classification'),
 'all':group(rows), 'multi':group(multi),
 'by_bank_count':{k:group([r for r in rows if r['C']==k]) for k in ('Niciunul','Unul','Doi','Trei','Patru sau mai mulți')},
 'by_method_recent_multi':{label:{'n':len(g:=[r for r in both if option in r['G_selected_options']]),'slow':sum(r['H'] in slow_values for r in g),'easy':sum(r['I'] in easy_values for r in g),'connections':count(g,'L')} for label,option in data['method_options'].items()},
 'by_connection_recent_multi':{k:{'n':len(g:=[r for r in both if r['L']==k]),'slow':sum(r['H'] in slow_values for r in g),'easy':sum(r['I'] in easy_values for r in g)} for k in dict.fromkeys(r['L'] for r in rows)},
 'later_addition_ids':[r['id'] for r in data['rows'] if r['cohort']!='main_102']
}
print(json.dumps(result,ensure_ascii=False,indent=2))
