import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 加载项目根目录 .env（含 DJANGO_PORT 等）
  const env = loadEnv(mode, path.resolve(__dirname, '..'), '')

  const djangoPort = env.DJANGO_PORT || '8001'
  const vitePort = parseInt(env.VITE_PORT || '8002', 10)

  return {
    base: '/admin/',
    plugins: [vue()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    build: {
      outDir: 'dist',
      emptyOutDir: true,
    },
    server: {
      port: vitePort,
      host: '0.0.0.0',
      proxy: {
        '/api': {
          target: `http://localhost:${djangoPort}`,
          changeOrigin: true,
        }
      }
    }
  }
})
