from django import forms

from .models import Product, Comment


class CommentForm(forms.Form):
    text = forms.CharField(max_length=500, widget=forms.Textarea(attrs={"rows": '2', 'cols': "50"}))
    product = forms.IntegerField(widget=forms.HiddenInput)
    slug = forms.CharField(widget=forms.HiddenInput)

    def clean_product(self):
        product_id = self.cleaned_data['product']
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            product = None
        return product

    def clean_text(self):
        text = self.cleaned_data['text']
        if text.strip() == '':
            raise forms.ValidationError(
                u'Text is empty', code='validation_error')
        return text

    def save(self):
        self.cleaned_data['author'] = self._user
        self.cleaned_data.pop('slug')
        answer = Comment(**self.cleaned_data)
        answer.save()
        return answer
