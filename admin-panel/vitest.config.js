import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    
    // 测试文件匹配模式
    include: [
      'src/**/*.{test,spec}.{js,ts}',
      'tests/**/*.{test,spec}.{js,ts}'
    ],
    
    // 排除文件
    exclude: [
      'node_modules',
      'dist',
      '.output',
      '.cache'
    ],
    
    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: './coverage',
      
      // 覆盖率阈值
      thresholds: {
        statements: 70,
        branches: 60,
        functions: 70,
        lines: 70
      },
      
      // 包含的目录
      include: [
        'src/stores/**/*.{js,ts}',
        'src/components/**/*.vue',
        'src/utils/**/*.{js,ts}',
        'src/api/**/*.{js,ts}'
      ],
      
      // 排除的文件
      exclude: [
        'src/main.js',
        'src/App.vue',
        '**/*.d.ts',
        '**/types/**'
      ]
    },
    
    // 设置文件
    setupFiles: ['./tests/setup.ts'],
    
    // 全局配置
    testTimeout: 10000,
    hookTimeout: 10000,
    
    // 输出详细度
    verbose: true,
    
    // 清理方法
    clearMocks: true,
    restoreMocks: false
  },
  
  // 服务器配置（用于测试）
  server: {
    port: 5174,
    strictPort: false
  }
})
