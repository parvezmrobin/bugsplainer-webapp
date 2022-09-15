<script setup lang="ts">
import "bootstrap";
import axios from "axios";
import Home from "./views/Home.vue";

axios.defaults.baseURL = origin.replace(/:\d+/, ":5000");
</script>

<template>
  <Home />
</template>

<style lang="scss">
@import "../node_modules/bootstrap/scss/bootstrap";
</style>
