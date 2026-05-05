import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const newsSchema = z.object({
  locale: z.enum(['en', 'ru', 'pl', 'de']),
  title: z.string(),
  summary: z.string(),
  date: z.coerce.date(),
  source_name: z.string(),
  source_url: z.string().url(),
  original_url: z.string().url(),
  tags: z.array(z.string()).default([]),
});

const news_en = defineCollection({
  loader: glob({ pattern: 'en/**/*.md', base: './src/content/news' }),
  schema: newsSchema,
});

const news_ru = defineCollection({
  loader: glob({ pattern: 'ru/**/*.md', base: './src/content/news' }),
  schema: newsSchema,
});

const news_pl = defineCollection({
  loader: glob({ pattern: 'pl/**/*.md', base: './src/content/news' }),
  schema: newsSchema,
});

const news_de = defineCollection({
  loader: glob({ pattern: 'de/**/*.md', base: './src/content/news' }),
  schema: newsSchema,
});

export const collections = {
  news_en,
  news_ru,
  news_pl,
  news_de,
};
