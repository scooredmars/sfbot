from .models import Bots, User
from django import forms
from allauth.account.forms import SignupForm
from django.http import HttpResponseRedirect


class UserSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, label="First Name")
    last_name = forms.CharField(max_length=30, label="Last Name")

    def __init__(self, *args, **kwargs):
        super(UserSignupForm, self).__init__(*args, **kwargs)
        self.fields["first_name"].widget.attrs.update(
            {"name": "first_name",
                "pattern": "[a-zA-Z]*", "placeholder": "First Name"}
        )
        self.fields["last_name"].widget.attrs.update(
            {"name": "last_name",
                "pattern": "[a-zA-Z]*", "placeholder": "Last Name"}
        )

    def signup(self, request, user):
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()


class AddBotForm(forms.ModelForm):
    class Meta:
        model = Bots
        fields = ("username", "password", "country", "server")
        widgets = {
            "password": forms.PasswordInput(),
        }

    def __init__(self, *args, **kwargs):
        super(AddBotForm, self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update(
            {"placeholder": "Username"})
        self.fields["password"].widget.attrs.update(
            {"placeholder": "Password"})
        self.fields["country"].widget.attrs.update({"class": "country-input"})
        self.fields["server"].widget.attrs.update({"class": "server-input"})

    def clean(self, *args, **keyargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        server = self.cleaned_data.get("server")

        sf_username = Bots.objects.filter(username=username)
        country = Bots.objects.filter(server=server)
        if sf_username.exists():
            if country.exists():
                raise forms.ValidationError(
                    "An account with this username already exists on this server"
                )
        if len(password) < 5:
            raise forms.ValidationError("Password is too short")
        if len(password) > 30:
            raise forms.ValidationError("Password is too long")

        return super(AddBotForm, self).clean(*args, **keyargs)


class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def __init__(self, *args, **kwargs):
        super(UserSettingsForm, self).__init__(*args, **kwargs)
        self.fields['username'].required = False

    def clean(self, *args, **keyargs):
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")

        username = User.objects.exclude(
            pk=self.instance.pk).filter(username=username)
        email = User.objects.exclude(pk=self.instance.pk).filter(email=email)
        if not username:
            if username:
                if len(username) < 10:
                    raise forms.ValidationError('This username is too short.')
                elif len(username) > 25:
                    raise forms.ValidationError('This username is too long.')
        else:
            raise forms.ValidationError(
                'This username is already in use. Please supply a different username.')
        if email:
            raise forms.ValidationError(
                'This email is already in use. Please supply a different email.')

        return super(UserSettingsForm, self).clean(*args, **keyargs)


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Bots
        fields = (
            "status",
            "tavern_status",
            "tavern_settings",
            "arena_status",
            "arena_settings",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].widget.attrs.update(
            {"class": "onoffswitch-checkbox"})
        self.fields["tavern_status"].widget.attrs.update(
            {"class": "onoffswitch-checkbox"}
        )
        self.fields["arena_status"].widget.attrs.update(
            {"class": "onoffswitch-checkbox"}
        )

    def save(self, commit=True):
        status = self.cleaned_data.get("status")
        bot_data = super(SettingsForm, self).save(commit=False)
        if commit:
            if status == True:
                bot_data.start = timezone.now()
                bot_data.save()
                if bot_data.profile.plan.name != "PREMIUM":
                    if str(bot_data.time_left) != "00:00:00":
                        # calculate data bot stop
                        time_left_str = str(bot_data.time_left)
                        date_time = datetime.datetime.strptime(
                            time_left_str, "%H:%M:%S"
                        )
                        time_left = date_time - datetime.datetime(1900, 1, 1)
                        seconds = time_left.total_seconds()
                        stop_time = bot_data.start + \
                            datetime.timedelta(0, seconds)
                        bot_data.stop = stop_time
                        bot_data.save()
            elif status == False:
                bot_data.start = None
                if bot_data.profile.plan.name != "PREMIUM":
                    bot_data.stop = None
                bot_data.save()
        return bot_data


class EditBotForm(forms.ModelForm):
    class Meta:
        model = Bots
        fields = ("username", "password", "country", "server")

    def __init__(self, *args, **kwargs):
        # get pk value from views and set them to request
        self.request = kwargs.pop("pk", None)
        super(EditBotForm, self).__init__(*args, **kwargs)

    def clean(self, *args, **keyargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        server = self.cleaned_data.get("server")

        username_change = Bots.objects.filter(username=username)

        if username_change.exists():
            bot_server_qs = Bots.objects.filter(
                server=server).filter(username=username)

            # Assignment pk value from request to variable.
            session_pk = self.request
            currnet_bot = Bots.objects.filter(username=username).only("id")
            for bot_data in currnet_bot:
                data = bot_data
            if (
                (data.username == username)
                & (data.password == password)
                & (data.server == server)
            ):
                return HttpResponseRedirect("dashboard")
            elif data.server != server:
                if bot_server_qs.exists():
                    bot_server_data = Bots.objects.filter(server=server).get(
                        username=username
                    )
                    if bot_server_data in bot_server_qs:
                        raise forms.ValidationError(
                            "An account with this username already exists on this server"
                        )
            elif data.password != password:
                if len(password) < 5:
                    raise forms.ValidationError("Password is too short")
                if len(password) > 30:
                    raise forms.ValidationError("Password is too long")
                if (data.username == username) and (data.id != session_pk):
                    raise forms.ValidationError(
                        "An account with this username already exists on this server"
                    )

        if len(password) < 5:
            raise forms.ValidationError("Password is too short")
        if len(password) > 30:
            raise forms.ValidationError("Password is too long")

        return super(EditBotForm, self).clean(*args, **keyargs)
