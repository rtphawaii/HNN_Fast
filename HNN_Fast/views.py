from django.shortcuts import render
from django.http import HttpRequest
from .outreach import outreach   # avoid "import *"
import csv, io, re
from django.http import HttpRequest, HttpResponse
from django.utils.timezone import now

def _normalize_item(d: dict) -> dict:
    return {
        "title": d.get("title") or d.get("text") or "Untitled result",
        "link": d.get("link", ""),
        "subtitle": d.get("subtitle", ""),
    }

def search(query: str) -> dict:
    raw = outreach(query)  # should return list[dict]
    # items = [_normalize_item(i) for i in raw]
    # return {
    #     "summary": f"You searched for: {query}",
    #     "items": items,
    # }
    return raw

import markdown
from django.utils.safestring import mark_safe
from django.shortcuts import render

def search_view(request):
    error = None
    results_html = None

    try:
        markdown_text = search('test')

        if markdown_text:
            results_html = mark_safe(
                markdown.markdown(
                    markdown_text,
                    extensions=["extra", "sane_lists"]
                )
            )
    except Exception as e:
        error = str(e)

    return render(
        request,
        "HNN_Fast/search.html",
        {
            "results_html": results_html,
            "error": error,
        },
    )


def _normalize_item(d: dict) -> dict:
    return {
        "title": d.get("title") or d.get("text") or "Untitled result",
        "link": d.get("link", ""),
        "subtitle": d.get("subtitle", ""),
    }
