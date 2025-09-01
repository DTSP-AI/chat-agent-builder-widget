import React from 'react'
import ChatWidget from './components/ChatWidget'
import AdminBuilder from './components/AdminBuilder'

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Agentic Widget</h1>
          <p className="text-gray-600">Multi-tenant chat widget with LangGraph agents</p>
        </header>
        
        <div className="space-y-8">
          <AdminBuilder />
        </div>
      </div>
      
      {/* Fixed chat widget */}
      <div className="fixed bottom-6 right-6">
        <ChatWidget />
      </div>
    </div>
  )
}