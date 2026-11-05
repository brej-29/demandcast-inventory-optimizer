import { analyze } from "./engine.js";
self.onmessage = ({ data }) => {
  try {
    self.postMessage({
      id: data.id,
      result: analyze(data.series, data.settings),
    });
  } catch (error) {
    self.postMessage({ id: data.id, error: error.message });
  }
};
