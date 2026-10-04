(function () {
  const data = document.getElementById("lab-data");
  const choiceBox = document.getElementById("lab-choices");
  if (data && choiceBox) {
    const cases = JSON.parse(data.textContent);
    let index = 0;
    let answered = 0;
    let correct = 0;
    let locked = false;

    function paint() {
      const item = cases[index];
      locked = false;
      document.getElementById("lab-kicker").textContent = "Case " + (index + 1) + " of " + cases.length;
      document.getElementById("lab-prompt").textContent = item.prompt;
      document.getElementById("lab-detail").textContent = item.detail;
      const feedback = document.getElementById("lab-feedback");
      feedback.textContent = "Choose an answer. The explanation appears here.";
      feedback.className = "mt-3 text-sm leading-6 text-slate-300";
      choiceBox.replaceChildren();
      item.options.forEach(function (label, option) {
        const button = document.createElement("button");
        button.type = "button";
        button.className = "rounded-lg border border-slate-700 px-3 py-2 text-left text-sm text-slate-200 hover:border-slate-400";
        button.textContent = label;
        button.addEventListener("click", function () { choose(option); });
        choiceBox.appendChild(button);
      });
    }

    function choose(option) {
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
    }

    document.getElementById("lab-next").addEventListener("click", function () {
      index = (index + 1) % cases.length;
      paint();
    });
    paint();
  }

  document.querySelectorAll(".exam-toggle").forEach(function (button) {
    button.addEventListener("click", function () {
      const answer = document.getElementById(button.dataset.target);
      const opening = answer.hidden;
      answer.hidden = !opening;
      button.setAttribute("aria-expanded", String(opening));
      button.textContent = opening ? "Hide the decision" : "Show the decision";
    });
  });

  const calc = document.getElementById("calc");
  if (calc) {
    calc.addEventListener("click", function () {
      const reserved = Number(document.getElementById("reserved").value);
      const burst = Number(document.getElementById("burst").value);
      const out = document.getElementById("calc-out");
      if (!Number.isFinite(reserved) || !Number.isFinite(burst) || reserved < 0 || burst < 1) {
        out.textContent = "Enter a reserved concurrency of 0 or more and a burst of at least 1.";
        return;
      }
      if (reserved === 0) {
        out.textContent = "Reserved concurrency of 0 throttles every invocation. This function cannot borrow the unreserved account pool.";
        return;
      }
      const started = Math.min(burst, reserved);
      out.textContent = started + " invocations can start. " + Math.max(burst - started, 0) + " are throttled. Those " + reserved + " reserved slots are also removed from the pool shared by functions with no reserved concurrency.";
    });
  }
})();
