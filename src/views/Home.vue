<script setup lang="ts">
import hljs from "highlight.js/lib/core";
import python from "highlight.js/lib/languages/python";
import { nextTick, ref, watch } from "vue";

hljs.registerLanguage("python", python);

const fileContent = ref("");
const codeEditor = ref<HTMLDivElement>();
const explainFrom = ref<number>();
const explainTill = ref<number>();

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
  const siblings = Array.from<Node>(codeEditor.value.childNodes);
  let anchorNode = selection.anchorNode as Node;
  while (anchorNode.parentNode !== codeEditor.value) {
    // reach the direct child of codeEditor
    anchorNode = anchorNode.parentNode as Node;
  }
  const anchorNodeIndex = siblings.indexOf(anchorNode);
  const precedingLines = siblings
    .slice(0, anchorNodeIndex)
    .reduce(
      (lineCount, sibling) =>
        lineCount + (sibling.textContent as string).split("\n").length - 1,
      0
    );

  let focusNode = selection.focusNode as Node;
  while (focusNode.parentNode !== codeEditor.value) {
    // reach the direct child of codeEditor
    focusNode = focusNode.parentNode as Node;
  }
  const focusNodeIndex = siblings.indexOf(focusNode);

  const selectedLines = siblings
    .slice(0, focusNodeIndex)
    .reduce(
      (lineCount, sibling) =>
        lineCount + (sibling.textContent as string).split("\n").length - 1,
      0
    );

  explainFrom.value = precedingLines + 1;
  explainTill.value = selectedLines + 1;
}
</script>

<template>
  <div class="container-fluid">
    <form class="row gy-2 gx-3 align-items-center">
      <div class="col-auto">
        <input
          type="file"
          class="form-control"
          style="height: calc(3.5rem + 2px); line-height: 3.5rem;"
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
        <button type="submit" class="btn btn-primary">Explain</button>
      </div>
    </form>
    <div class="row">
      <pre>
          <code
              class="language-python"
              ref="codeEditor"
              contenteditable="true"
              @mouseup="onMouseUp"
              @focusout="highlightCode"
          >{{ fileContent }}</code>
      </pre>
    </div>
  </div>
</template>

<style lang="scss">
@import "highlight.js/scss/monokai";
</style>
