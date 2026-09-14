from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Quiz
from .models import Question, Choice


class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'instructions', 'passing_score']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'instructions': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'passing_score': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'order']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter the question text'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class BaseChoiceFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            # An individual choice form already has its own error —
            # don't pile a second, confusing error on top of it.
            return

        filled_count = 0
        correct_count = 0
        for form in self.forms:
            text = form.cleaned_data.get('text')
            is_correct = form.cleaned_data.get('is_correct')
            if text:
                filled_count += 1
            if is_correct:
                correct_count += 1

        if filled_count < 2:
            raise forms.ValidationError("A question needs at least 2 choices filled in.")
        if correct_count != 1:
            raise forms.ValidationError("Exactly one choice must be marked as correct.")


ChoiceFormSet = inlineformset_factory(
    Question,
    Choice,
    formset=BaseChoiceFormSet,
    fields=['text', 'is_correct'],
    extra=4,
    can_delete=False,
    widgets={
        'text': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choice text'}),
        'is_correct': forms.CheckboxInput(),
    }
)