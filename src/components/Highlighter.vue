<template>
  <svg class="highlighter">
    <svg width="1em" height="1em" overflow="visible" viewBox="0 0 1 1">
      <rect
        v-for="highlightSegment in highlightSegments"
        :key="`${highlightSegment[0]}_${highlightSegment[1]}`"
        x="0.5px"
        :y="highlightSegment[0]"
        :height="highlightSegment[1] - highlightSegment[0]"
        :width="`${width}px`"
        fill="white"
        class="shadow"
      ></rect>
    </svg>
  </svg>
</template>

<script lang="ts">
import { defineComponent, PropType } from "vue";

let resizeObserver: ResizeObserver;

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
      width: 200,
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
  mounted() {
    this.onWindowResize();

    resizeObserver = new ResizeObserver(this.onWindowResize);
    resizeObserver.observe(this.$el);
  },
  beforeUnmount() {
    resizeObserver.disconnect();
  },

  methods: {
    onWindowResize() {
      const fontSize = parseFloat(getComputedStyle(this.$el).fontSize);
      this.width = this.$el.clientWidth / fontSize - 1; // 1em padding outside, 1em inside
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
  padding: 1em 0;
}

.shadow {
  -webkit-filter: drop-shadow(0.01em 0em 0.015em rgba(0, 0, 0, 0.7));
  filter: drop-shadow(0.01em 0em 0.015em rgba(0, 0, 0, 0.7));
}
</style>
