<template>
  <svg class="highlighter">
    <defs>
      <linearGradient id="Gradient1">
        <stop offset="98%" stop-color="#0184bb" stop-opacity="0.25" />
        <stop offset="100%" stop-color="#0184bb" stop-opacity="0.00" />
      </linearGradient>
    </defs>
    <svg width="1em" height="1em" overflow="visible" viewBox="0 0 1 1">
      <template v-for="highlightSegment in highlightSegments">
        <rect
          :y="highlightSegment[0]"
          :height="highlightSegment[1] - highlightSegment[0]"
          :width="`${width}px`"
          fill="url(#Gradient1)"
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

  methods: {
    onWindowResize() {
      const fontSize = parseFloat(getComputedStyle(this.$el).fontSize);
      this.width = this.$el.clientWidth / fontSize - 2; // 2em padding
    },
  },
  mounted() {
    this.onWindowResize();

    window.addEventListener("resize", this.onWindowResize);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.onWindowResize);
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
}
</style>
