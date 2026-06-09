/*
 * Journey taxonomy for the MindWave state picker.
 *
 * This is the product-side twin of `tools/email-to-obsidian/taxonomy.py`.
 * Where that file maps an *email* to a note type + vault folder, this maps a
 * *nervous-system state* to a journey + route. Same shape, different substrate:
 *
 *     note type  -> (vault subfolder, description)        [taxonomy.py]
 *     state type -> (journey route,  description, ...)    [this file]
 *
 * Edit this file to add, rename, or re-route journeys. The keys are the values
 * the classifier (`journey-classifier.js`) is allowed to return; each carries
 * the human description the classifier reads to decide which bucket a person is
 * in, plus the journey it routes them to and ONE micro action-item to do first.
 *
 * Keep the descriptions and `cues` concrete -- like the email taxonomy, they
 * are the only signal the classifier uses to choose a bucket.
 */

const BASE_URL = "https://explore.denverzenden.com/mindwave-journeys";

// state key -> journey definition
const JOURNEY_TYPES = {
  unwind: {
    label: "Wind Down",
    // Routed-to journey. The query param lets the destination open the right one.
    route: `${BASE_URL}?journey=unwind`,
    // What this state IS (read by the classifier to steer its choice).
    description:
      "Wired-but-tired. The body wants sleep but the mind won't power down. " +
      "Best served by a slow downshift toward rest, not stimulation.",
    // Words/phrases that signal this *intent* (not just surface symptoms).
    cues: ["sleep", "tired", "exhausted", "bed", "insomnia", "can't switch off",
           "wind down", "night", "rest", "wired"],
    // The ONE small thing to do first -- the product analog of `action_items`.
    action: "Lengthen your exhale: in for 4, out for 8, three times.",
  },

  quiet: {
    label: "Quiet the Loop",
    route: `${BASE_URL}?journey=quiet`,
    description:
      "An anxious loop -- racing or repetitive thoughts spinning faster than " +
      "they resolve. Needs the loop interrupted and slowed, not analyzed.",
    cues: ["racing", "anxious", "anxiety", "worry", "spiral", "overthinking",
           "can't stop thinking", "panic", "loop", "ruminating"],
    action: "Name 3 things you can hear right now. Out loud if you can.",
  },

  focus: {
    label: "Find Focus",
    route: `${BASE_URL}?journey=focus`,
    description:
      "Scattered and fragmented -- attention won't settle on one thing. Wants " +
      "to drop into flow, not to relax into sleep.",
    cues: ["focus", "scattered", "distracted", "can't concentrate", "foggy",
           "brain fog", "flow", "work", "study", "procrastinating"],
    action: "Pick the single next task. Close everything else for one journey.",
  },

  reset: {
    label: "Emotional Reset",
    route: `${BASE_URL}?journey=reset`,
    description:
      "Flat, heavy, or emotionally flooded -- frustration, sadness, or " +
      "numbness. Needs gentle regulation and a return to baseline, not a fix.",
    cues: ["sad", "down", "flat", "numb", "frustrated", "angry", "overwhelmed",
           "emotional", "cry", "heavy", "burned out", "burnout"],
    action: "Put a hand on your chest. One slow breath before you press play.",
  },

  calm: {
    label: "Return to Calm",
    route: `${BASE_URL}?journey=calm`,
    description:
      "General stress or activation with no single dominant signal. The safe " +
      "default: a guided downshift back toward a calm, present baseline.",
    cues: ["stress", "stressed", "tense", "on edge", "restless", "calm",
           "relax", "reset", "present", "ground"],
    action: "Unclench your jaw and drop your shoulders. Notice the difference.",
  },
};

// Fallback bucket if the classifier finds no clear intent -- mirrors
// taxonomy.py's DEFAULT_TYPE. "Return to Calm" is the safe general journey.
const DEFAULT_TYPE = "calm";

const ALLOWED_TYPES = Object.keys(JOURNEY_TYPES);

// Browser global (no bundler on this static site) + module export for tests.
if (typeof window !== "undefined") {
  window.JourneyTaxonomy = { JOURNEY_TYPES, DEFAULT_TYPE, ALLOWED_TYPES };
}
if (typeof module !== "undefined" && module.exports) {
  module.exports = { JOURNEY_TYPES, DEFAULT_TYPE, ALLOWED_TYPES };
}
