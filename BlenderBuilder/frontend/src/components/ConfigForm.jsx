import { useState } from 'react'

function ConfigForm() {
  const [postCount, setPostCount] = useState('4')
  const [color, setColor] = useState('red')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState(null)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)
    setError(null)

    try {
      const response = await fetch('/api/render', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          postCount,
          color,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || 'Failed to render')
      }

      setMessage(`Render completed! Output saved to: ${data.outputPath}`)
    } catch (err) {
      setError(err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label htmlFor="postCount" className="block text-sm font-medium text-gray-700 mb-2">
          Post Count
        </label>
        <select
          id="postCount"
          value={postCount}
          onChange={(e) => setPostCount(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="4">4 Post (2x2 grid)</option>
          <option value="6">6 Post (3x2 grid)</option>
        </select>
      </div>

      <div>
        <label htmlFor="color" className="block text-sm font-medium text-gray-700 mb-2">
          Color
        </label>
        <select
          id="color"
          value={color}
          onChange={(e) => setColor(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="red">Red</option>
          <option value="blue">Blue</option>
          <option value="white">White</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Rendering...' : 'Submit'}
      </button>

      {message && (
        <div className="p-4 bg-green-50 border border-green-200 rounded-md text-green-800 text-sm">
          {message}
        </div>
      )}

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-800 text-sm">
          {error}
        </div>
      )}
    </form>
  )
}

export default ConfigForm

