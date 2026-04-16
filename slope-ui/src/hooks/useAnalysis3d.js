import { useEffect, useRef } from 'react'
import { useMutation } from '@tanstack/react-query'
import { analyze3dMultiPayload, analyze3dPayload, validate3dPayload } from '../api/slopeApi3d.js'
import { useForm3dStore } from '../store/form3dStore.js'
import { useResults3dStore } from '../store/results3dStore.js'
import { useValidation3dStore } from '../store/validation3dStore.js'
import { build3dPayload, validate3dForm } from '../utils/validation3d.js'

function getFormState() {
  return useForm3dStore.getState()
}

export function useAnalysis3d() {
  const setValidationState = useValidation3dStore((s) => s.setValidationState)
  const setValidating = useValidation3dStore((s) => s.setValidating)
  const setLoading = useResults3dStore((s) => s.setLoading)
  const setError = useResults3dStore((s) => s.setError)
  const setSingleResult = useResults3dStore((s) => s.setSingleResult)
  const setMultiResult = useResults3dStore((s) => s.setMultiResult)
  const setLastPayload = useResults3dStore((s) => s.setLastPayload)
  const methodCfg = useForm3dStore((s) => s.methodConfig)

  const validateAbortRef = useRef(null)
  const analyzeAbortRef = useRef(null)
  const debounceRef = useRef(null)

  const validateMutation = useMutation({
    mutationFn: async () => {
      const state = getFormState()
      const local = validate3dForm(state)
      setValidationState(local)
      if (!local.isValid) return { valid: false, errors: ['Client-side validation failed'] }
      const payload = build3dPayload(state)
      setLastPayload(payload)
      if (validateAbortRef.current) validateAbortRef.current.abort()
      validateAbortRef.current = new AbortController()
      return validate3dPayload(payload, validateAbortRef.current.signal)
    },
    onMutate: () => setValidating(true),
    onSettled: () => setValidating(false),
    onError: (error) => setValidationState({ serverErrors: [error.message] }),
  })

  const analyzeMutation = useMutation({
    mutationFn: async ({ multi = false } = {}) => {
      const state = getFormState()
      const local = validate3dForm(state)
      setValidationState(local)
      if (!local.isValid) {
        throw new Error('Fix validation issues before running analysis.')
      }

      const payload = build3dPayload(state)
      setLastPayload(payload)
      if (analyzeAbortRef.current) analyzeAbortRef.current.abort()
      analyzeAbortRef.current = new AbortController()
      if (multi) {
        return analyze3dMultiPayload(
          {
            method_ids: state.methodConfig.comparisonMethodIds,
            base_request: payload,
          },
          analyzeAbortRef.current.signal,
        )
      }
      return analyze3dPayload(payload, analyzeAbortRef.current.signal)
    },
    onMutate: () => {
      setLoading(true)
      setError(null)
    },
    onSuccess: (data, vars) => {
      if (vars?.multi) setMultiResult(data)
      else setSingleResult(data)
    },
    onError: (error) => setError(error.message),
    onSettled: () => setLoading(false),
  })

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => validateMutation.mutate(), 300)
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current)
    }
    // validateMutation object identity may change and cause loops; only input state should trigger debounce.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [methodCfg]) // debounce on primary method state change

  return {
    validate: () => validateMutation.mutate(),
    runSingle: () => analyzeMutation.mutate({ multi: false }),
    runMulti: () => analyzeMutation.mutate({ multi: true }),
    isValidating: validateMutation.isPending,
    isRunning: analyzeMutation.isPending,
    canRun: validate3dForm(getFormState()).isValid && !analyzeMutation.isPending,
  }
}

