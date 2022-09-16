/* eslint-disable @typescript-eslint/ban-types,@typescript-eslint/no-explicit-any */
/// <reference types="vite/client" />

declare module "*.vue" {
  import type { DefineComponent } from "vue";
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
