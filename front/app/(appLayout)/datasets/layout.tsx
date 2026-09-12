'use client'

import React from 'react'
import styles from './index.module.scss'

type DatasetsLayoutProps = {
  children: React.ReactNode
}

// 数据集管理/脚本管理切换已迁移至全局左侧导航，本布局仅承载页面内容
const DatasetsLayout = ({ children }: DatasetsLayoutProps) => {
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

export default DatasetsLayout
