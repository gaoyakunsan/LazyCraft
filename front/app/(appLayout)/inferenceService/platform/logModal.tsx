'use client'
import React, { useEffect, useRef, useState } from 'react'
import { Button, Modal } from 'antd'
import { API_PREFIX } from '@/app-specs'

type IProps = {
  open: boolean
  serviceId: number | null
  serviceName: string
  onClose: () => void
}

// 轮询间隔(毫秒)
const POLL_INTERVAL = 2000

const LogModal = (props: IProps) => {
  const { open, serviceId, serviceName, onClose } = props
  const [logText, setLogText] = useState('')
  const offsetRef = useRef(0)
  const timerRef = useRef<NodeJS.Timeout | null>(null)
  const boxRef = useRef<HTMLDivElement>(null)
  // 用户上滚查看历史时暂停自动滚底
  const autoScrollRef = useRef(true)

  const fetchLog = async () => {
    if (!serviceId)
      return
    try {
      const token = localStorage.getItem('console_token')
      const res = await fetch(`${API_PREFIX}/infer-service/service/log/${serviceId}?offset=${offsetRef.current}`, {
        method: 'GET',
        headers: { Authorization: `Bearer ${token}` },
      })
      const data = await res.json()
      if (data?.status === 0 && data?.result) {
        const { content = '', offset = 0 } = data.result
        if (offsetRef.current === 0) {
          // 首次加载(或提示语)整块替换
          setLogText(content)
          offsetRef.current = offset
        }
        else if (content) {
          setLogText(prev => prev + content)
          offsetRef.current = offset
        }
      }
    }
    catch (error) {
      console.error('获取日志失败:', error)
    }
  }

  // 打开时立即拉取并启动轮询，关闭时清理
  useEffect(() => {
    if (open && serviceId) {
      offsetRef.current = 0
      setLogText('')
      autoScrollRef.current = true
      fetchLog()
      timerRef.current = setInterval(fetchLog, POLL_INTERVAL)
    }
    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }
  }, [open, serviceId])

  // 内容更新后自动滚底
  useEffect(() => {
    if (autoScrollRef.current && boxRef.current)
      boxRef.current.scrollTop = boxRef.current.scrollHeight
  }, [logText])

  const handleScroll = () => {
    const el = boxRef.current
    if (!el)
      return
    autoScrollRef.current = el.scrollHeight - el.scrollTop - el.clientHeight < 30
  }

  return (
    <Modal
      width={900}
      title={`运行日志 - ${serviceName}`}
      open={open}
      onCancel={onClose}
      footer={[<Button key="close" type="primary" onClick={onClose}>关闭</Button>]}
    >
      <div style={{ marginBottom: 8, color: '#8a8f99', fontSize: 12 }}>每 2 秒自动刷新，向上滚动查看历史时暂停自动滚底</div>
      <div
        ref={boxRef}
        onScroll={handleScroll}
        style={{
          background: '#0d1117',
          color: '#d1d5db',
          fontFamily: 'SFMono-Regular, Consolas, Menlo, monospace',
          fontSize: 12,
          lineHeight: '20px',
          height: 460,
          overflow: 'auto',
          padding: 12,
          borderRadius: 6,
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-all',
        }}
      >
        {logText || ' '}
      </div>
    </Modal>
  )
}

export default LogModal
