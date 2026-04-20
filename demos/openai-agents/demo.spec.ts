import { test, expect } from '@playwright/test';
import { createAgentViaUI } from '../shared/helpers';
import path from 'path';

const SCREENSHOTS = path.join(__dirname, 'screenshots');

test('OpenAI Agents SDK — create agent via UI, deploy, chat', async ({ page }) => {
  await createAgentViaUI(page, {
    name: 'demo-openai-agents',
    team: 'showcase',
    framework: 'openai_agents',
    model: 'gpt-5.2',
    screenshotDir: SCREENSHOTS,
  });

  const { existsSync } = await import('fs');
  for (const shot of ['builder-config', 'yaml-preview', 'deployed', 'ejected-sdk', 'chat-response']) {
    expect(existsSync(path.join(SCREENSHOTS, `${shot}.png`))).toBe(true);
  }
});
