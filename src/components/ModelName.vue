<template>
  <div class="form-floating">
    <select
      id="modelName"
      v-model="selectedModel"
      class="form-select"
      aria-label="Select Model Name"
    >
      <option v-for="model in models" :key="model" :value="model">
        {{ model }}
      </option>
    </select>
    <label for="modelName">Select Explainer Model</label>
  </div>
</template>

<script lang="ts">
import axios from "axios";
import { defineComponent } from "vue";

export default defineComponent({
  name: "ModelName",
  emits: {
    change: String,
  },
  data() {
    return {
      models: {} as string[],
      selectedModel: "",
    };
  },
  watch: {
    selectedModel() {
      this.$emit("change", this.selectedModel);
    },
  },
  async created() {
    try {
      const modelsResp = await axios.get<{ models: string[] }>("/models");
      this.models = modelsResp.data.models;
      this.selectedModel = "Bugsplainer";
    } catch (e) {
      console.error(e);
    }
  },
});
</script>

<style scoped lang="scss"></style>
