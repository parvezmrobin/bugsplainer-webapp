<template>
  <div class="form-floating">
    <select
      class="form-select"
      id="modelName"
      v-model="selectedModel"
      aria-label="Select Model Name"
    >
      <option :value="modelId" v-for="(model, modelId) in models">
        {{ model }}
      </option>
    </select>
    <label for="modelName">Works with selects</label>
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
      models: {} as Record<string, string>,
      selectedModel: "",
    };
  },
  watch: {
    selectedModel() {
      this.$emit('change', this.models[this.selectedModel]);
    },
  },
  async created() {
    try {
      const modelsResp = await axios.get<{ models: Record<string, string> }>(
        "/models"
      );
      this.models = modelsResp.data.models;
      this.selectedModel = "Bugsplainer";
    } catch (e) {
      console.error(e);
    }
  },
});
</script>

<style scoped lang="scss"></style>
