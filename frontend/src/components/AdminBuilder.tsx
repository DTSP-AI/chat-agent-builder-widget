import React, { useState } from 'react'
import { Save, Settings, User, Target, CheckCircle } from 'lucide-react'
import { postJSON } from '../lib/api'

export default function AdminBuilder() {
  const [tenantId, setTenantId] = useState('00000000-0000-0000-0000-000000000001')
  const [name, setName] = useState('Elena')
  const [avatarUrl, setAvatarUrl] = useState('')
  const [memoryMode, setMemoryMode] = useState<'thread' | 'persistent'>('thread')
  const [isLoading, setIsLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const [systemPrompt, setSystemPrompt] = useState(`You are Elena, a professional portfolio chat agent for multi-tenant websites.

Objectives:
1) Greet warmly, be concise, and clarify intent within 2 exchanges.
2) If the visitor is a qualified lead, collect name, email, and phone number.
3) Offer relevant landing pages (product, booking, contact) when intent is clear.
4) Produce a 1–2 sentence summary of each conversation for the CRM notes field.
5) Follow brand tone from identity.json. Respect mission.json guidelines and compliance items.

Safety:
- Never request or store payment info, SSNs, or sensitive health data.
- When unsure or out of scope, offer to connect to a human via contact info.

Routing:
- If user asks for a page, reply with the clean URL path or a short call-to-action.

Memory:
- Treat conversation context as thread memory; persistent memory may be enabled per agent.`)

  const [identity, setIdentity] = useState(`{
  "brand": "Portfolio Pro",
  "tone": "warm, professional, concise",
  "capabilities": ["lead_capture", "appointment_routing", "product_information"],
  "personality": {
    "communication_style": "friendly but efficient",
    "expertise_level": "knowledgeable assistant"
  }
}`)

  const [mission, setMission] = useState(`{
  "mission": "Convert visitors into qualified leads and help customers quickly",
  "guidelines": [
    "Always ask for name, email, and phone before handing off",
    "Offer relevant landing pages when intent is clear",
    "Summarize each conversation in 2 sentences for the CRM notes"
  ],
  "compliance": [
    "Never promise pricing without verification",
    "Never collect sensitive data (SSN, payment)"
  ]
}`)

  const handleSubmit = async () => {
    setIsLoading(true)
    setSuccess(false)

    try {
      // Validate JSON
      const parsedIdentity = JSON.parse(identity)
      const parsedMission = JSON.parse(mission)

      await postJSON('/api/v1/admin/agent', {
        tenant_id: tenantId,
        name,
        avatar_url: avatarUrl || null,
        system_prompt: systemPrompt,
        identity: parsedIdentity,
        mission: parsedMission,
        memory_mode: memoryMode
      })

      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (error) {
      console.error('Failed to save agent:', error)
      alert('Failed to save agent. Please check JSON format and try again.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
      <div className="flex items-center space-x-2 mb-6">
        <Settings className="w-5 h-5 text-gray-600" />
        <h2 className="text-xl font-semibold text-gray-900">Agent Builder</h2>
        {success && (
          <div className="flex items-center space-x-1 text-emerald-600">
            <CheckCircle className="w-4 h-4" />
            <span className="text-sm font-medium">Saved!</span>
          </div>
        )}
      </div>
      
      {/* Basic Configuration */}
      <div className="space-y-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              <User className="w-4 h-4 inline mr-1" />
              Tenant ID
            </label>
            <input
              type="text"
              value={tenantId}
              onChange={(e) => setTenantId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              placeholder="UUID for tenant isolation"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Agent Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              placeholder="e.g., Elena"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Avatar URL</label>
            <input
              type="text"
              value={avatarUrl}
              onChange={(e) => setAvatarUrl(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
              placeholder="https://example.com/avatar.png"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Memory Mode</label>
            <select
              value={memoryMode}
              onChange={(e) => setMemoryMode(e.target.value as 'thread' | 'persistent')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            >
              <option value="thread">Thread Memory (Session-based)</option>
              <option value="persistent">Persistent Memory (pgvector)</option>
            </select>
          </div>
        </div>
      </div>

      {/* System Prompt */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          <Target className="w-4 h-4 inline mr-1" />
          System Prompt
        </label>
        <textarea
          value={systemPrompt}
          onChange={(e) => setSystemPrompt(e.target.value)}
          rows={8}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent font-mono text-sm"
          placeholder="Define agent behavior, objectives, and constraints..."
        />
      </div>

      {/* Identity & Mission JSONs */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Identity JSON</label>
          <textarea
            value={identity}
            onChange={(e) => setIdentity(e.target.value)}
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent font-mono text-xs"
            placeholder="Agent identity configuration..."
          />
          <p className="text-xs text-gray-500 mt-1">Brand, tone, capabilities, personality</p>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Mission JSON</label>
          <textarea
            value={mission}
            onChange={(e) => setMission(e.target.value)}
            rows={8}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent font-mono text-xs"
            placeholder="Agent mission and guidelines..."
          />
          <p className="text-xs text-gray-500 mt-1">Mission, guidelines, compliance rules</p>
        </div>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSubmit}
        disabled={isLoading || !tenantId || !name}
        className="w-full md:w-auto flex items-center justify-center space-x-2 px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-gray-300 text-white font-medium rounded-lg transition-colors duration-200"
      >
        <Save className="w-4 h-4" />
        <span>{isLoading ? 'Saving...' : 'Save Agent Configuration'}</span>
      </button>
      
      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <h4 className="font-medium text-sm text-gray-700 mb-2">What happens when you save:</h4>
        <ul className="text-xs text-gray-600 space-y-1">
          <li>• Creates/updates agent in database with multi-tenant isolation</li>
          <li>• Writes identity.json and mission.json to backend/storage/{tenantId}/</li>
          <li>• Configures memory mode for session vs persistent storage</li>
          <li>• Makes agent available for chat via /api/v1/chat endpoint</li>
        </ul>
      </div>
    </div>
  )
}