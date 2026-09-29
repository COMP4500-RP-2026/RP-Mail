import sys,json,threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import email_lookup as e

root='https://researchportalplus.anu.edu.au'
project=root+'/en/projects/example/'
output=root+'/en/publications/example/'
a=root+'/en/persons/alice/'
b=root+'/en/persons/bob/'
html='<section class="introduction"><h1>Example Project</h1><ul class="relations persons"><li><a href="'+a+'">Example, Alice</a><span> (PI)</span></li><li><a href="'+b+'">Example, Bob</a><span> (CoI)</span></li><li>External Name (CoI)</li></ul></section><footer><a href="/en/persons/irrelevant/">Other person</a></footer>'
profile='<section class="profile"><h1>Alice</h1><a class="email" href="#">alice<span class="email-ta">@</span><script>encryptedA();</script>example<span class="email-tod">.</span><script>encryptedDot();</script>org</a></section><footer><a href="mailto:wrong@example.org">Contact admin</a></footer>'
pages={project:html,output:'<div class="introduction"><ul class="relations persons"><li><a href="'+b+'">Bob Example</a></li></ul></div>',a:profile,b:profile.replace('alice','bob')}
row=dict(project_url=project,output_url=output)
assert len(e.people(html,project))==2
assert e.profile_emails(profile)==['alice@example.org']
assert e.profile_emails('<section class="profile">No public email</section>')==[]
assert e.profile_emails('<footer><a href="mailto:admin@example.org">Admin</a></footer>')==[]
result=e.lookup(row,pages.__getitem__)
assert result['researcher_name']=='Bob Example'
assert result['researcher_email']=='bob@example.org'
assert len(json.loads(result['email_candidates']))==2
assert 'possible connection' in result['suggestion_reason']
filled=e.merge_result(row,result)
assert filled['reviewed']==''
assert filled['email_source_url']==b
manual=e.merge_result(dict(row,researcher_email='manual@example.org',researcher_name='Manual',project_name='Existing'),result)
assert manual['researcher_email']=='manual@example.org' and manual['project_name']=='Existing'
assert not manual.get('email_source_url')
for url in ['http://researchportalplus.anu.edu.au/en/projects/x','https://attacker.example/en/projects/x','https://researchportalplus.anu.edu.au@localhost/en/projects/x','https://researchportalplus.anu.edu.au/en/persons/']:
    if url.endswith('/en/persons/'):continue
    try:e.canonical(url);raise AssertionError('URL accepted')
    except ValueError:pass
stop=threading.Event();stop.set()
try:e.BrowserFetcher(stop)(project);raise AssertionError('Cancellation ignored')
except e.LookupStopped:pass
# A blocked project must not generate a candidate or an invented address.
def blocked(url):raise RuntimeError('HTTP 403')
try:e.lookup(row,blocked);raise AssertionError('Failure was hidden')
except RuntimeError:pass
assert e.lookup(row,lambda _: '<section class="introduction"><h1>Project</h1><ul class="relations persons"><li>No public profile</li></ul></section>')['email_candidates']=='[]'
print('Lookup tests passed: source scoping, email extraction, author ranking, preserved edits, missing data, errors and cancellation.')

def partial(url):
    if url==output:raise e.PageUnavailable('404 publication')
    if url==a:raise e.PageUnavailable('Timeout profile')
    return pages[url]
partial_result=e.lookup(row,partial)
assert partial_result['researcher_email']=='bob@example.org'
assert 'suggestion_reason' not in partial_result
assert json.loads(partial_result['email_candidates'])[0]['rank']==0
assert '404 publication' in partial_result['email_lookup_warnings']
assert 'Timeout profile' in partial_result['email_lookup_warnings']
def denied(url):
    if url==output:raise e.LookupFatal('HTTP 403')
    return pages[url]
try:e.lookup(row,denied);raise AssertionError('Access denial ignored')
except e.LookupFatal:pass
prior=dict(filled,email_candidates='[{"email":"known@example.org"}]')
retained=e.merge_result(prior,{'email_lookup_status':'失败','email_lookup_warnings':'Timeout'})
assert retained['email_candidates']==prior['email_candidates']
assert retained['email_source_url']==prior['email_source_url']
print('Recovery checks passed: partial results retained; no false author match; access denial stops; existing evidence preserved.')
