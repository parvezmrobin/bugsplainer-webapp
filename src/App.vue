<script setup lang="ts">
import axios from "axios";
axios.defaults.baseURL = origin.replace(/:\d+/, ':5000');
console.log(axios.defaults.baseURL)
import Home from "./views/Home.vue";
</script>

<template>
  <Home />
</template>

<style lang="scss">
@import "../node_modules/bootstrap/scss/bootstrap";
</style>
