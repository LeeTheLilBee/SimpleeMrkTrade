from engine.billing_hooks import (
    create_stripe_checkout_placeholder,
    create_stripe_portal_placeholder,
    set_billing_status,
    update_billing_event,
)

def start_checkout(username, plan):
    return create_stripe_checkout_placeholder(username, plan)

def open_customer_portal(username):
    return create_stripe_portal_placeholder(username)

def simulate_checkout_success(username, plan):
    return set_billing_status(
        username=username,
        plan=plan,
        status="active",
        provider="stripe",
        customer_id=f"cus_{username}_placeholder",
        subscription_id=f"sub_{username}_{plan.lower()}",
        checkout_url=None,
        portal_url=f"/billing/stripe/portal-view?user={username}",
        last_event={"name": "checkout.session.completed"}
    )

def process_webhook_event(event_type, username=None, plan=None):
    if not username:
        return {"ok": False, "message": "username required for stub processing"}

    updates = {}
    if event_type == "invoice.paid":
        updates["status"] = "active"
    elif event_type == "customer.subscription.deleted":
        updates["status"] = "canceled"
    elif event_type == "invoice.payment_failed":
        updates["status"] = "past_due"

    if plan:
        updates["plan"] = plan

    payload = update_billing_event(username, event_type, updates=updates)
    return {"ok": True, "billing": payload}
