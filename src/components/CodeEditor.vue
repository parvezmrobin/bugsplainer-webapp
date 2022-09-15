<template>
  <pre style="position: relative; overflow: visible">
          <code
              class="language-python"
              ref="codeEditor"
              contenteditable="true"
              @mouseup="onMouseUp"
              @focusout="highlightCode"
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

  emits: {
    "update:explainFrom": Number,
    "update:explainTill": Number,
  },

  computed: {
    highlightedLines() {
      const highlightedLines = this.explanations.map((exp) => [
        exp.from,
        exp.to,
      ]);
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
  },
});
</script>
<style lang="scss" scoped>
code:focus-visible {
  outline: none;
}
</style>
