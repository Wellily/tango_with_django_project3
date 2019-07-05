from django import forms
from rango2.models import Page, Category, UserProfile
from django.contrib.auth.forms import User


class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=128, help_text="Please enter the category name.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name', )  # 设定表单中包含哪些字段，这里何为可以不要views字段


class PageForm(forms.ModelForm):
    title = forms.CharField(max_length=128, help_text="Please enter the title of the page.")
    url = forms.URLField(max_length=200, help_text="Please enter the URL of the page.")
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Page
        fields = ('title', 'url', 'views')

    def clean(self):
        clean_data = self.cleaned_data
        url = clean_data.get('url')
        if url and not url.startswith('http://'):
            url = 'http://' + url
            clean_data['url'] = url
            return clean_data


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())  # 使用这个小组件，密码不会直接渲染在HTML上

    class Meta:
        model = User
        fields = ('username', 'email', 'password')  # 表单显示的字段


class UserProfileForm(forms.ModelForm):
    website = forms.URLField(required=False)
    picture = forms.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
