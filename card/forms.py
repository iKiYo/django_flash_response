from django import forms


class CSVUploadFileForm(forms.Form):
    file = forms.FileField(label='ファイル参照',
                           help_text='※拡張子csvのファイルをアップロードしてください。')

