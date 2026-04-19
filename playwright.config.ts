import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './demos',
  timeout: 120_000,
  retries: 1,
  workers: 5,
  use: {
    baseURL: 'http://localhost:3001',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  reporter: [['html', { outputFolder: 'playwright-report' }]],
});
