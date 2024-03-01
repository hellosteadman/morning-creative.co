{% load miditags %}Hey, thanks for signing up to Morning Creative's journal prompts. Every weekday evening, I'll share with you a thought, a question, or a provocation you can use to fill in your journal. Some will get your creative juices flowing; some probably won't feel as relevant.{% if latest_post %}

Here's what the last one looked like:
---

## {{ latest_post.title }}
from {{ latest_post.published|date:'jS F, Y' }}

{% miditags latest_post.body 'plain' %}

---{% endif %}
