import { govukEleventyPlugin } from '@x-govuk/govuk-eleventy-plugin'

export default function(eleventyConfig) {
  eleventyConfig.addPlugin(govukEleventyPlugin, {
    stylesheets: ['/assets/styles.css'],
    showBreadcrumbs: false,
    titleSuffix: 'ATproto Science',
    icons: {
      shortcut: '/assets/icon/favicon.ico',
      mask: '/assets/icon/mask.svg',
      touch: '/assets/icon/icon-180.png'
    },
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
        html: 'All content is available under the <a class="govuk-footer__link" href="https://creativecommons.org/licenses/by/4.0/">Creative Commons Attribution 4.0 International license</a>, except where otherwise stated.'
      },
      copyright: {
        text: '© ATproto Science 2024-2025'
      },
    }
  })

  // Passthrough copy for images and icons
  eleventyConfig.addPassthroughCopy('content/assets/images')
  eleventyConfig.addPassthroughCopy('content/assets/icon')

  // Custom computed data for event metadata
  eleventyConfig.addGlobalData('eleventyComputed', {
    eventDescription: (data) => {
      if (data.layout !== 'event') return data.description

      const parts = []

      // Format dates
      if (data.startdate) {
        const startDate = new Date(data.startdate)
        const options = { year: 'numeric', month: 'long', day: 'numeric' }

        if (data.enddate) {
          const endDate = new Date(data.enddate)
          // Check if same month and year
          if (startDate.getMonth() === endDate.getMonth() &&
              startDate.getFullYear() === endDate.getFullYear()) {
            parts.push(`${startDate.toLocaleDateString('en-US', { month: 'long', day: 'numeric' })}-${endDate.getDate()}, ${startDate.getFullYear()}`)
          } else {
            parts.push(`${startDate.toLocaleDateString('en-US', options)} - ${endDate.toLocaleDateString('en-US', options)}`)
          }
        } else {
          parts.push(startDate.toLocaleDateString('en-US', options))
        }
      }

      // Add location
      const locationParts = []
      if (data.city) locationParts.push(data.city)
      if (data.country) locationParts.push(data.country)
      if (locationParts.length > 0) {
        parts.push(locationParts.join(', '))
      }

      const eventInfo = parts.join(' &bull; ')

      // Combine event info with description, separated by double newline for markdown
      if (eventInfo && data.description) {
        return `**${eventInfo}**\n\n${data.description}`
      } else if (eventInfo) {
        return `**${eventInfo}**`
      } else {
        return data.description
      }
    }
  })

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
    pathPrefix: process.env.ELEVENTY_ENV === 'production' ? '/at-science-homepage/' : '/',
    dir: {
      // The folder where all your content will live:
      input: 'content',
    }
  }
};