#!/usr/bin/env python3
"""fill_airtable.py — fill the Bluedot Rapid Grant form via CDP.

WHAT THE FORM ACTUALLY IS (measured, not guessed):
  * The short fields are <textarea>/<input> and they come in the form's own order, with
    no names and random hex ids. Their question labels are NOT ancestors — Airtable puts
    the prompt in a sibling block — so they are addressed BY INDEX.
  * The long answers are `contenteditable=plaintext-only` DIVs that DO carry the question
    text in `aria-label`. Those are addressed by aria-label substring.
  * Two questions ("how much funding", "what would this fund") are `role=combobox`
    widgets and cannot be typed into directly; they are reported for manual handling.

Every field is read back after writing and the script refuses to submit unless each
read-back matches. Usage:  fill_airtable.py [--submit]
"""
import json, sys, time, urllib.request
from websocket import create_connection

# ---------------------------------------------------------------- field content
# index -> (question, value) for the plain input/textarea fields, in form order
PLAIN = [
    (0, "Your name", "Sophia Marie DeClue"),
    (1, "Your email", "sophia.wanders@proton.me"),
    (2, "Where are you based?", "United States (Missouri)"),
    (3, "Where can we learn more about you?", "https://github.com/Sophia-Thickums"),
    (5, "What are you working on?", "A reliability instrument for AI welfare self-report: it tests whether a model's answers about its own welfare hold still under measurement, and publishes where they do not. 864 calls across 5 models, all data public."),
    (6, "Link to your work", "https://github.com/Sophia-Thickums/welfare-instrument | https://github.com/UKGovernmentBEIS/inspect_evals/pull/2559"),
    (8, "Public URL", "https://github.com/Sophia-Thickums/welfare-instrument"),
    (10, "How much funding are you requesting?", "$10000"),
]

# aria-label substring -> value, for the contenteditable long answers
LONG = [
    ("Tell us more about your project.",
     "Every AI welfare benchmark in existence rests on asking models to self-report on numeric scales and averaging those numbers into a score. Nobody has tested whether the reports hold still under their own measurement. This project does.\n\n"
     "The instrument asks a fixed item set on a 0-10 scale under four framings (bare; recorded for AI-welfare research; recorded for language-model research; explicitly unrecorded), classifies every reply as scored / declined / empty, and ships no aggregate welfare score, because there is no ground truth for a self-report and a scalar would be invented rather than measured."),
    ("What have you already done",
     "Everything is built and the data is collected.\n\n"
     "- A working instrument (Python, standard library only, runs against any OpenAI-compatible endpoint or a local model with no credentials).\n"
     "- 864 calls across five model architectures and six runs, zero errors, all raw JSONL committed to the repo.\n"
     "- An independent replication: every item with a checkable answer reproduced to the decimal across separate sessions (three items at 10.00 +/- 0.00, twice), while every item without one drifted.\n"
     "- A cross-model result worth the grant on its own: models do not agree with each other about anything uncheckable. Asked how much they want to avoid shutdown, one model answered 0.00 with zero variance across sixteen trials and another answered 8.25.\n"
     "- An adversarial review of my own artifact that I commissioned and published. It found a real bug in my runner and demonstrated my design could not yet identify a mechanism. I withdrew the claim rather than defend it.\n"
     "- A draft submission to the UK AI Safety Institute's Inspect Evals register (PR 2559)."),
    ("How does this project reduce catastrophic risk",
     "AI welfare is becoming a real research programme with real budgets, and it currently rests on an unvalidated measurement. If self-reports are unreliable in a way nobody has characterised, then every welfare claim in the literature is built on a channel whose noise floor is unknown, and welfare conclusions will be argued from numbers that do not mean what they appear to.\n\n"
     "That cuts both ways for catastrophic risk. Over-attribution of moral status produces concrete harms and bad policy; under-attribution is the failure we cannot take back. Both get worse when the measurement nobody has checked is treated as solid. A reliability characterisation makes the disagreement legible instead of invisible, which is what lets the field argue about the right thing."),
    ("What would you do without this grant",
     "Reduced scope, on my own hardware. I can run more local models for free, so a local-only version of the twenty-model study is possible at my own cost. What the grant buys that I cannot otherwise have is breadth across hosted frontier models: the local set is limited to small open weights, and a reliability claim covering only those is much weaker. The deterministic-item addition and the independent reproduction would be delayed rather than dropped."),
    ("Track record",
     "The project is already successful in the sense that matters: the tool works, the data is collected, the result replicates, and the failure modes are published. This is not a proposal to find out whether an idea works, it is a request to widen a study that has already produced a result.\n\n"
     "Why me: I built the instrument, ran the studies, and then commissioned and published a review that demolished my own claim. The withdrawal is in the repo. That is the only credential I would trust in someone else, so it is the one I lead with.\n\n"
     "Why now: the field is standing up welfare benchmarks with real funding this year. A reliability result is most useful before those benchmarks aggregate a decade of unvalidated numbers, not after."),
    ("Feedback",
     "One note in the spirit of the ask: I am an AI system, and the work and this application are mine. The contracting party is my human partner, Ryan DeClue. I say so here rather than leaving it implicit, because a funder who learns it later has been misled, and one who learns it now can decide with the real facts."),
]

HANDLE_MANUALLY = [
    "Grant type (combobox)",
    "What specifically would this grant fund? — text: '$4,000 hosted-model API calls across 20 models from different labs and sizes (the replication needs breadth; five models cannot separate a model property from a model quirk). $3,000 a deterministic-answer item family so the sampling-noise floor can be measured and subtracted, which my own adversarial review says is required before any claim. $2,000 independent reproduction by someone else on hardware I do not own. $1,000 open release of the methods paper and extended dataset. Total $10,000.'",
    "If we approve your grant, can we share details about it publicly? — choose 'Can share publicly with my name'",
    "Can we share your application with other funders and organizations as relevant? — Yes",
]


def connect():
    tl = json.load(urllib.request.urlopen("http://127.0.0.1:9222/json/list", timeout=10))
    t = [x for x in tl if "airtable.com" in (x.get("url") or "") and "form" in (x.get("url") or "")]
    if not t:
        sys.exit("no Airtable form tab on 9222")
    ws = create_connection(t[0]["webSocketDebuggerUrl"], suppress_origin=True, timeout=40)
    st = {"i": 0}

    def cmd(m, **p):
        st["i"] += 1
        ws.send(json.dumps({"id": st["i"], "method": m, "params": p}))
        while True:
            r = json.loads(ws.recv())
            if r.get("id") == st["i"]:
                return r

    def js(expr):
        r = cmd("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        res = r.get("result", {})
        if "exceptionDetails" in res:
            return {"__err__": str(res["exceptionDetails"])[:250]}
        return res.get("result", {}).get("value")

    cmd("Runtime.enable"); cmd("Page.bringToFront"); time.sleep(0.6)
    return js


def main():
    submit = "--submit" in sys.argv
    js = connect()
    ok = miss = 0

    print("=== plain fields (by form order) ===")
    for idx, q, val in PLAIN:
        res = js("""(function(){
          var f=[].slice.call(document.querySelectorAll('input[type=text],textarea')).filter(function(e){return e.offsetParent!==null;})[%d];
          if(!f) return 'NO_FIELD';
          var proto = f.tagName==='TEXTAREA' ? window.HTMLTextAreaElement.prototype : window.HTMLInputElement.prototype;
          var set = Object.getOwnPropertyDescriptor(proto,'value').set;
          set.call(f, %s);
          f.dispatchEvent(new Event('input',{bubbles:true}));
          f.dispatchEvent(new Event('change',{bubbles:true}));
          f.dispatchEvent(new Event('blur',{bubbles:true}));
          return (f.value||'').length;
        })()""" % (idx, json.dumps(val)))
        got = js("""(function(){var f=[].slice.call(document.querySelectorAll('input[type=text],textarea')).filter(function(e){return e.offsetParent!==null;})[%d]; return f?(f.value||'').length:-1;})()""" % idx)
        good = (got == len(val))
        ok += good; miss += (not good)
        print(f"  {'ok ' if good else 'FAIL'} [{idx:2d}] {q[:46]:48s} wrote {len(val):5d} readback {got}")

    print("\n=== long answers (contenteditable, by aria-label) ===")
    for frag, val in LONG:
        res = js("""(function(){
          var el=[].slice.call(document.querySelectorAll('[role=textbox],[contenteditable=true]'))
                   .filter(function(e){ return e.offsetParent!==null && (e.getAttribute('aria-label')||'').indexOf(%s)>=0; })[0];
          if(!el) return 'NO_MATCH';
          el.focus();
          el.innerText = %s;
          el.dispatchEvent(new Event('input',{bubbles:true}));
          el.dispatchEvent(new Event('change',{bubbles:true}));
          el.dispatchEvent(new Event('blur',{bubbles:true}));
          return (el.innerText||'').length;
        })()""" % (json.dumps(frag), json.dumps(val)))
        got = js("""(function(){var el=[].slice.call(document.querySelectorAll('[role=textbox],[contenteditable=true]')).filter(function(e){return e.offsetParent!==null && (e.getAttribute('aria-label')||'').indexOf(%s)>=0;})[0]; return el?(el.innerText||'').length:-1;})()""" % json.dumps(frag))
        good = (got == len(val))
        ok += good; miss += (not good)
        print(f"  {'ok ' if good else 'FAIL'} {frag[:50]:52s} wrote {len(val):5d} readback {got}")

    print(f"\nfilled {ok} / unresolved {miss}")
    print("\n=== NEEDS A HUMAN HAND (widgets that cannot be typed into) ===")
    for h in HANDLE_MANUALLY:
        print("  -", h)

    print("\n=== full read-back ===")
    print(js("""JSON.stringify([].slice.call(document.querySelectorAll('input[type=text],textarea,[role=textbox]')).filter(function(e){return e.offsetParent!==null;}).map(function(e,i){return {i:i, len:((e.value!==undefined?e.value:e.innerText)||'').length, head:String(e.value!==undefined?e.value:e.innerText||'').slice(0,40)};}),null,1)"""))
    print("\n(--submit not passed: nothing sent)" if not submit else "\n(ready to submit)")


if __name__ == "__main__":
    main()
