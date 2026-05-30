---
layout: home

hero:
  name: 提示词学习中心
  text: 系统学习提示词工程
  tagline: 从入门到精通的专业课程体系
  image:
    src: /hero-image.svg
    alt: 提示词学习
  actions:
    - theme: brand
      text: 开始学习
      link: /guide/basic/what-is-prompt
    - theme: alt
      text: 查看课程
      link: /guide/

features:
  - title: 🌱 基础入门
    details: 了解提示词的基本概念、结构和常用技巧，为零基础学习者量身定制
    link: /guide/basic/
    linkText: 开始学习 →
  - title: ⚡ 进阶技巧
    details: 掌握链式思维、少样本学习、角色扮演等高级技巧，提升提示词效果
    link: /guide/intermediate/
    linkText: 深入了解 →
  - title: 🚀 高级应用
    details: 学习复杂任务分解、多模态提示词、优化策略等企业级应用方法
    link: /guide/advanced/
    linkText: 探索高级 →
  - title: 💎 最佳实践
    details: 企业级设计模式、安全伦理考量、性能评估方法，成为专业提示词工程师
    link: /guide/best-practices/
    linkText: 查看实践 →

---

<style>
/* 首页Hero区域样式 */
.VPHero {
  padding-bottom: 0 !important;
}

.VPImage {
  max-width: 400px !important;
}

/* 特性卡片网格 */
.VPFeatures {
  max-width: 1200px !important;
  margin: 0 auto !important;
  padding: var(--space-12) var(--space-6) !important;
}

.VPFeature {
  border: 1px solid var(--border-color) !important;
  border-radius: var(--radius-xl) !important;
  padding: var(--space-6) !important;
  transition: all var(--transition-normal) !important;
  background-color: var(--bg-primary) !important;
}

.VPFeature:hover {
  transform: translateY(-4px) !important;
  box-shadow: var(--shadow-lg) !important;
  border-color: var(--color-primary-light) !important;
}

.VPFeature .title {
  font-size: var(--text-xl) !important;
  font-weight: var(--font-bold) !important;
  color: var(--text-primary) !important;
  margin-bottom: var(--space-3) !important;
}

.VPFeature .details {
  color: var(--text-secondary) !important;
  line-height: var(--leading-relaxed) !important;
  font-size: var(--text-base) !important;
}

.VPFeature .link-text {
  color: var(--color-primary) !important;
  font-weight: var(--font-medium) !important;
  margin-top: var(--space-4) !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: var(--space-2) !important;
  transition: all var(--transition-fast) !important;
}

.VPFeature .link-text:hover {
  transform: translateX(4px) !important;
}

/* 学习路径可视化 */
.learning-path {
  margin: var(--space-16) auto;
  max-width: 1000px;
  padding: 0 var(--space-6);
}

.path-container {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: var(--space-8);
}

.path-step {
  display: flex;
  align-items: flex-start;
  gap: var(--space-6);
  opacity: 0;
  animation: fadeInUp 0.6s ease-out forwards;
}

.path-step:nth-child(1) { animation-delay: 0.1s; }
.path-step:nth-child(2) { animation-delay: 0.2s; }
.path-step:nth-child(3) { animation-delay: 0.3s; }
.path-step:nth-child(4) { animation-delay: 0.4s; }

.step-number {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-light));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: var(--font-bold);
  font-size: var(--text-lg);
  flex-shrink: 0;
  box-shadow: var(--shadow-md);
}

.step-content {
  flex: 1;
  background-color: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  transition: all var(--transition-normal);
}

.step-content:hover {
  border-color: var(--color-primary-light);
  box-shadow: var(--shadow-md);
  transform: translateX(4px);
}

.step-title {
  font-size: var(--text-lg);
  font-weight: var(--font-semibold);
  color: var(--text-primary);
  margin-bottom: var(--space-2);
}

.step-description {
  color: var(--text-secondary);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-3);
}

.step-link {
  color: var(--color-primary);
  font-weight: var(--font-medium);
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  transition: all var(--transition-fast);
}

.step-link:hover {
  gap: var(--space-3);
}

/* 统计数据展示 */
.stats-section {
  margin: var(--space-16) auto;
  max-width: 900px;
  padding: var(--space-10);
  background: linear-gradient(135deg, rgba(0, 164, 244, 0.05), rgba(0, 164, 244, 0.02));
  border-radius: var(--radius-2xl);
  border: 1px solid rgba(0, 164, 244, 0.1);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--space-8);
  text-align: center;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-2);
}

.stat-value {
  font-size: var(--text-4xl);
  font-weight: var(--font-bold);
  color: var(--color-primary);
  line-height: 1;
}

.stat-label {
  font-size: var(--text-base);
  color: var(--text-secondary);
  font-weight: var(--font-medium);
}

/* CTA区域 */
.cta-section {
  margin: var(--space-16) auto;
  max-width: 800px;
  text-align: center;
  padding: var(--space-12);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  border-radius: var(--radius-2xl);
  color: white;
}

.cta-title {
  font-size: var(--text-3xl);
  font-weight: var(--font-bold);
  margin-bottom: var(--space-4);
  color: white;
}

.cta-description {
  font-size: var(--text-lg);
  opacity: 0.95;
  margin-bottom: var(--space-6);
  line-height: var(--leading-relaxed);
}

.cta-button {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-4) var(--space-8);
  background-color: white;
  color: var(--color-primary);
  border-radius: var(--radius-full);
  font-weight: var(--font-semibold);
  font-size: var(--text-lg);
  text-decoration: none;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-lg);
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-xl);
}
</style>

<!-- 学习路径 -->
<div class="learning-path">
  <div class="path-container">
    
    <div class="path-step">
      <div class="step-number">1</div>
      <div class="step-content">
        <div class="step-title">🌱 基础入门</div>
        <div class="step-description">
          从零开始理解提示词的概念，掌握基本结构和使用方法。适合所有初学者。
        </div>
        <a href="/guide/basic/" class="step-link">
          开始基础学习 →
        </a>
      </div>
    </div>

    <div class="path-step">
      <div class="step-number">2</div>
      <div class="step-content">
        <div class="step-title">⚡ 进阶技巧</div>
        <div class="step-description">
          深入学习链式思维、少样本学习等高级技巧，显著提升提示词的效果和质量。
        </div>
        <a href="/guide/intermediate/" class="step-link">
          掌握进阶技能 →
        </a>
      </div>
    </div>

    <div class="path-step">
      <div class="step-number">3</div>
      <div class="step-content">
        <div class="step-title">🚀 高级应用</div>
        <div class="step-description">
          应对复杂场景，学习任务分解、多模态处理和企业级优化策略。
        </div>
        <a href="/guide/advanced/" class="step-link">
          探索高级应用 →
        </a>
      </div>
    </div>

    <div class="path-step">
      <div class="step-number">4</div>
      <div class="step-content">
        <div class="step-title">💎 最佳实践</div>
        <div class="step-description">
          掌握企业级设计规范、安全伦理考量，成为专业的提示词工程师。
        </div>
        <a href="/guide/best-practices/" class="step-link">
          学习最佳实践 →
        </a>
      </div>
    </div>

  </div>
</div>

<!-- 统计数据 -->
<div class="stats-section">
  <div class="stats-grid">
    <div class="stat-item">
      <div class="stat-value">12+</div>
      <div class="stat-label">专业课程</div>
    </div>
    <div class="stat-item">
      <div class="stat-value">50+</div>
      <div class="stat-label">实战案例</div>
    </div>
    <div class="stat-item">
      <div class="stat-value">4</div>
      <div class="stat-label">学习阶段</div>
    </div>
    <div class="stat-item">
      <div class="stat-value">∞</div>
      <div class="stat-label">持续更新</div>
    </div>
  </div>
</div>

<!-- 行动召唤 -->
<div class="cta-section">
  <div class="cta-title">准备好开始你的提示词学习之旅了吗？</div>
  <div class="cta-description">
    系统化的课程体系 + 实战练习 = 快速掌握提示词工程
  </div>
  <a href="/guide/basic/what-is-prompt" class="cta-button">
    立即开始学习 🚀
  </a>
</div>
