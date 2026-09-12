'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'

import AppNav from '@/app/components/top-bar/app-gateway'
import ResourceBaseNav from '@/app/components/top-bar/res-source'
import PromptNav from '@/app/components/top-bar/prompt-route'
import ModelNav from '@/app/components/top-bar/model-route'
import InferenceServiceNav from '@/app/components/top-bar/ai-path'
import ModelAdjustNav from '@/app/components/top-bar/model-tune'
import ToolsNav from '@/app/components/top-bar/tools-route'
import DatasetNav from '@/app/components/top-bar/data-route'
import useResponsiveBreakpoints from '@/shared/hooks/use-breakpoints'
import s from './index.module.scss'

const COLLAPSED_KEY = 'pulse-sidebar-collapsed'

type SubItem = { title: string; href: string }
type NavItem = { key: string; title: string; node: React.ReactNode; children?: SubItem[] }
type NavGroup = { title: string; items: NavItem[] }

/** 二级菜单项：按路径前缀匹配高亮 */
const SubNavItem = ({ title, href }: SubItem) => {
  const pathname = usePathname()
  const active = pathname === href || pathname.startsWith(`${href}/`)
  return (
    <Link href={href} className={`${s.subItem} ${active ? s.subActive : ''}`}>
      {title}
    </Link>
  )
}

const SideBar = () => {
  const deviceType = useResponsiveBreakpoints()
  const isMobileView = deviceType === 'mobile'
  const [collapsed, setCollapsed] = useState(false)
  const [mounted, setMounted] = useState(false)
  // 有二级菜单的分组默认折叠，点击箭头展开
  const [expandedMap, setExpandedMap] = useState<Record<string, boolean>>({})
  const pathname = usePathname()

  useEffect(() => {
    setCollapsed(window.localStorage.getItem(COLLAPSED_KEY) === '1')
    setMounted(true)
  }, [])

  const toggleCollapsed = () => {
    setCollapsed((prev) => {
      window.localStorage.setItem(COLLAPSED_KEY, prev ? '0' : '1')
      return !prev
    })
  }

  const toggleExpanded = (key: string) => {
    setExpandedMap(prev => ({ ...prev, [key]: !prev[key] }))
  }

  const navGroups: NavGroup[] = [
    {
      title: '应用',
      items: [
        { key: 'apps', title: '应用商店', node: <AppNav className={s.navItem} /> },
        {
          key: 'resourceBase',
          title: '资源库',
          node: <ResourceBaseNav className={`${s.navItem} ${s.iconNudge}`} />,
          children: [
            { title: '知识库', href: '/resourceBase/knowledgeBase' },
            { title: '数据库', href: '/resourceBase/dataBase' },
          ],
        },
        { key: 'prompt', title: 'Prompt', node: <PromptNav className={s.navItem} /> },
      ],
    },
    {
      title: '模型',
      items: [
        {
          key: 'modelWarehouse',
          title: '模型仓库',
          node: <ModelNav className={s.navItem} />,
          children: [
            { title: '模型管理', href: '/modelWarehouse/modelManage' },
            { title: '模型评测', href: '/modelWarehouse/modelTest' },
          ],
        },
        {
          key: 'inferenceService',
          title: '推理服务',
          node: <InferenceServiceNav className={s.navItem} />,
          children: [
            { title: '平台服务', href: '/inferenceService/platform' },
            { title: '云服务', href: '/inferenceService/cloud' },
          ],
        },
        { key: 'modelAdjust', title: '模型微调', node: <ModelAdjustNav className={s.navItem} /> },
      ],
    },
    {
      title: '运营',
      items: [
        { key: 'tools', title: '工具', node: <ToolsNav className={s.navItem} /> },
        {
          key: 'datasets',
          title: '数据集',
          node: <DatasetNav className={s.navItem} />,
          children: [
            { title: '数据集管理', href: '/datasets/datasetManager' },
            { title: '脚本管理', href: '/datasets/scriptManager' },
          ],
        },
      ],
    },
  ]

  // 当前路径落在某组二级菜单内时，自动展开该组
  useEffect(() => {
    if (!pathname)
      return
    navGroups.forEach(g => g.items.forEach((item) => {
      if (item.children?.some(c => pathname === c.href || pathname.startsWith(`${c.href}/`)))
        setExpandedMap(prev => ({ ...prev, [item.key]: true }))
    }))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname])

  // 移动端维持顶栏汉堡菜单的原有交互，侧栏不渲染
  if (isMobileView)
    return null

  return (
    <aside className={`${s.sidebar} ${collapsed ? s.collapsed : ''}`}>
      <Link href='/apps' className={s.brand}>
        <img src='/logo.svg' alt='' className={s.brandMark} />
        {!collapsed && <span className={s.brandText}>智能AI应用平台</span>}
      </Link>

      <nav className={s.nav} aria-label='主导航'>
        {navGroups.map(group => (
          <div key={group.title} className={s.group}>
            {!collapsed && <div className={s.groupTitle}>{group.title}</div>}
            {group.items.map((item) => {
              const expanded = !!expandedMap[item.key]
              return (
                <div key={item.key} className={s.itemWrap} title={collapsed ? item.title : undefined}>
                  {item.node}
                  {!collapsed && item.children && (
                    <button
                      type='button'
                      className={`${s.expandBtn} ${expanded ? s.expanded : ''}`}
                      aria-label={expanded ? '收起子菜单' : '展开子菜单'}
                      onClick={() => toggleExpanded(item.key)}
                    >
                      <svg viewBox='0 0 16 16' width='12' height='12' fill='none' stroke='currentColor'
                        strokeWidth='1.8' strokeLinecap='round' strokeLinejoin='round'
                      >
                        <path d='M4 6l4 4 4-4' />
                      </svg>
                    </button>
                  )}
                  {!collapsed && item.children && expanded && (
                    <div className={s.subList}>
                      {item.children.map(sub => (
                        <SubNavItem key={sub.href} {...sub} />
                      ))}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        ))}
      </nav>

      {mounted && (
        <button
          type='button'
          className={s.collapseBtn}
          onClick={toggleCollapsed}
          aria-label={collapsed ? '展开菜单' : '收起菜单'}
        >
          <svg viewBox='0 0 16 16' width='14' height='14' fill='none' stroke='currentColor'
            strokeWidth='1.6' strokeLinecap='round' strokeLinejoin='round'
            style={{ transform: collapsed ? 'rotate(180deg)' : 'none', transition: 'transform .2s' }}
          >
            <path d='M10 3L5 8l5 5' />
          </svg>
          {!collapsed && <span>收起菜单</span>}
        </button>
      )}
    </aside>
  )
}

export default SideBar
