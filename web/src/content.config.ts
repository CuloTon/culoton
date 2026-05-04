import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const news = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/news' }),
  schema: z.object({
    title: z.string(),
    summary: z.string(),
    date: z.coerce.date(),
    source_name: z.string(),
    source_url: z.string().url(),
    original_url: z.string().url(),
    tags: z.array(z.string()).default([]),
  }),
});

export const collections = { news };
