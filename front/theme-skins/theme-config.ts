import type { ThemeConfig } from 'antd'

/**
 * 全局主题令牌 —— 「脉冲 Pulse」青瓷亮色体系
 *
 * 与 app/styles/tokens.scss（CSS 变量）、tailwind.config.js（primary 色阶）
 * 三处保持同值；改动色板时三处同步。
 */
const theme: ThemeConfig = {
  token: {
    // 主色：青瓷（全站唯一强调色）
    colorPrimary: '#0E9F8C',
    colorInfo: '#0E9F8C',
    colorLink: '#0E9F8C',

    // 状态色
    colorSuccess: '#4E9F3D',
    colorWarning: '#D9930B',
    colorError: '#E04758',

    // 背景：晨岚底 + 云板面板
    colorBgLayout: '#F4F6F5',
    colorBgContainer: '#FFFFFF',
    colorBgElevated: '#FFFFFF',

    // 文本：墨松层级
    colorText: '#1C2B29',
    colorTextSecondary: '#5C6B68',
    colorTextTertiary: '#8A9995',
    colorTextQuaternary: '#8A9995',

    // 边框
    colorBorder: '#C7D0CD',
    colorBorderSecondary: '#DDE3E1',

    borderRadius: 6,
  },
  components: {
    Dropdown: {
      controlItemBgHover: '#EBEFEE',
    },
    Menu: {
      itemBg: '#FFFFFF',
      itemHoverBg: '#EBEFEE',
      itemSelectedBg: 'rgba(14,159,140,.09)',
      itemSelectedColor: '#0E9F8C',
    },
    Table: {
      headerBg: '#F7FAF9',
      rowHoverBg: '#F4F8F7',
    },
    Layout: {
      bodyBg: '#F4F6F5',
      headerBg: '#FFFFFF',
      siderBg: '#FFFFFF',
    },
  },
}

export default theme
