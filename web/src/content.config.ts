import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const LOCALE_ENUM = z.enum(['en', 'ru', 'pl', 'de', 'es', 'uk']);
const LOCALE_CODES = ['en', 'ru', 'pl', 'de', 'es', 'uk'] as const;

/** Build one defineCollection per locale for a content folder, keyed `${name}_${loc}`. */
function perLocale(folder: string, schema: z.ZodTypeAny) {
  const out: Record<string, ReturnType<typeof defineCollection>> = {};
  for (const loc of LOCALE_CODES) {
    out[`${folder}_${loc}`] = defineCollection({
      loader: glob({ pattern: `${loc}/**/*.md`, base: `./src/content/${folder}` }),
      schema,
    });
  }
  return out;
}

const newsSchema = z.object({
  locale: LOCALE_ENUM,
  title: z.string(),
  summary: z.string(),
  date: z.coerce.date(),
  source_name: z.string(),
  source_url: z.string().url(),
  original_url: z.string().url(),
  tags: z.array(z.string()).default([]),
});

const blogSchema = z.object({
  locale: LOCALE_ENUM,
  kind: z.enum(['morning', 'noon', 'evening']),
  title: z.string(),
  summary: z.string(),
  date: z.coerce.date(),
  articles_covered: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
});

const pulseSchema = z.object({
  locale: LOCALE_ENUM,
  slot: z.enum(['morning', 'afternoon', 'overnight']),
  title: z.string(),
  summary: z.string(),
  date: z.coerce.date(),
  source_chat: z.string().default('t.me/stonksonton'),
  message_count: z.number().int().nonnegative().default(0),
  participants: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
});

const taleSchema = z.object({
  locale: LOCALE_ENUM,
  title: z.string(),
  summary: z.string(),
  date: z.coerce.date(),
  articles_covered: z.array(z.string()).default([]),
  tags: z.array(z.string()).default([]),
});

export const collections = {
  ...perLocale('news', newsSchema),
  ...perLocale('blog', blogSchema),
  ...perLocale('pulse', pulseSchema),
  ...perLocale('tale', taleSchema),
};
