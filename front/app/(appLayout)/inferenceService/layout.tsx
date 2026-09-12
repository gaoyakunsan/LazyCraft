'use client'
import React from 'react'

// 平台服务/云服务切换已迁移至全局左侧导航，本布局仅承载页面内容
const InferenceService = ({ children }) => {
  return (
    <div className='h-full bg-white'>
      {children}
    </div>
  )
}

export default InferenceService
