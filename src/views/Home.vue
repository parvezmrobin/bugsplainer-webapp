<script setup lang="ts">
import { ref } from "vue";
import Explanations, {
  IExplanationEntry,
  IScoredExplanation,
} from "../components/Explanations.vue";
import ModelName from "../components/ModelName.vue";
import axios from "axios";
import CodeEditor from "../components/CodeEditor.vue";

const fileContent = ref("");
const explainFrom = ref<number>();
const explainTill = ref<number>();
const explanationModel = ref("");

const explanations = ref<IExplanationEntry[]>([]);

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

interface IExplanationResp {
  model: string;
  explanations: IScoredExplanation[];
}

async function explain() {
  if (!explainFrom.value || !explainTill.value) {
    return;
  }
  try {
    const explainResp = await axios.post<IExplanationResp>("/explain", {
      code: fileContent.value,
      start: explainFrom.value,
      end: explainTill.value,
      model: explanationModel.value,
    });
    const explanation = explainResp.data;
    explanations.value.push({
      from: explainFrom.value,
      to: explainTill.value,
      model: explanation.model,
      explanations: explanation.explanations,
    });
  } catch (e) {
    console.error(e);
  }
}
</script>

<template>
  <div class="container-fluid">
    <div class="row px-5">
      <h3>
        Bugsplainer
      </h3>
    </div>
    <form
      class="row px-5 gy-2 gx-3 align-items-center"
      @submit.prevent="explain"
    >
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
        <ModelName @change="explanationModel = $event" />
      </div>
      <div class="col-auto">
        <button
          type="submit"
          class="btn btn-primary"
          :disabled="!explainFrom || !explainTill"
        >
          Explain
        </button>
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
        <CodeEditor
          :file-content="fileContent"
          :explanations="explanations"
          v-model:explain-from="explainFrom"
          v-model:explain-till="explainTill"
        />
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
h3 {
  color: var(--bs-purple-600)
}
</style>
