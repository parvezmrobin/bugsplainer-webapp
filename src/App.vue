<template>
  <Home />
</template>

<script setup lang="ts">
import axios from "axios";
import Home from "./views/Home.vue";

axios.defaults.baseURL = origin.replace(/:\d+/, ":5002");
</script>

<style lang="scss">
$enable-negative-margins: true;
$accordion-padding-y: 0.5rem;
$accordion-padding-x: 0.5rem;
@import "../node_modules/bootstrap/scss/bootstrap";

$all-colors: map-merge-multiple(
  $blues,
  $indigos,
  $purples,
  $pinks,
  $reds,
  $oranges,
  $yellows,
  $greens,
  $teals,
  $cyans
);

:root {
  @each $name, $color in $all-colors {
    --bs-#{$name}: #{$color};
  }
}
</style>
