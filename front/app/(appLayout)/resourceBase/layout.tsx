'use client'

import React from 'react'
import styles from './index.module.scss'

type ResourceBaseLayoutProps = {
  children?: React.ReactNode
}

// 知识库/数据库切换已迁移至全局左侧导航，本布局仅承载页面内容
const ResourceBaseLayout = ({ children }: ResourceBaseLayoutProps) => {
  return (
    <div className='page'>
      <div className={styles.container}>
        <div className={styles.content}>
          {children}
        </div>
      </div>
    </div>
  )
}

export default ResourceBaseLayout
