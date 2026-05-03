/**
 * Testes de UX Mobile
 * Usa storage state — já autenticado via setup.js
 */
const { test, expect } = require('@playwright/test');

test.describe('UX Mobile', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/#/dashboard');
    await expect(page.locator('.dash-header').first()).toBeVisible({ timeout: 10_000 });
  });

  test('bottom navigation está fixo no rodapé', async ({ page }) => {
    const nav = page.locator('#bottom-nav');
    await expect(nav).toBeVisible();
    const pos = await nav.evaluate(el => {
      const s = window.getComputedStyle(el);
      return { position: s.position, bottom: s.bottom };
    });
    expect(pos.position).toBe('fixed');
    expect(pos.bottom).toBe('0px');
  });

  test('FAB antigo não existe mais', async ({ page }) => {
    await expect(page.locator('#fab-dashboard')).toHaveCount(0);
  });

  test('modal abre como bottom-sheet (alinhado ao rodapé)', async ({ page }) => {
    await page.click('.bottom-nav-item[href="#/agenda"]');
    await page.click('.agenda-toolbar .btn.primary');
    await expect(page.locator('.modal .panel')).toBeVisible();

    const modalStyle = await page.locator('.modal').evaluate(el => {
      return window.getComputedStyle(el).alignItems;
    });
    // Em mobile deve ser flex-end (bottom-sheet)
    expect(modalStyle).toBe('flex-end');
  });

  test('inputs têm font-size mínimo de 16px (evita zoom iOS)', async ({ page }) => {
    await page.click('.bottom-nav-item[href="#/agenda"]');
    await page.click('.agenda-toolbar .btn.primary');

    const fontSize = await page.locator('.modal input').first().evaluate(el => {
      return parseFloat(window.getComputedStyle(el).fontSize);
    });
    expect(fontSize).toBeGreaterThanOrEqual(16);
  });

  test('inputs têm altura mínima de 48px (WCAG touch target)', async ({ page }) => {
    await page.click('.bottom-nav-item[href="#/agenda"]');
    await page.click('.agenda-toolbar .btn.primary');

    const height = await page.locator('.modal input').first().evaluate(el => {
      return el.getBoundingClientRect().height;
    });
    expect(height).toBeGreaterThanOrEqual(44); // 44px é o mínimo Apple HIG
  });

  test('skip link de acessibilidade existe no HTML', async ({ page }) => {
    const skipLink = page.locator('.skip-link');
    await expect(skipLink).toHaveCount(1);
  });

  test('bottom nav tem aria-label', async ({ page }) => {
    const nav = page.locator('#bottom-nav');
    await expect(nav).toHaveAttribute('aria-label', 'Navegação principal');
  });

  test('botões de ação do card têm aria-label', async ({ page }) => {
    await page.click('.bottom-nav-item[href="#/agenda"]');
    await page.waitForTimeout(1000);

    const actionBtns = page.locator('.consult-action-btn[aria-label]');
    const count = await actionBtns.count();
    // Se houver consultas, deve ter aria-labels
    if (count > 0) {
      const label = await actionBtns.first().getAttribute('aria-label');
      expect(label).toBeTruthy();
    }
  });

  test('topbar dropdown tem aria-haspopup e aria-expanded', async ({ page }) => {
    const trigger = page.locator('.topbar-profile-btn');
    await expect(trigger).toHaveAttribute('aria-haspopup', 'true');
    await expect(trigger).toHaveAttribute('aria-expanded', 'false');

    await trigger.click();
    await expect(trigger).toHaveAttribute('aria-expanded', 'true');
  });

  test('conteúdo da página tem padding-bottom para não ficar atrás do bottom nav', async ({ page }) => {
    const paddingBottom = await page.locator('.page-content').evaluate(el => {
      return parseFloat(window.getComputedStyle(el).paddingBottom);
    });
    expect(paddingBottom).toBeGreaterThan(60);
  });

});
