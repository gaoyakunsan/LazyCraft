'use client'
import type { FC } from 'react'
import { Suspense } from 'react'

type LogoSiteComponentProps = {
  className?: string
}

// 演示环境隐藏默认品牌 Logo：直接不渲染任何内容。
// 如需恢复或替换为客户 Logo，将 /logo/logo2.png 替换为对应图片并恢复渲染逻辑即可。
const LogoSiteContent: FC<LogoSiteComponentProps> = () => {
  return null
}

const BrandMark: FC<LogoSiteComponentProps> = ({ className }) => {
  return (
    <Suspense>
      <LogoSiteContent className={className} />
    </Suspense>
  )
}

export default BrandMark
