<!--
  VELO Frontend -- Standalone Stub View (Phase F1.3, fixed 10.3)

  FIX 10.3: Bot URL from env variable, not hardcoded.
-->

<template>
  <div class="stub">
    <div class="stub__logo">
      <svg width="64" height="64" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="32" cy="32" r="30" fill="var(--velo-primary)" />
        <text x="32" y="40" text-anchor="middle" fill="white" font-size="24" font-weight="700" font-family="system-ui, sans-serif">V</text>
      </svg>
    </div>
    <h1 class="stub__title">VELO</h1>
    <p class="stub__message">
      Для входа откройте приложение через Telegram-бот
    </p>
    <a :href="botUrl" class="stub__button" target="_blank" rel="noopener">
      Открыть в Telegram
    </a>
    <p class="stub__hint">
      Нажмите кнопку «Открыть VELO» в чате с ботом
    </p>
  </div>
</template>

<script setup lang="ts">
// FIX 10.3: configurable via env, fallback to test bot.
const botUrl = import.meta.env.VITE_TELEGRAM_BOT_URL || 'https://t.me/velo_testbot'
</script>

<style scoped>
.stub {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  min-height: 100dvh;
  padding: var(--space-6);
  background: var(--velo-bg-start);
  text-align: center;
}
.stub__logo { margin-bottom: var(--space-2); }
.stub__title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--velo-text-primary);
  letter-spacing: 0.1em;
  margin: 0 0 var(--space-6) 0;
}
.stub__message {
  font-size: var(--text-base);
  color: var(--velo-text-secondary);
  margin: 0 0 var(--space-6) 0;
  max-width: 280px;
  line-height: 1.5;
}
.stub__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--space-3) var(--space-6);
  background: var(--velo-primary);
  color: white;
  font-size: var(--text-base);
  font-weight: 600;
  text-decoration: none;
  border-radius: var(--radius-lg);
  transition: background var(--transition-fast);
  min-width: 200px;
}
.stub__button:hover { background: var(--velo-primary-dark); }
.stub__hint {
  font-size: var(--text-sm);
  color: var(--velo-text-muted);
  margin: var(--space-4) 0 0 0;
  max-width: 240px;
  line-height: 1.4;
}
</style>
