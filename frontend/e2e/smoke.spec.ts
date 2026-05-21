import { expect, test } from '@playwright/test';

test.describe('ArenaWealth workbench', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/?offline_demo=true');
  });

  test('loads the reviewer workbench', async ({ page }) => {
    await expect(page.getByRole('heading', { name: 'ArenaWealth Pro' })).toBeVisible();
    await expect(page.locator('aside[aria-label="Workspace navigation"]')).toBeVisible();
    await expect(page.getByText('Allocation queue')).toBeVisible();
    await expect(page.getByText('Portfolio positions')).toBeVisible();
  });

  test('updates the cash deployment request', async ({ page }) => {
    await page.getByLabel('Available cash').fill('1000');
    await page.getByRole('button', { name: 'Analyze' }).click();
    await expect(page.getByText('$1,000.00 queued')).toBeVisible();
  });

  test('shows deterministic reviewer mode', async ({ page }) => {
    await page.getByLabel('Deterministic reviewer mode').check();
    await page.getByRole('button', { name: 'Analyze' }).click();
    await expect(page.getByText('offline-demo')).toBeVisible();
  });

  test('renders on a mobile viewport', async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto('/?offline_demo=true');
    await expect(page.getByRole('heading', { name: 'ArenaWealth Pro' })).toBeVisible();
    await expect(page.getByText('Deploy cash')).toBeVisible();
  });
});
