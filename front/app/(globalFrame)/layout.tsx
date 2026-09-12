import React from 'react'
import type { ReactNode } from 'react'
import { EntryCheckContextProvider } from '@/shared/hooks/permit-context'
import { LayerStackContextProvider } from '@/shared/hooks/modal-context'
import { EmitterProvider } from '@/shared/hooks/event-emitter'
import { RootStateHubProvider } from '@/shared/hooks/app-context'
import TopFrameEnclosure from '@/app/components/top-bar/head-wrap'
import Header from '@/app/components/top-bar'
import SideBar from '@/app/components/side-bar'
import SwrInitializer from '@/app/components/data-fetch'

// 通用布局组件的属性类型定义
type CommonLayoutProps = {
  children: ReactNode
}

const CommonLayout = ({ children }: CommonLayoutProps) => {
  // 构建完整的上下文提供者组件树结构
  const buildContextProviders = () => {
    return (
      <RootStateHubProvider>
        <EmitterProvider>
          <LayerStackContextProvider>
            <EntryCheckContextProvider>
              {/* 左侧导航 + 右侧（顶栏 + 内容）双列布局 */}
              <div className='flex h-full w-full'>
                <SideBar />
                <div className='flex h-full min-w-0 flex-1 flex-col'>
                  <TopFrameEnclosure>
                    <Header />
                  </TopFrameEnclosure>
                  <div className='min-h-0 flex-1'>
                    {children}
                  </div>
                </div>
              </div>
            </EntryCheckContextProvider>
          </LayerStackContextProvider>
        </EmitterProvider>
      </RootStateHubProvider>
    )
  }

  // 渲染主要的布局结构
  const renderMainLayout = () => {
    return (
      <>
        <SwrInitializer>
          {buildContextProviders()}
        </SwrInitializer>
      </>
    )
  }

  return renderMainLayout()
}

// 页面元数据配置
export const metadata = {
  title: '智能AI应用平台',
}

export default CommonLayout
