'use client'

import React from 'react'
import styles from './index.module.scss'

type ModelWarehouseLayoutProps = {
  children: React.ReactNode
}

// 模型管理/模型评测切换已迁移至全局左侧导航，本布局仅承载页面内容
const ModelWarehouseLayout = ({ children }: ModelWarehouseLayoutProps) => {
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

export default ModelWarehouseLayout
