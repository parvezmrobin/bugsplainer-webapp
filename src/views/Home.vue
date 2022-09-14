<script setup lang="ts">
import hljs from "highlight.js/lib/core";
import python from "highlight.js/lib/languages/python";
import { computed, nextTick, ref, watch } from "vue";

import Highlighter from "../components/Highlighter.vue";
import Explanations, { Explanation } from "../components/Explanations.vue";
import ModelName from "../components/ModelName.vue";

hljs.registerLanguage("python", python);

const fileContent = ref("");
const codeEditor = ref<HTMLDivElement>();
const explainFrom = ref<number>();
const explainTill = ref<number>();

const explanations = ref<Explanation[]>([]);

const highlightedLines = computed(() => {
  const highlightedLines = explanations.value.map((exp) => [exp.from, exp.to]);
  if (explainFrom.value && explainTill.value) {
    highlightedLines.push([explainFrom.value, explainTill.value]);
  }

  return highlightedLines;
});

function readFile(event: Event) {
  let files = (event.target as HTMLInputElement).files as FileList;
  const file = files[0];
  const reader = new FileReader();

  reader.onload = function () {
    if (reader.result === null) {
      throw new Error("The file reads to null");
    }
    fileContent.value = reader.result.toString();
  };
  reader.onerror = function () {
    throw new Error("Cannot read the file");
  };

  reader.readAsText(file, "utf-8");
}

function highlightCode() {
  if (!codeEditor.value) {
    throw new Error();
  }
  hljs.highlightElement(codeEditor.value);
}

watch(fileContent, async () => {
  await nextTick();
  highlightCode();
});

function onMouseUp() {
  const selection = window.getSelection();
  if (selection === null || codeEditor.value === undefined) {
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

  const siblings = Array.from<Node>(codeEditor.value.childNodes);

  while (anchorNode.parentNode !== codeEditor.value) {
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

  while (focusNode.parentNode !== codeEditor.value) {
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

  explainFrom.value = precedingLines + 1;
  explainTill.value = selectedLines + 1;
}

function explain() {
  if (!explainFrom.value || !explainTill.value) {
    return;
  }
  explanations.value.push({
    from: explainFrom.value,
    to: explainTill.value,
    explanation: `This is an explanation from line ${explainFrom.value} to ${explainTill.value}`,
  });
}
</script>

<template>
  <div class="container-fluid">
    <form class="row gy-2 gx-3 align-items-center" @submit.prevent="explain">
      <div class="col-auto">
        <input
          type="file"
          class="form-control"
          style="height: calc(3.5rem + 2px); line-height: 3.5rem"
          @change="readFile"
        />
      </div>
      <div class="col-auto">
        <div class="form-floating">
          <input
            type="number"
            class="form-control"
            id="explainFrom"
            v-model="explainFrom"
            placeholder="Explain From"
          />
          <label for="explainFrom">Explain From</label>
        </div>
      </div>
      <div class="col-auto">
        <div class="form-floating">
          <input
            type="number"
            class="form-control"
            id="explainTill"
            v-model="explainTill"
            placeholder="Explain Till"
          />
          <label for="explainTill">Explain Till</label>
        </div>
      </div>
      <div class="col-auto">
        <ModelName />
      </div>
      <div class="col-auto">
        <button type="submit" class="btn btn-primary">Explain</button>
      </div>
    </form>
    <div class="row gx-0">
      <div class="col-auto">
        <pre v-show="fileContent">
          <code class="hljs" style=" text-align: right;">{{
              fileContent.split('\n').map((_, i) => i).slice(1).join('\n')
            }}</code>
        </pre>
      </div>
      <div class="col">
        <pre style="position: relative; overflow: hidden">
          <code
              class="language-python"
              ref="codeEditor"
              contenteditable="true"
              @mouseup="onMouseUp"
              @focusout="highlightCode"
          >{{ fileContent }}</code>
          <Highlighter :lines="highlightedLines"/>
        </pre>
      </div>
      <div class="col">
        <Explanations :explanations="explanations" />
      </div>
    </div>
  </div>
</template>

<style lang="scss">
@import "highlight.js/scss/atom-one-light";

.hljs {
  background-color: transparent;
}
</style>

<style lang="scss" scoped>
code:focus-visible {
  outline: none;
}
</style>
