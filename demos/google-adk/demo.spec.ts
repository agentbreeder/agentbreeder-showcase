import { test, expect } from '@playwright/test';
import { createAgentViaUI } from '../shared/helpers';
import path from 'path';

const SCREENSHOTS = path.join(__dirname, 'screenshots');

test('Google ADK — create agent via UI, deploy, chat', async ({ page }) => {
  await createAgentViaUI(page, {
    name: 'demo-google-adk',
    team: 'showcase',
    framework: 'google_adk',
    model: 'gemini-3.0-flash',
    screenshotDir: SCREENSHOTS,
  });

  const { existsSync } = await import('fs');
  for (const shot of ['builder-config', 'yaml-preview', 'deployed', 'ejected-sdk', 'chat-response']) {
    expect(existsSync(path.join(SCREENSHOTS, `${shot}.png`))).toBe(true);
  }
});
