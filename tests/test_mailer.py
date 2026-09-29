import sys, tempfile, csv, json, sqlite3
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rp_mailer as m

class FakeSMTP:
    def __init__(self, fail=False): self.messages=[]; self.fail=fail
    def send_message(self, msg, **kwargs):
        self.messages.append((msg, kwargs))
        if self.fail: raise TimeoutError('simulated')
    def close(self): pass
    def __enter__(self): return self
    def __exit__(self, *args): pass

with tempfile.TemporaryDirectory() as directory:
    base=Path(directory)
    c=dict(sender_email='sender@example.org', sender_name='Research Team', team_name='Team', initiative_name='RP review', reply_to='reply@example.org')
    (base/'config.json').write_text(json.dumps(c))
    r=dict(output_uuid='o1', project_uuid='p1', title='A study', output_url='https://researchportalplus.anu.edu.au/en/publications/o1', project_code='DP1', already_in_relations='FALSE', researcher_name='Example', researcher_email='researcher@example.org', project_name='Project One', suggestion_reason='The grant ID was verified in the acknowledgement.', reviewed='yes')
    assert not m.validate(r)
    assert m.validate(dict(r, researcher_email='a@example.org,b@example.org'))
    assert m.validate(dict(r, already_in_relations='TRUE'))
    assert m.validate(dict(r, reviewed=''))
    msg=m.message(r,c)
    assert 'Not my research output' in msg.get_content()
    assert 'Not available in the current dataset' in msg.get_content()
    assert msg['Reply-To']=='reply@example.org'
    rows=[r,r,dict(r,output_uuid='o2'),dict(r,output_uuid='o3',reviewed='')]
    source=base/'input.csv'
    with source.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(r));w.writeheader();w.writerows(rows)
    args=SimpleNamespace(command='preview',input=source,config=base/'config.json',output=base/'preview',limit=1,to='self@example.org')
    m.run(args)
    assert len(list((base/'preview').glob('*.eml')))==2
    smtp=FakeSMTP()
    with patch.object(m,'BASE',base), patch.object(m,'validate_config'), patch.object(m,'connect',return_value=smtp), patch.object(m.time,'sleep'):
        args.command='test';m.run(args)
        assert smtp.messages[-1][1]['to_addrs']==['self@example.org']
        assert smtp.messages[-1][0]['To']=='self@example.org'
        assert not (base/'send_history.sqlite3').exists()
        args.command='send';m.run(args);assert len(smtp.messages)==2
        m.run(args);assert len(smtp.messages)==3
        m.run(args);assert len(smtp.messages)==3
        with closing(sqlite3.connect(base/'send_history.sqlite3')) as db:
            assert db.execute('select count(*) from history where status="accepted"').fetchone()[0]==2
            db.execute('delete from history');db.commit()
        smtp.fail=True
        try: m.run(args);raise AssertionError('Expected failure')
        except RuntimeError: pass
        with closing(sqlite3.connect(base/'send_history.sqlite3')) as db:
            assert db.execute('select status from history').fetchone()[0]=='uncertain'
        smtp.fail=False
        m.run(args)
        count=len(smtp.messages);m.run(args);assert len(smtp.messages)==count
print('All local checks passed; no network calls or real emails.')
