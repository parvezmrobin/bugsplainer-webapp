<template>
  <pre style="position: relative; overflow: visible">
    <code
      class="language-python"
      ref="codeEditor"
      contenteditable="true"
      @mouseup="onMouseUp"
      @focusout="highlightCode"
      @mousemove="onMouseMove"
    >{{ fileContent }}</code>
    <Highlighter :lines="highlightedLines"/>
  </pre>
</template>
<script lang="ts">
import hljs from "highlight.js/lib/core";
import python from "highlight.js/lib/languages/python";
import { defineComponent, nextTick, PropType } from "vue";
import Highlighter from "./Highlighter.vue";
import type { IExplanationEntry } from "./Explanations.vue";
import { eventBus } from "../utils";

hljs.registerLanguage("python", python);

export default defineComponent({
  name: "CodeEditor",
  components: {
    Highlighter,
  },

  props: {
    fileContent: {
      required: true,
      type: String,
    },
    explanations: {
      required: true,
      type: Array as PropType<IExplanationEntry[]>,
    },
    explainFrom: {
      required: false,
      type: Number,
    },
    explainTill: {
      required: false,
      type: Number,
    },
  },

  data() {
    return {
      fontSize: 14,
      currentlyFocusedCodeSegment: null as null | [number, number],
    };
  },

  emits: {
    "update:explainFrom": Number,
    "update:explainTill": Number,
  },

  computed: {
    uniqueExplanationLocations(): [number, number][] {
      return [...new Set(this.explanations.map((el) => [el.from, el.to].toString()))]
        .map((el) => el.split(","))
        .map(([from, to]) => [Number.parseInt(from), Number.parseInt(to)]);
    },
    highlightedLines() {
      const highlightedLines = this.uniqueExplanationLocations.slice();
      if (this.explainFrom && this.explainTill) {
        highlightedLines.push([this.explainFrom, this.explainTill]);
      }

      return highlightedLines;
    },
  },
  watch: {
    async fileContent() {
      await nextTick();
      this.highlightCode();
    },
  },
  mounted() {
    this.fontSize = parseFloat(getComputedStyle(this.$el).fontSize);
  },
  methods: {
    highlightCode() {
      if (!this.$refs.codeEditor) {
        throw new Error();
      }
      hljs.highlightElement(this.$refs.codeEditor as HTMLElement);
    },
    onMouseUp() {
      const selection = window.getSelection();
      if (
        selection === null ||
        this.$refs.codeEditor === null ||
        this.$refs.codeEditor === undefined
      ) {
        return;
      }
      let anchorNode = selection.anchorNode as Node;
      let focusNode = selection.focusNode as Node;
      if (
        anchorNode === focusNode &&
        selection.anchorOffset == selection.focusOffset
      ) {
        // this is a click; not selection
        return;
      }

      const codeEditor = this.$refs.codeEditor as HTMLPreElement;
      const siblings = Array.from<Node>(codeEditor.childNodes);

      while (anchorNode.parentNode !== codeEditor) {
        // reach the direct child of codeEditor
        anchorNode = anchorNode.parentNode as Node;
      }
      const anchorNodeIndex = siblings.indexOf(anchorNode);
      const linesInAnchor =
        (anchorNode.textContent as string)
          .slice(0, selection.anchorOffset)
          .split("\n").length - 1;
      const precedingLines = siblings
        .slice(0, anchorNodeIndex)
        .reduce(
          (lineCount, sibling) =>
            lineCount + (sibling.textContent as string).split("\n").length - 1,
          linesInAnchor
        );

      while (focusNode.parentNode !== codeEditor) {
        // reach the direct child of codeEditor
        focusNode = focusNode.parentNode as Node;
      }
      const focusNodeIndex = siblings.indexOf(focusNode);

      const linesInFocusNode =
        (focusNode.textContent as string)
          .slice(0, selection.focusOffset)
          .split("\n").length - 1;
      const selectedLines = siblings
        .slice(0, focusNodeIndex)
        .reduce(
          (lineCount, sibling) =>
            lineCount + (sibling.textContent as string).split("\n").length - 1,
          linesInFocusNode
        );

      this.$emit("update:explainFrom", precedingLines + 1);
      this.$emit("update:explainTill", selectedLines + 1);
    },
    onMouseMove(e: MouseEvent) {
      const codeEditor = this.$refs.codeEditor as HTMLPreElement;
      const boundingRect = codeEditor.getBoundingClientRect();
      const topPx = e.clientY - boundingRect.top;
      const lineNo = Math.round(topPx / this.fontSize / 1.5); // line height = 1.5

      for (const expLocation of this.uniqueExplanationLocations) {
        const [from, to] = expLocation;
        if (from <= lineNo && lineNo <= to) {
          if (this.currentlyFocusedCodeSegment) {
            if (this.currentlyFocusedCodeSegment.toString() !== expLocation.toString()) {
              eventBus.emit("focusHighlight", [from, to]);
              eventBus.emit("blurHighlight", this.currentlyFocusedCodeSegment);
              this.currentlyFocusedCodeSegment = expLocation;
            }
          } else {
            eventBus.emit("focusHighlight", [from, to]);
            this.currentlyFocusedCodeSegment = expLocation;
          }

          break;
        }
      }
    },
  },
});
</script>
<style lang="scss" scoped>
code:focus-visible {
  outline: none;
}
</style>
