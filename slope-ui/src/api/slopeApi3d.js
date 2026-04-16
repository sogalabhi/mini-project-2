import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || ''

const client = axios.create({
  baseURL: API_BASE,
})

function normalizeError(error) {
  const detail = error?.response?.data?.detail
  if (detail?.message) return detail.message
  return error?.message || 'Unknown API error'
}

export async function validate3dPayload(payload, signal) {
  try {
    const res = await client.post('/api/v1/3d/validate', payload, { signal })
    return res.data
  } catch (error) {
    throw new Error(normalizeError(error))
  }
}

export async function analyze3dPayload(payload, signal) {
  try {
    const res = await client.post('/api/v1/3d/analyze', payload, { signal })
    return res.data
  } catch (error) {
    throw new Error(normalizeError(error))
  }
}

export async function analyze3dMultiPayload(payload, signal) {
  try {
    const res = await client.post('/api/v1/3d/analyze/multi', payload, { signal })
    return res.data
  } catch (error) {
    throw new Error(normalizeError(error))
  }
}

export async function get3dMethods(signal) {
  const res = await client.get('/api/v1/3d/methods', { signal })
  return res.data
}

