import json,re,tempfile,sys
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import desktop_app as d
import localization as loc

def has_chinese(text):return bool(re.search('[\u4e00-\u9fff]',text))

with tempfile.TemporaryDirectory() as tmp:
    root=Path(tmp);data=root/'personal_data'
    with patch.object(d,'HOME',root),patch.object(d,'DATA',data),patch.object(d.core,'BASE',root):
        app=d.App();app.withdraw()
        app.open_path(Path(__file__).resolve().parents[1]/'examples/sample.csv')
        app.tree.selection_set('0');app.select();app.update()
        assert app.language_choice.get()=='English'
        assert not has_chinese(app.title())
        assert app.tabs.tab(0,'text')=='Record details'
        assert not has_chinese(app.status.get())
        pending=[app]
        while pending:
            widget=pending.pop();pending.extend(widget.winfo_children())
            if 'text' in widget.keys():
                assert not has_chinese(str(widget.cget('text'))),widget.cget('text')
        app.vars['researcher_name'].set('王 Test')
        app.vars['researcher_email'].set('test@example.org')
        app.tabs.select(1)
        app.language_choice.set('中文');app.switch_language();app.update()
        assert app.tabs.tab(0,'text')=='收件人和研究信息'
        assert app.vars['researcher_name'].get()=='王 Test'
        assert app.tree.selection()==('0',)
        assert app.tabs.index(app.tabs.select())==1
        assert json.loads((data/'settings.json').read_text(encoding='utf-8'))['language']=='zh'
        assert 'Dear 王 Test' in app.preview.get('1.0','end')
        app.language_choice.set('English');app.switch_language();app.update()
        assert app.tabs.tab(0,'text')=='Record details'
        assert app.rows[0]['researcher_name']=='王 Test'
        assert not has_chinese(app.detail_status.cget('text'))
        app.destroy()
        app=d.App();app.withdraw()
        assert app.language_choice.get()=='English'
        app.language_choice.set('中文');app.switch_language();app.destroy()
        app=d.App();app.withdraw()
        assert app.language_choice.get()=='中文'
        app.destroy()
loc.set_language('en')
for text in [
    '邮箱查找完成：处理 3 条，其中 1 条读取失败。请查看“邮箱来源与候选”，核对后再发送。',
    '将从 person@example.org 发送 3 封邮件。\n\n请先在右侧预览内容。现在发送？',
    '网站拒绝访问或限流（HTTP 403）。\n页面：https://researchportalplus.anu.edu.au/en/projects/test/',
    '邮箱查找中断，已完成 3 条并保留结果。\n网页读取失败：https://researchportalplus.anu.edu.au/en/projects/test/\n\n详细记录：test.log'
]:assert not has_chinese(loc.tr(text)),loc.tr(text)
print('Language checks passed: English defaults, all main labels, switching, unsaved edits, selection, English email, persisted preference and dynamic messages.')
