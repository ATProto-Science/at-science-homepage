import { govukEleventyPlugin } from '@x-govuk/govuk-eleventy-plugin'

export default function(eleventyConfig) {
  eleventyConfig.addPlugin(govukEleventyPlugin, {
    stylesheets: ['/assets/styles.css'],
    showBreadcrumbs: true,
    titleSuffix: 'ATproto Science',
    serviceNavigation: {
      // serviceName: 'ATProto Science',
      // serviceUrl: '/',
      // search: {
      //   indexPath: '/search-index.json',
      //   sitemapPath: '/sitemap'
      // },
      navigation: [
        {
          text: 'Home',
          href: '/'
        },
        {
          text: 'Products',
          href: '/products'
        },
        {
          text: 'Events',
          href: '/events'
        }
      ]
    },
    header: {
      logotype: {
        text: 'atproto.science'
      },
    //   productName: 'Lorem Ipsum productName',
    },
    footer: {
      logo: false,
      contentLicence: {
        html: 'Lorem Ipsum footer contentLicence'
      },
      copyright: {
        text: '© Lorem Ipsum footer copyright'
      },
    }
  })

  // Passthrough copy for images
  eleventyConfig.addPassthroughCopy('content/assets/images')

  // Collections
  eleventyConfig.addCollection('events', (collection) =>
    collection
      .getFilteredByGlob(['content/events/event-*.md'])
      .sort((a, b) => {
        // Sort by date (most recent first)
        const dateA = a.data?.date ? new Date(a.data.date) : new Date(0)
        const dateB = b.data?.date ? new Date(b.data.date) : new Date(0)
        return dateB - dateA
      })
  )

  eleventyConfig.addCollection('products', (collection) =>
    collection
      .getFilteredByGlob(['content/products/product-*.md'])
      .sort((a, b) => a.data?.title?.localeCompare(b.data?.title) || 0)
  )

  eleventyConfig.addCollection('news', (collection) =>
    collection
      .getFilteredByGlob(['content/news/news-*.md'])
      .sort((a, b) => {
        // Sort by date (most recent first)
        const dateA = a.data?.date ? new Date(a.data.date) : new Date(0)
        const dateB = b.data?.date ? new Date(b.data.date) : new Date(0)
        return dateB - dateA
      })
  )

  return {
    dataTemplateEngine: 'njk',
    htmlTemplateEngine: 'njk',
    markdownTemplateEngine: 'njk',
    pathPrefix: '/at-science-homepage/',
    dir: {
      // The folder where all your content will live:
      input: 'content',
    }
  }
};