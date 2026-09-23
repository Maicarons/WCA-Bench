import { defineConfig } from 'vitepress'
import nodePath from 'node:path'

// VitePress resolves `srcDir` from the current working directory (the `docs`
// argument of `vitepress build docs`). On Windows the resulting drive letter can
// be lower-cased (e.g. `f:/...`) when the shell's working directory uses a
// lower-case drive letter, while Rollup records chunk ids with the real
// file-system casing (`F:/...`). VitePress looks up page chunks by exact string
// equality of these absolute paths, so the mismatch aborts the build with
// "Cannot read properties of undefined (reading 'imports')".
// Normalizing the drive letter makes the two forms agree.
const docsSrcDir = nodePath.resolve(process.cwd(), 'docs')
const srcDir =
  process.platform === 'win32'
    ? docsSrcDir.replace(/^([a-z]):/, (_, drive: string) => `${drive.toUpperCase()}:`)
    : docsSrcDir

const enSidebar = {
  '/guide/': [
    {
      text: 'Project Proposal',
      items: [
        { text: 'Executive Summary', link: '/guide/' },
        { text: 'Project Overview and Objectives', link: '/guide/overview' },
        { text: 'Project Scope', link: '/guide/scope' },
        { text: 'Technical Approach Overview', link: '/guide/architecture' },
        { text: 'Expected Outcomes and Success Criteria', link: '/guide/outcomes' }
      ]
    }
  ],
  '/data/': [
    {
      text: 'Data Infrastructure',
      items: [
        { text: 'Overview', link: '/data/' },
        { text: 'Data Sources and Table Schemas', link: '/data/sources' },
        { text: 'Preprocessing Pipeline', link: '/data/pipeline' },
        { text: 'Data Splitting Strategy', link: '/data/splits' }
      ]
    }
  ],
  '/tasks/': [
    {
      text: 'Task Suite',
      items: [
        { text: 'Overview', link: '/tasks/' },
        { text: 'Task 1: Result Prediction', link: '/tasks/result-prediction' },
        { text: 'Task 2: Placement Prediction', link: '/tasks/placement' },
        { text: 'Task 3: DNF Prediction', link: '/tasks/dnf' },
        { text: 'Task 4: Human Limit Estimation', link: '/tasks/limit' },
        { text: 'Task 5: Skill Transfer Analysis', link: '/tasks/transfer' }
      ]
    }
  ],
  '/evaluation/': [
    {
      text: 'Evaluation Framework',
      items: [
        { text: 'Overview', link: '/evaluation/' },
        { text: 'Evaluation Protocol and Stratification', link: '/evaluation/protocol' },
        { text: 'Statistical Significance Testing', link: '/evaluation/statistics' },
        { text: 'Reproducibility Requirements', link: '/evaluation/reproducibility' },
        { text: 'Compute and Hardware', link: '/evaluation/compute' }
      ]
    }
  ],
  '/plan/': [
    {
      text: 'Development Plan',
      items: [
        { text: 'Plan Overview', link: '/plan/' },
        { text: 'Directory Organization and Documentation Layering', link: '/plan/structure' },
        { text: 'Phase Breakdown and Milestones', link: '/plan/roadmap' }
      ]
    },
    {
      text: 'Phase Task Breakdown',
      items: [
        { text: 'Phase 1: Data Infrastructure', link: '/plan/phase-1' },
        { text: 'Phase 2: Task Definition and Baselines', link: '/plan/phase-2' },
        { text: 'Phase 3: Benchmark Release', link: '/plan/phase-3' },
        { text: 'Phase 4: Iteration and Expansion', link: '/plan/phase-4' }
      ]
    },
    {
      text: 'Management and Governance',
      items: [
        { text: 'Dependencies', link: '/plan/dependencies' },
        { text: 'Acceptance Criteria', link: '/plan/acceptance' },
        { text: 'Risks and Mitigation', link: '/plan/risks' },
        { text: 'Publication Strategy', link: '/plan/publication' },
        { text: 'Conformance Audit', link: '/plan/audit' }
      ]
    }
  ]
}

const zhSidebar = {
  '/zh/guide/': [
    {
      text: '项目计划书',
      items: [
        { text: '执行摘要', link: '/zh/guide/' },
        { text: '项目概述与目标', link: '/zh/guide/overview' },
        { text: '项目范围界定', link: '/zh/guide/scope' },
        { text: '技术方案概述', link: '/zh/guide/architecture' },
        { text: '预期成果与成功标准', link: '/zh/guide/outcomes' }
      ]
    },
    {
      text: '社区',
      items: [
        { text: '参与排行榜', link: '/zh/guide/participate' }
      ]
    }
  ],
  '/zh/data/': [
    {
      text: '数据基础设施',
      items: [
        { text: '总览', link: '/zh/data/' },
        { text: '数据来源与表结构', link: '/zh/data/sources' },
        { text: '预处理管线', link: '/zh/data/pipeline' },
        { text: '数据划分策略', link: '/zh/data/splits' }
      ]
    }
  ],
  '/zh/tasks/': [
    {
      text: '任务套件',
      items: [
        { text: '总览', link: '/zh/tasks/' },
        { text: '任务一：成绩预测', link: '/zh/tasks/result-prediction' },
        { text: '任务二：名次预测', link: '/zh/tasks/placement' },
        { text: '任务三：DNF 预测', link: '/zh/tasks/dnf' },
        { text: '任务四：人类极限估计', link: '/zh/tasks/limit' },
        { text: '任务五：技能迁移分析', link: '/zh/tasks/transfer' }
      ]
    }
  ],
  '/zh/evaluation/': [
    {
      text: '评估框架',
      items: [
        { text: '总览', link: '/zh/evaluation/' },
        { text: '评估协议与分层', link: '/zh/evaluation/protocol' },
        { text: '统计显著性检验', link: '/zh/evaluation/statistics' },
        { text: '复现性要求', link: '/zh/evaluation/reproducibility' },
        { text: '计算与硬件', link: '/zh/evaluation/compute' }
      ]
    }
  ],
  '/zh/plan/': [
    {
      text: '开发计划',
      items: [
        { text: '计划总览', link: '/zh/plan/' },
        { text: '目录组织与文档分层', link: '/zh/plan/structure' },
        { text: '阶段划分与里程碑', link: '/zh/plan/roadmap' }
      ]
    },
    {
      text: '阶段任务分解',
      items: [
        { text: '阶段一：数据基础设施', link: '/zh/plan/phase-1' },
        { text: '阶段二：任务定义与基线', link: '/zh/plan/phase-2' },
        { text: '阶段三：基准发布', link: '/zh/plan/phase-3' },
        { text: '阶段四：迭代与扩展', link: '/zh/plan/phase-4' }
      ]
    },
    {
      text: '管理与治理',
      items: [
        { text: '依赖关系', link: '/zh/plan/dependencies' },
        { text: '验收标准', link: '/zh/plan/acceptance' },
        { text: '风险与缓解', link: '/zh/plan/risks' },
        { text: '发表策略', link: '/zh/plan/publication' },
        { text: '合规审计', link: '/zh/plan/audit' }
      ]
    }
  ]
}

// GitHub Pages serves this site from https://maicarons.github.io/WCA-Bench/, so the
// base path must be the repository name. Local dev/preview keep the root base.
const base = process.env.DOCS_BASE ?? (process.env.GITHUB_ACTIONS ? '/WCA-Bench/' : '/')

export default defineConfig({
  base,
  srcDir,
  cleanUrls: true,
  lastUpdated: true,
  head: [
    ['meta', { name: 'theme-color', content: '#3c8772' }],
    ['meta', { name: 'og:title', content: 'WCA-Bench Documentation' }],
    [
      'meta',
      {
        name: 'og:description',
        content:
          'Project Proposal & Development Plan · Data Infrastructure · Task Suite · Evaluation Framework'
      }
    ]
  ],
  markdown: {
    lineNumbers: true,
    theme: { light: 'github-light', dark: 'github-dark' }
  },
  locales: {
    root: {
      label: 'English',
      lang: 'en-US',
      title: 'WCA-Bench',
      description:
        'A standardized benchmark for sports data analysis built on the World Cube Association database',
      themeConfig: {
        siteTitle: 'WCA-Bench Docs',
        logo: undefined,
        outline: { level: [2, 3], label: 'On this page' },
        nav: [
          { text: 'Home', link: '/' },
          { text: 'Project Proposal', link: '/guide/', activeMatch: '^/guide/' },
          { text: 'Technical Design', link: '/data/', activeMatch: '^/(data|tasks|evaluation)/' },
          { text: 'Development Plan', link: '/plan/', activeMatch: '^/plan/' }
        ],
        sidebar: enSidebar,
        search: {
          provider: 'local',
          options: {
            translations: {
              button: { buttonText: 'Search docs', buttonAriaLabel: 'Search docs' },
              modal: {
                noResultsText: 'No results found',
                resetButtonTitle: 'Clear query',
                footer: { selectText: 'Select', navigateText: 'Switch', closeText: 'Close' }
              }
            }
          }
        },
        socialLinks: [{ icon: 'github', link: 'https://github.com/' }],
        docFooter: { prev: 'Previous', next: 'Next' },
        lastUpdatedText: 'Last updated',
        returnToTopLabel: 'Return to top',
        sidebarMenuLabel: 'Menu',
        darkModeSwitchLabel: 'Theme',
        footer: {
          message:
            'Released under the Apache-2.0 License · Data copyright belongs to the World Cube Association',
          copyright: 'WCA-Bench Project'
        }
      }
    },
    zh: {
      label: '简体中文',
      lang: 'zh-CN',
      title: 'WCA-Bench',
      description: '基于世界魔方协会数据库的体育数据分析标准化基准',
      themeConfig: {
        siteTitle: 'WCA-Bench Docs',
        logo: undefined,
        outline: { level: [2, 3], label: '本页目录' },
        nav: [
          { text: '首页', link: '/zh/' },
          { text: '项目计划书', link: '/zh/guide/', activeMatch: '^/zh/guide/' },
          {
            text: '技术方案',
            link: '/zh/data/',
            activeMatch: '^/zh/(data|tasks|evaluation)/'
          },
          { text: '开发计划', link: '/zh/plan/', activeMatch: '^/zh/plan/' }
        ],
        sidebar: zhSidebar,
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
    }
  }
})
