Hey dude.

You've got a new subscriber to the Morning Creative Journal Prompt.
{% if object.name %}Their name is {{ object.name }} and{% else %}They didn't leave a name, but{% endif %}
their email address is {{ object.email }}.

{% if latest_post %}They've just been sent the latest
prompt, from {{ latest_post|date:'F jS' }}.{% endif %}

Nice one!
