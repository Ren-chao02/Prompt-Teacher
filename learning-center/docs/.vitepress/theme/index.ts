import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import './custom.css'

const theme: Theme = {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    if (typeof window !== 'undefined') {
      // 客户端代码
      console.log('提示词学习中心 - VitePress主题已加载')
    }
  }
}

export default theme
