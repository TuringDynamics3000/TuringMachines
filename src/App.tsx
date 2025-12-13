import { useState } from 'react'
import DecisionTimeline from './components/DecisionTimeline'
import './index.css'

function App() {
  const [workflowId, setWorkflowId] = useState('wf_test_001')
  const [inputValue, setInputValue] = useState('wf_test_001')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setWorkflowId(inputValue)
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-gray-900">
            🔍 Turing Investigator
          </h1>
          <p className="text-gray-600 mt-1">Decision Authority Timeline Viewer</p>
        </div>
      </header>

      {/* Workflow ID Input */}
      <div className="max-w-4xl mx-auto px-4 py-6">
        <form onSubmit={handleSubmit} className="bg-white rounded-lg shadow-md p-6 mb-6">
          <label htmlFor="workflow-id" className="block text-sm font-medium text-gray-700 mb-2">
            Workflow ID
          </label>
          <div className="flex gap-3">
            <input
              id="workflow-id"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Enter workflow ID (e.g., wf_test_001)"
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
            >
              Load Timeline
            </button>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Enter a workflow ID to view its complete decision history
          </p>
        </form>

        {/* Decision Timeline Component */}
        <DecisionTimeline workflowId={workflowId} />
      </div>

      {/* Footer */}
      <footer className="mt-12 py-6 text-center text-gray-500 text-sm">
        <p>🔒 Decision Authority • Single Source of Truth</p>
        <p className="mt-1">Reads only from decision.finalised events</p>
      </footer>
    </div>
  )
}

export default App
