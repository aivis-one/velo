<!--
  VELO Frontend -- Standalone Stub View (DS-6)

  Shown when user opens app outside Telegram (no initData).
  Directs them to open via the bot.
  Matches 01_Welcome.png mockup style — glassmorphism buttons, pill shape.
-->

<template>
  <div class="stub">
    <div class="stub__logo">
      <VeloLogo :size="120" />
    </div>
    <h1 class="stub__title">VELΘ</h1>
    <p class="stub__message">
      Пространство для практики<br />и внутреннего развития
    </p>
    <a :href="botUrl" class="stub__button stub__button--primary" target="_blank" rel="noopener">
      Открыть в Telegram
    </a>
    <p class="stub__hint">
      Нажмите кнопку «Открыть VELO» в чате с ботом
    </p>
  </div>
</template>

<script setup lang="ts">
import VeloLogo from '@/components/ui/VeloLogo.vue'

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
  background: transparent;
  text-align: center;
}

.stub__logo {
  margin-bottom: var(--space-2);
}

.stub__title {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 400;
  color: var(--velo-text-primary);
  letter-spacing: 0.02em;
  margin: 0 0 var(--space-4) 0;
}

.stub__message {
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--velo-text-secondary);
  margin: 0 0 var(--space-8) 0;
  max-width: 280px;
  line-height: 1.5;
}

.stub__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  max-width: var(--velo-content-width);
  height: 50px;
  font-family: var(--font-body);
  font-size: var(--text-base);
  font-weight: 400;
  text-decoration: none;
  border-radius: var(--radius-full);
  border: 1px solid #ffffff;
  backdrop-filter: blur(2px);
  -webkit-backdrop-filter: blur(2px);
  box-shadow: var(--velo-shadow-glow);
  transition: opacity var(--transition-fast);
}

.stub__button:hover {
  opacity: 0.9;
}

.stub__button--primary {
  background: var(--velo-primary);
  color: white;
}

.stub__hint {
  font-family: var(--font-body);
  font-size: var(--text-sm);
  font-weight: 400;
  color: var(--velo-text-muted);
  margin: var(--space-4) 0 0 0;
  max-width: 240px;
  line-height: 1.4;
}
</style>
