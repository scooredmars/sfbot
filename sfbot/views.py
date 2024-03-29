from .models import Bots, FaqList, PageGenerator, Plan, Profile, User, PermissionList, Currency, Orders
from .forms import AddBotForm, UserSettingsForm, SettingsForm, EditBotForm
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.utils import timezone
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from django.views.generic.detail import DetailView
from allauth.account.views import PasswordChangeView
from datetime import timedelta
import json


def error_404(request, exception):
    return render(request, "404.html")


def error_500(request):
    return render(request, "404.html")


def home_view(request):
    plans = Plan.objects.all()
    users = User.objects.all().count()
    bots = Bots.objects.all().count()
    working_bots = Bots.objects.filter(status=True).count()
    plan_list = Plan.objects.all()
    permission_list = PermissionList.objects.all()

    if not permission_list:
        w_6 = PermissionList(name="6h", icon="check icon",
                             description="Bot works 6h per day")
        w_6.save()
        m_1 = PermissionList(name="1bot", icon="check icon",
                             description="Max 1 bot")
        m_1.save()
        w_12_n = PermissionList(
            name="12h no", icon="times icon", description="Bot works 12h per day")
        w_12_n.save()
        m_3_n = PermissionList(
            name="3bots no", icon="times icon", description="Max 3 bots")
        m_3_n.save()
        w_12_y = PermissionList(
            name="12h yes", icon="check icon", description="Bot works 12h per day")
        w_12_y.save()
        m_3_y = PermissionList(
            name="3bots yes", icon="check icon", description="Max 3 bots")
        m_3_y.save()
        w_24_n = PermissionList(
            name="24h no", icon="times icon", description="Bot works all the time")
        w_24_n.save()
        m_5_n = PermissionList(
            name="5bots no", icon="times icon", description="Max 5 bot")
        m_5_n.save()
        w_24_y = PermissionList(
            name="24h yes", icon="check icon", description="Bot works all the time")
        w_24_y.save()
        m_5_y = PermissionList(
            name="5bots yes", icon="check icon", description="Max 5 bot")
        m_5_y.save()
    if not plan_list:
        starter = Plan(name="STARTER", price="0", max_time="6", max_bots="1")
        starter.save()
        starter.permission_list.add(w_6, m_1, w_12_n, m_3_n, w_24_n, m_5_n)

        standard = Plan(name="STANDARD", price="4",
                        special_style="best", max_time="12", max_bots="3")
        standard.save()
        standard.permission_list.add(w_6, m_1, w_12_y, m_3_y, w_24_n, m_5_n)

        premium = Plan(name="PREMIUM", price="8", max_time="24", max_bots="5")
        premium.save()
        premium.permission_list.add(w_6, m_1, w_12_y, m_3_y, w_24_y, m_5_y)

    context = {
        "plans": plans,
        "users": users,
        "bots": bots,
        "working_bots": working_bots,
    }
    return render(request, "home.html", context)


def dashboard_view(request):
    # Dashboard
    all_bots = Bots.objects.all()
    user_bots = all_bots.filter(profile__user=request.user)
    user_profile_qs = Profile.objects.filter(user=request.user)

    if not user_profile_qs:
        starter_plan = Plan.objects.get(name="STARTER")
        create_user_profile = Profile(
            user=request.user, plan=starter_plan, create_account=timezone.now(), plan_start_date=timezone.now())
        create_user_profile.save()

    amount_user_bots = user_bots.count()
    user_profile = Profile.objects.get(user=request.user)
    current_plan = Plan.objects.get(profile=user_profile)
    lock_add = False
    if amount_user_bots >= current_plan.max_bots:
        lock_add = True

    # Add Bot
    form = AddBotForm()
    if request.method == "POST":
        form = AddBotForm(request.POST)
        if form.is_valid():
            if user_profile_qs:
                amount_user_bots = Bots.objects.filter(
                    profile__user=request.user).count()
                if amount_user_bots < current_plan.max_bots:
                    obj = form.save(commit=False)
                    # Set current user profile
                    obj.profile = Profile.objects.get(user=request.user)
                    # Convert float form plan to time in bot
                    if current_plan.max_time == 24.0:
                        obj.time_left = "{0:02.0f}:{1:02.0f}".format(
                            *divmod(float("23.99") * 60, 60)
                        )
                    else:
                        obj.time_left = "{0:02.0f}:{1:02.0f}".format(
                            *divmod(float(current_plan.max_time) * 60, 60)
                        )
                        obj.converted_time = current_plan.max_time
                    obj.save()
                    messages.add_message(
                        request, messages.SUCCESS, 'A new bot has been added.')
                    return HttpResponseRedirect(obj.get_absolute_url())

    context = {
        "user_bots": user_bots,
        "lock_add": lock_add,
        "form": form,
    }

    return render(request, "user/dashboard.html", context)


def profile_view(request):
    current_user = Profile.objects.filter(user=request.user)

    if current_user:
        amount_user_bots = Bots.objects.filter(
            profile__user=request.user).count()
        user_profile = Profile.objects.get(user=request.user)
        if amount_user_bots != 0:
            current_user_qs = Bots.objects.filter(profile__user=request.user)
        else:
            current_user_qs = User.objects.filter(username=request.user)
    else:
        current_user_qs = User.objects.filter(username=request.user)

    user_data = User.objects.get(username=request.user)
    form = UserSettingsForm()
    if request.method == "POST":
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            username = form.cleaned_data["username"]
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            email = form.cleaned_data["email"]

            obj = form.save(commit=False)

            if not username:
                obj.username = user_data.username
            if not first_name:
                obj.first_name = user_data.first_name
            if not last_name:
                obj.last_name = user_data.last_name
            if not email:
                obj.email = user_data.email
            messages.add_message(request, messages.SUCCESS,
                                 'Profile details updated.')
            obj.save()
            form = UserSettingsForm()
        else:
            messages.add_message(request, messages.ERROR,
                                 'Wrong data provided')

    context = {
        "current_user_qs": current_user_qs,
        "form": form,
        "user_profile": user_profile
    }

    return render(request, "user/profile.html", context)


def shop_view(request):
    plans = Plan.objects.all()
    user_profile = Profile.objects.get(user=request.user)
    starter_plan = Plan.objects.get(name="STARTER")
    user_plan = user_profile.plan.name
    currency = Currency.objects.all()
    lock = False
    if user_profile.plan_expiration_date:
        time_to_end = str(user_profile.plan_expiration_date -
                          user_profile.plan_start_date)
        if time_to_end != "0:00:00":
            lock = True
        else:
            if user_profile.plan != starter_plan:
                user_profile.plan = starter_plan
                user_profile.save()

    context = {
        "plans": plans,
        "user_plan": user_plan,
        "currency": currency,
        "user_profile": user_profile,
        "lock": lock,
    }
    return render(request, "user/shop.html", context)


def currency_view(request):
    body_data = json.loads(request.body)
    currency_id = body_data['productId']
    product = Currency.objects.get(id=currency_id)
    price = str(product.price)
    value = str(product.value)
    data = {
        'price': price,
        'value': value,
    }
    return JsonResponse(data)


def plan_modal_view(request):
    body_data = json.loads(request.body)
    modal_id = body_data['modalId']
    product = Plan.objects.get(id=modal_id)
    name = str(product.name)
    price = str(product.price)

    modal_data = {
        'name': name,
        'price': price,
        'id': modal_id,
    }

    return JsonResponse(modal_data)


def currency_payment_complete(request):
    body_data = json.loads(request.body)
    currency_id = body_data['productId']
    profile_id = body_data['userProfile']
    currency_product = Currency.objects.get(id=currency_id)
    profile = Profile.objects.get(id=profile_id)
    Orders.objects.create(profile=profile,
                          currency_package=currency_product)

    if currency_id and profile_id:
        profile.wallet += currency_product.value
        profile.save()
        messages.add_message(request, messages.SUCCESS,
                             "Successfully purchased: " + str(currency_product))

    return JsonResponse('Payment completed!', safe=False)


def plan_buy(request):
    body_data = json.loads(request.body)
    plan_id = body_data['planId']
    plan_product = Plan.objects.get(id=plan_id)
    user_profile = Profile.objects.get(user=request.user)
    if user_profile.plan != plan_product:
        if user_profile.wallet >= plan_product.price:
            user_profile.wallet -= plan_product.price
            user_profile.plan = plan_product
            user_profile.plan_start_date = timezone.now()
            user_profile.plan_expiration_date = user_profile.plan_start_date + \
                timedelta(30, 0)
            user_profile.save()
            user_bots = Bots.objects.filter(profile=user_profile)
            if user_bots:
                if plan_product.max_time == 24.0:
                    for bot in user_bots:
                        bot.time_left = "23:59:00"
                        bot.save()
                elif plan_product.max_time == 12.0:
                    for bot in user_bots:
                        bot.time_left = "12:00:00"
                        bot.converted_time = 12
                        bot.save()
            response = "The transaction was successful, the plan was purchased"
        else:
            response = "You don't have enough gears"
    else:
        response = "You already have a plan"
    messages.add_message(request, messages.SUCCESS, response)
    return JsonResponse('Payment completed!', safe=False)


class SettingsView(UpdateView):
    template_name = "user/settings.html"
    model = Bots
    form_class = SettingsForm
    success_url = "dashboard"

    def get_queryset(self):
        return Bots.objects.filter(profile__user=self.request.user)


class UserBotDetails(DetailView):
    model = Bots


class EditBotDetails(UpdateView):
    template_name = "user/edit-bot.html"
    model = Bots
    form_class = EditBotForm
    success_url = "../dashboard"
    context_object_name = "edit_info"

    def get_queryset(self):
        return Bots.objects.filter(profile__user=self.request.user)

    def get_form_kwargs(self):
        kwargs = super(EditBotDetails, self).get_form_kwargs()
        # Update the existing form kwargs dict with the pk session.
        kwargs.update({"pk": self.kwargs["pk"]})
        return kwargs


class Faq(ListView):
    template_name = "user/faq.html"
    model = FaqList
    context_object_name = "faqs"


class Regulations(ListView):
    template_name = "account/regulations.html"
    model = PageGenerator


class PrivacyPolicy(ListView):
    template_name = "account/privacy-policy.html"
    model = PageGenerator


class MyPasswordChangeView(PasswordChangeView):
    success_url = "/login/"