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
    items = [_normalize_item(i) for i in raw]
    return {
        "summary": f"You searched for: {query}",
        "items": items,
    }

def search_view(request: HttpRequest):
    q = (request.GET.get("q") or "").strip()
    results = None
    error = None

    if q:
        try:
            results = search(q)
        except Exception as exc:
            error = str(exc)

    return render(
        request,
        "OutreachAuto/search.html",   # see note below
        {"q": q, "results": results, "error": error},
    )

def _normalize_item(d: dict) -> dict:
    return {
        "title": d.get("title") or d.get("text") or "Untitled result",
        "link": d.get("link", ""),
        "subtitle": d.get("subtitle", ""),
    }

def download_csv_view(request: HttpRequest) -> HttpResponse:
    q = (request.GET.get("q") or "").strip()
    if not q:
        return HttpResponse("Missing ?q=...", status=400)

    # Recompute results for the given query (stateless + simple)
    raw = outreach(q)
    items = [_normalize_item(x) for x in raw]

    # Prepare CSV in-memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["query", "title", "link", "subtitle"])
    for it in items:
        writer.writerow([q, it["title"], it["link"], it["subtitle"]])

    csv_data = output.getvalue()
    output.close()

    # Nice filename: outreach_<query>_<YYYYMMDD-HHMM>.csv
    safe_q = re.sub(r"[^A-Za-z0-9._-]+", "_", q)[:60] or "results"
    stamp = now().strftime("%Y%m%d-%H%M")
    filename = f"outreach_{safe_q}_{stamp}.csv"

    resp = HttpResponse(csv_data, content_type="text/csv; charset=utf-8")
    resp["Content-Disposition"] = f'attachment; filename="{filename}"'
    return resp
