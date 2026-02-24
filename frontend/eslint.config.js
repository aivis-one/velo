// =============================================================================
// VELO Frontend -- ESLint Configuration (Flat Config)
// =============================================================================

import js from '@eslint/js'
import tseslint from 'typescript-eslint'
import pluginVue from 'eslint-plugin-vue'
import globals from 'globals'

export default [
  js.configs.recommended,

  ...tseslint.configs.recommended,

  ...pluginVue.configs['flat/recommended'],

  {
    files: ['src/**/*.{ts,vue}'],
    languageOptions: {
      globals: {
        ...globals.browser,
      },
      parserOptions: {
        parser: tseslint.parser,
      },
    },
    rules: {
      // Allow unused vars with underscore prefix.
      '@typescript-eslint/no-unused-vars': [
        'error',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      // Allow single-word component names (VButton, VCard, etc.).
      'vue/multi-word-component-names': 'off',
      // No console.log in production code.
      'no-console': ['warn', { allow: ['warn', 'error'] }],
    },
  },

  {
    ignores: ['dist/', 'node_modules/', '*.config.*'],
  },
]
