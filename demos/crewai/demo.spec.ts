import { test, expect } from '@playwright/test';
import { createAgentViaUI } from '../shared/helpers';
import path from 'path';

const SCREENSHOTS = path.join(__dirname, 'screenshots');

test('CrewAI — create agent via UI, deploy, chat', async ({ page }) => {
  await createAgentViaUI(page, {
    name: 'demo-crewai',
    team: 'showcase',
    framework: 'crewai',
    model: 'claude-sonnet-4-6',
    screenshotDir: SCREENSHOTS,
  });

  const { existsSync } = await import('fs');
  for (const shot of ['builder-config', 'yaml-preview', 'deployed', 'ejected-sdk', 'chat-response']) {
    expect(existsSync(path.join(SCREENSHOTS, `${shot}.png`))).toBe(true);
  }
});
