import sys,tempfile,queue,threading
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import desktop_app as d
class Fetch:
    def __init__(self,*args):pass
    def __enter__(self):return self
    def __exit__(self,*args):pass
def lookup(row,fetch):
    if row['id']==0:raise d.email_lookup.PageUnavailable('Timeout first project')
    return {'researcher_email':'public@example.org'}
with tempfile.TemporaryDirectory() as tmp:
    fake=SimpleNamespace(events=queue.Queue(),lookup_stop=threading.Event())
    with patch.object(d,'DATA',Path(tmp)),patch.object(d.email_lookup,'BrowserFetcher',Fetch),patch.object(d.email_lookup,'lookup',lookup):
        d.App.lookup_worker(fake,[(0,{'id':0}),(1,{'id':1})])
    messages=[]
    while not fake.events.empty():messages.append(fake.events.get())
    rows=[m[1] for m in messages if m[0]=='lookup_row']
    assert len(rows)==2 and rows[1][1]['researcher_email']=='public@example.org'
    assert messages[-1][0]=='ok'
    assert 'Timeout first project' in (Path(tmp)/'email_lookup.log').read_text(encoding='utf-8')
print('Batch continues after one failed project and logs the failed page; no browser or email used.')
