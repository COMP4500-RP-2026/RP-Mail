import sys,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import desktop_app as d

original=Path('examples/sample.csv').resolve()
with tempfile.TemporaryDirectory() as tmp:
    base=Path(tmp);data=base/'personal_data'
    with patch.object(d,'HOME',base),patch.object(d,'DATA',data),patch.object(d.core,'BASE',base):
        app=d.App()
        app.open_path(original)
        app.update()
        assert len(app.rows)==1
        app.tree.selection_set('0');app.select();app.update()
        assert 'personal capacity' in app.preview.get('1.0','end')
        assert 'We are reviewing' not in app.preview.get('1.0','end')
        app.vars['researcher_name'].set('Test Researcher')
        app.vars['researcher_email'].set('test@example.org')
        app.vars['project_name'].set('Example Project')
        app.vars['suggestion_reason'].set('Verified grant reference.')
        app.reviewed.set(True);app.mark_dirty();app.save_current();app.update()
        assert app.row_status(app.rows[0])=='可发送'
        app.settings.update(sender_name='Personal Sender',sender_email='person@example.org')
        app.render_preview()
        assert 'Kind regards,\nPersonal Sender' in app.preview.get('1.0','end')
        fields,rows,_=d.load_table(data/'mailing_list.csv')
        assert rows[0]['researcher_email']=='test@example.org'
        app.set_filter('可发送');app.update()
        assert len(app.tree.get_children())==1
        app.set_filter('全部记录');app.update()
        assert 'email_source_url' in app.fields
        import json
        candidate=dict(name='Selected Person',email='selected@example.org',source_url='https://researchportalplus.anu.edu.au/en/persons/selected/',basis='项目成员')
        app.rows[0]['email_candidates']=json.dumps([candidate])
        app.render_preview()
        app.contact_tree.selection_set('0');app.use_contact();app.update()
        assert app.rows[0]['researcher_email']=='selected@example.org'
        assert app.rows[0]['reviewed']==''
        assert app.rows[0]['email_source_url']==candidate['source_url']
        assert len(app.tabs.tabs())==3
        assert app.stop_button['state'].string=='disabled'
        app.destroy()
print('Desktop import, personal template, editing, persistence and filtering passed. No emails sent.')
