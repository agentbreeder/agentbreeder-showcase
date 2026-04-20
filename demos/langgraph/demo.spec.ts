import { test, expect } from '@playwright/test';
import { createAgentViaUI } from '../shared/helpers';
import path from 'path';

const SCREENSHOTS = path.join(__dirname, 'screenshots');

test('LangGraph + Ollama — create agent via UI, deploy, chat', async ({ page }) => {
  await createAgentViaUI(page, {
    name: 'demo-langgraph',
    team: 'showcase',
    framework: 'langgraph',
    model: 'ollama/gemma4',
    screenshotDir: SCREENSHOTS,
  });

  const { existsSync } = await import('fs');
  for (const shot of ['builder-config', 'yaml-preview', 'deployed', 'ejected-sdk', 'chat-response']) {
    expect(existsSync(path.join(SCREENSHOTS, `${shot}.png`))).toBe(true);
  }
});
