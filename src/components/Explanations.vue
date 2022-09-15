<template>
  <div class="root" style="position: relative; font-size: 14px">
    <div
      class="explanation"
      v-for="(explanationGroup, loc) in explanationGroups"
      :key="loc"
      :style="{
        top: `${(explanationGroup[0].from - 0.35) * 1.5}em`,
      }"
    >
      <div class="accordion" :id="`accordion_${loc}`">
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
            class="accordion-collapse collapse show"
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

export default defineComponent({
  name: "Explanations",

  props: {
    explanations: {
      required: true,
      type: Array as PropType<IExplanationEntry[]>,
    },
  },
  computed: {
    explanationGroups() {
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
});
</script>

<style scoped lang="scss">
.root {
  margin-top: 20px;
}

.explanation {
  position: absolute;
  left: 0;
  width: 100%;
  padding-left: 3em;
}
</style>
