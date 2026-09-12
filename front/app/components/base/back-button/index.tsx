'use client'
import { useRouter } from 'next/navigation'

type BackButtonProps = {
  /** 按钮文案，如「返回模型列表」 */
  label: string
  /** 点击后跳转的列表页地址 */
  fallback: string
}

/** 详情/创建页通用的返回列表按钮（替代原面包屑） */
const BackButton = ({ label, fallback }: BackButtonProps) => {
  const router = useRouter()
  return (
    <button
      type='button'
      onClick={() => router.push(fallback)}
      className='flex items-center gap-1.5 h-8 px-3 rounded-md border border-gray-200 bg-white text-[13px] text-gray-600 cursor-pointer transition-colors hover:text-primary-600 hover:border-primary-600'
    >
      <svg viewBox='0 0 16 16' width='14' height='14' fill='none' stroke='currentColor'
        strokeWidth='1.8' strokeLinecap='round' strokeLinejoin='round'
      >
        <path d='M10 3L5 8l5 5' />
      </svg>
      {label}
    </button>
  )
}

export default BackButton
