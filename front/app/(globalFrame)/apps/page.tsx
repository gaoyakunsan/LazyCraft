import React from 'react'
import AppList from '@/app/components/app-hub/app-list'

const AppListPage = async () => {
  return (
    <div className='px-4 h-full overflow-y-auto'>
      <AppList />
    </div>
  )
}

export default AppListPage
