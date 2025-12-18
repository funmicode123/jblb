import os
from django.template import Template, Context

def render_verification_email(custom_id, verify_url, referral_code=None):
    template_path = os.path.join(
        os.path.dirname(__file__),
        "verification_email_template.html"
    )

    with open(template_path, "r") as f:
        html = f.read()

    template = Template(html)
    context_data = {
        "custom_id": custom_id,
        "verify_url": verify_url
    }
    
    if referral_code:
        context_data["referral_code"] = referral_code
        # Count referrals (you might want to customize this logic)
        from ..models import Waitlist
        try:
            referral_count = Waitlist.objects.filter(
                referred_by__referral_code=referral_code,
                is_verified=True
            ).count()
            context_data["referral_count"] = referral_count
        except:
            context_data["referral_count"] = 0
    
    return template.render(Context(context_data))
