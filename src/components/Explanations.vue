<template>
  <div class="root" style="position: relative; font-size: 14px">
    <p
      v-for="explanation in explanations"
      class="explanation"
      :style="{
        top: `${(explanation.from - 0.35) * 1.5}em`,
        height: `${(explanation.to - explanation.from + 1) * 1.5}em`,
      }"
    >
      {{ explanation.explanation }}
    </p>
  </div>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";

export interface Explanation {
  from: number;
  to: number;
  explanation: string;
}

export default defineComponent({
  name: "Explanations",

  props: {
    explanations: {
      required: true,
      type: Array as PropType<Explanation[]>,
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
  left: -40px;
  background: linear-gradient(90deg, transparent, #50a14f88 20px);;
  width: 100%;
  padding-left: 3em;
}
</style>
