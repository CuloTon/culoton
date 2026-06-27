import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const news = await getCollection('news_en');
  const sorted = news.sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());

  return rss({
    title: 'BRAINROT — GRAM Blockchain News',
    description: 'Daily news, analysis and updates from the GRAM blockchain ecosystem. Powered by $BRT.',
    site: context.site!,
    items: sorted.map((entry) => ({
      title: entry.data.title,
      pubDate: entry.data.date,
      description: entry.data.summary,
      link: `/news/${entry.id.replace(/^en\//, '').replace(/\.md$/, '')}`,
      categories: entry.data.tags,
    })),
    customData: '<language>en-us</language>',
  });
}
