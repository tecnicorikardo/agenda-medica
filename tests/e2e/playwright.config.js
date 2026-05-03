// @ts-check
const { defineConfig } = require('@playwright/test');
const { STORAGE_STATE } = require('./setup');

module.exports = defineConfig({
  testDir: './specs',
  timeout: 20_000,
  expect: { timeout: 8_000 },
  fullyParallel: false,
  retries: 1,
  workers: 1,
  globalSetup: './setup.js',
  reporter: [['list'], ['html', { outputFolder: 'report', open: 'never' }]],

  use: {
    baseURL: 'http://localhost:8000',
    browserName: 'chromium',
    headless: true,
    locale: 'pt-BR',
    timezoneId: 'America/Sao_Paulo',
    screenshot: 'only-on-failure',
    video: 'off',
    trace: 'off',
    // Reutiliza sessão autenticada em todos os testes de UI
    storageState: STORAGE_STATE,
  },

  projects: [
    {
      name: 'mobile',
      use: {
        browserName: 'chromium',
        headless: true,
        viewport: { width: 390, height: 844 },
        userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        deviceScaleFactor: 3,
        isMobile: true,
        hasTouch: true,
        storageState: STORAGE_STATE,
      },
    },
    {
      name: 'desktop',
      use: {
        browserName: 'chromium',
        headless: true,
        viewport: { width: 1280, height: 800 },
        storageState: STORAGE_STATE,
      },
    },
    // Projeto sem autenticação — para testes de login/auth
    {
      name: 'no-auth',
      use: {
        browserName: 'chromium',
        headless: true,
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        storageState: undefined,
      },
      testMatch: '**/01-auth.spec.js',
    },
  ],
});
