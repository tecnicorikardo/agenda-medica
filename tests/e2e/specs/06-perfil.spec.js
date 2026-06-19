/**
 * Testes da página de Perfil
 * Usa storage state — já autenticado via setup.js
 */
const { test, expect } = require('@playwright/test');

test.describe('Perfil', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('/#/perfil');
    await expect(page.locator('.card').first()).toBeVisible({ timeout: 10_000 });
  });

  test('página de perfil carrega corretamente', async ({ page }) => {
    // Deve ter algum card de perfil
    await expect(page.locator('.card').first()).toBeVisible({ timeout: 8_000 });
  });

  test('exibe campo de nome', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    // O perfil tem input com placeholder "Dr(a). Nome Sobrenome"
    const nomeInput = page.locator('input[placeholder*="Nome Sobrenome"], input[placeholder*="nome"]').first();
    await expect(nomeInput).toBeVisible({ timeout: 8_000 });
  });

  test('exibe campo de CRM', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    const crmInput = page.locator('input[placeholder*="CRM"]').first();
    await expect(crmInput).toBeVisible({ timeout: 8_000 });
  });

  test('organiza configurações em quatro abas', async ({ page }) => {
    await expect(page.locator('.profile-tab')).toHaveCount(4);
    await expect(page.locator('.profile-tab').filter({ hasText: 'Dados pessoais' })).toHaveClass(/active/);
  });

  test('toggle de tema claro/escuro funciona', async ({ page }) => {
    await page.waitForLoadState('networkidle');
    await page.locator('.profile-tab').filter({ hasText: 'Aparência' }).click();
    // Botões de tema têm classe .theme-option
    const btnEscuro = page.locator('.theme-option').first();
    const btnClaro  = page.locator('.theme-option').nth(1);
    await expect(btnEscuro).toBeVisible({ timeout: 8_000 });
    await expect(btnClaro).toBeVisible({ timeout: 8_000 });

    // Ativa tema claro
    await btnClaro.click();
    const isLight = await page.evaluate(() => document.body.classList.contains('light'));
    expect(isLight).toBe(true);

    // Volta para escuro
    await btnEscuro.click();
    const isDark = await page.evaluate(() => !document.body.classList.contains('light'));
    expect(isDark).toBe(true);
  });

  test('seção de lembretes está visível', async ({ page }) => {
    await page.locator('.profile-tab').filter({ hasText: 'Notificações' }).click();
    const lembretesSection = page.locator('.card').filter({ hasText: /lembrete/i }).first();
    await expect(lembretesSection).toBeVisible({ timeout: 5_000 });
  });

  test('exibe teste de WhatsApp na aba de notificações', async ({ page }) => {
    await page.locator('.profile-tab').filter({ hasText: 'Notificações' }).click();
    await expect(page.locator('.card').filter({ hasText: 'Teste de WhatsApp' })).toBeVisible();
    await expect(page.getByRole('button', { name: /enviar whatsapp de teste/i })).toBeVisible();
  });

  test('navegação de volta para dashboard pelo bottom nav', async ({ page }) => {
    await page.click('.bottom-nav-item[href="#/dashboard"]');
    await expect(page).toHaveURL(/#\/dashboard/);
  });

});
