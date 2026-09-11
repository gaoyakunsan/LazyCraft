'use client'

import { Modal } from 'antd'
import React, { useEffect, useState } from 'react'

// 自定义事件名称
export const SHOW_423_MODAL_EVENT = 'show423Modal'

// 事件数据类型
export type Show423ModalEventDetail = {
  message: string
}

const ModelFont: React.FC = () => {
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    const handleShow423Modal = (event: CustomEvent<Show423ModalEventDetail>) => {
      setMessage(event.detail.message)
      setIsModalOpen(true)
    }

    window.addEventListener(SHOW_423_MODAL_EVENT, handleShow423Modal as EventListener)

    return () => {
      window.removeEventListener(SHOW_423_MODAL_EVENT, handleShow423Modal as EventListener)
    }
  }, [])

  const handleClose = () => {
    setIsModalOpen(false)
  }

  return (
    <Modal
      title="提示"
      open={isModalOpen}
      onCancel={handleClose}
      footer={null}
      width={600}
    >
      <div style={{ padding: '20px 0' }}>
        <p>{message}，请联系管理员。</p>
      </div>
    </Modal>
  )
}

export default ModelFont
