/**
 * Testes do Dashboard
 * Usa storage state — já autenticado via setup.js
 */
const { test, expect } = require('@playwright/test');

test.describe('Dashboard', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/#/dashboard');
    await expect(page.locator('.dash-header').first()).toBeVisible({ timeout: 10_000 });
  });

  test('exibe saudação dinâmica com nome do médico', async ({ page }) => {
    const saudacao = page.locator('.dash-saudacao');
    await expect(saudacao).toBeVisible();
    await expect(saudacao).toContainText(/bom dia|boa tarde|boa noite/i);
  });

  test('exibe data atual formatada', async ({ page }) => {
    await expect(page.locator('.dash-data')).toBeVisible();
  });

  test('exibe cards de KPI', async ({ page }) => {
    const cards = page.locator('.grid.cards .card');
    const count = await cards.count();
    expect(count).toBeGreaterThanOrEqual(3);
    await expect(page.locator('.kpi-card')).toHaveCount(3);
    await expect(page.locator('.kpi-icon')).toHaveCount(3);
  });

  test('exibe cards de acesso rápido Agenda e Pacientes', async ({ page }) => {
    await expect(page.locator('.quick-card').filter({ hasText: 'Agenda' })).toBeVisible();
    await expect(page.locator('.quick-card').filter({ hasText: 'Pacientes' })).toBeVisible();
  });

  test('card Agenda navega para #/agenda', async ({ page }) => {
    await page.click('.quick-card[href="#/agenda"]');
    await expect(page).toHaveURL(/#\/agenda/);
  });

  test('card Pacientes navega para #/pacientes', async ({ page }) => {
    await page.click('.quick-card[href="#/pacientes"]');
    await expect(page).toHaveURL(/#\/pacientes/);
  });

  test('bottom navigation está visível', async ({ page }) => {
    await expect(page.locator('#bottom-nav')).toBeVisible();
  });

  test('bottom navigation tem 4 abas', async ({ page }) => {
    const items = page.locator('.bottom-nav-item');
    await expect(items).toHaveCount(4);
  });

  test('aba Dashboard está ativa no bottom nav', async ({ page }) => {
    const dashItem = page.locator('.bottom-nav-item[href="#/dashboard"]');
    await expect(dashItem).toHaveClass(/active/);
  });

  test('navegação pelo bottom nav para Agenda funciona', async ({ page }) => {
    await page.click('.bottom-nav-item[href="#/agenda"]');
    await expect(page).toHaveURL(/#\/agenda/);
    await expect(page.locator('.agenda-toolbar')).toBeVisible({ timeout: 8_000 });
  });

  test('dropdown de perfil abre ao clicar no avatar', async ({ page }) => {
    await page.click('.topbar-profile-btn');
    await expect(page.locator('.topbar-dropdown')).toBeVisible();
    await expect(page.locator('.topbar-dropdown .dropdown-item').first()).toBeVisible();
  });

  test('dropdown de perfil fecha ao clicar fora', async ({ page }) => {
    await page.click('.topbar-profile-btn');
    await expect(page.locator('.topbar-dropdown')).toBeVisible();
    await page.click('body');
    await expect(page.locator('.topbar-dropdown')).toBeHidden();
  });

});
