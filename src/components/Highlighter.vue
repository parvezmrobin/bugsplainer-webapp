<template>
  <svg class="highlighter">
    <svg width="1em" height="1em" overflow="visible" viewBox="0 0 1 1">
      <template v-for="highlightSegment in highlightSegments">
        <rect
          :y="highlightSegment[0]"
          :height="highlightSegment[1] - highlightSegment[0]"
          width="200px"
          fill="cornflowerblue"
          fill-opacity="0.25"
        ></rect>
      </template>
    </svg>
  </svg>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";

export default defineComponent({
  name: "Highlighter",
  props: {
    lines: {
      required: true,
      type: Array as PropType<[number, number][]>,
    },
  },
  data() {
    return {
      highlightSegments: [] as [number, number][],
    };
  },
  watch: {
    lines: {
      immediate: true,
      deep: true,
      handler() {
        this.highlightSegments = this.lines.map(([from, to]) => {
          return [(from - 1) * 1.5, to * 1.5];
        });
      },
    },
  },
});
</script>

<style scoped lang="scss">
.highlighter {
  position: absolute;
  top: 20px;
  left: 0;
  z-index: -1;
  width: 100%;
  height: 100%;
  padding: 1em;
  color: aquamarine;
}
</style>
