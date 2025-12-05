import os
from django.template import Template, Context

def render_verification_email(custom_id, verify_url):
    template_path = os.path.join(
        os.path.dirname(__file__),
        "verification_email_template.html"
    )

    with open(template_path, "r") as f:
        html = f.read()

    template = Template(html)
    return template.render(Context({
        "custom_id": custom_id,
        "verify_url": verify_url
    }))
