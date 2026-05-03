/**
 * Helpers de autenticação reutilizáveis nos testes.
 * Lê credenciais do .env na raiz do projeto.
 */
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../../../.env') });

const BASE_URL = 'http://localhost:8000';

// Credenciais de teste — lidas do .env ou fallback para valores padrão de dev
const TEST_EMAIL    = process.env.TEST_EMAIL    || 'playwright.teste@gmail.com';
const TEST_PASSWORD = process.env.TEST_PASSWORD || 'Playwright@2026';
const TEST_NAME     = process.env.TEST_NAME     || 'Dr. Playwright Teste';

/**
 * Faz login via API e retorna os cookies de sessão.
 * Mais rápido que navegar pela UI em cada teste.
 */
async function loginViaAPI(request) {
  const res = await request.post(`${BASE_URL}/api/auth/login`, {
    data: { email: TEST_EMAIL, senha: TEST_PASSWORD },
  });
  return res;
}

/**
 * Navega para a página de login e faz login pela UI.
 */
async function loginViaUI(page) {
  await page.goto('/#/login');
  await page.waitForSelector('.login-card', { timeout: 10_000 });

  await page.fill('input[type="email"]', TEST_EMAIL);
  await page.fill('input[type="password"]', TEST_PASSWORD);
  await page.click('button[type="submit"]');

  // Aguarda welcome screen ou dashboard
  await page.waitForSelector('.welcome-screen, .dash-header, .quick-access-grid', {
    timeout: 15_000,
  });
}

/**
 * Aguarda a welcome screen terminar e o dashboard aparecer.
 */
async function waitForDashboard(page) {
  // Se welcome screen estiver visível, aguarda ela sair
  const welcome = page.locator('.welcome-screen');
  if (await welcome.isVisible().catch(() => false)) {
    await welcome.waitFor({ state: 'hidden', timeout: 10_000 });
  }
  await page.waitForSelector('.dash-header, .quick-access-grid', { timeout: 10_000 });
}

module.exports = { loginViaUI, loginViaAPI, waitForDashboard, TEST_EMAIL, TEST_PASSWORD, TEST_NAME, BASE_URL };
