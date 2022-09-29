<template>
  <div class="navbar bg-light px-5">
    <h3>Bugsplainer</h3>
    <div class="form-check form-switch">
      <input
        id="isExperimental"
        class="form-check-input"
        type="checkbox"
        :value="isExperimental"
        @change="$emit('update:isExperimental', $event.target.value)"
      />
      <label class="form-check-label text-warning" for="isExperimental">
        Experimental UI
      </label>
    </div>
  </div>
  <nav class="navbar sticky-top bg-light">
    <form
      class="row px-5 gy-2 gx-3 align-items-stretch"
      @submit.prevent="explain"
    >
      <div class="col">
        <SelectExperimentalFiles
          v-if="isExperimental"
          @update:fileContent="$emit('update:fileContent', $event)"
        />
        <input
          v-else
          type="file"
          class="form-control"
          style="height: calc(3.5rem + 2px); line-height: 3.5rem"
          @change="readFile"
        />
      </div>
      <div class="col">
        <div class="form-floating">
          <input
            id="explainFrom"
            type="number"
            class="form-control"
            placeholder="Explain From"
            :value="explainFrom"
            @input="$emit('update:explainFrom', $event.target.value)"
          />
          <label for="explainFrom">Explain From</label>
        </div>
      </div>
      <div class="col">
        <div class="form-floating">
          <input
            id="explainTill"
            type="number"
            class="form-control"
            :value="explainTill"
            placeholder="Explain Till"
            @input="$emit('update:explainTill', $event.target.value)"
          />
          <label for="explainTill">Explain Till</label>
        </div>
      </div>
      <div class="col-auto">
        <ModelName @change="explanationModel = $event" />
      </div>
      <div ref="tooltipRef" class="col-auto">
        <button
          type="submit"
          class="btn btn-primary"
          style="height: calc(3.5rem + 2px); width: 4.5rem"
          :disabled="explanationRequirement || fetchingExplanation"
        >
          <span
            v-if="fetchingExplanation"
            class="spinner-grow text-info"
            role="status"
          >
            <span class="visually-hidden">Loading...</span>
          </span>
          <template v-else> Explain </template>
        </button>
      </div>
    </form>
  </nav>
</template>

<script lang="ts">
import axios from "axios";
import { Tooltip } from "bootstrap";
import { defineComponent } from "vue";
import type { IScoredExplanation } from "./Explanations.vue";
import ModelName from "./ModelName.vue";
import SelectExperimentalFiles from "./SelectExperimentalFiles.vue";

export interface IExplanationResp {
  model: string;
  explanations: IScoredExplanation[];
}
let tooltip: Tooltip;

export default defineComponent({
  name: "Navbar",
  components: { SelectExperimentalFiles, ModelName },
  props: {
    fileContent: {
      required: true,
      type: String,
    },
    explainFrom: {
      required: true,
      type: Number,
    },
    explainTill: {
      required: true,
      type: Number,
    },
    isExperimental: {
      required: true,
      type: Boolean,
    },
  },
  emits: [
    "newExplanation",
    "update:fileContent",
    "update:explainFrom",
    "update:explainTill",
    "update:isExperimental",
  ],
  data() {
    return {
      explanationModel: "",
      fetchingExplanation: false,
    };
  },
  computed: {
    explanationRequirement() {
      if (!this.fileContent) {
        return "Please select a source code file";
      }

      if (!this.explainFrom || !this.explainTill) {
        return "Please select the a source code segment to explain";
      }

      return null;
    },
  },
  watch: {
    explanationRequirement() {
      if (!this.explanationRequirement) {
        tooltip.disable();
      } else {
        tooltip.enable();
        tooltip.setContent({ ".tooltip-inner": this.explanationRequirement });
      }
    },
  },
  mounted() {
    if (!this.$refs.tooltipRef) {
      throw new Error("tooltipRef is empty");
    }
    tooltip = new Tooltip(this.$refs.tooltipRef as HTMLDivElement, {
      title: this.explanationRequirement || "",
    });
  },
  beforeUnmount() {
    tooltip.dispose();
  },
  methods: {
    readFile(event: Event) {
      const files = (event.target as HTMLInputElement).files as FileList;
      const file = files[0];
      const reader = new FileReader();

      reader.onload = () => {
        if (reader.result === null) {
          throw new Error("The file reads to null");
        }
        this.$emit("update:fileContent", reader.result.toString());
      };
      reader.onerror = function () {
        throw new Error("Cannot read the file");
      };

      reader.readAsText(file, "utf-8");
    },
    async explain() {
      if (!this.explainFrom || !this.explainTill) {
        return;
      }
      try {
        this.fetchingExplanation = true;
        const explainResp = await axios.post<IExplanationResp>("/explain", {
          code: this.fileContent,
          start: Number(this.explainFrom),
          end: Number(this.explainTill),
          model: this.explanationModel,
        });
        const explanation = explainResp.data;
        this.$emit("newExplanation", explanation);
      } catch (e) {
        console.error(e);
      }

      this.fetchingExplanation = false;
    },
  },
});
</script>
<style lang="scss" scoped>
h3 {
  color: var(--bs-purple-600);
}

.form-check-input:checked {
  background-color: var(--bs-warning);
  border-color: var(--bs-warning);
}
</style>
