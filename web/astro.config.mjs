import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://brainrot-ton.fun',
  trailingSlash: 'never',
  build: {
    format: 'directory',
  },
  vite: {
    // Skip realpath() during resolution. The local NTFS volume intermittently
    // throws EIO on realpath for some node_modules entries (e.g. @ton/*); since
    // there are no real symlinks here, preserving paths is safe and avoids it.
    resolve: { preserveSymlinks: true },
  },
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'ru', 'pl', 'de'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
  integrations: [sitemap({
    i18n: {
      defaultLocale: 'en',
      locales: {
        en: 'en-US',
        ru: 'ru-RU',
        pl: 'pl-PL',
        de: 'de-DE',
      },
    },
  })],
});
