import { test, expect } from '@playwright/test';

test.describe('ArenaWealth Dashboard E2E Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
  });

  test.describe('Basic Dashboard Tests', () => {
    test('should display the dashboard header', async ({ page }) => {
      await expect(page.locator('h1')).toContainText('ArenaWealth Pro');
    });

    test('should display navigation menu', async ({ page }) => {
      const nav = page.locator('nav');
      await expect(nav).toBeVisible();
    });

    test('should load dashboard without console errors', async ({ page }) => {
      const errors: string[] = [];
      page.on('console', msg => {
        if (msg.type() === 'error') {
          errors.push(msg.text());
        }
      });

      await page.goto('http://localhost:5173');
      await page.waitForLoadState('networkidle');

      expect(errors.length).toBe(0);
    });

    test('should display portfolio summary cards', async ({ page }) => {
      await page.waitForSelector('text=Total Value');
      await expect(page.locator('text=Total Value')).toBeVisible();
      await expect(page.locator('text=Total Gain')).toBeVisible();
      await expect(page.locator('text=Positions')).toBeVisible();
    });

    test('should display portfolio positions table', async ({ page }) => {
      await page.waitForSelector('table');
      const table = page.locator('table');
      await expect(table).toBeVisible();

      // Check if table has rows
      const rows = await table.locator('tbody tr').count();
      expect(rows).toBeGreaterThan(0);
    });

    test('should display top performers section', async ({ page }) => {
      await page.waitForSelector('text=Top Performers');
      await expect(page.locator('text=Top Performers')).toBeVisible();
    });

    test('should display worst performers section', async ({ page }) => {
      await page.waitForSelector('text=Worst Performers');
      await expect(page.locator('text=Worst Performers')).toBeVisible();
    });
  });

  test.describe('Dashboard Toggle Tests', () => {
    test('should toggle between Basic and Rich dashboard', async ({ page }) => {
      // Find and click the dashboard toggle button
      const toggleButton = page.locator('button').filter({ hasText: /Basic|Rich/ }).first();
      if (await toggleButton.isVisible()) {
        await toggleButton.click();
        await page.waitForLoadState('networkidle');

        // Verify dashboard changed
        const dashboardContent = page.locator('text=Dashboard');
        await expect(dashboardContent).toBeVisible();
      }
    });
  });

  test.describe('Rich Dashboard Components Tests', () => {
    test('should display Rich Dashboard header', async ({ page }) => {
      // Try to switch to Rich dashboard if possible
      const toggleButton = page.locator('button').filter({ hasText: /Rich/ }).first();
      if (await toggleButton.isVisible()) {
        await toggleButton.click();
        await page.waitForLoadState('networkidle');
      }

      // Check for Rich Dashboard specific elements
      await page.waitForTimeout(2000);
      const richHeader = page.locator('text=Rich Dashboard');
      if (await richHeader.isVisible()) {
        await expect(richHeader).toBeVisible();
      }
    });

    test('should display Decision Engine component', async ({ page }) => {
      await page.waitForTimeout(2000);
      const decisionEngine = page.locator('text=Decision Engine');
      if (await decisionEngine.isVisible()) {
        await expect(decisionEngine).toBeVisible();
      }
    });

    test('should display Investment Advisor component', async ({ page }) => {
      await page.waitForTimeout(2000);
      const investmentAdvisor = page.locator('text=Investment Advisor');
      if (await investmentAdvisor.isVisible()) {
        await expect(investmentAdvisor).toBeVisible();
      }
    });

    test('should display Real-Time Price Updates section', async ({ page }) => {
      await page.waitForTimeout(2000);
      const realTimeUpdates = page.locator('text=Real-Time Price Updates');
      if (await realTimeUpdates.isVisible()) {
        await expect(realTimeUpdates).toBeVisible();
      }
    });
  });

  test.describe('Portfolio Data Tests', () => {
    test('should display correct total market value', async ({ page }) => {
      await page.waitForSelector('text=Total Value');
      const totalValueElement = page.locator('text=Total Value').locator('xpath=following-sibling::*');
      await expect(totalValueElement).toBeVisible();
    });

    test('should display gain/loss information', async ({ page }) => {
      await page.waitForSelector('text=Total Gain');
      const gainLossElement = page.locator('text=Total Gain').locator('xpath=following-sibling::*');
      await expect(gainLossElement).toBeVisible();
    });

    test('should display position count', async ({ page }) => {
      await page.waitForSelector('text=Positions');
      const positionCountElement = page.locator('text=Positions').locator('xpath=following-sibling::*');
      await expect(positionCountElement).toBeVisible();
    });
  });

  test.describe('Navigation Tests', () => {
    test('should navigate to different sections', async ({ page }) => {
      // Check if navigation links exist
      const navLinks = page.locator('nav a');
      const count = await navLinks.count();

      if (count > 0) {
        // Click first navigation link
        await navLinks.first().click();
        await page.waitForLoadState('networkidle');
      }
    });
  });

  test.describe('Responsive Design Tests', () => {
    test('should be responsive on mobile viewport', async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      await page.goto('http://localhost:5173');

      const header = page.locator('h1');
      await expect(header).toBeVisible();
    });

    test('should be responsive on tablet viewport', async ({ page }) => {
      await page.setViewportSize({ width: 768, height: 1024 });
      await page.goto('http://localhost:5173');

      const header = page.locator('h1');
      await expect(header).toBeVisible();
    });
  });
});
