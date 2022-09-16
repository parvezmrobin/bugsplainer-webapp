import mitt from "mitt";

export type Events = {
  focusHighlight: [number, number];
  blurHighlight: [number, number];
};
export const eventBus = mitt<Events>();
