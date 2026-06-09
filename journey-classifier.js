/*
 * Classify a person's current state into a MindWave journey.
 *
 * This is the product-side twin of `tools/email-to-obsidian/classifier.py`.
 * That file asks Claude "what kind of note is this email?" and returns a typed,
 * structured result. This does the same for a person: "what kind of state is
 * this?" -> a typed result that routes them to the right journey.
 *
 * It returns the SAME structured shape the Python classifier does, so the two
 * stay legible as one pattern:
 *
 *     { type, title, summary, action_items }
 *
 * THE CORE RULE (lifted verbatim in spirit from classifier.py):
 *   "Classify on intent, not content."
 *   The email classifier reads the *forwarder's note*, not the quoted email.
 *   Here we classify on what the person actually NEEDS, not the loudest surface
 *   symptom. "I can't sleep because work won't leave my head" is `unwind`
 *   (the need is rest), even though "work" would naively score `focus`.
 *
 * This implementation is a small client-side heuristic because the site is a
 * static GitHub Pages build with no place to hide an API key. The seam to swap
 * it for a real Claude call lives in `classifyWithClaude()` below -- point it at
 * a tiny serverless endpoint that runs the exact `classifier.py` prompt and the
 * UI doesn't change at all.
 */

(function () {
  const Tax =
    (typeof window !== "undefined" && window.JourneyTaxonomy) ||
    (typeof require === "function" && require("./journey-taxonomy.js"));

  const { JOURNEY_TYPES, DEFAULT_TYPE, ALLOWED_TYPES } = Tax;

  // Intent boosters: phrases where the underlying NEED differs from the noun.
  // This is the "classify on intent, not content" rule, encoded. Each entry
  // pushes a state up regardless of competing surface keywords.
  const INTENT_OVERRIDES = [
    // wanting rest, even when the cause is work/thoughts
    { re: /can'?t (sleep|switch off|shut off|wind down)/i, type: "unwind" },
    { re: /(keeps?|won'?t leave) me up|up all night/i, type: "unwind" },
    // the spiral itself is the problem, whatever it's "about"
    { re: /can'?t stop (thinking|worrying)/i, type: "quiet" },
    { re: /(mind|thoughts?) (racing|spinning|spiraling)/i, type: "quiet" },
    // wanting to get INTO something, not to relax out of it
    { re: /need to (focus|concentrate|get .* done|work|study)/i, type: "focus" },
  ];

  /**
   * Heuristic classifier. Scores each journey type by cue matches, applies the
   * intent overrides, and falls back to DEFAULT_TYPE when nothing is clear --
   * exactly like the Python side defaulting to its DEFAULT_TYPE bucket.
   *
   * @param {string} text  free-text from the user ("how are you arriving?")
   * @returns {{type:string, title:string, summary:string, action_items:string[]}}
   */
  function classify(text) {
    const input = (text || "").toLowerCase().trim();

    // Score by cue overlap (content signal).
    const scores = Object.fromEntries(ALLOWED_TYPES.map((t) => [t, 0]));
    for (const type of ALLOWED_TYPES) {
      for (const cue of JOURNEY_TYPES[type].cues) {
        if (input.includes(cue)) scores[type] += 1;
      }
    }

    // Apply intent overrides (intent signal beats raw content).
    for (const { re, type } of INTENT_OVERRIDES) {
      if (re.test(input)) scores[type] += 3;
    }

    // Pick the winner; tie/blank -> DEFAULT_TYPE.
    let best = DEFAULT_TYPE;
    let bestScore = 0;
    for (const type of ALLOWED_TYPES) {
      if (scores[type] > bestScore) {
        best = type;
        bestScore = scores[type];
      }
    }

    const def = JOURNEY_TYPES[best];
    return {
      type: best,
      title: def.label,
      summary: def.description,
      // Single concrete next step -- the product's `action_items`.
      action_items: [def.action],
      route: def.route,
      // Surface whether we actually read a signal or fell back, for honest UI.
      confident: bestScore > 0,
    };
  }

  /**
   * Drop-in async seam for a real Claude classification. Wire this to a
   * serverless endpoint running the `classifier.py` prompt+schema, then call it
   * instead of `classify()` in the UI. Falls back to the heuristic on any error
   * so the page never dead-ends.
   */
  async function classifyWithClaude(text, endpoint = "/api/classify-state") {
    try {
      const res = await fetch(endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      if (!res.ok) throw new Error(`classify endpoint ${res.status}`);
      const data = await res.json();
      // Trust the server's type but re-hydrate route/action from the taxonomy
      // so client and server can't drift.
      const type = ALLOWED_TYPES.includes(data.type) ? data.type : DEFAULT_TYPE;
      const def = JOURNEY_TYPES[type];
      return {
        type,
        title: data.title || def.label,
        summary: data.summary || def.description,
        action_items:
          data.action_items && data.action_items.length
            ? data.action_items
            : [def.action],
        route: def.route,
        confident: true,
      };
    } catch (_) {
      return classify(text);
    }
  }

  const api = { classify, classifyWithClaude };
  if (typeof window !== "undefined") window.JourneyClassifier = api;
  if (typeof module !== "undefined" && module.exports) module.exports = api;
})();
