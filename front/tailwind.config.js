/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
    './context/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        // 灰色系 - 中性灰绿（墨松），从浅到深
        gray: {
          25: '#fbfcfc',
          50: '#f6f9f8',
          100: '#eef2f1',
          200: '#e0e7e5',
          300: '#c7d0cd',
          400: '#8a9995',
          500: '#5c6b68',
          600: '#3a4a46',
          700: '#4e5d59',
          800: '#283632',
          900: '#1c2b29',
        },

        // 青瓷系 - 主色调（脉冲 Pulse 主题）
        primary: {
          25: '#f3faf8',
          50: '#e8f5f2',
          100: '#cceae4',
          200: '#a8dcd2',
          300: '#7acbbe',
          400: '#45b5a3',
          500: '#16ac97',
          600: '#0e9f8c',
          700: '#0c8574',
          800: '#0a6a5d',
          900: '#085549',
        },

        // 青瓷系 - 辅助色
        blue: {
          500: '#E6F4F1',
        },

        // 青瓷系 - 浅底 tint（原靛蓝用途）
        indigo: {
          25: '#F4F8F7',
          50: '#EDF5F3',
          100: '#DFEEEA',
          300: '#A3CDC5',
          400: '#7FB8AD',
          600: '#3D8A7C',
          800: '#2A6B60',
        },

        // 紫色系
        purple: {
          50: '#F6F5FF',
          200: '#DCD7FE',
        },

        // 绿色系
        green: {
          50: '#F3FAF7',
          100: '#DEF7EC',
          800: '#03543F',
        },

        // 黄色系
        yellow: {
          100: '#FDF6B2',
          800: '#723B13',
        },

      },

      // 响应式断点
      screens: {
        mobile: '100px',
        tablet: '640px',
        pc: '769px',
      },

      // 阴影系统
      boxShadow: {
        'xs': '0px 1px 2px 0px rgba(16, 24, 40, 0.05)',
        'sm': '0px 1px 2px 0px rgba(16, 24, 40, 0.06), 0px 1px 3px 0px rgba(16, 24, 40, 0.10)',
        'md': '0px 2px 4px -2px rgba(16, 24, 40, 0.06), 0px 4px 8px -2px rgba(16, 24, 40, 0.10)',
        'lg': '0px 4px 6px -2px rgba(16, 24, 40, 0.03), 0px 12px 16px -4px rgba(16, 24, 40, 0.08)',
        'xl': '0px 8px 8px -4px rgba(16, 24, 40, 0.03), 0px 20px 24px -4px rgba(16, 24, 40, 0.08)',
        '2xl': '0px 24px 48px -12px rgba(16, 24, 40, 0.18)',
        '3xl': '0px 32px 64px -12px rgba(16, 24, 40, 0.14)',
      },

      // 透明度
      opacity: {
        2: '0.02',
        8: '0.08',
      },

      // 字体大小
      fontSize: {
        '2xs': '0.625rem',
      },
    },
  },
  plugins: [],
  corePlugins: {
    preflight: false,
  },
}
