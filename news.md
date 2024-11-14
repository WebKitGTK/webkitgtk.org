---
layout: default
title: News
---

<ul class="news">
{% for post in site.posts %}
  <li><a href="{{ post.url | prepend: site.baseurl }}"><span class="title">{{ post.title }}</span>
    <span class="date">{{ post.date | date: "%Y-%m-%d" }}</span></a>
  </li>
{%endfor%}
</ul>
