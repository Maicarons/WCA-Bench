import { defineConfig } from 'vitepress'

export default defineConfig({
  lang: 'zh-CN',
  title: 'WCA-Bench',
  description: '基于世界魔方协会数据库的体育数据分析标准化基准',
  cleanUrls: true,
  lastUpdated: true,
  head: [
    ['meta', { name: 'theme-color', content: '#3c8772' }],
    ['meta', { name: 'og:title', content: 'WCA-Bench 文档' }],
    [
      'meta',
      {
        name: 'og:description',
        content: '项目计划书与开发计划 · 数据基础设施 · 任务套件 · 评估框架'
      }
    ]
  ],
  markdown: {
    lineNumbers: true,
    theme: { light: 'github-light', dark: 'github-dark' },
    container: { tipLabel: '提示', warningLabel: '注意', dangerLabel: '警告', infoLabel: '信息' }
  },
  themeConfig: {
    siteTitle: 'WCA-Bench Docs',
    logo: undefined,
    outline: { level: [2, 3], label: '本页目录' },
    nav: [
      { text: '首页', link: '/' },
      { text: '项目计划书', link: '/guide/', activeMatch: '^/guide/' },
      { text: '技术方案', link: '/data/', activeMatch: '^/(data|tasks|evaluation)/' },
      { text: '开发计划', link: '/plan/', activeMatch: '^/plan/' }
    ],
    sidebar: {
      '/guide/': [
        {
          text: '项目计划书',
          items: [
            { text: '执行摘要', link: '/guide/' },
            { text: '项目概述与目标', link: '/guide/overview' },
            { text: '项目范围界定', link: '/guide/scope' },
            { text: '技术方案概述', link: '/guide/architecture' },
            { text: '预期成果与成功标准', link: '/guide/outcomes' }
          ]
        }
      ],
      '/data/': [
        {
          text: '数据基础设施',
          items: [
            { text: '总览', link: '/data/' },
            { text: '数据来源与表结构', link: '/data/sources' },
            { text: '预处理管线', link: '/data/pipeline' },
            { text: '数据划分策略', link: '/data/splits' }
          ]
        }
      ],
      '/tasks/': [
        {
          text: '任务套件',
          items: [
            { text: '总览', link: '/tasks/' },
            { text: '任务一：成绩预测', link: '/tasks/result-prediction' },
            { text: '任务二：名次预测', link: '/tasks/placement' },
            { text: '任务三：DNF 预测', link: '/tasks/dnf' },
            { text: '任务四：人类极限估计', link: '/tasks/limit' },
            { text: '任务五：技能迁移分析', link: '/tasks/transfer' }
          ]
        }
      ],
      '/evaluation/': [
        {
          text: '评估框架',
          items: [
            { text: '总览', link: '/evaluation/' },
            { text: '评估协议与分层', link: '/evaluation/protocol' },
            { text: '统计显著性检验', link: '/evaluation/statistics' },
            { text: '复现性要求', link: '/evaluation/reproducibility' }
          ]
        }
      ],
      '/plan/': [
        {
          text: '开发计划',
          items: [
            { text: '计划总览', link: '/plan/' },
            { text: '目录组织与文档分层', link: '/plan/structure' },
            { text: '阶段划分与里程碑', link: '/plan/roadmap' }
          ]
        },
        {
          text: '阶段任务分解',
          items: [
            { text: '阶段一：数据基础设施', link: '/plan/phase-1' },
            { text: '阶段二：任务定义与基线', link: '/plan/phase-2' },
            { text: '阶段三：基准发布', link: '/plan/phase-3' },
            { text: '阶段四：迭代与扩展', link: '/plan/phase-4' }
          ]
        },
        {
          text: '管理与治理',
          items: [
            { text: '依赖关系', link: '/plan/dependencies' },
            { text: '验收标准', link: '/plan/acceptance' },
            { text: '风险与缓解', link: '/plan/risks' },
            { text: '发表策略', link: '/plan/publication' }
          ]
        }
      ]
    },
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索文档', buttonAriaLabel: '搜索文档' },
          modal: {
            noResultsText: '无匹配结果',
            resetButtonTitle: '清除查询条件',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' }
          }
        }
      }
    },
    socialLinks: [{ icon: 'github', link: 'https://github.com/' }],
    docFooter: { prev: '上一页', next: '下一页' },
    lastUpdatedText: '最后更新于',
    returnToTopLabel: '回到顶部',
    sidebarMenuLabel: '目录',
    darkModeSwitchLabel: '主题',
    footer: {
      message: '基于 Apache-2.0 许可证发布 · 数据版权归 World Cube Association 所有',
      copyright: 'WCA-Bench Project'
    }
  }
})
