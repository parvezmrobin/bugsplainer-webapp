<template>
  <Navbar
    v-model:fileContent="fileContent"
    v-model:explainFrom="explainFrom"
    v-model:explainTill="explainTill"
    v-model:isExperimental="isExperimental"
    @newExplanation="onNewExplanation"
  />
  <div class="container-fluid">
    <div class="row gx-0">
      <div class="col-auto">
        <pre v-show="fileContent">
          <code class="hljs" style=" text-align: right;">{{
              fileContent.split('\n').map((_, i) => i).slice(1).join('\n')
            }}</code>
        </pre>
      </div>
      <div class="col" style="max-width: 60%">
        <CodeEditor
          v-model:explain-from="explainFrom"
          v-model:explain-till="explainTill"
          v-model:fileContent="fileContent"
          :explanations="explanations"
        />
      </div>
      <div class="col">
        <Explanations :explanations="explanations" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from "vue";
import CodeEditor from "../components/CodeEditor.vue";
import Explanations, {
  IExplanationEntry,
} from "../components/Explanations.vue";
import Navbar, { IExplanationResp } from "../components/Navbar.vue";

const fileContent = ref("");
const explainFrom = ref<number>(NaN);
const explainTill = ref<number>(NaN);
const isExperimental = ref(false);

const explanations = ref<IExplanationEntry[]>([]);

watch(fileContent, () => {
  explanations.value = [];
  explainFrom.value = NaN;
  explainTill.value = NaN;
});

function onNewExplanation(explanation: IExplanationResp) {
  const from = explanation.from ?? explainFrom.value;
  const to = explanation.to ?? explainTill.value;
  if (!from || !to) {
    throw new Error("Explanation range was cleared while fetching explanation");
  }

  explanations.value.push({
    from,
    to,
    model: explanation.model,
    explanations: explanation.explanations,
  });
}
</script>

<style lang="scss">
@import "highlight.js/scss/atom-one-light";

.hljs {
  background-color: transparent;
}
</style>

<style lang="scss" scoped>
h3 {
  color: var(--bs-purple-600);
}
</style>
