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

const blogSchema = z.object({
  locale: z.enum(['en', 'ru', 'pl', 'de']),
  kind: z.enum(['morning', 'noon', 'evening']),
  title: z.string(),
  summary: z.string(),
  date: z.coerce.date(),
  articles_covered: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
});

const blog_en = defineCollection({
  loader: glob({ pattern: 'en/**/*.md', base: './src/content/blog' }),
  schema: blogSchema,
});

const blog_ru = defineCollection({
  loader: glob({ pattern: 'ru/**/*.md', base: './src/content/blog' }),
  schema: blogSchema,
});

const blog_pl = defineCollection({
  loader: glob({ pattern: 'pl/**/*.md', base: './src/content/blog' }),
  schema: blogSchema,
});

const blog_de = defineCollection({
  loader: glob({ pattern: 'de/**/*.md', base: './src/content/blog' }),
  schema: blogSchema,
});

const pulseSchema = z.object({
  locale: z.enum(['en', 'ru', 'pl', 'de']),
  slot: z.enum(['morning', 'afternoon', 'overnight']),
  title: z.string(),
  summary: z.string(),
  date: z.coerce.date(),
  source_chat: z.string().default('t.me/stonksonton'),
  message_count: z.number().int().nonnegative().default(0),
  participants: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
});

const pulse_en = defineCollection({
  loader: glob({ pattern: 'en/**/*.md', base: './src/content/pulse' }),
  schema: pulseSchema,
});

const pulse_ru = defineCollection({
  loader: glob({ pattern: 'ru/**/*.md', base: './src/content/pulse' }),
  schema: pulseSchema,
});

const pulse_pl = defineCollection({
  loader: glob({ pattern: 'pl/**/*.md', base: './src/content/pulse' }),
  schema: pulseSchema,
});

const pulse_de = defineCollection({
  loader: glob({ pattern: 'de/**/*.md', base: './src/content/pulse' }),
  schema: pulseSchema,
});

export const collections = {
  news_en,
  news_ru,
  news_pl,
  news_de,
  blog_en,
  blog_ru,
  blog_pl,
  blog_de,
  pulse_en,
  pulse_ru,
  pulse_pl,
  pulse_de,
};
