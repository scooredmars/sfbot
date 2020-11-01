from django.shortcuts import render
from .models import Bots, FaqList, PageGenerator, Plan, Profile, User, PermissionList, Currency, Orders


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