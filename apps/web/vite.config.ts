import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const target = loadEnv(mode, process.cwd(), "").LUMEN_API_TARGET || "http://127.0.0.1:8000";
  return {
    server: {
      proxy: {
        "/health": target,
        "/api": target,
      },
    },
  };
});
