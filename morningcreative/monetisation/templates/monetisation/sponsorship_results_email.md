{% load humanize %}Hi there!

Thanks for your sponsorship of the Morning Creative Journal Prompt.
It means the world to have your support.

This is just a one-time rundown of how your
sponsorship message performed.

* Your message was featured in [{{ issue }}]({{ base_url }}{{ issue.get_absolute_url }}).
* It was delivered to **{{ delivery_count }} subscribers**.
* It has an open rate of **{{ open_rate|floatformat:1 }}%** as of today.
* So far, **{{ click_count }} {% if click_count == 1 %}person{% else %}people{% endif %}** have clicked your link ({{ object.url }}).
* As well as being delivered to email subscribers, your message will always be visible at the top of the blog post.
