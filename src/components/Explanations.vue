<template>
  <div class="root" style="position: relative; font-size: 14px">
    <div
      v-for="(explanationGroup, loc) in explanationGroups"
      :id="`explanation_${loc}`"
      :key="loc"
      class="explanation"
      :style="{
        top: `${(explanationGroup[0].from - 0.4) * 1.5}em`,
      }"
      @mouseenter="onExplanationFocus"
      @mouseleave="onExplanationBlur"
    >
      <div
        :id="`accordion_${loc}`"
        class="accordion"
        :style="{
          '--bs-accordion-active-color': colorOfLoc[loc].color,
          '--bs-accordion-active-bg': colorOfLoc[loc].bg,
          '--bs-accordion-border-color': colorOfLoc[loc].bg,
        }"
      >
        <div
          v-for="(explanation, i) in explanationGroup"
          :key="loc + i"
          class="accordion-item"
        >
          <h2 :id="`heading${loc + i}`" class="accordion-header">
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
              <table class="table">
                <thead>
                  <tr>
                    <th scope="col">Score</th>
                    <th scope="col">Explanation</th>
                  </tr>
                </thead>
                <tbody>
                  <tr
                    v-for="exp in explanation.explanations"
                    :key="exp.explanation"
                  >
                    <th scope="row">{{ exp.score.toFixed(2) }}</th>
                    <td>{{ exp.explanation }}</td>
                  </tr>
                </tbody>
              </table>
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
  "orange",
  "sky-blue",
  "bluish-green",
  "yellow",
  "blue",
  "vermilion",
  "reddish-purple",
];
const colorNames = baseColorNames.map((color) => `var(--cb-${color})`);
const backgroundNames = baseColorNames.map(
  (color) => `var(--cb-${color}-light)`
);

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
          {
            color: colorNames[i % baseColorNames.length],
            bg: backgroundNames[i % baseColorNames.length],
          },
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

  mounted() {
    eventBus.on("focusHighlight", this.onHighlightFocus);
    eventBus.on("blurHighlight", this.onHighlightBlur);
  },

  beforeUnmount() {
    eventBus.off("focusHighlight", this.onHighlightFocus);
    eventBus.off("blurHighlight", this.onHighlightBlur);
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
      const explanationDiv = document.getElementById(
        explanationId
      ) as HTMLDivElement | null;
      if (explanationDiv === null) {
        return;
      }
      explanationDiv.style.zIndex = "10";
      this.getCollapseInstancesForEvent(explanationDiv).forEach(
        (collapseInstance) => collapseInstance.show()
      );
    },
    onHighlightBlur([from, to]: [number, number]) {
      const explanationId = `explanation_${from}_${to}`;
      const explanationDiv = document.getElementById(
        explanationId
      ) as HTMLDivElement | null;
      if (explanationDiv === null) {
        return;
      }
      explanationDiv.style.zIndex = "auto";
      this.getCollapseInstancesForEvent(explanationDiv).forEach(
        (collapseInstance) => collapseInstance.hide()
      );
    },
  },
});
</script>

<style scoped lang="scss">
$colors: (
  "orange": rgb(230, 159, 0),
  "sky-blue": rgb(86, 180, 233),
  "bluish-green": rgb(0, 158, 115),
  "yellow": rgb(240, 228, 66),
  "blue": rgb(0, 114, 178),
  "vermilion": rgb(213, 94, 0),
  "reddish-purple": rgb(204, 121, 167),
);

.root {
  margin-top: 20px;

  @each $name, $color in $colors {
    --cb-#{$name}: #{darken($color, 25%)};
    --cb-#{$name}-light: #{lighten($color, 25%)};
  }
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

.accordion-body {
  padding: 0;
}

.table {
  margin-bottom: 0;
}

tbody tr:last-child {
  th,
  td {
    border-bottom-width: 0;
  }
}
</style>
