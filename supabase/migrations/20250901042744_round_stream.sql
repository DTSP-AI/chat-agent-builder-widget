-- Agentic Widget Database Schema
-- Enables pgvector for persistent memory and creates multi-tenant tables

-- Enable vector extension for persistent memory
CREATE EXTENSION IF NOT EXISTS vector;

-- Tenants table for multi-tenant isolation
CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Agents table storing agent configurations per tenant
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    avatar_url TEXT,
    system_prompt TEXT NOT NULL,
    identity_json JSONB NOT NULL,
    mission_json JSONB NOT NULL,
    memory_mode TEXT NOT NULL CHECK (memory_mode IN ('thread', 'persistent')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, name)
);

-- Leads table for customer contact information
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    phone TEXT,
    notes TEXT,
    ghl_contact_id TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Agent memory table for persistent vector storage
CREATE TABLE IF NOT EXISTS agent_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    chunk TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_agents_tenant_name ON agents(tenant_id, name);
CREATE INDEX IF NOT EXISTS idx_leads_tenant_email ON leads(tenant_id, email);
CREATE INDEX IF NOT EXISTS idx_agent_memory_tenant_agent ON agent_memory(tenant_id, agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_memory_embedding ON agent_memory USING ivfflat (embedding vector_cosine_ops);

-- Insert default tenant for development
INSERT INTO tenants (id, name) VALUES ('00000000-0000-0000-0000-000000000001', 'Default Tenant')
ON CONFLICT (id) DO NOTHING;