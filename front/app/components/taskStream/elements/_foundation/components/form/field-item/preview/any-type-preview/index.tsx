'use client'
import React from 'react'
import ImagePreview from '../pic-overview'
import AudioPreview from '../audio-preview'
import TextEditor from '../../text-composer'
import BytesPreview from '../bytes-preview'
import { JsonEditor } from '../../code'
import MarkdownRenderer from '@/app/components/base/markdown-renderer'
// import { ValueType, formatValueByType } from '../../utils'

// 含 markdown 图片语法的文本（如智能体返回的数据分析报告），按 markdown 渲染以展示柱状图/饼图等图表
const MARKDOWN_IMAGE_RE = /!\[[^\]]*\]\([^)]+\)/

const judgeType = (value: any) => {
  if (!value)
    return undefined

  if (Array.isArray(value)) {
    // 检查数组中是否包含音频文件
    if (value.length > 0 && typeof value[0] === 'string' && /\.(wav|mp3|m4a|ogg|flac)$/i.test(value[0]))
      return 'audio'
    // 检查数组中是否包含图片文件
    if (value.length > 0 && typeof value[0] === 'string' && /\.(jpe?g|png|gif|bmp|webp|svg)$/i.test(value[0]))
      return 'image'
    return 'array'
  }

  if (value instanceof Object)
    return 'object'

  if (typeof value === 'string') {
    if (/\.(wav|mp3|m4a|ogg|flac)$/i.test(value))
      return 'audio'
    else if (/\.(jpe?g|png|gif|bmp|webp|svg)$/i.test(value))
      return 'image'
    else return 'text'
  }
  return 'text'
}
// 做临时处理，后续需要优化
const AnyTypePreview = (props) => {
  const { value } = props

  const type = judgeType(value)

  if (type === 'audio')
    return <AudioPreview {...props} />

  if (type === 'image')
    return <ImagePreview {...props} />

  if (type === 'text' && typeof value === 'string' && MARKDOWN_IMAGE_RE.test(value))
    return <MarkdownRenderer content={value} />

  return type === 'object'
    ? value.__mark__ === '<lazyllm-query>' ? <BytesPreview value={value.file_urls} /> : <JsonEditor {...props} />
    : (type === 'text' && value.includes('<lazyllm-query>'))
      ? (() => {
        try {
          const jsonString = value.replace('<lazyllm-query>', '')
          // 如果替换后是空字符串，显示空的输入框
          if (!jsonString.trim())
            return <TextEditor {...props} value="" />

          const parsedData = JSON.parse(jsonString)
          return <BytesPreview value={parsedData.files} />
        }
        catch (error) {
          console.warn('Failed to parse JSON for lazyllm-query:', error)
          // 如果JSON解析失败，显示原始内容
          return <TextEditor {...props} />
        }
      })()
      : <TextEditor {...props} />
}
export default React.memo(AnyTypePreview)
