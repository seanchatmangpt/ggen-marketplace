import { defineConfig } from "@playwright/test";

/**
 * Spatial-court Playwright config — anti-vacuity mutants are self-contained
 * (`page.setContent`) and do not need a live app server. Matrix tests that
 * `page.goto("/")` require a consumer baseURL; run them under the host app.
 */
export default defineConfig({
  testDir: "./tests/e2e/spatial",
  testMatch: "**/*.spec.ts",
  timeout: 30_000,
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  reporter: [["list"]],
  use: {
    headless: true,
    viewport: { width: 375, height: 667 },
  },
  projects: [{ name: "chromium", use: { browserName: "chromium" } }],
});
