<template>
  <div class="root" style="position: relative; font-size: 14px">
    <div
      class="explanation"
      :id="`explanation_${loc}`"
      v-for="(explanationGroup, loc) in explanationGroups"
      :key="loc"
      :style="{
        top: `${(explanationGroup[0].from - 0.4) * 1.5}em`,
      }"
      @mouseenter="onExplanationFocus"
      @mouseleave="onExplanationBlur"
    >
      <div
        class="accordion"
        :id="`accordion_${loc}`"
        :style="{
          '--bs-accordion-active-color': colorOfLoc[loc].color,
          '--bs-accordion-active-bg': colorOfLoc[loc].bg,
          '--bs-accordion-border-color': colorOfLoc[loc].bg,
        }"
      >
        <div
          class="accordion-item"
          v-for="(explanation, i) in explanationGroup"
          :key="loc + i"
        >
          <h2 class="accordion-header" :id="`heading${loc + i}`">
            <button
              class="accordion-button"
              type="button"
              data-bs-toggle="collapse"
              :data-bs-target="`#collapse${loc + i}`"
              aria-expanded="true"
              :aria-controls="`collapse${loc + i}`"
            >
              {{ explanation.model }}
            </button>
          </h2>
          <div
            :id="`collapse${loc + i}`"
            class="accordion-collapse collapse"
            :aria-labelledby="`heading${loc + i}`"
          >
            <div class="accordion-body">
              <ol>
                <li v-for="exp in explanation.explanations">
                  {{ exp.explanation }}
                </li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";
import Collapse from "bootstrap/js/dist/collapse";
import { eventBus } from "../utils";

export interface IScoredExplanation {
  score: number;
  explanation: string;
}

export interface IExplanationEntry {
  from: number;
  to: number;
  model: string;
  explanations: IScoredExplanation[];
}

const baseColorNames = [
  "blue",
  "indigo",
  "cyan",
  "orange",
  "purple",
  "teal",
  "yellow",
  "green",
];
const colorNames = baseColorNames.map((color) => `var(--bs-${color}-900)`);
const backgroundNames = baseColorNames.map((color) => `var(--bs-${color}-100)`);

export default defineComponent({
  name: "Explanations",

  props: {
    explanations: {
      required: true,
      type: Array as PropType<IExplanationEntry[]>,
    },
  },
  computed: {
    colorOfLoc(): Record<string, { color: string; bg: string }> {
      const colorKeyValues = Object.keys(this.explanationGroups).map(
        (loc, i) => [
          loc,
          { color: colorNames[i % 9], bg: backgroundNames[i % 9] },
        ]
      );

      return Object.fromEntries(colorKeyValues);
    },
    explanationGroups(): Record<string, IExplanationEntry[]> {
      const explanationGroups: Record<string, IExplanationEntry[]> = {};

      for (const explanationEntry of this.explanations) {
        const key = `${explanationEntry.from}_${explanationEntry.to}`;

        if (key in explanationGroups) {
          explanationGroups[key].push(explanationEntry);
        } else {
          explanationGroups[key] = [explanationEntry];
        }
      }

      return explanationGroups;
    },
  },

  methods: {
    getCollapseInstancesForEvent: function (explanationDiv: HTMLDivElement) {
      const collapseElements = explanationDiv.querySelectorAll(".collapse");
      return Array.from(collapseElements).map((collapseElement) =>
        Collapse.getOrCreateInstance(collapseElement)
      );
    },
    onExplanationFocus(e: MouseEvent) {
      const explanationDiv = e.target as HTMLDivElement;
      explanationDiv.style.zIndex = "10";
      this.getCollapseInstancesForEvent(explanationDiv).forEach(
        (collapseInstance) => collapseInstance.show()
      );
    },
    onExplanationBlur(e: MouseEvent) {
      const explanationDiv = e.target as HTMLDivElement;
      explanationDiv.style.zIndex = "auto";
      this.getCollapseInstancesForEvent(explanationDiv).forEach(
        (collapseInstance) => collapseInstance.hide()
      );
    },
    onHighlightFocus([from, to]: [number, number]) {
      const explanationId = `explanation_${from}_${to}`;
      const explanationDiv = document.getElementById(explanationId) as HTMLDivElement;
      explanationDiv.style.zIndex = "10";
      this.getCollapseInstancesForEvent(explanationDiv).forEach(
          (collapseInstance) => collapseInstance.show()
      );
    },
    onHighlightBlur([from, to]: [number, number]) {
      const explanationId = `explanation_${from}_${to}`;
      const explanationDiv = document.getElementById(explanationId) as HTMLDivElement;
      explanationDiv.style.zIndex = "auto";
      this.getCollapseInstancesForEvent(explanationDiv).forEach(
          (collapseInstance) => collapseInstance.hide()
      );
    },
  },

  mounted() {
    eventBus.on("focusHighlight", this.onHighlightFocus);
    eventBus.on("blurHighlight", this.onHighlightBlur);
  },

  beforeUnmount() {
    eventBus.off("focusHighlight", this.onHighlightFocus);
    eventBus.off("blurHighlight", this.onHighlightBlur);
  },
});
</script>

<style scoped lang="scss">
.root {
  margin-top: 20px;
}

.explanation {
  position: absolute;
  left: -20px;
  width: 100%;
  padding-left: 3em;
}

.accordion .accordion-item:first-child .accordion-button {
  color: var(--bs-accordion-active-color);
  background-color: var(--bs-accordion-active-bg);
}

ol {
  margin-bottom: 0;
}
</style>
