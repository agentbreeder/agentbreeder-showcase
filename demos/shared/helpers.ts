import { Page } from '@playwright/test';
import { mkdirSync, existsSync } from 'fs';
import path from 'path';

export async function waitForDashboard(page: Page): Promise<void> {
  await page.waitForSelector('text=AgentBreeder', { timeout: 15_000 });
}

export async function takeScreenshot(page: Page, filepath: string): Promise<void> {
  await page.screenshot({ path: filepath, fullPage: false });
}

export async function createAgentViaUI(
  page: Page,
  opts: {
    name: string;
    team: string;
    framework: string;
    model: string;
    screenshotDir: string;
  }
): Promise<void> {
  const { name, team, framework, model, screenshotDir } = opts;

  if (!existsSync(screenshotDir)) {
    mkdirSync(screenshotDir, { recursive: true });
  }

  // Navigate to dashboard
  await page.goto('/');
  await waitForDashboard(page);

  // Open new agent form
  await page.locator('button:has-text("New Agent"), a:has-text("New Agent")').click();
  await page.waitForSelector('[name="agent-name"], [placeholder*="agent name"]', { timeout: 10_000 });

  // Fill identity fields
  const nameField = page.locator('[name="agent-name"], [placeholder*="agent name"]').first();
  await nameField.fill(name);

  const teamField = page.locator('[name="team"], [placeholder*="team"]').first();
  await teamField.fill(team);

  // Select framework
  const frameworkSelect = page.locator('select[name="framework"], [data-testid="framework-select"]').first();
  await frameworkSelect.selectOption(framework);

  // Select model
  const modelField = page.locator('[name="model"], [placeholder*="model"], [data-testid="model-input"]').first();
  await modelField.fill(model);

  await takeScreenshot(page, path.join(screenshotDir, 'builder-config.png'));

  // Preview YAML
  await page.locator('button:has-text("Preview YAML"), [data-testid="preview-yaml"]').click();
  await page.waitForSelector('pre, code', { timeout: 5_000 });
  await takeScreenshot(page, path.join(screenshotDir, 'yaml-preview.png'));

  // Deploy
  await page.locator('button:has-text("Deploy"), [data-testid="deploy-btn"]').click();
  await page.locator('[data-status="running"], :has-text("running"), :has-text("deployed")').waitFor({ timeout: 90_000 });
  await takeScreenshot(page, path.join(screenshotDir, 'deployed.png'));

  // Eject to SDK
  await page.locator('button:has-text("Eject"), [data-testid="eject-btn"]').click();
  await page.locator('button:has-text("SDK"), [data-testid="eject-sdk"]').click();
  await page.waitForSelector('pre, code', { timeout: 10_000 });
  await takeScreenshot(page, path.join(screenshotDir, 'ejected-sdk.png'));

  // Chat panel
  await page.locator('button:has-text("Chat"), [data-testid="chat-btn"]').click();
  const chatInput = page.locator('[name="message"], [placeholder*="message"], textarea').first();
  await chatInput.fill('What are the top 3 benefits of AI agents in enterprise?');
  await chatInput.press('Enter');
  await page.locator('.agent-response, [data-testid="agent-response"], .message-content').waitFor({ timeout: 60_000 });
  await takeScreenshot(page, path.join(screenshotDir, 'chat-response.png'));
}
