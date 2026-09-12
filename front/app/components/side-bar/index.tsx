'use client'
import { useEffect, useState } from 'react'
import Link from 'next/link'

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

type NavGroup = {
  title: string
  items: { key: string; title: string; node: React.ReactNode }[]
}

const SideBar = () => {
  const deviceType = useResponsiveBreakpoints()
  const isMobileView = deviceType === 'mobile'
  const [collapsed, setCollapsed] = useState(false)
  const [mounted, setMounted] = useState(false)

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

  const navGroups: NavGroup[] = [
    {
      title: '应用',
      items: [
        { key: 'apps', title: '应用商店', node: <AppNav className={s.navItem} /> },
        { key: 'resourceBase', title: '资源库', node: <ResourceBaseNav className={s.navItem} /> },
        { key: 'prompt', title: 'Prompt', node: <PromptNav className={s.navItem} /> },
      ],
    },
    {
      title: '模型',
      items: [
        { key: 'modelWarehouse', title: '模型仓库', node: <ModelNav className={s.navItem} /> },
        { key: 'inferenceService', title: '推理服务', node: <InferenceServiceNav className={s.navItem} /> },
        { key: 'modelAdjust', title: '模型微调', node: <ModelAdjustNav className={s.navItem} /> },
      ],
    },
    {
      title: '运营',
      items: [
        { key: 'tools', title: '工具', node: <ToolsNav className={s.navItem} /> },
        { key: 'datasets', title: '数据', node: <DatasetNav className={s.navItem} /> },
      ],
    },
  ]

  // 移动端维持顶栏汉堡菜单的原有交互，侧栏不渲染
  if (isMobileView)
    return null

  return (
    <aside className={`${s.sidebar} ${collapsed ? s.collapsed : ''}`}>
      <Link href='/apps' className={s.brand}>
        <span className={s.brandMark} aria-hidden />
        {!collapsed && <span className={s.brandText}>智能AI应用平台</span>}
      </Link>

      <nav className={s.nav} aria-label='主导航'>
        {navGroups.map(group => (
          <div key={group.title} className={s.group}>
            {!collapsed && <div className={s.groupTitle}>{group.title}</div>}
            {group.items.map((item) => {
              return (
                <div key={item.key} className={s.itemWrap} title={collapsed ? item.title : undefined}>
                  {item.node}
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
