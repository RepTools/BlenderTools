import { useState } from 'react'
import ConfigForm from './components/ConfigForm'

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-gray-800 mb-6 text-center">
          Blender Builder
        </h1>
        <ConfigForm />
      </div>
    </div>
  )
}

export default App

