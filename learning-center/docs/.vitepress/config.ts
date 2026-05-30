import { defineConfig } from 'vitepress'

export default defineConfig({
  title: '提示词学习中心',
  description: '系统学习提示词工程，从入门到精通的专业课程',
  
  themeConfig: {
    nav: [
      { text: '首页', link: '/' },
      { text: '基础入门', link: '/guide/basic/' },
      { text: '进阶技巧', link: '/guide/intermediate/' },
      { text: '高级应用', link: '/guide/advanced/' },
      { text: '最佳实践', link: '/guide/best-practices/' },
    ],

    sidebar: {
      '/guide/': [
        {
          text: '基础入门',
          items: [
            { text: '什么是提示词', link: '/guide/basic/what-is-prompt' },
            { text: '提示词的基本结构', link: '/guide/basic/prompt-structure' },
            { text: '常用提示词技巧', link: '/guide/basic/common-techniques' },
          ]
        },
        {
          text: '进阶技巧',
          items: [
            { text: '链式思维 (Chain-of-Thought)', link: '/guide/intermediate/chain-of-thought' },
            { text: '少样本学习', link: '/guide/intermediate/few-shot-learning' },
            { text: '角色扮演提示词', link: '/guide/intermediate/role-playing' },
          ]
        },
        {
          text: '高级应用',
          items: [
            { text: '复杂任务分解', link: '/guide/advanced/task-decomposition' },
            { text: '多模态提示词', link: '/guide/advanced/multimodal-prompts' },
            { text: '提示词优化策略', link: '/guide/advanced/optimization-strategies' },
          ]
        },
        {
          text: '最佳实践',
          items: [
            { text: '企业级提示词设计', link: '/guide/best-practices/enterprise-design' },
            { text: '安全与伦理考量', link: '/guide/best-practices/safety-ethics' },
            { text: '性能评估方法', link: '/guide/best-practices/evaluation-methods' },
          ]
        }
      ]
    },

    socialLinks: [
      { icon: 'github', link: 'https://github.com' }
    ],

    footer: {
      message: '基于 VitePress 构建 | 提示词教学平台',
      copyright: '© 2024 提示词教学平台'
    },

    search: {
      provider: 'local'
    }
  },

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
    ['meta', { name: 'theme-color', content: '#00A4F4' }]
  ]
})
