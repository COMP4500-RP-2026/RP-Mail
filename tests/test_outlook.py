import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import rp_mailer as m

config=dict(transport='outlook', sender_email='school@example.org', sender_name='Name', team_name='Team', initiative_name='Review', reply_to='reply@example.org')
row=dict(output_uuid='out1',project_uuid='proj1',researcher_email='researcher@example.org',researcher_name='Researcher',title='Title',project_name='Project',project_code='DP1',output_url='https://researchportalplus.anu.edu.au/en/publications/out1',suggestion_reason='Verified reason')
account=MagicMock()
account.SmtpAddress='school@example.org'
app=MagicMock()
app.Session.Accounts=[account]
client=MagicMock()
client.gencache.EnsureDispatch.return_value=app
with patch.dict(sys.modules, {'win32com':SimpleNamespace(client=client),'win32com.client':client}):
    m.validate_config(config, True)
    transport=m.connect(config)
    mail=account.DeliveryStore.GetDefaultFolder.return_value.Items.Add.return_value
    msg=m.message(row,config)
    transport.send_message(msg,from_addr=config['sender_email'],to_addrs=['self@example.org'],draft=True)
    mail.Save.assert_called_once()
    mail.Send.assert_not_called()
    assert mail.SendUsingAccount is account
    assert mail.To=='self@example.org'
    transport.send_message(msg,from_addr=config['sender_email'],to_addrs=[row['researcher_email']])
    mail.Send.assert_called_once()
    mail.ReplyRecipients.Add.assert_called_with('reply@example.org')
    mail.Recipients.ResolveAll.return_value=False
    try:
        transport.send_message(msg,from_addr=config['sender_email'],to_addrs=[row['researcher_email']])
        raise AssertionError('Expected unresolved recipient failure')
    except ValueError: pass
    assert mail.Send.call_count==1
    app.Session.Accounts=[]
    try:
        m.connect(config)
        raise AssertionError('Expected sender mismatch failure')
    except ValueError: pass
print('Outlook adapter checks passed; no actual Outlook accessed or messages sent.')

# Verify drafts reserve their production keys and cannot be sent twice.
import csv, json, tempfile
from contextlib import closing
import sqlite3
with tempfile.TemporaryDirectory() as d:
    base=Path(d)
    (base/'config.json').write_text(json.dumps(config))
    row.update(reviewed='yes', already_in_relations='FALSE')
    with (base/'data.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(row));w.writeheader();w.writerow(row)
    args=SimpleNamespace(command='draft',input=base/'data.csv',config=base/'config.json',output=base/'preview',limit=10)
    fake=MagicMock()
    with patch.object(m,'BASE',base),patch.object(m,'connect',return_value=fake),patch.object(m.time,'sleep'):
        m.run(args)
        assert fake.send_message.call_args.kwargs['draft'] is True
        with closing(sqlite3.connect(base/'send_history.sqlite3')) as db:
            assert db.execute('select status from history').fetchone()[0]=='drafted'
        args.command='send';m.run(args)
        assert fake.send_message.call_count==1
print('Draft history checks passed.')
