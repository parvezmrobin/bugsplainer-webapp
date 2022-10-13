import mitt from "mitt";

export type Events = {
  focusHighlight: [number, number];
  blurHighlight: [number, number];
};
export const eventBus = mitt<Events>();

export type ExperimentalFileContent = {
  content: string;
  start: number[];
  end: number[];
  commit_message: string[];
};
