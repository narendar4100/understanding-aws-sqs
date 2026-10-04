# Generates the static learning pages. Run once, then remove this file.
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "frontend"

LINKS = [
    ("home", "", "Home", "slate"),
    ("iam", "iam/", "IAM", "amber"),
    ("vpc", "vpc/", "VPC", "sky"),
    ("s3", "s3/", "S3", "green"),
    ("lambda", "lambda/", "Lambda", "orange"),
    ("sqs", "sqs/", "SQS", "emerald"),
    ("sns", "sns/", "SNS", "violet"),
    ("eventbridge", "eventbridge/", "EventBridge", "fuchsia"),
    ("northline", "projects/northline/", "Northline", "cyan"),
    ("clearfile", "projects/clearfile/", "Clearfile", "indigo"),
]

ICONS = {
    "users": "USR", "apigw": "API", "sqs": "SQS", "lambda": "λ", "db": "DB",
    "ok": "OK", "dlq": "DLQ", "iam": "IAM", "vpc": "VPC", "s3": "S3", "events": "EB",
}


def nav(base, current):
    items = []
    for key, href, label, color in LINKS:
        url = (base or "./") if key == "home" else base + href
        if key == current and key == "home":
            cls = "rounded-lg bg-slate-800 px-2.5 py-1.5 text-white"
        elif key == current:
            cls = f"rounded-lg bg-{color}-950 px-2.5 py-1.5 text-{color}-300"
            current_attr = ' aria-current="page"'
        else:
            cls = "rounded-lg px-2.5 py-1.5 text-slate-300 hover:bg-slate-900 hover:text-white"
            current_attr = ""
        items.append(f'<a href="{url}"{current_attr} class="{cls}">{label}</a>')
    home = base or "./"
    return f'''<nav class="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-3 px-6 py-5" aria-label="Primary navigation">
      <a href="{home}" class="font-semibold text-white">AWS Architecture Lab</a>
      <div class="flex flex-wrap gap-1 text-xs">{"".join(items)}</div>
    </nav>'''


def diagram(steps):
    parts = ['<div class="mt-6 overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/70 px-4 py-5"><div class="arch-flow min-w-[40rem]">']
    for index, (icon, label, sub) in enumerate(steps):
        if index:
            parts.append('<div class="arch-arrow arch-arrow--ok arch-arrow--long"></div>')
        parts.append(
            f'<div class="arch-node"><div class="arch-icon arch-icon--{icon}"><span class="font-mono text-[10px] font-semibold">{ICONS[icon]}</span></div>'
            f'<p class="arch-label">{label}</p><p class="arch-sub">{sub}</p></div>'
        )
    parts.append("</div></div>")
    return "".join(parts)


def table(headers, rows):
    head = "".join(f'<th class="px-4 py-3">{cell}</th>' for cell in headers)
    body = []
    for row in rows:
        cells = "".join(
            f'<td class="px-4 py-3{" text-white" if index == 0 else ""}">{cell}</td>'
            for index, cell in enumerate(row)
        )
        body.append(f"<tr>{cells}</tr>")
    return (
        '<div class="mt-6 overflow-x-auto rounded-xl border border-slate-800"><table class="w-full min-w-[760px] text-left text-sm">'
        f'<thead class="bg-slate-950 text-slate-300"><tr>{head}</tr></thead>'
        f'<tbody class="divide-y divide-slate-800 text-slate-400">{"".join(body)}</tbody></table></div>'
    )


def bullets(items, tone="text-slate-300"):
    lis = "".join(f"<li>• {item}</li>" for item in items)
    return f'<ul class="mt-4 space-y-2 text-sm leading-6 {tone}">{lis}</ul>'


def story(bad_title, bad, good_title, good):
    return f'''<div class="mt-6 grid gap-4 md:grid-cols-2">
      <article class="rounded-xl border border-rose-900/70 bg-black/40 p-5">
        <p class="text-xs font-medium uppercase tracking-wider text-rose-300">Fragile design</p>
        <h3 class="mt-2 text-lg font-semibold text-white">{bad_title}</h3>{bullets(bad, "text-slate-400")}
      </article>
      <article class="rounded-xl border border-emerald-900/70 bg-black/40 p-5">
        <p class="text-xs font-medium uppercase tracking-wider text-emerald-300">Exam-ready design</p>
        <h3 class="mt-2 text-lg font-semibold text-white">{good_title}</h3>{bullets(good, "text-slate-400")}
      </article>
    </div>'''


def lab_shell(title, lede):
    return f'''<section id="live-lab" class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8" aria-labelledby="lab-title">
      <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-amber-300">Live decision lab</p>
      <h2 id="lab-title" class="mt-2 text-2xl font-semibold text-white">{title}</h2>
      <p class="mt-3 max-w-3xl text-sm leading-6 text-slate-400">{lede}</p>
      <div class="mt-6 grid gap-4 lg:grid-cols-[1.3fr_.7fr]">
        <div class="rounded-xl bg-slate-950 p-5">
          <p id="lab-kicker" class="font-mono text-xs text-slate-500"></p>
          <p id="lab-prompt" class="mt-2 text-lg font-semibold leading-7 text-white"></p>
          <p id="lab-detail" class="mt-3 whitespace-pre-wrap font-mono text-xs leading-5 text-slate-400"></p>
          <div id="lab-choices" class="mt-5 flex flex-wrap gap-2"></div>
          <button id="lab-next" type="button" class="mt-5 rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-200 hover:border-slate-400">Next case</button>
        </div>
        <div class="rounded-xl border border-slate-800 bg-black p-5">
          <p class="text-xs uppercase tracking-wider text-slate-500">Result</p>
          <p id="lab-feedback" class="mt-3 text-sm leading-6 text-slate-300" aria-live="polite">Choose an answer. The explanation appears here.</p>
          <p id="lab-score" class="mt-4 font-mono text-xs text-slate-500">0 answered</p>
          <p class="mt-4 text-xs leading-5 text-slate-500">Answer before moving on. A second click does not change the score for that case.</p>
          <p class="hidden text-emerald-300 text-rose-300"></p>
        </div>
      </div>
    </section>'''


def drills(items):
    cards = []
    for index, (question, answer) in enumerate(items, 1):
        cards.append(f'''<article class="rounded-xl border border-slate-800 bg-slate-950 p-5">
          <p class="font-mono text-xs text-slate-500">Exam drill {index}</p>
          <h3 class="mt-2 font-semibold leading-6 text-white">{question}</h3>
          <button type="button" class="exam-toggle mt-4 rounded-lg border border-slate-700 px-3 py-2 text-sm text-slate-200 hover:border-slate-400" data-target="exam-{index}" aria-expanded="false">Show the decision</button>
          <p id="exam-{index}" hidden class="mt-3 text-sm leading-6 text-slate-300">{answer}</p>
        </article>''')
    return f'<div class="mt-6 grid gap-4 lg:grid-cols-2">{"".join(cards)}</div>'


def script(cases, extra=""):
    payload = json.dumps(cases, ensure_ascii=False)
    return f'''<script>
    const cases = {payload};
    let index = 0, answered = 0, correct = 0, locked = false;
    const choiceBox = document.getElementById("lab-choices");
    function paint() {{
      const item = cases[index];
      locked = false;
      document.getElementById("lab-kicker").textContent = "Case " + (index + 1) + " of " + cases.length;
      document.getElementById("lab-prompt").textContent = item.prompt;
      document.getElementById("lab-detail").textContent = item.detail;
      const feedback = document.getElementById("lab-feedback");
      feedback.textContent = "Choose an answer. The explanation appears here.";
      feedback.className = "mt-3 text-sm leading-6 text-slate-300";
      choiceBox.replaceChildren();
      item.options.forEach((label, option) => {{
        const button = document.createElement("button");
        button.type = "button";
        button.className = "rounded-lg border border-slate-700 px-3 py-2 text-left text-sm text-slate-200 hover:border-slate-400";
        button.textContent = label;
        button.addEventListener("click", () => choose(option));
        choiceBox.appendChild(button);
      }});
    }}
    function choose(option) {{
      if (locked) return;
      locked = true;
      const item = cases[index];
      const ok = option === item.answer;
      answered += 1;
      if (ok) correct += 1;
      const feedback = document.getElementById("lab-feedback");
      feedback.textContent = (ok ? "Correct. " : "Not this answer. ") + item.why;
      feedback.className = ok ? "mt-3 text-sm leading-6 text-emerald-300" : "mt-3 text-sm leading-6 text-rose-300";
      document.getElementById("lab-score").textContent = correct + " correct out of " + answered + " answered";
    }}
    document.getElementById("lab-next").addEventListener("click", () => {{
      index = (index + 1) % cases.length;
      paint();
    }});
    document.querySelectorAll(".exam-toggle").forEach((button) => {{
      button.addEventListener("click", () => {{
        const answer = document.getElementById(button.dataset.target);
        const opening = answer.hidden;
        answer.hidden = !opening;
        button.setAttribute("aria-expanded", String(opening));
        button.textContent = opening ? "Hide the decision" : "Show the decision";
      }});
    }});
    paint();
    {extra}
  </script>'''


def render(page):
    base = "../" * page["depth"]
    jumps = "".join(
        f'<a href="#{key}" class="rounded-full border border-slate-700 px-3 py-1.5 text-slate-300 hover:border-slate-400">{label}</a>'
        for key, label in page["jumps"]
    )
    docs = ", ".join(
        f'<a class="text-emerald-400 hover:text-emerald-300" href="{url}" target="_blank" rel="noreferrer">{label}</a>'
        for label, url in page["docs"]
    )
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="{page["description"]}" />
  <title>{page["title"]}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&amp;family=IBM+Plex+Sans:wght@400;500;600&amp;display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="{base}assets/site.css" />
  <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
</head>
<body class="min-h-screen bg-slate-950 text-slate-100 antialiased">
  <header class="border-b border-slate-800">
    {nav(base, page["id"])}
    <div class="mx-auto max-w-6xl px-6 py-8">
      <p class="text-[11px] font-medium uppercase tracking-[0.18em] {page["accent"]}">{page["eyebrow"]}</p>
      <h1 class="mt-2 max-w-4xl text-3xl font-semibold tracking-tight text-white sm:text-4xl">{page["headline"]}</h1>
      <p class="mt-3 max-w-3xl text-sm leading-6 text-slate-400 sm:text-base">{page["lede"]}</p>
      {diagram(page["diagram"])}
    </div>
  </header>
  <main class="mx-auto max-w-6xl px-6 py-8">
    <div class="flex flex-wrap gap-2 text-xs">{jumps}</div>
    <section id="core" class="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
      <p class="text-[11px] font-medium uppercase tracking-[0.18em] {page["accent"]}">Core model</p>
      <h2 class="mt-2 text-2xl font-semibold text-white">{page["summary_title"]}</h2>
      <p class="mt-4 max-w-4xl text-sm leading-7 text-slate-300">{page["summary"]}</p>
      {story(page["bad_title"], page["bad"], page["good_title"], page["good"])}
      <h3 class="mt-8 text-lg font-semibold text-white">{page["compare_title"]}</h3>
      {table(page["compare_headers"], page["compare_rows"])}
    </section>
    {page.get("extra", "")}
    <section id="best-lab" class="mt-12 rounded-2xl border border-amber-900/60 bg-amber-950/20 p-6 sm:p-8">
      <p class="text-[11px] font-medium uppercase tracking-[0.18em] text-amber-300">Best lab to assign</p>
      <h2 class="mt-2 text-2xl font-semibold text-white">{page["best_title"]}</h2>
      <p class="mt-3 max-w-4xl text-sm leading-7 text-slate-300">{page["best"]}</p>
    </section>
    {lab_shell(page["lab_title"], page["lab_lede"])}
    <section id="limits" class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
      <p class="text-[11px] font-medium uppercase tracking-[0.18em] {page["accent"]}">Limits and exam traps</p>
      <h2 class="mt-2 text-2xl font-semibold text-white">What this service will not do for you</h2>
      {bullets(page["will_not"])}
      {table(["Limit or behavior", "Figure students should remember", "How the exam uses it"], page["limits"])}
    </section>
    <section id="cost" class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
      <p class="text-[11px] font-medium uppercase tracking-[0.18em] {page["accent"]}">Cost</p>
      <h2 class="mt-2 text-2xl font-semibold text-white">{page["cost_title"]}</h2>
      {bullets(page["cost_points"])}
      <p class="mt-4 rounded-xl bg-black p-5 text-sm leading-7 text-slate-300">{page["cost_example"]}</p>
    </section>
    <section id="alternatives" class="mt-12">
      <p class="text-[11px] font-medium uppercase tracking-[0.18em] {page["accent"]}">Alternatives</p>
      <h2 class="mt-2 text-2xl font-semibold text-white">{page["alt_title"]}</h2>
      {table(["Need", "Choose", "Why"], page["alternatives"])}
    </section>
    <section id="waf" class="mt-12 rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
      <p class="text-[11px] font-medium uppercase tracking-[0.18em] {page["accent"]}">Well-Architected</p>
      <h2 class="mt-2 text-2xl font-semibold text-white">Check the design against all six pillars</h2>
      {table(["Pillar", "What good looks like here", "Evidence"], page["waf"])}
    </section>
    <section id="drills" class="mt-12">
      <p class="text-[11px] font-medium uppercase tracking-[0.18em] {page["accent"]}">Exam drills</p>
      <h2 class="mt-2 text-2xl font-semibold text-white">Decide before you reveal the answer</h2>
      <p class="mt-3 max-w-3xl text-sm leading-6 text-slate-400">These are original Cloud Practitioner, Solutions Architect Associate, Developer Associate, and SysOps-style decisions. They are not copied exam items.</p>
      {drills(page["drills"])}
    </section>
    <footer class="mt-12 border-t border-slate-800 py-8 text-sm leading-6 text-slate-500">Quotas and prices change. Confirm the current quota and pricing pages before relying on a number. Official references: {docs}.</footer>
  </main>
  {script(page["cases"], page.get("extra_script", ""))}
</body>
</html>
'''
    destination = ROOT / page["path"]
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(html, encoding="utf-8", newline="\n")


JUMPS = [
    ("core", "Core"), ("best-lab", "Best lab"), ("live-lab", "Live lab"),
    ("limits", "Limits"), ("cost", "Cost"), ("alternatives", "Alternatives"),
    ("waf", "Well-Architected"), ("drills", "Exam drills"),
]
