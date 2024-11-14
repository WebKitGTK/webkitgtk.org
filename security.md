---
layout: default
title: Security Advisories
---

<ul class="news">
{% for post in site.tags.WSA %}
  <li><a href="{{ post.url | prepend: site.baseurl }}"><span class="title">{{ post.title }}</span>
    <span class="date">{{ post.date | date: "%Y-%m-%d" }}</span></a>
  </li>
{%endfor%}
</ul>
