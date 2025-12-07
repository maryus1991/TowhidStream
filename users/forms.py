from django import forms


class LoginForm(forms.Form):

    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder":"نام کاربری",
                "autocomplete": "username",
            }
        )
        
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder":"رمز عبور",
                "autocomplete": "password",
            }
        )
    )


class RegistrationForm(forms.Form):
    name = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder":"نام"
            }
        )
    )
    
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "placeholder":"نام کاربری"
            }
        )
    )
    
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder":"رمز عبور",
            }
        )
    )
    
    conform_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder":"تکرار رمز عبور",
            }
        )
    )
    
    
    
    def clean_conform_password(self):
        conform_password = self.cleaned_data["conform_password"]
        password = self.cleaned_data.get("password")

        if password and password != conform_password:

            raise forms.ValidationError("رمز عبور شما به صورت یکسان وارد نشده است")
        else:
            return conform_password

    def clean_password(self):
        password = self.cleaned_data["password"]
        if len(password) < 8:
            raise forms.ValidationError("رمز شما باید حداقل 8 کاراکتر باشد")

        if password.isdigit():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.isupper():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        if password.islower():
            raise forms.ValidationError(
                "رمز شما باید شامل حروف بزرگ و کوچک و اعداد انگلیسی باشد"
            )

        return password