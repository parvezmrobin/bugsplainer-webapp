<template>
  <div class="d-flex flex-column justify-content-center border rounded h-100">
    <div class="dropdown">
      <button
        class="btn dropdown-toggle"
        type="button"
        data-bs-toggle="dropdown"
        aria-expanded="false"
      >
        Select A Sample File
      </button>
      <ul class="dropdown-menu">
        <li v-for="filename in filenames" :key="filename">
          <a
            class="dropdown-item"
            role="button"
            @click="selectedFilename = filename"
          >
            <span class="text-muted">
              {{ filename.substring(0, filename.lastIndexOf("/") + 1) }} </span
            >{{ filename.substring(filename.lastIndexOf("/") + 1) }}
          </a>
        </li>
      </ul>
    </div>

    <div v-show="selectedFilename" class="px-3 font-monospace mt-n1">
      .../{{ selectedFilename.split("/").slice(-1)[0] }}
    </div>
  </div>
</template>

<script lang="ts" setup>
import axios from "axios";
import { computed, ref, watch } from "vue";

const filenames = ref<string[]>([]);
const selectedFilename = ref<string>("");
const emit = defineEmits(["update:fileContent"]);

async function loadFiles() {
  try {
    const filesResponse = await axios.get("/experimental/files");
    filenames.value = filesResponse.data.files;
  } catch (e) {
    console.error(e);
  }
}

watch(selectedFilename, async () => {
  try {
    const filesResponse = await axios.get(
      "/experimental/file?path=" + encodeURI(selectedFilename.value)
    );
    const fileContent = filesResponse.data.content;
    emit("update:fileContent", fileContent);
  } catch (e) {
    console.error(e);
  }
});

// noinspection JSUnusedGlobalSymbols
const dropdownToggleColor = computed(() => {
  const color = selectedFilename.value ? "--bs-secondary" : "--bs-body-color";
  return `var(${color})`;
});

// noinspection JSUnusedGlobalSymbols
const dropdownToggleFontSize = computed(() => {
  return selectedFilename.value ? "0.8rem" : "1rem";
});

loadFiles();
</script>

<style scoped lang="scss">
.d-flex {
  background-color: white;
}

.dropdown-toggle,
.dropdown-toggle:hover,
.dropdown-toggle:focus,
.dropdown-toggle.show {
  color: v-bind("dropdownToggleColor");
  font-size: v-bind("dropdownToggleFontSize");
  border-color: transparent;
}

.dropdown-item {
  font-family: var(--bs-font-monospace);
}
</style>
