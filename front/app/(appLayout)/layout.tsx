import React from 'react'
import type { ReactNode } from 'react'
import { EntryCheckContextProvider } from '@/shared/hooks/permit-context'
import { LayerStackContextProvider } from '@/shared/hooks/modal-context'
// import { ProviderContextProvider } from '@/shared/hooks/provider-context'
import { EmitterProvider } from '@/shared/hooks/event-emitter'
import { RootStateHubProvider } from '@/shared/hooks/app-context'
import TopFrameEnclosure from '@/app/components/top-bar/head-wrap'
import Header from '@/app/components/top-bar'
import SideBar from '@/app/components/side-bar'
import SwrInitializer from '@/app/components/data-fetch'

type AppLayoutProps = {
  children: ReactNode
}

const AppLayout = ({ children }: AppLayoutProps) => {
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
                  <div className='min-h-0 flex-1 px-4'>
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

  return (
    <>
      <SwrInitializer>
        {buildContextProviders()}
      </SwrInitializer>
    </>
  )
}

export const metadata = {
  title: '智能AI应用平台',
}

export default AppLayout
