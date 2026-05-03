/**
 * Testes de Autenticação
 * Roda no projeto 'no-auth' (sem storage state pré-carregado)
 */
const { test, expect } = require('@playwright/test');
const { BASE_URL, TEST_EMAIL, TEST_PASSWORD } = require('../helpers/auth');

test.describe('Autenticação', () => {

  test('exibe tela de login ao acessar a raiz sem sessão', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('.login-card')).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('.login-title')).toContainText('Agenda Médica');
  });

  test('exibe erro com credenciais inválidas', async ({ page }) => {
    await page.goto('/#/login');
    await page.fill('input[type="email"]', 'invalido@teste.com');
    await page.fill('input[type="password"]', 'senhaerrada');
    await page.click('button[type="submit"]');
    await expect(page.locator('.toast')).toBeVisible({ timeout: 5_000 });
    await expect(page.locator('.toast')).toContainText(/inválid|incorret|erro/i);
  });

  test('login com credenciais válidas redireciona para dashboard', async ({ page }) => {
    await page.goto('/#/login');
    await page.fill('input[type="email"]', TEST_EMAIL);
    await page.fill('input[type="password"]', TEST_PASSWORD);
    await page.click('button[type="submit"]');
    // Aguarda welcome screen ou dashboard
    await page.waitForSelector('.welcome-screen, .dash-header, .quick-access-grid', { timeout: 15_000 });
    // Aguarda welcome screen sair se aparecer
    const welcome = page.locator('.welcome-screen');
    if (await welcome.isVisible().catch(() => false)) {
      await welcome.waitFor({ state: 'hidden', timeout: 10_000 });
    }
    await expect(page).toHaveURL(/#\/dashboard/);
  });

  test('acesso direto a rota protegida sem sessão redireciona para login', async ({ page, context }) => {
    // Limpa cookies para simular usuário não autenticado
    await context.clearCookies();
    await page.goto('/#/agenda');
    await expect(page.locator('.login-card')).toBeVisible({ timeout: 8_000 });
  });

  test('campo de senha tem toggle de visibilidade', async ({ page }) => {
    await page.goto('/#/login');
    const senhaWrap = page.locator('.login-senha-wrap');
    const senhaInput = senhaWrap.locator('input').first();
    const btnEye = page.locator('.btn-eye');
    await expect(senhaInput).toHaveAttribute('type', 'password');
    await btnEye.click();
    await expect(senhaInput).toHaveAttribute('type', 'text');
    await btnEye.click();
    await expect(senhaInput).toHaveAttribute('type', 'password');
  });

  test('health check da API responde 200', async ({ request }) => {
    const res = await request.get(`${BASE_URL}/api/health`);
    expect(res.status()).toBe(200);
    expect((await res.json()).ok).toBe(true);
  });

});
