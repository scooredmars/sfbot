from django.urls import path

from . import views

urlpatterns = [
    path("", views.home_view, name="index"),
    path("dashboard", views.dashboard_view, name="dashboard"),
    path("<int:pk>", views.SettingsView.as_view(), name="settings"),
    path("<int:pk>", views.UserBotDetails.as_view(), name="bot-detail"),
    path("edit/<int:pk>", views.EditBotDetails.as_view(), name="edit-bot"),
    path("profile", views.profile_view, name="profile"),
    path("complete", views.currency_payment_complete, name="complete"),
    path("shop", views.shop_view, name="shop"),
    path("plan_modal", views.plan_modal_view, name="plan_modal"),
    path("currency", views.currency_view, name="currency"),
    path("plan", views.plan_buy, name="plan"),
    path("faq", views.Faq.as_view(), name="faq"),
    path("regulations", views.Regulations.as_view(), name="regulations"),
    path("privacy-policy", views.PrivacyPolicy.as_view(), name="privacy-policy"),
]